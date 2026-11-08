# G-BRC verdict — FAIL at the dev gate — virgin NOT read

## Dev results (season-blocked walk-forward, fit-set matches only)

Pooled dev n = 856 (2022–2025, 214 per season). Climatology =
expanding prior-seasons-only fit-set rates.

| Arm / baseline | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero (pooled) | 1.061084 | 0.214934 | 0.689712 |
| Climatology (pooled) | 1.050133 | 0.211964 | 0.677470 |
| SHRINK (pooled) | 1.061084 | 0.214934 | 0.689712 |
| X2 (pooled) | 1.062083 | 0.215296 | 0.686804 |

Gate Zero fails all three dev-gate comparisons (1X2 LL +0.010951,
RPS +0.002970, OU2.5 LL +0.012242 vs climatology/base rate). Per the
frozen prereg, variants are moot: SHRINK and X2 are dead with it,
and the virgin (2026) is NOT read. No virgin parameters, metrics,
or predictions exist; no `results_virgin.json`, no
`fitted_params_virgin.json`, no `predictions/` directory.

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | Gate Zero | Climatology |
|---|---|---|
| 2022 | 1.048850 / 0.217468 / 0.689810 | 1.037523 / 0.214106 / 0.712789 |
| 2023 | 1.067313 / 0.214224 / 0.703201 | 1.056192 / 0.212942 / 0.660288 |
| 2024 | 1.034647 / 0.206713 / 0.707891 | 1.035878 / 0.207060 / 0.694231 |
| 2025 | 1.093527 / 0.221331 / 0.657946 | 1.070939 / 0.213746 / 0.642572 |

Gate Zero beats climatology on 1X2 LL in only one dev season
(2024, by 0.001231) and on OU2.5 LL in only one (2022). The
failure is broad, not a gate-edge call: every pooled leg fails by
0.003–0.012, and 2025 — the low-goals year (2.00/match) — is the
worst season for the model on all three metrics.

## Arm notes

- **SHRINK is identical to Gate Zero** (0 of 2,568 scored
  match-arms differ in lambdas). This is genuine, not a bug: the
  prior-match-count buckets for target-season teams are only `0`
  or `6+` in every dev season (2022: 12×6+, 8×0; 2023: 12×6+,
  8×0; 2024: 15×6+, 5×0; 2025: 14×6+, 6×0) — no team ever sits
  in the 1–5 window where SHRINK bites, because teams arrive with
  either a full prior season (13+ recorded matches) or no
  in-league history at all (and n=0 is identical to Gate Zero's
  unseen rule by design). The G-J2 thin-data lesson has no
  exposure to act on in this league.
- **X2 is live but does not rescue the gate**: its lambdas differ
  from Gate Zero on 554/856 matches (140/142/136/136 per season
  — every match involving a first-season mover), yet its pooled
  1X2 LL (1.062083) and RPS (0.215296) are marginally worse than
  Gate Zero's, and its OU2.5 LL (0.686804), while better than Gate
  Zero's, still loses to the base rate (0.677470). Per-season sign
  check vs Gate Zero: 2/4 (2023, 2025) — passes the ≥half rule,
  but moot: the dev gate is failed. The pooled mover offsets are
  small (ex-B dGF −0.04, newcomers −0.06) and their per-season
  signs flip; the gate, not optimism, decides.

## Verification (independent of the engine's own output)

- Recomputed all pooled and per-season LL/RPS/OU values from
  `results_dev_predictions.csv` (2,568 rows) through a second
  script: exact match to 6 decimal places on every number above.
- DC fidelity: the engine's `dc.py` diffs identical to
  `league/BR-SerieB/engine/goals/dc.py` except its docstring, and
  a replay of the production `model_v2.py` DC class on the 2021
  fit (147 matches, cutoff 2022-04-09, hl=270, goals-only)
  reproduces the engine's fitted ratings, home advantage
  (h = 0.352869), rho (−0.10), and lambdas with max difference
  0.00e+00. The failure belongs to the reference pattern in this
  league, not to the copy.
- Dev determinism: two full `run_g_brc.py dev` runs produce
  byte-identical `results_dev.json` and
  `results_dev_predictions.csv`.
- Virgin isolation: the dev loader allows seasons 2021–2025 only
  and `run_dev` asserts no 2026 row is loaded; the predictions
  file contains exactly 642 rows per season for 2022–2025 and no
  2026 season value (the substring "2026" occurs only inside
  probability decimals). `virgin-metrics` / `virgin-predict` were
  never run.
- Mover sets: derived by team id from the two leagues' analysis
  CSVs and asserted equal to the frozen prereg lists for
  2022–2025 (the run raises on any mismatch; it did not raise).

## Diagnosis

The unmodified Dixon-Coles pattern cannot beat climatology in
Série C on this window — the same outcome as G-BRB (Série B),
whose Gate Zero also failed all three dev comparisons. Plausible
contributors, stated as observations not excuses: the 2021 seed
is a partial season (147/206 matches, rounds 2–3 heavily
missing); era drift is material (goals/match 2.42 in 2024 →
2.00 in 2025, the model's worst season); and with 20 teams
playing 19 first-phase rounds, ratings have thin histories at
each season start. Nothing in the dev evidence suggests a
rescue arm within this prereg, and post-hoc arms are forbidden.

## Verdict

**G-BRC: FAIL.** Nothing ships. BR-SerieC is now fully complete
as a league: 1 candidate through its gate (FAIL) + 4 candidates
NOT BUILDABLE (S/C/K/T — no target exists in any season).
