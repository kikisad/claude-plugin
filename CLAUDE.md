# CLAUDE.md — claude-plugin

Marketplace interne : le registre est **`.claude-plugin/marketplace.json`** ; chaque plugin vit sous **`plugins/<nom>/`** avec **`plugins/<nom>/.claude-plugin/plugin.json`** (manifest + version). Les skills : **`plugins/<nom>/skills/<skill>/SKILL.md`** (+ `references/`, etc.).

## Règle obligatoire : bump de version

Toute modification d'un plugin (skill, agent, référence, manifest) doit s'accompagner d'un bump de version dans `plugins/<plugin>/.claude-plugin/plugin.json`.

Sans bump, les utilisateurs qui ont installé le plugin ne reçoivent aucune mise à jour.

Règle de bump :

- Correction, reformulation, contexte mineur → `PATCH`
- Nouveau skill / agent, changement de comportement → `MINOR`
- Refonte structurelle → `MAJOR`

## Doc utilisateur

Installation marketplace et détail des plugins : **`README.md`**.
