# P4 Gate Zero — Sanctioned Recalibration Arm (level-only refit)

**VERDICT: P4 DIES.** Both pre-registered measures fail their thresholds.

| Measure | Result | Threshold | Verdict |
|---|---|---|---|
| A — rescue rate (sealed calibration failures) | **12 / 40 = 30.0%** | ≥ 1/3 (33.3%) | FAIL (short by 1 candidate) |
| B — break rate (eventual passes) | **26 / 84 = 31.0%** | ≤ 10% | FAIL (3× the limit) |

Replay script: `league/improvement_scratch/P4/replay_p4.py`.
Per-candidate arithmetic: `league/improvement_scratch/P4/per_candidate.csv`
(221 rows = 122 PASS + 99 sealed-window FAILs, i.e. every candidate that
passed the pooled dev gate). No verdict of record changes; this is a
counterfactual method test on already-read windows, per AUDIT.md §6 P4
("same replay protocol as P1", kill rule "as P1") and the coordinator's
reading registered in IMPROVEMENT_STATUS.md: adopt iff the arm rescues
≥⅓ of sealed calibration failures AND breaks ≤10% of passes.

## Method as implemented

- **Arm of record.** PASS candidates: the shipped arm. Sealed FAILs:
  the reference arm (Gate Zero for S/C/K/G, arm A for total shots) if
  it was scored on the sealed window, else the first scored arm
  (e.g. K-PT, where only X8 was read).
- **Offset.** For the gated quantity at the primary line:
  `offset = mean P(over) − actual over-rate` over the **last dev
  season only**, from the shipped/reference arm's persisted artefacts.
- **Application.** Sealed per-match probabilities shifted by the
  offset: `p′ = clamp(p − offset, 0.001, 0.999)` (an over-predicting
  dev season subtracts). Calibration re-scored as
  `mean(p′) − actual` in pp, with SE recomputed as
  `sd(p′ᵢ − yᵢ)/√n` where per-match rows exist.
- **Leg semantics (Form A, as specified in the task).** Clean pass
  `|diff| ≤ 1.0pp`; provisional pass `|diff| ≤ 1.0pp + 1 SE`; else fail.
  Rescued = a sealed calibration failure whose leg now passes (clean
  or provisional) — for goals, the failing component must pass and no
  other component may fail. Broken = a PASS whose leg now fails.
- **Goals** carry two quantities (home-win rate, OU2.5 over-rate).
  Each got its own last-dev-season offset, applied to its own sealed
  probabilities. Included only where persisted artefacts support both
  quantities (2 of 11 sealed-calibration-failure goals candidates and
  2 of 4 passing goals candidates were measurable; the rest are
  counted unmeasurable, not silently dropped — see coverage).
- **Artefact tiers.** Dev offset source: per-match file (exact) or
  the per-season aggregate persisted in `results_dev.json`
  (mean P(over) and actual rate for the last dev season — the offset
  is a difference of means, so the aggregate gives the identical
  number). Sealed source: per-match predictions (exact, incl.
  clamping and SE recomputation; actuals joined by match_id from the
  league data file where a predictions file carries no actuals
  column), or the aggregate in `results_virgin.json`. For the
  aggregate-sealed tier, `after = before − offset` and the SE is
  carried over: a pure shift leaves `sd(pᵢ − yᵢ)` unchanged, so the
  carried SE is exact except for clamping, which binds only for
  probabilities within one offset of 0/1 (rare at these lines;
  median |offset| = 2.13pp, max 11.23pp).

## Coverage (flagged per instructions)

| Population | Measurable | Coverage |
|---|---|---|
| A: sealed calibration failures (70) | 40 | **57.1%** |
| B: eventual passes (122) | 84 | **68.9%** |

Both populations clear the 50% floor, so the verdict stands on the
measured subset — but coverage is very uneven by market:

