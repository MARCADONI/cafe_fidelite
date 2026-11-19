Migration de Café Fidélité V2 vers V3
1. Objectif
Cette procédure permet de migrer une installation existante de Café Fidélité V2 utilisant SQLite vers la version V3 utilisant PostgreSQL dans des conteneurs Docker.

La migration doit garantir :
- La conservation des clients existants.
- La conservation des étampes, récompenses et dettes d'étampes.
- La conservation des cartes prépayées et de leurs soldes.
- La conservation des transactions, annulations et journaux d'audit.
- La conservation des comptes utilisateurs.
- L'attribution des transactions historiques à la première succursale.
2. Stratégie de migration
La migration est réalisée en deux étapes distinctes :
1. Migration du schéma SQLite de la V2 vers la V3.
2. Transfert des données SQLite vers PostgreSQL.
Cette approche permet de séparer les modifications du modèle de données du changement de moteur de base de données.

Les migrations Django précédemment livrées sont conservées.
Nouvelles migrations
| Migration | Description |

|---|---|

| 0012 | Création du modèle Succursale |

| 0013 | Création du modèle AffectationSuccursale |

| 0014 | Ajout des succursales aux transactions |

| 0015 | Attribution des données historiques à CAFE01 |

| 0016 | Rendre obligatoire la succursale des transactions |

La première succursale est identifiée par le code CAFE01.
3. Prérequis
- Python 3.13.
- Environnement virtuel contenant les dépendances Django.
- Docker et Docker Compose.
- Une base SQLite fonctionnelle provenant de la V2.
- Le code source de la V3.
- Un fichier .env correctement configuré.
Les commandes suivantes sont présentées pour PowerShell.
4. Sauvegarde de la version V2
Avant de commencer, arrêter le serveur Django V2 et toute opération susceptible de modifier la base.

Depuis la version V2, créer un répertoire de sauvegarde en dehors du dépôt :
New-Item -ItemType Directory -Force ..\backup_v2
Sauvegarder la base SQLite :
Copy-Item db.sqlite3 ..\backup_v2\db_v2.sqlite3
Enregistrer les soldes avant migration :
python manage.py balances --settings=config.settings.local |
    Set-Content -Encoding utf8 ..\backup_v2\balances_avant.txt
Vérifier l'intégrité de la sauvegarde :
python -c "import sqlite3; c=sqlite3.connect('file:../backup_v2/db_v2.sqlite3?mode=ro', uri=True); print(c.execute('PRAGMA integrity_check').fetchall()); c.close()"
Le résultat attendu est :
[('ok',)]
La sauvegarde originale ne doit jamais être modifiée.
5. Préparation de la version V3
Récupérer la version V3 du projet après avoir sauvegardé la base V2.

Installer les dépendances conformément au README.

Créer un répertoire de travail :
New-Item -ItemType Directory -Force migration_data
Créer une copie de la sauvegarde :
Copy-Item ..\backup_v2\db_v2.sqlite3 migration_data\db_migration.sqlite3
Le répertoire migration_data/ doit être exclu de Git et de l'image Docker.
6. Configuration SQLite temporaire
Utiliser le fichier config/settings/migration.py :
from .local import *
from .base import BASE_DIR
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "migration_data" / "db_migration.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}
Cette configuration permet de travailler sur une copie indépendante de la base V2.

Vérifier le chemin utilisé :
python manage.py shell --settings=config.settings.migration -c "from django.db import connection; print(connection.settings_dict['NAME'])"
7. Migration du schéma SQLite
Appliquer les migrations Django :
python manage.py migrate --settings=config.settings.migration
Vérifier les soldes :
python manage.py balances --settings=config.settings.migration
Vérifier la succursale historique :
python manage.py balances --succursale CAFE01 --settings=config.settings.migration
Vérifier l'attribution des transactions :
python manage.py shell --settings=config.settings.migration -c "from cafe_fidelite.loyalty.models import Achat, EmissionCarte, Annulation; print({m.__name__: m.objects.exclude(succursale__code='CAFE01').count() for m in (Achat, EmissionCarte, Annulation)})"
Pour une base provenant exclusivement de la V2, les trois compteurs doivent être égaux à zéro.
8. Exportation des données
Exporter les données de la base SQLite migrée :
python manage.py dumpdata --settings=config.settings.migration --all --natural-foreign --exclude contenttypes --exclude auth.permission --exclude sessions --indent 2 --output migration_data/donnees_v3.json
Les permissions et les types de contenu sont régénérés par les migrations Django.

