# Changelog

All notable changes to this project are recorded here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [Unreleased]

### Added

- Records cache schema v2: every walk-forward record now also
  stores the probabilities the system actually serves — the monthly
  walk-forward meta stack (`ph_meta`/`pd_meta`/`pa_meta`, the exact
  recipe the go-live gates score) and the Dixon-Coles derivative
  probabilities (`p_over_dc`, `p_btts`) — plus the actual goals
  (`fthg`/`ftag`). Schema 1 caches are treated as stale and rebuilt
  once. Before this, the cache stored only the DC and T3 components,
  so the served stack had never been proper-scored directly and
  backtests labelled "meta" silently measured T3.
- Two experiments from the eleventh audit round.
  `experiments/experiment_deriv_calib.py` re-measures the served
  derivative bias (O/U 2.5 under-predicts goals by 2.2 points pooled
  TOP5, BTTS by 2.8) and tests three pre-registered recalibration
  candidates on a held-out era split — all three are rejected: the
  bias is era-varying and recent-era Brier does not improve, so no
  static derivative recalibration layer is adopted.
  `experiments/experiment_spi_benchmark.py` scores the stored meta
  probabilities against FiveThirtyEight's SPI on 9,946 identical
  matches (2018-01 to 2023-06, 100% of the in-window records joined
  and score-verified): the project's stack leads SPI on Brier, log
  loss and RPS overall and in all five divisions, with the caveat
  that the meta stack consumes opening market probabilities as
  features while SPI did not.

### Fixed

- Audit round 13 (self-audit of the round 12 fixes; no high-severity
  findings — every round 12 fix re-verified substantively). The one
  medium item was the `best_bets` lifecycle: `ta_model.build()` ran
  only in the weekly refit, while `best_picks` consumed the file
  daily, so stored rows ranked for up to a week with probabilities,
  EV and prices frozen at creation — including three legacy rows
  from the pre-guard build still presenting 0.13–0.16 above the DC
  probability. The build is now a daily shadow step (the chain grows
  to sixteen steps, renumbered), still-open bets that are re-issued
  are repriced from the day's candidates (settled rows are never
  rewritten), the safest-pick ranking reads probabilities and EV
  from the current `model_markets.csv` instead of the stored bet
  rows, and the TA loader anchors on the full kickoff datetime — a
  same-day match that had already kicked off (Le Havre–PSG) was the
  sole top pick for its match in `best_picks.csv` under the old
  date-only anchor.
- Postponed-match grading fallbacks are bounded to 45 days in both
  graders, and recommendation grades now record the matched result
  date (`result_date`). Unbounded, a leg whose match was cancelled
  could have settled against the pair's next meeting months later;
  exposure was zero (no pending picks, no fallback-graded legs).
- Two defects the fix round introduced were caught by its own
  verification loop and fixed before merge: the prematch-predicate
  extraction in the corner loader dropped a variable binding the
  next line still used (the unit suite stayed green — the loader is
  file-driven; the live shadow run failed the step and exposed it),
  and the bogus-price purge would have deleted rows the previous
  build itself issued whenever the model's probability disagrees
  enough with the market (price x p_market > 1.02) — the purge now
  runs after the merge, exempts rows the current build issued or
  refreshed, and never touches settled rows.
- Regression tests for the fixes themselves (65 -> 75): a 23-match
  slip pool pinning the branch-and-bound optimum against an
  independent enumeration (the round 12 property test's 6-match
  pool could not fail on the original truncation defect), shadow
  gating integration tests (previously only a manual sandbox
  check), the postponed-fallback wiring, the prematch kickoff
  predicates, and the archive missing-date warning (whose folder
  list is now filtered to ISO date names — a stray folder could
  silently disable it). The corner parity golden pins its gamma.
- Minor: `refresh_fixtures` prints its +/- fixture listing again
  (the round 12 return statement sat in front of it) and its
  standalone CLI exits non-zero when a league came from the frozen
  fallback; the shadow's fixture exception path now also flags
  leagues written from fallback before a mid-refresh failure
  (`LAST_SOURCES`); a not-yet-published future date page is
  classified empty rather than failed in the TipsterArea sync; the
  slip search node budget is doubled to 8M (the production slip-10
  search measured ~89% of 4M on a 23-match slate); stale step
  references and dead imports cleaned up.

