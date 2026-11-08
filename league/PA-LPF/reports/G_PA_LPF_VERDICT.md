# G-PA-LPF Verdict — Panama LPF goals model

Date: 2026-11-10. Branch `build/pa-lpf`. Prereg:
`league/PA-LPF/prereg/PREREG_G_PA_LPF.md` (commit a18477b8,
frozen before any fitting). Engine:
`league/PA-LPF/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun, and the
engine's lambdas were reproduced by the production DC fit itself.

## Verdict: FAIL — Gate Zero fails the dev gate on the 1X2 LL and RPS legs; nothing ships

Gate Zero beats climatology on the OU2.5 leg but **loses the pooled
1X2 LL leg by +0.00099** (1.100580 vs 1.099590) and the pooled RPS
leg by +0.00049 (0.226401 vs 0.225908). Per the frozen prereg the
dev gate requires all three legs, so Gate Zero **FAILS**. Per the
frozen rule — Gate Zero fails dev ⇒ variants moot — SHRINK is not
virgin-read, the virgin window (2026, n = 186) was **NOT read**,
and no predictions or fitted parameters exist for this league.
This was not the pre-fit expectation from EDA F2 (GA traits
moderate-to-strong: split-half GA 0.43–0.93; GF weak: −0.08–0.30)
— the model is essentially tied with climatology on outcomes,
winning only the totals leg. A FAIL is a complete outcome; no gate
was moved and no rescue arm was invented.

## Dev results (walk-forward expanding, season-blocked; n = 382)

Seed 2023 (partial, n = 120, never scored); scored folds 2024–2025
(awarded-excluded; 2 awarded matches excluded everywhere).
Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2024 | 191 | Gate Zero | 1.0972 | 0.2278 | 0.6733 |
| 2024 | 191 | SHRINK | 1.0972 | 0.2278 | 0.6733 |
| 2024 | 191 | Climatology | 1.0936 | 0.2274 | 0.6803 |
| 2024 | 191 | Naive trailing-10 | 1.1248 | 0.2377 | 0.6878 |
| 2025 | 191 | Gate Zero | 1.1040 | 0.2250 | 0.6709 |
| 2025 | 191 | SHRINK | 1.1040 | 0.2250 | 0.6709 |
| 2025 | 191 | Climatology | 1.1056 | 0.2245 | 0.6817 |
| 2025 | 191 | Naive trailing-10 | 1.0964 | 0.2210 | 0.6992 |
| Pooled | 382 | Gate Zero | **1.1006** | **0.2264** | **0.6721** |
| Pooled | 382 | SHRINK | **1.1006** | **0.2264** | **0.6721** |
| Pooled | 382 | Climatology | 1.0996 | 0.2259 | 0.6810 |
| Pooled | 382 | Naive trailing-10 | 1.1106 | 0.2293 | 0.6935 |

Dev gate (pooled LL and RPS must beat climatology, OU LL must beat
the base-rate baseline): Gate Zero **FAILS** LL (1.1006 > 1.0996,
by +0.0010) and RPS (0.2264 > 0.2259, by +0.0005) but **PASSES**
OU LL (0.6721 < 0.6810, by −0.0089). SHRINK **FAILS** identically.
The model loses 1X2 LL in 2024 (−0.0036) and wins it in 2025
(+0.0016); it loses RPS in both seasons; it wins OU LL in both
seasons (by −0.0071 and −0.0107).

### Why the 1X2 legs fail (diagnosis, not a rescue)

The model is not broken — it is tied with climatology on outcomes
in a small, noisy league. The two scored seasons are the only dev
evidence (n = 382) and the pooled gaps are ~0.001 LL, far inside
season-to-season noise: the arm wins the LL leg in one season and
loses it in the other. The totals leg is the only one with a clear
signal (won in both seasons), and the naive trailing-10 — which
updates within the season — beats the model on 1X2 LL in 2025
(1.0964 vs 1.1040) but loses pooled (1.1106), so freshness is not
the story here the way it was in AM. The honest reading: with a
120-match seed and two scored seasons, a season-blocked DC fit
cannot separate itself from the base rate on 1X2 in this league.
Per-fold fitted params are sane (2024: h = 0.2955, rho = −0.10,
mu = 1.3031; 2025: h = 0.1964, rho = −0.05, mu = 1.1337) — the fit
is healthy; the outcome legs fail on noise and sample size, not on
a broken fit. Calibration on dev (from `results_dev.csv`): mean
predicted P(over 2.5) vs actual over-rate 2024 0.402 vs 0.387
(+1.4pp), 2025 0.374 vs 0.424 (−5.1pp); mean predicted home-win
probability vs actual 2024 0.426 vs 0.414 (+1.2pp), 2025 0.403 vs
0.372 (+3.1pp) — no systematic totals bias, unlike AM's staleness
pattern.

### Why SHRINK ≡ Gate Zero (verified, not a bug)

The SHRINK arm shrinks ratings only for teams with 1–5 prior
in-league matches in the training window. Under expanding
season-blocked fits no PA-LPF team ever has 1–5 prior matches:
recomputed independently per target season, the only sub-6-prior
teams are brand-new clubs with n = 0 (Veraguas United in 2024,
SD Atletico Nacional in 2025, Union Cocle in 2026 — the last one
is the virgin-season newcomer). n = 0 is identical to Gate Zero's
unseen rule, so the two arms produce byte-identical predictions in
every season. The arm is degenerate in this league by construction
— a design note recorded in EDA F4 before fitting, not an
implementation defect. (The G-J2 lesson it addresses bites only in
mid-season / partial-window fits, which this walk-forward never
performs.)

## Virgin results: NOT READ

Per the frozen rule, Gate Zero's dev failure makes variants moot
and the virgin is not read. `engine/goals/results_virgin.json`
records `{"virgin_read": false, "reason": "gate_zero_failed_dev",
"shipped_arm": null}`. No virgin predictions file and no
`fitted_params_virgin.json` exist (verified: no `predictions/`
directory exists). The 2026 window (in progress, n = 186:
Clausura complete, Apertura rounds 1–15) remains untouched for any
future re-test under a fresh prereg; its running level (2.70
goals/match) was observed only as a design-level aggregate during
EDA, never fitted on.

## Per-leg verdicts

| Leg | Gate Zero | SHRINK |
|---|---|---|
| Dev gate | **FAIL** (LL ✗ +0.0010, RPS ✗ +0.0005, OU LL ✓ −0.0089 vs climatology) | **FAIL** (identical) |
| Virgin LL | not read (moot) | not read (moot) |
| Calibration | not read (moot) | not read (moot) |
| Per-season sign check | n/a (comparator) | moot (identical) |
| **Overall** | **FAIL** | **FAIL** |

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly (dev JSON identical to Codex's run; dev CSV
  md5 identical).
- Dev isolation confirmed in code and in the outputs: dev loads
  only seasons 2023–2025; `results_dev.csv` contains no 2026 row
  and none of the 2 awarded match ids; scored n = 382 asserted in
  code; 764 CSV rows = 382 unique matches × 2 arms.
- Pooled and per-season metrics recomputed from `results_dev.csv`
  with independent code match the JSON to 6 decimals; pooled
  climatology recomputed from the CSV's climatology columns matches
  too, and the 2024/2025 climatology rates match a raw recomputation
  from the analysis CSV (2024: HW 0.4667 / D 0.2333 / AW 0.3000 /
  OU 0.4667 from 2023 alone; 2025: HW 0.4341 / D 0.2669 / AW 0.2990 /
  OU 0.4180 from 2023+2024).
- Spot check: the production DC fit itself (`model_v2.py`, class
  `DC`, goals-only 5-tuples) reproduces the engine's lambdas
  exactly (max diff 0.0) on the first 40 matches of 2024 (fold
  h = 0.2955, rho = −0.10, mu = 1.3031). An independent
  Poisson/DC probability computation from the CSV lambdas
  reproduces p_home/p_draw/p_over_2_5 exactly (max diff 0.0, first
  200 rows); all probability rows sum to 1.
- Engine diff vs the AL sibling: `dc.py` identical except
  docstring/variable names and the goals-only observation (no xG
  blend branch — intended, no xG exists here); `arms.py`
  identical in effect except the dropped mover/multiplier
  parameters (no mover arm in this league); `harness.py` differs
  only in the intended adaptations (CSV name, HALF_SPLIT 0.449173,
  scored-n 382, virgin-n 186, season labels, predictions
  filename, guarded virgin protocol). No silent divergence.
- SHRINK degeneracy verified independently (prior-count audit above);
  the identical arm numbers are correct, not a silent bug.
- The virgin gate branch was exercised: running the virgin command
  wrote only the not-read marker and created no predictions or
  fitted-params file — the virgin rows were never loaded (the guard
  returns before any 2026 load in code).
- One coordinator correction during verification (Phase A): the
  pooled draw/away-win shares in the first EDA draft were wrong
  (0.279/0.314); recomputation from the CSV gives 0.299/0.294 and
  the files were corrected before the Phase A commit. A second
  correction: the tournament-name calendar mapping — FotMob labels
  flip between folders (2023–2025 Apertura Jan–May, 2026 Apertura
  Jul–Nov); the docs now record the flip as labelled instead of
  asserting one mapping.
- One coordinator fix to the engine after Codex's run: the virgin
  branch's calibration check implemented only the strict ≤ 1.0pp
  rule and ignored the prereg's PROVISIONAL rule (breach within
  1 SE = provisional pass). Fixed in `harness.py` before commit;
  the branch is dead for this league (virgin not read) and the fix
  does not change any dev output (dev rerun byte-identical after
  the fix).

## What ships

- Nothing. G-PA-LPF: FAIL (1X2 / OU / BTTS / DC — no arm ships).
- S-PA-LPF / C-PA-LPF / K-PA-LPF / T-PA-LPF: not buildable (prereg
  `PREREG_SCKT_NOT_BUILDABLE.md`); nothing ships for them.
- League completion state: the single buildable candidate (G-PA-LPF)
  is through its gates with a FAIL verdict, and the four other
  markets are recorded not buildable — **league complete: 0 pass /
  1 fail / 4 not buildable**.