Les sessions existantes ne sont pas transférées. Les utilisateurs devront se reconnecter.

Le fichier JSON contient des données potentiellement sensibles et ne doit pas être ajouté au dépôt Git.
9. Préparation de PostgreSQL
Configurer le fichier .env conformément au README.

Construire les images et démarrer PostgreSQL :
docker compose build app
docker compose up -d --wait db
Créer une base PostgreSQL indépendante pour la migration :
docker compose exec db sh -c 'createdb -U "$POSTGRES_USER" cafe_fidelite_validation'
Cette base doit être nouvelle. Si elle existe déjà, vérifier son contenu avant de poursuivre.

Configurer temporairement DATABASE_URL dans .env pour utiliser cafe_fidelite_validation, en conservant les véritables identifiants PostgreSQL.

Appliquer les migrations :
docker compose run --rm --no-deps --entrypoint python app manage.py migrate --noinput
Vérifier la connexion :
docker compose run --rm --no-deps --entrypoint python app manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor); print(connection.settings_dict['NAME'])"
Résultat attendu :
postgresql
cafe_fidelite_validation
10. Importation des données
Ne pas initialiser les données de démonstration V3 avant l'importation.

Vérifier que la base de destination est bien la base de validation et qu'elle ne contient aucune donnée métier à conserver.

Les migrations initialisent certaines données de référence. Pour éviter les conflits avec les identifiants de la base source, vider uniquement une base de validation neuve, sans données métier à conserver. Arrêter d'abord les services applicatifs (docker compose stop app nginx). Vérifier le nom et le contenu de la destination :
docker compose run --rm --no-deps --entrypoint python app manage.py shell -c "from django.db import connection; from cafe_fidelite.loyalty.models import Client, Achat, EmissionCarte, Annulation; print(connection.settings_dict['NAME']); print({m.__name__: m.objects.count() for m in (Client, Achat, EmissionCarte, Annulation)})"
Si la base n'est pas cafe_fidelite_validation, ou si elle contient des données à conserver, arrêter ici. Si les données ont déjà été importées, passer directement à la vérification. Sinon, sauvegarder la destination avant toute opération destructive :
docker compose exec db sh -c 'pg_dump -U "$POSTGRES_USER" -d cafe_fidelite_validation -Fc -f /tmp/avant_import_validation.dump'
docker compose cp db:/tmp/avant_import_validation.dump migration_data/avant_import_validation.dump
Vider uniquement la base neuve vérifiée :
docker compose run --rm --no-deps --entrypoint python app manage.py flush --noinput
Importer ensuite les données :
docker compose run --rm --no-deps -v "${PWD}/migration_data:/migration_data:ro" --entrypoint python app manage.py loaddata /migration_data/donnees_v3.json
En cas d'erreur, arrêter la procédure et identifier la cause avant toute nouvelle tentative.
11. Vérification des soldes PostgreSQL
Démarrer les conteneurs :
docker compose up -d --force-recreate app nginx
Afficher les soldes du réseau :
docker compose exec app python manage.py balances
Afficher les soldes du premier café :
docker compose exec app python manage.py balances --succursale CAFE01
Enregistrer les résultats :
docker compose exec -T app python manage.py balances |
    Set-Content -Encoding utf8 migration_data/balances_apres.txt
Comparer les valeurs obtenues avec les soldes enregistrés avant la migration.

Vérifier également les transactions historiques :
docker compose exec app python manage.py shell -c "from cafe_fidelite.loyalty.models import Achat, EmissionCarte, Annulation; print({m.__name__: m.objects.exclude(succursale__code='CAFE01').count() for m in (Achat, EmissionCarte, Annulation)})"
12. Résultats de notre vérification
Soldes de fidélité
| Client | Étampes V2 | Étampes V3 SQLite | Récompenses V2 | Récompenses V3 SQLite |

|---|---:|---:|---:|---:|

| Client Test | 0 | 0 | 0 | 0 |

| Jean Tremblay | 1 | 1 | 0 | 0 |

| Marc Adoni | 1 | 1 | 1 | 1 |
Cartes prépayées
| Carte | Cafés restants V2 | Cafés restants V3 SQLite | État V3 SQLite |

|---|---:|---:|---|

