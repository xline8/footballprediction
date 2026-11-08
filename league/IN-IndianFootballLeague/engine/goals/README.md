# G-IN — goals engine (IN-IndianFootballLeague)

Dixon-Coles goals model, goals-only (no xG in this feed). Reference:
FI `dc.py` carried over verbatim (sweep optimiser, 14 sweeps,
damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, rho grid
(0.0, -0.05, -0.10, -0.15), decay HL = 270 days); `arms.py` carries
the FI adjusted_lambdas / match_counts mechanics for the two G-IN
arms. Harness adapted from the FI harness + the IL naive
trailing-10 baseline.

- Arms: `gate_zero`, `shrink` (n<6 prior in-league matches => a/d
  exponents scaled by n/6 at prediction). There is NO `x2` arm:
  the entrant offset was dropped pre-fitting (EDA F4: 6 dev
  transitions, mean GF -0.110 / GA +0.025, signs mixed).
- Baselines: climatology (prior-seasons pooled H/D/A rates + OU2.5
  over-rate) and naive trailing-10 (per-team trailing-10 goals-for
  means, independent Poissons, no home advantage).
- Dev: warm-up 2021/2022, scored seasons 2022/2023-2024/2025
  (n=418), season-blocked expanding fit. Virgin 2025/2026 (n=66)
  read ONCE, only for dev-passing arms; 2026/2027 untouched.
- Gates: see `prereg/PREREG_G_IN.md` (frozen before any fitting).

Run: `python3 run_g_in.py` (dev + gated virgin) or
`IN_DEV_ONLY=1 python3 run_g_in.py` (dev only).
