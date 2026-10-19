# Rétrospective — Devoir 1

## 1. Analyse des six nouvelles demandes

### Annuler une transaction
La version 1 conserve les achats dans la table `Achat`, mais ne prévoit aucun mécanisme d'annulation. Les compteurs de fidélité et les soldes des cartes prépayées sont mis à jour directement. Il faudrait donc ajouter une logique permettant d'annuler une opération tout en conservant sa trace et en corrigeant les soldes.

### Produire des rapports
La version 1 enregistre les achats avec leur type et leur date. Elle possède donc une partie des données nécessaires aux rapports. Cependant, aucune interface ne permet actuellement de consulter des statistiques sur une période. Il faudra également décider comment traiter les transactions annulées.

### Modifier la règle de fidélité
Le seuil de 10 cafés est directement inscrit dans le code du service de fidélité. Un gérant ne peut pas le modifier depuis l'application. Il faudra rendre cette règle configurable et conserver les informations nécessaires pour comprendre les récompenses attribuées avant et après un changement.

### Effacer un client
La version 1 utilise une relation entre les clients et leurs achats. La suppression d'un client entraîne actuellement la suppression de ses achats associés, ce qui risque de modifier les statistiques historiques. Il faudra prévoir une stratégie d'anonymisation ou de conservation des transactions sans renseignements personnels.

### Fusionner deux fiches clients
La version 1 ne permet pas de fusionner deux clients. Leurs achats, leurs cartes prépayées et leurs soldes de fidélité sont associés à des fiches distinctes. Il faudra ajouter une opération permettant de regrouper ces informations sans perdre les avantages accumulés.

### Gérer les employés et les permissions
La version 1 possède une administration Django, mais les écrans du comptoir ne sont pas protégés par des rôles barista et gérant. Les achats ne conservent pas non plus l'identité de l'employé responsable. Il faudra ajouter une authentification et des autorisations adaptées.

## 2. Ce qui nous a surpris

Les nouvelles demandes montrent qu'un système de fidélité ne consiste pas seulement à incrémenter des compteurs. Il doit aussi permettre de retracer les opérations, corriger les erreurs, préserver les données et distinguer les responsabilités des employés.

La nécessité de conserver les données existantes pendant les migrations est particulièrement importante.

## 3. Une décision que nous prendrions autrement

Dans la version 1, nous avons choisi de conserver à la fois les achats et des compteurs représentant les soldes actuels. Cette approche simplifie l'affichage des informations d'un client, mais peut provoquer des incohérences si une transaction doit être annulée ou corrigée.

Avec le recul, nous aurions défini dès le départ une stratégie explicite de traçabilité et de synchronisation entre les transactions et les soldes.

Pour la version 2, nous allons réexaminer cette décision dans un ADR, en tenant compte des besoins d'annulation, de rapports et de migration.


# Rétrospective — Devoir 2 : Bilan du développement

## 4. Évolution de l'application

Le Devoir 2 a permis de faire évoluer Café Fidélité à partir de l'architecture développée lors du Devoir 1.

L'objectif principal était d'intégrer six nouvelles demandes tout en conservant les fonctionnalités existantes et en améliorant la qualité du logiciel.

Les principales évolutions réalisées concernent :

- L'annulation des transactions.
- La production de rapports statistiques.
- La configuration des règles de fidélité.
- L'anonymisation des clients.
- La fusion des fiches clients.
- L'authentification et les permissions des employés.

Des mécanismes supplémentaires de traçabilité ont également été ajoutés, notamment avec les modèles `MouvementFidelite` et `JournalAudit`.

## 5. Difficultés rencontrées

### 5.1 Cohérence des soldes lors des annulations

L'une des principales difficultés concernait les annulations de transactions.

Dans la version 1, les achats modifiaient directement les compteurs de fidélité ou les soldes des cartes prépayées.

L'ajout des annulations nécessitait donc de prendre en compte les effets de chaque opération afin de corriger les soldes sans supprimer les informations historiques.

**Solution adoptée :** enrichir les informations conservées sur les transactions et centraliser les règles de correction dans les services métier.

### 5.2 Évolution de la base de données

L'ajout de nouveaux modèles et champs a nécessité plusieurs migrations Django.

Le défi consistait à faire évoluer le schéma sans supprimer les données existantes.

