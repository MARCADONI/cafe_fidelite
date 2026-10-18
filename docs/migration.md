# Migration de Café Fidélité — v1 vers v2

## Objectif

Mettre à jour une base de données existante de la version 1 vers la version 2 sans perdre les clients, les achats, les étampes, les récompenses ni les soldes des cartes prépayées.

## Stratégie

- Conserver toutes les migrations de la v1.
- Ajouter de nouvelles migrations Django.
- Conserver les soldes existants sans les recalculer.
- Initialiser une règle historique de fidélité à 10 étampes.
- Reconstituer une émission pour chaque carte prépayée existante.
- Laisser l'employé responsable vide lorsque l'information n'existait pas dans la v1.

## Vérification

Avant migration :

`python manage.py balances`

Après migration :

`python manage.py balances`

Les résultats doivent être comparés pour chaque client et chaque carte.

## Résultats réels

À compléter après exécution des migrations :

- Version et tag v1 utilisés :
- Nombre de clients avant :
- Nombre de clients après :
- Nombre d'achats avant :
- Nombre d'achats après :
- Nombre de cartes avant :
- Nombre de cartes après :
- Nombre d'émissions reconstruites :
- Soldes identiques : oui / non
- Problèmes rencontrés :
- Corrections apportées :

## Conclusion

La migration sera considérée comme validée lorsque les données et les soldes de la v1 seront conservés et que les nouveaux modèles de la v2 seront opérationnels.