# Rétrospective — Devoir 1

## 1. Analyse des six nouvelles demandes

### Annuler une transaction
La version 1 conserve les achats dans la table `Achat`, mais ne prévoit aucun mécanisme d'annulation. Les compteurs de fidélité et les soldes des cartes prépayées sont mis à jour directement. Il faudrait donc ajouter une logique permettant d'annuler une opération tout en conservant sa trace et en corrigeant les soldes.

### Produire des rapports
La version 1 enregistre les achats avec leur type et leur date. Elle possède donc une partie des données nécessaires aux rapports. Cependant, aucune interface ne permet actuellement de consulter des statistiques sur une période. Il faudra également décider comment traiter les transactions annulées.

### Modifier la règle de fidélité
Le seuil de 10 cafés est directement inscrit dans le code du service de fidélité. Un gérant ne peut pas le modifier depuis l'application. Il faudra rendre cette règle configurable et conserver les informations nécessaires pour comprendre les récompenses attribuées avant et après un changement.

### Effacer un client
La version 1 utilise une relation entre les clients et leurs achats. La suppression d'un client entraîne actuellement la suppression de ses achats associés, ce qui risque de modifier les statistiques historiques. Il faudra prévoir une stratégie d'anonymisation ou de conservation des transactions sans renseignements personnels.

### Fusionner deux fiches clients
La version 1 ne permet pas de fusionner deux clients. Leurs achats, leurs cartes prépayées et leurs soldes de fidélité sont associés à des fiches distinctes. Il faudra ajouter une opération permettant de regrouper ces informations sans perdre les avantages accumulés.

### Gérer les employés et les permissions
La version 1 possède une administration Django, mais les écrans du comptoir ne sont pas protégés par des rôles barista et gérant. Les achats ne conservent pas non plus l'identité de l'employé responsable. Il faudra ajouter une authentification et des autorisations adaptées.

## 2. Ce qui nous a surpris

Les nouvelles demandes montrent qu'un système de fidélité ne consiste pas seulement à incrémenter des compteurs. Il doit aussi permettre de retracer les opérations, corriger les erreurs, préserver les données et distinguer les responsabilités des employés.

La nécessité de conserver les données existantes pendant les migrations est particulièrement importante.

## 3. Une décision que nous prendrions autrement

Dans la version 1, nous avons choisi de conserver à la fois les achats et des compteurs représentant les soldes actuels. Cette approche simplifie l'affichage des informations d'un client, mais peut provoquer des incohérences si une transaction doit être annulée ou corrigée.

Avec le recul, nous aurions défini dès le départ une stratégie explicite de traçabilité et de synchronisation entre les transactions et les soldes.

Pour la version 2, nous allons réexaminer cette décision dans un ADR, en tenant compte des besoins d'annulation, de rapports et de migration.