**Solution adoptée :** conserver les migrations initiales et ajouter progressivement les nouvelles structures nécessaires.

Les migrations de l'application `loyalty`, de `0001_initial` à `0011_journalaudit`, ont été appliquées dans l'environnement local.

La validation comparative des données avant et après migration doit être documentée séparément.

### 5.3 Fusion et anonymisation des clients

La fusion de deux clients et l'anonymisation d'un compte introduisent des contraintes supplémentaires.

Il fallait notamment empêcher qu'un compte devenu inactif soit réutilisé pour effectuer des opérations métier.

**Solution adoptée :** introduire des états permettant de distinguer les clients actifs, fusionnés et anonymisés, ainsi qu'une validation centralisée dans les services.

### 5.4 Gestion des permissions

L'ajout des fonctions administratives a nécessité de distinguer les opérations courantes des opérations sensibles.

**Solution adoptée :** utiliser l'authentification Django et les groupes d'utilisateurs pour contrôler l'accès aux interfaces réservées aux gérants.

Les vérifications sont réalisées côté serveur afin de ne pas dépendre uniquement de l'affichage des boutons dans l'interface.

### 5.5 Traçabilité des opérations

L'historique des achats ne suffisait pas à identifier toutes les actions administratives sensibles.

**Solution adoptée :** introduire un journal d'audit permettant d'enregistrer notamment les fusions, les anonymisations, les annulations et la programmation des règles de fidélité.

Cette évolution facilite l'analyse des opérations et le diagnostic des problèmes.

### 5.6 Tests et débogage

Les tests automatisés ont permis d'identifier des erreurs dans certaines fonctionnalités.

Parmi les difficultés rencontrées :

- Une référence à une variable non définie dans la journalisation de l'annulation d'une vente de carte.
- Une initialisation incorrecte des comptes de fidélité dans un test de fusion.
- Des problèmes d'indentation lors de l'ajout de nouveaux tests.

Ces problèmes ont montré l'importance de vérifier les interactions entre les services métier, les modèles et les tests.

La suite contient actuellement 64 tests détectés. Le résultat final doit être confirmé après les dernières corrections.

## 6. Ce que nous avons appris

Ce projet a permis de mieux comprendre plusieurs principes de développement logiciel.

**La séparation des responsabilités** facilite l'évolution du système : les vues gèrent les interactions HTTP, tandis que les services regroupent les règles métier.

**La traçabilité doit être prévue dès la conception** : elle devient particulièrement importante lorsqu'un système doit prendre en charge des annulations et des corrections.

**Les migrations nécessitent une stratégie de conservation des données** : modifier le schéma ne suffit pas, il faut également vérifier les informations existantes.

**Les tests automatisés sont essentiels** : ils permettent de détecter les régressions et de vérifier les comportements attendus.

**Les contrôles d'accès doivent être appliqués côté serveur** : masquer une fonctionnalité dans l'interface ne constitue pas une protection suffisante.

## 7. Une décision que nous prendrions autrement

Si nous devions recommencer le projet, nous définirions dès la première version un mécanisme plus complet de traçabilité des opérations.

Nous prévoirions notamment :

- L'identification de l'employé responsable.
- L'enregistrement explicite des effets de chaque transaction.
- Un historique des mouvements de fidélité.
- Des règles d'annulation documentées dès le départ.
- Des tests couvrant les scénarios de correction et les cas limites.

Cette approche aurait réduit la complexité des adaptations nécessaires lors du Devoir 2.

## 8. Améliorations futures

Plusieurs améliorations pourraient être envisagées :

- Renforcer les tests automatisés et leur couverture.
- Améliorer l'ergonomie des interfaces administratives.
- Ajouter des filtres avancés au journal d'audit.
- Faciliter l'exportation des rapports.
- Améliorer les outils de vérification de la cohérence des données.
- Automatiser davantage les vérifications lors des évolutions du projet.

## 9. Conclusion

Le Devoir 2 a montré qu'une application fonctionnelle peut nécessiter des adaptations importantes lorsque de nouvelles exigences apparaissent.

L'évolution de Café Fidélité a permis de mettre en pratique les principes de séparation des responsabilités, de maintenabilité, de traçabilité, de contrôle d'accès et de validation des comportements.

L'expérience acquise souligne l'importance de concevoir un logiciel non seulement pour répondre aux besoins actuels, mais également pour faciliter ses évolutions futures.