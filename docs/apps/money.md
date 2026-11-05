# MoneyCraft demos

[All apps](README.md) | [Repo README](../../README.md)

**What it is**: sovereign offline-first quantitative finance terminal: market feeds
(synthetic drift), technical indicators, personal wealth vs inflation simulator
(Girokonto, Festgeld, Bausparer), global indices desk, G10 forex, crypto
derivatives, Monte Carlo backtester, EVM honeypot auditor, private tax ledger.
The app's own comparison is Bloomberg Terminal / QuickBooks / Firefly III. Driven by
`C:\Program Files\MoneyCraft\moneycraft-cli.exe` (verified against 0.7.0, 2026-11-05).

## Demos

| Demo | What actually runs | Artifacts | AI step |
|---|---|---|---|
| `ledger-reconcile` | `status`, `ticker EUR/USD`, `ticker BTC/USD` (60 bars each), `backtest sma-cross --symbol BTC --capital 10000`, `simulate-wealth` (defaults), `portfolio`. Every number in the report is parsed from the engine's own JSON. | `ledger-report.md/.json` | none |
| `capability-map` | The installed CLI's `commands` output (or `--help`). | `capabilities.txt` | none |

Measured on 0.7.0. Status: 20 modules, `ready`. FX feed: 60 bars, EUR/USD last
close ~1.085. Crypto feed: 60 bars, BTC/USD last close ~99,746. Backtest
`sma-cross`: 10,000 -> 13,860 (38.6% ROI, Sharpe 2.45, win rate 0.67, 142 trades,
max drawdown 7.8%). Wealth sim: 500 EUR/mo free cashflow, net real yield -1.61%,
912 EUR/yr inflation drag. Portfolio: 8 positions, 486,240 USD equity, 48,180 USD
unrealized, 92,400 USD realized YTD. Feeds are synthetic drift, so closes move
between runs; counts and shapes are stable.

## Hands-in / Hands-out

| Direction | What |
|---|---|
| Hands-in | a ticker symbol, a strategy name, wealth-sim assumptions |
| Hands-out | ledger reconciliation report (Markdown + JSON) |

## Run it

```
/craft/money
craft(operation="run_demo", app="money", demo="ledger-reconcile")
```

Artifacts: `outbox/money/ledger-reconcile/`.

## Observed gaps

- Live market tick feeds require external broker API credentials; headless runs use synthetic drift.
- Tax compliance modules limited to standard GAAP / IFRS profiles.
