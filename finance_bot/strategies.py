"""Stratégies d'investissement et backtest simple.

Les stratégies opèrent sur une série de prix (historique ou simulé) et
retournent le résultat d'un portefeuille en paper-trading.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class BacktestResult:
    strategy: str
    invested_eur: float       # total réellement investi
    final_value_eur: float    # valeur finale (positions + cash restant)
    units_held: float
    cash_left_eur: float
    roi_pct: float            # rendement sur l'investi

    def summary(self) -> str:
        sign = "+" if self.roi_pct >= 0 else ""
        return (
            f"Stratégie    : {self.strategy}\n"
            f"Investi      : {self.invested_eur:.2f}€\n"
            f"Valeur finale: {self.final_value_eur:.2f}€\n"
            f"Unités       : {self.units_held:.8f}\n"
            f"Cash restant : {self.cash_left_eur:.2f}€\n"
            f"Rendement    : {sign}{self.roi_pct:.2f}%"
        )


def buy_hold(prices: List[float], budget_eur: float) -> BacktestResult:
    """Investit tout le budget au premier prix, puis garde jusqu'à la fin."""
    if not prices:
        raise ValueError("La série de prix est vide.")
    if budget_eur <= 0:
        raise ValueError("Le budget doit être positif.")
    units = budget_eur / prices[0]
    final_value = units * prices[-1]
    roi = (final_value - budget_eur) / budget_eur * 100.0
    return BacktestResult("buy-hold", budget_eur, final_value, units, 0.0, roi)


def dca(prices: List[float], eur_per_step: float) -> BacktestResult:
    """Dollar-Cost Averaging : investit `eur_per_step` à chaque pas de prix.

    Stratégie classique pour lisser le risque de timing : on achète un peu
    régulièrement, quel que soit le prix.
    """
    if not prices:
        raise ValueError("La série de prix est vide.")
    if eur_per_step <= 0:
        raise ValueError("Le montant par pas doit être positif.")
    units = 0.0
    invested = 0.0
    for price in prices:
        if price <= 0:
            continue
        units += eur_per_step / price
        invested += eur_per_step
    final_value = units * prices[-1]
    roi = (final_value - invested) / invested * 100.0 if invested else 0.0
    return BacktestResult("dca", invested, final_value, units, 0.0, roi)


def synthetic_prices(start: float, steps: int, drift: float = 0.01,
                     volatility: float = 0.05, seed: int = 42) -> List[float]:
    """Génère une série de prix synthétique déterministe (marche aléatoire).

    Utile pour démontrer/tester les stratégies sans dépendre du réseau.
    `drift` = tendance moyenne par pas, `volatility` = amplitude des secousses.
    """
    import random

    rng = random.Random(seed)
    prices = [float(start)]
    for _ in range(max(0, steps - 1)):
        shock = rng.uniform(-volatility, volatility)
        nxt = prices[-1] * (1 + drift + shock)
        prices.append(max(0.01, nxt))
    return prices


def run_backtest(strategy: str, prices: List[float], *, budget_eur: float = 20.0,
                 eur_per_step: float = 5.0) -> BacktestResult:
    """Dispatch vers la stratégie demandée."""
    strategy = strategy.lower()
    if strategy == "buy-hold":
        return buy_hold(prices, budget_eur)
    if strategy == "dca":
        return dca(prices, eur_per_step)
    raise ValueError(f"Stratégie inconnue : {strategy!r}. Choix : buy-hold, dca.")
