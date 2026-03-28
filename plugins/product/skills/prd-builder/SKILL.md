---
name: prd-builder
description: Transforme des inputs bruts en un PRD structure et cree la page Notion correspondante. Utiliser quand l'utilisateur mentionne "PRD", "spec", "feature a specifier", "brief produit", ou veut formaliser une idee en document structure.
compatibility: "Requires Notion MCP (notion-fetch, notion-search, notion-create-pages). Optional: PostHog MCP"
allowed-tools: Read
argument-hint: "[lien Notion ou brief]"
---


## Prerequisites

**MCPs requis :**
- Notion MCP connecté (`notion-fetch`, `notion-search`, `notion-create-pages`)
- PostHog MCP optionnel (`event-definitions-list`, `query-run`)

Si le MCP Notion est absent → arrêter et indiquer lequel configurer.

**Variables d'environnement :**
Uniquement si l'utilisateur demande à Claude de créer la page projet lui-même (pas de lien Notion fourni).

| Variable | Utilisation |
|---|---|
| `$NOTION_PROJECTS_DB_ID` | BDD Projets où créer la page |

Si vide → AskUserQuestion, puis écrire dans `.claude/settings.local.json` sous `env.NOTION_PROJECTS_DB_ID`.

---

## Étape 1 — Collecter les inputs

Demander à l'utilisateur de partager tout ce qu'il a :
- Documents (specs, briefs, études, notes de réunion)
- Liens (pages Notion existantes, tickets, articles)
- Données analytics (PostHog, Google Analytics)
- Verbatims ou retours utilisateurs
- Son intuition / hypothèse de départ

Si l'utilisateur n'a pas encore de données PostHog, proposer d'en récupérer via l'outil PostHog
en demandant sur quelle feature ou comportement il veut des données.

## Étape 2 — Clarifier le problème

Poser les questions suivantes une par une, en s'adaptant aux inputs déjà fournis.
Ne pas poser une question si la réponse est déjà claire dans les documents.

Questions à poser :
1. "Quel est le problème exact que tu essaies de résoudre ?"
2. "Qui est impacté par ce problème (type d'utilisateur, volume estimé) ?"
3. "Pourquoi est-ce important maintenant ?"
4. "As-tu une hypothèse de solution ?"
5. "Quelle est la valeur attendue — en termes business ou utilisateur ?"

Reformuler les réponses pour valider la compréhension avant d'aller à l'étape suivante.

## Étape 3 — Construire le PRD

Synthétiser tous les inputs et les réponses en une structure PRD claire.
Respecter exactement la structure définie dans `${CLAUDE_SKILL_DIR}/references/prd-structure.md`.

Rédiger chaque section de façon concise et factuelle.
Utiliser les données réelles (métriques, verbatims) pour étayer chaque section.
Si une section manque de données, le signaler explicitement plutôt que d'inventer.

## Étape 4 — Valider avec l'utilisateur

Présenter le PRD complet dans le chat.
Demander : "Est-ce que ça reflète bien ton idée ? Y a-t-il des ajustements ?"
Itérer jusqu'à validation.

## Étape 5 — Créer la page Notion

Une fois le PRD validé :
1. Chercher dans Notion si un projet similaire existe déjà (pour éviter les doublons)
2. Identifier la bonne base de données ou section Notion pour créer le projet
3. Créer la page Notion avec exactement la structure définie dans `${CLAUDE_SKILL_DIR}/references/prd-structure.md`
4. Confirmer à l'utilisateur avec le lien vers la page créée

## Gotchas

**`notion-search` retourne des résultats hors de la base cible.**
Toujours filtrer par `$NOTION_PROJECTS_DB_ID` lors de la vérification des doublons — ne pas se fier au titre seul.

**Créer avant de valider = doublon silencieux.**
Ne jamais appeler `notion-create-pages` avant que l'utilisateur ait confirmé le PRD à l'Étape 4.

**Les accents et caractères spéciaux dans les titres cassent `notion-search`.**
Tester avec une version simplifiée du titre si la recherche ne retourne rien d'évident.
