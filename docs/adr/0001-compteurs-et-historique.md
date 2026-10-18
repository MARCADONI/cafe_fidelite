# ADR-0001 — Conservation des compteurs et de l'historique

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 2 — Compteur ou historique

## Contexte

Dans la version 1 de Café Fidélité, les soldes sont conservés dans des compteurs : progression de fidélité, récompenses disponibles et cafés restants sur les cartes prépayées.

L'application enregistre également les achats dans un historique, mais celui-ci ne couvre pas toutes les opérations nécessaires à une traçabilité complète, notamment l'émission des cartes prépayées et les annulations.

Les nouvelles fonctionnalités de la version 2 exigent des annulations, des rapports historiques, des changements de règles de fidélité, l'effacement de renseignements personnels et la fusion de clients.

Nous devons également garantir la conservation des soldes existants lors de la migration de la version 1 vers la version 2.

## Décision

Nous conservons une architecture hybride reposant sur les compteurs et un historique enrichi des opérations.

Les compteurs continueront à représenter les soldes courants afin de permettre une consultation rapide.

L'historique conservera les événements nécessaires à la traçabilité, notamment les achats, les utilisations de récompenses, les émissions de cartes prépayées et les annulations.

Les soldes issus de la version 1 seront préservés lors de la migration. Ils constitueront l'état initial de référence pour la version 2.

À partir de cette migration, les opérations modifiant les soldes seront exécutées dans des transactions atomiques afin de maintenir la cohérence entre les compteurs et les enregistrements historiques.

Les transactions historiques serviront de référence pour les rapports et les audits. Les compteurs représenteront les soldes opérationnels, qui devront pouvoir être vérifiés à partir de l'état initial migré et des opérations ultérieures.

En cas de divergence, aucune correction automatique silencieuse ne sera effectuée. Une vérification devra identifier la cause avant de rétablir la cohérence.

## Options écartées

### 1. Utiliser uniquement les compteurs

Cette solution est simple et rapide pour consulter les soldes.

Cependant, elle ne permet pas de répondre correctement aux besoins de rapports historiques et de traçabilité des annulations.

### 2. Utiliser uniquement l'historique

Cette solution permettrait de calculer les soldes à partir des opérations.

Cependant, elle nécessiterait de reconstituer des informations qui ne sont pas nécessairement disponibles dans la version 1. Elle compliquerait également la migration et le calcul des soldes lorsque les règles de fidélité changent.

### 3. Conserver les deux sans mécanisme de cohérence

Cette approche correspond en partie à la version 1, mais elle présente un risque de divergence entre les compteurs et l'historique.

Nous la rejetons au profit d'une synchronisation explicite.

## Conséquences

### Avantages

- Conservation des soldes existants lors de la migration.
- Consultation rapide des récompenses et des cartes prépayées.
- Possibilité de produire des rapports historiques.
- Meilleure traçabilité des opérations et des annulations.
- Architecture compatible avec les nouvelles fonctionnalités.

### Inconvénients

- Complexité supplémentaire pour synchroniser les compteurs et l'historique.
- Nécessité de développer des tests de cohérence.
- Obligation de gérer explicitement les cas d'annulation complexes.
- Conservation d'un état initial pour permettre la vérification des soldes migrés.

## Vérification

Des tests automatisés vérifieront que :

1. Une opération modifie correctement le solde et son historique.
2. Une opération échouée ne modifie ni le solde ni l'historique.
3. Les soldes existants restent identiques après la migration.
4. Les annulations et les rapports tiennent compte des opérations historiques selon les règles définies dans leurs ADR respectifs.