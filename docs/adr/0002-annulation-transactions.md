# ADR-0002 — Annulation des transactions

- **Statut :** Accepté
- **Date :** 2026-10-18
- **Demande concernée :** Section 3.1 — Annuler une transaction

## Contexte

Dans la version 1 de Café Fidélité, chaque achat est enregistré dans le modèle `Achat`, tandis que les soldes de fidélité et les cartes prépayées sont mis à jour directement.

Aucun mécanisme ne permet actuellement d'annuler une opération.

La version 2 doit permettre à un gérant d'annuler un achat payant, un café gratuit, une utilisation de carte prépayée ou la vente d'une carte.

L'annulation doit corriger les soldes sans effacer l'historique. Elle doit également conserver l'identité de la personne ayant effectué l'annulation ainsi que sa date.

## Décision

Nous allons mettre en place un mécanisme d'annulation logique plutôt qu'une suppression physique des transactions.

Chaque transaction annulable conservera son état d'annulation. Une annulation sera enregistrée séparément avec :

- La transaction concernée.
- Le gérant responsable.
- La date et l'heure.
- Le motif de l'annulation.

Une transaction ne pourra être annulée qu'une seule fois.

Toutes les modifications de soldes et les écritures d'historique seront réalisées dans une transaction atomique Django.

### Annulation d'un achat payant

L'effet de l'achat sur la fidélité sera inversé.

Si une récompense issue de cet achat est encore disponible, elle pourra être retirée et la progression recalculée.

Si la récompense a déjà été consommée, nous conserverons le café gratuit dans l'historique et enregistrerons une dette d'étampe. Cette dette sera compensée par les prochains achats payants.

La correction tiendra compte du seuil de fidélité applicable à l'achat d'origine.

### Annulation d'un café gratuit

La récompense utilisée sera restituée au client.

Le café initialement servi restera visible dans l'historique, avec son état annulé.

### Annulation d'un café prépayé

Un café sera restitué sur la carte prépayée concernée.

Si la carte était devenue inactive parce que son solde était à zéro, elle sera réactivée.

### Annulation de la vente d'une carte prépayée

La vente d'une carte pourra être annulée uniquement si aucun café n'a été utilisé et qu'aucune autre opération n'empêche de rétablir son état initial.

La carte sera invalidée, mais l'opération restera dans l'historique.

### Limite temporelle

Nous autorisons l'annulation d'une transaction ancienne sans limite de date.

Les règles applicables à l'opération d'origine seront conservées afin d'éviter de recalculer incorrectement les avantages après un changement de politique de fidélité.

### Permissions

Seul un utilisateur possédant le rôle de gérant pourra annuler une transaction.

Le motif de l'annulation sera obligatoire.

Un barista devra demander l'intervention d'un gérant, même lorsqu'il vient de commettre l'erreur.

## Options écartées

### Supprimer définitivement la transaction

Cette solution est simple, mais elle fait disparaître la preuve de l'opération et empêche de savoir qui l'a annulée.

### Modifier uniquement les compteurs

Cette approche corrige les soldes visibles, mais ne garantit pas la cohérence avec les rapports et l'historique.

### Autoriser les baristas à annuler leurs propres transactions

Cette possibilité faciliterait la correction immédiate des erreurs.

Nous l'écartons afin de conserver une séparation claire des responsabilités entre barista et gérant.

### Interdire toutes les annulations anciennes

Cette règle simplifierait le système, mais empêcherait de corriger certaines erreurs découvertes tardivement.

## Conséquences

### Avantages

- Les opérations annulées restent traçables.
- Les soldes peuvent être corrigés sans supprimer les transactions.
- Chaque annulation est attribuée à un gérant.
- Les rapports peuvent distinguer les transactions actives et annulées.
- Les opérations anciennes restent interprétables malgré les changements de règles.

### Inconvénients

- La logique d'annulation est plus complexe que la suppression d'un achat.
- Les récompenses déjà consommées nécessitent une gestion particulière.
- Il faut conserver les règles historiques de fidélité.
- Les cartes prépayées nécessitent des contrôles avant leur annulation.
- Des tests automatisés doivent vérifier les cas limites.

## Vérification

Nous développerons notamment les tests suivants :

1. Un gérant peut annuler un achat payant.
2. Un barista ne peut pas annuler une transaction.
3. Une annulation restitue correctement une récompense disponible.
4. Une récompense déjà consommée entraîne une dette d'étampe.
5. Une annulation de café prépayé restitue un café.
6. Une carte épuisée est réactivée après restitution.
7. Une carte déjà utilisée ne peut pas voir sa vente annulée.
8. Une transaction ne peut pas être annulée deux fois.
9. Une annulation conserve le gérant, la date et le motif.
10. Une erreur pendant l'annulation ne laisse aucune modification partielle en base de données.