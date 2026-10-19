# Utilisation de l'intelligence artificielle générative

## Outil utilisé

Dans le cadre de ce projet, nous avons utilisé **ChatGPT d'OpenAI** comme outil d'assistance à la conception, au développement, au débogage et à la documentation.

L'intelligence artificielle a été utilisée comme outil d'accompagnement et d'explication pendant le développement du projet.

---

## Utilisations principales

### 1. Compréhension du sujet

ChatGPT a été utilisé pour nous aider à analyser les exigences du devoir et à identifier les principales fonctionnalités à développer :

* gestion des clients ;
* enregistrement des achats ;
* programme de fidélité ;
* gestion des récompenses ;
* cartes prépayées.

L'outil a également été utilisé pour réfléchir aux zones de conception laissées ouvertes dans l'énoncé.

---

### 2. Conception du modèle de données

ChatGPT a été utilisé pour nous assister dans la définition des principales entités :

* `Client` ;
* `Fidelite` ;
* `Achat` ;
* `CartePrepayee`.

L'outil nous a également aidés à réfléchir aux relations entre ces entités et à produire une représentation du diagramme entité-relation.

Les décisions de conception retenues ont ensuite été intégrées dans `docs/conception.md`.

---

### 3. Architecture de l'application

ChatGPT a été utilisé pour discuter de l'organisation du projet Django et de la séparation entre :

```text
views.py
services.py
models.py
templates
```

Une attention particulière a été portée à la séparation entre la gestion des requêtes HTTP et la logique métier.

La logique de fidélité et de cartes prépayées a ainsi été regroupée dans `services.py`.

---

### 4. Assistance à l'implémentation

ChatGPT a fourni des explications et des propositions de code pour plusieurs fonctionnalités, notamment :

* les modèles Django ;
* la configuration de Django Admin ;
* les formulaires ;
* la recherche et la création des clients ;
* l'enregistrement des achats ;
* le calcul de la progression de fidélité ;
* la création et l'utilisation des récompenses ;
* l'émission des cartes prépayées ;
* l'utilisation des cafés disponibles sur les cartes prépayées.

Le code proposé a été intégré progressivement et testé dans l'environnement de développement.

---

### 5. Débogage

ChatGPT a également été utilisé pour aider à comprendre et résoudre certaines erreurs rencontrées pendant le développement.

Parmi les problèmes examinés :

* configuration de Cookiecutter Django ;
* configuration de SQLite ;
* migrations Django ;
* configuration d'une application Django ;
* emplacement des templates ;
* erreurs d'indentation Python ;
* erreurs ou avertissements dans les templates HTML/CSS.

Les corrections ont été testées avec les outils Django, notamment :

```bash
python manage.py check
```

ainsi qu'en utilisant directement les fonctionnalités de l'application.

---

### 6. Documentation

ChatGPT a été utilisé comme assistance à la rédaction et à l'organisation de la documentation du projet, notamment :

* `README.md` ;
* `docs/conception.md` ;
* `AI-USAGE.md`.

La documentation de conception décrit les décisions retenues ainsi que leur relation avec certains principes étudiés dans le cours.

---

## Exemples de questions et demandes faites à l'IA

Les interactions avec l'IA ont notamment porté sur des demandes similaires aux suivantes :

> Comment structurer le projet Django afin qu'il puisse évoluer au cours des prochains devoirs ?

> Comment représenter les relations entre Client, Fidelite, Achat et CartePrepayee ?

> Où devrait être placée la logique métier du programme de fidélité ?

> Comment enregistrer une récompense après 10 achats payants ?

> Comment permettre l'utilisation d'une récompense sans augmenter la progression de fidélité ?

> Comment gérer une carte prépayée contenant 11 cafés ?

> Comment séparer la logique métier des vues Django ?

> Comment corriger une erreur d'indentation ou de configuration Django ?

---

## Vérification et responsabilité

Les propositions produites avec l'aide de l'intelligence artificielle ont été intégrées progressivement au projet.

Les fonctionnalités ont été vérifiées manuellement pendant le développement, notamment :

* création d'un client ;
* recherche d'un client ;
* refus d'un numéro de téléphone déjà utilisé ;
* enregistrement d'achats payants ;
* progression de fidélité de 0 à 10 ;
* création d'une récompense après 10 achats ;
* utilisation d'une récompense ;
* émission d'une carte prépayée de 11 cafés ;
* diminution du nombre de cafés disponibles ;
* désactivation d'une carte arrivée à zéro ;
* vérification de l'historique dans Django Admin.

L'utilisation de l'intelligence artificielle ne remplace donc pas la vérification du fonctionnement de l'application par les membres de l'équipe.


# Utilisation de l'intelligence artificielle — Devoir 2

## 1. Contexte