| Carte 1 | 11 | 11 | Active |

| Carte 2 | 0 | 0 | Inactive |

| Carte 3 | 7 | 7 | Active |

| Carte 4 | 9 | 9 | Active |

Les soldes historiques observés sous SQLite V3 sont identiques aux soldes V2 enregistrés avant migration.
Validation PostgreSQL
| Vérification | Résultat |

|---|---|

| Nombre de clients | Validé : 3 dans chaque base |

| Conservation des étampes | À valider |

| Conservation des récompenses | À valider |

| Conservation des cartes | À valider |

| Attribution des transactions à CAFE01 | À valider |

| Persistance après redémarrage | À valider |

| Tests automatisés PostgreSQL | À valider |

Le 19 novembre 2026, la connexion PostgreSQL a été rétablie en synchronisant le mot de passe du rôle avec les variables d'environnement, sans supprimer le volume. Les compteurs suivants ont été observés :
Modèle	SQLite V3	PostgreSQL V3
Client	3	3
Achat	47	47
CartePrepayee	4	4
EmissionCarte	4	4
Annulation	5	5
Succursale	1	1


Les six compteurs sont identiques. La comparaison des soldes PostgreSQL et du contenu intégral reste à confirmer. Une sauvegarde PostgreSQL a été créée avant toute nouvelle manipulation.
Comparaison intégrale des exports
Exporter PostgreSQL avec les mêmes options que SQLite :
docker compose exec app python manage.py dumpdata --all --natural-foreign --exclude contenttypes --exclude auth.permission --exclude sessions --indent 2 --output /tmp/donnees_postgresql.json
docker compose cp app:/tmp/donnees_postgresql.json migration_data/donnees_postgresql.json
@'
import json
from pathlib import Path

def indexer(nom):
    objets = json.loads(Path(nom).read_text(encoding="utf-8-sig"))
    return {(o["model"], o["pk"]): o["fields"] for o in objets}

a = indexer("migration_data/donnees_v3.json")
b = indexer("migration_data/donnees_postgresql.json")
print("SQLite :", len(a), "PostgreSQL :", len(b))
print("Manquants :", len(a.keys() - b.keys()))
print("Supplementaires :", len(b.keys() - a.keys()))
print("Differents :", sum(a[k] != b[k] for k in a.keys() & b.keys()))
print("Exports identiques :", a == b)
'@ | python -
Les écarts éventuels doivent être analysés avant de conclure à une perte de données. Les exports contiennent des informations sensibles et restent hors Git.
13. Tests automatisés
La validation SQLite de la V3 a été effectuée le 18 novembre 2026.
Ran 94 tests in 7.968s
OK
Pour exécuter les tests sous PostgreSQL :
docker compose exec app python manage.py test cafe_fidelite.loyalty.tests --verbosity=2
La réussite des tests SQLite ne dispense pas de la validation sous PostgreSQL.
14. Vérification de la persistance
Après validation de l'importation :
docker compose down
docker compose up -d --wait
docker compose ps
Afficher de nouveau les soldes :
docker compose exec app python manage.py balances
Les résultats doivent être identiques à ceux obtenus avant le redémarrage.

Ne jamais utiliser docker compose down -v sur une installation contenant des données à conserver.
15. Retour arrière
En cas d'échec de la migration :
1. Arrêter l'application V3.
2. Conserver la base PostgreSQL pour analyser les erreurs.
3. Restaurer le code de la version V2.
4. Restaurer une copie de la sauvegarde SQLite originale.
5. Redémarrer l'application V2.
6. Vérifier les soldes avec la commande balances.
Le retour arrière suppose qu'aucune nouvelle transaction n'a été enregistrée dans la V3 après la migration.
16. Sécurité des données
Les éléments suivants ne doivent jamais être ajoutés au dépôt Git :
- Le fichier .env.
- Les bases SQLite.
- Les sauvegardes PostgreSQL.
- Les fichiers JSON d'exportation.
- Les fichiers contenant des renseignements personnels.
Le fichier .env.example contient uniquement des exemples de configuration.
17. Conclusion
La migration du schéma V2 vers V3 permet d'introduire la gestion multisite sans modifier les soldes historiques observés sous SQLite.

Le transfert définitif vers PostgreSQL sera considéré comme validé uniquement après comparaison des données, réussite des tests PostgreSQL et vérification de la persistance.