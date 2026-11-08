# C-AR Verdict — Liga Profesional corners model

Date: 2026-11-09. Branch `build/ar-liga`. Prereg:
`league/AR-LigaProfesional/prereg/PREREG_C_AR.md` (commit 7169cb5,
frozen before any fitting). Engine:
`league/AR-LigaProfesional/engine/corners/`. Implementation by
Codex (gpt-5.6-luna) under the two-agent flow; all numbers below
were reproduced by the coordinator's own reruns, the shipped
arm's virgin calibration was recomputed independently from the
predictions CSV, and the sign check was re-applied at the
prereg's own threshold (see Verification notes).
Predictions-only product: no Liga Profesional corners odds source
exists in-system — expected, not a defect.

## Verdict: PASS (calibration PROVISIONAL) — the X7 arm ships

Both arms pass the dev gate and both take a PROVISIONAL PASS on
the virgin calibration leg. Under the frozen both-pass rule the
arm with the lower pooled virgin LL ships: **X7** (0.6881 vs Gate
Zero 0.6944). The shipped product is recorded with its fitted
parameters in `engine/corners/fitted_params_virgin.json`, and the
virgin predictions CSV on file is the X7 product, labelled
`arm = x7`. **This league's first passing market → AR-LigaProfesional
joins the daily runner with corners** (coordinator records the
join; market config: arm X7 as fitted, halves constant 0.480,
primary line 9.5, ladder 8.5/9.5/10.5).

One fact about the shipped arm must be stated plainly, because it
is the result, not a footnote: the box-touch coefficient fitted
to **exactly 0** on the virgin fit window — and on every fit
window from 2024 onward (dev diagnostics: active-with-nonzero-beta
share 12.2% in 2022, 55.3% in 2023, 0% in 2024, 2025 - Apertura,
2025 - Clausura, 2026 - Apertura). The F9 trait is real
(split-half r = 0.749/0.802) but, exactly as in C-J1 and C-DK,
it earns zero inside this multiplier structure at trailing scale.
X7's virgin win therefore does not come from the box-touch
multiplier doing work: with its beta at 0, X7 is the core model
with the territorial multiplier inert, while Gate Zero's own
big-chance beta fitted to 0.025 on the virgin window and hurt
there. The frozen rules select on virgin LL, not on mechanism —
X7 passes every leg and ships as registered.

## Dev results (walk-forward, scored blocks 2022 – 2026 - Apertura, n = 1,854)

LL@9.5, pooled:

| Gate Zero | X7 | Base rate | Naive t-10 |
|---|---|---|---|
| 0.6817 | 0.6831 | 0.6889 | 0.6903 |

Per-block LL@9.5 (model arms):

| Block | Gate Zero | X7 | X7 both-teams-active share |
|---|---|---|---|
| 2022 | 0.6923 | 0.6907 | 12.2% |
| 2023 | 0.6880 | 0.6986 | 55.3% |
| 2024 | 0.6760 | 0.6763 | 70.9% |
| 2025 - Apertura | 0.6647 | 0.6638 | 96.7% |
| 2025 - Clausura | 0.6976 | 0.6995 | 100% |
| 2026 - Apertura | 0.6651 | 0.6601 | 93.3% |

Dev gate (pooled LL@9.5 beats BOTH baselines): Gate Zero **PASS**
(0.6817 < 0.6889 and < 0.6903). X7 **PASS** (0.6831 < both). Both
arms were therefore read on the virgin window. X7's low active
share in 2022–2023 is the FEATURES min-8 trailing rule absorbing
the touches_opp_box gaps of those blocks (44–63% coverage), as
designed.

## Virgin results (block "2026 - Clausura", n = 240, read once after dev froze)

Actual over-9.5 rate 45.42%; mean total corners 9.44.

| Arm | LL@9.5 | Mean P(over 9.5) | Calib diff | Calib SE |
|---|---|---|---|---|
| Gate Zero | 0.6944 | 42.44% | −2.97pp | 3.23pp |
| **X7** | **0.6881** | 42.54% | −2.87pp | 3.21pp |
| Base rate (baseline) | 0.7155 | 34.25% | — | — |
| Naive t-10 (baseline) | 0.7042 | — | — | — |

## Per-leg verdicts

| Leg | Gate Zero | X7 |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin (i) LL ≤ Gate Zero (0.6944) and ≤ best baseline (0.7042) | PASS | PASS (0.6881) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 1.97pp ≤ SE 3.23pp) | PROVISIONAL PASS (breach 1.87pp ≤ SE 3.21pp) |
| Virgin (iii) dev sign check vs Gate Zero (≥3 of 6 blocks) | n/a | PASS (3/6 blocks) |
| **Overall** | PASS (provisional) | **PASS (provisional) — ships** |

Both-pass rule: both arms pass → the lower pooled virgin LL
ships → X7. Fitted parameters (virgin fit window, fit_n = 2,168):
gamma 0.15, NB moment ratio r = 1.1222, X7 beta = [0.0] (Gate
Zero's on the same window: beta = [0.0, 0.025]).

## Verification notes (coordinator, independent of Codex)

- Full harness rerun (dev + virgin) reproduces every dev and
  virgin number exactly.
- Independent recompute from the shipped predictions CSV
  (`c_ar_virgin_predictions.csv`, arm X7): LL@9.5 0.6881,
  calibration −2.87pp, SE 3.21pp, actual over-rate 45.42% —
  identical to the harness's virgin table.
- The runner script applies the sign check at ≥2 blocks (an NL
  leftover: NL had 3 dev seasons and a ≥2-of-3 rule). The
  coordinator re-applied the AR prereg's own threshold
  (≥3 of 6): X7 wins 3 of 6 blocks (2022, 2025 - Apertura,
  2026 - Apertura) → leg (iii) PASS either way; no outcome
  changes. The discrepancy is recorded here rather than silently
  relying on the runner's printout.
- Virgin predictions of the two arms genuinely differ (they are
  not the C-J1-style tie): Gate Zero's fitted big-chance beta is
  nonzero on the virgin window while X7's box-touch beta is 0,
  so the both-pass rule, not the tie rule, decides.
