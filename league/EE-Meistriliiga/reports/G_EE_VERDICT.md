# Verdict — G-EE (EE-Meistriliiga goals) — **FAIL at the dev gate**

No arm passes the dev gate, so the virgin window (2026) was **NOT read**,
no virgin predictions exist, no virgin fit was made, and **nothing ships**.
This is a complete outcome under the frozen preregistration
(`prereg/PREREG_G_EE.md`, committed before any fitting).

## Dev gate (mechanical, pooled dev seasons 2022–2025, n = 720)

An arm passes iff pooled dev 1X2 LL and RPS beat climatology AND OU2.5 LL
beats the base-rate baseline. All three arms pass the first two legs and
fail the third:

| Arm | 1X2 LL | vs clim 1.062183 | RPS | vs clim 0.238943 | OU2.5 LL | vs base 0.695738 | Dev gate |
|---|---:|---:|---:|---:|---:|---:|---|
| Gate Zero | 0.944985 | beats | 0.194538 | beats | 0.712278 | **loses by 0.016540** | **FAIL** |
| SHRINK | 0.944985 | beats | 0.194538 | beats | 0.712278 | **loses by 0.016540** | **FAIL** |
| X2 | 0.934156 | beats | 0.190372 | beats | 0.713264 | **loses by 0.017526** | **FAIL** |

## Dev table (per season, n = 180 each)

| Season | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|---:|
| 2022 | climatology | 1.049031 | 0.239227 | 0.717815 |
| 2022 | Gate Zero | 0.809289 | 0.160437 | 0.715407 |
| 2022 | SHRINK | 0.809289 | 0.160437 | 0.715407 |
| 2022 | X2 | 0.809289 | 0.160437 | 0.715407 |
| 2022 | naive trailing-10 | 0.927039 | 0.193510 | 0.791621 |
| 2023 | climatology | 1.118195 | 0.233366 | 0.726089 |
| 2023 | Gate Zero | 1.136242 | 0.231708 | 0.739999 |
| 2023 | SHRINK | 1.136242 | 0.231708 | 0.739999 |
| 2023 | X2 | 1.101866 | 0.220867 | 0.761309 |
| 2023 | naive trailing-10 | 1.068451 | 0.219128 | 0.715610 |
| 2024 | climatology | 1.066915 | 0.236890 | 0.682314 |
| 2024 | Gate Zero | 0.966563 | 0.198862 | 0.689682 |
| 2024 | SHRINK | 0.966563 | 0.198862 | 0.689682 |
| 2024 | X2 | 0.912058 | 0.181661 | 0.699239 |
| 2024 | naive trailing-10 | 0.946503 | 0.193176 | 0.727977 |
| 2025 | climatology | 1.014592 | 0.246290 | 0.656735 |
| 2025 | Gate Zero | 0.867847 | 0.187146 | 0.704025 |
| 2025 | SHRINK | 0.867847 | 0.187146 | 0.704025 |
| 2025 | X2 | 0.913413 | 0.198524 | 0.677102 |
| 2025 | naive trailing-10 | 0.914092 | 0.203799 | 0.736584 |

Pooled baselines: climatology 1X2 LL 1.062183, RPS 0.238943, OU2.5 LL
0.695738; naive trailing-10 1X2 LL 0.964021, RPS 0.202403, OU2.5 LL
0.742948. The model beats both baselines clearly on 1X2 LL and RPS, and
beats naive on OU2.5 LL — but the gate's OU leg is against the
climatology base rate, and the model loses that leg in three of four
seasons (2023, 2024, 2025) and pooled.

## Why the OU leg fails (diagnostic, not a rescue)

The model's mean P(over 2.5) sits in a narrow 0.50–0.60 band while the
actual over-rate swings with the season goal level (2.544 goals/match in
2023, 3.178 in 2025). Gate Zero mean P(over 2.5) minus actual over-rate,
per dev season: 2022 +5.1pp, 2023 +7.9pp, 2024 −8.1pp, 2025 −15.8pp.
The flat pre-season base rate absorbs the level miss more cheaply in
log-loss than the model's per-match varying totals probabilities. The
1X2 side does not suffer the same fate (mean P(home win) tracks the
actual home-win rate within 8pp in every dev season). No rescue arm was
invented: the preregistration forbids post-hoc arms, and the OU failure
is pooled, not a single-season fluke.

## Arm notes

- **SHRINK ≡ Gate Zero exactly** (max |Δp| = 0.0 across all 720 dev
  matches), as predicted in the design: no team has 1–5 training-window
  matches in any season-blocked fit (entrants have 0, incumbents 28+),
  so the shrinkage factor is 0 on zero ratings or 1.0 everywhere else.
  The G-J2 thin-history mechanism does not occur in this league under a
  season-blocked fit.
- **X2 improves the 1X2 side** (pooled LL 0.934156 vs Gate Zero 0.944985;
  RPS 0.190372 vs 0.194538; better in 2023 and 2024, worse in 2025) but
  its OU2.5 LL is marginally worse than Gate Zero's (0.713264 vs
  0.712278), so it fails the same leg. The per-season sign check (leg
  iii) is moot: no variant reaches the virgin stage.
- **X2 is inactive for 2022** by design (no prior entrant), so all three
  arms coincide that season.

## Virgin window: NOT READ

Per the preregistration, the virgin (complete 2026, 180 matches) is read
once and only for dev-passing arms. No arm passed dev, so 2026 was not
read by any fitting, prediction, or diagnostic code in this build. The
dev harness loads seasons 2021–2025 only; the delivered
`predictions_dev.csv` contains 2,160 rows (720 matches × 3 arms) from
2022–2025 and zero 2026 rows.

## Verification (coordinator, independent of the implementation)

- Pooled metrics recomputed from `predictions_dev.csv` with a separate
  code path: Gate Zero LL 0.944985 / RPS 0.194538 / OU LL 0.712278;
  X2 LL 0.934156 / RPS 0.190372 / OU LL 0.713264 — identical to
  `results_dev.json` to 6dp. Honest pre-season climatology recomputed
  independently: OU LL 0.695738, 1X2 LL 1.062183 — identical, so the
  baseline carries no lookahead.
- Engine reviewed line-by-line: decay, rho grid, tau correction,
  attack/defence updates, score-matrix normalisation, X2 offsets
  (frozen per-season table, 2022 inactive), SHRINK definition, RPS and
  OU LL formulas all match the preregistration and the production
  `model_v2.py` pattern. Defence-sign and X2-offset synthetic checks
  pass. Harness rerun is byte-identical (deterministic).
- Fits: rho 0.0 (2022), 0.0 (2023), −0.15 (2024), −0.10 (2025); fitted
  home advantage 0.133 / 0.204 / 0.179 / 0.094; training sizes
  156 / 336 / 516 / 696.

## What ships

Nothing. G-EE is FAIL. The engine and dev results are committed as the
audit record; no fitted virgin parameters and no virgin predictions
exist. S-EE, C-EE, T-EE and K-EE remain NOT BUILDABLE (see their verdict
files). EE-Meistriliiga is complete: 0 pass / 1 fail / 4 not buildable.
