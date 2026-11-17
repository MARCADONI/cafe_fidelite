# ADR-0014 — Gestion des fichiers statiques en production

## Statut

Accepté

## Contexte

Dans la version 2 de Café Fidélité, l'application fonctionne principalement dans un environnement local de développement.

La version 3 introduit une architecture conteneurisée utilisant PostgreSQL, Gunicorn et un proxy inverse.

L'application doit fonctionner avec `DEBUG = False`, tout en permettant l'affichage correct des fichiers statiques, notamment les feuilles de style, les fichiers JavaScript et les ressources de l'administration Django.

Il est donc nécessaire de choisir une stratégie de distribution des fichiers statiques adaptée à la production.

## Options envisagées

### Option 1 — Servir les fichiers statiques avec Nginx

Nginx distribue directement les fichiers statiques collectés par Django.

Cette solution offre de bonnes performances, mais nécessite de rendre les fichiers collectés accessibles au conteneur Nginx, notamment à l'aide d'un volume partagé ou d'une image adaptée.

Elle augmente la complexité de la configuration des conteneurs.

### Option 2 — Utiliser WhiteNoise

WhiteNoise permet de servir les fichiers statiques à partir de l'application Django dans un environnement de production.

Les fichiers sont collectés à l'aide de la commande `collectstatic` et distribués par le middleware WhiteNoise.

Cette solution permet également d'utiliser la compression et la gestion du cache.

Elle est particulièrement adaptée à une application de taille modérée et limite le nombre de composants nécessaires.

### Option 3 — Utiliser un conteneur dédié aux fichiers statiques

Un conteneur supplémentaire serait responsable de la distribution des fichiers statiques.

Cette solution permet une séparation complète des responsabilités, mais introduit une complexité disproportionnée par rapport aux besoins actuels du projet.

## Décision

Nous retenons l'option 2.

WhiteNoise sera utilisé pour distribuer les fichiers statiques de Café Fidélité en production.

Nginx conservera son rôle de proxy inverse et transmettra les requêtes HTTP au serveur Gunicorn, y compris les requêtes concernant les fichiers statiques.

WhiteNoise interceptera les requêtes destinées aux fichiers statiques dans la pile middleware Django.

La configuration de production utilisera notamment :

- `DEBUG = False`.
- Une valeur définie pour `STATIC_URL`.
- Un répertoire `STATIC_ROOT` destiné aux fichiers collectés.
- Le middleware WhiteNoise.
- Un mécanisme de stockage permettant la compression et le versionnement des fichiers statiques.

La commande `python manage.py collectstatic --noinput` sera exécutée lors de la construction de l'image Docker, avant son utilisation en production.

Les fichiers collectés seront intégrés à l'image finale de l'application.

La collecte des fichiers statiques ne devra pas nécessiter de connexion à la base de données ni de secrets de production pendant la construction de l'image.

Aucun volume partagé entre Nginx et Django ne sera nécessaire pour les fichiers statiques.

## Séparation des environnements

La configuration locale de développement pourra conserver le fonctionnement habituel de Django avec le rechargement automatique et `DEBUG = True`.

La configuration de production sera clairement séparée et utilisera WhiteNoise avec Gunicorn.

Le fonctionnement des fichiers statiques en production ne devra pas dépendre de la configuration locale de développement.

## Périmètre

WhiteNoise sera utilisé uniquement pour les fichiers statiques de l'application.

Il ne sera pas utilisé pour distribuer des fichiers téléversés dynamiquement par les utilisateurs.

Si une fonctionnalité de téléversement est introduite ultérieurement, une stratégie de stockage distincte devra être définie.

## Conséquences positives

- Fonctionnement des fichiers statiques avec `DEBUG = False`.
- Affichage correct des ressources de l'administration Django.
- Réutilisation d'une dépendance déjà présente dans le projet.
- Réduction de la complexité de la configuration Docker.
- Absence de volume partagé pour les fichiers statiques.
- Possibilité de compresser et de mettre en cache les ressources.
- Préparation du futur déploiement sur un serveur distant.

## Conséquences négatives

- Les requêtes statiques passent par le serveur d'application.
- L'image Docker doit être reconstruite lorsque les fichiers statiques sont modifiés.
- La configuration de WhiteNoise doit être vérifiée lors des mises à jour.
- Une application présentant un trafic important pourrait nécessiter une autre stratégie de distribution des ressources.

## Tests prévus

- Vérifier l'affichage des feuilles de style de l'application.
- Vérifier l'affichage des fichiers JavaScript.
- Vérifier l'affichage correct de l'administration Django.
- Vérifier l'accès aux fichiers statiques avec `DEBUG = False`.
- Vérifier le fonctionnement des ressources après une reconstruction de l'image Docker.
- Vérifier que les fichiers statiques restent accessibles après un redémarrage des conteneurs.
- Vérifier qu'une ressource inexistante retourne une erreur 404 normale.

## Références

- ADR-0013 — Exécution des migrations Django en production.
- Documentation Django relative aux fichiers statiques.
- Documentation WhiteNoise.