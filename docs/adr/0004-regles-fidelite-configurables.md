# ADR-0004 — Configuration des règles de fidélité

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 3.3 — Changer la règle du café gratuit

## Contexte

Dans la version 1 de Café Fidélité, le seuil permettant d'obtenir un café gratuit est fixé à 10 achats payants directement dans le code Python.

Le gérant ne peut pas modifier ce seuil depuis l'application.

La version 2 doit permettre de définir une nouvelle règle avec une date d'entrée en vigueur, tout en préservant les étampes et les récompenses déjà acquises.

L'historique des achats et les rapports doivent rester cohérents lorsque plusieurs règles se succèdent.

## Décision

Nous allons rendre le seuil de fidélité configurable à l'aide d'un nouveau modèle Django nommé `RegleFidelite`.

Ce modèle contiendra notamment :

- `seuil` : nombre d'étampes nécessaires pour obtenir une récompense.
- `date_entree_vigueur` : date à partir de laquelle la règle s'applique.
- `date_creation` : date de création de la règle.
- `cree_par` : gérant ayant configuré la règle.

Une seule règle pourra entrer en vigueur à une date donnée.

Le système sélectionnera automatiquement la règle dont la date d'entrée en vigueur est la plus récente sans dépasser la date de l'achat.

### Conservation des anciennes étampes

Les étampes déjà accumulées seront conservées lorsque le seuil change.

Les achats futurs utiliseront le nouveau seuil pour déterminer si une récompense doit être attribuée.

Par exemple, un client possédant 8 étampes avant le changement de 10 à 12 conservera ses 8 étampes et devra effectuer 4 achats supplémentaires pour obtenir une récompense.

### Conservation des récompenses acquises

Une récompense attribuée avant le changement restera disponible.

Le passage à un seuil plus élevé ne supprimera pas les cafés gratuits déjà gagnés.

### Historique des règles

Les anciennes règles seront conservées dans la base de données.

Les transactions de fidélité enregistreront les informations nécessaires pour retrouver la règle qui leur était applicable.

Une règle ayant déjà pris effet ne pourra pas être modifiée ou supprimée. Une nouvelle règle devra être créée pour effectuer un changement ultérieur.

### Modification par le gérant

Seul un gérant pourra créer une nouvelle règle.

Le formulaire permettra de saisir le seuil et la date d'entrée en vigueur.

La nouvelle règle ne nécessitera aucune modification du code Python.

### Date d'entrée en vigueur

Les changements de seuil seront planifiés pour une date future.

Nous n'autoriserons pas les changements rétroactifs afin d'éviter de recalculer les récompenses déjà attribuées.

La date sera interprétée selon le fuseau horaire configuré pour l'application.

### Cohérence des transactions

Lorsqu'un achat payant est enregistré, le service de fidélité déterminera le seuil applicable et conservera cette information.

Les opérations de fidélité seront exécutées dans des transactions atomiques.

En cas d'annulation, le système utilisera les informations historiques de l'achat concerné et non simplement le seuil actuellement en vigueur.

## Options écartées

### Modifier directement la constante dans le code

Cette solution serait simple à programmer, mais elle obligerait à modifier et redémarrer l'application pour chaque changement.

Elle ne permettrait pas de conserver facilement l'historique des règles.

### Réinitialiser les étampes lors d'un changement

Cette approche simplifierait le calcul des nouveaux soldes.

Cependant, elle ferait perdre des avantages déjà accumulés par les clients.

### Appliquer rétroactivement les nouvelles règles

Cette solution permettrait de recalculer tout l'historique avec le nouveau seuil.

Nous l'écartons parce qu'elle pourrait modifier ou supprimer des récompenses déjà acquises.

### Conserver uniquement le seuil actuel

Cette solution éviterait de créer un historique des règles.

Cependant, elle empêcherait d'interpréter correctement les anciennes transactions après plusieurs changements.

## Conséquences

### Avantages

- Le gérant peut modifier la règle sans changer le code.
- Les étampes existantes sont préservées.
- Les récompenses déjà gagnées restent disponibles.
- Les anciennes règles restent consultables.
- Les transactions peuvent être interprétées selon leur date.

### Inconvénients

- Un nouveau modèle Django est nécessaire.
- Les services de fidélité doivent rechercher le seuil applicable.
- Les annulations doivent tenir compte des règles historiques.
- Les règles doivent être validées pour éviter les dates en double et les modifications rétroactives.

## Vérification

Des tests automatisés vérifieront que :

1. Le seuil initial est de 10 étampes.
2. Un gérant peut planifier une règle à 12 étampes.
3. Un barista ne peut pas modifier les règles.
4. Une règle future ne s'applique pas avant sa date d'entrée en vigueur.
5. Une règle devient applicable à la date prévue.
6. Les étampes déjà accumulées sont conservées.
7. Les récompenses déjà attribuées restent disponibles.
8. Les anciennes transactions conservent leur interprétation historique.
9. Deux règles ne peuvent pas avoir la même date d'entrée en vigueur.
10. Une règle déjà entrée en vigueur ne peut pas être modifiée.