Dans le cadre du Devoir 2 du cours 8INF228 — Adaptation et qualité des applications, nous avons continué à utiliser ChatGPT d'OpenAI comme outil d'assistance au développement et à l'évolution de Café Fidélité.

L'utilisation de cet outil a principalement concerné la compréhension des nouvelles exigences, la conception des fonctionnalités, l'implémentation, le débogage, les tests et la documentation.

## 2. Analyse des nouvelles exigences

ChatGPT a été utilisé pour analyser les six nouvelles demandes :

- Annulation des transactions.
- Production de rapports statistiques.
- Modification des règles de fidélité.
- Effacement des renseignements personnels.
- Fusion des fiches clients.
- Gestion des employés et des permissions.

L'outil a contribué à identifier les impacts de ces fonctionnalités sur les modèles existants, les services métier et les interfaces Django.

## 3. Assistance à la conception

ChatGPT a participé à la réflexion sur plusieurs décisions d'architecture, notamment :

- La conservation des compteurs et de l'historique des transactions.
- La gestion des effets des annulations.
- La préservation des données lors des migrations.
- La séparation entre les opérations métier et les contrôles d'accès.
- La traçabilité des modifications sensibles.

L'outil a également aidé à structurer les documents ADR et à expliciter les avantages, les inconvénients et les compromis des décisions retenues.

## 4. Assistance à l'implémentation

ChatGPT a fourni des explications et des propositions de code pour faire évoluer l'application Django.

Les principales fonctionnalités concernées sont :

### Annulations

Assistance à la conception et à l'implémentation des mécanismes d'annulation des achats payants, des récompenses et des opérations liées aux cartes prépayées.

### Règles de fidélité

Assistance à la gestion des seuils de fidélité configurables et de leur application aux transactions.

### Gestion des clients

Assistance à la mise en œuvre de la fusion des fiches clients et de l'anonymisation des renseignements personnels.

### Sécurité

Assistance à l'utilisation de l'authentification Django et des groupes d'utilisateurs pour protéger les fonctionnalités réservées aux gérants.

### Traçabilité

Assistance à l'intégration des modèles `MouvementFidelite` et `JournalAudit`.

## 5. Assistance aux tests automatisés

ChatGPT a été utilisé pour proposer des scénarios de tests Django couvrant notamment :

- Les opérations de fidélité.
- Les annulations et leurs conséquences.
- La fusion des clients.
- L'anonymisation.
- Les contrôles d'accès.
- Le journal d'audit.

L'outil a également été utilisé pour analyser les messages d'erreur produits lors de l'exécution des tests.

La suite de tests comportait 64 tests lors de la dernière exécution connue. La réussite complète de cette suite reste à confirmer après les corrections.

## 6. Débogage et limites rencontrées

L'assistance de ChatGPT a été utile pour identifier certaines erreurs, mais les propositions générées n'étaient pas toujours directement adaptées au code existant.

Par exemple, des difficultés ont été rencontrées avec :

- Des références à des variables non définies.
- Des propositions utilisant des noms de champs différents de ceux des modèles Django existants.
- Des problèmes d'indentation dans les fichiers Python.
- La préparation des données nécessaires à certains tests.

Ces situations ont montré la nécessité de confronter les propositions de l'IA au code réel et aux résultats des tests.

## 7. Assistance à la documentation

ChatGPT a contribué à la préparation et à la mise à jour des documents suivants :

- `README.md`.
- `docs/Conception.md`.
- `docs/migration.md`.
- Le document de rétrospective.
- Les sept décisions d'architecture du dossier `docs/ADR/`.
- `AI-USAGE.md`.

Cette assistance a notamment permis de structurer les explications, de présenter les décisions techniques et d'identifier les éléments restant à vérifier.

## 8. Exemples de demandes adressées à ChatGPT

Les échanges ont notamment porté sur des questions telles que :

> Comment annuler une transaction sans perdre son historique ?

> Comment conserver la cohérence des compteurs de fidélité après une annulation ?

> Comment fusionner deux comptes clients tout en préservant leurs avantages ?

> Comment anonymiser les renseignements personnels sans supprimer les statistiques historiques ?

> Comment protéger une interface Django pour qu'elle soit accessible uniquement aux gérants ?

> Comment enregistrer les opérations sensibles dans un journal d'audit ?

> Comment organiser et exécuter les tests automatisés Django ?

> Comment documenter les décisions d'architecture et les migrations du projet ?

## 9. Vérification et responsabilité

Les propositions de l'intelligence artificielle ont servi de support au développement.

Le code et les recommandations ont été intégrés progressivement dans le projet, puis examinés à l'aide des outils Django et des tests disponibles.

Les membres de l'équipe demeurent responsables des décisions retenues, de la validation du comportement de l'application et du contenu remis dans le cadre du devoir.

L'intelligence artificielle a constitué un outil d'assistance, et non une garantie de correction ou de conformité aux exigences.