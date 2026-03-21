# Conventions pasa-marketplace

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

Tout skill qui écrit quelque part (Notion, Slack, PostHog). L'utilisateur décide quand ça s'exécute.

## Quand utiliser `context: fork`

Tout skill qui fetch + analyse + produit un output long. Toujours accompagné de `agent:`.
- `agent: Explore` si lecture seule
- `agent: general-purpose` si le skill écrit aussi

## Frontmatter : ce qu'on n'ajoute pas

Pas de `allowed-tools` ni autres primitives runtime — agnosticisme plateforme.

## Configuration sensible

Aucune valeur sensible dans le repo. Stockage dans `${CLAUDE_PLUGIN_DATA}/config.json`.

Au premier run : AskUserQuestion pour collecter tous les IDs en un seul appel, puis écriture du fichier. Runs suivants : lecture silencieuse.

## Agents

Un agent = raisonnement spécialisé réutilisable. Si la logique s'écrit en `if/then` → MCP call dans le skill.
Toujours dans `[plugin]/agents/`. Sous-dossiers seulement à partir de 5+ agents.

---

## Checklist avant de merger un skill

- [ ] Aucune valeur sensible — IDs, tokens, URLs internes
- [ ] `disable-model-invocation: true` si le skill écrit quelque part
- [ ] Section `## Gotchas` dans le SKILL.md
- [ ] `${CLAUDE_SKILL_DIR}` pour tout chemin vers un fichier bundlé
- [ ] SKILL.md < 500 lignes