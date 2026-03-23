---
name: create-ticket
description: Crée un ticket (Bug, Improvement ou Projet) dans Notion à partir de n'importe quelle source. Utiliser quand l'utilisateur mentionne "créer un ticket", "logger ce bug", "ajouter dans Notion", ou colle un message Slack, un lien Notion, ou une réunion Granola.
compatibility: "Requires Notion MCP (notion-search, notion-create-pages) + Slack MCP (slack_read_thread) + optionally Granola MCP (get_meeting_transcript, query_granola_meetings)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Slack, lien Notion, nom de réunion Granola, ou texte brut]"
---

> Templates de contenu : `${CLAUDE_SKILL_DIR}/references/templates.md`

---

## Setup

Avant toute action, lire `${CLAUDE_PLUGIN_DATA}/config.json` via Read.

**Si absent** — appeler AskUserQuestion pour collecter les deux IDs en un seul appel, puis écrire le fichier :

```json
{
  "NOTION_FEATURES_DB_ID": "<notion-database-id>",
  "NOTION_PROJECTS_DB_ID": "<notion-database-id>"
}
```

**Si présent** — lire silencieusement et utiliser les deux IDs dans la suite.

---

## Étape 0 — Lire l'input

| Type d'input | Action |
|---|---|
| **Texte brut** | Analyser directement |
| **Lien Slack** | Extraire `channel_id` et `thread_ts` de l'URL → `slack_read_thread(channel_id, thread_ts)`. Lire le fil complet (parent + réponses). |
| **Lien Notion** | `notion-fetch(url)` — lire pour contexte uniquement, extraire les éléments pertinents |
| **Granola** | Si lien ou nom de réunion → `get_meeting_transcript` ou `query_granola_meetings`. Si texte collé directement → analyser tel quel. |

> Conversion timestamp Slack : URL `.../p1741234567890123` → `thread_ts = 1741234567.890123` (point après les 10 premiers chiffres).

Si plusieurs liens fournis, les lire tous avant de continuer.

---

## Étape 1 — Analyser et annoncer la décision

Inférer :

| Champ | Comment l'inférer |
|---|---|
| **Titre** | Phrase courte et claire résumant le sujet |
| **Problème** | Description détaillée du bug ou besoin |
| **Solution** | Si mentionnée ou évidente, sinon laisser vide |
| **Type** | Voir règle ci-dessous |

**Règle de décision :**
- Durée estimée > 1 jour → **Projet** (BDD Projets)
- Sinon → **Bug/Improvement** (`Fix` si dysfonctionnement, `Improvement` si amélioration/feature) (BDD Features)

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

```
AskUserQuestion: "Priority pour '[titre inféré]' ([type]) ? (High / Medium / Low)"
```

---

## Étape 3 — Vérifier les doublons

Chercher dans la BDD cible (Features ou Projets selon le type décidé à l'étape 1). Faire 1 à 2 recherches avec des formulations différentes.

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

### Bug / Improvement → `config.NOTION_FEATURES_DB_ID`

```json
{
  "parent": { "data_source_id": "${config.NOTION_FEATURES_DB_ID}" },
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

### Projet → `config.NOTION_PROJECTS_DB_ID`

Inférer `Origin` depuis le contexte (ex: `Slack`, `Client`, `Interne`, `Granola`).

```json
{
  "parent": { "data_source_id": "${config.NOTION_PROJECTS_DB_ID}" },
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

<!-- A enrichir au fil des runs -->
