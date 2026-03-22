# Anthropic — Skill Authoring Best Practices

Source : documentation officielle Anthropic (skill authoring guide)

---

## Concision avant tout

La context window est partagée avec tout le reste. Ne mettre dans SKILL.md que ce que Claude ne sait pas déjà.

Questions à se poser pour chaque ligne :
- "Claude a-t-il vraiment besoin de cette explication ?"
- "Est-ce que ce paragraphe justifie son coût en tokens ?"

---

## Degré de liberté

Adapter la précision des instructions à la fragilité de la tâche.

| Cas | Approche |
|-----|----------|
| Plusieurs approches valides, contexte variable | Instructions en texte libre — laisser Claude décider |
| Pattern préféré, variation acceptable | Pseudocode ou template avec paramètres |
| Opération fragile, séquence critique | Instructions exactes, pas de variation autorisée |

---

## Description (frontmatter)

- Toujours en **3ème personne** — la description est injectée dans le system prompt
  - Bon : `"Produit un schéma de tracking pour une feature"`
  - Mauvais : `"Je génère un schéma"` / `"Vous pouvez utiliser ce skill pour..."`
- Inclure **quand l'utiliser**, pas seulement ce que ça fait
- Être spécifique — Claude choisit parmi potentiellement 100+ skills

---

## Structure progressive

SKILL.md = table des matières. Les fichiers `references/` sont chargés uniquement si nécessaire.

- SKILL.md < 500 lignes
- Tout ce qui dépasse 300 lignes → déplacer dans `references/`
- Référencer les fichiers directement depuis SKILL.md — **pas de références imbriquées** (A → B → C casse la lecture)
- Pour les fichiers de référence longs (> 100 lignes) : ajouter une table des matières en tête de fichier

---

## Templates de sortie

Fournir un template quand le format de sortie est important.

- Instructions strictes (`TOUJOURS utiliser cette structure`) → pour les outputs qui doivent être parsés ou réutilisés
- Instructions flexibles (`format suggéré, adapter selon le contexte`) → pour les outputs narratifs

---

## Exemples input/output

Quand la qualité du résultat dépend du style, fournir des paires exemple :

```
**Exemple 1 :**
Input : [contexte]
Output :
[résultat attendu]
```

Les exemples transmettent le style et le niveau de détail mieux que les descriptions.

---

## Terminologie

Choisir un terme et s'y tenir dans tout le skill. La cohérence aide Claude à suivre les instructions sans ambiguïté.

**Bon — cohérent :**
- Toujours "KPI", jamais "métrique" / "indicateur" / "mesure"
- Toujours "créer", jamais "générer" / "produire" / "rédiger"

**Mauvais — incohérent :**
- Mélanger "page Notion" / "document" / "fiche" pour désigner la même chose
- Alterner "utilisateur" et "user" dans le même fichier

### Naming des skills (convention Anthropic)

Privilégier la **forme gérondive** (verbe + -ant) pour le nom du skill — ça décrit l'activité clairement.

- Bon : `"Generating PRDs"`, `"Tracking KPIs"`, `"Routing bugs"`
- Acceptable : `"PRD Builder"`, `"KPI Generator"`
- À éviter : `"Helper"`, `"Tool"`, `"Utils"`, noms trop génériques
