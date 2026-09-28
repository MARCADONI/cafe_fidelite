# Cafe Fidelite

Systeme de fidelite pour un cafe permettant de gerer les clients, les achats, les recompenses et les cartes prepayees.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy cafe_fidelite

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

## Deployment

The following details how to deploy this application.

**********************************************************************************************
# Café Fidélité — Devoir 1

Projet réalisé dans le cadre du cours **8INF228 — Adaptation et qualité des applications** à l'Université du Québec à Chicoutimi (UQAC).

## Auteurs

* ADONI KOUADIO AMBOF MARC CHRISTIAN ADOK25040100
* KADIATOU LAMARANA BAH BAHK30629900

---

# 1. Description du projet

**Café Fidélité** est une application Web Django fonctionnant localement et permettant de gérer le programme de fidélité d'un café.

L'application permet de :

* créer un client ;
* rechercher un client par numéro de téléphone ;
* enregistrer un achat de café ;
* suivre la progression de fidélité d'un client ;
* obtenir une récompense après 10 achats payants ;
* utiliser une récompense pour obtenir un café gratuit ;
* émettre une carte prépayée de 11 cafés ;
* utiliser les cafés d'une carte prépayée ;
* conserver l'historique des achats ;
* consulter et administrer les données avec Django Admin.

L'application utilise **SQLite**. Aucun serveur de base de données externe n'est nécessaire.

---

# 2. Prérequis

Pour lancer le projet, il faut disposer de :

* **Python 3.13**
* **Git**
* une connexion Internet lors de l'installation initiale des dépendances

Le projet utilise **uv** pour installer et gérer les dépendances Python.

Aucune installation de PostgreSQL, MySQL, Docker ou autre serveur de base de données n'est nécessaire.

---

# 3. Récupération du projet

Cloner le dépôt GitHub :

```bash id="z5o0j8"
git clone <URL_DU_DEPOT_GITHUB>
```

Se déplacer dans le dossier du projet :

```bash id="k5w1zv"
cd cafe_fidelite
```

Le dossier doit notamment contenir :

```text id="ujz2w8"
cafe_fidelite/
├── cafe_fidelite/
├── config/
├── docs/
├── manage.py
├── pyproject.toml
├── uv.lock
├── README.md
└── AI-USAGE.md
```

Toutes les commandes suivantes doivent être exécutées depuis ce dossier, c'est-à-dire le dossier contenant `manage.py`.

---

# 4. Installation de uv

Vérifier si `uv` est déjà installé :

```bash id="92dthf"
uv --version
```

Si une version est affichée, passer directement à la section suivante.

Sinon, installer `uv` avec :

```bash id="t7qxk5"
python -m pip install uv
```

Si la commande `python` n'est pas disponible sous Windows, essayer :

```bash id="4tbwh7"
py -m pip install uv
```

Vérifier ensuite l'installation :

```bash id="frd8po"
uv --version
```

---

# 5. Installation des dépendances

Depuis le dossier contenant `manage.py`, exécuter :

```bash id="y1j1ps"
uv sync
```

Cette commande crée l'environnement virtuel `.venv` et installe les dépendances définies par le projet.

---

# 6. Vérification du projet

Avant de créer la base de données, vérifier la configuration Django :

```bash id="m2x8gq"
uv run python manage.py check
```

Le résultat attendu est :

```text id="xgk8z3"
System check identified no issues (0 silenced).
```

---

# 7. Création de la base de données

Le projet utilise **SQLite**.

Il n'est donc pas nécessaire d'installer ou de configurer un serveur de base de données.

Appliquer les migrations Django avec :

```bash id="ohjpc2"
uv run python manage.py migrate
```

Cette commande crée les tables nécessaires dans la base de données SQLite locale.

---

# 8. Création d'un compte administrateur

Pour accéder à Django Admin, créer un superutilisateur :

```bash id="g4kn2c"
uv run python manage.py createsuperuser
```

Django demandera notamment :

```text id="vnm06n"
Username:
Email address:
Password:
Password (again):
```

Les identifiants choisis ici seront utilisés pour se connecter à l'interface d'administration.

