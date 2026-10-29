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
- A second audit pass fixed the numbers the system reports about
  itself: `ta_model` now prices bets from each bookmaker's latest
  quote instead of the best price ever captured; `generate_predictions`
  reports `partial`/`error` instead of unconditional success and no
  longer leaves a stale file looking fresh; the Kelly summary in
  `resolve_and_monitor` is computed over the Kelly-staked rows only;
  the calibration summary groups BTTS picks under the `BTS` key the
  producers actually write; and slip EV is the joint EV of the whole
  slip, not a sum of per-leg EVs.
- Market state is now genuinely pre-match: `_prematch_state` filters
  snapshots to those captured before kickoff, so in-play prices can
  no longer appear as prematch prices in `market_compare` or as the
  opening odds of cup picks in the money ledger. Slip units in the
  calibration grading are keyed by the slip's content rather than
  its archive date, so a stale file re-archived under a new date no
  longer counts the same slip twice.
- Model persistence and fit aggregation: a refit triggered from the
  prediction path is now saved (`ModelState.updated_at` was never
  set, so the save was a no-op), a stored half-life that disagrees
  with the configuration forces a refit, teams missing from the
  cached state get neutral ratings instead of silently dropped
  prediction rows, and per-division fit failures roll up into the
  pipeline's run status.
- Cup predictions use the fitted per-division rho (previously
  discarded for a fixed default), the latest 1X2 snapshot per match
  instead of the oldest, a linear goal-anchor ramp instead of a
  cliff at 100 results, and the corner dispersion from
  `corner_params.json` instead of a hardcoded copy.
- Scraper and live-pick hardening: `--fresh` is honored in the
  async fetch path, the legacy 1X2 table fallback no longer copies
  the first odd to all three selections, a date page that parses to
  zero matches is reported instead of passing silently, market rows
  whose price cells cannot be aligned to their labels are skipped,
  and `make_picks_live` skips past-dated rows and tolerates empty
  probability cells.
- API corrections: graded picks are reachable (`?status=win/loss`
  joins `grades.jsonl` and is no longer emptied by the upcoming
  filter), `/api/status` counts graded picks from the grades file,
  `/api/odds` returns upcoming fixtures only instead of a full
  season, and the upcoming filter compares UTC kickoff times rather
  than the server's local date.
- Data enrichment: closing odds are read from the closing columns
  (the opening columns were used and labelled closing), and the xG
  join uses the producer's team-name normalizer so aliased clubs
  match instead of silently falling back to goal difference.
  Asian-handicap quarter lines are settled as split half-lines in
  the evaluation path, the corner base-rate dispersion no longer
  depends on iteration order, a mistyped Gladbach alias and the
  `utd` short forms are fixed, `best_picks --date` anchors its
  loaders on the requested date, and the ledger/grade/archive file
  rewrites are atomic.

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
