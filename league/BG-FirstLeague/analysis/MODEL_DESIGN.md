# Step 6 — Model Design: BG-FirstLeague

Feasibility: goals everywhere; SOT / corners / cards / total shots
have their target in the data from 2021/2022 AND in the virgin
2025/2026, so all five candidates are buildable. Windows frozen in
PREPROCESSING (Step 2). Calibration = actual − predicted. Gate legs
identical across candidates (dev gate vs baselines; virgin LL leg +
calibration leg |breach| ≤ 1pp clean PASS, ≤ 1 SE PROVISIONAL PASS,
else FAIL; both-pass → lower virgin LL ships, ties → simpler arm;
Gate Zero dev failure ⇒ candidate FAILS, virgin NOT read).

Phase rule (frozen, Step 1/2): all phases (regular, championship
play-off, ECL group, relegation group, ECL play-off) are in every
window, flagged by the `phase` column; no phase feature anywhere.

## G-BG (goals) — Dixon-Coles, goals-only (X1 dropped)

- Reference: production `model_v2.py` DC pattern as frozen in the
  TH/ZA goals preregs (hl=270, 14 sweeps, damping 0.7, +0.25
  smoothing, rho grid, season-blocked expanding fit).
- Arms: **Gate Zero**; **SHRINK** (programme-sanctioned G-J2-lesson
  arm: ratings of teams with <6 prior in-league matches shrunk
  a,d *= n/6; motivated by the mover gaps GF −0.205 / GA +0.399
  measured against the real tier-2 corpus).
- Dev: seed-fit on 2021/2022, evaluate 2022/2023–2024/2025 (n=859).
  Virgin: 2025/2026 (n=293). Metrics 1X2 LL/RPS + OU2.5 LL vs
  climatology. Halves via frozen goals constant 0.4542.

## S-BG (SOT) — production v5 pattern

- Target total SOT (stats feed). Primary line **8.5** (scored-dev
  over-rate 0.458). Ladder 7.5/8.5/9.5.
- Arms: **Gate Zero** (v5 unmodified, constants as the TH/ZA SOT
  preregs); **RS** (Beta-Binomial prior P 200 → 20,000).
- Per-match walk-forward: warm-up 2021/2022 updates state, never
  scored; dev scored 2022/2023–2024/2025 (stats rows n=841); virgin
  2025/2026 (n=293). Baselines: league base rate; naive trailing-10.
  Halves: **FT-only** (no halves source).

## C-BG (corners) — production v3 pattern (J1 construction)

- Target total corners (stats feed). Primary line **9.5**
  (scored-dev over-rate 0.467). Ladder 8.5/9.5/10.5.
- Arms: **Gate Zero (X9)** — core `mu_cs` + territorial multiplier
  from possession + big chance (beta grids as PREREG_C_J1). Recorded
  in advance: `big_chance` does not exist in this league, so this
  multiplier is inactive on every row and Gate Zero reduces to the
  core — reported as such, not patched. **POSS** — identical engine,
  territorial multiplier from possession alone (beta_poss grid
  ±{0, .01, .02, .03, .04} as in the J1 possession grid, multiplier
  clamped [0.70, 1.43]); X7 (box touches) does not exist here.
- Per-season gamma/beta/r fitting on prior walk-forward rows only,
  as in the J1/TH/ZA preregs; the fitting objective is at THIS
  league's primary line (9.5) everywhere. Seed 2021/2022; dev scored
  2022/2023–2024/2025 (n=841); virgin 2025/2026 (n=293). Baselines:
  league base rate (per-season NB) and naive trailing-10.
  Halves: **FT-only**.

## K-BG (cards) — production cards pattern

- Target total **event-unified yellows** (direct Yellow + YellowRed,
  frozen in Step 1: the stats feed publishes no yellow key at all,
  so no stats-vs-events conflict exists; the event feed carries
  plain yellows in every season). Primary line **4.5** (scored-dev
  over-rate 0.561). Ladder 3.5/4.5/5.5.
- Arms: **Gate Zero** (decayed team yellow ratings, NB count, naive
  ensemble, as the RU/TH cards preregs); **X8** — Gate Zero plus the
  referee multiplier of the shared cards model (trailing referee
  yellow rate, K_REF = 8 shrinkage, multiplier clamped [0.67, 1.50],
  min 8 prior in-league matches else fallback to Gate Zero for that
  match), justified by referee strictness r = 0.379 at ~100%
  coverage (X8, Step 5).
- Seed/warm-up 2021/2022; dev scored 2022/2023–2024/2025 (n=859);
  virgin 2025/2026 (n=293). Baselines: league base rate; naive
  trailing-10. Halves via frozen cards constant 0.3183.

## T-BG (total shots) — shots family (J1 construction)

- Target total shots (stats feed, as published). Primary line
  **17.5** (scored-dev over-rate 0.473). Ladder 16.5/17.5/18.5.
- Arms: **A** v1 pattern (ratings + NB + naive ensemble); **B** v2
  pattern (+ level layer); **C** E9 (NB r from trailing window),
  constructions as the TH/ZA total-shots preregs, retargeted to this
  league's line.
- Seed/tuning 2021/2022; dev scored 2022/2023–2024/2025 (n=841);
  virgin 2025/2026 (n=293). Baselines: league base rate; naive
  trailing-10. Halves: **FT-only**.
