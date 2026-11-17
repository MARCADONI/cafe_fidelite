# Rétrospective — Version 2

## Bilan de la version 2

La version 2 de Café Fidélité a permis d'enrichir l'application initiale en introduisant les annulations de transactions, les rapports statistiques, les règles de fidélité configurables, l'anonymisation, la fusion des clients ainsi que l'authentification et les permissions des employés.

La séparation entre les modèles, les services métier, les vues et les formulaires a facilité cette évolution. L'utilisation de compteurs associés à un historique des transactions permet de consulter rapidement les soldes tout en conservant une traçabilité des opérations. Les modèles `MouvementFidelite` et `JournalAudit` renforcent cette traçabilité.

## Difficultés rencontrées

L'implémentation des annulations a représenté une difficulté particulière. Une transaction annulée peut avoir généré une récompense déjà utilisée, ce qui nécessite un mécanisme de dette d'étampes. Il était également nécessaire de conserver la cohérence entre les compteurs et l'historique.

La gestion des permissions a révélé des incohérences dans les noms des groupes Django. Ces erreurs ont été corrigées grâce aux tests automatisés. La dernière exécution de la suite de tests métier de la V2 compte 75 tests réussis.

## Impact des nouvelles exigences

La version 2 reposait sur l'hypothèse que l'application serait utilisée dans un seul café. Cette hypothèse est présente dans plusieurs parties du système : les modèles transactionnels, les services métier, les permissions et les rapports statistiques.

Les achats, les émissions de cartes et les annulations sont associés aux employés, mais ne possèdent aucune référence à une succursale. Les permissions reposent principalement sur les rôles des utilisateurs, sans restriction géographique. L'introduction d'un deuxième café nécessite donc des modifications dans plusieurs couches de l'application.

Cependant, les modèles `Client`, `Fidelite` et `CartePrepayee` sont déjà indépendants de la notion de café. Cette séparation constitue un avantage important pour la mise en place d'un programme de fidélité partagé entre plusieurs succursales.

## Préparation de la version 3

Pour la version 3, nous souhaitons conserver les mécanismes métier existants tout en introduisant explicitement la notion de succursale et les affectations des employés. Les contrôles d'accès devront prendre en compte le rôle de l'utilisateur ainsi que les succursales auxquelles il est autorisé à accéder.

Le passage de SQLite à PostgreSQL et la conteneurisation représentent également de nouveaux défis. Nous devrons préserver les données existantes, vérifier les soldes avant et après la migration et séparer la configuration de développement de celle de production.

Cette évolution montre l'importance de la séparation des responsabilités, mais également les limites d'une conception fondée sur une hypothèse métier implicite. Nous chercherons à rendre cette hypothèse explicite dans la V3, sans introduire de complexité inutile.