# Phase 3 — EDA: ENG-Championship

All numbers computed by `analysis/eda_compute.py` from the built CSV
(raw dump: `analysis/eda_numbers.json`). Complete seasons only for
pooled rates unless stated. J1/DK/SCO checklist replicated.

## Levels per season (per match, both teams)

| Season | Goals | xG | SOT | Corners | Shots | Yellows (stats) | Reds |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.504 | 2.417 | 7.903 | 9.738 | 23.104 | 3.695 | 0.126 |
| 2022/2023 | 2.424 | 2.411 | 7.546 | 9.986 | 23.221 | 3.862 | 0.117 |
| 2023/2024 | 2.673 | 2.526 | 8.393 | 10.614 | 25.020 | 4.025 | 0.102 |
| 2024/2025 | 2.454 | 2.469 | 7.700 | 10.153 | 23.718 | 3.783 | 0.117 |
| 2025/2026 (virgin) | 2.596 | 2.599 | 8.142 | 10.308 | 25.220 | 3.759 | 0.101 |
| 2026/2027 (partial, n=180) | 2.956 | 2.930 | 8.633 | 10.361 | 27.200 | 3.744 | 0.117 |

F1 — This is a **low-scoring, low-volume** league by program
standards: goals 2.42–2.67 (SCO 2.47–2.96, CH 3.11), SOT ≈ 7.9,
shots ≈ 24. Levels drift moderately; per-league fitting with time
decay is justified. The partial 2026/2027 runs hot on every attacking
stat (small n, early season) — it stays a reserved confirmatory
window, never a design input.

## Home advantage & base rates (complete seasons pooled, n=2,783)

- Home goals 1.395–1.481/season vs away 1.022–1.202; pooled home
  edge **+0.285 goals** (weaker than SCO's +0.38). Home-win rate
  43.4%; OU2.5 over-rate 47.5%.

## F2 — Team trait reliability (career-pooled split-half, 44 teams)

| Trait | r | Verdict |
|---|---|---|
| possession | 0.868 | SIGNAL |
| box touches-for | 0.841 | SIGNAL |
| xG-for | 0.821 | SIGNAL |
| big-chance-for | 0.811 | SIGNAL |
| goals-for | 0.737 | SIGNAL |
| shots-for | 0.712 | SIGNAL |
| SOT-for | 0.688 | SIGNAL |
| corners-for | 0.517 | SIGNAL (moderate) |
| yellows-for | **−0.010** | **NOISE** |

Reliabilities sit well below SCO's (0.90–0.99): with 25% of the
league replaced every season and 44 clubs cycling through, career
traits are diluted by churn — exactly the mover problem the goals
design must face. The striking line is **yellows-for r = −0.01**:
a club's card rate carries no persistent team signal at all in this
league. The cards candidate still runs (target exists, virgin
contains it) but its Gate Zero starts with the weakest trait base
of any cards build in the program.

## F3 — Half shares: frozen-constant question

Measured on the complete-splits era 2023/2024–2025/2026 (stats-based
n≈1,972; goals via events):

| Market | 1H share | True SD of per-match share |
|---|---|---|
| goals | **0.4453** | ≈ noise (events-based, tiny denominators) |
| SOT | **0.4548** | 0.000 |
| corners | **0.4638** | 0.050 |
| total shots | **0.4573** | 0.026 |
| yellows | **0.3109** | 0.080 (cards stay back-loaded; constant still the only mechanism) |

Verdict (same as J1/DK/SCO): per-match 1H share variance is ≈
sampling noise around a league constant. **Frozen constants only**
(table above), presentation only.

## F4 — Mover tier offsets (the Championship's central question)

Entry-season performance of clubs whose previous season was in the
adjacent tier (warehouse team lists for PL id 47 / L1 id 108;
pooled over the five entry seasons 2022/2023–2026/2027):

| Entry source | team-matches | GF/match | GA/match | GD/match | ΔGF vs mu 1.265 | ΔGA vs mu |
|---|---|---|---|---|---|---|
| from Premier League | 606 | 1.574 | 1.084 | **+0.490** | **+0.309** | **−0.181** |
| from League One | 599 | 1.234 | 1.387 | **−0.154** | **−0.031** | **+0.122** |

**SIGNAL, asymmetric**: the PL→Championship step is large (a
relegated PL club is, on entry, roughly half a goal per match better
than the average Championship club — the parachute effect, measured
rather than asserted), while the L1→Championship step is mostly a
defensive problem (GA +0.12) with attack near league average
(GF −0.03). These magnitudes freeze the X2 arm's offsets in
PREREG_G_ENGCH (J1 F4 pattern: descriptive magnitudes, applied only
at prediction time in the mover's entry season).

## F5 — Set-play xG share reliability: r = **0.721** (SIGNAL)
## F6 — xG per shot reliability: r = **0.529** (SIGNAL)
## F7 — xGOT per shot, era-guarded: r = **0.344** on the 2025-era
   measurement; population era starts 2024/2025 (93.7% of shots).
   Below J1's accepted 0.518 and the era starts inside the last dev
   season, so the trait could not be honestly dev-tested across the
   dev window → X6 dropped (FEATURES).
## F8 — Referee yellow rate reliability: r = **0.259** (53 referees
   with ≥10 matches) — **NOISE** by the program's standard (J1 0.65,
   DK 0.56; SCO dropped X8 at 0.158). X8 is dropped in FEATURES.
## F11 — xG calibration: goals/xG 0.994–1.058 per complete season —
   FotMob xG is calibrated for this league; the production blend
   pattern (X1) is legitimate.

## Feasibility summary

All five targets (goals, SOT, corners, cards, total shots) exist in
100% of matches in every season, and the virgin season (2025/2026)
contains all of them → **five candidates** (MODEL_DESIGN).
