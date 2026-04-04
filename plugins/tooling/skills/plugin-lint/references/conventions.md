# Conventions marketplace

Décisions d'équipe sur quand et comment appliquer les patterns officiels.
Pour le détail technique de chaque pattern, voir best-practices.md.

---

## Structure du marketplace

Chaque plugin = un domaine fonctionnel, pas une persona utilisateur.
Plugins actuels : `data`, `product`, `operations`, `tooling`

## Naming

- Nom de plugin : un mot, orienté métier
- Nom de skill : kebab-case, sans préfixe de domaine
- Namespace : `pasa:<plugin>:<skill>`

## Quand utiliser `disable-model-invocation`

À éviter — empêche l'invocation normale du skill par le modèle, ce qui est souvent gênant en pratique. Réserver aux skills qui ont un risque d'exécution involontaire critique (ex : suppression de données, envoi d'emails en masse).

## Quand utiliser `context: fork`

Tout skill qui fetch + analyse + produit un output long. Toujours accompagné de `agent:`.

- `agent: Explore` si lecture seule
- `agent: general-purpose` si le skill écrit aussi

## `allowed-tools` — quand l'ajouter

Recommandé pour les skills en **lecture seule** (évite des modifications accidentelles) et les skills qui appellent des outils externes spécifiques (MCP, Bash restreint).

```yaml
allowed-tools: Read, Grep, Glob          # skill d'audit / exploration
allowed-tools: Bash(gh *), Read          # skill GitHub CLI
```

Ne pas l'ajouter si le skill peut légitimement avoir besoin de n'importe quel outil selon le contexte.

## Configuration sensible

Aucune valeur sensible dans le repo. Pattern officiel :

1. `**.claude/settings.local.json**` — non commité (gitignored), contient les vraies valeurs.
2. `**.claude/settings.local.json.example**` — commité, documente les clés attendues sans valeur :
  ```json
   {
     "env": {
       "NOTION_TOKEN": "",
       "POSTHOG_API_KEY": ""
     }
   }
  ```
3. **Au premier run** : si une variable d'env est vide, AskUserQuestion pour la valeur, puis Claude l'écrit dans `settings.local.json`. Runs suivants : lecture silencieuse via l'env.

Ne jamais utiliser `${CLAUDE_PLUGIN_DATA}/config.json` — préférer ce pattern natif Claude Code.

## Dépôt agnostique — pas de secrets ni de liens internes

Le repo (skills, références, exemples) doit rester **neutre** : installable par une autre équipe sans exposer ton workspace.

- **Jamais** de mots de passe, clés API, tokens (PostHog, Notion, Slack, GitHub PAT, etc.) ou IDs de workspace / projet en clair dans un fichier commité.
- **Jamais** de **liens directs** vers des pages Notion, bases internes, dashboards privés ou URLs « internes » à une org — même pour de la doc : décrire le flux (« ouvrir la page configurée dans Notion ») ou utiliser des variables d’env documentées dans `.claude/settings.local.json.example`, pas une URL `notion.so/...` pointant vers une ressource réelle.
- Objectif : le marketplace ne dépend d’aucun compte, d’aucune base, d’aucun lien figé ; tout passe par la config locale non versionnée ou les MCP.

## Agents

Un agent = raisonnement spécialisé réutilisable. Si la logique s'écrit en `if/then` → MCP call dans le skill.
Toujours dans `[plugin]/agents/`. Sous-dossiers seulement à partir de 5+ agents.

## Évaluations

Les évaluations de skills vivent dans `evals/<plugin>/<skill>/`, à la racine du repo — pas dans le dossier du skill.

- `evals/<plugin>/<skill>/rubric.md` — critères de scoring, **non commité** (`evals/` est dans `.gitignore`)
- `evals/<plugin>/<skill>/sample-input.md` — input réel fixe pour les runs comparatifs, **non commité**

Le dossier `evals/` est conçu pour être extrait en repo indépendant si besoin.

---

## Checklist avant de merger un skill

- **Version bumpée** dans `plugins/<plugin>/.claude-plugin/plugin.json` (sans bump = pas de mise à jour pour les utilisateurs)
- Aucune valeur sensible — IDs, tokens, clés (PostHog, Notion, etc.)
- Aucun lien direct vers pages Notion / outils internes — dépôt agnostique (voir section « Dépôt agnostique »)
- `disable-model-invocation: true` **uniquement** si le skill est à risque d'exécution involontaire critique (suppression, envoi en masse) — ne pas ajouter par défaut
- Section `## Gotchas` dans le SKILL.md
- `${CLAUDE_SKILL_DIR}` pour tout chemin vers un fichier bundlé
- SKILL.md < 500 lignes

