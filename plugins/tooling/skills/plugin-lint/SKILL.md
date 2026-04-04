---
name: plugin-linter
description: Audite la structure et le contenu d'un plugin ou marketplace Claude Code. Utiliser quand l'utilisateur demande d'auditer, vérifier, linter un plugin ou checker les best practices.
allowed-tools: Read, Glob, Grep
argument-hint: "[chemin optionnel]"
---

Audite la structure du répertoire courant (ou `$ARGUMENTS` si fourni).

Les contrôles **déterministes** (JSON, chemins bundlés, Gotchas, règle de bump) sont dans ce skill : `${CLAUDE_SKILL_DIR}/scripts/plugin-lint-check.py` ([fichiers de support](https://code.claude.com/docs/fr/skills#ajouter-des-fichiers-de-support)). Copie versionnée : `githooks/pre-commit` — activer avec `git config core.hooksPath githooks` à la racine du clone (ou copier ce fichier vers `.git/hooks/pre-commit` et `chmod +x`). Ce script ne couvre pas les secrets ni le jugement sémantique — l’audit ci-dessous reste nécessaire.

Références :

- Bonnes pratiques officielles Anthropic : [references/anthropic-skill-authoring.md](${CLAUDE_SKILL_DIR}/references/anthropic-skill-authoring.md)
- Bonnes pratiques projet : [references/anthropic-plugin-best-practices.md](${CLAUDE_SKILL_DIR}/references/anthropic-plugin-best-practices.md)
- Conventions : [references/conventions.md](${CLAUDE_SKILL_DIR}/references/conventions.md)

## Étape 1 — Détecter le contexte

- `marketplace.json` présent → auditer chaque plugin référencé dans `plugins[]`
- `plugin.json` présent → auditer ce plugin
- Ni l'un ni l'autre → chercher les sous-dossiers avec `.claude-plugin/`

## Étape 2 — Exécuter les checklists

**Option — checks automatiques** : à la racine du dépôt, `python3 "${CLAUDE_SKILL_DIR}/scripts/plugin-lint-check.py"` (mêmes règles que `.git/hooks/pre-commit`). Corriger jusqu’à exit 0, puis continuer l’audit ci-dessous.

Consulter `references/anthropic-plugin-best-practices.md` pour la checklist complète.
Consulter `references/conventions.md` pour les conventions pasa.

**Vérification des fichiers référencés** : pour chaque chemin `${CLAUDE_SKILL_DIR}/references/...` ou `${CLAUDE_SKILL_DIR}/examples/...` présent dans les SKILL.md audités, vérifier que le fichier existe réellement. Tout lien mort → 🔴 bloquant.

## Étape 3 — Produire le rapport

Dans cet ordre :

**🔴 Secrets exposés** — fichier + ligne + valeur masquée + correction. Confirmer explicitement si rien trouvé.

**🔴 Problèmes bloquants** — fichier + problème + correction.

**🟡 Améliorations suggérées** — fichier + correction recommandée.

**🔵 Opportunités structurelles** — patterns avancés applicables.

**Score de synthèse** :

```
X bloquants / Y suggestions / Z opportunités
```

Décision recommandée :

- 0 bloquant → `✅ Prêt à merger`
- ≥1 bloquant, corrigeable → `⚠️ À corriger avant merge`
- Secret exposé ou structure cassée → `🚫 Bloqué`

**Checklist de merge** (basée sur `references/conventions.md`) :

```
- [✅/❌] Version bumpée dans plugin.json
- [✅/❌] Aucune valeur sensible (IDs, tokens, URLs internes) — `.claude/settings.local.json.example` présent si le skill lit des env vars
- [✅/❌] disable-model-invocation absent sauf cas critique (suppression, envoi en masse)
- [✅/❌] Section ## Gotchas dans chaque SKILL.md
- [✅/❌] ${CLAUDE_SKILL_DIR} pour tout chemin bundlé
- [✅/❌] SKILL.md < 500 lignes
- [✅/❌] `name` valide : max 64 chars, minuscules/chiffres/tirets, pas de `anthropic` ni `claude`
- [✅/❌] Description contient ce que ça fait + triggers ("Utiliser quand...")
- [✅/❌] Outils MCP en fully-qualified (`ServerName:tool_name`)
```

Remplir chaque case avec ✅ ou ❌ selon ce qui a été observé dans l'audit.

---

## Gotchas

- **Chemins hardcodés** : utiliser `./references/foo.md` au lieu de `${CLAUDE_SKILL_DIR}/references/foo.md` — le fichier est introuvable hors du répertoire d'installation.
- **Version non bumpée** : modifier un skill sans incrémenter `plugin.json` → les utilisateurs installés ne reçoivent aucune mise à jour.
- **Secret dans le repo** : coller un token ou une URL interne directement dans SKILL.md ou une référence — stocker dans `.claude/settings.local.json` (non commité) et documenter les clés dans `.claude/settings.local.json.example` (commité, valeurs vides).
- **Ancien pattern `CLAUDE_PLUGIN_DATA`** : skill qui écrit dans `${CLAUDE_PLUGIN_DATA}/config.json` au lieu d'utiliser `settings.local.json` — migrer vers le pattern natif.
- `**disable-model-invocation` abusif** : poser ce flag sur un skill d'écriture standard (Notion, Slack…) empêche l'invocation normale — réserver aux actions vraiment critiques (suppression, envoi en masse).
- **SKILL.md trop long** : dépasser 500 lignes — déplacer le contenu détaillé dans `references/` et charger à la demande.
- **Section Gotchas absente** : SKILL.md sans `## Gotchas` → impossible pour l'équipe de capitaliser sur les erreurs connues.
- **Traversée de chemin** : utiliser `../` dans un chemin référencé — interdit, risque de sortir du sandbox plugin.
- **Namespace incorrect** : namespace du skill ne respectant pas le format `pasa:<plugin>:<skill>`.
- **Lien mort** : référence vers `${CLAUDE_SKILL_DIR}/references/foo.md` ou `examples/bar.md` dont le fichier n'existe pas dans le repo.
- `**context: fork` sans `agent:`** : le fork n'a pas de type d'agent défini → comportement indéterminé.
- `**name` invalide** : contient des majuscules, espaces, les mots réservés `anthropic` ou `claude`, ou dépasse 64 caractères — la validation échoue silencieusement.
- **MCP sans préfixe server** : référencer `send_message` au lieu de `Slack:slack_send_message` — Claude échoue à localiser l'outil si plusieurs MCP servers sont actifs.

---

