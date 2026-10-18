# ADR-0007 — Gestion des employés et des permissions

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 3.6 — Des employés et des permissions

## Contexte

Dans la version 1 de Café Fidélité, les fonctionnalités du comptoir sont accessibles sans authentification.

L'application utilise déjà Django, qui possède un système intégré de gestion des utilisateurs, des groupes et des permissions.

La version 2 doit distinguer au minimum deux rôles : barista et gérant.

Chaque employé doit se connecter avec son propre compte et chaque transaction doit conserver l'identité de la personne qui l'a effectuée.

## Décision

Nous allons utiliser le système d'authentification et d'autorisation intégré à Django.

### 1. Comptes individuels

Chaque employé possédera un compte utilisateur personnel avec un identifiant et un mot de passe.

Les comptes partagés seront interdits.

Les mots de passe seront gérés par les mécanismes de sécurité intégrés à Django.

### 2. Gestion des rôles

Nous utiliserons deux groupes Django :

- `barista`
- `gerant`

Les utilisateurs du groupe `barista` pourront effectuer les opérations quotidiennes.

Les utilisateurs du groupe `gerant` disposeront également des autorisations nécessaires pour effectuer les opérations de gestion.

Les permissions seront définies explicitement plutôt que de donner automatiquement le statut de superutilisateur aux gérants.

### 3. Authentification obligatoire

Toutes les pages du comptoir nécessiteront une connexion.

Un utilisateur non authentifié sera redirigé vers la page de connexion.

Une fois connecté, il pourra accéder uniquement aux fonctionnalités autorisées pour son rôle.

### 4. Contrôle des autorisations

Les permissions seront vérifiées côté serveur.

Masquer un bouton dans une page HTML ne sera pas considéré comme une mesure de sécurité suffisante.

Les requêtes HTTP directes vers une fonctionnalité interdite seront également rejetées.

Les opérations sensibles vérifieront les autorisations avant toute modification de la base de données.

### 5. Traçabilité des transactions

Chaque nouvelle transaction conservera l'identité de l'employé qui l'a effectuée.

Les achats existants provenant de la version 1 seront conservés sans attribution artificielle à un employé.

Le champ représentant l'employé pourra donc être vide pour les anciennes transactions.

Les opérations d'annulation conserveront séparément l'identité du gérant responsable.

### 6. Annulation par un barista

Un barista ne pourra pas annuler ses propres transactions, même immédiatement après leur création.

Il devra demander l'intervention d'un gérant.

Cette décision assure une séparation claire entre les opérations quotidiennes et les corrections.

### 7. Gestion des comptes

La création et l'attribution des rôles seront effectuées par un administrateur autorisé.

Un gérant ne recevra pas automatiquement les permissions d'administration complète de Django.

La désactivation d'un compte employé empêchera ses futures connexions, sans effacer son identité des transactions historiques.

### 8. Données de démonstration

La version 2 fournira au minimum :

- Un compte de démonstration barista.
- Un compte de démonstration gérant.

La procédure de création de ces comptes et leurs identifiants seront documentés dans le README.

Les mots de passe de démonstration seront réservés à l'environnement local et ne devront pas être réutilisés pour de vrais comptes.

## Options écartées

### 1. Créer notre propre système d'authentification

Cette approche offrirait davantage de contrôle, mais augmenterait la complexité et les risques de sécurité.

Django fournit déjà les fonctionnalités nécessaires.

### 2. Utiliser un compte commun pour tous les employés

Cette solution serait simple, mais empêcherait d'identifier correctement l'employé responsable d'une transaction.

### 3. Donner les droits de superutilisateur aux gérants

Cette approche faciliterait l'accès aux fonctionnalités de gestion, mais accorderait des permissions beaucoup trop larges.

### 4. Contrôler les permissions uniquement dans les templates

Masquer les boutons ne suffit pas à empêcher un utilisateur d'envoyer directement une requête HTTP.

Les autorisations doivent être vérifiées côté serveur.

### 5. Permettre aux baristas d'annuler leurs propres achats

Cette solution faciliterait les corrections immédiates.

Nous l'écartons pour conserver une séparation claire des responsabilités.

## Conséquences

### Avantages

- Réutilisation du système de sécurité de Django.
- Comptes individuels pour chaque employé.
- Séparation claire des responsabilités.
- Traçabilité des transactions.
- Protection des fonctionnalités sensibles.
- Possibilité de désactiver un employé sans perdre l'historique.

### Inconvénients

- Les utilisateurs doivent se connecter avant d'utiliser le comptoir.
- Les groupes et permissions doivent être initialisés.
- Les vues existantes doivent être protégées.
- Les transactions de la version 1 ne peuvent pas être attribuées rétroactivement à un employé.
- Des tests d'autorisation doivent être ajoutés.

## Vérification

Nous développerons des tests automatisés pour vérifier que :

1. Un utilisateur non connecté ne peut pas accéder aux pages du comptoir.
2. Un barista peut rechercher et créer un client.
3. Un barista peut enregistrer un achat.
4. Un barista peut émettre une carte prépayée.
5. Un barista ne peut pas annuler une transaction.
6. Un barista ne peut pas consulter les rapports.
7. Un barista ne peut pas modifier les règles de fidélité.
8. Un barista ne peut pas effacer ou fusionner des clients.
9. Un gérant peut effectuer les opérations autorisées.
10. Chaque nouvelle transaction conserve son employé responsable.
11. Les anciennes transactions restent valides sans employé associé.
12. Les autorisations sont vérifiées côté serveur, y compris pour les requêtes POST directes.