---
name: kpi-generator
description: Produit un schema de tracking complet pour une feature. Pose des questions si le contexte est insuffisant. Tracking baseline avant dev + nouveaux KPIs apres dev.
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Notion de la feature]"
---

# KPI Generator

Produit le schema de tracking complet d'une feature : ce qu'on mesure avant de toucher au code (baseline) et ce qu'on instrumente apres le dev (nouveaux KPIs).

> **Philosophie** : inutile de tout tracker. On traque ce qui permet de comprendre les usages reels et de prendre des decisions avec de l'impact.

> **Si le lien Notion fourni ne contient pas assez de contexte sur la feature** — poser des questions via AskUserQuestion avant de continuer : objectif de la feature, actions cles des utilisateurs, donnees metier impactees.

---

## Setup

Verifier si `${CLAUDE_PLUGIN_DATA}/config.json` existe.

**Si absent** — AskUserQuestion pour collecter en un seul appel :
- ID projet PostHog

Puis ecrire `${CLAUDE_PLUGIN_DATA}/config.json`.

**Si present** — lire silencieusement et continuer.

---

## Phase 1 — Lire le contexte (en parallele)
```
notion-fetch(url: $ARGUMENTS)
event-definitions-list(q: "<mot-cle de la feature>")
```

De la page Notion, extraire :
- Objectif de la feature
- Actions cles des utilisateurs
- Donnees metier impactees (ce qui change en BDD)
- Section KPI existante — si presente, la challenger (voir Phase 2)

**Si le contexte est insuffisant** — poser des questions via AskUserQuestion avant de continuer.

Verifier les events trouves avec une query HogQL sur 30j :
```json
{
  "kind": "DataVisualizationNode",
  "source": {
    "kind": "HogQLQuery",
    "query": "SELECT event, count() as total, max(timestamp) as last_seen FROM events WHERE event IN ('event_a', 'event_b') AND timestamp >= now() - INTERVAL 30 DAY GROUP BY event ORDER BY total DESC"
  }
}
```

Statuts possibles :
- ✅ Actif — volume > 0 sur 30j
- ⚠️ Inactif — existe dans PostHog mais 0 donnees sur 30j
- 🔲 A creer — absent de PostHog

---

## Phase 2 — Challenger les KPIs existants (si section KPI presente)

Si la page Notion a deja une section KPI, invoquer `@kpi-challenger` pour valider chaque KPI :
- Correspond a un event actif ou une donnee BDD reelle → garder
- Ne correspond a rien dans PostHog et pas en BDD → proposer de supprimer ou reformuler

---

## Phase 3 — Proposer via AskUserQuestion (OBLIGATOIRE)

Construire les options a partir de ce qui a ete detecte. Separer PostHog vs BDD.

AskUserQuestion avec deux questions en un seul appel :

- "Quels KPIs veux-tu suivre en baseline (avant le dev) ?"
  options : events existants detectes + donnees BDD identifiees

- "Quels nouveaux KPIs veux-tu mesurer apres le dev ?"
  options : nouveaux comportements induits par la feature + comparaisons V1/V2 si applicable

Maximum 2-5 KPIs par tableau.

---

## Phase 4 — Produire le schema de tracking

### Baseline — avant de commencer
| KPI | Source | Event / Requete | Statut actuel |
|-----|--------|-----------------|---------------|
| ... | PostHog / BDD | ... | ✅ / ⚠️ / 🔲 |

**Regles baseline :**
- Inclure uniquement ce qui permet d'etablir un point de reference avant les changements
- Si un event est inactif (⚠️) → le signaler comme "a reactiver avant dev"
- `$pageview` filtre par URL suffit pour mesurer les visites — ne pas creer un event dedie

### Nouveaux KPIs — apres le dev
| KPI | Source | Event prevu | Ce que ca mesure |
|-----|--------|-------------|-----------------|
| ... | PostHog / BDD | ... | ... |

**Regles nouveaux KPIs :**
- Nommage events PostHog : `object_action` ou `object_scope_action` — snake_case, verbes au passe
- Verbes : `clicked`, `viewed`, `submitted`, `started`, `ended`, `canceled`, `failed`
- Ne pas creer un event PostHog si `$pageview` + filtre URL suffit
- Ne pas dupliquer ce qui est deja mesurable en BDD

---

## Phase 5 — Mettre a jour la section KPI dans Notion

`notion-update-page` avec `update_content` pour remplacer ou creer la section `## KPIs`.

Format cible :
```
## KPIs

> Inutile de tout tracker. On traque ce qui permet de comprendre les usages reels et de prendre des decisions avec de l'impact.

### Baseline — avant de commencer
[tableau]

### Nouveaux KPIs — apres le dev
[tableau]
```

Si la section n'existe pas → la creer a la fin de la page.

---

## Gotchas

**`event-definitions-list` ne confirme pas que l'event a des donnees recentes.**
Toujours verifier avec une query HogQL sur 30j avant de marquer actif.

**`$pageview` matche les URLs qui contiennent le pattern.**
`/planning` matche aussi `/planning-v2`. Toujours verifier les URLs exactes avant de proposer un filtre.

**Une section KPI deja presente dans Notion n'est pas forcement valide.**
Passer systematiquement par `@kpi-challenger` si elle existe.

**Les donnees BDD ne necessitent pas d'event PostHog.**
Volumes, statuts, montants → Metabase suffit. Ne pas dupliquer dans PostHog.

**Contexte insuffisant = questions obligatoires.**
Ne jamais supposer l'objectif ou les actions cles. Poser la question plutot que d'inventer.

---

## Configuration

MCPs requis : Notion (`notion-fetch`, `notion-update-page`) + PostHog (`event-definitions-list`, `query-run`)