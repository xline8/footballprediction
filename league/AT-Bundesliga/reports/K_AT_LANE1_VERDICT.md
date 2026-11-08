# K-AT-L1 Verdict — Lane 1 re-entry of AT-Bundesliga cards (yellows), arm X8

Date: 2026-11-11. Branch `build/lane1-kat`. Prereg:
`league/AT-Bundesliga/prereg/PREREG_L1_K_AT.md`, **prereg commit
39b18fec** (the branch's first commit, before any sealed access).
Dev evaluation commit f0748dd2 (dev-pass token recorded there, before
the sealed read). Run script:
`league/AT-Bundesliga/engine/cards/run_lane1.py`, executed under
`league/gate_lib/` guards. Original candidate:
`league/AT-Bundesliga/reports/K_AT_VERDICT.md` (FAIL at the dev gate,
sealed window never read).

## Verdict: FAIL — at the sealed legs. Nothing ships.

X8 reproduced its documented dev pass exactly and was read once on
the sealed window 2025/2026 (n=195). On that window it **loses leg
(i)** — its LL@4.5 (0.6569) is worse than Gate Zero's (0.6509) and
worse than the league base rate (0.6503), beating only naive
trailing-10 (0.6646) — and **fails leg (ii) outright**: calibration
is +7.25pp (predicted − actual), SE 3.42pp, far beyond the 1.0pp
tolerance and beyond the 1 SE provisional boundary (4.42pp). Leg
(iii), the dev sign check, passes 3/3, but legs are conjunctive:
FAIL, verdict final, no iteration against the window.

No runner-join change is prepared (join prep is PASS-only), and the
referee operational gate is not run (it gates shipping, and nothing
ships).

## Dev results — reproduced (scored 2022/2023–2024/2025, n=585)

Gate_lib dev evaluation re-ran the league engine on dev data only
(the dev loader's season set excludes 2025/2026 and 2026/2027 in
code; `assert_no_sealed_rows` double-checked). The recomputation
reproduces the original verdict's numbers within artefact rounding
— the regenerated `results_dev.json` is byte-identical to the
committed artefact:

LL@4.5, pooled dev:

| Arm / baseline | Recomputed | Documented | Reproduced |
|---|---|---|---|
| X8 (arm of record) | 0.6561 (0.6560816) | 0.6561 | yes |
| Gate Zero (baseline only) | 0.6654 (0.6654252) | 0.6654 | yes |
| League base rate | 0.6803 (0.6802749) | 0.6803 | yes |
| Naive trailing-10 | 0.6636 (0.6636086) | 0.6636 | yes |

Dev gate (arm of record beats BOTH baselines): **PASS** —
0.6561 < 0.6803 and 0.6561 < 0.6636. Dev-pass token for `K-AT-L1`
recorded in `engine/cards/lane1_dev_pass_registry.json` before the
sealed read.

Per-season dev LL@4.5 (X8 vs Gate Zero): 2022/2023 0.6488 vs 0.6527;
2023/2024 0.6645 vs 0.6779; 2024/2025 0.6550 vs 0.6657 — sign check
leg (iii): X8 ≤ Gate Zero in **3 of 3** dev seasons, PASS.

## Sealed results — the single read (2025/2026, n=195)

Loaded once through gate_lib's fail-closed `load_sealed_rows`
(which asserted the recorded dev-pass token first), online
walk-forward continuing from the dev end state. Full numbers in
`engine/cards/results_virgin_lane1.json`; arm-of-record predictions
in `predictions/k_at_lane1_virgin_predictions.csv` (evidence of the
read, not a shipped product).

LL@4.5 on the sealed window:

| Entity | LL@4.5 | Mean P(over 4.5) |
|---|---|---|
| **X8 (arm of record)** | **0.6569** (0.6569361) | 0.4161 |
| Gate Zero (baseline) | 0.6509 (0.6509299) | 0.4109 |
| League base rate | 0.6503 (0.6502995) | — |
| Naive trailing-10 | 0.6646 (0.6646256) | — |

Actual over-4.5 rate on the window: 0.3436 (the dev pooled actual
was 0.4239 — the sealed season's card level fell well below the dev
regime, and every arm over-predicted it; that level miss is what
both failing legs are made of).

| Leg | Result |
|---|---|
| (i) X8 LL ≤ Gate Zero's AND ≤ best baseline's | **FAIL** — 0.6569 > 0.6509 (GZ) and > 0.6503 (base rate, the best baseline); beats naive only |
| (ii) Calibration \|predicted − actual\| ≤ 1.0pp (clean) / within 1 SE (provisional) | **FAIL** — +7.25pp, SE 3.42pp; provisional boundary is 4.42pp (gate_lib `calibration_band`: FAIL). Gate Zero itself is +6.73pp (SE 3.41pp) — also FAIL band |
| (iii) Dev sign check ≥ half the dev seasons | PASS — 3/3 |

Referee coverage on the sealed window: 179/195 = 91.8% (matches the
figure published in the original verdict). X8 fallbacks on the
window: 16 unknown-identity, 8 thin-history — those fixtures took
the Gate Zero prediction, per the no-imputation rule.

## P6 worst-fold block

### P6 worst-fold block — AT-Bundesliga cards (primary metric: ll_4.5)

Source: `league/AT-Bundesliga/engine/cards/results_dev.json` (persisted dev artefacts; information only — no gate change).
Worst dev season (highest ll_4.5 for the reference arm): **2023/2024**.

| Entity | Pooled ll_4.5 | Pooled source | Worst-season (2023/2024) ll_4.5 | n (worst) | Δ vs pooled |
|---|---|---|---|---|---|
| gate_zero | 0.6654 | n-weighted, computed | 0.6779 | 195 | +0.0124 |
| gate_zero [base] | 0.6803 | n-weighted, computed | 0.6834 | 195 | +0.0032 |
| gate_zero [naive] | 0.6636 | n-weighted, computed | 0.6785 | 195 | +0.0149 |
| x8 | 0.6561 | n-weighted, computed | 0.6645 | 195 | +0.0084 |

Reading (added for this verdict): X8 wins even the worst dev fold
(0.6645 vs Gate Zero 0.6779, base 0.6834, naive 0.6785), so the
sealed failure is not a pooled margin resting on one easy dev
season — it is the sealed season's own level drop, which no dev
fold shows.

## Verification notes

- Dev reproduction: byte-identical `results_dev.json`; all four
  pooled numbers within 5e-5 of the documented values.
- Sealed cross-check: the sealed walk-forward was recomputed with
  the league's original harness (`virgin_metrics()`, run in a /tmp
  copy because that code path overwrites the verdict file) — X8
  LL@4.5 0.6569360670769957, calibration +0.0725444 (SE 0.0342387),
  coverage 179/195, fallbacks 16/8: identical to this run's
  gate_lib numbers to every printed digit.
- The original harness's own virgin verdict writer cannot be used:
  it crashes with `KeyError: 'gate_zero'` whenever Gate Zero is not
  itself a dev-passing arm, and its calibration token merges the
  clean/provisional boundary (`|diff| ≤ 0.01 + SE`) — the §5.6-class
  virgin-leg token divergence the cohort report recorded for this
  candidate. All leg arithmetic here is gate_lib's. Note the crash
  and the token change nothing: even under the harness's merged
  token, +7.25pp > 1.0pp + 3.42pp, so calibration fails under either
  reading, and leg (i) fails independently.
- The engine's NB r estimates at the capped 500.0 for all methods in
  both windows, exactly as in the original documented run — the
  reproduction target — and is unchanged by this entry.
