# K-FO Verdict — Faroe Islands Premier League cards model

Date: 2026-11-10. Branch `build/fo-premier-league`. Prereg:
`league/FO-PremierLeague/prereg/PREREG_K_FO.md` (commit 4c162d84,
frozen before any fitting). Engine:
`league/FO-PremierLeague/engine/cards/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun of the dev
harness (identical to the last digit) and recomputed from the
per-match `results_dev.csv`. The cards code was read in full by the
coordinator (causality assertions, bounded trailing-10 deque,
MoM r discipline).

## Verdict: FAIL — Gate Zero fails the dev gate, nothing ships

Gate Zero's pooled LL@3.5 (0.6847) does not beat the league base
rate (0.6824), so it fails the dev gate. SHRINK passes its own dev
gate (0.6810 beats both baselines) but is **moot per the frozen
rule**: Gate Zero fails dev ⇒ variants moot. The virgin window
(2026) is NOT read for any arm.

## Dev results (chronological online walk-forward; n = 539)

Season 2021 is warm-up (processed, used only for the NB-size
estimation, never scored). Scored dev seasons: 2022–2025. NB size r
per method, estimated by the production method of moments on 2021
causal one-step-ahead residuals only, then frozen: Gate Zero —
model r = 72.79, base r = 500 (denominator ≤ 0, clipped), naive r =
66.37; SHRINK — model r = 138.75, base r = 500, naive r = 66.37.

| Season | n | Method | LL@3.5 | LL@4.5 | Mean P(over 3.5) | Actual over-3.5 |
|---|---|---|---|---|---|---|
| 2022 | 134 | Gate Zero | 0.6869 | 0.6737 | 0.5336 | 0.6045 |
| 2022 | 134 | SHRINK | 0.6816 | 0.6726 | 0.5381 | 0.6045 |
| 2022 | 134 | Base rate | 0.6804 | 0.6811 | 0.5424 | 0.6045 |
| 2022 | 134 | Naive t-10 | 0.7034 | 0.7081 | 0.5296 | 0.6045 |
| 2023 | 135 | Gate Zero | 0.6829 | 0.6576 | 0.5411 | 0.6296 |
| 2023 | 135 | SHRINK | 0.6760 | 0.6574 | 0.5436 | 0.6296 |
| 2023 | 135 | Base rate | 0.6745 | 0.6705 | 0.5418 | 0.6296 |
| 2023 | 135 | Naive t-10 | 0.6657 | 0.6571 | 0.5647 | 0.6296 |
| 2024 | 135 | Gate Zero | 0.6848 | 0.6778 | 0.5904 | 0.6000 |
| 2024 | 135 | SHRINK | 0.6808 | 0.6706 | 0.5959 | 0.6000 |
| 2024 | 135 | Base rate | 0.6799 | 0.6612 | 0.5996 | 0.6000 |
| 2024 | 135 | Naive t-10 | 0.6991 | 0.6741 | 0.5884 | 0.6000 |
| 2025 | 135 | Gate Zero | 0.6843 | 0.6772 | 0.5679 | 0.5407 |
| 2025 | 135 | SHRINK | 0.6856 | 0.6764 | 0.5732 | 0.5407 |
| 2025 | 135 | Base rate | 0.6949 | 0.6831 | 0.5746 | 0.5407 |
| 2025 | 135 | Naive t-10 | 0.7040 | 0.7008 | 0.5412 | 0.5407 |
| Pooled | 539 | Gate Zero | **0.6847** | 0.6716 | 0.5583 | 0.5937 |
| Pooled | 539 | SHRINK | **0.6810** | 0.6692 | 0.5627 | 0.5937 |
| Pooled | 539 | Base rate | **0.6824** | 0.6740 | 0.5647 | 0.5937 |
| Pooled | 539 | Naive t-10 | **0.6930** | 0.6850 | 0.5561 | 0.5937 |

Dev gate (pooled LL@3.5 beats BOTH baselines): Gate Zero **FAIL**
(0.6847 > base 0.6824; it beats naive 0.6930, but the gate needs
both). SHRINK **PASS** on its own numbers (0.6810 < 0.6824 and <
0.6930) — but see the frozen rule below.

Why Gate Zero loses to the base rate: the team-rating signal in
yellows is real (split-half r = 0.869 for / 0.851 against), yet on
this dev window the decayed team rates do not out-predict the
decayed league mean at the 3.5 line. Gate Zero beats the base rate
in only one of four seasons (2025, by 1.1pp); it loses 2022–2024
by 0.7pp, 0.8pp and 0.5pp. The naive trailing-10 is worse still
except in 2023. SHRINK's pooled edge over the base rate is 0.14pp
— a whisker, and it loses to the base rate in 2023 (0.6760 vs
0.6745) and to Gate Zero in 2025. Even on its own terms it is not
a convincing model, which is consistent with the frozen rule
treating it as moot rather than as a rescue.

## The frozen rule, applied

PREREG_K_FO and the brief freeze: *Gate Zero fails dev ⇒ variants
moot. Do not virgin-read any variant arm when Gate Zero failed
dev.* Gate Zero failed, so SHRINK's dev pass buys no virgin read.
The rule exists for exactly this shape of result: a shrinkage
tweak of a reference architecture that cannot beat a league-mean
baseline on dev is not a shippable model, and a virgin read would
be a result in search of a gate.

For the record (moot, not a pass): SHRINK's per-season sign check
vs Gate Zero would pass 3/4 (2022, 2023, 2024; not 2025).

## Virgin: NOT READ

No virgin read for any K-FO arm. `results_virgin.json` records
`{"virgin_read": false, ...}` with the reason. No virgin number is
computed or reported here.

## Operational check (referee availability)

Referee identity coverage is **0/810** matches:
`content.matchFacts.infoBox.Referee.text` is empty in every
payload. No referee arm exists (feature X8 DROPPED at the data
level in `analysis/FEATURES.md`), and none can be added without a
new preregistration and a new data source. The completed-match
records are post-match snapshots and contain no publication
timestamp, so they cannot by themselves prove anything about
pre-match publication of appointments — but with zero identities
recorded at all, the question is moot for this league: there is no
referee signal to ship, and the shipped outcome (nothing) needs
no referee fallback.

## Per-leg verdicts

| Leg | Gate Zero | SHRINK |
|---|---|---|
| Dev gate | FAIL (0.6847 > base 0.6824) | PASS on own numbers (0.6810) — MOOT per frozen rule |
| Virgin LL | not read | not read (moot) |
| Calibration | not read | not read (moot) |
| Per-season sign check (dev LL@3.5 ≤ Gate Zero in ≥2 of 4) | n/a (comparator) | would pass 3/4 (moot) |
| **Overall** | **FAIL** | **FAIL (moot)** |

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly (pooled and per-season, both lines).
- Per-match `results_dev.csv` (539 rows) recomputed independently:
  pooled LL@3.5 / LL@4.5 match the JSON to 4 decimals for all four
  methods.
- Dev isolation confirmed in code: the dev path loads only seasons
  2021–2025 (asserted, 674 rows); season 2026 is never loaded.
  The awarded match 3822183 is excluded from every pass
  (2022 n = 134, not 135).
- Cards code read in full: state updates happen after prediction
  (asserted), the trailing-10 deque is bounded at 10, r is
  estimated from 2021 warm-up causal residuals only, `nb_over`
  matches the production implementation and was checked against
  SciPy (diff 1.2e-15). One cosmetic wart noted, not a bug: the
  CSV rebuild loop iterates the arms dict and `break`s after
  Gate Zero when filling base/naive columns — harmless because
  base/naive means and r are arm-independent (verified: base r =
  500 and naive r = 66.37 under both arms).
- No fitted virgin parameters exist (no virgin fit was run); no
  predictions CSV is written. Nothing ships.
