# Exploratory data analysis

`eda_compute.py` writes `eda_numbers.json` and `inventory_summary.json`; `make_charts.py` writes the three required charts. Pooled levels, per-season levels, home advantage, split-half reliabilities, half-share noise tests, phase counts, and team-id stability are in the JSON outputs.

Dev scored windows are 2022/2023–2024/2025. Exact scored n from the CSV is goals 776, SOT 765, corners 765, event cards 776, and total shots 765. The closest-to-0.5 primary lines are OU2.5, SOT 8.5, corners 9.5, cards 4.5, and total shots 18.5. Pre-virgin event first-half shares are goals 0.4563 and cards 0.3693; all other half constants are null.
