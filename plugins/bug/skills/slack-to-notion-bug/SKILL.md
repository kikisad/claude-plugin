---
name: slack-to-notion-bug
description: Cree un ticket de bug ou d'amelioration dans Notion a partir d'un message Slack.
compatibility: "Requires Notion MCP (notion-search, notion-create-pages) + Slack MCP (slack_read_thread, slack_read_channel)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Slack ou texte du message]"
---

# Slack -> Notion Bug

Cree un ticket dans la base **Taches** Notion a partir d'un message Slack.

---

## Etape 0 — Lire les liens Slack si fournis

- **Texte brut** : le message Slack est colle directement -> passer a l'etape 1
- **Lien Slack** : une URL `https://[workspace].slack.com/archives/...` est fournie -> lire le message d'abord

```
slack_read_thread(
  channel_id = [extrait de l'URL],
  thread_ts  = [timestamp extrait de l'URL, ex: p1234567890 -> 1234567890.000000]
)
```

> Dans une URL Slack du type `.../p1741234567890123`, le timestamp est `1741234567.890123` (inserer un point apres les 10 premiers chiffres).

Lire **l'integralite du fil** (message parent + reponses). Si plusieurs liens, les lire tous avant de continuer.

---

## Etape 1 — Analyser le message Slack

| Champ | Comment l'inferer |
|---|---|
| **Titre** | Resumer le probleme en une phrase courte et claire |
| **Type** | `Fix` si bug/dysfonctionnement, `Improvement` si amelioration/feature |
| **Priority** | Voir tableau ci-dessous |
| **Probleme** | Description detaillee du bug ou besoin |
| **Solution** | Si mentionnee ou evidente, sinon laisser vide |
| **Contexte** | Pour les Improvements : contexte metier |
| **Criteres d'acceptation** | Pour les Improvements : liste de criteres |
| **Factory** | `Dev` par defaut, sauf si precise autrement |

### Tableau de priorite

| Message contient | Priority |
|---|---|
| urgent, bloquant, critique, prod down, impossible d'utiliser | `High` |
| Gênant, impact important, client bloqué | `Medium` |
| mineur, cosmetique, amelioration, quand tu peux | `Low` |
| rien de precis | `Medium` par defaut |

---

## Etape 2 — Verifier les doublons dans Notion

Avant de creer quoi que ce soit, rechercher des tickets similaires dans la base **Taches**.

```json
{
  "data_source_url": "NOTION_TASKS_DB_URL",
  "query": "[mots-cles extraits du titre ou du probleme]",
  "page_size": 5,
  "max_highlight_length": 150
}
```

Faire **1 a 2 recherches** avec des formulations differentes si la premiere ne ramene rien de pertinent.

| Cas | Comportement |
|---|---|
| **Doublon evident** — meme probleme, meme composant | Arreter. Afficher le ticket existant avec son lien. |
| **Ticket similaire** — meme zone fonctionnelle | Afficher les similaires (max 3) et demander si creer quand meme. |
| **Aucun resultat similaire** | Continuer directement a l'etape suivante. |

---

## Etape 3 — Confirmer avec l'utilisateur (si ambigu)

Si le type, la priorite ou le titre sont ambigus, poser **une seule question** synthetique avant de creer.

Exemple : *"Je vais creer un bug High intitule 'Contrats envoyes marques A envoyer'. C'est bon ?"*

Si l'utilisateur dit "vas-y" ou donne le texte directement sans ambiguite -> creer directement.

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

Si un lien Slack est fourni comme source, ajouter :
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

```json
{
  "parent": { "data_source_id": "NOTION_TASKS_DB_ID" },
  "pages": [
    {
      "icon": "[voir ci-dessus]",
      "properties": {
        "Nom": "[titre]",
        "Type": "[Fix ou Improvement]",
        "Priority": "[priority label]",
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

## Configuration

```
NOTION_TASKS_DB_ID=<notion-database-id>
NOTION_TASKS_DB_URL=collection://<notion-database-id>
```

---

## Exemples

**Bug simple** : *"Y'a un double filtre consultant sur la page des habilitations"*
-> Type: `Fix`, Priority: `Low`, Titre: `Supprimer le deuxieme filtre consultant sur la page des habilitations`

**Bug urgent** : *"Plusieurs clients remontent que leurs contrats envoyes sont marques 'A envoyer', c'est bloquant !"*
-> Type: `Fix`, Priority: `High`, source Slack incluse

**Amelioration** : *"Il faudrait bloquer la modification des specificites de paie une fois que le consultant a complete sa paie"*
-> Type: `Improvement`, Priority: `High`, avec criteres d'acceptation generes
