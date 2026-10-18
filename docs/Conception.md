# Conception — Système de fidélité pour un café

## 1. Présentation

Cette application est un système local de gestion de fidélité destiné à un café.

Elle permet principalement :

* d'enregistrer et rechercher des clients ;
* d'enregistrer les achats de cafés ;
* de suivre la progression du programme de fidélité ;
* d'accorder une récompense après 10 cafés achetés ;
* d'utiliser une récompense pour obtenir un café gratuit ;
* d'émettre des cartes prépayées contenant 11 cafés ;
* de suivre l'utilisation des cartes prépayées.

L'application est développée avec Python et Django et utilise SQLite comme base de données.

---

## 2. Entités principales

Le système repose sur quatre entités principales :

### Client

Représente un client inscrit au programme.

Attributs principaux :

* `id` : identifiant unique ;
* `nom` : nom du client ;
* `telephone` : numéro de téléphone unique utilisé pour identifier le client ;
* `courriel` : adresse courriel facultative ;
* `date_creation` : date d'inscription du client.

### Fidelite

Représente l'état du programme de fidélité d'un client.

Attributs principaux :

* `id` : identifiant unique ;
* `client` : client associé ;
* `progression` : nombre de cafés payants comptabilisés vers la prochaine récompense ;
* `recompenses` : nombre de cafés gratuits disponibles.

Une fidélité appartient à un seul client et un client possède au maximum un état de fidélité.

### Achat

Représente un café enregistré dans le système.

Attributs principaux :

* `id` : identifiant unique ;
* `client` : client ayant effectué l'achat ou utilisé un avantage ;
* `type_achat` : type de l'opération ;
* `carte_prepayee` : carte utilisée, lorsqu'il s'agit d'un café prépayé ;
* `date_achat` : date et heure de l'opération.

Trois types d'achats sont actuellement supportés :

* `PAYANT` : achat normal faisant progresser la fidélité ;
* `GRATUIT_FIDELITE` : café obtenu grâce à une récompense ;
* `PREPAYE` : café consommé à partir d'une carte prépayée.

### CartePrepayee

Représente une carte de 11 cafés achetée par un client.

Attributs principaux :

* `id` : identifiant unique ;
* `client` : propriétaire de la carte ;
* `cafes_restants` : nombre de cafés encore disponibles ;
* `date_emission` : date d'émission de la carte ;
* `active` : indique si la carte peut encore être utilisée.

---

## 3. Diagramme entité-relation

```mermaid
erDiagram
    CLIENT ||--o| FIDELITE : possede
    CLIENT ||--o{ ACHAT : effectue
    CLIENT ||--o{ CARTE_PREPAYEE : possede
    CARTE_PREPAYEE ||--o{ ACHAT : peut_etre_utilisee_pour

    CLIENT {
        int id PK
        string nom
        string telephone UK
        string courriel
        datetime date_creation
    }

    FIDELITE {
        int id PK
        int client_id FK
        int progression
        int recompenses
    }

    CARTE_PREPAYEE {
        int id PK
        int client_id FK
        int cafes_restants
        datetime date_emission
        boolean active
    }

    ACHAT {
        int id PK
        int client_id FK
        string type_achat
        int carte_prepayee_id FK
        datetime date_achat
    }
```

### Cardinalités

Les principales relations sont :

* un `Client` possède au maximum une `Fidelite` ;
* un `Client` peut avoir plusieurs `Achat` ;
* un `Client` peut posséder plusieurs `CartePrepayee` ;
* une `CartePrepayee` peut être associée à plusieurs `Achat` de type `PREPAYE` ;
* un `Achat` peut ne pas avoir de carte prépayée associée.

---

## 4. Diagramme ASCII

Le même modèle peut être représenté de façon simplifiée comme suit :

