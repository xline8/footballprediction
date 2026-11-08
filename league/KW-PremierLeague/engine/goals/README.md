# G-KW — goals engine (KW-PremierLeague)

Dixon-Coles goals model, goals-only (no xG in this feed — no
`expected_goals*` key in any of the 711 payloads). Reference: `dc.py`
carried over verbatim (sweep optimiser, 14 sweeps, damping 0.7, +0.25
smoothing, home init 0.28, MAXG = 10, rho grid (0.0, −0.05, −0.10,
−0.15), decay HL = 270 days). Harness adapted from the BY harness +
the IL naive trailing-10 baseline. `arms.py` is identical to the
reference except the entrant rule uses the frozen canonical season
order (split-season labels are not integers) — documented divergence
in `prereg/PREREG_G_KW.md`.

- Arms: `gate_zero`, `shrink` (n<6 prior in-league matches ⇒ a/d
  exponents scaled by n/6 at prediction), `x2` (shrink + entrant
  offset from completed entrant transitions before the predicted
  season, clamped to [0.8, 1.25], 0 if fewer than 3 transitions).
- Baselines: climatology (prior-seasons pooled H/D/A rates + OU2.5
  over-rate) and naive trailing-10 (per-team trailing-10 goals-for
  means, independent Poissons, no home advantage).
- Dev: warm-up 2021 (calendar season, n=64), scored seasons
  2021/2022–2024/2025 (n=422), season-blocked expanding fit. Virgin
  2025/2026 (n=111) read ONCE, only for dev-passing arms; 2026/2027
  untouched.
- Gates: see `prereg/PREREG_G_KW.md` (frozen before any fitting).

Run: `python3 run_g_kw.py` (dev + gated virgin) or
`KW_DEV_ONLY=1 python3 run_g_kw.py` (dev only).
