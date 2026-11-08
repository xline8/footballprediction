# Step 6 — Model Design: TH-ThaiLeague

Feasibility: goals everywhere; SOT / corners / cards / total shots have
their target in the stats era (from 2022/2023) AND in the virgin 2025/2026,
so all five candidates are buildable. Windows frozen in PREPROCESSING.
Calibration = actual − predicted. Gate legs identical across candidates
(dev gate vs baselines; virgin LL leg + calibration leg |breach| ≤ 1pp
clean, ≤ 1 SE provisional, else FAIL; both-pass → lower virgin LL ships;
Gate Zero dev failure ⇒ candidate FAILS, virgin NOT read).

## G-TH (goals) — Dixon-Coles, goals-only (X1 dropped)

- Reference: production `model_v2.py` DC pattern as frozen in the
  RU-1Division goals prereg (hl=270, 14 sweeps, damping 0.7, +0.25
  smoothing, rho grid, season-blocked expanding fit).
- Arms: **Gate Zero**; **SHRINK** (sanctioned G-J2-lesson arm: ratings of
  teams with <6 prior in-league matches shrunk a,d *= n/6; motivated by
  the X2 mover gaps, GF −0.262 / GA +0.503).
- Dev: seed-fit on 2021/2022, evaluate 2022/2023–2024/2025 (n=720).
  Virgin: 2025/2026 (n=240). Primary metrics 1X2 LL/RPS + OU2.5 LL vs
  climatology. Halves via frozen goals constant 0.4402.

## S-TH (SOT) — production v5 pattern

- Target total SOT (stats feed). Primary line **9.5** (scored-dev
  over-rate 0.473). Ladder 8.5/9.5/10.5.
- Arms: **Gate Zero** (v5 unmodified, constants as PREREG_S_RU1);
  **RS** (Beta-Binomial prior P 200 → 20,000).
- Per-match walk-forward: warm-up 2022/2023 updates state, never scored;
  dev scored 2023/2024–2024/2025 (n=480); virgin 2025/2026 (n=240).
  Baselines: league base rate; naive trailing-10. Halves constant 0.4447.

## C-TH (corners) — production v3 pattern (J1 construction)

- Target total corners (stats feed). Primary line **9.5** (scored-dev
  over-rate 0.498). Ladder 8.5/9.5/10.5.
- Arms: **Gate Zero (X9)** — core `mu_cs` + territorial multiplier from
  possession + big chance (beta grids as PREREG_C_J1);
  **X7** — identical engine, territorial covariate = opp-box touches
  (beta grid as PREREG_C_J1; arm inactive where trailing touches missing).
- Per-season gamma/beta/r fitting on prior walk-forward rows only, as in
  the J1/RU preregs. Seed 2022/2023; dev scored 2023/2024–2024/2025
  (n=480); virgin 2025/2026 (n=240). Baselines: league base rate
  (per-season NB) and naive trailing-10. Halves constant 0.4622.

## K-TH (cards) — production cards pattern

- Target total **stats-feed yellows** (frozen in Step 1/2: dev-era events
  carry no plain yellows, so no event target exists in dev; virgin
  event-unified sensitivity preregistered, gate on stats target).
  Primary line **4.5** (scored-dev over-rate 0.438). Ladder 3.5/4.5/5.5.
- Arms: **Gate Zero only** (X8 dropped — FEATURES). Architecture as
  PREREG_K_RU1 (decayed team yellow ratings, NB count, naive ensemble).
- Seed 2022/2023; dev scored 2023/2024–2024/2025 (n=480); virgin
  2025/2026 (n=240). Baselines: league base rate; naive trailing-10.
  Halves constant 0.3076.

## T-TH (total shots) — shots family (J1/RU construction)

- Target total shots (stats feed, as published). Primary line **26.5**
  (scored-dev over-rate 0.494). Ladder 25.5/26.5/27.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble); **B** v2
  pattern (+ level layer); **C** E9 (NB r from trailing window),
  constructions as PREREG_T_RU1 / PREREG_T_J1.
- Seed 2022/2023; dev scored 2023/2024–2024/2025 (n=480); virgin
  2025/2026 (n=240). Baselines: league base rate; naive trailing-10.
  Halves constant 0.4522.
