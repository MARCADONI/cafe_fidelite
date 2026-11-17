# ADR-0008 — Gestion des succursales et affectation des employés

## Statut

Accepté

## Contexte

La version 2 de Café Fidélité était destinée à un seul café. Les transactions étaient associées aux clients et aux employés, mais aucune information ne permettait d'identifier la succursale dans laquelle elles avaient été effectuées.

La version 3 doit permettre de gérer plusieurs succursales à partir d'une application et d'une base de données communes. Un employé peut également travailler dans plusieurs cafés.

Il est donc nécessaire de déterminer la succursale associée à chaque transaction et de vérifier que l'employé est autorisé à y travailler.

## Options envisagées

### Option 1 — Associer chaque employé à une seule succursale

Chaque employé possède une référence vers sa succursale.

Cette solution est simple, mais elle ne permet pas à un barista de travailler dans plusieurs cafés sans modifier son affectation ou créer plusieurs comptes.

### Option 2 — Permettre une sélection libre de la succursale

L'employé sélectionne la succursale lors de chaque transaction.

Cette solution est flexible, mais elle présente un risque d'erreur et nécessite des contrôles supplémentaires pour empêcher les accès non autorisés.

### Option 3 — Affectations multiples et sélection d'une succursale active

Les employés sont associés à une ou plusieurs succursales autorisées. Une succursale active est sélectionnée pour la session de travail.

Cette solution combine flexibilité et contrôle des accès.

## Décision

Nous retenons l'option 3.

Un modèle `Succursale` sera introduit afin de représenter chaque café. Il contiendra notamment un identifiant, un code unique, un nom et un état actif.

Un modèle `AffectationSuccursale` permettra d'associer les employés aux succursales dans lesquelles ils sont autorisés à travailler.

Lorsqu'un employé possède une seule succursale active autorisée, celle-ci sera sélectionnée automatiquement. Lorsqu'il possède plusieurs affectations, il devra sélectionner sa succursale de travail.

La succursale sélectionnée sera conservée dans la session Django. Le serveur vérifiera systématiquement que cette succursale est active et que l'utilisateur possède les autorisations nécessaires.

Les transactions suivantes posséderont une référence obligatoire vers une succursale :

- Les achats payants.
- Les utilisations de récompenses.
- Les consommations de cafés prépayés.
- Les émissions de cartes prépayées.
- Les annulations de transactions.

Une annulation sera rattachée à la succursale de la transaction originale. Les permissions seront vérifiées sur cette succursale, indépendamment de celle sélectionnée dans la session.

Le propriétaire pourra intervenir dans toutes les succursales.

Les transactions provenant de la version 2 seront associées à une première succursale créée lors de la migration.

L'ajout d'une nouvelle succursale pourra être réalisé par un utilisateur autorisé, sans modification du code source.

## Conséquences positives

- Un employé peut travailler dans plusieurs cafés avec un seul compte.
- Chaque transaction possède une origine identifiable.
- Les rapports peuvent être filtrés par succursale.
- Les permissions peuvent être vérifiées côté serveur.
- L'ajout de nouvelles succursales ne nécessite pas de modification du code.
- Les transactions historiques conservent leur succursale même si un employé change d'affectation.

## Conséquences négatives

- De nouveaux modèles et de nouvelles relations doivent être introduits.
- Les services métier doivent recevoir le contexte de la succursale.
- La gestion de la session et des autorisations devient plus complexe.
- Une migration est nécessaire pour associer les transactions existantes au premier café.
- Des tests supplémentaires sont nécessaires pour vérifier les accès entre succursales.