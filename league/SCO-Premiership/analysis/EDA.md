# Phase 3 — EDA: SCO-Premiership

All numbers computed by `analysis/eda_compute.py` from the built CSV
(raw dump: `analysis/eda_numbers.json`). Complete seasons only for
pooled rates unless stated. J1/DK checklist replicated.

## Levels per season (per match, both teams)

| Season | Goals | xG | SOT | Corners | Shots | Yellows (stats) | Reds |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.469 | 2.432 | 8.088 | 10.741 | 24.439 | 3.886 | 0.206 |
| 2022/2023 | 2.939 | 2.657 | 8.311 | 10.254 | 25.202 | 3.899 | 0.294 |
| 2023/2024 | 2.759 | 2.790 | 8.658 | 10.925 | 25.732 | 3.592 | 0.140 |
| 2024/2025 | 2.961 | 2.779 | 8.583 | 11.035 | 25.338 | 3.658 | 0.184 |
| 2025/2026 (virgin) | 2.781 | 2.788 | 8.627 | 10.018 | 25.316 | 3.991 | 0.184 |
| 2026/2027 (partial, n=75) | 2.853 | 3.293 | 9.600 | 11.427 | 29.213 | 3.827 | 0.133 |

F1 — Levels drift moderately (goals 2.47–2.96); per-league fitting
with time decay is justified. The partial 2026/2027 runs hot on
shots/SOT/xG (small n, early season) — another reason it stays a
reserved confirmatory window, never a design input.

## Home advantage & base rates (complete seasons pooled, n=1,140)

- Home goals 1.404–1.702/season vs away 1.066–1.268; pooled home
  edge **+0.38 goals**. Home-win rate 46.0%; OU2.5 over-rate 53.7%
  (dev-window 53.8%).

## F2 — Team trait reliability (career-pooled split-half, 14 teams)

| Trait | r | Verdict |
|---|---|---|
| possession | 0.985 | SIGNAL |
| SOT-for | 0.972 | SIGNAL |
| xG-for | 0.970 | SIGNAL |
| shots-for | 0.969 | SIGNAL |
| box touches-for | 0.966 | SIGNAL |
| corners-for | 0.963 | SIGNAL |
| big-chance-for | 0.953 | SIGNAL |
| goals-for | 0.901 | SIGNAL |
| yellows-for | 0.639 | SIGNAL (moderate) |

Reliabilities are inflated relative to J1/DK by the extreme trait
spread (Old Firm vs the rest — the same dominance that makes traits
easy to measure also makes the league's matches lopsided). They are
reported as measured; the dev gate, not the reliability, decides.

## F3 — Half shares: frozen-constant question

Measured on the complete-splits era 2023/2024–2025/2026 (n=684;
goals via events, n=643 matches with ≥1 goal):

| Market | 1H share | True SD of per-match share |
|---|---|---|
| goals | **0.4405** | ≈ noise (events-based share obs. SD 0.322 at tiny denominators) |
| SOT | **0.4492** | 0.019 |
| corners | **0.4704** | 0.039 |
| total shots | **0.4582** | 0.016 |
| yellows | **0.3120** | 0.100 (cards stay back-loaded; constant still the only mechanism) |

Verdict (same as J1/DK): per-match 1H share variance is ≈ sampling
noise around a league constant for goals/SOT/shots; corners and
yellows carry a small true component but nowhere near enough to
model per team/match. **Frozen constants only** (table above),
presentation only.

## F5 — Set-play xG share reliability: r = **0.676** (SIGNAL-CANDIDATE)
## F6 — xG per shot reliability: r = **0.740** (SIGNAL-CANDIDATE)
## F7 — xGOT per shot, era-guarded (2025-era measurement): r = **0.490**;
   population era starts 2024/2025 (94.1% of shots carry xGOT).
   Near J1's accepted 0.518 → arm status with the era guard.
## F8 — Referee yellow rate reliability: r = **0.158** (23 referees
   with ≥10 matches) — **NOISE** by the program's standard (J1 0.65,
   DK 0.56). Scottish refereeing strictness, as captured here, does
   not persist measurably. X8 is dropped in FEATURES.
## F11 — xG calibration: goals/xG 0.989–1.106 per complete season —
   FotMob xG is calibrated for this league; the production blend
   pattern (X1) is legitimate.

## Feasibility summary

All five targets (goals, SOT, corners, cards, total shots) exist in
100% of matches in every season, and the virgin season (2025/2026)
contains all of them → **five candidates** (MODEL_DESIGN).
