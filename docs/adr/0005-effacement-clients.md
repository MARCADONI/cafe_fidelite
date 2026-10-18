# ADR-0005 — Effacement des renseignements personnels d'un client

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 3.4 — Effacer un client

## Contexte

Dans la version 1 de Café Fidélité, les achats sont associés aux clients par une relation `ForeignKey` utilisant `on_delete=models.CASCADE`.

La suppression physique d'un client entraînerait donc la suppression de ses achats, ce qui modifierait les statistiques historiques du café.

La version 2 doit permettre à un gérant de répondre à une demande d'effacement des renseignements personnels sans modifier le nombre de cafés comptabilisés dans les rapports.

Cette fonctionnalité s'inscrit dans l'esprit de la Loi 25 du Québec, sans prétendre assurer une conformité juridique complète.

## Décision

Nous allons mettre en place un mécanisme d'anonymisation irréversible des fiches clients.

### 1. Suppression des renseignements personnels

Lorsqu'un gérant confirme l'effacement, le système supprime ou remplace les renseignements personnels du client :

- Nom.
- Numéro de téléphone.
- Adresse courriel.
- Tout autre renseignement directement ou indirectement identifiant conservé par l'application.

La fiche sera marquée comme anonymisée et ne pourra plus être utilisée pour enregistrer de nouvelles opérations.

L'identifiant technique interne pourra être conservé uniquement s'il ne permet pas de réidentifier le client, directement ou par recoupement.

### 2. Conservation des transactions

Les achats historiques seront conservés afin de maintenir les statistiques.

Les transactions devront rester exploitables pour les rapports sans contenir de renseignements personnels permettant d'identifier l'ancien client.

Les relations entre les transactions et la fiche anonymisée pourront être conservées lorsque cela ne présente pas de risque de réidentification.

### 3. Cartes prépayées

Si le client possède une carte prépayée avec des cafés restants, le gérant devra confirmer que le solde a été traité à l'extérieur de l'application avant de procéder.

Cette opération ne constituera pas un remboursement informatique : le système ne gère aucun paiement.

Les cartes seront rendues inutilisables après l'effacement.

Leurs émissions et consommations historiques resteront comptabilisées dans les rapports.

### 4. Fidélité et récompenses

Les étampes et récompenses restantes ne pourront plus être utilisées après l'effacement.

La fiche anonymisée sera fermée aux nouvelles opérations.

Les achats et cafés gratuits déjà servis resteront dans l'historique statistique.

### 5. Journaux et historique des modifications

L'effacement devra également concerner les anciennes valeurs personnelles éventuellement conservées dans :

- Les journaux d'audit applicatifs.
- Les historiques de modification.
- Les champs descriptifs libres.
- Les autres enregistrements pouvant identifier le client.

Nous éviterons de conserver des copies du nom, du téléphone ou du courriel dans les événements métier.

Le journal de l'opération pourra conserver sa date, le gérant responsable et le type d'action, sans conserver les renseignements effacés.

### 6. Permissions

Seul un utilisateur possédant le rôle de gérant pourra effectuer l'effacement.

Une confirmation explicite sera obligatoire avant l'exécution.

### 7. Cohérence et atomicité

L'effacement des données applicatives sera réalisé dans une transaction atomique Django.

Si une étape échoue, les modifications de la base de données seront annulées afin d'éviter un effacement partiel.

Les sauvegardes et journaux externes feront l'objet d'une procédure distincte, documentée dans le projet, car une transaction Django ne peut pas effacer automatiquement leurs copies.

## Options écartées

### 1. Supprimer physiquement le client et tous ses achats

Cette approche éliminerait les renseignements personnels, mais modifierait les statistiques historiques.

Elle est incompatible avec les exigences du devoir.

### 2. Conserver le client et masquer uniquement son nom

Cette solution ne serait pas suffisante puisque son téléphone, son courriel ou d'autres données pourraient encore permettre de l'identifier.

### 3. Conserver les données personnelles dans un journal d'archive

Cette solution faciliterait la récupération d'une ancienne fiche, mais contredirait l'objectif d'effacement des renseignements identifiants.

### 4. Supprimer les cartes prépayées sans traitement du solde

Cette approche risquerait de faire disparaître des avantages déjà payés.

Nous préférons imposer une vérification préalable du solde restant.

## Conséquences

### Avantages

- Les statistiques historiques restent inchangées.
- Les renseignements personnels sont retirés de la base opérationnelle.
- Les achats restent disponibles pour les rapports.
- Les fiches anonymisées ne peuvent plus effectuer de nouvelles opérations.
- L'accès à l'effacement est limité aux gérants.

### Inconvénients

- L'effacement doit couvrir plusieurs modèles et journaux.
- Les cartes prépayées nécessitent une procédure de clôture.
- L'anonymisation doit éviter les possibilités de réidentification.
- Les sauvegardes et fichiers externes nécessitent une politique distincte.
- Une fiche anonymisée ne pourra pas être restaurée à partir de ses anciennes informations personnelles.

## Vérification

Nous développerons des tests automatisés pour vérifier que :

1. Un gérant peut anonymiser un client.
2. Un barista ne peut pas effectuer l'opération.
3. Le nom, le téléphone et le courriel sont effacés.
4. Le client anonymisé ne peut plus effectuer d'achats.
5. Les statistiques avant et après l'effacement sont identiques.
6. Les cartes prépayées deviennent inutilisables.
7. Une carte possédant un solde restant nécessite une confirmation de traitement.
8. Les journaux applicatifs ne conservent pas les anciennes données personnelles.
9. Une erreur pendant l'opération ne laisse pas de modifications partielles.