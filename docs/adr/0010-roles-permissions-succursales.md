# ADR-0010 — Rôles et permissions par succursale

## Statut

Accepté

## Contexte

Dans la version 2 de Café Fidélité, les permissions reposent sur deux groupes Django : Barista et Gerant.

Les baristas réalisent les opérations quotidiennes, tandis que les gérants disposent de permissions supplémentaires permettant notamment d'annuler des transactions, de consulter les rapports et de réaliser des opérations sensibles.

L'introduction de plusieurs succursales nécessite de compléter ce mécanisme. Un gérant ne doit pas pouvoir consulter les rapports ou modifier les transactions d'une autre succursale.

Le propriétaire doit cependant disposer d'un accès à l'ensemble du réseau.

## Options envisagées

### Option 1 — Créer des groupes Django pour chaque succursale

Cette solution consiste à créer des groupes tels que BaristaCafeA, GerantCafeA et GerantCafeB.

Elle permet de distinguer les utilisateurs selon leur succursale, mais entraîne une multiplication des groupes à chaque ouverture d'un nouveau café.

Elle rend également la gestion des permissions plus complexe.

### Option 2 — Utiliser uniquement les rôles Django

Cette solution consiste à conserver les groupes Barista et Gerant et à ajouter un groupe Proprietaire.

Elle permet de distinguer les responsabilités des utilisateurs, mais ne suffit pas à déterminer les succursales auxquelles ils peuvent accéder.

### Option 3 — Combiner les rôles et les affectations aux succursales

Cette solution consiste à utiliser les groupes Django pour représenter les responsabilités des utilisateurs et le modèle AffectationSuccursale pour déterminer leur périmètre d'accès.

Elle permet de distinguer les permissions fonctionnelles des restrictions liées aux succursales.

## Décision

Nous retenons l'option 3.

Les groupes Django suivants seront utilisés :

- Barista
- Gerant
- Proprietaire

Les groupes déterminent les opérations qu'un utilisateur peut effectuer. Les affectations déterminent les succursales dans lesquelles ces opérations sont autorisées.

### Barista

Le barista peut effectuer les opérations courantes dans les succursales auxquelles il est affecté :

- Rechercher et créer des clients.
- Enregistrer des achats payants.
- Utiliser des récompenses.
- Émettre et utiliser des cartes prépayées.

Il ne peut pas annuler des transactions, consulter les rapports administratifs ou effectuer des opérations sensibles.

### Gérant

Le gérant dispose des permissions du barista dans sa succursale.

Il peut également :

- Annuler les transactions appartenant à sa succursale.
- Consulter les rapports de sa succursale.
- Consulter les entrées du journal d'audit relevant de sa succursale.

Il ne peut pas consulter les rapports d'une autre succursale ni modifier ses transactions.

Chaque gérant est affecté à une seule succursale dans la version 3.

Les opérations ayant un impact sur l'ensemble du réseau, notamment la modification des règles globales, la fusion et l'anonymisation des clients, sont réservées au propriétaire.

### Propriétaire

Le propriétaire dispose des permissions métier de l'ensemble des rôles dans toutes les succursales.

Il peut notamment :

- Effectuer les opérations quotidiennes.
- Annuler les transactions de toutes les succursales.
- Consulter les rapports locaux et globaux.
- Consulter l'ensemble du journal d'audit.
- Modifier les règles de fidélité.
- Fusionner et anonymiser les clients.
- Créer et gérer les succursales.
- Gérer les affectations des employés.

Le rôle Proprietaire est un rôle métier distinct du statut de superutilisateur Django.

## Vérification des permissions

Les permissions seront systématiquement vérifiées côté serveur.

Les décorateurs existants `employe_required` et `gerant_required` seront adaptés. Un mécanisme centralisé permettra également de vérifier les autorisations du propriétaire et les affectations aux succursales.

Les contrôles seront appliqués dans les vues et dans les services métier réalisant les opérations sensibles.

Les requêtes de consultation des transactions, des rapports et du journal d'audit seront filtrées selon le périmètre autorisé.

La succursale active conservée dans la session sera vérifiée avant chaque opération concernée.

Lors d'une annulation, le serveur vérifiera les permissions sur la succursale de la transaction originale.

Un utilisateur ne pourra pas contourner les restrictions en modifiant une URL, un identifiant de transaction, un formulaire ou les paramètres d'une requête HTTP.

L'affichage ou le masquage des fonctionnalités dans les templates constitue uniquement une mesure ergonomique et ne remplace pas les contrôles côté serveur.

## Migration des permissions

Les comptes et les groupes existants de la version 2 seront conservés.

Les employés appartenant aux groupes Barista et Gerant seront affectés à la première succursale lors de la migration.

Le groupe Proprietaire sera créé dans la version 3.

Aucun employé existant ne recevra automatiquement les permissions du propriétaire.

## Conséquences positives

- Séparation claire entre les responsabilités et le périmètre d'accès.
- Conservation du mécanisme d'authentification Django existant.
- Protection des transactions et des rapports de chaque succursale.
- Possibilité d'ajouter des succursales sans créer de nouveaux groupes.
- Centralisation des contrôles d'autorisation.
- Réduction du risque d'accès non autorisé.

## Conséquences négatives

- Augmentation de la complexité des contrôles d'accès.
- Adaptation nécessaire des vues et des services métier existants.
- Gestion supplémentaire des affectations des employés.
- Nécessité de tests spécifiques aux accès entre succursales.

## Tests prévus

- Vérifier qu'un barista peut enregistrer une transaction dans une succursale autorisée.
- Vérifier qu'un barista ne peut pas effectuer une annulation.
- Vérifier qu'un employé ne peut pas sélectionner une succursale non autorisée.
- Vérifier qu'un gérant peut annuler une transaction de sa succursale.
- Vérifier qu'un gérant ne peut pas annuler une transaction d'une autre succursale.
- Vérifier qu'un gérant ne peut pas consulter les rapports d'une autre succursale.
- Vérifier qu'un gérant ne peut pas modifier les règles globales.
- Vérifier qu'un propriétaire peut accéder à toutes les succursales.
- Vérifier que les restrictions restent effectives lors d'un accès direct aux URL.

## Références

- ADR-0007 — Rôles et permissions.
- ADR-0008 — Gestion des succursales et affectation des employés.
- ADR-0009 — Programme de fidélité partagé entre les succursales.

Cet ADR remplace l'ADR-0007.