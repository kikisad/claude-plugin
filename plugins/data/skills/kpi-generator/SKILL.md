---
name: kpi-generator
description: Propose les KPIs essentiels pour une feature a partir d'une page Notion de contexte et les ajoute dans Notion.
compatibility: "Requires Notion MCP (notion-fetch, notion-update-page) + PostHog MCP (event-definitions-list, query-run)"
disable-model-invocation: true
allowed-tools: Read
argument-hint: "[lien Notion de la feature]"
---

# KPI Generator

Propose les KPIs essentiels pour une feature a partir d'une page Notion de contexte.

## Philosophie

**Moins c'est plus.** 3-5 metriques qui permettent de prendre des decisions, pas plus.

Les KPIs se repartissent en deux categories :
- **PostHog** -> comportements utilisateurs : clics, navigation, usage des features. Ne pas creer un event pour quelque chose deja disponible en BDD ou via `$pageview`.
- **BDD (Metabase)** -> donnees metier : volumes crees, statuts, montants.

> `$pageview` existe par defaut dans PostHog et capture toutes les visites de pages — ne jamais proposer un event `feature_viewed` si `$pageview` filtre par URL suffit.

## Conventions PostHog

- Format events : `object_action` ou `object_scope_action` — snake_case, verbes au **passe**
- Verbes : `clicked`, `viewed`, `submitted`, `started`, `ended`, `canceled`, `failed`

---

## Phase 1 — Lire le contexte (en parallele)

Lancer simultanement :
```
notion-fetch(url: <lien fourni>)
event-definitions-list(q: "<mot-cle de la feature>")
```

De la page Notion, extraire :
- **Nom et objectif** de la feature
- **Section KPI existante** si presente -> ne pas dupliquer
- **Actions cles des utilisateurs** (navigation, clics, usages de features)
- **Donnees metier cles** (ce qui change en BDD : volumes, statuts, montants)
- **V1 existante ?** -> quels events V1 sont deja trackes

### Verifier que les events ont des donnees reelles

Lancer une query HogQL pour verifier le volume reel sur 30j :

```json
{
  "kind": "DataVisualizationNode",
  "source": {
    "kind": "HogQLQuery",
    "query": "SELECT event, count() as total, max(timestamp) as last_seen FROM events WHERE event IN ('event_a', 'event_b') AND timestamp >= now() - INTERVAL 30 DAY GROUP BY event ORDER BY total DESC"
  }
}
```

- Actif -> volume + date last seen
- Existant mais inactif -> 0 donnees sur 30j
- A creer -> absent de PostHog

---

## Phase 2 — Proposer via ask_user_input_v0 (OBLIGATOIRE)

Construire les options a partir de la spec. Separer clairement PostHog vs BDD.

```javascript
ask_user_input_v0({
  questions: [
    {
      question: "Quels KPIs veux-tu inclure ?",
      type: "multi_select",
      options: [
        // PostHog — comportements utilisateurs
        "Usage des filtres — est-ce que les nouveaux filtres sont utilises (PostHog)",
        "Adoption de la page — nb de visites /ma-feature via $pageview (PostHog)",
        // BDD — donnees metier
        "Nb de red flags poses — combien de societes bloquees (BDD)",
        "Contrats bloques — nb de contractualisations empechees (BDD)",
      ]
    }
  ]
})
```

---

## Phase 3 — Construire le tableau KPI

Deux sections distinctes, **maximum 5-6 KPIs au total** :

### KPIs PostHog (comportements utilisateurs)
| KPI | Pourquoi c'est utile |
|-----|---------------------|
| Usage des filtres (`company_filter_applied`) | Verifier que les nouveaux filtres sont reellement utilises |
| Visites page (`$pageview` filtre par URL) | Mesurer si l'adoption augmente |

### KPIs BDD (Metabase)
| KPI | Pourquoi c'est utile |
|-----|---------------------|
| Nb de red flags poses | Mesurer l'adoption de la feature de securisation |
| Nb de contrats bloques | Quantifier l'impact financier direct |

### Regles
- Ne jamais creer un event PostHog si `$pageview` + filtre URL suffit
- Ne pas dupliquer ce qui est deja en BDD dans PostHog
- Marquer les events existants (actif) vs a creer
- Si V1/V2 : inclure un KPI de comparaison de trafic via `$pageview`

---

## Phase 4 — Mettre a jour la section KPI dans Notion

Utiliser `notion-update-page` avec `update_content` pour remplacer la section KPI.

Format cible dans la page :
```
## KPIs

### PostHog — Comportements utilisateurs
| KPI | Pourquoi c'est utile |
| --- | --- |
| Usage des filtres (`company_filter_applied`) | Verifier que les nouveaux filtres sont reellement utilises |

### BDD — Donnees metier
| KPI | Pourquoi c'est utile |
| --- | --- |
| Nb de red flags poses | Mesurer l'adoption de la feature de securisation |

> **Event a instrumenter** — `company_filter_applied` (prop `filter_type`) a creer cote front.
```

> Si la section KPI n'existe pas -> la creer a la fin du contenu de la page.
