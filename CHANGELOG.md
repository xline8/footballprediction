# Changelog

All notable changes to this project are recorded here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [Unreleased]

### Fixed

- `score_ledger` settled every Over/Under pick against a hardcoded
  2.5 line; picks that carry their own line (cup picks, e.g. OU 1.5)
  are now settled against it, with an exact integer line graded as a
  push.
- `ta_model` corner grading never matched its actual-count lookup
  (raw DD/MM/YYYY dates and raw team names against ISO dates and
  normalized names), so corner bets were settled against goal totals.
  Keys now agree on both sides, and a corner bet with no matching
  actual counts stays open instead of being graded on goals.
- Failure honesty in the runners: `run_daily_shadow` now flags any
  failed step (including market sync, recommendations, grading, and
  archive) in its exit code instead of always ending in success, and
  grades the money ledger (`score_ledger`) daily — previously only a
  manual incremental run did. `pipeline_orchestrator` propagates
  failed steps into the run status and process exit code, and its
  prediction and corner steps verify the inner status / output
  freshness instead of reporting success over stale files.
- The slip search in `slip_recommender` is bounded by a node budget;
  oversized pools now return the best candidate found so far instead
  of running unbounded inside the daily chain.

### Removed

- JIT capture and the API-Football integration (`jit_orchestrator.py`,
  `daily_api_capture.py`, `data_enrichment/api_football_client.py`,
  `data_enrichment/fetch_corner_odds.py`, and the `--corner-export` path
  in `ta_scrape.py`). The capture existed to collect near-kickoff corner
  and BTTS odds, but the API plan in use has no access to the current
  season, so it never produced a single row; every market the project
  actually prices already comes from tipsterarea. The corner model stays
  and is still graded on calibration against actual corner counts.

## [1.0.0] - 2026-10-29

First tagged release: the research engine running as a daily production
system.

### Added

- Cup predictions for EFL Cup and DFB Pokal (`predict_cups.py`):
  league-rating based, with the total anchored to each competition's
  measured scoring rate, advance probabilities for single-leg ties, and
  per-competition ledger buckets.
- Market orchestration: tipsterarea match-page odds synced daily for all
  model fixtures, and `market_compare.csv` with 1xBet prices, cross-book
  medians, and normalised implied probabilities.
- Daily recommendations (`slip_recommender.py`): a single bet, a slip at
  total odds near 2, and a slip at total odds near 10, all scoped to the
  report date.
- Closing-line value as the ledger's headline metric, backfilled for all
  graded picks (358 of 358 covered).
- A daily archive of the nine pipeline outputs under `archive/<date>/`.
- Unit tests for the core math, a GitHub Actions test workflow, an MIT
  license, and this changelog.

### Changed

- The Dixon-Coles fit defaults to `blend` (0.5 goals + 0.5 xG) after the xG
  experiment passed its three go-live gates.
- Training data now refreshes itself weekly from football-data.co.uk and
  Understat before refitting, and match results sync daily from
  tipsterarea. API-Football is used only by JIT near-kickoff capture.
- README rewritten to match the running system; the research and
  verification documents moved into `docs/`.

### Findings recorded

- Edge-band experiment: UNVALIDATED. The 0.20–0.22 live-pick band never
  fires in the 2017/18–2025/26 walk-forward history (largest observed edge
  about +0.08), so the policy engine emits no live picks.
- Corner model calibration: per-division bias and ladder deviation were
  inside tolerance on 12,457 graded matches, both correction gates failed,
  and the model was left unchanged.
- Ledger at release: 358 graded league picks, ROI −5.79% at opening odds,
  mean CLV EV −0.0597, beat-close rate 57.5%.

## [0.1.0] - 2026-10-26

- Initial commit: Dixon-Coles, corners, and value-betting research
  pipeline with leak-free walk-forward backtests, the de-vigging fix, and
  the market-efficiency research report.
