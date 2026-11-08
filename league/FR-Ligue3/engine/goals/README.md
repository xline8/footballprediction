# G-FR — goals engine (FR-Ligue3)

Dixon-Coles goals model, goals-only (no xG in this feed). Reference:
FI `dc.py` / `arms.py` carried over verbatim (sweep optimiser, 14
sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, rho
grid (0.0, −0.05, −0.10, −0.15), decay HL = 270 days). Harness adapted
from the FI harness + the IL naive trailing-10 baseline.

- Arms: `gate_zero`, `shrink` (n<6 prior in-league matches ⇒ a/d
  exponents scaled by n/6 at prediction).
- Baselines: climatology (prior-seasons pooled H/D/A rates + OU2.5
  over-rate) and naive trailing-10 (per-team trailing-10 goals-for
  means, independent Poissons, no home advantage).
- Dev: warm-up 2021, scored seasons 2022–2024 (n=1,066),
  season-blocked expanding fit. Virgin 2025 (n=364) read ONCE, only
  for dev-passing arms; 2026 untouched.
- Gates: see `prereg/PREREG_G_FR.md` (frozen before any fitting).

Run: `python3 run_g_no.py` (dev + gated virgin) or
`FR_DEV_ONLY=1 python3 run_g_fr.py` (dev only).

Outputs: `results_dev.json` (+ CSV), `results_virgin.json` (only if
Gate Zero passes dev), `fitted_params_virgin.json`,
`virgin_rows_<arm>.csv`.
