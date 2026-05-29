"""Tests unitaires du Finance Bot. N'effectuent aucun appel réseau."""

from __future__ import annotations

import os
import tempfile
import unittest

from finance_bot import strategies
from finance_bot.portfolio import Portfolio
from finance_bot.projection import project


class TestPortfolio(unittest.TestCase):
    def test_init_and_buy_sell(self):
        pf = Portfolio()
        pf.initialize(20.0)
        self.assertEqual(pf.cash_eur, 20.0)

        units = pf.buy("bitcoin", 10.0, price_eur=50000.0)
        self.assertAlmostEqual(units, 10.0 / 50000.0)
        self.assertAlmostEqual(pf.cash_eur, 10.0)
        self.assertIn("bitcoin", pf.positions)

        eur = pf.sell("bitcoin", units, price_eur=60000.0)
        self.assertAlmostEqual(eur, units * 60000.0)
        self.assertNotIn("bitcoin", pf.positions)
        # On a gagné car on a vendu plus cher (simulation).
        self.assertGreater(pf.cash_eur, 20.0)

    def test_buy_insufficient_funds(self):
        pf = Portfolio()
        pf.initialize(20.0)
        with self.assertRaises(ValueError):
            pf.buy("bitcoin", 50.0, price_eur=50000.0)

    def test_sell_more_than_held(self):
        pf = Portfolio()
        pf.initialize(20.0)
        pf.buy("ethereum", 5.0, price_eur=2000.0)
        with self.assertRaises(ValueError):
            pf.sell("ethereum", 999.0, price_eur=2000.0)

    def test_value(self):
        pf = Portfolio()
        pf.initialize(20.0)
        pf.buy("solana", 10.0, price_eur=100.0)  # 0.1 unités
        total = pf.value({"solana": 150.0})
        # 10€ cash + 0.1 * 150 = 25€
        self.assertAlmostEqual(total, 25.0)

    def test_persistence_roundtrip(self):
        pf = Portfolio()
        pf.initialize(20.0)
        pf.buy("bitcoin", 7.0, price_eur=70000.0)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "pf.json")
            pf.save(path)
            loaded = Portfolio.load(path)
        self.assertAlmostEqual(loaded.cash_eur, pf.cash_eur)
        self.assertAlmostEqual(loaded.positions["bitcoin"], pf.positions["bitcoin"])
        self.assertEqual(len(loaded.history), len(pf.history))


class TestProjection(unittest.TestCase):
    def test_zero_rate_no_contrib(self):
        rows = project(20.0, 0.0, 5)
        self.assertEqual(rows[-1].balance, 20.0)
        self.assertEqual(rows[-1].interest, 0.0)

    def test_growth_positive(self):
        rows = project(20.0, 6.0, 10)
        self.assertGreater(rows[-1].balance, 20.0)
        self.assertEqual(rows[0].year, 0)
        self.assertEqual(rows[-1].year, 10)

    def test_monthly_contributions_counted(self):
        rows = project(20.0, 0.0, 1, monthly_contribution=5.0)
        # 0% de rendement : solde = 20 + 12*5 = 80
        self.assertAlmostEqual(rows[-1].balance, 80.0)
        self.assertAlmostEqual(rows[-1].contributed, 80.0)


class TestStrategies(unittest.TestCase):
    def test_buy_hold_up_market(self):
        res = strategies.buy_hold([100.0, 110.0, 120.0], budget_eur=20.0)
        self.assertAlmostEqual(res.invested_eur, 20.0)
        self.assertGreater(res.roi_pct, 0)

    def test_dca_invests_each_step(self):
        res = strategies.dca([100.0, 100.0, 100.0], eur_per_step=5.0)
        self.assertAlmostEqual(res.invested_eur, 15.0)
        # Prix constant → ROI ~ 0
        self.assertAlmostEqual(res.roi_pct, 0.0, places=6)

    def test_synthetic_prices_deterministic(self):
        a = strategies.synthetic_prices(100.0, 10, seed=1)
        b = strategies.synthetic_prices(100.0, 10, seed=1)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 10)

    def test_run_backtest_dispatch(self):
        prices = [100.0, 105.0, 110.0]
        res = strategies.run_backtest("buy-hold", prices, budget_eur=20.0)
        self.assertEqual(res.strategy, "buy-hold")
        with self.assertRaises(ValueError):
            strategies.run_backtest("unknown", prices)


if __name__ == "__main__":
    unittest.main()
