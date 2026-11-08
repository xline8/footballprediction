# Phase 3 — EDA: ENG-LeagueOne

All numbers computed by `analysis/eda_compute.py` from the built CSV
(raw dump: `analysis/eda_numbers.json`). Complete seasons only for
pooled rates unless stated. J1/DK/SCO/ENGCH checklist replicated.

## Levels per season (per match, both teams)

| Season | Goals | xG | SOT | Corners | Shots | Yellows (stats) | Reds |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.688 | — (era starts 22/23) | 8.366 | 10.158 | 24.725 | 3.420 | 0.127 |
| 2022/2023 | 2.564 | 2.220 | 8.065 | 10.190 | 24.504 | 3.641 | 0.147 |
| 2023/2024 | 2.587 | 2.394 | 8.196 | 10.307 | 24.607 | 4.074 | 0.169 |
| 2024/2025 | 2.576 | 2.396 | 7.831 | 9.668 | 22.763 | 3.803 | 0.126 |
| 2025/2026 (virgin) | 2.625 | 2.597 | 7.880 | 10.039 | 23.982 | 3.724 | 0.113 |
| 2026/2027 (partial, n=158) | 2.791 | 2.976 | 8.614 | 11.278 | 27.222 | 3.709 | 0.108 |

F1 — League One is a **mid-volume** league: goals 2.56–2.69 (a touch
above the Championship's 2.42–2.67), SOT ≈ 8.1, corners ≈ 10.1,
shots ≈ 24.3. Yellows jump in 2023/2024 (3.64 → 4.07) and stay
elevated — a level shift the cards walk-forward must absorb. The
partial 2026/2027 runs hot on every attacking stat (small n, early
season) — it stays a reserved confirmatory window, never a design
input.

## Home advantage & base rates (complete seasons pooled, n=2,785)

- Home goals ≈1.40–1.50/season vs away ≈1.14–1.19; pooled home
  edge **+0.274 goals** (Championship +0.285). Home-win rate
  44.1%; OU2.5 over-rate 49.2%.

## F2 — Team trait reliability (career-pooled split-half, 49 teams)

| Trait | r | Verdict |
|---|---|---|
| possession | 0.962 | SIGNAL |
| xG-for | 0.913 | SIGNAL |
| shots-for | 0.886 | SIGNAL |
| box touches-for | 0.870 | SIGNAL |
| SOT-for | 0.799 | SIGNAL |
| big-chance-for | 0.791 | SIGNAL |
| corners-for | 0.615 | SIGNAL |
| goals-for | 0.605 | SIGNAL |
| yellows-for | 0.309 | WEAK (real but thin — cf. ENGCH −0.01) |

Traits are markedly stronger than the Championship's (possession
0.962 vs 0.868; xG-for 0.913 vs 0.821) despite *higher* churn
(29% vs 25%): League One's persistent clubs separate more cleanly.
Yellows-for r = 0.309 is weak but not the Championship's pure noise
— the cards Gate Zero has a thin trait base to work with.

## F3 — Half shares: frozen-constant question

Measured on the complete-splits era (stats-based n≈1,945; goals via
events):

| Market | 1H share | True SD of per-match share |
|---|---|---|
| goals | **0.4425** | ≈ noise (events-based, tiny denominators) |
| SOT | **0.4414** | 0.000 |
| corners | **0.4672** | 0.040 |
| total shots | **0.4551** | 0.020 |
| yellows | **0.3277** | 0.083 (cards stay back-loaded; constant still the only mechanism) |

Verdict (same as J1/DK/SCO/ENGCH): per-match 1H share variance is ≈
sampling noise around a league constant. **Frozen constants only**
(table above), presentation only.

## F4 — Mover tier offsets (League One's central question)

Entry-season performance of clubs whose previous season was in the
adjacent tier (Championship team lists from warehouse id 48;
League Two is not in the warehouse, so promoted clubs are the new
clubs not in the Championship list — exact in this closed system;
pooled over the five entry seasons 2022/2023–2026/2027):

| Entry source | team-matches | GF/match | GA/match | GD/match | ΔGF vs mu 1.304 | ΔGA vs mu |
|---|---|---|---|---|---|---|
| from Championship | 596 | 1.544 | 1.151 | **+0.393** | **+0.240** | **−0.153** |
| from League Two (inferred) | 792 | 1.177 | 1.423 | **−0.246** | **−0.127** | **+0.119** |

**SIGNAL, asymmetric and mirrored vs the Championship's own F4**:
the Championship step *down* into League One is worth +0.39 GD
(relegated clubs are strong here), and the League Two step *up*
costs −0.25 GD split between weaker attack (GF −0.13) and leakier
defence (GA +0.12). Cross-check with the Championship's measured
evidence: ENGCH's ex-L1 clubs entered at GD −0.154 there — the same
clubs, one tier up, are below average; one tier down from the
Championship they are above average here. The step sizes are
coherent. These magnitudes freeze the X2 arm's offsets in
PREREG_G_ENGL1 (J1 F4 pattern: descriptive magnitudes, applied
only at prediction time in the mover's entry season).

## F5 — Set-play xG share reliability: r = **0.456** (MODERATE) —
   below the signals the program has acted on (J1 0.62, ENGCH
   0.721), and the xG era starts only in 2022/2023, the first dev
   evaluation season, so a trailing set-play arm would spend much
   of dev inactive under its min-8 rule. Judged NOT supported for
   this build (FEATURES X3).
## F6 — xG per shot reliability: r = **0.457** (MODERATE SIGNAL) —
   shotmap coverage is 100% in every dev evaluation season, so the
   X4 arm is honestly testable across dev (early-2022/2023 matches
   fall back to Gate Zero under the min-8 rule, as pre-registered).
## F7 — xGOT per shot, era-guarded: r = **−0.094** on the 2025-era
   measurement; population era starts 2024/2025 (94.4% of shots).
   Pure noise → X6 dropped (FEATURES).
## F8 — Referee yellow rate reliability: r = **0.305** (75 referees
   with ≥10 matches) — **NOISE** by the program's standard (J1 0.65,
   DK 0.56; ENGCH dropped X8 at 0.259). Coverage is good (~100%
   after the seed season) but the trait itself does not persist.
   X8 is dropped in FEATURES; K-ENGL1 runs Gate Zero only.
## F11 — xG calibration (xG era only): goals/xG 1.155 (2022/2023),
   1.081, 1.075, 1.011 (2025/2026) — goals run above FotMob xG
   early in the era and converge to parity. The blend (X1) is
   legitimate; the early tilt is part of what the dev gate judges.
   (2021/2022's ratio is meaningless — xG exists in 18 matches —
   and is not reported as a season value.)

## Feasibility summary

All five targets (goals, SOT, corners, cards, total shots) exist in
100% of matches in every season, and the virgin season (2025/2026)
contains all of them → **five candidates** (MODEL_DESIGN).
