"""Projections à intérêts composés.

Montre l'effet du temps et de la régularité (versements mensuels) — le vrai
« super-pouvoir » pour faire fructifier un petit capital sur le long terme.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class YearProjection:
    year: int
    balance: float
    contributed: float   # total versé (capital + versements) à ce stade
    interest: float      # gains cumulés = balance - contributed


def project(
    principal: float,
    annual_rate_pct: float,
    years: int,
    monthly_contribution: float = 0.0,
) -> List[YearProjection]:
    """Projette une croissance à intérêts composés mensuels.

    - `principal` : capital de départ (ex. 20€).
    - `annual_rate_pct` : taux annuel en pourcent (ex. 6 pour 6%).
    - `years` : horizon en années.
    - `monthly_contribution` : versement ajouté chaque mois.

    Hypothèse : rendement constant et lissé. La réalité fluctue — ceci illustre
    l'ordre de grandeur, ce n'est pas une promesse.
    """
    if years < 0:
        raise ValueError("Le nombre d'années doit être positif.")
    monthly_rate = (annual_rate_pct / 100.0) / 12.0

    balance = float(principal)
    contributed = float(principal)
    results: List[YearProjection] = [
        YearProjection(0, balance, contributed, balance - contributed)
    ]

    for year in range(1, years + 1):
        for _ in range(12):
            balance *= (1 + monthly_rate)
            balance += monthly_contribution
            contributed += monthly_contribution
        results.append(
            YearProjection(year, balance, contributed, balance - contributed)
        )
    return results
