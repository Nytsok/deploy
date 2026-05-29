"""Fournisseur de prix de marché.

Stratégie : essayer l'API publique CoinGecko (gratuite, sans clé) pour de vrais
prix crypto en EUR. Si le réseau est indisponible, on bascule sur un repli
hors-ligne déterministe afin que le bot reste utilisable et testable partout.

Aucune dépendance externe : on utilise uniquement la stdlib (urllib).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids={ids}&vs_currencies=eur"
)

# Prix de repli (EUR) utilisés uniquement si le réseau est indisponible.
# Valeurs indicatives — clairement marquées comme telles dans l'UI.
OFFLINE_FALLBACK_EUR = {
    "bitcoin": 60000.0,
    "ethereum": 3000.0,
    "solana": 140.0,
    "cardano": 0.45,
    "tether": 0.92,
}


class PriceResult:
    """Résultat d'une requête de prix, avec l'origine de la donnée."""

    def __init__(self, asset: str, eur: float, source: str):
        self.asset = asset
        self.eur = eur
        self.source = source  # "live" ou "offline-fallback"

    @property
    def is_live(self) -> bool:
        return self.source == "live"

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return f"PriceResult(asset={self.asset!r}, eur={self.eur}, source={self.source!r})"


def get_price(asset: str, timeout: float = 6.0) -> PriceResult:
    """Retourne le prix en EUR d'un actif.

    Tente d'abord un prix réel via CoinGecko, puis se rabat sur une valeur
    hors-ligne si le réseau échoue. Lève KeyError si l'actif est inconnu et
    qu'aucun prix réel n'a pu être obtenu.
    """
    asset = asset.strip().lower()
    try:
        url = COINGECKO_URL.format(ids=urllib.parse.quote(asset))
        req = urllib.request.Request(url, headers={"User-Agent": "finance-bot/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        eur = data.get(asset, {}).get("eur")
        if eur is not None:
            return PriceResult(asset, float(eur), "live")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        # Réseau indisponible / réponse invalide → repli hors-ligne.
        pass

    if asset in OFFLINE_FALLBACK_EUR:
        return PriceResult(asset, OFFLINE_FALLBACK_EUR[asset], "offline-fallback")

    raise KeyError(
        f"Actif inconnu '{asset}' et aucun prix réel disponible. "
        f"Actifs hors-ligne connus : {', '.join(sorted(OFFLINE_FALLBACK_EUR))}."
    )
