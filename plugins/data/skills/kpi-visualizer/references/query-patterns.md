# Query Patterns — Référence générique

Patterns réutilisables pour n'importe quelle feature. Remplacer les placeholders `<...>`.

---

## Vérification d'events (toujours faire avant de marquer ✓)

```sql
SELECT event, count() as total, max(timestamp) as last_seen,
       countIf(timestamp >= now() - INTERVAL 7 DAY) as last_7d
FROM events
WHERE event LIKE '%<mot_clé>%'
AND timestamp >= now() - INTERVAL 30 DAY
GROUP BY event ORDER BY total DESC
```

---

## Comparer deux versions par URL

```json
{
  "series": [
    {
      "event": "$pageview", "custom_name": "V2", "math": "dau",
      "properties": [
        { "key": "$current_url", "value": "<url_v2>", "operator": "icontains", "type": "event" }
      ]
    },
    {
      "event": "$pageview", "custom_name": "V1", "math": "dau",
      "properties": [
        { "key": "$current_url", "value": "<url_v1>", "operator": "icontains", "type": "event" },
        { "key": "$current_url", "value": "<url_v2>", "operator": "not_icontains", "type": "event" }
      ]
    }
  ]
}
```
> ⚠️ Toujours exclure V2 de la série V1 avec `not_icontains` — sinon double comptage.

---

## Découvrir les URLs et tabs d'une feature

```sql
SELECT properties.$current_url as url, count() as views
FROM events
WHERE event = '$pageview'
AND properties.$current_url LIKE '%<feature>%'
AND timestamp >= now() - INTERVAL 30 DAY
GROUP BY url ORDER BY views DESC LIMIT 50
```

---

## Comparer deux périodes (delta)

```sql
SELECT
  last_period.count - prev_period.count as delta,
  round(100 * (last_period.count - prev_period.count) / prev_period.count, 1) as pct_change
FROM
  (SELECT countIf(timestamp >= now() - INTERVAL 7 DAY) as count FROM events WHERE event = '<event>') as last_period,
  (SELECT countIf(timestamp >= now() - INTERVAL 14 DAY AND timestamp < now() - INTERVAL 7 DAY) as count FROM events WHERE event = '<event>') as prev_period
```

---

## Taux de conversion entre deux events (funnel simplifié)

```sql
SELECT
  countIf(event = '<event_debut>') as started,
  countIf(event = '<event_fin>') as completed,
  round(100 * countIf(event = '<event_fin>') / countIf(event = '<event_debut>'), 1) as conversion_pct
FROM events
WHERE event IN ('<event_debut>', '<event_fin>')
AND timestamp >= now() - INTERVAL 30 DAY
```

---

## Utilisateurs actifs par jour (DAU) avec rolling average 7j

```sql
SELECT
  toDate(timestamp) as day,
  count(DISTINCT person_id) as dau,
  avg(count(DISTINCT person_id)) OVER (ORDER BY toDate(timestamp) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7d_avg
FROM events
WHERE event = '<event>'
AND timestamp >= now() - INTERVAL 30 DAY
GROUP BY day ORDER BY day
```

---

## First-time users (activation)

```sql
SELECT count(DISTINCT person_id) as new_users
FROM events
WHERE event = '<event>'
AND timestamp >= now() - INTERVAL 30 DAY
AND person_id NOT IN (
  SELECT DISTINCT person_id FROM events
  WHERE event = '<event>'
  AND timestamp < now() - INTERVAL 30 DAY
)
```

---

## Répartition par propriété (breakdown générique)

```sql
SELECT
  properties.<propriete> as segment,
  count() as total,
  count(DISTINCT person_id) as unique_users
FROM events
WHERE event = '<event>'
AND timestamp >= now() - INTERVAL 30 DAY
AND properties.<propriete> IS NOT NULL
GROUP BY segment ORDER BY total DESC LIMIT 20
```

---

## Multi-events sur le même graphe (TrendsQuery)

```json
{
  "kind": "TrendsQuery",
  "series": [
    { "kind": "EventsNode", "event": "<event_1>", "custom_name": "<label_1>", "math": "total" },
    { "kind": "EventsNode", "event": "<event_2>", "custom_name": "<label_2>", "math": "total" },
    { "kind": "EventsNode", "event": "<event_3>", "custom_name": "<label_3>", "math": "total" }
  ],
  "dateRange": { "date_from": "-30d" },
  "interval": "day",
  "trendsFilter": { "display": "ActionsLineGraph" }
}
```
Variantes display : `ActionsBarValue` (classement) · `BoldNumber` (KPI) · `ActionsPie` (répartition)

---

## KPIs agrégés en un seul appel (éviter N queries pour N KPIs)

```json
{
  "kind": "TrendsQuery",
  "series": [
    { "kind": "EventsNode", "event": "<event_1>", "custom_name": "KPI 1", "math": "total" },
    { "kind": "EventsNode", "event": "<event_2>", "custom_name": "KPI 2", "math": "dau" }
  ],
  "dateRange": { "date_from": "-30d" },
  "trendsFilter": { "display": "BoldNumber" }
}
```
> Retourne une valeur par série — pas un total agrégé. Pour un total combiné, utiliser HogQL.

---

## Segmenter mobile vs desktop

```sql
SELECT
  CASE
    WHEN properties.$os IN ('iOS', 'Android') THEN 'mobile'
    WHEN properties.$os IN ('Windows', 'Mac OS X', 'Linux', 'Chrome OS') THEN 'desktop'
    ELSE 'other'
  END AS device_type,
  count() AS total
FROM events
WHERE event = '<event>'
AND timestamp >= now() - INTERVAL 30 DAY
GROUP BY device_type ORDER BY total DESC
```

---

## Appliquer les filtres de date du dashboard (HogQL dynamique)

```sql
SELECT event, count()
FROM events
WHERE event = '<event>'
AND properties.$current_url LIKE '%<feature>%'
AND {filters}   -- applique automatiquement le date range du dashboard
GROUP BY event
```

---

## Running total (cumul dans le temps)

```sql
SELECT
  toDate(timestamp) AS day,
  COUNT(*) OVER (ORDER BY toDate(timestamp)) AS cumulative_total
FROM events
WHERE event = '<event>'
AND timestamp >= now() - INTERVAL 30 DAY
ORDER BY day
```

---

## Accéder à une propriété JSON imbriquée

```sql
SELECT JSONExtractString(properties, '<nested_key>') AS value, count()
FROM events
WHERE event = '<event>'
GROUP BY value ORDER BY count() DESC
```
