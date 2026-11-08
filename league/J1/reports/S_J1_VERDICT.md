# S-J1 Verdict — J1 shots-on-target model

Date: 2026-11-09. Branch `build/s-j1`. Prereg:
`league/J1/prereg/PREREG_S_J1.md` (commit 30a5079, frozen before any
fitting). Engine: `league/J1/engine/sot/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced by the coordinator's own rerun, and the shipped arm's
virgin predictions were recomputed independently from the
production `model_sot.py` v5 code (see Verification notes).
Predictions-only product: no J.League SOT odds source exists
in-system — expected, not a defect.

## Verdict: PASS — Gate Zero ships; all three variant arms fail

Gate Zero (the unmodified v5 pattern) passes the dev gate and both
virgin legs and ships. RS, X4 and X6 each pass the dev gate (X6 on
its era folds) and the per-season sign check, and their calibration
breaches are within tolerance — but every variant's virgin LL@8.5 is
worse than Gate Zero's, so each fails virgin leg (i). Under the
frozen both-pass rule the only passing arm is Gate Zero, and it
ships. The virgin predictions CSV on file is the Gate Zero product,
labelled `arm = GZ`.

## Dev results (per-match walk-forward, scored 2022–2025, n = 1,372)

LL@8.5 (binary log-loss on P(over 8.5); lower is better):

| Season | n | Gate Zero | RS | X4 | X6 | Base rate | Naive t-10 |
|---|---|---|---|---|---|---|---|
| 2022 | 306 | 0.6753 | 0.6748 | 0.6746 | 0.6746 | — | — |
| 2023 | 306 | 0.6541 | 0.6524 | 0.6543 | 0.6543 | — | — |
| 2024 | 380 | 0.6751 | 0.6754 | 0.6770 | 0.6770 | — | — |
| 2025 | 380 | 0.6583 | 0.6575 | 0.6559 | 0.6567 | — | — |
| **Pooled** | 1372 | **0.6658** | **0.6652** | **0.6655** | 0.6658 | 0.6864 | 0.6714 |

X6 is identical to X4 in 2022–2024 by construction (era guard: the
xGOT trait cannot activate before 2025) and is judged for the dev
gate on its era folds only — season 2025 (n = 380): X6 0.6567 vs
Gate Zero 0.6583, base rate 0.6665, naive 0.6597.

Dev gate (pooled LL@8.5 must beat BOTH baselines): Gate Zero
**PASS** (0.6658 < 0.6864 and < 0.6714). RS **PASS** (0.6652).
X4 **PASS** (0.6655). X6 **PASS** on era folds (0.6567 < 0.6665
and < 0.6597). All four arms were therefore read on the virgin
window. On dev the variants are marginally ahead of Gate Zero —
RS by 0.0006, X4 by 0.0003 pooled — well inside noise, and the
virgin window reverses the ordering.

## Virgin results (season "2026", n = 200, read once after dev froze)

Actual over-8.5 rate 42.5%; mean total SOT 8.165.

| Arm | LL@8.5 | Mean P(over 8.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | **0.6815** | 42.20% | −0.30pp | 3.50pp |
| RS | 0.6819 | 42.16% | −0.34pp | 3.50pp |
| X4 | 0.6831 | 43.60% | +1.10pp | 3.51pp |
| X6 | 0.6883 | 44.72% | +2.22pp | 3.52pp |
| Base rate (baseline) | 0.6821 | 41.44% | −1.06pp | — |
| Naive t-10 (baseline) | 0.6993 | 42.89% | +0.39pp | — |

## Per-leg verdicts

| Leg | Gate Zero | RS | X4 | X6 |
|---|---|---|---|---|
| Dev gate | PASS | PASS | PASS | PASS (era folds) |
| Virgin (i) LL ≤ Gate Zero (0.6815) and ≤ best baseline (0.6821) | PASS | FAIL (0.6819) | FAIL (0.6831) | FAIL (0.6883) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PASS (−0.30pp) | PASS (−0.34pp) | PROVISIONAL PASS (breach 0.10pp ≤ SE 3.51pp) | PROVISIONAL PASS (breach 1.22pp ≤ SE 3.52pp) |
| Virgin (iii) dev sign check vs Gate Zero | n/a | PASS (3/4 seasons) | PASS (2/4 seasons) | PASS (era fold 0.6567 ≤ 0.6583) |
| **Overall** | **PASS — ships** | FAIL | FAIL | FAIL |

Reading of the variants: harder ratio shrinkage (RS) is a wash —
best on dev, a hair worse on the virgin window, exactly what F6's
NOISE verdict on the team SOT-rate trait predicts (there is little
team ratio signal to shrink away, and v5's P = 200 prior already
shrinks hard). The xG/shot quality input (X4) helps on dev,
including the 2025 season, but over-predicts the virgin window
(+1.10pp) and loses leg (i) to both Gate Zero and the base-rate
baseline. Adding the era-guarded xGOT trait (X6) pushes the same
direction further (+2.22pp, worst LL): on this virgin window the
quality traits price in more SOT than J1 actually produced. None
of this reopens any forbidden item; the arms were gated exactly as
registered and they did not pass.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every dev and
  virgin number and the predictions CSV exactly (byte-identical
  result files).
- Independent recomputation: the coordinator re-ran the Gate Zero
  walk-forward using the production `model_sot.py` v5 classes
  (a separate code path from the league engine) and compared all
  200 virgin rows — max abs diff on exp_sot_home, exp_sot_away and
  P(over 8.5) is 7e-15. Five rows were also printed and checked
  individually, including the 1H ladder: CSV 1H P(over 3.5) equals
  NB(0.448 · exp_total, r = 79.94) recomputed by hand.
- Virgin isolation confirmed in code: the dev path loads only
  seasons 2021–2025; season "2026" is touched only by the virgin
  step, which reads only dev-passing arms.
- Era-guard correctness for X6, three ways: (1) code — xGOT keys
  are only populated for matches dated ≥ 2025-01-01 in the loader
  and only era matches enter the trait history; (2) empirical —
  the trait history built over the full corpus contains 1,159
  era entries, minimum date 2025-02-14, zero pre-2025 entries;
  (3) behavioural — X6 ≡ X4 on every dev season before 2025 and
  first differs in 2025.
- Coordinator corrections during verification (Codex's first run
  was invalid and was sent back once, narrowly): (1) a key-name
  bug (`xg_h` vs `xg_home`) meant the shotmap history never
  loaded, so X4/X6 silently fell back to Gate Zero everywhere —
  fixed, with activation diagnostics measured by the coordinator
  (X4 differs from Gate Zero on 1,305/1,372 dev and 199/200
  virgin matches; X6 differs from X4 on 302/380 era dev matches
  and 199/200 virgin matches, and on 0/992 pre-era dev matches);
  (2) X4's multiplier base corrected to the league venue ratio
  rho per the prereg (it had used the team BB ratio); (3) the
  harness's per-season baseline table overwrote all lines but
  9.5 — fixed; (4) the harness selection now applies the prereg's
  provisional-pass calibration rule. None of the corrections
  changed a frozen constant, a gate, or the dev-gate outcome;
  correction (1) changed X4/X6 from fictitious passes-by-identity
  into real, failing arms.
- Codex could not commit from its sandbox (read-only git
  metadata); the commits on `build/s-j1` were made by the
  coordinator, as in the G-J1 flow.