| Market | A measurable | B measurable |
|---|---|---|
| Corners | 14 / 17 | 36 / 40 |
| Total shots | 17 / 20 | 31 / 33 |
| Cards | 7 / 8 | 12 / 12 |
| Goals | 2 / 11 | 2 / 4 |
| **SOT** | **0 / 14** | **3 / 33** |

SOT is the blind spot: the SOT template family persists only
per-season log-losses in `results_dev.json` (no per-season
mean-predicted vs actual, no per-match dev file), so no last-dev-season
offset exists for 44 of 47 SOT candidates in the two populations.
The verdict therefore says nothing about SOT specifically; for the
four markets where the test could run, it fails on both measures
(counting-only: A = 11/38 = 28.9%, B = 26/82 = 31.7%).

## Results detail

Rescued (12): C-AT2, T-AT, T-BE, T-CH, T-IE, G-IL, T-KR, C-NLE,
T-PT, T-RU1, K-SCOCH, K-UA. Total shots dominate the rescues (6 of
12) — the market whose level drift is most nearly a pure level shift.

Broken (26): C-AR, C-AU, K-AU, C-BRB, C-CH (CH-SuperLeague), T-CH,
K-DE2, C-DE3, T-DE3, T-DK1, C-EG, C-ENGL1, T-ENGL1, K-FI, T-FR,
C-HR, T-IS, C-ITB, T-NL, K-NO, K-PL, C-RO, T-SA, T-TR, T-US, C-ZA.
The mechanism is visible in the CSV: the last dev season's bias is
often opposite in sign to the sealed season's bias, so the
"correction" pushes a passing candidate out of the band
(e.g. K-FI: dev offset +10.62pp, sealed −2.16pp → −12.78pp;
C-CH SuperLeague: offset −4.19pp, sealed +1.06pp → +5.25pp).
A single-season level estimate is itself a noisy, regime-specific
quantity — recalibrating on it trades one level error for another.

## Validation of the replay itself

- **Before-legs reproduce the recorded verdicts.** All 84 measurable
  PASS candidates recompute to a passing sealed calibration leg
  (61 provisional, 21 clean, 2 goals provisional/provisional), and
  39 of 40 measurable sealed calibration failures recompute to a
  failing leg on the failing quantity. The one exception is K-DE3
  (Gate Zero arm): recomputed +2.73pp vs a 1+SE boundary of 3.56pp
  reads provisional under Form A, where the verdict records FAIL —
  that league's operative provisional test appears to be the
  stricter `|diff| ≤ SE` form (cf. AUDIT.md §5.6 on divergent
  provisional formulas). It does not affect the headline: K-DE3 is
  not rescued under either form (after = +4.81pp).
- **Spot-check by independent code.** C-CH (per-match tier),
  recomputed from the raw CSVs outside the replay script, matches
  exactly: offset +7.06pp, sealed before −6.97pp, after −14.03pp,
  SE 3.77pp. K-NO's actuals-join reproduces its verdict's SE
  (3.05pp) and clean-pass diff (−0.84pp) exactly. G-IL (Gate Zero)
  reproduces the verdict's OU diff −11.70pp exactly.
- **Sensitivity — provisional Form B** (`|diff| ≤ max(1pp, SE)`,
  the stricter form some preregs used): counting markets only,
  rescues fall to 8/38 and breaks rise to 35/82. P4 dies harder.
- **Sensitivity — strict per-match-only subset** (dev and sealed
  both per-match, no aggregates): A = 2/5, B = 1/7 — too small to
  carry a verdict, directionally mixed, and not the headline.
- Knife-edge note: K-NO's break is by 0.07pp (+4.12 vs boundary
  4.05). Removing it still leaves B = 25/84 = 29.8%.

## Conclusion

The level-only recalibration arm, fitted on the most recent dev
season, does not generalise: it rescues 30.0% of sealed calibration
failures (below the ⅓ bar) while breaking 31.0% of passes (three
times the 10% limit). **P4 Gate Zero FAILS; the proposal dies by
its pre-registered kill rule.** No thresholds were changed, no
verdict of record was altered, and nothing was committed.
