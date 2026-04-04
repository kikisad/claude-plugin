---
name: plugin-linter
description: Audite la structure et le contenu d'un plugin ou marketplace Claude Code. Utiliser quand l'utilisateur demande d'auditer, vérifier, linter un plugin ou checker les best practices.
allowed-tools: Read, Glob, Grep
argument-hint: "[chemin optionnel]"
---

Audite le répertoire courant (ou `$ARGUMENTS` si fourni).

---

## 1. Checks déterministes — ne pas refaire à la main

Tout ce qui est **automatisable** vit dans `${CLAUDE_SKILL_DIR}/scripts/plugin-lint-check.py` (chemin bundlé). La liste exacte des règles est dans le **docstring en tête de ce fichier** (source de vérité).

**À faire en premier** : à la racine du dépôt,

`python3 "${CLAUDE_SKILL_DIR}/scripts/plugin-lint-check.py"`

- Si **exit ≠ 0** : transmettre la sortie stderr à l’utilisateur ; **ne pas** rejouer les mêmes vérifs « à la main » avec Read/Grep.
- Si **exit 0** : passer à la section 2 (IA uniquement).

`PLUGIN_LINT_CHECK_SKIP_GIT=1` ignore la règle de bump sur le staging (tests / CI).

---

## 2. Ce que tu fais en IA (hors script)

Ne duplique pas les points déjà dans le docstring du script. Concentre-toi sur :

### Dépôt agnostique — secrets et liens (bloquant si violation)

Le marketplace doit rester **réutilisable par n’importe quelle équipe** : rien dans le contenu commité ne doit révéler un compte, un workspace ou une page interne.

- **Interdit dans SKILL.md, références, agents, exemples** : mots de passe ; clés ou tokens (PostHog, Notion, Slack, etc.) ; secrets en clair même « pour un test » ; IDs de projet / workspace / base de données internes.
- **Interdit** : **liens directs** vers des pages Notion, tableaux de bord privés, URLs d’outils internes (même « publics » dans ton org). Remplacer par des formulations génériques (« la base Notion configurée via le MCP », « le dashboard analytics du workspace ») ou par des **variables d’environnement** documentées dans `.claude/settings.local.json.example` sans valeurs.
- Si tu trouves un secret ou un lien interne → **🔴 bloquant** : fichier, extrait masqué, correction (retirer + pointer vers le pattern `settings.local.json` / doc dans `references/conventions.md`).

### Autres vérifications IA

- **Jugement** sur `disable-model-invocation`, `context: fork` / `agent:`, adéquation des `allowed-tools`.
- **Qualité** : `description` + triggers, clarté du contenu, MCP en **fully-qualified** (`ServerName:outil`), namespace `pasa:<plugin>:<skill>` si pertinent.
- **Règles de nom / schéma** que le script ne vérifie pas (ex. longueur ou mots réservés pour `name`, hors simple présence).
- **Liens ou références** non couverts par le script (chemins sans extension typique, documentation dans `references/` à propos de la conformité Anthropic).

Références pour l’audit manuel :

- [references/anthropic-skill-authoring.md](${CLAUDE_SKILL_DIR}/references/anthropic-skill-authoring.md)
- [references/anthropic-plugin-best-practices.md](${CLAUDE_SKILL_DIR}/references/anthropic-plugin-best-practices.md)
- [references/conventions.md](${CLAUDE_SKILL_DIR}/references/conventions.md)

---

## 3. Détecter le contexte

- `marketplace.json` présent → auditer chaque plugin listé dans `plugins[]`
- `plugin.json` seul → auditer ce plugin
- Sinon → repérer les répertoires qui contiennent un `.claude-plugin/` (ex. sous `plugins/*/`)

---

## 4. Rapport

Après résultat du script (section 1) et lecture ciblée (section 2), produire dans cet ordre :

**🔴 Secrets** — ou « rien détecté » explicitement.

**🔴 Bloquants** (IA) — hors liste du script.

**🟡 Suggestions**

**🔵 Opportunités** (patterns avancés).

**Synthèse** : `X bloquants / Y suggestions / Z opportunités` et décision `✅ Prêt à merger` / `⚠️ À corriger` / `🚫 Bloqué`.

---

## Gotchas

- **Doublon script / skill** : ne pas rechecker à la main ce qui est dans le docstring de `plugin-lint-check.py`.
- **Script vert mais PR douteuse** : le bump « obligatoire » ne s’applique qu’avec des fichiers stagés ; l’IA peut encore signaler oubli de bump si la politique d’équipe l’exige hors pre-commit.
- **Chemins hardcodés** `./references/...` : le script ne valide que les motifs `${CLAUDE_SKILL_DIR}/…` avec extension ; les autres restent à l’audit manuel.
- **Lien Notion / outil interne** dans le repo : même sans secret, c’est une fuite de contexte org — à traiter comme bloquant pour un marketplace public ou partagé.

---