---
name: plugin-linter
description: >
  Audite un plugin ou marketplace Claude Code et détecte les écarts par rapport aux bonnes pratiques officielles.
  Utiliser après chaque refactoring de plugin pour vérifier la conformité.
  Triggers : "audite mon plugin", "vérifie mon plugin", "lint mon plugin", "check best practices".
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
argument-hint: "[chemin optionnel]"
---

# Plugin Linter

Audite la structure d'un plugin ou d'un marketplace Claude Code et produit un rapport de conformité.

> Référence complète des bonnes pratiques : voir [references/best-practices.md](${CLAUDE_SKILL_DIR}/references/best-practices.md)

---

## Détection automatique du contexte

Avant toute chose, lister le répertoire courant (ou le chemin fourni via `$ARGUMENTS`) et détecter le type :

- `.claude-plugin/marketplace.json` présent → **marketplace** → auditer le marketplace + chaque plugin référencé dans `plugins[]`
- `.claude-plugin/plugin.json` présent (sans `marketplace.json`) → **plugin standalone** → auditer ce plugin uniquement
- Ni l'un ni l'autre → chercher les sous-dossiers contenant `.claude-plugin/` et les auditer un par un

Dans le cas d'un marketplace : extraire tous les `source`, résoudre les chemins relatifs depuis la racine, et auditer chaque plugin individuellement.

```
/plugin-linter [chemin optionnel]
```

---

## Checklist de vérification

### 1. Manifest `plugin.json`

- [ ] Présent dans `.claude-plugin/plugin.json` uniquement — pas ailleurs
- [ ] Champs obligatoires : `name`, `description`, `version`
- [ ] `name` en kebab-case (minuscules, chiffres, tirets)
- [ ] `version` en semantic versioning `MAJOR.MINOR.PATCH`
- [ ] `description` orientée usage, pas technique
- [ ] Aucun composant (`skills/`, `agents/`, `hooks/`) déclaré dans `.claude-plugin/`

### 2. Structure des dossiers

- [ ] `skills/`, `agents/`, `hooks/`, `.mcp.json` à la **racine du plugin**
- [ ] Chaque skill dans `skills/<skill-name>/SKILL.md`
- [ ] Aucun fichier référencé en dehors du répertoire plugin (pas de `../`)

### 3. SKILL.md — frontmatter

- [ ] Frontmatter entre `---`
- [ ] `description` : 1 phrase avec des triggers en langage naturel
- [ ] `disable-model-invocation: true` si la skill a des effets de bord (create, send, deploy...)
- [ ] `user-invocable: false` si c'est du contexte de fond non-actionnable
- [ ] `allowed-tools` défini si la skill nécessite des outils spécifiques
- [ ] MCPs requis mentionnés (dans `compatibility` ou une section `## Configuration`)
- [ ] `argument-hint` présent si la skill accepte des arguments
- [ ] `${CLAUDE_SKILL_DIR}` utilisé pour les chemins vers les fichiers bundlés

### 4. SKILL.md — contenu

- [ ] Moins de 500 lignes — sinon déplacer dans `references/`
- [ ] Fichiers de support (`references/`, `examples/`, `scripts/`) référencés explicitement
- [ ] Valeurs hardcodées (IDs, URLs internes) isolées dans `references/` ou une section `## Configuration`
- [ ] Contenu concis, sans prose inutile

### 5. Marketplace `marketplace.json`

- [ ] Présent dans `.claude-plugin/marketplace.json`
- [ ] Champs obligatoires : `name`, `owner.name`, `plugins`
- [ ] Chaque entrée plugin a `name` et `source`
- [ ] Chemins relatifs commencent par `./`
- [ ] `metadata.description` recommandé

### 6. Exposition publique — secrets et données sensibles

Le repo étant public, scanner **tous** les fichiers du plugin (SKILL.md, references/, examples/, plugin.json, .mcp.json, settings.json) à la recherche de :

- [ ] Aucune clé API, token, secret ou mot de passe en clair
  - Patterns à détecter : `sk-`, `Bearer `, `token:`, `api_key`, `apiKey`, `secret`, `password`, `Authorization`
- [ ] Aucun ID interne d'outil tiers exposé directement
  - IDs Notion (base de données, pages) — format UUID ou `collection://`
  - IDs PostHog project — format numérique dans une URL ou champ dédié
  - IDs Slack (workspace, channel) — format `T`, `C`, `U` + chaîne alphanumérique
- [ ] Aucune URL interne ou privée (intranet, staging, apps internes non publiques)
- [ ] Aucun nom d'utilisateur, email ou information personnelle identifiable
- [ ] Les valeurs dans `## Configuration` sont des **placeholders** (`<your-api-key>`, `<notion-db-id>`) et non des vraies valeurs

**Règle :** une valeur dans `## Configuration` est acceptable uniquement si c'est un placeholder explicite. Toute vraie valeur est un 🔴 problème bloquant.

---

## Opportunités d'amélioration structurelle

Après la checklist, identifier les opportunités d'amélioration issues des patterns avancés de la doc officielle. Consulter [references/best-practices.md](${CLAUDE_SKILL_DIR}/references/best-practices.md) pour les détails de chaque pattern.

Pour chaque opportunité applicable, indiquer : le fichier concerné, ce qui manque, et le bénéfice concret.

---

## Format du rapport

### Conforme
Points qui respectent les bonnes pratiques.

### Améliorations suggérées
Points non-bloquants. Pour chaque point : fichier + correction recommandée.

### Problèmes bloquants
Points qui empêchent le bon fonctionnement. Pour chaque point : fichier + problème exact + correction.

### Secrets et données sensibles exposées
**Section prioritaire** — tout ce qui ne devrait pas être dans un repo public.
Pour chaque occurrence : fichier + ligne + valeur masquée (ne pas répéter la valeur en clair) + correction.
Si rien de sensible détecté : le confirmer explicitement.

### Opportunités structurelles
Patterns avancés applicables au plugin qui amélioreraient la qualité ou l'expérience utilisateur.

---

## Règles de comportement

- Toujours lister le répertoire en premier pour détecter le contexte
- Ne pas supposer — si un fichier est absent, le signaler sans inventer son contenu
- Pas de jugements stylistiques sur le contenu métier
- Dans un marketplace multi-plugins : un sous-rapport par plugin + récap final priorisé
- **La section "Secrets et données sensibles" passe toujours en premier dans le récap final**, avant les problèmes structurels
- Ne jamais répéter une valeur sensible en clair dans le rapport — la masquer partiellement (ex: `sk-ant-...****`)
