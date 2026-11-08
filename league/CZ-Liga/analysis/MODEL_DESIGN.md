# Step 6 — Model Design (CZ-Liga)

Windows (all candidates): training seed 2021/2022; dev =
walk-forward, season-blocked, evaluation seasons 2022/2023,
2023/2024, 2024/2025 (n = 810 included matches; stats-target subsets
smaller where the feed is missing); **virgin = 2025/2026 (n = 270
included, complete), read ONCE, only for arms passing the dev gate**.
2026/2027 is in progress and is NOT read in this build (reserved
confirmatory). Inclusion: phase != placement everywhere.
Calibration rule (programme-wide): |breach| ≤ 1.0pp clean PASS;
≤ 1 SE PROVISIONAL; else FAIL. Gates never move after results.

## Candidates

### G-CZ — goals (Dixon–Coles, goals-only)
Reference: production `model_v2.py` DC pattern, hl = 270, observation
goals-only throughout (X1 dropped — no xG). Arms: **Gate Zero**;
**SHRINK** (sanctioned G-J2-lesson arm: ratings of teams with <6
prior in-league matches shrunk `a *= n/6, d *= n/6` at prediction
time); **X2** (mover tier offset, FEATURES X2: promoted club's
ratings shifted by the cumulative mean ΔGF/ΔGA of transitions
completed before the target season, per EDA F4; ≡ Gate Zero for
2022/2023 where no transition is completed). Primary metrics: 1X2
LL/RPS + OU2.5 LL vs climatology.

### S-CZ — shots on target (v5 pattern)
Reference: production `model_sot.py` v5 (joint Poisson ridge + NB +
Beta-Binomial on-target ratio). Arms: **Gate Zero**; **RS**
(ratio-shrink, BB prior 200 → 20,000). Primary line **8.5** (dev
over-rate 0.4986). **Declared risk (frozen)**: v5's shots input is
the raw `total_shots` series whose counting changes at 2025/2026
(EDA F1); within-era the input is consistent and the virgin
walk-forward updates state from virgin-era matches themselves, but
early virgin matches inherit dev-era shot levels. The virgin gate
judges the result as-is (RO precedent, same declaration).

### C-CZ — corners (corners_v3 pattern)
Reference: production corners pattern; Gate Zero covariate =
possession only (X9 reduced form; big_chance has no dev-era data).
Arms: **Gate Zero only** (X7 dropped on data absence — no variant is
registered rather than inventing one; RO precedent). Primary line
**10.5** (dev over-rate 0.4565, closest to 0.5).

### K-CZ — cards (cards pattern, event-unified yellows)
Target: event yellows (frozen, PREPROCESSING/EDA F6). Arms: **Gate
Zero only** (X8 dropped — referee names absent from the entire dev
era, F5). Primary line **3.5** (dev over-rate 0.5676, closest to 0.5;
note this league's cards line sits lower than the 4.5 typical
elsewhere because the event-yellow level is ~4.1/match).

### T-CZ — total shots: NOT BUILDABLE (no prereg, no virgin read)
The target's definition changes at the rich-feed boundary exactly
where the virgin window begins (dev mean ≈ 17.5 → virgin 25.5,
+44%, with SOT/corners/goals continuous). A dev→virgin gate on the
raw series would test the feed change, not a model. The
total-minus-blocked reconstruction cannot be verified against
dev-era data (components not stored there). Recorded as
considered-and-rejected, exactly as RO. Verdict doc:
`reports/T_CZ_VERDICT.md` (NOT BUILDABLE).

## Halves presentation

Goals and cards: FT + 1H/2H via the frozen EDA F3 constants
(0.4509 / 0.3150), presentation only, for shipped markets.
SOT and corners: **FT-only** (halves_share_1h = null; no dev-era
period splits exist — the splits that do exist begin inside the
virgin season itself and may not define their own presentation
constants in this build).