- An external audit (GPT, verified line by line against the code)
  found nine defects, all fixed here. The fixture loader now drops
  matches that are already results or whose UTC kickoff has passed,
  so a midday rerun can no longer predict or recommend played
  matches. The daily shadow gates every consumer of the league
  predictions on a successful predictions step and no longer
  archives stale artifacts into the new date folder that later
  grading runs read; it also refreshes league fixtures itself when
  the stalest file is over 12 hours old and refuses to predict on
  fixtures over 48 hours old. `ModelState` stamps a content
  fingerprint of its training data (goals + xG) and treats a
  mismatch as a refit trigger, so corrected scores or backfilled xG
  cannot leave a silently stale cached model. The training-data
  refresh now reads `clean()`'s violation count: any residual
  violation is a pre-commit failure on the existing rollback path
  instead of a printed warning on data that gets committed anyway.
  The TipsterArea parser preserves the raw status text (`status_raw`
  column) that the AET/PEN-to-FT canonicalization used to discard.
  League grading fills results the Understat dumps do not have yet
  from the synced TipsterArea results. A T3 failure is reported in
  the predictions result (`t3_status`) instead of vanishing into a
  print while the run reports success. Documentation for the T3 and
  meta components now matches the production path (nine-logit
  recipe), and the stale `DC_FIT_MODE` comment in `model_v2.py` is
  corrected.
- A twelfth audit round re-audited the fixes above and the model and
  grading paths around them, and fixed what it found — including one
  high defect the previous round's own fix had introduced. The
  `ModelState` data fingerprint hashed `xg_matches.csv` at the
  project root, a file the fit never reads, so its xG component was
  permanently "absent" and xG-only revisions never invalidated the
  cached models; it now hashes the file the fit actually consumes
  (`xg_raw/xg_matches.csv`). `ta_model.calibrate()` could end
  further from its 1X2 target than the raw Dixon-Coles matrix,
  inflating derivative probabilities on strong favourites
  (Barcelona vs Alaves: BTS Yes 0.90 against the raw matrix's 0.55,
  at 7.8 expected goals against 3.8); calibration now falls back to
  the raw matrix whenever it does not improve the 1X2 fit, and
  `best_picks` ranks TA rows by the shrunk probability instead of
  raw `p_model`. The slip search is an exact branch-and-bound for
  the in-band optimum (the old DFS exhausted its node budget on
  large slates and returned a prefix candidate, 0.606 against the
  0.635 optimum on the 2026-10-31 slate); `search_truncated` is now
  a column of both slip CSVs. Fixture fallback content is surfaced:
  `refresh_fixtures` reports its per-league source and the shadow
  fails the run when a league was served from the frozen on-disk
  dump instead of letting the fresh file mtime defeat the staleness
  gate. The market sync step is gated on prediction success like
  the other consumers. TipsterArea result matching folds systematic
  club-name variants (Cologne/Koln, Internazionale/Inter Milan,
  Stade Rennais/Rennais, ...), lifting the league fill coverage
  from 333 to 394 of 397 results with zero score disagreements, and
  postponed matches are graded via an earliest-played-date fallback
  in both graders. `status_raw` is also persisted in `fixtures.csv`
  and a newly filled value rewrites the results row. The corner and
  cup loaders apply the same kickoff-time prematch filter as the
  league loader, `/api/status` reports the prediction file's age,
  and shadow step labels use a single [n/15] scheme. README figures
  are corrected to the current ledger (mean CLV EV −0.0773,
  beat-close 53.6%, stored-probability Brier 0.5766 / RPS 0.1956),
  and the five experiment files that had no recorded outcome gain a
  STATUS header. First unit tests cover the corner model, the
  cups/league corner parity surface, feature-row leakage, and the
  T3 model's train-only imputation statistics (65 tests).
- A ninth audit round verified PR #29 (the soft-partial gating
  matrix exercised end to end, the shrink-ordering change proven
  rollback-safe at byte level, the newly matched fixture's market
  rows reconciled snapshot-for-snapshot) and fixed what it found,
  including one medium defect the previous round's own fix had
  introduced. The refresh rollback's created-file deletion could
  remove pre-existing raw season CSVs: it told run-created files
  from old ones via an existence map that was only filled
  incrementally inside the step's error handling, after the initial
  stats call and the ordered backups, so a failure before or during
  the backup phase left later files unrecorded and the rollback
  deleted them — every raw file when the stats call itself raised,
  in a run that had overwritten nothing. The map is now completed
  before the step's fallible work begins. The refresh's post-commit
  work (loader reload, records rebuild) is guarded: an exception
  there previously escaped after the new data was committed and the
  backups discarded, and now returns a failed step result marked
  `committed` instead. The model-fit rollup reports failure when
  zero divisions entered it, the incremental run's aggregation
  applies the same soft-partial rule as the full pipeline, and
  `prepare.py`, `clean.py`, and `model_corners_v3.py` take their
  directories from `paths` like `download.py` does (each keeps its
  hardcoded path as an out-of-tree fallback). Three unit tests
  added.
