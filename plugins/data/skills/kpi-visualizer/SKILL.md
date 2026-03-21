---
name: kpi-visualizer
description: Genere un dashboard produit visuel depuis PostHog avec KPIs, tendances et funnels.
compatibility: "Requires PostHog MCP (event-definitions-list, query-run) + ask_user_input_v0 + show_widget. Optional: Notion MCP (notion-fetch, notion-update-page)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Notion ou URL PostHog]"
---

# KPI Visualizer

> **Références techniques** : [`references/posthog-reference.md`](${CLAUDE_SKILL_DIR}/references/posthog-reference.md) · [`references/query-patterns.md`](${CLAUDE_SKILL_DIR}/references/query-patterns.md)

---

## Setup

Avant toute action, verifier si `${CLAUDE_PLUGIN_DATA}/config.json` existe (via Read).

**Si absent** — appeler AskUserQuestion pour collecter tous les IDs en un seul appel, puis ecrire le fichier :

```json
{
  "POSTHOG_PROJECT_ID": "<your-project-id>"
}
```

**Si present** — lire silencieusement et utiliser `config.POSTHOG_PROJECT_ID` dans la suite du workflow.

---

## Routing

| Trigger | Workflow |
|---------|----------|
| Page Notion + "KPIs", "tracking", "qu'est-ce qu'on devrait tracker" | -> **KPI Generator** |
| "dashboard", "stats", "metriques", "usage de", "compare V1 vs V2" | -> **Dashboard** |
| Les deux | -> KPI Generator puis Dashboard |

---

## Workflow B — Dashboard

### 1. Explorer PostHog en silence

URLs fournies -> sauter le scan HogQL, aller direct a l'interview.
Sinon, lancer en parallele :

```
event-definitions-list(q: "<mot-cle>")
query-run(HogQL: SELECT distinct $current_url, count() FROM events
  WHERE event='$pageview' AND $current_url LIKE '%mot-cle%'
  AND timestamp >= now() - INTERVAL 30 DAY GROUP BY 1 ORDER BY 2 DESC LIMIT 50)
```

### 2. Interviewer via ask_user_input_v0 (OBLIGATOIRE)

Options ancrees sur ce qui existe reellement. Pas de question sur la periode (-30d par defaut).

```javascript
ask_user_input_v0({ questions: [{
  question: "Quels elements veux-tu dans le dashboard ?",
  type: "multi_select",
  options: [ /* events reels, URLs reelles, tabs reels trouves */ ]
}]})
```

### 3. Toutes les queries en parallele

**Tendance / comparaison**
```json
{ "kind": "InsightVizNode", "source": { "kind": "TrendsQuery",
  "series": [{ "kind": "EventsNode", "event": "event_name", "custom_name": "Label", "math": "total" }],
  "dateRange": { "date_from": "-30d" }, "interval": "day",
  "trendsFilter": { "display": "ActionsLineGraph" } }}
```

Variantes : `"math": "dau"` · `"display": "BoldNumber"` · `"display": "ActionsBarValue"` · `"display": "ActionsPie"`

**Comparer deux pages par URL**
```json
{ "kind": "InsightVizNode", "source": { "kind": "TrendsQuery", "series": [
  { "kind": "EventsNode", "event": "$pageview", "custom_name": "V2", "math": "dau",
    "properties": [{ "key": "$current_url", "value": "/feature-v2", "operator": "icontains", "type": "event" }] },
  { "kind": "EventsNode", "event": "$pageview", "custom_name": "V1", "math": "dau",
    "properties": [
      { "key": "$current_url", "value": "/feature", "operator": "icontains", "type": "event" },
      { "key": "$current_url", "value": "/feature-v2", "operator": "not_icontains", "type": "event" }
    ] }
], "dateRange": { "date_from": "-30d" }, "interval": "day",
"trendsFilter": { "display": "ActionsLineGraph" } }}
```

> Tab specifique : ajouter `{ "key": "$current_url", "value": "?tab=xxx", "operator": "icontains", "type": "event" }`

**Funnel**
```json
{ "kind": "InsightVizNode", "source": { "kind": "FunnelsQuery",
  "series": [
    { "kind": "EventsNode", "event": "step_1", "custom_name": "Etape 1" },
    { "kind": "EventsNode", "event": "step_2", "custom_name": "Etape 2" }
  ],
  "dateRange": { "date_from": "-30d" },
  "funnelsFilter": { "funnelWindowInterval": 14, "funnelWindowIntervalUnit": "day" } }}
```

### 4. Dashboard avec show_widget

Chart.js CDN -> voir `## Configuration`.
Donnees injectees statiquement. Structure : KPI cards -> graphique principal -> charts secondaires.

### Dashboard PostHog natif (si explicitement demande)

```
entity-search(entities: ["dashboard"], query: <sujet>)
-> completer existant ou creer : dashboard-create + insight-create-from-query
-> lien : https://app.posthog.com/project/${config.POSTHOG_PROJECT_ID}/dashboard/[id]
```

---

## Gotchas

### PostHog

**`event-definitions-list` ne confirme pas que l'event a des donnees recentes.**
Toujours verifier avec une query HogQL sur 30j avant de marquer actif.

**Exclure V2 quand on filtre V1 par URL.**
`$current_url icontains /planning` matche aussi `/planning-v2`. Toujours ajouter `not_icontains /planning-v2` sur la serie V1.

**`LIMIT 100` par defaut dans HogQL.**
Ajouter `LIMIT 1000` ou plus pour les dashboards ou longues periodes.

**Les tabs dans les URLs sont des query params, pas des paths.**
`/planning-v2?tab=in_mission` -> filtrer avec `icontains ?tab=in_mission` (avec le `?`).

**`BoldNumber` avec multi-series retourne une valeur par serie, pas un total.**
Utiliser une seule serie sans filtre ou faire le calcul dans HogQL avec `countIf`.

### Notion

**`notion-update-page update_content` : `old_str` doit etre une correspondance exacte.**
Re-fetcher la page juste avant tout `update_content`.

**La section KPI peut contenir un tableau Notion natif (non markdown).**
Si la mise a jour echoue sur un tableau, re-fetcher pour voir le format exact retourne.

---

## Configuration

```
CHARTJS_CDN=https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js
```
