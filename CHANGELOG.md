# Changelog

All notable changes to this project are recorded here. The format follows
Keep a Changelog, and the project uses semantic versioning.

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
