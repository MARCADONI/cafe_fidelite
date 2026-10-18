# ADR-0003 — Rapports statistiques du café

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 3.2 — Les rapports du patron

## Contexte

La version 1 de Café Fidélité enregistre les achats dans le modèle `Achat`, avec un type de transaction et une date.

Cependant, aucune fonctionnalité ne permet actuellement au gérant de consulter les statistiques sur une période.

La version 2 doit produire quatre indicateurs :

- Nombre de cafés payants.
- Nombre de cafés gratuits donnés.
- Nombre de cafés consommés avec une carte prépayée.
- Nombre de cartes prépayées vendues.

Le système ne doit pas calculer de montants financiers.

Nous devons également définir le traitement des transactions annulées et des annulations effectuées après la période concernée.

## Décision

Nous allons produire des rapports dynamiques à partir de l'historique des transactions.

### 1. Période sélectionnée

Le gérant pourra choisir une date de début et une date de fin.

Les deux dates seront incluses dans la période.

Le système utilisera les dates des opérations dans le fuseau horaire configuré pour l'application.

### 2. Catégories de transactions

Les rapports distingueront :

- Les achats payants (`PAYANT`).
- Les cafés gratuits de fidélité (`GRATUIT_FIDELITE`).
- Les cafés consommés sur une carte prépayée (`PREPAYE`).
- Les émissions de cartes prépayées, considérées comme des ventes dans le système.

L'émission d'une carte correspond à une carte vendue, même si le paiement est traité à l'extérieur de l'application.

### 3. Transactions annulées

Une transaction annulée sera exclue des totaux nets.

Elle restera néanmoins conservée dans l'historique afin de permettre la traçabilité.

Une transaction ne pourra être déduite qu'une seule fois, puisque les annulations multiples seront interdites.

### 4. Annulations tardives

Si une transaction du 10 octobre est annulée le 18 octobre, le rapport du 10 octobre sera corrigé lors de sa prochaine consultation.

Le rapport reflétera donc les transactions actuellement valides pour la période demandée.

Nous privilégions cette approche parce que le patron souhaite obtenir des statistiques corrigées après les erreurs de saisie.

### 5. Conservation des statistiques après l'effacement d'un client

Les transactions nécessaires aux rapports seront conservées sans renseignements permettant d'identifier un client effacé.

Les statistiques ne dépendront pas de la présence de sa fiche personnelle.

### 6. Contrôle d'accès

Seuls les utilisateurs possédant le rôle de gérant pourront accéder aux rapports.

Un barista ne pourra pas consulter cette fonctionnalité, même en saisissant directement son adresse URL.

### 7. Implémentation prévue

Nous utiliserons les requêtes de l'ORM Django pour filtrer les transactions par date, type et statut d'annulation.

Les émissions de cartes seront comptabilisées à partir des enregistrements correspondants, enrichis des informations nécessaires pour distinguer les cartes valides des ventes annulées.

Les rapports seront calculés à la demande, sans stocker de statistiques agrégées supplémentaires dans la base de données.

## Options écartées

### 1. Inclure les transactions annulées dans les totaux

Cette approche représenterait toutes les opérations enregistrées initialement.

Nous l'écartons parce qu'elle conserverait dans les statistiques des erreurs pourtant corrigées.

### 2. Conserver les rapports historiques inchangés

Cette solution faciliterait la reproduction exacte d'un ancien rapport.

Cependant, une transaction annulée tardivement continuerait d'être comptabilisée dans le rapport de sa date d'origine.

Nous préférons des rapports nets corrigés.

### 3. Stocker les statistiques dans des compteurs supplémentaires

Cette approche pourrait améliorer les performances pour de très grands volumes.

Elle introduirait toutefois de nouveaux risques de désynchronisation lors des annulations.

Pour la taille prévue de notre application locale, les calculs à la demande sont suffisants.

## Conséquences

### Avantages

- Rapports cohérents avec les annulations.
- Aucune duplication des statistiques.
- Consultation possible sur différentes périodes.
- Conservation des statistiques après anonymisation des clients.
- Utilisation des outils ORM de Django.

### Inconvénients

- Les résultats d'une ancienne période peuvent changer après une annulation.
- Les requêtes peuvent devenir plus coûteuses si l'historique grandit considérablement.
- Les émissions de cartes prépayées de la version 1 doivent être prises en compte lors de la migration.
- Les données de démonstration doivent contenir plusieurs dates afin de tester les filtres.

## Vérification

Nous développerons des tests automatisés pour vérifier que :

1. Un achat payant est comptabilisé dans la bonne période.
2. Un café gratuit est comptabilisé séparément.
3. Un café prépayé est comptabilisé séparément.
4. Une carte émise est comptée parmi les cartes vendues.
5. Une transaction annulée est exclue des totaux nets.
6. Une annulation tardive corrige le rapport de la période d'origine.
7. Les dates de début et de fin sont incluses.
8. Un barista ne peut pas accéder aux rapports.
9. L'effacement d'un client ne modifie pas les statistiques.