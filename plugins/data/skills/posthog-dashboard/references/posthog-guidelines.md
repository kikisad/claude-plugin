# PostHog — Référence technique

Source : https://posthog.com/docs

> Ce fichier = lookup table pure. Pour les patterns SQL/JSON copy-paste → voir `query-patterns.md`

---

## Tables HogQL

| Table | Contenu |
|-------|---------|
| `events` | Tous les events (event, timestamp, properties, person_id, distinct_id) |
| `persons` | Profils utilisateurs et leurs propriétés |
| `groups` | Groupes d'utilisateurs |
| `raw_session_replay_events` | Sessions enregistrées |

Accès aux propriétés en dot notation : `properties.$current_url`, `person.properties.$initial_browser`

---

## Types de queries (via `query-run`)

| Type | Usage |
|------|-------|
| `TrendsQuery` | Séries temporelles, volumes, DAU, comparaisons |
| `FunnelsQuery` | Taux de conversion entre étapes séquentielles |
| `RetentionQuery` | Rétention semaine par semaine |
| `PathsQuery` | Parcours utilisateurs entre events |
| `HogQLQuery` | SQL direct — exploration, vérification, calculs custom |
| `DataVisualizationNode` | Wrapper visuel |

---

## Propriétés système ($) — capturées automatiquement

| Propriété | Valeur |
|-----------|--------|
| `$current_url` | URL complète avec query params |
| `$pathname` | Chemin sans domaine |
| `$host` | Domaine uniquement |
| `$browser` / `$browser_version` | Navigateur |
| `$os` / `$os_version` | Système d'exploitation |
| `$device_type` | `Desktop` / `Mobile` / `Tablet` |
| `$referrer` / `$referring_domain` | Source de trafic |
| `$session_id` | ID de session |
| `$lib` / `$lib_version` | SDK PostHog utilisé |
| `$geoip_country_code` / `$geoip_city_name` | Géolocalisation |

---

## Math modes — TrendsQuery `series[].math`

| Valeur | Calcule |
|--------|---------|
| `total` | Nombre total d'occurrences |
| `dau` | Utilisateurs uniques / jour (basé sur `person_id`) |
| `weekly_active` | Utilisateurs actifs sur 7j glissants |
| `monthly_active` | Utilisateurs actifs sur 30j glissants |
| `unique_session` | Sessions uniques |
| `first_time_for_user` | Première occurrence — utile pour l'activation |
| `avg` / `sum` / `min` / `max` | Agrégation numérique — nécessite `math_property` |
| `median` / `p75` / `p90` / `p99` | Percentiles — nécessite `math_property` |

---

## Display modes — TrendsQuery `trendsFilter.display`

| Valeur | Rendu |
|--------|-------|
| `ActionsLineGraph` | Courbe temporelle (défaut) |
| `ActionsBarValue` | Barres horizontales — classement |
| `ActionsBar` | Barres verticales empilées |
| `BoldNumber` | Chiffre KPI unique |
| `ActionsPie` | Camembert |
| `WorldMap` | Carte mondiale par pays |

---

## Opérateurs de filtre — `properties[].operator`

| Opérateur | Signification |
|-----------|--------------|
| `exact` | Égalité stricte |
| `is_not` | Différent de |
| `icontains` | Contient (insensible à la casse) |
| `not_icontains` | Ne contient pas |
| `regex` | Expression régulière |
| `gt` / `lt` / `gte` / `lte` | Comparaison numérique |
| `is_set` | La propriété existe |
| `is_not_set` | La propriété n'existe pas |

---

## Notes importantes

- PostHog merge les anonymous users quand `identify` est envoyé → un user peut avoir plusieurs `distinct_id`
- `dau` compte les `person_id` uniques après merge — pas les `distinct_id`
- Les propriétés personne sont stockées sur chaque event → filtres sur person properties rapides
- `{filters}` dans une query HogQL applique dynamiquement les filtres de date du dashboard
