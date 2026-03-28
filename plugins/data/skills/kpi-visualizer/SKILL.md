---
name: kpi-visualizer
description: Génère un dashboard produit visuel depuis PostHog avec KPIs, tendances et funnels. Utiliser quand l'utilisateur mentionne "dashboard", "stats", "métriques", "usage de", "compare V1 vs V2", ou fournit une URL PostHog.
compatibility: "Requires PostHog MCP (event-definitions-list, query-run). Optional: Notion MCP (notion-fetch, notion-update-page)"
allowed-tools: Read
argument-hint: "[lien Notion ou URL PostHog]"
---

> **Références techniques** : [`references/posthog-reference.md`](${CLAUDE_SKILL_DIR}/references/posthog-reference.md) · [`references/query-patterns.md`](${CLAUDE_SKILL_DIR}/references/query-patterns.md)

---

## Prerequisites

**MCPs requis :**
- PostHog MCP connecté (`PostHog:event-definitions-list`, `PostHog:query-run`)
- Notion MCP optionnel (`Notion:notion-fetch`, `Notion:notion-update-page`)

Si le MCP PostHog est absent → arrêter et indiquer lequel configurer.

**Variables d'environnement :**

| Variable | Utilisation |
|---|---|
| `$POSTHOG_PROJECT_ID` | ID projet pour les liens de dashboard natif PostHog |

Si vide → AskUserQuestion, puis écrire dans `.claude/settings.local.json` sous `env.POSTHOG_PROJECT_ID`.

---

## Routing

| Trigger | Workflow |
|---------|----------|
| Page Notion + "KPIs", "tracking", "qu'est-ce qu'on devrait tracker" | -> **KPI Generator** |
| "dashboard", "stats", "métriques", "usage de", "compare V1 vs V2" | -> **Dashboard** |
| Les deux | -> KPI Generator puis Dashboard |

---

## Workflow — Dashboard

### 1. Explorer PostHog en silence

URLs fournies -> sauter le scan HogQL, aller directement à l'interview.
Sinon, lancer en parallèle :

```
PostHog:event-definitions-list(q: "<mot-clé>")
PostHog:query-run(HogQL: SELECT distinct $current_url, count() FROM events
  WHERE event='$pageview' AND $current_url LIKE '%mot-cle%'
  AND timestamp >= now() - INTERVAL 30 DAY GROUP BY 1 ORDER BY 2 DESC LIMIT 50)
```

### 2. Interviewer via AskUserQuestion (OBLIGATOIRE)

Options ancrées sur ce qui existe réellement. Pas de question sur la période (-30d par défaut).

```
AskUserQuestion: "Quels éléments veux-tu dans le dashboard ?
Options disponibles : [liste des events réels / URLs réelles / tabs trouvés]
(tu peux en choisir plusieurs)"
```

### 3. Toutes les queries en parallèle

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

> Tab spécifique : ajouter `{ "key": "$current_url", "value": "?tab=xxx", "operator": "icontains", "type": "event" }`

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

Utiliser l'outil natif Claude (artifact HTML) pour rendre les graphiques — pas de CDN externe.
Données injectées statiquement en inline. Structure : KPI cards -> graphique principal -> charts secondaires.

### Dashboard PostHog natif (si explicitement demandé)

```
PostHog:entity-search(entities: ["dashboard"], query: <sujet>)
-> compléter existant ou créer : PostHog:dashboard-create + PostHog:insight-create-from-query
-> lien : https://app.posthog.com/project/$POSTHOG_PROJECT_ID/dashboard/[id]
```

---

## Gotchas

### PostHog

**`PostHog:event-definitions-list` ne confirme pas que l'event a des données récentes.**
Toujours vérifier avec `PostHog:query-run` sur 30j avant de marquer actif.

**Exclure V2 quand on filtre V1 par URL.**
`$current_url icontains /planning` matche aussi `/planning-v2`. Toujours ajouter `not_icontains /planning-v2` sur la série V1.

**`LIMIT 100` par défaut dans HogQL.**
Ajouter `LIMIT 1000` ou plus pour les dashboards ou longues périodes.

**Les tabs dans les URLs sont des query params, pas des paths.**
`/planning-v2?tab=in_mission` -> filtrer avec `icontains ?tab=in_mission` (avec le `?`).

**`BoldNumber` avec multi-series retourne une valeur par série, pas un total.**
Utiliser une seule série sans filtre ou faire le calcul dans HogQL avec `countIf`.

### Notion

**`Notion:notion-update-page update_content` : `old_str` doit être une correspondance exacte.**
Re-fetcher via `Notion:notion-fetch` juste avant tout `update_content`.

**La section KPI peut contenir un tableau Notion natif (non markdown).**
Si la mise à jour échoue sur un tableau, re-fetcher pour voir le format exact retourné.

