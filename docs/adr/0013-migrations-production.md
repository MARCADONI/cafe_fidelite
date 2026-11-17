# ADR-0013 — Exécution des migrations Django en production

## Statut

Accepté

## Contexte

Dans la version 2 de Café Fidélité, l'application utilise SQLite et les migrations Django sont exécutées manuellement dans l'environnement local de développement.

La version 3 introduit PostgreSQL et une architecture conteneurisée avec Docker Compose.

Le système doit pouvoir démarrer de manière fiable à partir d'une installation neuve, tout en permettant la migration des données existantes de la version 2.

Il est nécessaire de déterminer à quel moment les migrations Django doivent être exécutées.

## Options envisagées

### Option 1 — Exécution manuelle des migrations

Les migrations sont exécutées par l'administrateur à l'aide d'une commande Docker Compose.

Cette solution permet de contrôler précisément le moment où le schéma de la base de données est modifié.

Cependant, elle nécessite une intervention supplémentaire et présente un risque d'oubli lors du démarrage ou d'une mise à jour.

### Option 2 — Exécution automatique au démarrage

Les migrations sont exécutées automatiquement avant le démarrage du serveur d'application.

Cette solution simplifie l'installation et garantit que l'application utilise un schéma compatible avec sa version.

Elle nécessite toutefois de vérifier la disponibilité de PostgreSQL avant l'exécution des migrations.

### Option 3 — Utiliser un conteneur dédié aux migrations

Un conteneur temporaire exécute les migrations avant le démarrage du conteneur Django.

Cette solution sépare les responsabilités et peut être pertinente dans une architecture comportant plusieurs instances de l'application.

Elle introduit cependant une complexité supplémentaire pour une application utilisant une seule instance.

## Décision

Nous retenons l'option 2.

Les migrations Django seront exécutées automatiquement au démarrage du conteneur de l'application.

Un script de démarrage sera responsable de l'exécution des migrations avant le lancement du serveur Gunicorn.

La séquence de démarrage sera la suivante :

1. Démarrage du conteneur PostgreSQL.
2. Vérification de la disponibilité de PostgreSQL à l'aide d'un healthcheck.
3. Démarrage du conteneur Django.
4. Exécution de la commande `python manage.py migrate --noinput`.
5. Démarrage du serveur Gunicorn uniquement si les migrations réussissent.

Docker Compose utilisera une dépendance conditionnée par l'état de santé du conteneur PostgreSQL.

En cas d'échec des migrations, le script de démarrage devra interrompre le lancement de l'application et transmettre les erreurs à la sortie standard ou à la sortie d'erreur.

## Conservation des migrations existantes

Les migrations livrées dans les versions précédentes ne seront ni supprimées ni réécrites.

Les modifications nécessaires à la version 3 seront introduites dans de nouvelles migrations Django.

La création de la première succursale et l'association des transactions historiques à cette succursale seront réalisées à l'aide de migrations de données.

Les migrations devront préserver les soldes de fidélité, les cartes prépayées, les transactions et les informations historiques.

## Migration de SQLite vers PostgreSQL

L'exécution automatique des migrations Django concerne principalement l'évolution du schéma de la base de données.

Elle ne constitue pas, à elle seule, une procédure de transfert des données entre SQLite et PostgreSQL.

Le transfert des données de la version 2 fera l'objet d'une procédure distincte, documentée dans `docs/migration.md`.

Cette procédure devra notamment permettre :

- La sauvegarde de la base SQLite existante.
- Le transfert des données vers PostgreSQL.
- L'association des transactions historiques à la première succursale.
- La conservation des comptes utilisateurs et des relations entre les données.
- La comparaison des soldes avant et après le transfert.

L'ordre exact des opérations sera validé à l'aide d'une migration réelle des données de démonstration de la version 2.

Aucune donnée de démonstration de la version 3 ne devra être chargée automatiquement pendant le transfert d'une base existante.

## Persistance des données

PostgreSQL utilisera un volume Docker nommé.

Les données seront conservées lors de l'arrêt et du redémarrage des conteneurs.

L'exécution répétée de la commande de migration ne devra pas recréer les données existantes ni réinitialiser les soldes des clients.

Une sauvegarde de la base devra être réalisée avant toute migration importante d'une installation existante.

## Conséquences positives

- Installation simplifiée de l'application.
- Réduction du risque d'oubli des migrations.
- Synchronisation du schéma avec la version de l'application.
- Conservation de l'historique des migrations Django.
- Détection des erreurs avant le démarrage de Gunicorn.
- Compatibilité avec une architecture utilisant une seule instance de l'application.

## Conséquences négatives

- Le démarrage de l'application peut être ralenti par les migrations.
- Une migration défectueuse peut empêcher le démarrage du service.
- Les migrations doivent être testées avant leur utilisation en production.
- Une architecture future comportant plusieurs instances pourrait nécessiter un mécanisme dédié aux migrations.

## Tests prévus

- Vérifier le démarrage sur une base PostgreSQL vide.
- Vérifier que Django attend la disponibilité de PostgreSQL.
- Vérifier l'application automatique des migrations.
- Vérifier que Gunicorn ne démarre pas lorsqu'une migration échoue.
- Vérifier qu'un redémarrage ne duplique pas les données.
- Vérifier la persistance des données après un arrêt et un redémarrage des conteneurs.
- Vérifier la conservation des soldes lors de la migration de la version 2 vers la version 3.

## Références

- ADR-0001 — Compteurs et historique.
- ADR-0008 — Gestion des succursales et affectation des employés.
- Documentation de migration : `docs/migration.md`.

