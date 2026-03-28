---
name: skill-score
description: Score un skill sur un input réel, génère une variante améliorée et compare les deux. Utiliser quand l'utilisateur veut améliorer un skill, "voir ce que ça produit vraiment", ou "scorer ce skill".
argument-hint: "[nom du skill]"
allowed-tools: Read, Glob, Write, Edit, Bash
---

## Préparer le contexte (prepare)

Localiser `plugins/*/skills/$ARGUMENTS/SKILL.md`. Lire le fichier.
Identifier `<plugin>` et `<skill_version>` depuis le chemin et le `plugin.json` correspondant.

Chercher `evals/<plugin>/$ARGUMENTS/rubric.md` et `evals/<plugin>/$ARGUMENTS/runs.jsonl`.

**Si `evals/<plugin>/$ARGUMENTS/` absent** — le créer :

1. Générer `rubric.md` automatiquement depuis le SKILL.md :
   5-6 critères adaptés, 2 pts chacun. Toujours inclure : complétude output, exactitude des inférences, structure, fidélité à l'intention. Ajouter les critères spécifiques au skill.

2. AskUserQuestion :
   > "Donne-moi un input réel pour **[skill]** — exactement ce que tu lui passerais."
   Écrire dans `evals/<plugin>/$ARGUMENTS/sample-input.md`.

3. Initialiser le dossier :
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/init-eval.sh evals/<plugin>/$ARGUMENTS/
   ```

**Si `evals/<plugin>/$ARGUMENTS/` présent** — extraire le contexte via script :

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/get-context.sh evals/<plugin>/$ARGUMENTS/runs.jsonl
```

Retourne `{segment, last_score, mode, ignored_changes, efficience_backlog}`.
Utiliser `mode` pour choisir le prompt Fork B. Passer `ignored_changes` et `efficience_backlog` aux forks concernés.

Ne jamais lire le fichier runs.jsonl entier — seul ce JSON est passé aux forks.

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
- ASI — pour chaque critère probablement < 2/2, explique précisément
  ce qui manque dans l'output produit (une ligne par critère faible)
[SKILL.md + sample-input.md]
```

**Fork B — Variante**

Le prompt de Fork B s'adapte selon le résultat du check de stabilité (2 derniers runs à quality_max) :

Si `mode == "qualite"` :
```
context: fork
agent: general-purpose
Tu es un optimiseur de prompt (rôle Blue). Mode : QUALITÉ.
Objectif : améliorer le score qualité du skill.
Scope : SKILL.md uniquement. Ne pas proposer de modifications aux fichiers references/ ni au rubric.
Rejets connus : [extrait jq changements ignorés segment courant]
ASI Fork A : [diagnostics par critère faible retournés par Fork A]
Identifie le point faible qualité le plus impactant. Propose UNE modification ciblée.
Retourne UNIQUEMENT un diff JSON — pas le fichier entier :
{
  "section": "nom de la section modifiée",
  "old": "extrait exact à remplacer",
  "new": "nouveau texte",
  "rationale": "une ligne"
}
[SKILL.md + sample-input.md + extrait runs.jsonl]
```

Si `mode == "efficience"` (2 derniers runs du segment à quality_max) :
```
context: fork
agent: general-purpose
Tu es un optimiseur de prompt (rôle Blue). Mode : EFFICIENCE.
Objectif : réduire MCP calls ou AskUserQuestion sans dégrader la qualité.
Scope : SKILL.md uniquement. Ne pas proposer de modifications aux fichiers references/ ni au rubric.
Backlog pistes (toutes, dans l'ordre — reprendre la plus prometteuse non encore tentée) :
[extrait jq backlog pistes_efficience]
Rejets connus : [extrait jq changements ignorés segment courant]
Retourne UNIQUEMENT un diff JSON — pas le fichier entier :
{
  "section": "nom de la section modifiée",
  "old": "extrait exact à remplacer",
  "new": "nouveau texte",
  "rationale": "une ligne",
  "gains": { "mcp_calls": -N, "ask_user_question": -N, "tokens": -N }
}
[SKILL.md + sample-input.md + extrait runs.jsonl]
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

- `✅ Appliquer` → `Edit(old: diff.old, new: diff.new)` sur SKILL.md + bump PATCH plugin.json + append runs.jsonl
- `❌ Ignorer` → append runs.jsonl (rejeté + raison)
- `🔁 Relancer` → nouveau Fork B depuis SKILL.md original. Si 2+ rejets consécutifs dans le segment : proposer de changer le sample-input (input différent = angles différents) avant de relancer.

**Dans tous les cas**, appender dans `evals/<plugin>/<skill>/runs.jsonl` :
```json
{"run": N, "date": "YYYY-MM-DD", "segment": N, "skill_version": "x.y.z", "input_summary": "...", "scores": {"quality": X, "quality_max": Y, "mcp_calls": A, "ask_user_question": B, "tokens_injected": C, "steps_completed": "X/Y"}, "issue": "...", "change": "... ou null", "piste_efficience": "...", "decision": "applied | ignored | relaunched", "reason": "... si ignored"}
```
```bash
bash ${CLAUDE_SKILL_DIR}/scripts/append-run.sh evals/<plugin>/<skill>/runs.jsonl '<objet_json_compact>'
```

---

## Gotchas

**Le rubric est le seul juge — ne pas le modifier entre deux runs.**
Changer le rubric invalide toutes les comparaisons historiques.

**Fork Blue retourne un diff JSON, pas le fichier entier.**
Si Blue retourne un SKILL.md complet, rejeter et relancer — coût ~10x pour le même résultat.

**`diff.old` doit être un extrait exact du SKILL.md.**
Un `old` approximatif fait échouer l'Edit silencieusement. Vérifier avant d'appliquer.

**Fork Blue lit l'extrait runs.jsonl — s'il ne le fait pas, il repropose des rejets.**
Toujours passer l'extrait jq des changements ignorés au Fork B.

**Mode efficience requiert 2 runs consécutifs à quality_max dans le segment courant.**
Un seul run parfait peut être un input facile — pas un signal fiable. Fork B reste en mode qualité tant que les 2 derniers runs du segment ne sont pas tous les deux à quality_max.

**Le segment scope les comparaisons historiques.**
Incrémenter `segment` lors d'un bump MAJOR ou d'une refonte du rubric. Fork B ne lit les rejets connus que dans le segment courant — les pistes_efficience restent cross-segments (une bonne idée ne périme pas).

**`🔁 Relancer` ≠ rollback.**
Relancer génère une nouvelle variante depuis le SKILL.md original, pas depuis la variante rejetée.