```text
                         ┌──────────────────────┐
                         │        CLIENT        │
                         ├──────────────────────┤
                         │ id                   │
                         │ nom                  │
                         │ telephone (unique)   │
                         │ courriel             │
                         │ date_creation        │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │ 1               │ 1               │ 1
                  │                 │                 │
                  │ 0..1            │ 0..N            │ 0..N
                  ▼                 ▼                 ▼
       ┌──────────────────┐ ┌──────────────────┐ ┌────────────────────┐
       │     FIDELITE     │ │      ACHAT       │ │  CARTE_PREPAYEE   │
       ├──────────────────┤ ├──────────────────┤ ├────────────────────┤
       │ id               │ │ id               │ │ id                 │
       │ client_id        │ │ client_id        │ │ client_id          │
       │ progression      │ │ type_achat       │ │ cafes_restants     │
       │ recompenses      │ │ date_achat       │ │ date_emission      │
       └──────────────────┘ │ carte_prepayee_id│ │ active             │
                            └────────▲─────────┘ └──────────┬─────────┘
                                     │                      │
                                     │       0..N           │ 1
                                     └──────────────────────┘
                                      achats avec la carte
```

---

## 5. Choix d'identification du client

Le numéro de téléphone est utilisé comme principal moyen de recherche et d'identification du client.

Le champ `telephone` est donc unique.

Nous avons préféré le téléphone au nom, car plusieurs clients peuvent avoir le même nom. Le courriel reste facultatif afin de ne pas empêcher l'inscription d'un client qui ne souhaite pas le fournir.

---

## 6. Programme de fidélité

Le programme de fidélité et les cartes prépayées sont traités comme deux mécanismes distincts.

Pour la fidélité, seuls les achats de type `PAYANT` augmentent la progression.

La règle est :

```text
Achat PAYANT
      |
      v
progression + 1
      |
      v
progression >= 10 ?
   /          \
 NON          OUI
  |            |
  v            v
fin       progression - 10
                |
                v
         recompenses + 1
```

Après 10 achats payants, une récompense est donc ajoutée au compte du client.

La récompense n'est pas utilisée automatiquement.

Par exemple :

```text
Avant le 10e achat :
Progression = 9
Récompenses = 0

10e achat PAYANT :
Progression = 0
Récompenses = 1
```

Cette récompense reste disponible jusqu'à ce que le client décide de l'utiliser.

Lorsqu'elle est utilisée :

```text
Récompenses = 1
       |
       v
Utiliser une récompense
       |
       v
Achat GRATUIT_FIDELITE
       |
       v
Récompenses = 0
```

L'utilisation d'une récompense ne fait pas progresser le compteur de fidélité.

---

## 7. Cartes prépayées

Une carte prépayée contient initialement 11 cafés.

L'application ne gère pas le paiement de la carte. Elle enregistre seulement son émission et son utilisation.

À sa création :

```text
cafes_restants = 11
active = True
```

À chaque utilisation :

```text
Utilisation de la carte
          |
          v
Création Achat PREPAYE
          |
          v
cafes_restants - 1
          |
          v
cafes_restants == 0 ?
       /       \
     NON       OUI
      |         |
      v         v
   Active    active = False
```

Une carte arrivée à zéro reste enregistrée afin de conserver son historique, mais elle ne peut plus être utilisée.

Un même client peut posséder plusieurs cartes au cours du temps.

---

## 8. Interaction entre fidélité et carte prépayée

Nous avons choisi de ne pas faire progresser le programme de fidélité lorsqu'un café est consommé avec une carte prépayée.

Les trois opérations ont donc des comportements distincts :

```text
PAYANT
  |
  +--> crée un Achat
  +--> progression fidélité + 1


GRATUIT_FIDELITE
  |
  +--> crée un Achat
  +--> récompenses - 1
  +--> progression inchangée


PREPAYE
  |
  +--> crée un Achat
  +--> cafés restants sur la carte - 1
  +--> progression fidélité inchangée
```

Cette décision évite qu'une même consommation bénéficie à la fois du mécanisme prépayé et du mécanisme de fidélité.

---

## 9. Organisation de la logique métier

La logique métier n'est pas placée directement dans les vues Django.

Elle est principalement regroupée dans `services.py`.

L'architecture utilisée est :

