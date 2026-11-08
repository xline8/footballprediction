# G-BY — goals engine (BY-PremierLeague)

Dixon-Coles goals model, goals-only (no xG in this feed). Reference:
FI `dc.py` / `arms.py` carried over verbatim (sweep optimiser, 14
sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, rho
grid (0.0, −0.05, −0.10, −0.15), decay HL = 270 days). Harness adapted
from the FI harness + the IL naive trailing-10 baseline.

- Arms: `gate_zero`, `shrink` (n<6 prior in-league matches ⇒ a/d
  exponents scaled by n/6 at prediction), `x2` (shrink + entrant
  offset from completed entrant transitions before the predicted
  season, clamped to [0.8, 1.25], 0 if fewer than 3 transitions).
- Baselines: climatology (prior-seasons pooled H/D/A rates + OU2.5
  over-rate) and naive trailing-10 (per-team trailing-10 goals-for
  means, independent Poissons, no home advantage).
- Dev: warm-up 2021, scored seasons 2022–2024 (n=690),
  season-blocked expanding fit. Virgin 2025 (n=240) read ONCE, only
  for dev-passing arms; 2026 untouched.
- Gates: see `prereg/PREREG_G_BY.md` (frozen before any fitting).

Run: `python3 run_g_by.py` (dev + gated virgin) or
`BY_DEV_ONLY=1 python3 run_g_by.py` (dev only).