- An eighth audit round verified PR #28 end to end (the full rollback
  reproduced in a stubbed sandbox, the 9 newly graded TipsterArea bets
  re-settled independently, the calibration summary recomputed
  digit-for-digit, CI green) and fixed the low-severity residue, most
  of it about signal honesty. The cup step now honors the failure
  status `predict_cups` returns, so the weekly cups-to-picks gate can
  trip; a step that raises an exception is named in `failed_steps`
  and in `last_full_pipeline.json` instead of leaving the list empty;
  and a `partial` from the model or odds step no longer blocks
  dependents or fails the run — it is recorded as `partial_steps`
  (the model step now reports `partial` when only some divisions fail
  to fit, since the failed divisions keep their previous valid
  state). Backup and stat calls in the training refresh moved inside
  its error handling, rollback deletes files the failed run itself
  created, backup timestamps carry microseconds so same-second runs
  cannot share a backup name, and leftover xG dump backups from older
  runs are swept. A legitimate football-data correction that shrinks
  one division can be accepted once with `REFRESH_ACCEPT_SHRINK=1`
  instead of failing every weekly refresh forever. The build-xG step
  snapshots `xg_matches.csv` and restores it when a build comes back
  degraded, `download.py` takes its output directory from
  `paths.RAW_DIR` instead of a second hardcoded copy, and the fixture
  matcher accepts an exact-name pair at ±2 days when the candidate is
  unique (a 2-day date disagreement between the Understat dump and
  TipsterArea had left Lorient vs Brest permanently unmatched); the
  fuzzy rescue stays at ±1 day. Five unit tests added.
- A seventh audit round verified PR #27 (the incomplete-download gate
  and the records-meta merge both reproduced in isolation, and the
  day's recommendation files recomputed exactly) and fixed what it
  found, mostly about failure honesty in the full pipeline. The
  training refresh now backs up and rolls back everything it
  overwrites — raw season CSVs, `all_matches.csv`, and the Understat
  dumps, not just `all_matches_clean.csv` — stops before `prepare` /
  `clean` when the download is incomplete, checks row counts per
  division instead of only in aggregate, and rotates backups on the
  failure path too. `run_full_pipeline` skips steps whose upstreams
  failed instead of letting them overwrite state and predictions on
  stale inputs, counts module-missing skips as failures, runs the
  corner step after scoring so its staleness guard reads the current
  run's predictions, and records each run's outcome in
  `last_full_pipeline.json`, which `/api/status` exposes. The records
  meta merge moved into `cache_records` itself, so the daily
  `make_picks_live` rebuild path can no longer wipe the fingerprint
  and trigger an extra rebuild. The daily shadow tees its output to
  `logs/shadow-<date>.log` and finally calls `ta_model.grade()`, which
  no chain had ever invoked, leaving TipsterArea bets ungraded for
  weeks. Remaining local-date anchors on UTC-dated fixtures (slip
  recommender, best picks, market compare/archive defaults, the odds
  endpoint) now use the UTC date, the season label is month-aware
  instead of raw calendar year, the safest-pick tie-break treats a
  missing `ev_model` as worse than a negative one, the build-xG step
  surfaces corrupt dumps, the odds step returns a real status, and
  the calibration summary adds `overall_unique` (final legs
  deduplicated per selection) beside the per-product leg count.
  Seven unit tests added.
- A sixth audit round verified PR #26 (the fixture rescue survived a
  full-file stress test: four independent computations over all 1,349
  predictions, zero changed assignments, every rescued row a genuine
  name variant) and fixed what it found, most of it around the weekly
  refit. The training refresh now fails and rolls back when the
  football-data download is incomplete instead of reporting success
  on stale data, and the records-cache metadata has a single schema:
  the orchestrator merges its fingerprint into the meta that
  `cache_records` writes instead of overwriting it and erasing the
  `data_stamp` the daily chain checks, which had caused a second full
  records rebuild every active week. Backups from the refresh are
  rotated (newest 3). Cup fixtures are selected on the UTC date like
  the league path, the market-sync and market-compare paths prefer a
  cup row's stored `game_id`, the safest-pick tie-break falls through
  to `ev_model` for model candidates, `ModelState.is_stale` measures
  from `updated_at` instead of the fit horizon (and `n_matches_trained`
  is recorded for batch fits), the xG map is loaded once per
  prediction run instead of once per division-month group, and
  `weekly_refit.sh` is executable.
