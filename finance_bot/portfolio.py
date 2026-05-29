"""Portefeuille en paper-trading (simulation, aucun argent réel).

Persiste l'état dans un fichier JSON local. Gère le cash en EUR et des positions
en unités d'actifs, avec un historique des transactions simulées.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "portfolio.json")


@dataclass
class Transaction:
    timestamp: str
    action: str          # "buy" | "sell" | "init"
    asset: str           # "EUR" pour init/cash, sinon nom de l'actif
    units: float         # unités d'actif échangées
    eur: float           # montant EUR du mouvement
    price_eur: float     # prix unitaire au moment de l'opération


@dataclass
class Portfolio:
    cash_eur: float = 0.0
    positions: Dict[str, float] = field(default_factory=dict)  # asset -> units
    history: List[Transaction] = field(default_factory=list)

    # --- Persistance -----------------------------------------------------
    @classmethod
    def load(cls, path: str = DEFAULT_PATH) -> "Portfolio":
        if not os.path.exists(path):
            return cls()
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls(
            cash_eur=float(data.get("cash_eur", 0.0)),
            positions={k: float(v) for k, v in data.get("positions", {}).items()},
            history=[Transaction(**t) for t in data.get("history", [])],
        )

    def save(self, path: str = DEFAULT_PATH) -> None:
        payload = {
            "cash_eur": self.cash_eur,
            "positions": self.positions,
            "history": [asdict(t) for t in self.history],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    # --- Opérations ------------------------------------------------------
    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def initialize(self, cash_eur: float) -> None:
        if cash_eur < 0:
            raise ValueError("Le capital initial doit être positif.")
        self.cash_eur = float(cash_eur)
        self.positions = {}
        self.history = [
            Transaction(self._now(), "init", "EUR", 0.0, float(cash_eur), 1.0)
        ]

    def buy(self, asset: str, eur: float, price_eur: float) -> float:
        """Achète pour `eur` d'un actif au prix `price_eur`. Retourne les unités."""
        asset = asset.lower()
        if eur <= 0:
            raise ValueError("Le montant d'achat doit être positif.")
        if price_eur <= 0:
            raise ValueError("Le prix doit être positif.")
        if eur > self.cash_eur + 1e-9:
            raise ValueError(
                f"Fonds insuffisants : {eur:.2f}€ demandés, {self.cash_eur:.2f}€ disponibles."
            )
        units = eur / price_eur
        self.cash_eur -= eur
        self.positions[asset] = self.positions.get(asset, 0.0) + units
        self.history.append(
            Transaction(self._now(), "buy", asset, units, eur, price_eur)
        )
        return units

    def sell(self, asset: str, units: float, price_eur: float) -> float:
        """Vend `units` d'un actif au prix `price_eur`. Retourne l'EUR encaissé."""
        asset = asset.lower()
        if units <= 0:
            raise ValueError("Le nombre d'unités à vendre doit être positif.")
        if price_eur <= 0:
            raise ValueError("Le prix doit être positif.")
        held = self.positions.get(asset, 0.0)
        if units > held + 1e-12:
            raise ValueError(
                f"Position insuffisante : {units} demandées, {held} détenues."
            )
        eur = units * price_eur
        self.positions[asset] = held - units
        if self.positions[asset] <= 1e-12:
            del self.positions[asset]
        self.cash_eur += eur
        self.history.append(
            Transaction(self._now(), "sell", asset, units, eur, price_eur)
        )
        return eur

    # --- Valorisation ----------------------------------------------------
    def value(self, prices_eur: Dict[str, float]) -> float:
        """Valeur totale = cash + positions valorisées aux prix fournis."""
        total = self.cash_eur
        for asset, units in self.positions.items():
            total += units * prices_eur.get(asset, 0.0)
        return total
