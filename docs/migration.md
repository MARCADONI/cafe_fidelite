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

## Historique des migrations Django

L'évolution de Café Fidélité repose sur les migrations Django de l'application `loyalty`.

Les migrations initiales de la version 1 ont été conservées. Les évolutions successives ont permis d'intégrer les nouvelles fonctionnalités de la version 2.

### Migrations appliquées

| Migration | Description |
|---|---|
| `0001_initial` | Création des structures initiales |
| `0002_fidelite` | Introduction du modèle de fidélité |
| `0003_carteprepayee` | Introduction des cartes prépayées |
| `0004_achat` | Introduction de l'historique des achats |
| `0005_client_date_anonymisation_client_est_anonymise_and_more` | Évolution des données des clients et autres modèles |
| `0006_achat_employe_achat_seuil_fidelite_applique_and_more` | Évolution du suivi des achats et de leurs règles |
| `0007_initialiser_donnees_v2` | Initialisation des données nécessaires à la version 2 |
| `0008_achat_dette_remboursee_achat_etampes_ajoutees_and_more` | Ajout d'informations nécessaires au suivi des effets des achats |
| `0009_achat_effets_traces` | Évolution de la traçabilité des effets des achats |
| `0010_mouvementfidelite` | Introduction de l'historique des mouvements de fidélité |
| `0011_journalaudit` | Introduction du journal d'audit |

Ces onze migrations ont été signalées comme appliquées lors de la dernière vérification de l'environnement local.

### Vérification de l'état des migrations

La commande suivante permet d'afficher les migrations :

```powershell
.\.venv\Scripts\python.exe manage.py showmigrations loyalty
```

Une migration précédée de `[X]` est considérée comme appliquée dans la base de données utilisée par Django.

Pour vérifier que les modèles ne nécessitent pas de nouvelles migrations :

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Pour vérifier l'absence de migrations en attente :

```powershell
.\.venv\Scripts\python.exe manage.py migrate --check
```

### Conservation des données historiques

La stratégie de migration vise à préserver les données de la version 1, notamment :

- Les fiches clients.
- L'historique des achats.
- Les compteurs de progression et les récompenses.
- Les soldes des cartes prépayées.

La validation effective de cette conservation nécessite une comparaison des données avant et après migration.

Les résultats chiffrés doivent être consignés dans la section « Résultats réels » du présent document.

### Précautions et retour arrière

Avant une migration sur une base contenant des données importantes, une sauvegarde doit être effectuée.

Les migrations qui transforment ou anonymisent des données peuvent nécessiter des procédures particulières de restauration.

La réversibilité d'une migration doit être vérifiée avant toute tentative de retour arrière.

## Conclusion

La migration sera considérée comme validée lorsque les données et les soldes de la v1 seront conservés et que les nouveaux modèles de la v2 seront opérationnels.   