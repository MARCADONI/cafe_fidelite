# Rétrospective de Café Fidélité — Version 2

## 1. Bilan de la version 2

La version 2 de Café Fidélité a permis d'enrichir considérablement les fonctionnalités de la version initiale. Elle a notamment introduit les annulations de transactions, les rapports statistiques, les règles de fidélité configurables, la fusion des clients, l'anonymisation et la gestion des permissions.

La séparation entre les modèles, les services métier et les interfaces a facilité l'ajout de ces fonctionnalités. Les tests automatisés ont également permis de vérifier les règles métier et de limiter les régressions.

## 2. Ce que nous n'avions pas anticipé

Lors de la conception de la V2, nous avions supposé que l'application serait utilisée dans un seul café.

Nous n'avions pas anticipé l'ouverture d'une deuxième succursale, le partage des cartes prépayées entre plusieurs établissements ni la nécessité de limiter les permissions des gérants à leur propre café.

Nous avions également utilisé SQLite et le serveur de développement Django sans prévoir immédiatement un environnement de production reproductible.

## 3. L'hypothèse d'un seul café

L'hypothèse d'un seul café était présente à plusieurs endroits dans notre application :

- Les transactions ne contenaient aucune référence à une succursale.
- Les rapports statistiques portaient sur l'ensemble des transactions.
- Les permissions dépendaient uniquement du rôle de l'utilisateur.
- Les annulations ne vérifiaient pas l'établissement d'origine.
- La configuration supposait une utilisation locale.

L'ajout d'une succursale ne pouvait donc pas être réalisé uniquement en modifiant un modèle. Il nécessitait également des adaptations dans les services, les vues, les permissions et les rapports.

Cependant, les clients, les soldes de fidélité et les cartes prépayées étaient déjà représentés indépendamment des interfaces. Cette séparation constituait une base favorable à leur partage entre plusieurs cafés.

## 4. Les décisions que nous prendrions autrement

Avec le recul, nous accorderions davantage d'importance à la séparation entre les permissions liées aux rôles et celles liées au périmètre d'accès.

Nous distinguerions également plus clairement la configuration de développement de celle de production.

Cela ne signifie pas que toutes les fonctionnalités multisites auraient dû être développées dès la première version. Il aurait toutefois été avantageux de limiter davantage les hypothèses implicites concernant l'environnement d'exécution et le nombre d'établissements.

## 5. Conclusion

La version 2 constitue une base fonctionnelle et relativement bien structurée, mais certaines hypothèses limitent son évolution vers un réseau de cafés.

La version 3 représente donc une occasion d'améliorer l'architecture sans réécrire entièrement l'application, tout en préservant les fonctionnalités existantes et les données historiques.