# ADR-0009 — Programme de fidélité partagé entre les succursales

## Statut

Accepté

## Contexte

Dans la version 2 de Café Fidélité, chaque client possède un compte de fidélité unique contenant ses étampes, ses récompenses et ses éventuelles dettes d'étampes. Les cartes prépayées sont également associées directement au client.

La version 3 introduit plusieurs succursales. Les clients doivent pouvoir accumuler et utiliser leurs avantages dans l'ensemble du réseau, indépendamment de la succursale dans laquelle ils ont été obtenus.

Il est nécessaire de déterminer si les règles de fidélité doivent être communes à toutes les succursales et comment traiter les éventuelles promotions locales.

## Options envisagées

### Option 1 — Un programme de fidélité par succursale

Chaque succursale possède ses propres compteurs, récompenses et règles de fidélité.

Cette solution offre une autonomie importante aux succursales, mais elle complexifie le partage des avantages et ne répond pas directement à l'exigence d'une fidélité commune.

### Option 2 — Un compte global avec des règles propres à chaque succursale

Les clients possèdent un compte de fidélité unique, mais chaque succursale peut définir son propre seuil de récompense.

Cette solution offre davantage de flexibilité commerciale, mais elle complique la conversion des étampes, la compréhension des soldes et la gestion des annulations.

### Option 3 — Un programme global avec une règle commune

Les clients possèdent un compte de fidélité unique et toutes les succursales appliquent la même règle de fidélité.

Cette solution simplifie le partage des avantages et garantit une expérience cohérente dans l'ensemble du réseau.

## Décision

Nous retenons l'option 3.

Les modèles `Client`, `Fidelite` et `CartePrepayee` restent indépendants des succursales.

Les étampes, les récompenses, les dettes d'étampes et les crédits prépayés sont partagés dans l'ensemble du réseau.

Un client peut notamment :

- Accumuler des étampes dans plusieurs succursales.
- Utiliser une récompense dans une succursale différente de celle où elle a été obtenue.
- Acheter une carte prépayée dans une succursale et l'utiliser dans une autre.

Le modèle `RegleFidelite` conserve une portée globale. Le seuil applicable est déterminé selon la date de la transaction, conformément au fonctionnement de la version 2.

La modification de la règle globale est réservée au propriétaire du réseau.

Les transactions continuent de conserver les informations nécessaires à leur annulation, notamment le seuil appliqué et les effets produits sur les compteurs.

Les opérations modifiant les soldes doivent être atomiques. Les services métier devront également gérer les accès concurrents afin d'éviter qu'une récompense ou un crédit prépayé soit consommé simultanément dans deux succursales.

## Gestion des promotions locales

Les promotions propres à une succursale, telles que l'attribution de deux étampes pour un achat lors d'une journée d'ouverture, ne seront pas implémentées dans la version 3.

Ce choix limite la complexité du système et permet de respecter les exigences actuelles sans introduire prématurément un mécanisme de promotions.

Une évolution future pourrait introduire un modèle de promotion associé à une succursale et à une période de validité.

Les effets réels de chaque promotion devraient alors être enregistrés dans les transactions afin de permettre leur annulation correcte.

## Conséquences positives

- Les clients bénéficient d'un programme de fidélité uniforme.
- Les soldes sont partagés entre toutes les succursales.
- Les modèles existants de fidélité et de cartes prépayées peuvent être conservés.
- Les données historiques de la version 2 restent compatibles.
- Les règles de conversion et d'annulation restent cohérentes.
- L'ajout d'une succursale ne nécessite pas la création d'un nouveau programme de fidélité.

## Conséquences négatives

- Les gérants ne peuvent pas définir indépendamment leur propre seuil de fidélité.
- Les promotions locales ne sont pas disponibles dans cette version.
- Les opérations simultanées provenant de plusieurs succursales nécessitent une gestion rigoureuse de la concurrence.

## Tests prévus

- Accumulation d'étampes dans deux succursales.
- Utilisation d'une récompense dans une autre succursale.
- Utilisation d'une carte prépayée dans plusieurs succursales.
- Annulation d'un achat ayant contribué à une récompense utilisée dans une autre succursale.
- Vérification de l'application de la même règle de fidélité dans toutes les succursales.
- Vérification des permissions de modification de la règle globale.
- Vérification de l'intégrité des soldes lors d'opérations concurrentes.

## Références

- ADR-0001 — Compteurs et historique.
- ADR-0002 — Annulation des transactions.
- ADR-0004 — Règles de fidélité configurables.
- ADR-0008 — Gestion des succursales et affectation des employés.