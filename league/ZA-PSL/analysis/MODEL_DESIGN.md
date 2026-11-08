# Step 6 — Model Design: ZA-PSL

Feasibility: goals everywhere; SOT / corners / cards / total shots have
their target in the stats era (from 2022/2023) AND in the virgin
2025/2026, so all five candidates are buildable. Windows frozen in
PREPROCESSING. Calibration = actual − predicted. Gate legs identical
across candidates (dev gate vs baselines; virgin LL leg + calibration
leg |breach| ≤ 1pp clean, ≤ 1 SE provisional, else FAIL; both-pass →
lower virgin LL ships; Gate Zero dev failure ⇒ candidate FAILS, virgin
NOT read).

Phase rule (frozen, Step 1/2): every modelled row is `regular` — the
league is a straight double round-robin; the 12 Qualification Group
play-off rows in the index are excluded from the corpus entirely, not
modelled as a phase. The 2024/2025 season (15 teams, 210 matches after
Royal AM's expulsion) is a complete official season and an ordinary dev
season.

## G-ZA (goals) — Dixon-Coles, goals-only (X1 dropped)

- Reference: production `model_v2.py` DC pattern as frozen in the
  TH goals prereg (hl=270, 14 sweeps, damping 0.7, +0.25 smoothing, rho
  grid, season-blocked expanding fit).
- Arms: **Gate Zero**; **SHRINK** (programme-sanctioned G-J2-lesson arm:
  ratings of teams with <6 prior in-league matches shrunk a,d *= n/6;
  motivated by the entrant gaps, GF −0.271 / GA +0.147).
- Dev: seed-fit on 2021/2022, evaluate 2022/2023–2024/2025 (n=690).
  Virgin: 2025/2026 (n=240). Primary metrics 1X2 LL/RPS + OU2.5 LL vs
  climatology. Halves via frozen goals constant 0.4724.

## S-ZA (SOT) — production v5 pattern

- Target total SOT (stats feed). Primary line **6.5** (scored-dev
  over-rate 0.536). Ladder 5.5/6.5/7.5.
- Arms: **Gate Zero** (v5 unmodified, constants as PREREG_S_TH);
  **RS** (Beta-Binomial prior P 200 → 20,000).
- Per-match walk-forward: warm-up 2022/2023 updates state, never scored;
  dev scored 2023/2024–2024/2025 (n=448); virgin 2025/2026 (n=240).
  Baselines: league base rate; naive trailing-10. Halves constant 0.4736.

## C-ZA (corners) — production v3 pattern (J1 construction)

- Target total corners (stats feed). Primary line **8.5** (scored-dev
  over-rate 0.542). Ladder 7.5/8.5/9.5.
- Arms: **Gate Zero (X9)** — core `mu_cs` + territorial multiplier from
  possession + big chance (beta grids as PREREG_C_J1);
  **X7** — identical engine, territorial covariate = opp-box touches
  (beta grid as PREREG_C_J1; arm inactive where trailing touches missing).
- Per-season gamma/beta/r fitting on prior walk-forward rows only, as in
  the J1/TH preregs. Seed 2022/2023; dev scored 2023/2024–2024/2025
  (n=448); virgin 2025/2026 (n=240). Baselines: league base rate
  (per-season NB) and naive trailing-10. Halves constant 0.4679.

## K-ZA (cards) — production cards pattern

- Target total **stats-feed yellows** (frozen in Step 1/2: dev-era and
  virgin-era events carry no plain yellows, so no event target exists in
  either window; no virgin unified sensitivity is possible — recorded).
  Primary line **3.5** (scored-dev over-rate 0.526). Ladder 2.5/3.5/4.5.
- Arms: **Gate Zero only** (X8 dropped — FEATURES). Architecture as
  PREREG_K_TH (decayed team yellow ratings, NB count, naive ensemble).
- Seed 2022/2023; dev scored 2023/2024–2024/2025 (n=447); virgin
  2025/2026 (n=240). Baselines: league base rate; naive trailing-10.
  Halves constant 0.3253.

## T-ZA (total shots) — shots family (J1 construction)

- Target total shots (stats feed, as published). Primary line **21.5**
  (scored-dev over-rate 0.522). Ladder 20.5/21.5/22.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble); **B** v2
  pattern (+ level layer); **C** E9 (NB r from trailing window),
  constructions as PREREG_T_TH / PREREG_T_J1.
- Seed 2022/2023; dev scored 2023/2024–2024/2025 (n=448); virgin
  2025/2026 (n=240). Baselines: league base rate; naive trailing-10.
  Halves constant 0.4584.
