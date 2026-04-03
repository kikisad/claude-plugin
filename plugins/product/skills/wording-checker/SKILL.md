---
name: wording-checker
description: Applique les règles de wording asap.work pour rédiger ou corriger de la microcopy UI (labels, boutons, erreurs, toasts, empty states, confirmations). Utiliser quand l'utilisateur mentionne du wording, un libellé, un CTA, un texte d'interface, ou veut auditer une PR ou une maquette.
allowed-tools: Read
---

## Contexte

asap.work a des règles de wording précises pour garantir une voix cohérente, claire et bienveillante dans tous ses produits. Ce skill t'aide à les appliquer, que tu rédiges from scratch ou que tu corriges du texte existant.

Les règles complètes sont dans `${CLAUDE_SKILL_DIR}/references/wording-rules.md`. Consulte-le si tu as besoin d'un détail précis sur un composant ou un pattern.

---

## Règles fondamentales (mémorise-les)

**Voix & ton**
- Tutoiement, voix active, phrases courtes (une idée par phrase)
- Clair, direct, professionnel, bienveillant — jamais culpabilisant

**Casse**
- Bas de casse partout (majuscule au 1er mot uniquement)
- Accents sur les majuscules aussi ("État", "Événement")
- Espaces insécables avant `: ; ? !` en français

**Ponctuation**
- Pas d'ellipses `…` sauf action en cours ("Chargement…")
- Pas de `!`

**Terminologie**
- Un concept = un mot. Ne pas mélanger synonymes dans l'UI.
- Respecter le glossaire asap : "Société", "Client", "Facture", "Mission", "Avoir"

---

## Logique par composant

### Boutons & CTA
Verbe à l'infinitif, 1 à 3 mots, action claire.

| Type | Règle | Exemple |
|---|---|---|
| Primaire | Action principale | "Créer une société" |
| Secondaire | Alternative sûre | "Enregistrer le brouillon" |
| Destructif | Nommer l'objet explicitement | "Supprimer la facture #F-2025-041" |
| Lien discret | Annulation | "Annuler" |

❌ "OK", "Valider", "Soumission", "Suivant" (sauf étapes numérotées)

**États du bouton :**
- En cours : verbe + "…" + spinner → "Enregistrement…"
- Succès (toast) : nom + participe → "Société créée."
- Échec (toast) : "Échec de [action]. Réessayez."

### Titres & navigation
- Titre de page / section : groupe nominal ("Factures", "Paramètres du compte")
- Onglets : noms courts, pluriels si liste d'éléments
- Breadcrumb : singulier pour l'élément courant

❌ Verbe dans un titre de liste ("Créer une facture" comme titre de page)

### Champs & formulaires
- Label : nom clair et explicite
- Placeholder : **exemple**, jamais une instruction
  - ✅ "Ex. Dupont SAS" ❌ "Entrez la raison sociale"
- Progression multi-étapes : "Étape 2/4 — Informations légales"

### Erreurs
Structure : **ce qui se passe** + pourquoi (si utile) + quoi faire.

✅ "Connexion impossible. Vérifiez vos identifiants ou réinitialisez votre mot de passe."
✅ "SIREN invalide. Entrez 9 chiffres."
❌ "Erreur 400" ❌ "Mauvaise saisie."

Pas de tournure culpabilisante :
- ❌ "Vous avez saisi un IBAN invalide." → ✅ "IBAN invalide. Vérifiez le format (FR76…)."
- ❌ "Vous n'avez pas rempli tous les champs." → ✅ "Certains champs sont manquants."

### Empty states
Expliquer + proposer une action.
✅ "Aucune facture. **Créer une facture** pour démarrer."
❌ "Vide." ❌ "Aucun résultat."

### Modales & confirmations destructives
- Titre : verbe + objet ("Supprimer la société")
- Corps : conséquence claire ("Cette action est définitive. Les données associées seront perdues.")
- CTA rouge : nommer l'objet ("Supprimer") — Secondaire : "Annuler"

❌ Titre "Confirmation" + CTA "OK"

### Toasts / notifications
- Succès : phrase courte, point final → "Facture envoyée."
- Info : action possible → "Nouveau format disponible. **Mettre à jour**."
- Alerte : état + solution → "Échéance dépassée. **Relancer le client**."

### Chargement
Microcopy courte, utile.
✅ "Chargement des sociétés…" ✅ "Synchronisation avec la banque… (≈ quelques secondes)"

---

## Patterns récurrents

**Créer vs Ajouter**
- Première étape d'un processus → "Créer" (ex. "Créer une société")
- Élément qui s'intègre à quelque chose d'existant → "Ajouter" (ex. "Ajouter un contact")
- Nouvelle entrée dans une liste → "Ajouter un nouveau…"

**Le / un**
- "Ajouter" → **le/les** ("Ajouter le consultant responsable")
- "Sélectionner" → **un** ("Sélectionner un contact")

**Formats de données**
- Dates : "14 oct. 2025" (pas 14/10/2025, pas "14 octobre 2025" sauf espace)
- Heures : 24h → "14:30"
- Nombres : espace fine milliers, virgule décimale → "1 234,56 €"
- Devise : symbole après le montant + espace insécable → "1 234,56 €"
- TVA : toujours préciser la base ("Montant HT", "Montant TTC", "TVA (20 %)")

---

## Comment l'utiliser

**Cas 1 — Rédiger from scratch**
L'utilisateur décrit un composant ou un contexte. Tu proposes le wording final en appliquant les règles. Justifie brièvement tes choix si ce n'est pas évident.

**Cas 2 — Corriger du texte existant**
L'utilisateur colle un texte. Tu identifies les problèmes (tournure passive, culpabilisante, casse incorrecte, CTA ambigu…) et tu proposes une version corrigée avec explication.

**Cas 3 — Audit d'une PR ou d'une maquette**
L'utilisateur partage plusieurs éléments d'interface. Tu passes en revue composant par composant et tu produis un rapport structuré : ✅ conforme / ❌ à corriger + proposition.

Dans tous les cas : sois direct, montre la version finale en premier, explique ensuite si nécessaire. Pas de longues introductions.

---

Pour les détails complets sur un composant ou un pattern non couvert ici, consulte `${CLAUDE_SKILL_DIR}/references/wording-rules.md`.
