# Football 1X2 & Derivative Market Prediction

A quantitative research engine that predicts pre-match football outcomes for the
top five European leagues (EPL, La Liga, Bundesliga, Serie A, Ligue 1) and prices
derivative markets (Over/Under 2.5, BTTS) from a calibrated scoreline matrix.

The engine is built for research, not for chasing returns. It tests whether the
B365 and Pinnacle markets hide exploitable value; the answer so far is no, and
the code is structured to keep that conclusion honest.

## Contents

- [Key achievements](#key-achievements)
- [Quick start](#quick-start)
- [How it works](#how-it-works)
- [Live shadow tracker](#live-shadow-tracker)
- [Cups: EFL Cup & DFB Pokal](#cups-efl-cup--dfb-pokal)
- [Reference](#reference)
- [Automation](#automation)
- [Environment & dependencies](#environment--dependencies)
- [Testing](#testing)

## Key achievements

- **Elite calibration.** The meta model reaches a walk-forward log loss of
  **1.0013** and Brier 0.5986, near the information ceiling implied by the
  market. A Dixon-Coles bivariate Poisson model, a feature model, and market
  odds are stacked into a multinomial logistic meta-model.
- **Strict discipline.** Every experiment runs leak-free walk-forward validation,
  proper scoring metrics (log loss, Brier, per-class), and a dual gate: a log
  loss safety check plus a fixed-threshold yield check with a bootstrap
  significance test. A de-vigging bug that inflated a false +3.23% strategy was
  found and fixed; a small-sample +6.7% policy was kept out because its bootstrap
  p-value was 0.216. No live betting strategy is active without a significant,
  stable backtest.
- **Market efficiency finding.** The 1X2 and Over/Under 2.5 derivative markets
  look efficient: soft books copy sharp lines, and after removing the margin no
  tested rule produces a statistically significant positive ROI.

## Quick start

Run the end-to-end pipeline:

```
python setup_cache.py
python pipeline_orchestrator.py --run-all
```

Individual pieces also run standalone: `python model_v2.py final` fits and prints
the scoring report, `python backtest_value.py` reruns the value-bet backtest, and
`python refresh_fixtures.py` pulls fresh fixtures.

JIT hybrid capture runs every 30 minutes (organic odds accumulation for
closing-line value):

```
python jit_orchestrator.py             # live run
python jit_orchestrator.py --dry-run   # log window, skip API
python jit_orchestrator.py --selfcheck # offline window-logic check
```

## How it works

Main pipeline order (`pipeline_orchestrator.py`):

```
data → xg → model → corner_model → scoring → odds → ta_scrape → ta_model
    → cups → picks → validation → status
```

| Component | File | Role |
|---|---|---|
| Dixon-Coles engine | `model_v2.py` | bivariate Poisson model with low-score dependency correction and decayed team ratings. Fit mode `DC_FIT_MODE` (`goals` or `blend`; default `blend` = 0.5·goals + 0.5·xG where xG exists) |
| Meta model | `experiment_meta.py`, `backtest_picks.py` | stacks logits of the DC model, the feature model, and market-implied probabilities with a walk-forward multinomial logistic regression; consumes sharp signals (Pinnacle deviation, shin-fair probabilities, midweek flags) |
| Matrix pricing | `matrix_pricer.py` | builds the bivariate Poisson scoreline matrix and meta-calibrates it so summed 1X2 marginals match the meta model; O/U and BTTS derive from that matrix |
| Corner model | `model_corners_v3.py` | Poisson model predicting team corner counts and corner O/U lines from rolling shot statistics (fitted parameters in `ta/corner_params.json`). Beats league base-rate on walk-forward log loss, Brier, MAE, RMSE; awaiting historical corner odds for a final ROI backtest (`data_enrichment/fetch_corner_odds.py` scaffolding in place) |
| Data enrichment | `data_enrichment/` | joins Pinnacle odds, midweek/cup fatigue flags, and rolling xG differentials into `all_matches_enriched.csv`, without touching the clean source data |
| JIT hybrid capture | `jit_orchestrator.py` | every 30 minutes loads the Understat fixture cache, keeps matches starting within 45 minutes, scrapes the free source (TipsterArea) for 1X2 and O/U first, then calls API-Football v3 only for premium markets the scrape lacks (Corners O/U, BTTS), deduping into `ta/external_corner_odds.csv` and `ta/external_btts_odds.csv`. API is hit only for leagues with a match in the window; raw responses cached; `--selfcheck` verifies window logic offline. On the free plan the API serves only current-day data, so capture backfills forward from today |
| Policy engine | `backtest_picks.py` | filters betting decisions after the model (edge thresholds, overlays, staking) so calibration stays intact; candidate policies must clear the dual gate before going live |

## Live shadow tracker

`run_daily_shadow.py` runs the production monitor as a daily cron-safe chain:
generate predictions → filter and record picks → resolve and grade. Each step is
isolated with try/except, so a failure in one stage never crashes the pipeline.
It is deliberately strict: with no validated edge, it emits **0 picks** and
records nothing to the ledger. When a strategy clears the gates, this is the
component that goes to a real ledger without risking live money.

## Cups: EFL Cup & DFB Pokal

`predict_cups.py` predicts EFL Cup and DFB Pokal ties without API-Football.
Fixtures come from the tipsterarea scrape (`ta/fixtures.csv`), market odds
from tipsterarea match-page snapshots (summarised in `market_compare.csv`),
and results for grading from `ta/results.csv`.

Each team is mapped to its league division (E0–E3 in England, D1–D2 in
Germany), and a tie is only predicted when both teams map. Goal lambdas come
from the two divisions' league fits. The tie's total is then rescaled to the
competition's own measured scoring rate, taken from scraped cup results, at
full weight once 100 or more finished ties are on file and half weight below
that. The rescale keeps the home:away split from the league fits. This is a
known simplification. The model has no cup-specific team ratings, and the
per-competition grading shows what that costs.

Single-leg ties also get advance probabilities in the `p_adv_h` and
`p_adv_a` columns, the chance of going through when a level score can be
settled by extra time (lambdas scaled to 30 minutes) and penalties weighted
by the two teams' 90-minute win probabilities. Both columns stay empty for
two-legged ties.

Corners use the home team's division corner base rate (HC/AC, half-life 270)
times each team's relative rolling shots factor over its last 5 league
matches. If either team has fewer than 3 league matches with shots data,
corners are skipped for that tie and the goal prediction still runs. Cup
corners are not graded, because no available results source records cup
corner counts.

Cup results never enter league training data, and cup rows never mix into
`predictions_upcoming.csv` or `predictions_corners_upcoming.csv`. Predictions
live in `predictions_cups_upcoming.csv` and `predictions_corners_cups.csv`,
and cup picks are graded per competition in `ledger_summary.json`.

## Reference

[QUANT_RESEARCH_REPORT.md](QUANT_RESEARCH_REPORT.md) contains the full scientific
summary: the modeling milestones, the de-vigging and small-sample lessons, and
the market-efficiency evidence.

[EXPERIMENT_XG_DC.md](EXPERIMENT_XG_DC.md) documents the xG-vs-goals Dixon-Coles
fit experiment and the go-live gates (meta stack, derivatives, held-out seasons)
behind the `blend` fit-mode default.

## Daily recommendations (single bet + slips)

`slip_recommender.py` builds three deterministic recommendation files per
report date from real 1xBet odds in `market_compare.csv` joined to model
probabilities (markets 1X2 / DC / OU / BTS; one leg per match). All three are
produced in the daily shadow run (step 8b) and archived daily.

- **`recommended_single.csv`** — the day's single bet: highest EV
  (`p_model * o_1xbet - 1`) among legs with `p_model >= 0.45` and
  `o_1xbet >= 1.40` (tie-break: probability, then odds). Columns add `ev` and
  `below_floor` (true only when the relaxed 0.40 / 1.30 floor had to be used).
- **`recommended_slip.csv`** — slip with total odds in the 1.85–2.15 band
  (target 2.0): 2–4 legs from the report date only, `p_model >= 0.50`,
  `o_1xbet >= 1.20`, highest joint probability (tie-break total EV). Without
  an in-band combo, the closest-to-2.0 combo of that date is emitted with
  `in_band=false`. Columns: one row per leg plus `slip_total_odds`,
  `slip_joint_prob`, `slip_ev`, `in_band`.
- **`recommended_slip10.csv`** — slip with total odds in the 9.0–11.0 band
  (target 10.0): 3–6 legs, `p_model >= 0.35`, `o_1xbet >= 1.30`, highest
  joint probability. The pool starts at the report date and expands day by
  day (max +4) only until an in-band combo exists; every leg row carries its
  own match date and the extra column `pool_expanded_to` records how far the
  pool reached. Without an in-band combo, the closest-to-10.0 combo is
  emitted with `in_band=false`.

## Automation

Weekly refit runs every Monday at 04:00 WIB (Sunday 21:00 UTC) via
`weekly_refit.sh` — the full `--run-all` pipeline — so team-rating decay and
model parameters stay fresh:

**Training-data refresh (`step_refresh_training_data`).** Before refitting,
the pipeline refreshes league training data (no API-Football — histories come
from football-data.co.uk + Understat only):

- Re-downloads **current-season only** football-data.co.uk CSVs (21 divisions,
  season `2627`, override via `FOOTBALL_REFRESH_SEASON`), then rebuilds
  `all_matches_clean.csv` via `prepare.py` + `clean.py`.
- Refreshes Understat season dumps (`xg_raw/{League}_{year}.json`) via
  `getLeagueData` (same fetcher as `refresh_fixtures.py`), so `build_xg_matches`
  picks up the latest xG.
- Backs up `all_matches_clean.csv` and xG dumps to timestamped `.bak-*` before
  overwriting; validates total rows and current-season rows never decrease
  (rollback + explicit failure if they do), then rebuilds `records_cache` with
  a data-freshness stamp when the data changed.

**Daily results sync (`run_daily_shadow.py`).** The daily live-shadow chain now
explicitly syncs tipsterarea results for yesterday + H-2 before grading, using
`ta_scrape.py <date> --fresh` (forces a network fetch past the 20-min date-page
cache so late-finishing games land in `ta/results.csv`; network failure is a
warning, not a pipeline failure).

```
0 21 * * 0 cd /path/to/football-data && ./weekly_refit.sh >> logs/weekly_refit.log 2>&1
```

JIT capture cron:

```
*/30 * * * * cd /path/to/football-data && python jit_orchestrator.py >> logs/jit_capture.log 2>&1
```

## Environment & dependencies

Requires `API_FOOTBALL_KEY` in the environment (or `.env`). Optional overrides:
`FOOTBALL_DC_FIT_MODE` (`goals`|`blend`, default `blend`).

Dependencies: `numpy` (see `requirements.txt`). The optional API server
(`api_server.py`) and scrapers use `fastapi`, `uvicorn`, `pydantic`, `requests`,
and `httpx`.

## Testing

`test_core.py` holds the smoke tests:

```
python test_core.py
```

The xG cache is rebuilt from tracked Understat season dumps with
`data_enrichment/build_xg_matches.py` (local, offline; missing season files are
skipped without failing the pipeline).
