# 💶 Finance Bot — faire fructifier 20€ (sans risque, en simulation)

Un bot finance **en paper-trading** (simulation, **zéro argent réel**) qui aide à
comprendre comment un petit capital peut évoluer avec des stratégies
d'investissement disciplinées.

> ⚠️ **Avertissement honnête.** Ceci est un outil **éducatif**. Il ne déplace
> aucun argent réel, ne se connecte à aucun compte bancaire ou broker, et ne
> garantit **aucun** gain. Les marchés sont risqués : un investissement peut
> perdre de la valeur. Tout bot qui *promet* de faire fructifier de l'argent
> automatiquement est généralement une arnaque. Ne risquez que ce que vous
> pouvez vous permettre de perdre, et renseignez-vous (ou consultez un conseiller).

## Pourquoi pas du « vrai » trading automatique ?

- Trader réellement demande vos identifiants broker → risque de sécurité.
- Un bot peut perdre vos 20€ (voire plus avec l'effet de levier).
- C'est réglementé selon les pays.

À la place, ce bot vous montre **concrètement et sans risque** comment 20€
pourraient évoluer selon différentes stratégies, avec de **vrais prix de marché**.

## Fonctionnalités

- 📈 **Paper-trading** : portefeuille simulé démarrant à 20€.
- 🌐 **Prix réels** (crypto via l'API publique CoinGecko, sans clé) + repli
  hors-ligne si pas de réseau.
- 🧠 **Stratégies** :
  - `buy-hold` : on achète une fois, on garde.
  - `dca` : *Dollar-Cost Averaging* — on investit un montant fixe à intervalle
    régulier (la stratégie la plus recommandée pour les débutants).
- 🧮 **Projection à intérêts composés** : visualisez l'effet du temps.
- 💾 **Portefeuille persistant** en JSON local.

## Utilisation

Aucune dépendance à installer (Python 3.9+, stdlib uniquement).

```bash
cd finance_bot

# Voir l'aide
python3 -m finance_bot --help

# Initialiser un portefeuille à 20€
python3 -m finance_bot init --cash 20

# Voir le prix actuel d'un actif (bitcoin, ethereum...)
python3 -m finance_bot price --asset bitcoin

# Acheter pour 10€ de bitcoin (simulation)
python3 -m finance_bot buy --asset bitcoin --eur 10

# Voir l'état du portefeuille (valorisé au prix du marché)
python3 -m finance_bot status

# Vendre 0.0001 BTC (simulation)
python3 -m finance_bot sell --asset bitcoin --units 0.0001

# Projeter la croissance de 20€ à 6% / an pendant 10 ans, +5€/mois
python3 -m finance_bot project --principal 20 --rate 6 --years 10 --monthly 5

# Backtest d'une stratégie DCA sur un historique de prix simulé
python3 -m finance_bot backtest --strategy dca --eur-per-step 5 --steps 12
```

## Tests

```bash
python3 -m unittest discover -s finance_bot -p "test_*.py" -v
```
</content>
</invoke>
