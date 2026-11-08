# S-NL Verdict — Eredivisie shots-on-target model

Date: 2026-11-09. Branch `build/nl-eredivisie`. Prereg:
`league/NL-Eredivisie/prereg/PREREG_S_NL.md` (commit 3c36b73, frozen
before any fitting). Engine: `league/NL-Eredivisie/engine/sot/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
all numbers below were reproduced by the coordinator's own rerun,
and the shipped arm's virgin LL was recomputed independently from
the predictions CSV (see Verification notes). Predictions-only
product: no Eredivisie SOT odds source exists in-system — expected,
not a defect.

## Verdict: PASS (calibration PROVISIONAL) — Gate Zero ships

Gate Zero (the unmodified v5 pattern) passes the dev gate and both
virgin legs and ships. The two quality arms (X4, X6) post the
**best virgin LLs of the candidate** and clean calibrations — and
both fail the frozen leg (iii), the dev per-season sign check, so
under the prereg as written they cannot ship. RS fails virgin leg
(i). The virgin predictions CSV on file is the Gate Zero product,
labelled `arm = GZ`.

## Dev results (per-match walk-forward, scored 2022/2023–2024/2025, n = 918)

LL@9.5 (binary log-loss on P(over 9.5); lower is better):

| Season | n | Gate Zero | RS | X4 | X6 | Base rate | Naive t-10 |
|---|---|---|---|---|---|---|---|
| 2022/2023 | 306 | 0.6916 | 0.6896 | 0.6907 | 0.6907 | — | — |
| 2023/2024 | 306 | 0.6853 | 0.6847 | 0.6893 | 0.6893 | — | — |
| 2024/2025 | 306 | 0.6795 | 0.6790 | 0.6806 | 0.6870 | — | — |
| **Pooled** | 918 | **0.6855** | **0.6844** | **0.6869** | 0.6890 | 0.6985 | 0.6978 |

X6 is identical to X4 before the era (xGOT guard: no era-valid
matches before 2024/2025) and is judged for the dev gate on its era
fold only — season 2024/2025 (n = 306): X6 0.6870 vs base rate
0.6992 and naive 0.6940 on the same subset.

Dev gate (pooled LL@9.5 beats BOTH baselines; X6 on era folds):
Gate Zero **PASS** (0.6855 < 0.6985, < 0.6978). RS **PASS**
(0.6844). X4 **PASS** (0.6869). X6 **PASS** on era folds (0.6870 <
0.6992 and < 0.6940). All four arms were therefore read on the
virgin window (see the coordinator correction in Verification
notes — the harness's first virgin read covered only GZ/RS).

## Virgin results (season "2025/2026", n = 306, read once after dev froze)

Actual over-9.5 rate 53.9%; mean total SOT 10.38.

| Arm | LL@9.5 | Mean P(over 9.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | **0.6943** | 52.10% | −1.82pp | 2.86pp |
| RS | 0.6949 | 51.99% | −1.93pp | 2.87pp |
| X4 | **0.6927** | 53.27% | −0.66pp | 2.86pp |
| X6 | 0.6930 | 53.67% | −0.25pp | 2.86pp |
| Base rate (baseline) | 0.6947 | 47.79% | −6.21pp | — |
| Naive t-10 (baseline) | 0.7146 | 54.29% | +0.39pp | — |

## Per-leg verdicts

| Leg | Gate Zero | RS | X4 | X6 |
|---|---|---|---|---|
| Dev gate | PASS | PASS | PASS | PASS (era folds) |
| Virgin (i) LL ≤ Gate Zero (0.6943) and ≤ best baseline (0.6947) | PASS | FAIL (0.6949) | PASS (0.6927) | PASS (0.6930) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 0.82pp ≤ SE 2.86pp) | PROVISIONAL PASS | PASS (−0.66pp) | PASS (−0.25pp) |
| (iii) dev sign check vs Gate Zero | n/a | PASS (3/3 seasons) | **FAIL (1/3)** | **FAIL (era fold 0.6870 > 0.6795)** |
| **Overall** | **PASS — ships** | FAIL | FAIL | FAIL |

Reading of the variants, plainly: the xG/shot quality input (X4)
and its xGOT extension (X6) are the better models on the virgin
window — better LL, near-perfect calibration — in a league where
F6/F7 measured both traits as genuinely reliable (r = 0.759 /
0.522), unlike J1. They are blocked by leg (iii): on dev they beat
Gate Zero in only one of three seasons (X4) / lost the era fold
(X6). The sign check exists to stop exactly this shape of result —
a variant that is worse on most of dev and better on one virgin
window — from shipping on a single window's evidence. It is
applied as written. If a future prereg wants X4/X6, its evidence
base is this table plus a fresh virgin window (2026/2027, once
complete); nothing here re-opens the frozen gate. RS is a wash
(best on dev by 0.0011, worse on virgin): v5's P = 200 prior is
already the right shrinkage for this league, F6's r = 0.581
notwithstanding.

**S-NL therefore joins the daily runner with SOT / Gate Zero** —
the league's first PASS.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun reproduces every dev number and the GZ/RS
  virgin numbers byte-identically.
- Independent recomputation: virgin LL@9.5 recomputed from the
  shipped predictions CSV (P(over 9.5) column vs actual totals) =
  0.6943 — identical to the harness figure.
- Coordinator correction during verification (Codex's first
  virgin read was incomplete and was sent back once, narrowly):
  the harness's read-list required the leg-(iii) sign check
  already at the dev-gate stage, so X4/X6 — which pass the frozen
  dev gate (beat both baselines) — were not read. The condition
  was corrected to the prereg's dev gate only and the virgin step
  re-run; GZ/RS results reproduced exactly, X4/X6 were read for
  the first (and only) time in that re-run. Leg (iii) was then
  applied where the prereg puts it: at the ship decision, where
  both variants fail it.
- Activation diagnostics (coordinator-measured on the virgin
  window): X4's probabilities differ from Gate Zero's on 306/306
  virgin matches; X6 differs from X4 on 304/306 — both arms are
  genuinely active, not identity fallbacks.
- Era-guard correctness for X6: xGOT sums are populated only from
  matches dated ≥ 2024-08-01 in the arm's history builder;
  behaviourally, X6 ≡ X4 on every pre-era dev season and first
  differs in 2024/2025.
- Virgin isolation confirmed in code: the dev path loads only
  seasons 2021/2022–2024/2025; season 2026/2027 is loaded by no
  step.
