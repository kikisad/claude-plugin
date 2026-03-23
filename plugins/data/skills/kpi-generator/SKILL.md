---
name: kpi-generator
description: Produit un schéma de tracking complet pour une feature : baseline avant dev + nouveaux KPIs après dev. Utiliser quand l'utilisateur mentionne des KPIs à définir, "qu'est-ce qu'on devrait tracker", "on veut mesurer cette feature", ou fournit un lien Notion de feature sans KPIs définis.
compatibility: "Requires Notion MCP (notion-fetch, notion-update-page) + PostHog MCP (event-definitions-list, query-run)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Notion de la feature]"
---

## Setup

Vérifier si `${CLAUDE_PLUGIN_DATA}/config.json` existe.

**Si absent** — AskUserQuestion pour collecter en un seul appel :
- ID projet PostHog

Puis écrire `${CLAUDE_PLUGIN_DATA}/config.json`.

**Si présent** — lire silencieusement et continuer.

---

## Étape 1 — Lire le contexte (en parallèle)
```
notion-fetch(url: $ARGUMENTS)
event-definitions-list(q: "<mot-clé de la feature>")
```

De la page Notion, extraire :
- Objectif de la feature
- Actions clés des utilisateurs
- Données métier impactées (ce qui change en BDD)
- Section KPI existante — si présente, la challenger (voir Étape 2)

**Si le contexte est insuffisant** — poser des questions via AskUserQuestion avant de continuer.

Vérifier les events trouvés avec une query HogQL sur 30j :
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
- ⚠️ Inactif — existe dans PostHog mais 0 données sur 30j
- 🔲 À créer — absent de PostHog

---

## Étape 2 — Challenger les KPIs existants (si section KPI présente)

Si la page Notion a déjà une section KPI, invoquer `@kpi-challenger` pour valider chaque KPI :
- Correspond à un event actif ou une donnée BDD réelle → garder
- Ne correspond à rien dans PostHog et pas en BDD → proposer de supprimer ou reformuler

---

## Étape 3 — Proposer via AskUserQuestion (OBLIGATOIRE)

Construire les options à partir de ce qui a été détecté. Séparer PostHog vs BDD.

AskUserQuestion avec deux questions en un seul appel :

- "Quels KPIs veux-tu suivre en baseline (avant le dev) ?"
  options : events existants détectés + données BDD identifiées

- "Quels nouveaux KPIs veux-tu mesurer après le dev ?"
  options : nouveaux comportements induits par la feature + comparaisons V1/V2 si applicable

Maximum 2-5 KPIs par tableau.

---

## Étape 4 — Produire le schéma de tracking

### Baseline — avant de commencer
| KPI | Source | Event / Requête | Statut actuel |
|-----|--------|-----------------|---------------|
| ... | PostHog / BDD | ... | ✅ / ⚠️ / 🔲 |

**Règles baseline :**
- Inclure uniquement ce qui permet d'établir un point de référence avant les changements
- Si un event est inactif (⚠️) → le signaler comme "à réactiver avant dev"
- `$pageview` filtré par URL suffit pour mesurer les visites — ne pas créer un event dédié

### Nouveaux KPIs — après le dev
| KPI | Source | Event prévu | Ce que ça mesure |
|-----|--------|-------------|-----------------|
| ... | PostHog / BDD | ... | ... |

**Règles nouveaux KPIs :**
- Nommage events PostHog : `object_action` ou `object_scope_action` — snake_case, verbes au passé
- Verbes : `clicked`, `viewed`, `submitted`, `started`, `ended`, `canceled`, `failed`
- Ne pas créer un event PostHog si `$pageview` + filtre URL suffit
- Ne pas dupliquer ce qui est déjà mesurable en BDD

---

## Étape 5 — Mettre à jour la section KPI dans Notion

`notion-update-page` avec `update_content` pour remplacer ou créer la section `## KPIs`.

Format cible :
```
## KPIs

> Inutile de tout tracker. On traque ce qui permet de comprendre les usages réels et de prendre des décisions avec de l'impact.

### Baseline — avant de commencer
[tableau]

### Nouveaux KPIs — après le dev
[tableau]
```

Si la section n'existe pas → la créer à la fin de la page.

---

## Gotchas

**`event-definitions-list` ne confirme pas que l'event a des données récentes.**
Toujours vérifier avec une query HogQL sur 30j avant de marquer actif.

**`$pageview` matche les URLs qui contiennent le pattern.**
`/planning` matche aussi `/planning-v2`. Toujours vérifier les URLs exactes avant de proposer un filtre.

**Une section KPI déjà présente dans Notion n'est pas forcément valide.**
Passer systématiquement par `@kpi-challenger` si elle existe.

**Les données BDD ne nécessitent pas d'event PostHog.**
Volumes, statuts, montants → Metabase suffit. Ne pas dupliquer dans PostHog.

**Contexte insuffisant = questions obligatoires.**
Ne jamais supposer l'objectif ou les actions clés. Poser la question plutôt que d'inventer.

---

## Configuration

MCPs requis : Notion (`notion-fetch`, `notion-update-page`) + PostHog (`event-definitions-list`, `query-run`)