Cette étape est recommandée pour tester et consulter les données enregistrées dans l'application.

---

# 9. Lancement de l'application

Démarrer le serveur Django avec :

```bash id="kncgh9"
uv run python manage.py runserver
```

Si le démarrage fonctionne correctement, Django affiche une adresse similaire à :

```text id="s8t4ue"
Starting development server at http://127.0.0.1:8000/
```

Ouvrir ensuite un navigateur Web.

## Interface principale

Accéder à :

```text id="70u4l3"
http://127.0.0.1:8000/clients/
```

Cette page permet de rechercher ou de créer un client.

## Interface d'administration

Accéder à :

```text id="1b8g48"
http://127.0.0.1:8000/admin/
```

Utiliser le compte créé avec `createsuperuser`.

---

# 10. Procédure rapide de lancement

Pour un ordinateur sur lequel Python 3.13, Git et uv sont déjà installés, les commandes principales sont :

```bash id="xpm49p"
git clone <URL_DU_DEPOT_GITHUB>
cd cafe_fidelite
uv sync
uv run python manage.py check
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Puis ouvrir :

```text id="rfwr43"
http://127.0.0.1:8000/clients/
```

---

# 11. Utilisation de l'application

## 11.1 Créer un client

Accéder à :

```text id="daz8y1"
http://127.0.0.1:8000/clients/
```

Le formulaire de création permet de saisir :

* le nom ;
* le numéro de téléphone ;
* le courriel.

Le numéro de téléphone doit être unique.

---

## 11.2 Rechercher un client

Sur la même page, entrer le numéro de téléphone d'un client puis cliquer sur :

```text id="fhucx3"
Rechercher
```

Si le client existe, ses informations sont affichées.

Un bouton permet ensuite d'accéder à sa page d'achat.

---

## 11.3 Enregistrer un achat payant

Sur la page du client, cliquer sur :

```text id="1ggtr4"
Enregistrer un achat payant
```

Chaque achat payant augmente la progression de fidélité de 1.

Exemple :

```text id="h6cqxc"
0/10
 ↓
1/10
 ↓
2/10
 ↓
...
 ↓
9/10
 ↓
10e achat
 ↓
0/10 + 1 récompense
```

Après 10 achats payants, le client obtient une récompense disponible.

---

## 11.4 Utiliser une récompense

Lorsqu'un client possède au moins une récompense, le bouton :

```text id="pry19v"
Utiliser une récompense
```

apparaît.

L'utilisation de cette récompense :

* enregistre un achat de type `GRATUIT_FIDELITE` ;
* diminue le nombre de récompenses de 1 ;
* ne modifie pas la progression de fidélité.

---

# 12. Cartes prépayées

## 12.1 Émettre une carte

Sur la page du client, cliquer sur :

```text id="e72fx4"
Émettre une carte de 11 cafés
```

Une nouvelle carte est créée avec :

```text id="6y4hcg"
Cafés restants : 11 / 11
Statut : Active
```

L'application ne traite pas le paiement de la carte.

La transaction financière est effectuée à la caisse, en dehors de l'application.

---

## 12.2 Utiliser une carte

Pour une carte active, cliquer sur :

```text id="m65kkf"
Utiliser un café de cette carte
```

Chaque utilisation diminue le nombre de cafés restants :

```text id="uxw4gv"
11 → 10 → 9 → 8 → ... → 2 → 1 → 0
```

Chaque utilisation est enregistrée comme un achat de type :

```text id="t3yp7m"
PREPAYE
```

L'utilisation d'une carte prépayée ne fait pas progresser le compteur de fidélité.

---

## 12.3 Fin d'une carte

Lorsque le nombre de cafés atteint zéro :

```text id="a08gk8"
Cafés restants : 0 / 11
Statut : Terminée
```

La carte est automatiquement désactivée.

Elle reste néanmoins enregistrée afin de conserver l'historique.

Un client peut ensuite recevoir une nouvelle carte prépayée.

---

# 13. Types d'achats

Trois types d'achats sont enregistrés dans l'application :

| Type               | Description                            | Effet                   |
| ------------------ | -------------------------------------- | ----------------------- |
| `PAYANT`           | Achat normal                           | Progression fidélité +1 |
| `GRATUIT_FIDELITE` | Café obtenu avec une récompense        | Récompenses -1          |
| `PREPAYE`          | Café utilisé depuis une carte prépayée | Cafés restants -1       |

---

# 14. Django Admin

L'administration est disponible à :

```text id="e6tj4f"
http://127.0.0.1:8000/admin/
```

Elle permet notamment de consulter :

* les clients ;
* les fidélités ;
* les achats ;
* les cartes prépayées.

Elle peut être utilisée pour vérifier l'état de la base de données pendant l'évaluation.

---

# 15. Technologies utilisées

Le projet utilise principalement :

* Python 3.13 ;
* Django ;
* SQLite ;
* HTML ;
* Bootstrap ;
* Cookiecutter Django ;
* uv ;
* Git ;
* GitHub.

---

# 16. Structure de l'application

La partie principale développée pour le devoir se trouve dans :

```text id="kgns8g"
cafe_fidelite/loyalty/
```

Organisation principale :

```text id="ucbn37"
cafe_fidelite/
│
├── cafe_fidelite/
│   │
│   ├── loyalty/
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── loyalty/
│   │   │       ├── client_recherche_creation.html
│   │   │       └── enregistrer_achat.html
│   │   │
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── users/
│
├── config/
│   ├── settings/
│   └── urls.py
│
├── docs/
│   └── conception.md
│
├── AI-USAGE.md
├── manage.py
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 17. Architecture

