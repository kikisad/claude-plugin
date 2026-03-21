---
name: slack-to-notion-bug
description: Cree un ticket de bug ou d'amelioration dans Notion a partir d'un message Slack.
compatibility: "Requires Notion MCP (notion-search, notion-create-pages) + Slack MCP (slack_read_thread, slack_read_channel)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Slack ou texte du message]"
---

# Slack -> Notion Bug

Cree un ticket dans la base **Features** Notion a partir d'un message Slack.

> Exemples : voir `${CLAUDE_SKILL_DIR}/references/examples.md`

---

## Setup

Avant toute action, verifier si `${CLAUDE_PLUGIN_DATA}/config.json` existe (via Read).

**Si absent** — appeler AskUserQuestion pour collecter tous les IDs en un seul appel, puis ecrire le fichier :

```json
{
  "NOTION_FEATURES_DB_ID": "<notion-database-id>",
  "SLACK_BUGS_CHANNEL_ID": "<slack-channel-id-optionnel>"
}
```

> `SLACK_BUGS_CHANNEL_ID` est optionnel — si l'utilisateur fournit un lien Slack, le channel_id est extrait de l'URL.

**Si present** — lire silencieusement et utiliser `config.NOTION_FEATURES_DB_ID` dans la suite du workflow.

---

## Etape 0 — Lire le message Slack

- **Texte brut** : le message est colle directement -> passer a l'etape 1
- **Lien Slack** : extraire `channel_id` et `thread_ts` de l'URL, puis :

```
slack_read_thread(
  channel_id = [extrait de l'URL, ou config.SLACK_BUGS_CHANNEL_ID],
  thread_ts  = [timestamp extrait de l'URL, ex: p1234567890 -> 1234567890.000000]
)
```

> Dans une URL Slack du type `.../p1741234567890123`, le timestamp est `1741234567.890123` (inserer un point apres les 10 premiers chiffres).

Lire **l'integralite du fil** (message parent + reponses). Si plusieurs liens, les lire tous avant de continuer.

---

## Etape 1 — Analyser le message Slack

Inferer les champs suivants :

| Champ | Comment l'inferer |
|---|---|
| **Titre** | Resumer le probleme en une phrase courte et claire |
| **Type** | `Fix` si bug/dysfonctionnement, `Improvement` si amelioration/feature |
| **Probleme** | Description detaillee du bug ou besoin |
| **Solution** | Si mentionnee ou evidente, sinon laisser vide |
| **Contexte** | Pour les Improvements : contexte metier |
| **Criteres d'acceptation** | Pour les Improvements : liste de criteres |
| **Factory** | `Dev` par defaut, sauf si precise autrement |

---

## Etape 2 — Demander la Priority a l'utilisateur

Presenter le titre et le type inferes, puis demander la priorite :

```
ask_user_input_v0({
  questions: [{
    question: "Priority pour '[titre infere]' ([type]) ?",
    type: "single_select",
    options: ["High", "Medium", "Low"]
  }]
})
```

---

## Etape 3 — Verifier les doublons dans Notion

Rechercher des tickets similaires dans la base **Features**.

```json
{
  "data_source_id": "${config.NOTION_FEATURES_DB_ID}",
  "query": "[mots-cles extraits du titre ou du probleme]",
  "page_size": 5,
  "max_highlight_length": 150
}
```

Faire **1 a 2 recherches** avec des formulations differentes si la premiere ne ramene rien.

| Cas | Comportement |
|---|---|
| **Doublon evident** | Arreter. Afficher le ticket existant avec son lien. |
| **Ticket similaire** | Afficher les similaires (max 3) et demander si creer quand meme. |
| **Aucun resultat** | Continuer directement. |

---

## Etape 4 — Construire le contenu Notion

### Pour un ticket `Fix` (bug)

```
icon: /icons/bug_red.svg

### Probleme
[Description du probleme extraite du message Slack]

### Solution
[Solution proposee, ou laisser vide si non connue]
```

Si un lien Slack est fourni, ajouter :
```
Source Slack : [lien slack]
```

### Pour un ticket `Improvement`

```
icon: emoji pertinent (ex: 🚀, ✨)

### Contexte
[Contexte metier]

### Description du probleme
[Probleme detaille]

---
**Criteres d'acceptation :**
- [ ] Critere 1
- [ ] Critere 2
```

---

## Etape 5 — Creer le ticket dans Notion

Si l'utilisateur a fourni un lien Notion direct vers une feature existante, creer la page dans cette feature.
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

> Ne pas inclure les proprietes calculees (Completion, Done SP, RICE score, etc.) — elles sont auto-calculees.

---

## Etape 6 — Presenter le resultat

Apres creation, afficher :
- Le titre du ticket cree
- Le lien direct vers la page Notion
- Un resume en 1 ligne (type, priorite)

---

## Gotchas

<!-- A enrichir au fil des runs -->
