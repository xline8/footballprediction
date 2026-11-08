# G-PT DEV engine

`run_g_pt.py dev` loads only 2021/2022 through 2025/2026, fits season-blocked Dixon-Coles Gate Zero and SHRINK, and writes `results_dev.json` and `results_dev.csv`. The `virgin` interface is reserved and is not run. Season labels are ordered lexically as frozen in the preregistration; the output uses negative log loss.

Virgin: see the market virgin runner (`virgin_*_pt.py`) and `results_virgin.json`; verdict in `league/PT-LigaPortugal/reports/`.