La logique métier a été séparée des vues Django.

L'organisation générale est :

```text id="rx77wz"
Navigateur
    |
    v
Templates HTML
    |
    v
views.py
    |
    v
services.py
    |
    v
models.py
    |
    v
SQLite
```

`views.py` gère principalement les requêtes et réponses HTTP.

`services.py` contient les règles métier, notamment :

* l'enregistrement d'un achat payant ;
* l'utilisation d'une récompense ;
* l'émission d'une carte prépayée ;
* l'utilisation d'une carte prépayée.

`models.py` définit les données persistées.

---

# 18. Documentation de conception

Les décisions architecturales, le diagramme entité-relation, le diagramme ASCII, les cardinalités et les principes de conception sont documentés dans :

```text id="uykllz"
docs/conception.md
```

---

# 19. Utilisation de l'intelligence artificielle

L'utilisation de l'intelligence artificielle générative pendant le développement est déclarée dans :

```text id="7a9bve"
AI-USAGE.md
```

---

# 20. Arrêter le serveur

Dans le terminal où Django est lancé, utiliser :

```text id="vplimj"
Ctrl + C
```

pour arrêter le serveur de développement.

---

# 21. Résolution de problèmes

## `uv` n'est pas reconnu

Installer uv :

```bash id="9uv0t5"
python -m pip install uv
```

Puis fermer et rouvrir le terminal si nécessaire.

---

## Python 3.13 n'est pas disponible

Vérifier la version installée :

```bash id="vvhsoj"
python --version
```

Le projet a été développé et testé avec Python 3.13.

---

## Les tables n'existent pas

Exécuter :

```bash id="t4qm0k"
uv run python manage.py migrate
```

---

## Impossible d'accéder à Django Admin

Créer d'abord un administrateur :

```bash id="f3bscu"
uv run python manage.py createsuperuser
```

Puis relancer le serveur :

```bash id="r6bmfh"
uv run python manage.py runserver
```

et accéder à :

```text id="ah1m5v"
http://127.0.0.1:8000/admin/
```

---

## Vérifier la configuration Django

En cas de problème, exécuter :

```bash id="b3xfh7"
uv run python manage.py check
```

Le résultat attendu est :

```text id="md3xsv"
System check identified no issues (0 silenced).
```

---

# 22. Version

Ce dépôt correspond au **Devoir 1 — Système de fidélité pour un café, version 1** du cours **8INF228 — Adaptation et qualité des applications**.
