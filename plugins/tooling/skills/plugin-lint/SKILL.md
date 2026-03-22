---
name: plugin-linter
description: Audite un plugin ou marketplace Claude Code. Triggers : "audite mon plugin", "vérifie mon plugin", "lint mon plugin", "check best practices".
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
argument-hint: "[chemin optionnel]"
---

Audite la structure du répertoire courant (ou `$ARGUMENTS` si fourni).

Références :
- Bonnes pratiques officielles Anthropic : [references/anthropic-skill-authoring.md](${CLAUDE_SKILL_DIR}/references/anthropic-skill-authoring.md)
- Bonnes pratiques projet : [references/anthropic-plugin-best-practices.md](${CLAUDE_SKILL_DIR}/references/anthropic-plugin-best-practices.md)
- Conventions : [references/conventions.md](${CLAUDE_SKILL_DIR}/references/conventions.md)

## Étape 1 — Détecter le contexte

- `marketplace.json` présent → auditer chaque plugin référencé dans `plugins[]`
- `plugin.json` présent → auditer ce plugin
- Ni l'un ni l'autre → chercher les sous-dossiers avec `.claude-plugin/`

## Étape 2 — Exécuter les checklists

Consulter `references/anthropic-plugin-best-practices.md` pour la checklist complète.
Consulter `references/conventions.md` pour les conventions pasa.

## Étape 3 — Produire le rapport

Dans cet ordre :

**🔴 Secrets exposés** — fichier + ligne + valeur masquée + correction. Confirmer explicitement si rien trouvé.

**🔴 Problèmes bloquants** — fichier + problème + correction.

**🟡 Améliorations suggérées** — fichier + correction recommandée.

**🔵 Opportunités structurelles** — patterns avancés applicables.

---

## Gotchas

<!-- A enrichir au fil des runs -->

---

Ne pas supposer — si un fichier est absent, le signaler. Pas de jugements stylistiques sur le contenu métier.