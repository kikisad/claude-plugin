---
name: create-ticket
description: Crée un ticket (Bug, Improvement ou Projet) dans Notion à partir de n'importe quelle source. Utiliser quand l'utilisateur mentionne "créer un ticket", "logger ce bug", "ajouter dans Notion", ou colle un message Slack, un lien Notion, ou une réunion Granola.
compatibility: "Requires Notion MCP (notion-search, notion-create-pages, notion-fetch) + Slack MCP (slack_read_thread) + optionally Granola MCP (get_meeting_transcript, query_granola_meetings)"
allowed-tools: Read
argument-hint: "[lien Slack, lien Notion, nom de réunion Granola, ou texte brut]"
---

> Templates de contenu : `${CLAUDE_SKILL_DIR}/references/templates.md`

---

## Prerequisites

**MCPs requis :**
- Notion MCP connecté (`Notion:notion-search`, `Notion:notion-create-pages`)
- Slack MCP connecté (`Slack:slack_read_thread`)
- Granola MCP optionnel (`Granola:get_meeting_transcript`, `Granola:query_granola_meetings`)

Si un MCP requis est absent → arrêter et indiquer lequel configurer.

**Variables d'environnement :**
Lire depuis `.claude/settings.local.json`. Pour chaque variable vide → AskUserQuestion en un seul appel, puis écrire les valeurs dans `.claude/settings.local.json` sous `env`.

| Variable | Utilisation |
|---|---|
| `$NOTION_FEATURES_DB_ID` | BDD cible pour Fix et Improvement |
| `$NOTION_PROJECTS_DB_ID` | BDD cible pour Projet |

---

## Étape 0 — Lire l'input

| Type d'input | Action |
|---|---|
| **Texte brut** | Analyser directement |
| **Lien Slack** | Extraire `channel_id` et `thread_ts` de l'URL → `Slack:slack_read_thread(channel_id, thread_ts)`. Lire le fil complet (parent + réponses). |
| **Lien Notion** | `Notion:notion-fetch(url)` — lire pour contexte uniquement, extraire les éléments pertinents |
| **Granola** | Si lien ou nom de réunion → `Granola:get_meeting_transcript` ou `Granola:query_granola_meetings`. Si texte collé directement → analyser tel quel. |

> Conversion timestamp Slack : URL `.../p1741234567890123` → `thread_ts = 1741234567.890123` (point après les 10 premiers chiffres).

Si plusieurs liens fournis, les lire tous avant de continuer.

---

## Étape 1 — Détecter et annoncer

**Si le fil contient plusieurs demandes distinctes** — les lister avant tout :

```
J'ai détecté 2 demandes dans ce fil. Je vais créer 2 tickets :
1. [titre A]
2. [titre B]
Dis-moi si tu veux en ignorer une.
```

Puis traiter chaque demande séquentiellement avec les étapes 2→6.

**Pour chaque demande**, inférer :

| Champ | Comment l'inférer |
|---|---|
| **Titre** | Phrase courte et claire résumant le sujet |
| **Problème** | Description détaillée du bug ou besoin |
| **Solution** | Si mentionnée ou évidente, sinon laisser vide |
| **Type** | Voir règle ci-dessous |

**Règle de décision :**
- Durée estimée > 1 jour → **Projet** (BDD Projets)
- Sinon → **Bug/Improvement** (`Fix` si dysfonctionnement, `Improvement` si amélioration/feature) (BDD Features)
- **Si ambiguïté sur la durée** (extraction de données, reporting, intégration) → AskUserQuestion : "C'est plutôt une extraction ponctuelle (<1j) ou un développement à part entière (>1j) ?"

Annoncer la décision avant toute création :

```
Titre : [titre inféré]
Type : Projet — raison : [x]
→ Création dans la BDD Projets.
Dis-moi si tu veux changer quelque chose.
```

Pas de question posée — Claude décide, l'utilisateur corrige si besoin.

---

## Étape 2 — Demander la priorité

**Si plusieurs tickets détectés à l'étape 1** — regrouper en un seul appel :

```
AskUserQuestion: "Priority pour chaque ticket ? (High / Medium / Low)
1. [titre A] ([type A])
2. [titre B] ([type B])"
```

**Si un seul ticket** — demande individuelle :

```
AskUserQuestion: "Priority pour '[titre inféré]' ([type]) ? (High / Medium / Low)"
```

---

## Étape 3 — Vérifier les doublons

Chercher dans la BDD cible (Features ou Projets selon le type décidé à l'étape 1) via `Notion:notion-search`. Faire 1 à 2 recherches avec des formulations différentes.

| Cas | Comportement |
|---|---|
| **Doublon évident** | Arrêter. Afficher le ticket existant avec son lien. |
| **Ticket similaire** | Afficher les similaires (max 3) et demander si créer quand même. |
| **Aucun résultat** | Continuer directement. |

---

## Étape 4 — Construire le contenu

Lire les templates depuis `${CLAUDE_SKILL_DIR}/references/templates.md` et appliquer le bon selon le type.

---

## Étape 5 — Créer dans la bonne BDD

### Bug / Improvement → `$NOTION_FEATURES_DB_ID`

```json
{
  "parent": { "data_source_id": "$NOTION_FEATURES_DB_ID" },
  "pages": [{
    "icon": "[/icons/bug_red.svg pour Fix, emoji pertinent pour Improvement]",
    "properties": {
      "Nom": "[titre]",
      "Type": "[Fix ou Improvement]",
      "Priority": "[priority choisie]",
      "Etat": "Raffinage",
      "DoD": "__NO__",
      "Feature flag": "__NO__",
      "Scope change?": "__NO__",
      "Factory": ["Dev"]
    },
    "content": "[contenu selon template Fix ou Improvement]"
  }]
}
```

### Projet → `$NOTION_PROJECTS_DB_ID`

Inférer `Origin` depuis le contexte (ex: `Slack`, `Client`, `Interne`, `Granola`).

```json
{
  "parent": { "data_source_id": "$NOTION_PROJECTS_DB_ID" },
  "pages": [{
    "icon": "[emoji pertinent]",
    "properties": {
      "Nom": "[titre]",
      "Priority": "[priority choisie]",
      "Statut": "Raffinage / Découverte",
      "Origin": "[inféré du contexte]"
    },
    "content": "[contenu selon template Projet]"
  }]
}
```

> Ne pas inclure les propriétés calculées (Completion, RICE score, etc.) — elles sont auto-calculées.

---

## Étape 6 — Résultat

Afficher :
- Lien direct vers la page Notion créée
- 2 lignes : type, priorité, BDD cible

---

## Gotchas

**Extraction du `thread_ts` Slack.**
URL `.../p1741234567890123` → `thread_ts = 1741234567.890123` (insérer un point après les 10 premiers chiffres). Oublier ce point retourne une erreur silencieuse.

**`Notion:notion-search` retourne des pages archivées.**
Vérifier que les résultats ne sont pas archivés avant de signaler un doublon — une page archivée ne compte pas.

**`Notion:notion-search` cherche dans tout le workspace.**
Filtrer explicitement par `$NOTION_FEATURES_DB_ID` ou `$NOTION_PROJECTS_DB_ID` selon le type pour éviter les faux positifs de doublons.

**Ne pas inclure les propriétés calculées dans `Notion:notion-create-pages`.**
Completion, RICE score, etc. sont auto-calculées par Notion — les inclure provoque une erreur 400.
