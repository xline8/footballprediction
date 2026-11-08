# Brief — P5 shared gate library + Gate Zero reproduction test

Repo: ~/workspace/footballprediction (work in place; NEVER git commit, NEVER push).
Python: .venv/bin/python. Read first: league/AUDIT.md §5.7, §5.9, §5.11, §5.12, §6 (P5 paragraph);
league/IMPROVEMENT_PROGRAM.md (P5 line). This builds the P5 workstream of the improvement program.

## Deliverable 1 — package league/gate_lib/

Pure-stdlib Python package (no new dependencies), documented, with modules:

1. `sealed_guard.py` — Dev-pass assertion / sealed-data loader.
   - `DevPassRegistry`: tokens are recorded in a JSON registry file: candidate id ->
     {dev_pass: bool, dev_results_sha256 or source path, recorded_at}. Provide
     `record_dev_pass(registry_path, candidate_id, dev_pass, evidence)`.
   - `load_sealed_rows(csv_path, candidate_id, registry_path, virgin_season=None)`:
     REFUSES (raises `SealedAccessError`, fail-closed) when: registry missing/unreadable,
     candidate absent, dev_pass is not exactly True. Only on a valid token does it read
     the CSV and return rows. Also provide `assert_no_sealed_rows(rows, sealed_seasons)`
     helper for dev loaders (raises if any row's season is in the sealed set).
2. `prereg.py` — Mechanical prereg parsing. `parse_prereg(path) -> PreregSpec` dataclass with:
   primary_line (float), ladder (list[float]), calibration_tolerance_pp (float, default
   search for "1.0pp"/"≤ 1.0pp" patterns; record raw matched text), sign_convention_stated
   (string: "predicted_minus_actual" / "actual_minus_predicted" / None, from text search),
   baselines (list of names found: e.g. league base rate / climatology, naive trailing-10),
   virgin_season (from the league's config.yaml `virgin_primary` if a config path is given,
   else None), gate_text (the verbatim GATE LEGS section excerpt if present).
   Extraction must be regex/text based over the actual prereg files — varied real formats:
   "Primary line: **24.5**", "Primary line **3.5** (dev over-rate ...)", "- **Primary line: 24.5**",
   "Primary line **2.5**, secondary ...". Ladder from "Ladder 3.5/4.5/5.5" / "23.5 / 24.5 / 25.5" near
   the primary-line mention. If a token cannot be found, set None and add to `missing_tokens`
   (never guess). `load_config(path)` minimal YAML-subset reader for virgin_primary +
   halves_constants (the config files are simple; do NOT add a yaml dependency if PyYAML is
   unavailable in .venv — check first; a tiny subset parser is fine).
3. `constants.py` — Template-constant derivation (M_BAR class).
   - `derive_level_prior(values) -> float` = arithmetic mean of the league's own dev values.
   - `derive_half_share(first_half, full_time) -> float` = sum(1h)/sum(FT).
   - `CandidateSpec` dataclass: league, candidate, constants dict {name: {value, derivation}}
     where derivation is None or {method, source, n}.
   - `check_constants(spec, other_specs) -> list[Finding]`: flag any constant whose value
     exactly equals another league's constant for the same name AND has no derivation record
     (the J1-copy failure mode, AUDIT §5.9: M_BAR=24.9 in ~45 engines). Also flag constants
     with no derivation record at all as a warning.
4. `metrics.py` — ONE calibration sign convention: predicted − actual, everywhere.
   - `log_loss(p, y)` (clip p to [1e-12, 1-1e-12] — note: check whether shipped artefacts
     used clipping; for reproduction of persisted values use unclipped-safe computation and
     document), `calibration(p_list, y_list) -> (diff_pp, se_pp)` with diff = mean(p) −
     actual_rate in percentage points and SE = sd(p_i − y_i, ddof=1)/sqrt(n) in pp,
     `pooled_ll(season_rows)` = n-weighted mean of per-season LLs,
     `calibration_band(diff_pp, se_pp, tol_pp=1.0) -> "PASS"|"PROVISIONAL"|"FAIL"`
     (|diff|<=tol → PASS; elif |diff| <= tol + SE → PROVISIONAL; else FAIL),
     `sign_check(per_season_ll_arm, per_season_ll_ref) -> (wins, n, passed)` with the frozen
     rule wins >= ceil(n/2) where a win is arm LL <= ref LL.
5. `reproduce.py` — generic artefact readers used by the Gate Zero runner:
   normalisers that extract, from the heterogeneous persisted formats, per candidate:
   (a) dev per-season + pooled LL at a given line for arms and baselines from
   results_dev.json (schemas in the wild: {"protocol","rows":[...]} list rows with
   ll_<line>/oull_2_5/ll_1x2 fields and arm/kind/season; {"arms": {name: {"seasons": {...},
   "pooled": {...}}}}; {"metrics": ...}; goals rows carry ll_1x2/rps/oull_2_5);
   (b) sealed aggregate metrics from results_virgin.json (same schema variety, incl.
   {"gate_zero": {...ll_<line>, calibration_diff, calibration_se});
   (c) per-match sealed recompute from a virgin predictions CSV: given the primary line,
   find the p_over column (patterns: p_over_<line with .->_>, ft_p_over_<line>,
   p_over_<line>) and the actual column (actual_total / actual_total_sot /
   actual_target / actual_corners_total / home_goals+away_goals for goals /
   for J1 cards: NO actual column — join league/J1/data/j1_matches.csv on match_id,
   actual = yellow_cards_home + yellow_cards_away; determine the cards target from the
   prereg text). Group by `arm` column when present; the shipped/reference arm is the one
   named in results_virgin.json (shipped_arm / read_arms / export_arm) or gate_zero.
   Every normaliser returns None-fields rather than raising when a schema piece is absent,
   so the runner can record "not reproducible from artefacts" per leg.
6. `__init__.py` exporting the public API; `README.md` in league/gate_lib/ stating the four
   guards (dev-pass assertion, mechanical prereg tokens, derived template constants, one
   sign convention predicted − actual) and how a future build consumes each one.
7. `tests/` — a small self-test script `league/gate_lib/tests/run_tests.py` (plain asserts,
   runnable with .venv/bin/python) covering: guard refuses without token and accepts with
   one; parser on at least 3 real preregs returns the known primary lines (T-J1 24.5,
   K-J1 2.5, K-AE 3.5); calibration sign (p all 0.6, y all 0 → +60pp... use a small exact
   example); constants checker flags a copied 24.9 with no derivation and passes a derived one.

## Deliverable 2 — Gate Zero runner + outputs

Script: league/improvement_scratch/P5/run_gate_zero.py — imports ONLY league/gate_lib for
gate arithmetic (plus stdlib). It must, for each sampled candidate below:
- parse the prereg via gate_lib (primary line from the parser, never hard-coded in the runner);
- recompute dev legs from results_dev.json: pooled LL@primary per arm + both baselines,
  dev_pass per arm (arm pooled LL strictly < both baselines); for goals candidates also the
  1X2 LL and RPS pooled legs where the artefacts carry them;
- recompute the per-season sign check where per-season LLs exist (variant arms vs the
  reference arm = Gate Zero / arm A analogue per the prereg/verdict);
- recompute sealed legs: FIRST from the per-match virgin CSV via gate_lib.metrics
  (LL@primary, calibration diff pp under predicted − actual, SE pp, band) for the shipped/
  reference arm; ALSO read the persisted results_virgin.json aggregates for all arms/
  baselines and recompute leg (i) (virgin LL <= reference arm and <= best baseline) and
  leg (ii) banding from those aggregates translated to the library sign convention
  (note each artefact's own stored sign convention where the JSON states one —
  "sign_convention" fields exist in some; verdicts state others);
- compare every recomputed value against the SHIPPED value (results_*.json full precision
  is the primary comparison target; verdict .md stated values are secondary, rounded).
- Emit league/improvement_scratch/P5/reproduction.csv with columns:
  candidate,league,market,leg,arm,value_recomputed,value_shipped,abs_delta,match,source
  (source = per_match_csv | dev_aggregate | virgin_aggregate), notes.
- FLOATING-POINT CRITERION (state it in the report): match iff abs_delta <= 5e-7 for
  full-precision JSON comparisons; for per-match CSV recompute vs JSON, CSVs carry ~16
  significant digits so the same 5e-7 criterion applies; verdict-text values compare after
  rounding recomputed to the verdict's printed precision.

### Sample (10 candidates — fixed, do not change except the substitution rule below)
1. T-J1  — J1 total_shots, PASS provisional. prereg league/J1/prereg/PREREG_T_J1.md,
   engine league/J1/engine/total_shots/, virgin CSV league/J1/predictions/t_j1_virgin_predictions.csv
2. S-J1  — J1 sot, PASS clean. PREREG_S_J1, engine/sot, s_j1_virgin_predictions.csv
3. K-J1  — J1 cards, FAIL sealed (virgin LL leg). PREREG_K_J1, engine/cards,
   k_j1_virgin_predictions.csv (actuals via j1_matches.csv join — see above)
4. G-SCO — SCO-Premiership goals, PASS provisional. league/SCO-Premiership/prereg/PREREG_G_SCO.md,
   engine/goals, predictions/g_sco_virgin_predictions.csv
5. G-TR  — TR-SuperLig goals, PASS provisional. league/TR-SuperLig/prereg/PREREG_G_TR.md,
   engine/goals, predictions/g_tr_virgin_predictions.csv
6. T-GR  — GR-SuperLeague total_shots, PASS clean (AUDIT §5.12 sign case: harness returned
   predicted−actual against prereg's actual−predicted — your report must address the sign
   explicitly). league/GR-SuperLeague/prereg/PREREG_T_GR.md, engine/total_shots,
   predictions/t_gr_virgin_predictions.csv
7. S-LV  — LV-Virsliga sot, PASS clean. league/LV-Virsliga/prereg/PREREG_S_LV.md,
   engine/sot, predictions/s_lv_virgin_predictions.csv (different CSV schema:
   actual_target, p_over_8_5/9_5/10_5)
8. C-GR  — GR-SuperLeague corners, PASS clean. PREREG_C_GR, engine/corners,
   predictions/c_gr_virgin_predictions.csv
9. G-AE  — AE-ProLeague goals, FAIL dev (no results_virgin.json exists — the correct
   reproduction is dev legs + confirmation that no sealed artefact exists / sealed legs
   are absent, which is itself a leg row). PREREG_G_AE, engine/goals.
10. K-AE — AE-ProLeague cards, FAIL dev (same as above). PREREG_K_AE, engine/cards.

Substitution rule (pre-registered): if a candidate's artefacts cannot support recompute of
a leg, first record the leg as NOT_REPRODUCIBLE with the reason; only if a candidate cannot
support ANY leg, replace it with another league in the same stratum and record the
substitution in the report.

## Deliverable 3 — league/improvement_scratch/P5/gate_zero_report.md
Contents: headline verdict (Gate Zero PASS iff every sampled leg that is reproducible
reproduces within criterion — state the criterion and justify it); the sample table
(league, market, shipped outcome); leg-by-leg summary table (counts per candidate:
legs reproduced / mismatched / not reproducible); every mismatch diagnosed as
LIBRARY_BUG (fix + rerun) vs ARTEFACT_INCONSISTENCY (record; shipped verdicts never
change) vs SIGN_CONVENTION (artefact stores actual−predicted; library is predicted−actual;
|diff| and banding unaffected — count these separately and say whether they are mismatches
under the criterion); the constants-guard demonstration (run check_constants over the
sample: e.g. T-J1 M_BAR 24.9 HAS a derivation record in its prereg (≈ dev mean 24.898) vs a
hypothetical undocumented copy — demonstrate on real data where possible); guard
demonstration (show load_sealed_rows refusing K-AE/G-AE (no dev-pass token) and accepting
T-J1 after recording its dev pass from results_dev.json); limitations stated honestly
(e.g. dev legs are recomputed from persisted per-season aggregates, not refits; virgin
per-match CSVs exist only for shipped/reference arms in most leagues, other arms' sealed
legs reproduce from persisted aggregates).

## Rules
- Do NOT modify any existing engine, prereg, verdict, results or predictions file. New files
  only under league/gate_lib/ and league/improvement_scratch/P5/.
- Shipped verdicts NEVER change. No git operations at all.
- Run the tests and the runner; iterate until the runner completes on all 10 candidates.
- Where a schema defeats the normaliser, extend the normaliser generically (no per-league
  if-chains keyed on league name; schema-shape dispatch is fine).
