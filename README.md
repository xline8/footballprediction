# Football Match Outcome Prediction

Prediction pipeline for top-5 European football leagues (EPL, La Liga, Bundesliga, Serie A, Ligue 1). Uses a **Dixon-Coles** bivariate Poisson model for match outcomes, a shot-based **corner model**, plus a value-betting layer that blends model probabilities against market odds.

## Pipeline

`pipeline_orchestrator.py --run-all` runs the full chain:

| Step | What it does | Code |
|---|---|---|
| 1. Data | Validates match data (`all_matches_clean.csv`) and loads cache | `football_etl.py`, `data_loader.py` |
| 2. Models | Fits/updates Dixon-Coles for each division (walk-forward, no leakage) | `model_v2.py`, `model_state.py` |
| 3. Corners | Predicts corner markets via shot-based rolling factors | `model_corners_v3.py` |
| 4. Odds | Integrates market odds from football-data + tipsterarea | `ta_scrape.py`, `ta_model.py` |
| 5. Picks | Generates value bets, appends to `ledger/picks.jsonl`, writes `best_picks.csv` | `make_picks.py`, `best_picks.py` |
| 6. Validation | Consistency checks on predictions, picks, ledger, model cache | `validation.py` |

Other entry points:

- `python setup_cache.py` — build/verify caches (matches, model states).
- `python refresh_fixtures.py` — refresh fixtures from Understat (`xg_raw/`), backup-aware.
- `python download.py` — download raw football-data CSV files into `raw/`.
- `python backtest_value.py` — backtest the value-bet strategy against historical odds.
- `python grade_picks.py` — grade settled picks from the ledger.
- `python model_v2.py final` — full fit + validation report (Brier, log-loss, calibration).

## Model

**Dixon-Coles** — bivariate Poisson with a low-score adjustment (`tau`) and home-advantage term. Trained on a rolling window (`max_train` ~4000 matches) with a half-life time decay (`hl`). Ratings persist per division in `.cache/models/` via `ModelState`.

Validation is strictly **walk-forward** (expansion windows, monthly groups) — features and ratings are computed only from matches before the prediction date, to prevent leakage. Proper scoring rules are reported: Brier score, overall + per-class log loss, and a calibration table.

**Features** (built but not yet wired into live predictions): Elo ratings, rolling xG, rest days, head-to-head — see `features.py` / `feature_analysis.py`.

## Setup

```bash
pip install -r requirements.txt
python setup_cache.py        # build caches
python pipeline_orchestrator.py --run-all
```

Python 3.10+; dependencies: numpy only (scipy optional). Paths are centralized in `paths.py`.

## Layout

```
pipeline_orchestrator.py   main orchestrator
football_etl.py            shared ETL + math primitives (pois, tau, norm, blend)
model_v2.py                Dixon-Coles model
model_corners_v3.py        corner model
model_state.py             per-division model persistence
features.py                leak-free feature builder (Elo, xG, rest, H2H)
validation.py              proper scoring metrics
paths.py                   central path constants
xg_raw/                    Understat fixtures / xG raw data
raw/                       football-data CSV downloads
ledger/                    picks (picks.jsonl) + grading (graded.csv)
test_core.py               smoke tests (math, scoring, walk-forward leak-free)
```

## Tests

```bash
python test_core.py
```