- A fifth audit pass verified the fourth round's fixes and closed the
  last two items the audit series had deliberately left open. Cup
  picks now carry the TipsterArea `game_id` from `predict_cups`
  through `best_picks_today.csv` into the ledger sync, which prefers
  the stored id over its fuzzy fixture guess (archived files fall back
  to the guess), and the fixture matcher rescues name variants its
  exact-key index used to miss entirely — one side identical after
  normalization, the other at similarity 0.85 or better — recovering
  fixtures such as Nottingham Forest and Internazionale that silently
  lost market data. `score_ledger` runs its pipeline inside `main()`
  instead of at import time, so its settle rules are unit-testable
  (three tests added; importing the module writes nothing and no
  longer raises `SystemExit` without a ledger), with subprocess
  output proven byte-identical on the real ledger. Smaller fixes: the
  shadow prints `failed_dates` next to `empty_dates` and surfaces
  partial results-sync failures from stderr, and `fetch_xg`'s dormant
  remote merge joins on the same name pipeline as the local map
  (158/158 mapped pairs, up from 142). The experiments README now
  notes that its scripts predate the Pinnacle column rename.
- A fourth audit pass closed the gaps the third one left. The
  historical CLV headline now matches the Pinnacle-first hierarchy it
  always claimed: `score_ledger --recompute-clv` restates the stored
  close/CLV fields (settlement untouched), moving the 358-grade
  headline from the average-close figures (EV -0.0597, beat-close
  57.5%) to Pinnacle-true ones (EV -0.0773, beat-close 53.6%).
  `backtest_value` resolves Pinnacle closing columns per row (PP*
  first), so the current season is no longer silently excluded from
  value backtests. `/api/status` serves its data section from a
  TTL-cached match cache instead of blocking ~2s per call.
  `grade_recommendations` refreshes pending rows when an archive is
  regenerated and only prunes a pending leg once its match has a
  result, so a postponed match cannot be pruned on archive loss.
  Smaller items: `settle` validates 1X2 sides and labels quarter-line
  half outcomes, the cup close proxy requires snapshots before
  kickoff (not just an NS flag), the shadow checks corner-file
  freshness like the orchestrator does, and `best_picks` writes its
  CSVs atomically.
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
- A third audit pass fixed the scraper's price alignment at the
  root: the match-page parser only captured cells whose class was
  exactly `odd`, missing about 18% of numeric prices (bold and
  moved-price variants) and letting surviving prices shift onto the
  wrong selections. Cells are now captured by class prefix, and
  no-odds placeholders hold their position instead of shifting the
  row. Replaying the cached pages recovers roughly 9% more priced
  rows than the guarded parser, all correctly aligned. The slip
  unit key entry above also needed completion: the unit's key date
  now comes from the slip's own legs, not the archive date, so the
  same physical slip can no longer be counted twice.
- Cup picks entering the money ledger are translated from the
  `1`/`X`/`2` side vocabulary to the ledger's `H`/`D`/`A` (the
  first 1X2 cup pick would previously have been graded an automatic
  loss), must clear a non-negative edge floor, and are deduplicated
  per match and market instead of per selection. `score_ledger`
  settles quarter Over/Under lines as split stakes, no longer
  grades an Over/Under pick's CLV against the 2.5 closing pair when
  the pick carries another line, and skips a pick with an unknown
  market instead of aborting the whole grading run.
- football-data renamed its Pinnacle columns from `PS*` to `PP*`
  in the 2026-27 files; every closing-odds reader now tries `PP*`
  first. Without this the current season's Pinnacle closing prices
  were silently empty and the "Pinnacle-first" benchmarks and CLV
  chain quietly ran on average prices instead.
- Reported numbers that were not what they claimed: `best_picks`'
  `ev_model` was identically zero by construction and is now
  computed from the Bet365 prices in the prediction rows (left
  empty where no price exists), and the backtester's default
  `meta` model silently graded pure Dixon-Coles probabilities and
  now resolves to the actual meta model. The Asian-handicap
  evaluation scores against the exact expected payoff instead of
  the `pw + 0.5*pp` approximation, and the feature Elo is zero-sum.
- Freshness and time discipline: the records cache carries a
  training-data stamp and is rebuilt after a data refresh, the
  match cache requires a format version plus the source file's
  stamp, `ta_model` ignores quotes captured at or after kickoff
  and never creates bets for matches that already started,
  "latest quote" comparisons parse timestamps instead of comparing
  strings across mixed UTC offsets, and fixture date filters
  compare against the UTC date. Remaining full-file rewrites
  (shadow ledger, calibration summary, recommendation files) are
  atomic, orphaned pending calibration rows are pruned, and the
  orchestrator's `--predict-only`/`--update-data` modes exit
  non-zero on failure like the other modes.

### Removed

- The legacy exogenous-enrichment cluster (`enrich_pipeline.py`,
  `data_enrichment/fetch_xg.py`, `data_enrichment/fetch_closing_odds.py`,
  `data_enrichment/synthesize_european.py`): no production module
  imported it and its output file was read only by experiments.
  `data_enrichment/utils.py` and `build_xg_matches.py` are live and
  remain.
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
