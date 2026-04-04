# claude-plugin

Marketplace de plugins Claude Code pour l'équipe produit.

## Plugins


| Plugin       | Description                              |
| ------------ | ---------------------------------------- |
| `product`    | Aide à la rédaction des documents projet |
| `data`       | Analyse de données et métriques          |
| `operations` | Automatisation des process et workflows  |
| `tooling`    | Maintenance et bonnes pratiques          |


## Structure

```
plugins/
  <plugin>/
    .claude-plugin/
      plugin.json       # manifest + version
    skills/
      <skill>/
        SKILL.md
        references/     # fichiers de contexte chargés par le skill
    agents/
      <agent>/
        AGENT.md
.claude-plugin/
  marketplace.json      # registre de tous les plugins
```

## Ajouter ou modifier un plugin

1. Modifier les fichiers du plugin concerné sous `plugins/<plugin>/`
2. **Bumper la version** dans `plugins/<plugin>/.claude-plugin/plugin.json` — sans bump, les mises à jour ne sont pas détectées
3. Vérifier la checklist dans `plugins/tooling/skills/plugin-lint/references/conventions.md`
4. Commit + push sur `main`

## Versioning

Format `MAJOR.MINOR.PATCH` :

- `PATCH` — correction, reformulation, ajout de contexte mineur
- `MINOR` — nouveau skill ou agent, changement de comportement
- `MAJOR` — refonte structurelle du plugin

## Hooks Git (dépôt / contributeurs)

Le pre-commit lance le linter plugin (`plugin-lint-check.py`). Les scripts vivent dans **`githooks/`** (versionné).

**Une fois après chaque clone** (ou sur ce repo si ce n’est pas déjà fait) :

```bash
git config core.hooksPath githooks
```

Sans ça, Git n’exécute pas les hooks du dossier versionné. Alternative ponctuelle : `cp githooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit` (sans `core.hooksPath`).

> `core.hooksPath` est une config **locale** (`.git/config`), elle n’est pas poussée sur le remote : chaque clone doit exécuter la commande ci-dessus.

## Installation

### Claude Code (CLI)

**1. Ajouter le marketplace**

```bash
killian/claude-plugin
```

**2. Sélectionner les plugins voulus** depuis le marketplace via l'interface Claude Code.

**3. MCPs requis**

Si tu es déjà connecté à Claude, les tools MCP par défaut sont utilisés automatiquement.
Penser à ajouter les tools référencés dans les skills : PostHog / Notion / Slack

---

### Claude Desktop

Les plugins Claude Code ne sont pas supportés nativement dans Claude Desktop.
Les tools utilisés par les skills (PostHog, Notion, Slack) s'ajoutent via les **connecteurs natifs de Claude Desktop** (Personaliser → Connecteurs)