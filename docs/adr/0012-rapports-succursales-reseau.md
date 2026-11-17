# ADR-0012 — Rapports statistiques par succursale et réseau

## Statut

Accepté

## Contexte

Dans la version 2 de Café Fidélité, les rapports statistiques permettent aux gérants de consulter les activités du café sur une période donnée.

Les rapports sont calculés à partir des transactions enregistrées dans la base de données. Les transactions annulées sont exclues des totaux nets.

La version 3 introduit plusieurs succursales partageant un programme de fidélité commun.

Il devient nécessaire de produire des rapports propres à chaque succursale ainsi que des rapports consolidés pour l'ensemble du réseau.

Une difficulté supplémentaire concerne les récompenses obtenues grâce à des achats effectués dans une succursale, mais utilisées dans une autre.

## Options envisagées

### Option 1 — Attribuer les récompenses à la succursale d'origine

Le café gratuit est comptabilisé dans la succursale ayant contribué à l'obtention de la récompense.

Cette solution permettrait de rapprocher les achats des récompenses obtenues, mais elle devient complexe lorsque les étampes sont accumulées dans plusieurs succursales.

Elle ne représente pas nécessairement l'activité réelle de la succursale ayant servi le café.

### Option 2 — Répartir les récompenses entre les succursales

Le café gratuit est réparti proportionnellement entre les succursales ayant contribué à son obtention.

Cette solution permettrait une répartition théorique des récompenses, mais nécessite une traçabilité supplémentaire et complexifie les calculs statistiques.

### Option 3 — Attribuer chaque transaction à sa succursale de réalisation

Chaque transaction est comptabilisée dans la succursale où elle a été effectuée.

Les achats payants, les consommations de récompenses, les émissions de cartes et les consommations prépayées sont ainsi attribués à leur lieu de réalisation.

Cette solution représente directement l'activité de chaque succursale et simplifie les rapports.

## Décision

Nous retenons l'option 3.

Chaque transaction est comptabilisée dans la succursale à laquelle elle appartient.

Un café gratuit obtenu grâce à des étampes accumulées dans plusieurs succursales est comptabilisé dans la succursale où il est consommé.

Une carte prépayée est comptabilisée comme vendue dans sa succursale d'émission. Les consommations associées à cette carte sont comptabilisées dans les succursales où elles sont réalisées.

## Rapports par succursale

Les rapports de la version 2 sont conservés et adaptés afin de permettre un filtrage par succursale.

Les indicateurs existants comprennent notamment :

- Les achats payants.
- Les cafés gratuits consommés.
- Les cafés consommés à partir de cartes prépayées.
- Les cartes prépayées vendues.

Les indicateurs sont calculés sur une période sélectionnée.

Un gérant peut uniquement consulter les rapports de sa succursale.

## Rapports du réseau

Le propriétaire peut consulter :

- Les rapports d'une succursale particulière.
- Les rapports consolidés de l'ensemble du réseau.

Les rapports consolidés regroupent les transactions de toutes les succursales sur la période sélectionnée.

Chaque transaction est comptabilisée une seule fois.

Les indicateurs représentant des nombres de transactions peuvent être additionnés entre succursales. Les indicateurs non additifs, tels que le nombre de clients distincts, doivent être recalculés à l'échelle du réseau lorsqu'ils sont utilisés.

Les soldes de fidélité et des cartes prépayées restent globaux et ne doivent pas être additionnés plusieurs fois.

## Gestion des annulations

Les règles de la version 2 concernant les annulations sont conservées.

Une transaction annulée est exclue des totaux nets.

Une annulation est rattachée à la succursale de la transaction originale, conformément à l'ADR-0008.

Une annulation effectuée après la période de la transaction corrige les rapports de la période d'origine.

Les transactions annulées restent disponibles dans l'historique et les mécanismes d'audit.

## Contrôle des permissions

Le filtrage des rapports est effectué côté serveur.

Pour un gérant, la succursale autorisée est déterminée à partir de son affectation et non uniquement à partir des paramètres transmis dans la requête HTTP.

Toute demande concernant une succursale non autorisée ou l'ensemble du réseau est refusée.

Le propriétaire peut sélectionner librement une succursale ou consulter les résultats globaux.

Les restrictions restent applicables lors d'un accès direct à une URL.

## Conséquences positives

- Les rapports représentent l'activité réelle de chaque succursale.
- Les rapports existants peuvent être adaptés sans modifier les règles fondamentales de fidélité.
- Les récompenses partagées ne nécessitent pas de mécanisme complexe de répartition.
- Les transactions ne sont pas comptabilisées plusieurs fois.
- Le propriétaire dispose d'une vision locale et globale du réseau.
- Les gérants ne peuvent pas accéder aux statistiques des autres succursales.

## Conséquences négatives

- Les rapports ne représentent pas directement la contribution de chaque succursale à l'obtention d'une récompense.
- Une succursale peut servir des cafés gratuits générés par des achats effectués ailleurs.
- Les requêtes statistiques existantes doivent être adaptées.
- Les permissions et les filtres nécessitent des tests supplémentaires.

## Tests prévus

- Vérifier les rapports d'une succursale sur une période donnée.
- Vérifier les rapports consolidés du réseau.
- Vérifier qu'un gérant ne peut pas consulter les rapports d'une autre succursale.
- Vérifier qu'un gérant ne peut pas consulter les rapports globaux.
- Vérifier qu'un propriétaire peut consulter toutes les succursales.
- Vérifier qu'une récompense obtenue dans une succursale et consommée dans une autre est comptabilisée dans la succursale de consommation.
- Vérifier qu'une carte vendue dans une succursale et utilisée dans une autre apparaît correctement dans les rapports.
- Vérifier qu'une annulation corrige les statistiques de la succursale et de la période d'origine.
- Vérifier l'absence de double comptabilisation dans les rapports consolidés.

## Références

- ADR-0002 — Annulation des transactions.
- ADR-0003 — Rapports statistiques.
- ADR-0008 — Gestion des succursales et affectation des employés.
- ADR-0009 — Programme de fidélité partagé entre les succursales.
- ADR-0010 — Rôles et permissions par succursale.

Cet ADR étend les décisions relatives aux rapports statistiques de la version 2 à un environnement comportant plusieurs succursales.