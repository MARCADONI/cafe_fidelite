# ADR-0011 — Gestion globale des clients, fusion et anonymisation

## Statut

Accepté

## Contexte

Dans la version 2 de Café Fidélité, les clients sont identifiés indépendamment des employés et possèdent un compte de fidélité unique.

Les gérants peuvent fusionner les fiches de clients en double et anonymiser les renseignements personnels d'un client.

L'introduction de plusieurs succursales soulève une difficulté supplémentaire : un même client peut posséder des transactions et des avantages provenant de plusieurs cafés.

Une fusion ou une anonymisation réalisée dans une succursale peut donc avoir des conséquences sur l'ensemble du réseau.

Il est nécessaire de définir la portée des fiches clients et les permissions associées aux opérations sensibles.

## Options envisagées

### Option 1 — Des clients propres à chaque succursale

Chaque succursale possède ses propres fiches clients.

Cette solution facilite l'administration locale, mais entraîne une duplication des informations et complique le partage des avantages entre les cafés.

Elle ne correspond pas au fonctionnement d'un programme de fidélité commun.

### Option 2 — Des clients globaux administrés par tous les gérants

Chaque client possède une fiche unique accessible dans toutes les succursales.

Les gérants peuvent fusionner ou anonymiser les clients indépendamment de leurs transactions dans les autres cafés.

Cette solution facilite les opérations administratives, mais permet à un gérant de modifier des données ayant un impact sur les autres succursales.

### Option 3 — Des clients globaux avec des opérations sensibles réservées au propriétaire

Les clients possèdent une fiche unique pour l'ensemble du réseau.

Les baristas et les gérants peuvent effectuer les opérations courantes, mais les opérations sensibles ayant une portée globale sont réservées au propriétaire.

Cette solution protège les données communes tout en conservant la simplicité du programme de fidélité.

## Décision

Nous retenons l'option 3.

### Identité des clients

Le modèle `Client` conserve une portée globale.

Le numéro de téléphone reste le principal moyen d'identification du client et conserve sa contrainte d'unicité à l'échelle du réseau.

Un client inscrit dans une succursale peut être retrouvé et utiliser ses avantages dans une autre succursale sans créer une nouvelle fiche.

Aucune relation obligatoire vers une succursale ne sera ajoutée au modèle `Client`.

### Consultation des informations

Les employés autorisés peuvent consulter les informations nécessaires aux opérations courantes, notamment :

- L'identité du client.
- Le solde des étampes.
- Les récompenses disponibles.
- Les cartes prépayées et leurs soldes.

Les historiques transactionnels sont filtrés selon les succursales autorisées.

Le propriétaire peut consulter l'historique complet du client dans l'ensemble du réseau.

### Fusion des clients

La fusion des fiches clients est réservée au propriétaire.

Les mécanismes de fusion introduits dans la version 2 sont conservés.

Lors d'une fusion :

- Une fiche principale est sélectionnée.
- Les avantages des deux clients sont regroupés conformément aux règles métier existantes.
- Les cartes prépayées conservent leurs soldes.
- Les transactions historiques conservent leur succursale d'origine.
- La fiche secondaire est identifiée comme fusionnée.
- L'opération est enregistrée dans le journal d'audit.

La fusion doit être exécutée de manière atomique afin de garantir la cohérence des données.

### Anonymisation des clients

L'anonymisation est réservée au propriétaire.

Elle s'applique à la fiche globale du client et non uniquement aux données d'une succursale.

Les règles définies dans la version 2 sont conservées :

- Effacement des renseignements personnels.
- Clôture des avantages non utilisés selon les règles existantes.
- Conservation des transactions historiques.
- Interdiction de nouvelles opérations sur une fiche anonymisée.
- Enregistrement de l'action dans le journal d'audit.

Les statistiques historiques des succursales ne doivent pas être modifiées par l'anonymisation.

### Contrôle des permissions

Les permissions de fusion et d'anonymisation sont vérifiées dans les vues Django et dans les services métier.

Un gérant ne peut pas contourner ces restrictions en accédant directement aux URL ou en modifiant les identifiants transmis au serveur.

Les opérations de fusion et d'anonymisation sont considérées comme des opérations globales dans le journal d'audit. Elles ne sont pas attribuées artificiellement à une seule succursale.

## Conséquences positives

- Une seule fiche client est nécessaire pour l'ensemble du réseau.
- Les avantages sont accessibles dans toutes les succursales.
- Les doublons entre succursales sont limités.
- Les opérations sensibles ne peuvent pas être effectuées indépendamment par les gérants.
- Les historiques et les statistiques des succursales sont préservés.
- Les mécanismes métier de la version 2 peuvent être réutilisés.

## Conséquences négatives

- Les gérants perdent leur autonomie concernant la fusion et l'anonymisation.
- Le propriétaire doit intervenir pour traiter les demandes correspondantes.
- Les services métier et les permissions existantes doivent être adaptés.
- Les opérations globales nécessitent une attention particulière concernant la concurrence et la cohérence des données.

## Tests prévus

- Vérifier qu'un client créé dans une succursale peut être retrouvé dans une autre.
- Vérifier l'unicité du numéro de téléphone dans l'ensemble du réseau.
- Vérifier qu'un gérant ne peut pas fusionner des clients.
- Vérifier qu'un gérant ne peut pas anonymiser un client.
- Vérifier qu'un propriétaire peut fusionner des clients possédant des transactions dans plusieurs succursales.
- Vérifier la conservation des soldes et des succursales d'origine après une fusion.
- Vérifier qu'une anonymisation conserve les statistiques historiques de chaque succursale.
- Vérifier qu'un client anonymisé ou fusionné ne peut plus effectuer de nouvelles transactions sur sa fiche inactive.
- Vérifier que les opérations globales sont enregistrées dans le journal d'audit.

## Références

- ADR-0005 — Effacement des clients.
- ADR-0006 — Fusion des clients.
- ADR-0008 — Gestion des succursales et affectation des employés.
- ADR-0009 — Programme de fidélité partagé entre les succursales.
- ADR-0010 — Rôles et permissions par succursale.

Cet ADR conserve les mécanismes métier de fusion et d'anonymisation de la version 2, mais modifie leur périmètre d'autorisation.