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
