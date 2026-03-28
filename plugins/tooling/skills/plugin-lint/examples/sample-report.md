# Exemple de rapport plugin-lint

Plugin audité : `plugins/demo/.claude-plugin/` (plugin fictif à des fins de calibration)

---

## 🔴 Secrets exposés

Aucun secret trouvé. ✓

## 🔴 Problèmes bloquants

**`plugins/demo/skills/fetch-data/SKILL.md` — lien mort**
- Ligne 12 : `[references/api-guide.md](${CLAUDE_SKILL_DIR}/references/api-guide.md)`
- Le fichier `references/api-guide.md` n'existe pas dans le répertoire du skill.
- Correction : créer le fichier ou supprimer la référence.

## 🟡 Améliorations suggérées

**`plugins/demo/.claude-plugin/plugin.json` — version non bumpée**
- La version est `1.0.0` mais le skill `fetch-data/SKILL.md` a été modifié depuis le dernier tag.
- Correction : incrémenter en `1.1.0` (ajout de skill = MINOR).

## 🔵 Opportunités structurelles

**`plugins/demo/skills/fetch-data/SKILL.md` — candidat à `context: fork`**
- Le skill fetch + analyse + produit un output long sans fork déclaré.
- Appliquer `context: fork` + `agent: Explore` pour isoler l'exécution et éviter la saturation de contexte principal.

---

## Score de synthèse

```
1 bloquant / 1 suggestion / 1 opportunité
```

Décision recommandée : **⚠️ À corriger avant merge**

---

## Checklist de merge

```
- [❌] Version bumpée dans plugin.json
- [✅] Aucune valeur sensible (IDs, tokens, URLs internes)
- [✅] disable-model-invocation si le skill écrit quelque part  (N/A — read-only)
- [✅] Section ## Gotchas dans chaque SKILL.md
- [✅] ${CLAUDE_SKILL_DIR} pour tout chemin bundlé
- [✅] SKILL.md < 500 lignes  (47 lignes)
```
