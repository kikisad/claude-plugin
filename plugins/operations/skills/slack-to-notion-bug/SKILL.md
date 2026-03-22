---
name: slack-to-notion-bug
description: Crée un ticket de bug ou d'amélioration dans Notion à partir d'un message Slack. Utiliser quand l'utilisateur colle un message Slack, un lien Slack, ou mentionne "créer un ticket", "logger ce bug", "ajouter dans Notion".
compatibility: "Requires Notion MCP (notion-search, notion-create-pages) + Slack MCP (slack_read_thread, slack_read_channel)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Slack ou texte du message]"
---

> Exemples : voir `${CLAUDE_SKILL_DIR}/references/examples.md`

---

## Setup

Avant toute action, vérifier si `${CLAUDE_PLUGIN_DATA}/config.json` existe (via Read).

**Si absent** — appeler AskUserQuestion pour collecter tous les IDs en un seul appel, puis écrire le fichier :

```json
{
  "NOTION_FEATURES_DB_ID": "<notion-database-id>",
  "SLACK_BUGS_CHANNEL_ID": "<slack-channel-id-optionnel>"
}
```

> `SLACK_BUGS_CHANNEL_ID` est optionnel — si l'utilisateur fournit un lien Slack, le channel_id est extrait de l'URL.

**Si présent** — lire silencieusement et utiliser `config.NOTION_FEATURES_DB_ID` dans la suite du workflow.

---

## Étape 0 — Lire le message Slack

- **Texte brut** : le message est collé directement -> passer à l'étape 1
- **Lien Slack** : extraire `channel_id` et `thread_ts` de l'URL, puis :

```
slack_read_thread(
  channel_id = [extrait de l'URL, ou config.SLACK_BUGS_CHANNEL_ID],
  thread_ts  = [timestamp extrait de l'URL, ex: p1234567890 -> 1234567890.000000]
)
```

> Dans une URL Slack du type `.../p1741234567890123`, le timestamp est `1741234567.890123` (insérer un point après les 10 premiers chiffres).

Lire **l'intégralité du fil** (message parent + réponses). Si plusieurs liens, les lire tous avant de continuer.

---

## Étape 1 — Analyser le message Slack

Inférer les champs suivants :

| Champ | Comment l'inférer |
|---|---|
| **Titre** | Résumer le problème en une phrase courte et claire |
| **Type** | `Fix` si bug/dysfonctionnement, `Improvement` si amélioration/feature |
| **Problème** | Description détaillée du bug ou besoin |
| **Solution** | Si mentionnée ou évidente, sinon laisser vide |
| **Contexte** | Pour les Improvements : contexte métier |
| **Critères d'acceptation** | Pour les Improvements : liste de critères |
| **Factory** | `Dev` par défaut, sauf si précisé autrement |

---

## Étape 2 — Demander la priorité à l'utilisateur

Présenter le titre et le type inférés, puis demander la priorité :

```
ask_user_input_v0({
  questions: [{
    question: "Priority pour '[titre inféré]' ([type]) ?",
    type: "single_select",
    options: ["High", "Medium", "Low"]
  }]
})
```

---

## Étape 3 — Vérifier les doublons dans Notion

Rechercher des tickets similaires dans la base **Features**.

```json
{
  "data_source_id": "${config.NOTION_FEATURES_DB_ID}",
  "query": "[mots-clés extraits du titre ou du problème]",
  "page_size": 5,
  "max_highlight_length": 150
}
```

Faire **1 à 2 recherches** avec des formulations différentes si la première ne ramène rien.

| Cas | Comportement |
|---|---|
| **Doublon évident** | Arrêter. Afficher le ticket existant avec son lien. |
| **Ticket similaire** | Afficher les similaires (max 3) et demander si créer quand même. |
| **Aucun résultat** | Continuer directement. |

---

## Étape 4 — Construire le contenu Notion

### Pour un ticket `Fix` (bug)

```
icon: /icons/bug_red.svg

### Problème
[Description du problème extraite du message Slack]

### Solution
[Solution proposée, ou laisser vide si non connue]
```

Si un lien Slack est fourni, ajouter :
```
Source Slack : [lien slack]
```

### Pour un ticket `Improvement`

```
icon: emoji pertinent (ex: 🚀, ✨)

### Contexte
[Contexte métier]

### Description du problème
[Problème détaillé]

---
**Critères d'acceptation :**
- [ ] Critère 1
- [ ] Critère 2
```

---

## Étape 5 — Créer le ticket dans Notion

Si l'utilisateur a fourni un lien Notion direct vers une feature existante, créer la page dans cette feature.
Sinon, utiliser `config.NOTION_FEATURES_DB_ID`.

```json
{
  "parent": { "data_source_id": "${config.NOTION_FEATURES_DB_ID}" },
  "pages": [
    {
      "icon": "[voir ci-dessus]",
      "properties": {
        "Nom": "[titre]",
        "Type": "[Fix ou Improvement]",
        "Priority": "[priority choisie par l'utilisateur]",
        "Etat": "Raffinage",
        "DoD": "__NO__",
        "Feature flag": "__NO__",
        "Scope change?": "__NO__",
        "Factory": ["Dev"]
      },
      "content": "[contenu markdown selon le type]"
    }
  ]
}
```

> Ne pas inclure les propriétés calculées (Completion, Done SP, RICE score, etc.) — elles sont auto-calculées.

---

## Étape 6 — Présenter le résultat

Après création, afficher :
- Le titre du ticket créé
- Le lien direct vers la page Notion
- Un résumé en 1 ligne (type, priorité)

---

## Gotchas

<!-- A enrichir au fil des runs -->
