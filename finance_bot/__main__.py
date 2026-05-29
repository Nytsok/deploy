"""Interface en ligne de commande du Finance Bot (paper-trading éducatif).

Aucun argent réel n'est déplacé. Sans garantie de gain. Voir le README.
"""

from __future__ import annotations

import argparse
import sys

from . import strategies
from .portfolio import Portfolio
from .prices import get_price
from .projection import project

DISCLAIMER = (
    "⚠️  Simulation éducative — aucun argent réel, aucune garantie de gain. "
    "Investir comporte un risque de perte."
)


def _print_disclaimer() -> None:
    print(DISCLAIMER)
    print("-" * 70)


def cmd_init(args: argparse.Namespace) -> int:
    pf = Portfolio()
    pf.initialize(args.cash)
    pf.save()
    print(f"✅ Portefeuille initialisé avec {args.cash:.2f}€ de cash (simulation).")
    return 0


def cmd_price(args: argparse.Namespace) -> int:
    res = get_price(args.asset)
    tag = "prix réel" if res.is_live else "REPLI HORS-LIGNE (indicatif, réseau indisponible)"
    print(f"{res.asset} : {res.eur:.4f}€  [{tag}]")
    return 0


def cmd_buy(args: argparse.Namespace) -> int:
    pf = Portfolio.load()
    res = get_price(args.asset)
    units = pf.buy(args.asset, args.eur, res.eur)
    pf.save()
    src = "réel" if res.is_live else "hors-ligne"
    print(
        f"✅ Acheté (simulation) {units:.8f} {args.asset} pour {args.eur:.2f}€ "
        f"@ {res.eur:.4f}€ [{src}]. Cash restant : {pf.cash_eur:.2f}€."
    )
    return 0


def cmd_sell(args: argparse.Namespace) -> int:
    pf = Portfolio.load()
    res = get_price(args.asset)
    eur = pf.sell(args.asset, args.units, res.eur)
    pf.save()
    print(
        f"✅ Vendu (simulation) {args.units:.8f} {args.asset} pour {eur:.2f}€ "
        f"@ {res.eur:.4f}€. Cash : {pf.cash_eur:.2f}€."
    )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    pf = Portfolio.load()
    prices = {}
    any_offline = False
    for asset in pf.positions:
        res = get_price(asset)
        prices[asset] = res.eur
        any_offline = any_offline or not res.is_live

    total = pf.value(prices)
    print(f"💶 Cash       : {pf.cash_eur:.2f}€")
    if pf.positions:
        print("📊 Positions  :")
        for asset, units in sorted(pf.positions.items()):
            val = units * prices.get(asset, 0.0)
            print(f"   - {asset:<10} {units:.8f} → {val:.2f}€ (@ {prices[asset]:.4f}€)")
    else:
        print("📊 Positions  : (aucune)")
    print("-" * 70)
    print(f"💰 Valeur totale : {total:.2f}€")
    if any_offline:
        print("   (certains prix sont des replis hors-ligne, indicatifs)")
    return 0


def cmd_project(args: argparse.Namespace) -> int:
    rows = project(args.principal, args.rate, args.years, args.monthly)
    print(
        f"Projection : {args.principal:.2f}€ à {args.rate:.1f}%/an, "
        f"{args.years} ans, +{args.monthly:.2f}€/mois"
    )
    print(f"{'Année':>5} {'Solde':>12} {'Versé':>12} {'Gains':>12}")
    for r in rows:
        print(f"{r.year:>5} {r.balance:>12.2f} {r.contributed:>12.2f} {r.interest:>12.2f}")
    print("-" * 70)
    print("ℹ️  Rendement lissé hypothétique — la réalité fluctue, pas une promesse.")
    return 0


def cmd_backtest(args: argparse.Namespace) -> int:
    prices = strategies.synthetic_prices(
        start=args.start, steps=args.steps, drift=args.drift,
        volatility=args.volatility, seed=args.seed,
    )
    res = strategies.run_backtest(
        args.strategy, prices, budget_eur=args.budget, eur_per_step=args.eur_per_step
    )
    print(f"Backtest sur {len(prices)} pas de prix synthétiques (déterministes).")
    print(res.summary())
    print("-" * 70)
    print("ℹ️  Prix simulés à des fins de démonstration — résultats non garantis.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="finance_bot",
        description="Bot finance en paper-trading (simulation, sans argent réel).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init", help="Initialiser le portefeuille avec du cash.")
    sp.add_argument("--cash", type=float, default=20.0, help="Capital initial en EUR (def. 20).")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("price", help="Afficher le prix d'un actif.")
    sp.add_argument("--asset", required=True, help="Ex: bitcoin, ethereum, solana.")
    sp.set_defaults(func=cmd_price)

    sp = sub.add_parser("buy", help="Acheter (simulation) pour un montant en EUR.")
    sp.add_argument("--asset", required=True)
    sp.add_argument("--eur", type=float, required=True, help="Montant à investir en EUR.")
    sp.set_defaults(func=cmd_buy)

    sp = sub.add_parser("sell", help="Vendre (simulation) un nombre d'unités.")
    sp.add_argument("--asset", required=True)
    sp.add_argument("--units", type=float, required=True)
    sp.set_defaults(func=cmd_sell)

    sp = sub.add_parser("status", help="Afficher l'état valorisé du portefeuille.")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("project", help="Projeter une croissance à intérêts composés.")
    sp.add_argument("--principal", type=float, default=20.0)
    sp.add_argument("--rate", type=float, default=6.0, help="Taux annuel en %% (def. 6).")
    sp.add_argument("--years", type=int, default=10)
    sp.add_argument("--monthly", type=float, default=0.0, help="Versement mensuel EUR.")
    sp.set_defaults(func=cmd_project)

    sp = sub.add_parser("backtest", help="Backtester une stratégie sur des prix simulés.")
    sp.add_argument("--strategy", choices=["buy-hold", "dca"], default="dca")
    sp.add_argument("--budget", type=float, default=20.0, help="Budget total (buy-hold).")
    sp.add_argument("--eur-per-step", type=float, default=5.0, help="Montant par pas (dca).")
    sp.add_argument("--steps", type=int, default=12)
    sp.add_argument("--start", type=float, default=100.0, help="Prix de départ simulé.")
    sp.add_argument("--drift", type=float, default=0.01)
    sp.add_argument("--volatility", type=float, default=0.05)
    sp.add_argument("--seed", type=int, default=42)
    sp.set_defaults(func=cmd_backtest)

    return p


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    _print_disclaimer()
    try:
        return args.func(args)
    except (ValueError, KeyError) as exc:
        print(f"❌ Erreur : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
