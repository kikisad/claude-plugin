# Règles de wording asap.work — Référence complète

> Source : >[lien supprimé]

---

## Règles globales

### Voix & ton
- **Voix** : claire, directe, professionnelle, bienveillante
- **Personne** : tutoiement, voix active
- **Longueur** : une idée par phrase, aller à l'essentiel
- **Accessibilité** : expliquer au survol (tooltip) si besoin de traduction ou définition

### Casse, ponctuation, accents
- **Français** : accents partout, même en majuscules
- **Espaces insécables** avant `: ; ? !` (Option+Espace Mac / Ctrl+Maj+Espace Windows)
- **Capitalisation** : bas de casse (majuscule au 1er mot uniquement), noms propres avec majuscule
  - Exception : "uniquement", "obligatoirement" peuvent être en haut de casse à l'occasion
- **Ponctuation** : pas d'ellipses `…` sauf action en cours ; pas de `!`

### Constance terminologique
- Un concept = un mot unique dans tout le produit
- Interdire les synonymes en UI
- Maintenir un glossaire (voir section Glossaire)

### Inclusivité & clarté
- Formulations épicènes si pas au détriment de la concision (ex : "le talent" ou "le client", pas "l'entreprise cliente")
- Bannir les tournures passives et culpabilisantes
- Ne pas répéter quelque chose d'évident (ex : "123 talents en mission" pas "123 nombre de talents en mission")

---

## Structures par composant

### A. Boutons & CTA
- Règle : verbe d'action à l'infinitif, 1 à 3 mots, objectif clair
- Primaire = action principale ; Secondaire = alternative sûre ; Destructif = danger (couleur + libellé explicite)

✅ "Créer une société" / "Enregistrer" / "Envoyer la facture"
❌ "Soumission" (nom) / "OK" (ambigu) / "Valider" sans précision

**États :**
- En cours : "Enregistrement…" (avec spinner)
- Succès (toast) : "Société créée."
- Échec (toast) : "Échec de création. Réessayez."

### B. Titres, onglets, navigation
- Titres de page/sections : groupes nominaux ("Sociétés", "Paramètres du compte")
- Onglets : noms courts, pluriels si listent des éléments
- Breadcrumbs : singulier pour l'élément courant

✅ Page "Factures" / Détail "Facture #F-2025-041"
❌ "Créer une facture" comme titre de liste

### C. Champs & formulaires
- Libellé de champ : nom clair + aide minimale
- Placeholder = exemple, pas une instruction
  - ✅ Label "Raison sociale" — Placeholder "Ex. Dupont SAS"
  - ❌ Placeholder "Entrez la raison sociale ici…"
- Aides contextuelles : sous-label concis ou tooltip "i"
- Regroupement logique : sections (Identité, Adresse, Fiscalité…)
- Progression : "Étape 2/4 — Informations légales"

**Boutons de formulaire :**
- Principal : "Créer la société"
- Secondaire : "Enregistrer le brouillon"
- Lien discret : "Annuler"

### D. Messages d'erreur, d'aide, d'info, de succès
- Structure erreur : ce qui se passe + pourquoi (si utile) + quoi faire
- ✅ "Connexion impossible. Vérifiez vos identifiants ou réinitialisez votre mot de passe."
- ✅ "SIREN invalide. Entrez 9 chiffres."
- ❌ "Erreur 400" / "Mauvaise saisie."

**Empty state :** expliquer + proposer une action
- ✅ "Vous n'avez pas encore de factures. **Créez votre première facture** pour démarrer."

### E. Modales & confirmations
- Titre = verbe + objet ; CTA destructif explicite
- ✅ Titre "Supprimer la société" / Texte "Cette action est définitive. Les données associées seront perdues." / CTA rouge "Supprimer" / Secondaire "Annuler"
- ❌ Titre "Confirmation" / CTA "OK"

### F. Tables, filtres, recherches
- En-têtes : noms courts et métiers ("Statut", "Montant TTC")
- Actions en ligne : verbes ("Modifier", "Dupliquer", "Archiver")
- Recherche : "Rechercher une facture" (champ) ; "Filtrer" (bouton)
- Tris & filtres : indiquer l'état ("Tri : Date ↓", "Filtres (2)")

### G. États de chargement
- ✅ "Chargement des sociétés…"
- ✅ "Synchronisation avec la banque… (≈ quelques secondes)"

---

## Normes de données (i18n, légales, finance)

### Dates & heures (fr-FR)
- Format UI : "14 oct. 2025"
- Horaires : 24h "14:30", fuseau explicité si nécessaire
- Relatif OK au survol ("il y a 2 h" ↔ "14 oct. 2025, 12:31")

### Nombres, unités, devises
- Séparateur milliers : espace fine insécable (1 234) ; décimal : ","
- Devise : "1 234,56 €" (symbole après, espace insécable) ; codes ISO en colonnes si multi-devises
- TVA : préciser base ("Montant HT", "Montant TTC", "TVA (20 %)")

### Formats juridiques & confidentialité
- Termes conformes : SIREN, SIRET, TVA intracommunautaire
- Consentements en clair : "J'accepte les Conditions et la Politique de confidentialité"
- Permissions : décrire précisément la portée ("Accès en lecture aux factures")

---

## Patterns réutilisables

