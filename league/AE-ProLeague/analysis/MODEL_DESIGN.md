# Step 6 — Model Design: UAE Pro League candidates

Feature consumption per `FEATURES.md` only. References are the
production patterns, seeded from the program's proven league ports
(CY/SA engines, same architecture family). All windows frozen here and
repeated in each prereg **before any fitting**:

- **Training seed**: 2021/2022 (warm-up / fit history, never scored).
- **Dev**: walk-forward, season-blocked, scored folds 2022/2023,
  2023/2024, 2024/2025 — n=545 scored matches (546 minus 1 awarded).
- **Virgin**: 2025/2026 complete (n=182), read ONCE per candidate, only
  for arms passing the dev gate. If Gate Zero fails dev, the candidate
  FAILS and the virgin is NOT read.
- **Confirmatory**: 2026/2027 (partial, 49) — reserved, NOT read.
- Awarded matches (2) excluded from all fits and scores.
- Gate legs (identical program-wide): dev LL must beat both baselines;
  virgin (i) LL ≤ Gate Zero's and ≤ best baseline's, (ii) calibration
  |breach| ≤1pp clean PASS, within 1 SE PROVISIONAL, else FAIL,
  (iii) dev per-season sign check for variants. Both-pass → lower
  virgin LL ships; ties → simpler arm.

## Feasibility matrix

| Market | Target exists | Virgin contains target | Candidate |
|---|---|---|---|
| Goals | score 100% | yes | **G-AE** |
| SOT | stats 100% all seasons | yes | **S-AE** |
| Corners | stats 100% all seasons | yes | **C-AE** |
| Cards | stats yellows 100% (event feed dead in virgin — target frozen stats, DATA_UNDERSTANDING §3) | yes | **K-AE** |
| Total shots | stats 100% all seasons | yes | **T-AE** |

## Candidates

1. **G-AE (goals)** — production Dixon-Coles, goals-only (X1 fallback).
   Arms: Gate Zero; SHRINK (ratings of teams with <6 prior in-league
   matches shrunk `a,d *= n/6` at prediction — the sanctioned G-J2
   lesson arm; 14-team league with 2–3 movers/season makes thin-history
   openers structural). Primary metrics 1X2 LL/RPS + OU2.5 LL vs
   climatology.
2. **S-AE (SOT)** — v5 pattern (ridge Poisson ratings + NB r=79.94 +
   Beta-Binomial ratio prior 200, 50/50 naive trailing-10 ensemble).
   Arms: Gate Zero; RS (prior 20,000). No X4/X6 (no shotmap).
   Primary line **9.5** (dev over-rate 0.446, closest to 0.5; 8.5 is
   0.576). Ladder 8.5/9.5/10.5.
3. **C-AE (corners)** — corners_v3 pattern (ratings + NB, territorial
   multiplier). Arms: Gate Zero (X9 possession + big chances); X7
   (box-touch multiplier). Primary line **10.5** (dev over-rate 0.439;
   9.5 is 0.563 — 10.5 is closest to 0.5). Ladder 9.5/10.5/11.5.
4. **K-AE (cards)** — production cards pattern on stats-feed yellows.
   Arms: Gate Zero only (X8 dropped, FEATURES). Primary line **3.5**
   (dev over-rate 0.523). Ladder 3.5/4.5/5.5.
5. **T-AE (total shots)** — shots family. Arms: A (v1 pattern),
   B (v2 level layer), C (E9 trailing-200 r). Primary line **25.5**
   (dev over-rate 0.528). Ladder 24.5/25.5/26.5.

## Halves presentation

FT + 1H/2H via the frozen constants of EDA F3 for every market
(legitimate sources exist: period splits from 2023/2024 for count
stats; goal-event minutes for goals). Presentation only.
