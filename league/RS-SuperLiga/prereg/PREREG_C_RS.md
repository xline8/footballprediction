# Pre-registration — C-RS (RS-SuperLiga corners model): NOT BUILT

Frozen: 2026-11-10, before any fitting. Branch `wip-rs-superliga`.

C-RS is **not built**, by feasibility, recorded here so the absence is an
auditable decision and not an omission:

- Corners exist ONLY in the virgin season. The stats feed is absent in
  every dev season (2021/2022–2024/2025: 0 stats rows in 1,192 matches);
  corners first appear in 2025/2026 (inventory level 9.003/match,
  `inventory_summary.json`). There is no dev corners series at all.
- The corners reference pattern (Poisson ratings + NB with X7 multiplier)
  needs the X7 box-touches/territory input. X7 is dropped: `touches_opp_box`
  exists only in the virgin season, so a corners arm needing trailing
  touches across the dev walk-forward would be NaN for every dev season.
  Even the FI fallback of a possession-only covariate is unavailable:
  `BallPossesion` is also virgin-only.
- The conveyor feasibility rule requires the target to exist AND a valid
  virgin window to contain it. The virgin (2025/2026) does contain the
  target — but a dev gate can only validate an arm against the SAME
  quantity, and the quantity exists in exactly ZERO dev seasons. No
  season-blocked walk-forward dev protocol is possible.
- No arm, window, or line is therefore frozen, nothing is fitted, and
  the virgin is not read for corners. If a future season adds stats-era
  dev seasons, C-RS can be pre-registered fresh at that point — it may
  not be rescued inside this prereg.
