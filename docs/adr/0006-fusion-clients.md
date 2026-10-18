# ADR-0006 — Fusion de deux fiches clients

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 3.5 — Fusionner deux fiches

## Contexte

Dans la version 1 de Café Fidélité, chaque client possède une fiche identifiée par un numéro de téléphone unique.

Une même personne peut néanmoins avoir plusieurs fiches si elle utilise différents numéros de téléphone.

Les étampes, les récompenses, les cartes prépayées et les achats sont alors répartis entre plusieurs enregistrements.

La version 2 doit permettre de fusionner ces fiches sans perdre les avantages accumulés ni l'historique.

## Décision

Nous allons créer une opération de fusion permettant à un gérant de sélectionner deux clients et de choisir la fiche principale à conserver.

La fiche principale deviendra l'unique fiche active.

### 1. Identifiant conservé

Le gérant choisira explicitement le client principal.

Son identifiant technique sera conservé.

La fiche secondaire sera désactivée et ses renseignements personnels redondants seront supprimés.

Une trace de fusion sera conservée sans dupliquer inutilement les renseignements personnels.

### 2. Fusion des étampes

Les progressions de fidélité des deux fiches seront additionnées.

Si la somme atteint le seuil de fidélité applicable à la date de fusion, de nouvelles récompenses seront attribuées.

Exemple avec un seuil de 10 :

- Client A : 6 étampes.
- Client B : 7 étampes.
- Total : 13 étampes.
- Résultat : 1 récompense supplémentaire et 3 étampes restantes.

La fusion utilisera le seuil en vigueur au moment de l'opération, sans recalculer les récompenses historiques déjà attribuées.

### 3. Fusion des récompenses

Les récompenses disponibles des deux fiches seront additionnées.

Les récompenses supplémentaires obtenues grâce au cumul des étampes seront ajoutées au résultat.

Aucune récompense déjà acquise ne sera perdue.

Les éventuelles dettes d'étampes introduites par le mécanisme d'annulation seront également prises en compte avant de déterminer les nouvelles récompenses.

### 4. Conservation des cartes prépayées

Chaque carte prépayée sera transférée vers la fiche principale.

Les cartes conserveront leurs soldes, leur statut et leur historique.

Les soldes de deux cartes distinctes ne seront pas fusionnés en un seul compteur.

### 5. Conservation de l'historique

Les achats de la fiche secondaire seront associés à la fiche principale.

Les dates, les types de transactions et les informations d'annulation seront conservés.

La fusion ne devra pas modifier les statistiques historiques.

### 6. Prévention des erreurs

Avant de confirmer, le gérant verra un récapitulatif des deux fiches et du résultat attendu.

Il devra confirmer explicitement l'opération.

Une fiche anonymisée, déjà fusionnée ou inactive ne pourra pas être utilisée comme source d'une nouvelle fusion.

### 7. Annulation d'une fusion

Nous ne proposerons pas d'annulation automatique de fusion.

Après une fusion, certaines opérations peuvent avoir été effectuées sur la fiche principale, ce qui rendrait difficile la séparation exacte des avantages.

En cas d'erreur, une correction administrative contrôlée sera nécessaire.

### 8. Permissions

Seul un utilisateur possédant le rôle de gérant pourra fusionner des fiches.

Un barista ne pourra pas accéder à cette fonctionnalité, même directement par son URL.

### 9. Cohérence et atomicité

La fusion sera exécutée dans une transaction atomique Django.

Les fiches et les soldes concernés seront verrouillés lorsque le moteur de base de données le permet.

La logique devra également empêcher deux fusions concurrentes incompatibles, notamment dans l'environnement SQLite utilisé par le projet.

Si une étape échoue, aucune modification partielle ne sera conservée.

## Options écartées

### 1. Supprimer simplement la fiche secondaire

Cette solution entraînerait la perte des avantages et de l'historique associés à cette fiche.

### 2. Fusionner uniquement les coordonnées personnelles

Cette approche conserverait deux comptes de fidélité distincts et ne satisferait pas la demande.

### 3. Fusionner toutes les cartes en une seule

Cette solution simplifierait l'affichage, mais ferait perdre la distinction entre les cartes émises et compliquerait leur historique.

### 4. Permettre une annulation automatique de fusion

Cette fonctionnalité serait pratique, mais nécessiterait de reconstituer les soldes et de répartir les opérations réalisées après la fusion.

Nous privilégions une fusion confirmée et traçable.

## Conséquences

### Avantages

- Conservation des avantages des deux fiches.
- Conservation des cartes prépayées individuelles.
- Conservation de l'historique des transactions.
- Possibilité de corriger les doublons.
- Gestion centralisée du client après fusion.

### Inconvénients

- La logique métier devient plus complexe.
- Les dettes d'étampes doivent être prises en compte.
- La fusion doit éviter les modifications partielles.
- Une fusion incorrecte n'est pas automatiquement réversible.
- Les références aux anciennes fiches doivent être traitées soigneusement.

## Vérification

Nous développerons des tests automatisés pour vérifier que :

1. Un gérant peut fusionner deux clients.
2. Un barista ne peut pas effectuer la fusion.
3. Les étampes sont correctement additionnées.
4. Le dépassement du seuil crée les récompenses appropriées.
5. Les récompenses disponibles sont conservées.
6. Les dettes d'étampes sont prises en compte.
7. Toutes les cartes prépayées sont conservées.
8. L'historique des achats est préservé.
9. Les statistiques restent inchangées.
10. Une fiche fusionnée ne peut plus être utilisée.
11. Une fusion échouée ne laisse aucune modification partielle.
12. Un client ne peut pas être fusionné avec lui-même.