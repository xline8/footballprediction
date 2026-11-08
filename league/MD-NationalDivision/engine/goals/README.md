# G-MD — goals engine (MD-NationalDivision)

Dixon-Coles goals model, ported verbatim from the programme
reference (`dc.py` / `arms.py`: iterative sweep optimiser, 14
sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10,
production tau, rho grid (0.0, −0.05, −0.10, −0.15) by goals
log-likelihood, decay HL = 270 days). Observation is goals-only in
every match — the X1 blend's documented fallback, since no xG
exists in this feed (no `expected_goals*` key in any of 556
payloads, no shotmap). One port adaptation: `arms.py` season arithmetic compares season start years (split-season labels "2021/2022"), mechanics unchanged.

- Arms: `gate_zero`, `shrink` (n<6 prior-match shrink), `x2`
  (entrant offset, rule-based; see `prereg/PREREG_G_MD.md`).
- Baselines: climatology (training-pooled rates) and naive
  trailing-10 (IL precedent).
- Dev: warm-up 2021/2022, scored seasons 2022/2023–2024/2025
  (n=258), season-blocked expanding fit. The dev harness never
  reads 2025/2026 or 2026/2027 rows.
- Virgin: 2025/2026 read ONCE, only if Gate Zero passes the dev
  gate (`run_g_md.py` enforces this).
- Gates: see `prereg/PREREG_G_MD.md` (frozen before any fitting).

Run: `python3 run_g_md.py`, or dev only:
`MD_DEV_ONLY=1 python3 run_g_md.py`.
