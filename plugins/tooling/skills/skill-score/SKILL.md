---
name: skill-score
description: Score un skill sur un input réel, génère une variante améliorée et compare les deux. Utiliser quand l'utilisateur veut améliorer un skill, "voir ce que ça produit vraiment", ou "scorer ce skill".
argument-hint: "[nom du skill]"
allowed-tools: Read, Glob, Write, Edit
---

## Préparer le contexte (prepare)

Localiser `plugins/*/skills/$ARGUMENTS/SKILL.md`. Lire le fichier.
Identifier `<plugin>` et `<skill_version>` depuis le chemin et le `plugin.json` correspondant.

Chercher `evals/<plugin>/$ARGUMENTS/rubric.md` et `evals/<plugin>/$ARGUMENTS/runs.json`.

**Si `evals/<plugin>/$ARGUMENTS/` absent** — le créer :

1. Générer `rubric.md` automatiquement depuis le SKILL.md :
   5-6 critères adaptés, 2 pts chacun. Toujours inclure : complétude output, exactitude des inférences, structure, fidélité à l'intention. Ajouter les critères spécifiques au skill.

2. AskUserQuestion :
   > "Donne-moi un input réel pour **[skill]** — exactement ce que tu lui passerais."
   Écrire dans `evals/<plugin>/$ARGUMENTS/sample-input.md`.

3. Créer `runs.json` avec un tableau vide `[]`.

**Si `evals/<plugin>/$ARGUMENTS/` présent** — extraire uniquement ce qui est nécessaire via Bash :

```bash
# Dernier score et contexte
jq '.[-1] | {quality: .scores.quality, quality_max: .scores.quality_max, decision: .decision, piste_efficience: .piste_efficience}' runs.json

# Changements déjà rejetés (pour Fork B)
jq '[.[] | select(.decision == "ignored") | .change, .piste_efficience] | map(select(. != null))' runs.json
```

Ne jamais lire le fichier entier — seuls ces deux extraits sont passés aux forks.

---

## Scorer (train)

Lancer deux forks en parallèle :

**Fork A — Dry-run original**
```
context: fork
agent: general-purpose
Exécute ce SKILL.md sur l'input fourni.
Suis chaque étape. N'appelle aucun outil d'écriture externe.
Retourne :
- L'output complet que tu aurais produit
- Métriques d'efficience :
  - MCP calls : nombre d'appels outils externes effectués
  - AskUserQuestion : nombre d'interruptions utilisateur
  - Tokens injectés : (len(SKILL.md) + len(input) + len(références chargées)) ÷ 4, arrondi
  - Étapes exécutées : X/Y
[SKILL.md + sample-input.md]
```

**Fork B — Variante**

Le prompt de Fork B s'adapte selon `last_score` vs `quality_max` du rubric :

Si `last_score < quality_max` → mode qualité :
```
context: fork
agent: general-purpose
Tu es un optimiseur de prompt (rôle Blue). Mode : QUALITÉ.
Objectif : améliorer le score qualité du skill.
Rejets connus : [extrait jq des changements ignorés]
Identifie le point faible qualité le plus impactant. Propose UNE modification ciblée.
Retourne UNIQUEMENT un diff JSON — pas le fichier entier :
{
  "section": "nom de la section modifiée",
  "old": "extrait exact à remplacer",
  "new": "nouveau texte",
  "rationale": "une ligne"
}
[SKILL.md + sample-input.md + extrait runs.json]
```

Si `last_score == quality_max` → mode efficience :
```
context: fork
agent: general-purpose
Tu es un optimiseur de prompt (rôle Blue). Mode : EFFICIENCE.
Objectif : réduire MCP calls ou AskUserQuestion sans dégrader la qualité.
Point de départ : [last_ignored_piste ou "identifier le meilleur levier"]
Rejets connus : [extrait jq des changements ignorés]
Retourne UNIQUEMENT un diff JSON — pas le fichier entier :
{
  "section": "nom de la section modifiée",
  "old": "extrait exact à remplacer",
  "new": "nouveau texte",
  "rationale": "une ligne",
  "gains": { "mcp_calls": -N, "ask_user_question": -N, "tokens": -N }
}
[SKILL.md + sample-input.md + extrait runs.json]
```

Attendre les deux résultats.

Lancer ensuite deux forks de scoring en parallèle :

**Fork Score A**
```
context: fork
agent: general-purpose
Score cet output contre ce rubric (section Qualité uniquement).
Retourne un JSON :
{
  "total": X,
  "detail": { "critère": score, ... },
  "point_faible": "...",
  "piste_efficience": "..."
}
[rubric.md + output Fork A + métriques efficience Fork A]
```

**Fork Score B** — même prompt avec output Fork B + métriques Fork B.

---

## Comparer et proposer (program)

Afficher :

```
                      Original    Variante
Qualité               X/12        Y/12
── Efficience ──────────────────────────
MCP calls             A           B
AskUserQuestion       C           D
Tokens injectés       ~E          ~F
Étapes exécutées      G/H         G/H
─────────────────────────────────────
[critère 1]           2/2         2/2
[critère 2]           1/2         2/2
...
Changement apporté : [une ligne Blue]
```

AskUserQuestion :
> "Qualité : +X pts. Efficience : -Y calls, -Z tokens.
> Tu appliques ?"

- `✅ Appliquer` → `Edit(old: diff.old, new: diff.new)` sur SKILL.md + bump PATCH plugin.json + append runs.json
- `❌ Ignorer` → append runs.json (rejeté + raison)
- `🔁 Relancer` → nouveau Fork B depuis SKILL.md original

**Dans tous les cas**, appender dans `evals/<plugin>/<skill>/runs.json` :
```json
{
  "run": N,
  "date": "YYYY-MM-DD",
  "skill_version": "x.y.z",
  "input_summary": "...",
  "scores": {
    "quality": X,
    "quality_max": Y,
    "mcp_calls": A,
    "ask_user_question": B,
    "tokens_injected": C,
    "steps_completed": "X/Y"
  },
  "issue": "...",
  "change": "... ou null",
  "piste_efficience": "...",
  "decision": "applied | ignored | relaunched",
  "reason": "... si ignored"
}
```
```bash
# Appender sans relire tout le fichier
jq '. += [<nouvel_objet>]' runs.json > runs.tmp && mv runs.tmp runs.json
```

---

## Gotchas

**Le rubric est le seul juge — ne pas le modifier entre deux runs.**
Changer le rubric invalide toutes les comparaisons historiques.

**Fork Blue retourne un diff JSON, pas le fichier entier.**
Si Blue retourne un SKILL.md complet, rejeter et relancer — coût ~10x pour le même résultat.

**`diff.old` doit être un extrait exact du SKILL.md.**
Un `old` approximatif fait échouer l'Edit silencieusement. Vérifier avant d'appliquer.

**Fork Blue lit l'extrait runs.json — s'il ne le fait pas, il repropose des rejets.**
Toujours passer l'extrait jq des changements ignorés au Fork B.

**Mode qualité vs efficience dépend du dernier score, pas du score actuel.**
Si le run A retourne 12/12 mais que le dernier runs.json était 11/12, Fork B reste en mode qualité — c'est le run A qui déterminera le mode du prochain run.

**`🔁 Relancer` ≠ rollback.**
Relancer génère une nouvelle variante depuis le SKILL.md original, pas depuis la variante rejetée.