### Pattern "Créer"
- Page liste : "Factures" + bouton "Créer une facture"
- Formulaire : titre "Nouvelle facture", CTA "Créer la facture"
- Succès (toast) : "Facture créée."
- Redirection : vers le détail avec bandeau "Vous pouvez maintenant **envoyer la facture**."

### Pattern "Modifier"
- Titre : "Modifier la société"
- CTA : "Enregistrer"
- Succès : "Modifications enregistrées."

### Pattern "Inviter un utilisateur"
- Champ : "Adresse e-mail" (Ex. prénom.nom@exemple.com)
- CTA : "Envoyer l'invitation"
- Succès : "Invitation envoyée à prénom.nom@exemple.com."
- Échec : "Invitation impossible. Cette adresse possède déjà un compte."

### Pattern "Téléverser un document"
- Bouton : "Importer un document"
- Formats sous le champ : "PDF, PNG, JPG — 10 Mo max"
- États : "Téléversement…" / "Import réussi." / "Fichier trop volumineux (10 Mo max)."

### Pattern le / un
- Ajouter : le / les (ex. "Ajouter le consultant responsable")
- Sélectionner : un (ex. "Sélectionner un contact")

### Pattern "Créer vs Ajouter"
- Première étape du processus → Créer (ex. "Créer une société")
- Étape intermédiaire, fait partie de → Ajouter (ex. "Ajouter un contact administratif")
- Nouvel élément dans une liste → "Ajouter un nouveau…" (ex. "Ajouter de nouvelles conditions")

---

## Tournures à bannir

### Tournures passives → reformuler en actif

| ❌ Passif | ✅ Actif |
|---|---|
| "Une erreur a été détectée." | "Impossible d'enregistrer. Vérifiez les champs ci-dessous." |
| "Votre demande a été refusée." | "Nous ne pouvons pas accepter cette demande pour le moment." |
| "Le document a été téléchargé avec succès." | "Document téléchargé." ou "Téléversement terminé." |
| "Un e-mail de confirmation vous a été envoyé." | "Vous allez recevoir un e-mail de confirmation." |
| "L'accès est limité aux utilisateurs autorisés." | "Vous n'avez pas encore accès à cette section." |
| "Les champs obligatoires doivent être remplis." | "Complétez tous les champs obligatoires." |
| "La mission a été annulée." | "Cette mission est annulée." / "La mission n'a pas pu être validée." |

### Tournures culpabilisantes → reformuler en neutre

| ❌ Culpabilisant | ✅ Neutre & bienveillant |
|---|---|
| "Vous n'avez pas rempli tous les champs." | "Certains champs sont manquants." |
| "Vous avez saisi un IBAN invalide." | "IBAN invalide. Vérifiez le format (FR76…)." |
| "Vous avez oublié de valider le CRA." | "CRA non validé." / "Il reste un CRA à valider." |
| "Vous n'avez pas respecté le format du fichier." | "Format de fichier non reconnu." |
| "Vous devez remplir ce champ." | "Champ requis." |
| "Vous n'avez pas téléchargé de pièce jointe." | "Aucune pièce jointe détectée." / "Ajoutez un document pour continuer." |
| "Vous avez déjà un compte." | "Un compte existe déjà avec cet e-mail." |
| "Votre mot de passe est incorrect." | "Mot de passe invalide." / "Vérifiez votre mot de passe." |
| "Vous n'avez pas validé la mission dans les temps." | "Mission en attente de validation." |

---

## Glossaire asap.work

- **Société** : entité légale liée au compte. (Pas "Entreprise", "Organisation")
- **Client** : tiers facturé. (Pas "Prospect" sauf statut CRM)
- **Facture** : document commercial (montant TTC, date d'échéance, statut)
- **Avoir** : note de crédit associée à une facture
- **Mission** : engagement entre un talent et un client
- **Talent** : consultant / freelance côté asap

**Statuts figés :**
- Facture : Brouillon, Envoyée, Payée, En retard, Annulée
- Paiement : En attente, Réussi, Échoué
- Utilisateur : Actif, Invité, Suspendu

---

## Kit de micro-copies prêtes à l'emploi

**Toasts succès :** "Enregistré." / "Modifications enregistrées." / "Invitation envoyée." / "Paiement confirmé."

**Toasts échec :** "Action impossible. Réessayez." / "Connexion échouée. Vérifiez vos identifiants."

**Empty states :**
- "Aucune société. **Créer une société** pour commencer."
- "Aucun résultat. Ajustez vos **filtres** ou **termes de recherche**."

**Chargement :** "Chargement en cours…" / "Synchronisation…"

**Pagination :** "Affichage 1–25 sur 134"

**Confirmations :** "Voulez-vous vraiment supprimer **Facture #F-2025-041** ? Cette action est définitive."

---

## Checklist de validation (à utiliser pour auditer)

- [ ] CTA = verbe d'action clair ("Créer la société")
- [ ] Titres/onglets = noms cohérents avec le glossaire
- [ ] Placeholders = exemples ; labels explicites
- [ ] Erreurs = cause + solution ; pas de codes bruts
- [ ] Empty states = explication + action proposée
- [ ] Dates = "14 oct. 2025" ; Heures = 24h
- [ ] Nombres = espace milliers ; décimal "," ; devises "1 234,56 €"
- [ ] Statuts = liste fermée et cohérente
- [ ] Destructif = confirmation nominative de l'objet
- [ ] Termes = 100 % conformes au glossaire
