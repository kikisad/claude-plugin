---
name: kpi-visualizer
description: Genere un dashboard visuel depuis PostHog avec tendances, funnels et KPIs. Accepte une page Notion en contexte. Pose des questions si le contexte est insuffisant.
disable-model-invocation: true
argument-hint: "[lien Notion ou URL PostHog]"
---

# KPI Visualizer

> Références techniques : [`references/posthog-reference.md`](${CLAUDE_SKILL_DIR}/references/posthog-reference.md) · [`references/query-patterns.md`](${CLAUDE_SKILL_DIR}/references/query-patterns.md)

---

## Setup

Verifier si `${CLAUDE_PLUGIN_DATA}/config.json` existe.

**Si absent** — AskUserQuestion pour collecter en un seul appel :
- ID projet PostHog

Puis ecrire `${CLAUDE_PLUGIN_DATA}/config.json`.

**Si present** — lire silencieusement et utiliser `config.POSTHOG_PROJECT_ID`.

---

## Phase 1 — Lire le contexte

**Page Notion fournie** — lancer en parallele :
```
notion-fetch(url: $ARGUMENTS)
event-definitions-list(q: "<mot-cle>")
```
Si section KPI presente → challenger chaque KPI contre ce qui existe dans PostHog.
- Correspond a un event actif → garder
- Ne correspond a rien → signaler, proposer de supprimer ou remplacer

**URL PostHog ou mot-cle direct** — lancer en parallele :
```
event-definitions-list(q: "<mot-cle>")
query-run(HogQL: voir query-patterns.md → "Decouvrir les URLs et tabs d'une feature")
```

**Contexte insuffisant apres lecture** → AskUserQuestion avant de continuer.

---

## Phase 2 — Interviewer via AskUserQuestion (OBLIGATOIRE)

Options ancrees sur ce qui existe reellement. Periode par defaut : -30d.

AskUserQuestion — une seule question multi-select :
- "Quels elements veux-tu dans le dashboard ?"
- options : events reels, URLs reelles, tabs reels detectes

---

## Phase 3 — Queries

Lire `references/posthog-reference.md` et `references/query-patterns.md` avant de lancer quoi que ce soit.

**Strategie : maximiser l'information, minimiser les calls.**

Avec le contexte collecte en Phase 1-2, determiner les patterns avant de lancer :

- Events specifiques connus → lancer directement les queries ciblees en parallele
- Context flou → lancer d'abord une query de verification (HogQL sur 30j) pour confirmer ce qui existe, puis les queries finales en parallele

**Choisir le bon pattern selon le besoin :**

| Besoin | Pattern |
|--------|---------|
| Adoption / usage general | Trends `dau` ou `total` |
| Comparer V1 vs V2 | "Comparer deux versions par URL" |
| Etapes sequentielles | FunnelsQuery |
| Volume metier | HogQL direct |
| Taux de conversion simple | "Taux de conversion entre deux events" |
| Nouveaux utilisateurs | "First-time users" |
| Breakdown par segment | "Repartition par propriete" |

---

## Phase 4 — Generer le dashboard

Chart.js CDN → `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js`

Le format est libre — adapter la structure a ce qui raconte le mieux l'histoire des donnees.
Principe : KPI cards → graphique principal → charts secondaires. Donnees injectees statiquement.

**Dashboard PostHog natif (si explicitement demande)**
```
entity-search(entities: ["dashboard"], query: <sujet>)
→ dashboard-create + insight-create-from-query
→ lien : https://app.posthog.com/project/${config.POSTHOG_PROJECT_ID}/dashboard/[id]
```

---

## Gotchas

**`event-definitions-list` ne confirme pas que l'event a des donnees recentes.**
Toujours verifier avec la query de verification dans `query-patterns.md` avant de marquer actif.

**Exclure V2 quand on filtre V1 par URL.**
`icontains /planning` matche aussi `/planning-v2` — voir pattern "Comparer deux versions" dans `query-patterns.md`.

**`LIMIT 100` par defaut dans HogQL.**
Ajouter `LIMIT 1000` pour les dashboards ou longues periodes.

**Les tabs sont des query params, pas des paths.**
`/planning-v2?tab=in_mission` → filtrer avec `icontains ?tab=in_mission`.

**`BoldNumber` avec multi-series retourne une valeur par serie, pas un total.**
Utiliser une seule serie ou calculer avec `countIf` en HogQL.

**KPIs Notion pas forcement valides.**
Toujours challenger contre PostHog avant de visualiser.

**Contexte insuffisant = questions obligatoires.**
Ne jamais supposer ce qu'on veut visualiser. Poser la question plutot qu'inventer.

### Notion

**`old_str` dans `notion-update-page` doit etre une correspondance exacte.**
Re-fetcher la page juste avant tout `update_content`.

**Section KPI peut contenir un tableau Notion natif.**
Si echec, re-fetcher pour voir le format exact.

---

## Configuration

MCPs requis : PostHog (`event-definitions-list`, `query-run`)
MCPs optionnels : Notion (`notion-fetch`)