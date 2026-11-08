# G-FI — goals engine (FI-Ykkonen)

Dixon-Coles goals model, goals-only (no xG in this feed). Reference:
FI `dc.py` / `arms.py` carried over verbatim (sweep optimiser, 14
sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, rho
grid (0.0, −0.05, −0.10, −0.15), decay HL = 270 days). Harness adapted
from the FI harness + the IL naive trailing-10 baseline. Port template:
NO-2Divisjon `engine/goals/` (proven).

- Arms: `gate_zero`, `shrink` (n<6 prior in-league matches ⇒ a/d
  exponents scaled by n/6 at prediction), `x2` (shrink + frozen
  entrant multipliers g_log −0.182 / c_log +0.223, EDA F4, 22 dev
  transitions).
- Baselines: climatology (prior-seasons pooled H/D/A rates + OU2.5
  over-rate) and naive trailing-10 (per-team trailing-10 goals-for
  means, independent Poissons, no home advantage).
- Dev: warm-up 2021, scored seasons 2022–2024 (n=1,010),
  season-blocked expanding fit. Virgin 2025 (n=162) read ONCE, only
  for dev-passing arms; 2026 untouched.
- Split: Jarvis OPSI A (board comment 6761468990) — dev ≤ 2024
  as-is; Kakkonen 2021–2023 / Ykkönen 2024–2026 structure recorded
  in `prereg/PREREG_G_FI.md`.
- Gates: see `prereg/PREREG_G_FI.md` (frozen before any fitting).

Run: `python3 run_g_fi.py` (dev + gated virgin) or
`FI_DEV_ONLY=1 python3 run_g_fi.py` (dev only).

Outputs: `results_dev.json` (+ CSV), `results_virgin.json` (only if
Gate Zero passes dev), `fitted_params_virgin.json`,
`virgin_rows_<arm>.csv`.
