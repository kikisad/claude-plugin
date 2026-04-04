# Bonnes pratiques officielles — Claude Code Plugins

Source : [https://code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins), /skills, /plugin-marketplaces

---

## Patterns structurels avancés

### `$ARGUMENTS` et arguments positionnels

Les skills peuvent recevoir des arguments dynamiques via `$ARGUMENTS` (tous les arguments) ou `$0`, `$1`, `$2`... (par position).

**Opportunité :** si une skill demande toujours à l'utilisateur de saisir quelque chose de variable (un nom, un chemin, un ID), elle devrait utiliser `$ARGUMENTS` plutôt que de poser une question à chaque fois.

```yaml
---
name: ma-skill
argument-hint: "[nom-du-projet]"
---
Traiter le projet "$ARGUMENTS"...
```

---

### `argument-hint`

Champ frontmatter qui affiche un hint dans l'autocomplete quand l'utilisateur tape `/skill-name`.

**Opportunité :** toute skill qui accepte des arguments devrait avoir un `argument-hint` pour guider l'utilisateur.

```yaml
argument-hint: "[issue-number]"
```

---

### `context: fork` — exécution en sous-agent isolé

Permet de faire tourner une skill dans un contexte isolé, sans accès à l'historique de conversation. Idéal pour des tâches autonomes longues.

**Opportunité :** les skills de recherche, d'analyse ou de génération de fichiers volumineux bénéficient d'un `context: fork` pour ne pas polluer le contexte principal.

```yaml
context: fork
agent: Explore   # ou general-purpose, Plan
```

---

### Backtick `!` — injection de contexte dynamique

Permet d'exécuter une commande shell avant que la skill soit envoyée à Claude. Le résultat remplace le placeholder dans le prompt.

**Opportunité :** si une skill a besoin de contexte live (état git, contenu d'un fichier, sortie d'une API), utiliser `!` plutôt que de demander à Claude de le récupérer lui-même.

```yaml
---
name: pr-summary
allowed-tools: Bash(gh *)
---
Diff actuel : !`gh pr diff`
Résume ce PR en 3 points.
```

---

### `${CLAUDE_SKILL_DIR}` — chemins absolus vers les fichiers bundlés

Quand une skill référence des scripts ou fichiers dans son dossier, utiliser `${CLAUDE_SKILL_DIR}` pour que le chemin soit correct même après installation via marketplace (les plugins sont copiés dans un cache).

**Opportunité :** toute skill qui exécute un script local devrait utiliser `${CLAUDE_SKILL_DIR}/scripts/mon-script.sh` plutôt qu'un chemin relatif.

---

### Fichiers de support (`references/`, `examples/`, `scripts/`)

Les skills peuvent embarquer des fichiers additionnels dans leur dossier. Cela permet de garder `SKILL.md` sous 500 lignes en déportant la doc dense, les exemples ou les scripts.

**Opportunité :** si `SKILL.md` dépasse 300 lignes, identifier les sections qui sont de la documentation de référence (patterns, gotchas, exemples) et les déplacer dans `references/`.

Structure recommandée :

```
ma-skill/
├── SKILL.md                  ← orchestration + navigation
├── references/
│   └── patterns.md           ← patterns techniques détaillés
├── examples/
│   └── sample.md             ← exemples de sortie attendue
└── scripts/
    └── run.sh                ← scripts exécutables
```

---

### `disable-model-invocation` vs `user-invocable`

Deux flags distincts souvent confondus :


| Flag                             | Effet                                                                                                                                                           |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `disable-model-invocation: true` | Claude ne peut pas déclencher la skill automatiquement. L'utilisateur doit la lancer avec `/skill-name`. La description n'est **pas** chargée dans le contexte. |
| `user-invocable: false`          | L'utilisateur ne peut pas la lancer manuellement. Claude la charge automatiquement quand c'est pertinent. Utile pour du contexte de fond.                       |


**Opportunité :** vérifier que chaque skill utilise le bon flag selon son intention réelle.

---

### `allowed-tools` — restriction des outils

Permet de limiter les outils disponibles quand une skill est active, sans demander de permission à chaque fois.

**Opportunité :** les skills en lecture seule (exploration, audit) devraient restreindre à `Read, Grep, Glob` pour éviter des modifications accidentelles. Les skills qui appellent une API externe devraient lister explicitement les outils requis.

```yaml
allowed-tools: Read, Grep, Glob          # lecture seule
allowed-tools: Bash(gh *), Read          # GitHub CLI + lecture
```

---

### `settings.json` — activer un agent par défaut

Un plugin peut inclure un `settings.json` à sa racine pour activer un agent custom comme contexte principal quand le plugin est activé.

**Opportunité :** si un plugin a une identité forte (ex: "mode data analyst"), il peut avoir un agent dédié qui s'active automatiquement.

```json
{ "agent": "mon-agent-custom" }
```

---

### `version` dans `plugin.json` — convention de bump

Convention recommandée pour le semantic versioning dans ce contexte :


| Changement                                   | Bump                        |
| -------------------------------------------- | --------------------------- |
| Nouvelle skill ajoutée                       | `MINOR` (ex: 1.1.0 → 1.2.0) |
| Correction ou amélioration d'une SKILL.md    | `PATCH` (ex: 1.1.0 → 1.1.1) |
| Restructuration du plugin ou breaking change | `MAJOR` (ex: 1.x.x → 2.0.0) |


**Important :** si la version est définie à la fois dans `plugin.json` et dans `marketplace.json`, c'est `plugin.json` qui fait foi. Éviter de définir la version aux deux endroits.

---

### `README.md` — documentation utilisateur

La doc officielle recommande d'inclure un `README.md` avant de distribuer un plugin, avec : instructions d'installation, liste des skills disponibles, MCPs requis, et exemples d'utilisation.

**Opportunité :** tout plugin distribué via marketplace sans `README.md` est difficile à adopter pour un nouveau membre de l'équipe.

---

### Chemins interdits dans les plugins

Les plugins sont copiés dans un cache lors de l'installation. Les fichiers en dehors du répertoire plugin ne sont pas copiés.

**Règles à vérifier :**

- Pas de `../` dans les chemins référencés
- Pas de dépendances vers des fichiers partagés entre plugins via chemins relatifs
- Si du partage est nécessaire : utiliser des symlinks (suivis lors de la copie)

---

### MCP — noms fully-qualified

Quand un SKILL.md référence un outil MCP, toujours utiliser le format `ServerName:tool_name`.

Sans le préfixe, Claude peut échouer à localiser l'outil si plusieurs MCP servers sont actifs simultanément.

```markdown
# Mauvais
"Utilise l'outil bigquery_schema pour récupérer le schéma."

# Bon
"Utilise BigQuery:bigquery_schema pour récupérer le schéma."
"Utilise Slack:slack_send_message pour envoyer le message."
```

**Opportunité :** tout SKILL.md qui mentionne un outil MCP sans préfixe de server → corriger.

---

### `.mcp.json` — déclaration des MCPs requis

Un plugin peut inclure un `.mcp.json` à sa racine pour déclarer les MCP servers nécessaires. Cela permet à Claude Code de les activer automatiquement quand le plugin est chargé.

**Opportunité :** toute skill qui mentionne un MCP dans `compatibility` devrait avoir un `.mcp.json` correspondant pour automatiser la configuration.

```json
{
  "mcpServers": {
    "notion": { "command": "npx", "args": ["-y", "@anthropic-ai/mcp-server-notion"] }
  }
}
```