```text
Utilisateur
    |
    v
Template HTML
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

Les vues sont principalement responsables de :

* recevoir les requêtes HTTP ;
* récupérer les informations envoyées par les formulaires ;
* appeler les services appropriés ;
* préparer les données pour les templates ;
* rediriger l'utilisateur ;
* afficher les messages de succès ou d'erreur.

Les services sont responsables des règles métier telles que :

```text
enregistrer_achat_payant()
utiliser_recompense()
emettre_carte_prepayee()
utiliser_carte_prepayee()
```

---

## 10. Principes de conception appliqués

### Encapsuler ce qui varie

Les règles de fidélité et de cartes prépayées sont regroupées dans `services.py`.

Ces règles sont susceptibles d'évoluer davantage que l'affichage des pages.

Par exemple, si le programme passe plus tard de :

```text

10 cafés → 1 récompense
```

à une autre règle, la modification pourra principalement être effectuée dans la couche de services.

### Préférer la composition à l'héritage

Nous n'avons pas créé des classes telles que :

```text
ClientFidele
ClientAvecCarte
ClientAvecRecompense
```

Un `Client` est plutôt associé à différents objets :

```text
Client
  |
  +-- Fidelite
  |
  +-- Achat
  |
  +-- CartePrepayee
```

Cette approche utilise la composition et les relations entre objets plutôt qu'une hiérarchie d'héritage inutile.

### Single Responsibility Principle

Les principales responsabilités sont séparées :

```text
Client
→ informations du client

Fidelite
→ état de la fidélité

Achat
→ historique des cafés enregistrés

CartePrepayee
→ état d'une carte

views.py
→ interaction HTTP

