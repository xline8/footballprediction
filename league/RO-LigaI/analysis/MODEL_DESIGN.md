# Step 6 — Model Design (RO-LigaI)

Windows (all candidates): training seed 2021/2022; dev =
walk-forward, season-blocked, evaluation seasons 2022/2023,
2023/2024, 2024/2025; **virgin = 2025/2026 (n = 315, complete),
read ONCE, only for arms passing the dev gate**. 2026/2027 is in
progress and is NOT read in this build (reserved confirmatory).
Inclusion: phase != ecl_playoff everywhere. Calibration rule
(programme-wide): |breach| ≤ 1.0pp clean PASS; ≤ 1 SE PROVISIONAL;
else FAIL.

## Candidates

### G-RO — goals (Dixon–Coles, goals-only)
Reference: production `model_v2.py` DC pattern, hl = 270, blend
fallback = goals-only throughout (X1). Arms: **Gate Zero**;
**SHRINK** (sanctioned G-J2-lesson arm: ratings of teams with <6
prior in-league matches shrunk `a *= n/6, d *= n/6` at prediction
time). Primary metrics: 1X2 LL/RPS + OU2.5 LL vs climatology.

### S-RO — shots on target (v5 pattern)
Reference: production `model_sot.py` v5 (joint Poisson ridge +
NB + Beta-Binomial on-target ratio), fed by stats-feed SOT and
total shots (ratio input uses raw total shots — see prereg for why
the level break does not invalidate the ratio, and the risk note).
Arms: **Gate Zero**; **RS** (ratio-shrink). Primary line **8.5**
(dev pooled: median 8, mean 8.30). X4/X6 dropped (no shotmap).

### C-RO — corners (corners_v3 pattern)
Reference: production corners pattern; Gate Zero covariates =
possession only (X9 reduced form; big chances have no dev-era
data). Arms: **Gate Zero only** (X7 dropped on data absence — no
variant is registered rather than inventing one). Primary line
**8.5** (dev pooled over-rates: 8.5 → 0.568, 9.5 → 0.421; 8.5 is
closest to 0.5. Median 9, mean 9.10.)

### K-RO — cards (cards pattern, event-unified yellows)
Target: event yellows (frozen, PREPROCESSING). Arms: **Gate
Zero**; **X8** referee covariate. Primary line **4.5** (dev pooled
over-rate 0.467).

### T-RO — total shots: NOT BUILDABLE (no prereg, no virgin read)
The target's definition changes at the rich-feed boundary exactly
where the virgin window begins (dev mean ≈18.1 → virgin 26.1,
+44%, with SOT/corners/goals continuous). A dev→virgin gate on the
raw series would test the feed change, not a model. The
total-minus-blocked reconstruction (19.2 in the virgin season)
cannot be verified against dev-era data (no components stored)
and still drifts +4.7 by 2026/2027, so it is recorded as a
considered-and-rejected unification, not adopted silently.
Verdict doc: `reports/T_RO_VERDICT.md` (NOT BUILDABLE).

## Halves presentation

FT + 1H/2H via the frozen constants of EDA F3, presentation only,
for shipped markets.
