# G-BA Verdict — BA-PremierLeague goals model

Date: 2026-11-10. Branch `build/ba-premier-league`. Prereg:
`league/BA-PremierLeague/prereg/PREREG_G_BA.md` (commit 02673f5f,
frozen before any fitting). Engine:
`league/BA-PremierLeague/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun, and virgin
predictions were recomputed by hand from the fitted parameters
with independent code.

## Verdict: PASS (provisional calibration) — Gate Zero ships

Both arms pass the dev gate and all virgin legs. Calibration on the
virgin window is provisional on both legs (HW breach 0.004pp over
the 1.0pp boundary; OU breach 1.45pp, both well within 1 SE), which
the frozen rule records as a pass. SHRINK is numerically identical
to Gate Zero everywhere (see below), so the both-pass tie rule ships
the simpler arm: **Gate Zero**. Fitted parameters:
`engine/goals/fitted_params_virgin.json` (h = 0.3204, rho = 0.0,
mu = 1.1811 goals/team/match, training n = 968). Virgin predictions:
`predictions/g_ba_virgin_predictions.csv` (n = 64, arm = gate_zero).

## Dev results (walk-forward expanding, season-blocked; n = 772)

Seed 2021/2022 (never scored); scored folds 2022/2023–2025/2026.
Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022/2023 | 198 | Gate Zero | 0.9867 | 0.2031 | 0.6830 |
| 2022/2023 | 198 | SHRINK | 0.9867 | 0.2031 | 0.6830 |
| 2022/2023 | 198 | Climatology | 1.0531 | 0.2212 | 0.6967 |
| 2022/2023 | 198 | Naive trailing-10 | 1.0541 | 0.2289 | 0.7025 |
| 2023/2024 | 198 | Gate Zero | 0.9578 | 0.2038 | 0.6869 |
| 2023/2024 | 198 | SHRINK | 0.9578 | 0.2038 | 0.6869 |
| 2023/2024 | 198 | Climatology | 1.0186 | 0.2219 | 0.7161 |
| 2023/2024 | 198 | Naive trailing-10 | 0.9836 | 0.2134 | 0.6841 |
| 2024/2025 | 196 | Gate Zero | 0.8966 | 0.1866 | 0.6900 |
| 2024/2025 | 196 | SHRINK | 0.8966 | 0.1866 | 0.6900 |
| 2024/2025 | 196 | Climatology | 1.0790 | 0.2472 | 0.6994 |
| 2024/2025 | 196 | Naive trailing-10 | 0.8908 | 0.1818 | 0.7078 |
| 2025/2026 | 180 | Gate Zero | 0.9476 | 0.1842 | 0.6775 |
| 2025/2026 | 180 | SHRINK | 0.9476 | 0.1842 | 0.6775 |
| 2025/2026 | 180 | Climatology | 1.0589 | 0.2226 | 0.6746 |
| 2025/2026 | 180 | Naive trailing-10 | 1.0042 | 0.2053 | 0.7045 |
| Pooled | 772 | Gate Zero | **0.9473** | **0.1947** | **0.6845** |
| Pooled | 772 | SHRINK | **0.9473** | **0.1947** | **0.6845** |
| Pooled | 772 | Climatology | 1.0522 | 0.2283 | 0.6972 |
| Pooled | 772 | Naive trailing-10 | 0.9829 | 0.2074 | 0.6996 |

Dev gate (pooled LL and RPS must beat climatology, OU LL must beat
the base-rate baseline): Gate Zero **PASS** (0.9473 < 1.0522,
0.1947 < 0.2283, 0.6845 < 0.6972). SHRINK **PASS** identically.
The model also beats the naive trailing-10 on pooled LL (0.9473 <
0.9829) and RPS, though the naive wins single seasons (2024/2025
LL 0.8908 vs model 0.8966) — the model is not uniformly dominant,
it is better pooled.

### Why SHRINK ≡ Gate Zero (verified, not a bug)

The SHRINK arm shrinks ratings only for teams with 1–5 prior
in-league matches in the training window. Under expanding
season-blocked fits no BA team ever has 1–5 prior matches:
recomputed independently per target season, prior-match counts are
0 (brand-new clubs: 2 in 2022/23, 2 in 2023/24, 2 in 2026/27) or
≥33 (every returning club). n=0 is identical to Gate Zero's unseen
rule, so the two arms produce byte-identical predictions in every
season. The arm is degenerate in this league by construction — a
design note, not an implementation defect. (The G-J2 lesson it
addresses bites only in mid-season / partial-window fits, which
this walk-forward never performs.)

## Virgin results (season "2026/2027", in progress, n = 64, read once after dev froze)

| Arm | 1X2 LL | RPS | OU2.5 LL | HW calib diff | HW SE | OU calib diff | OU SE |
|---|---|---|---|---|---|---|---|
| Gate Zero | 0.8880 | 0.1630 | 0.6989 | −1.00pp | 5.41pp | −2.45pp | 6.32pp |
| SHRINK | 0.8880 | 0.1630 | 0.6989 | −1.00pp | 5.41pp | −2.45pp | 6.32pp |
| Climatology | 1.0625 | 0.2186 | 0.6815 | — | — | — | — |

Actual virgin rates: home-win 46.9% (30/64), over-2.5 42.2% (27/64).
Mean predicted: home-win 45.9%, over-2.5 39.7%. Calibration diffs
are predicted − actual, per the prereg. Note the virgin OU2.5 LL
(0.6989) is worse than climatology's (0.6815) — that is not a gate
leg (the OU leg lives in the dev gate, which passed), but it is
recorded plainly: on 64 matches the model's totals edge is thin.
The confirmatory re-read at season end (reserved in the prereg)
will test whether the provisional calibration holds at full n.

## Per-leg verdicts

| Leg | Gate Zero | SHRINK |
|---|---|---|
| Dev gate | PASS | PASS |
| Virgin LL (≤ Gate Zero and ≤ climatology 1.0625) | PASS (0.8880) | PASS (0.8880) |
| Calibration — home-win (≤1.0pp, or breach ≤1 SE = provisional) | PROVISIONAL PASS (breach 0.004pp ≤ SE 5.41pp) | PROVISIONAL PASS (same) |
| Calibration — OU2.5 | PROVISIONAL PASS (breach 1.45pp ≤ SE 6.32pp) | PROVISIONAL PASS (same) |
| Per-season sign check (dev LL ≤ Gate Zero in ≥2 of 4 seasons) | n/a (comparator) | PASS (4/4, equal) |
| **Overall** | **PASS** | **PASS** |

Both-pass rule: both arms pass all legs with identical virgin LL,
so the tie goes to the simpler arm — **Gate Zero ships**.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly (dev and virgin).
- Dev isolation confirmed in code and in the outputs: dev loads
  only seasons 2021/2022–2025/2026; `results_dev.csv` contains no
  2026/2027 row and none of the 4 awarded match ids; scored n = 772
  asserted in code.
- Pooled and per-season metrics recomputed from `results_dev.csv`
  with independent code match the JSON to 6 decimals; pooled
  climatology recomputed as the weighted mean of the per-season
  expanding climatology rows (not full-period rates).
- Spot check: a fresh DC implementation written from the production
  pattern (not importing engine code) reproduces the engine's
  lambdas and probabilities exactly (max diff 0.0) on the first 40
  matches of 2022/2023, including Codex's hand-checked match
  `3905126` (Posušje–Velež, λ 1.2567/1.3977).
- Virgin spot check: 5 virgin predictions recomputed by hand from
  `fitted_params_virgin.json` (independent score-matrix code)
  match the CSV exactly (max diff 0.0), including both newcomers
  (BSK Banja Luka, Čelik Zenica); 1H/2H lambdas equal the
  0.4493/0.5507 constant split of the same FT lambdas and the 1H OU
  0.5 line equals the split-lambda matrix value; all 64 rows'
  1X2 probabilities sum to 1.
- Two coordinator corrections during verification, neither touching
  a model or a gate: (1) Codex's naive trailing-10 used only
  prior-season matches (stale — it ignored earlier matches of the
  target season itself); fixed to every match strictly before
  kickoff per the causality contract, dev re-run and re-frozen
  (naive pooled LL 1.0104 → 0.9829; model numbers unchanged);
  (2) `fitted_params_virgin.json` omitted the two newcomer clubs
  (zero training matches, so absent from the fit's team-name map);
  the file was patched directly with a=0, d=0, training_n=0 for
  Čelik Zenica (10109) and BSK Banja Luka (187927) — definitional
  values, no harness re-run and no second virgin read — and the
  harness code was fixed the same way for any future run.
- SHRINK degeneracy verified independently (prior-count audit above);
  the identical arm numbers are correct, not a silent bug.

## What ships

- G-BA (goals: 1X2 / OU 1.5/2.5/3.5 / BTTS, FT + 1H/2H via frozen
  constant 0.4493), Gate Zero arm, fitted params in
  `engine/goals/fitted_params_virgin.json`.
- S-BA / C-BA / K-BA / T-BA: not buildable (prereg
  `PREREG_SCKT_NOT_BUILDABLE.md`); nothing ships for them.
- League completion state: the single buildable candidate (G-BA)
  is through its gates — **league complete: 1 pass / 0 fail /
  4 not buildable**.
