# G-AL Verdict — AL-KategoriaSuperiore goals model

Date: 2026-11-10. Branch `build/al-kategoria-superiore`. Prereg:
`league/AL-KategoriaSuperiore/prereg/PREREG_G_AL.md` (commit 96fcfd57,
frozen before any fitting). Engine:
`league/AL-KategoriaSuperiore/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun, and the engine's
lambdas were reproduced by a fresh DC implementation written from the
production pattern.

## Verdict: FAIL — Gate Zero fails the dev gate; nothing ships

Gate Zero loses to climatology on **all three** pooled dev legs
(1X2 LL, RPS, OU2.5 LL). Per the frozen rule — Gate Zero fails dev
⇒ variants moot — SHRINK is not virgin-read, the virgin window
(2026/2027, n=55) was **NOT read**, and no predictions or fitted
parameters exist for this league. This was the honest pre-fit
expectation from EDA F2 (team traits weak: split-half GF 0.27 /
GA 0.14; tiers flat, top +0.32 to bottom −0.65 GD/match): there is
too little team signal in this league for the DC ratings to beat
the league base rate. A FAIL is a complete outcome; no gate was
moved and no rescue arm was invented.

## Dev results (walk-forward expanding, season-blocked; n = 720)

Seed 2021/2022 (never scored); scored folds 2022/2023–2025/2026
(regular season only; 14 playoff matches excluded everywhere).
Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022/2023 | 180 | Gate Zero | 1.0832 | 0.2270 | 0.6744 |
| 2022/2023 | 180 | SHRINK | 1.0832 | 0.2270 | 0.6744 |
| 2022/2023 | 180 | Climatology | 1.0892 | 0.2296 | 0.6659 |
| 2022/2023 | 180 | Naive trailing-10 | 1.1083 | 0.2343 | 0.6797 |
| 2023/2024 | 180 | Gate Zero | 1.1314 | 0.2362 | 0.6776 |
| 2023/2024 | 180 | SHRINK | 1.1314 | 0.2362 | 0.6776 |
| 2023/2024 | 180 | Climatology | 1.0916 | 0.2283 | 0.6685 |
| 2023/2024 | 180 | Naive trailing-10 | 1.0654 | 0.2176 | 0.6822 |
| 2024/2025 | 180 | Gate Zero | 1.1053 | 0.2150 | 0.6900 |
| 2024/2025 | 180 | SHRINK | 1.1053 | 0.2150 | 0.6900 |
| 2024/2025 | 180 | Climatology | 1.0925 | 0.2116 | 0.6764 |
| 2024/2025 | 180 | Naive trailing-10 | 1.1275 | 0.2229 | 0.7007 |
| 2025/2026 | 180 | Gate Zero | 1.0688 | 0.2164 | 0.6695 |
| 2025/2026 | 180 | SHRINK | 1.0688 | 0.2164 | 0.6695 |
| 2025/2026 | 180 | Climatology | 1.0813 | 0.2202 | 0.6530 |
| 2025/2026 | 180 | Naive trailing-10 | 1.1067 | 0.2302 | 0.6607 |
| Pooled | 720 | Gate Zero | **1.0972** | **0.2237** | **0.6779** |
| Pooled | 720 | SHRINK | **1.0972** | **0.2237** | **0.6779** |
| Pooled | 720 | Climatology | 1.0886 | 0.2224 | 0.6660 |
| Pooled | 720 | Naive trailing-10 | 1.1020 | 0.2263 | 0.6808 |

Dev gate (pooled LL and RPS must beat climatology, OU LL must beat
the base-rate baseline): Gate Zero **FAIL** on all three legs
(LL 1.0972 > 1.0886, RPS 0.2237 > 0.2224, OU LL 0.6779 > 0.6660).
SHRINK **FAIL** identically. The model beats climatology in 2 of 4
seasons on LL (2022/23, 2025/26) but loses badly in 2023/24
(1.1314 vs 1.0916) and 2024/25 — and the naive trailing-10 wins a
season outright (2023/24 LL 1.0654) while losing pooled. Nothing
here is uniformly dominant; pooled, the base rate wins.

### Why SHRINK ≡ Gate Zero (verified, not a bug)

The SHRINK arm shrinks ratings only for teams with 1–5 prior
in-league matches in the training window. Under expanding
season-blocked fits no AL team ever has 1–5 prior matches:
recomputed independently per target season, prior-match counts are
0 (brand-new clubs: 2 in 2022/23, 2 in 2024/25, 2 in 2025/26) or
≥36 (every returning club). n=0 is identical to Gate Zero's unseen
rule, so the two arms produce byte-identical predictions in every
season. The arm is degenerate in this league by construction — a
design note, not an implementation defect. (The G-J2 lesson it
addresses bites only in mid-season / partial-window fits, which
this walk-forward never performs.)

## Virgin results: NOT READ

Per the frozen rule, Gate Zero's dev failure makes variants moot
and the virgin is not read. `engine/goals/results_virgin.json`
records `{"virgin_read": false, "reason": "gate_zero_failed_dev",
"shipped_arm": null}`. No virgin predictions file and no
`fitted_params_virgin.json` exist (verified: no `predictions/`
directory was created). The 2026/2027 window (in progress, n=55)
remains untouched for any future re-test under a fresh prereg;
its hot running level (2.58 goals/match) was observed only as a
design-level aggregate during EDA, never fitted on.

## Per-leg verdicts

| Leg | Gate Zero | SHRINK |
|---|---|---|
| Dev gate | **FAIL** (LL +0.0085, RPS +0.0012, OU LL +0.0119 vs climatology) | **FAIL** (identical) |
| Virgin LL | not read (moot) | not read (moot) |
| Calibration | not read (moot) | not read (moot) |
| Per-season sign check | n/a (comparator) | moot (identical) |
| **Overall** | **FAIL** | **FAIL** |

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly (dev JSON identical to Codex's run).
- Dev isolation confirmed in code and in the outputs: dev loads
  only seasons 2021/2022–2025/2026; `results_dev.csv` contains no
  2026/2027 row and none of the 14 playoff match ids; scored n = 720
  asserted in code; 1,440 CSV rows = 720 unique matches × 2 arms.
- Pooled and per-season metrics recomputed from `results_dev.csv`
  with independent code match the JSON to 6 decimals; pooled
  climatology recomputed from the CSV's climatology columns matches
  too, and the 2022/23 climatology rates match a raw recomputation
  from the CSV (HW 0.4111 / D 0.2944 / AW 0.2944 / OU 0.3722).
- Spot check: a fresh DC implementation written from the production
  pattern (not importing engine code) reproduces the engine's
  lambdas exactly (max diff 0.0) on the first 40 matches of
  2022/2023 (fold h = 0.2501, rho = −0.10, train n = 180).
  Per-fold fitted params are sane (h 0.1355–0.2501, rho ∈ {0.0,
  −0.10, −0.15}, mu 1.1082–1.1308) — the fit is healthy; the league
  is just flat.
- Engine diff vs the BA sibling: `dc.py`/`arms.py` identical except
  docstrings; `harness.py` differs only in the intended adaptations
  (CSV name, HALF_SPLIT 0.4267, playoff exclusion, scored-n 720,
  virgin-n 55, league names). No silent divergence.
- SHRINK degeneracy verified independently (prior-count audit above);
  the identical arm numbers are correct, not a silent bug.
- The virgin gate branch was exercised: running the virgin command
  wrote only the not-read marker and created no predictions or
  fitted-params file — the virgin rows were never loaded.
- Two coordinator corrections during verification, neither touching
  a model or a gate: (1) the builder's repo-root resolution had one
  `dirname` too many (resolved to `~/workspace` instead of the
  worktree) — fixed before the CSV was built; (2) the EDA pooled
  HW/D/AW/OU/BTTS row was recomputed from the CSV (41.0/30.4/28.6/
  38.6/47.3) after a first draft carried wrong pooled rates.

## What ships

- Nothing. G-AL: FAIL (1X2 / OU / BTTS / DC — no arm ships).
- S-AL / C-AL / K-AL / T-AL: not buildable (prereg
  `PREREG_SCKT_NOT_BUILDABLE.md`); nothing ships for them.
- League completion state: the single buildable candidate (G-AL)
  is through its gates with a FAIL verdict, and the four other
  markets are recorded not buildable — **league complete: 0 pass /
  1 fail / 4 not buildable**.