services.py
→ règles métier
```

Cette séparation limite le nombre de raisons pour lesquelles chaque partie du système devrait être modifiée.

### Open/Closed Principle

La séparation entre les différents types d'achats et les services facilite l'ajout futur de nouvelles règles sans devoir réécrire entièrement les fonctionnalités existantes.

L'architecture cherche donc à préparer l'extension du système sans anticiper inutilement toutes les fonctionnalités des prochains devoirs.

### Autres principes SOLID

Les principes de substitution de Liskov, de ségrégation des interfaces et d'inversion des dépendances ne sont pas fortement sollicités dans cette première version.

Nous avons choisi de ne pas introduire artificiellement des interfaces ou des hiérarchies de classes uniquement pour démontrer ces principes.

Ils pourront devenir plus pertinents lors de l'évolution du système.

---

## 11. Décisions concernant les zones grises

### Fidélité et prépayé : un ou deux mécanismes ?

**Décision : deux mécanismes distincts.**

La fidélité représente une récompense acquise grâce aux achats payants réguliers, tandis que la carte prépayée représente un ensemble de cafés déjà acquis à l'avance.

Cette séparation rend leurs règles indépendantes et facilite leur évolution.

### Café gratuit automatique ou récompense stockée ?

**Décision : récompense stockée.**

Après 10 achats payants, le système ajoute une récompense disponible au client.

Le café gratuit n'est donc pas automatiquement consommé au prochain passage.

Cette approche sépare :

```text
gagner une récompense
```

de :

```text
utiliser une récompense
```

Elle permettra également plus facilement d'ajouter ultérieurement des règles comme une date d'expiration ou différents types de récompenses.

### Comment identifier un client ?

**Décision : numéro de téléphone unique.**

Le nom est conservé comme information descriptive et le courriel est facultatif.

Le téléphone permet une recherche simple au comptoir tout en évitant l'ambiguïté de plusieurs clients portant le même nom.

---

## 12. Évolutivité

Cette première version cherche à satisfaire les besoins actuels sans prévoir prématurément toutes les fonctionnalités futures.

Les choix de conception ont toutefois été faits afin que le produit puisse évoluer progressivement.

La séparation entre :

```text
Client
Fidelite
Achat
CartePrepayee
services.py
views.py
```

permet de modifier les règles métier et d'ajouter de nouvelles fonctionnalités sans concentrer toute la logique dans une seule classe ou une seule vue.

# Conception — Évolution vers la version 2

## 1. Objectif

La version 2 de Café Fidélité étend la version 1 sans remplacer ses fonctionnalités existantes.

Elle introduit six nouvelles capacités :

1. Annulation des transactions.
2. Rapports statistiques.
3. Configuration des règles de fidélité.
4. Effacement des renseignements personnels.
5. Fusion des fiches clients.
6. Authentification et permissions des employés.

L'application continue de fonctionner localement avec Django et SQLite. Aucun paiement n'est traité.

## 2. Architecture générale

L'application conserve une architecture séparant les responsabilités :

- **Modèles Django** : représentation des données persistantes.
- **Services métier** : règles de fidélité, annulations, fusions et statistiques.
- **Vues Django** : réception des requêtes et contrôle d'accès.
- **Formulaires Django** : validation des données saisies.
- **Templates** : présentation des interfaces.
- **Tests automatisés** : vérification des règles d'affaires.

Les opérations modifiant plusieurs enregistrements seront exécutées de manière atomique.

## 3. Modèles de données

### 3.1 Client

Le modèle `Client` conserve ses informations existantes :

- `id`
- `nom`
- `telephone`
- `courriel`
- `date_creation`

De nouveaux champs permettront de distinguer les clients actifs, anonymisés et fusionnés.

Les renseignements personnels seront effacés lors d'une anonymisation. Une fiche anonymisée ne pourra plus être utilisée pour effectuer des opérations.

### 3.2 Fidelite

Le modèle `Fidelite` conserve :

- `client`
- `progression`
- `recompenses`

Un mécanisme supplémentaire permettra de représenter les dettes d'étampes résultant de certaines annulations.

Les soldes existants de la v1 seront conservés pendant la migration.

### 3.3 Achat

Le modèle `Achat` conserve :

- `client`
- `type_achat`
- `carte_prepayee`
- `date_achat`

Il sera enrichi afin de conserver :

- L'employé responsable de l'achat.
- L'état d'annulation.
- Les informations nécessaires pour retrouver la règle de fidélité applicable.
- Les données nécessaires aux corrections des soldes.

Les achats provenant de la v1 ne seront pas attribués artificiellement à un employé.

### 3.4 CartePrepayee

Le modèle `CartePrepayee` conserve :

- `client`
- `cafes_restants`
- `date_emission`
- `active`

La v2 permettra de distinguer une carte épuisée, une carte annulée et une carte clôturée après anonymisation.

Chaque carte conservera son propre solde, y compris après une fusion de clients.

### 3.5 RegleFidelite

Ce nouveau modèle permettra de configurer le programme de fidélité.

Champs prévus :

- `id`
- `seuil`
- `date_entree_vigueur`
- `date_creation`
- `cree_par`

Les anciennes règles seront conservées pour interpréter les transactions historiques.

### 3.6 Annulation

Ce nouveau modèle conservera la trace des annulations.

Champs prévus :

- `id`
- `achat` ou référence à l'opération annulée
- `gerant`
- `motif`
- `date_annulation`

La référence devra également permettre l'annulation de l'émission d'une carte prépayée.

Une opération ne pourra être annulée qu'une seule fois.

### 3.7 EmissionCarte

Ce modèle représentera explicitement la vente ou l'émission d'une carte prépayée.

Champs prévus :

- `id`
- `carte`
- `employe`
- `date_emission`

Il permettra de produire les rapports de cartes vendues et de tracer leurs annulations.

Pour les cartes créées en v1, la migration reconstruira les enregistrements nécessaires à partir des données disponibles, sans inventer l'identité de l'employé.

### 3.8 FusionClient

Ce modèle enregistrera les opérations de fusion.

Champs prévus :

- `id`
- `client_principal`
- `client_secondaire`
- `gerant`
- `date_fusion`

Les références historiques devront être conçues pour rester compatibles avec l'anonymisation ultérieure des clients.

### 3.9 Employés

Nous utiliserons le modèle utilisateur intégré de Django.

Deux groupes seront configurés :

- `barista`
- `gerant`

Les permissions seront vérifiées côté serveur.

Les gérants pourront effectuer les opérations quotidiennes ainsi que les opérations sensibles.

## 4. Relations principales

- Un client possède un compte de fidélité au maximum.
- Un client peut posséder plusieurs achats.
- Un client peut posséder plusieurs cartes prépayées.
- Une carte prépayée peut être associée à plusieurs achats de type `PREPAYE`.
- Une carte possède un enregistrement d'émission.
- Un achat peut être annulé au maximum une fois.
- Une émission de carte peut être annulée au maximum une fois.
- Un employé peut enregistrer plusieurs transactions.
- Un gérant peut effectuer plusieurs annulations et fusions.
- Plusieurs règles de fidélité peuvent se succéder dans le temps.

## 5. Stratégie compteurs et historique

Nous conservons une architecture hybride.

Les compteurs permettent une consultation rapide des soldes actuels.

L'historique permet de produire des rapports, de retracer les opérations et de comprendre les annulations.

Les compteurs existants de la v1 sont préservés comme état initial de référence.

À partir de la v2, les modifications des compteurs et de l'historique doivent rester synchronisées.

Cette décision est documentée dans l'ADR-0001.

## 6. Principales règles métier

### Annulations

Une annulation ne supprime pas physiquement l'opération.

Elle conserve le gérant responsable, la date et le motif.

Les soldes sont corrigés en fonction du type d'opération annulée.

### Rapports

Les rapports sont calculés sur une période choisie par le gérant.

Les transactions annulées sont exclues des totaux nets.

Une annulation tardive corrige les rapports de la période d'origine.

### Règles de fidélité

Le seuil est configurable avec une date d'entrée en vigueur.

Les étampes déjà accumulées et les récompenses acquises sont conservées.

### Anonymisation

Les renseignements personnels du client sont effacés.

Les statistiques historiques restent inchangées.

Les avantages non utilisés sont clôturés selon la procédure prévue.

### Fusion

Le gérant choisit la fiche principale.

Les étampes, les récompenses et les cartes sont conservées.

L'historique des achats reste exploitable.

### Permissions

Les baristas effectuent les opérations courantes.

Les gérants peuvent également effectuer les opérations sensibles.

Toutes les pages du comptoir nécessitent une authentification.

## 7. Stratégie de migration v1 vers v2

Les migrations de la version 1 ne seront ni supprimées ni modifiées.

De nouvelles migrations ajouteront les champs et les modèles nécessaires.

Les nouvelles relations vers les employés devront accepter une valeur nulle pour les anciennes opérations.

La migration devra notamment :

1. Conserver tous les clients existants.
2. Conserver les compteurs de fidélité.
3. Conserver les soldes des cartes prépayées.
4. Conserver les achats historiques.
5. Initialiser la règle de fidélité historique à 10 étampes.
6. Reconstituer les émissions de cartes existantes à partir des informations disponibles.
7. Ajouter les structures de traçabilité sans réinitialiser les soldes.

La commande `python manage.py balances` permettra de vérifier les soldes avant et après la migration.

Les résultats de cette vérification seront documentés dans `docs/migration.md`.

## 8. Qualité et tests

Les tests automatisés couvriront les règles de la v1 et les six nouvelles demandes.

Ils vérifieront notamment :

- La conservation des soldes après migration.
- L'attribution des récompenses.
- La consommation des cartes prépayées.
- Les annulations et leurs effets.
- Les rapports statistiques.
- Les changements de seuil.
- L'anonymisation des clients.
- La fusion des fiches.
- Les permissions des employés.

Les tests pourront être exécutés avec :

`python manage.py test`

## 9. Décisions architecturales

Les décisions sont documentées dans :

- `docs/adr/0001-compteurs-et-historique.md`
- `docs/adr/0002-annulation-transactions.md`
- `docs/adr/0003-rapports-statistiques.md`
- `docs/adr/0004-regles-fidelite-configurables.md`
- `docs/adr/0005-effacement-clients.md`
- `docs/adr/0006-fusion-clients.md`
- `docs/adr/0007-roles-et-permissions.md`

Ces documents précisent les choix retenus, les alternatives écartées et les conséquences de chaque décision.