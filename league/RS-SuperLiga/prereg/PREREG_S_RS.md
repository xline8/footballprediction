# Pre-registration — S-RS (RS-SuperLiga shots-on-target model): NOT BUILT

Frozen: 2026-11-10, before any fitting. Branch `wip-rs-superliga`.

S-RS is **not built**, by feasibility, recorded here so the absence is an
auditable decision and not an omission:

- Shots on target exists ONLY in the virgin season. The stats feed is
  absent in every dev season (2021/2022–2024/2025: 0 stats rows in 1,192
  matches); ShotsOnTarget first appears in 2025/2026 (inventory level
  8.831/match, `inventory_summary.json`). There is no dev SOT series at
  all — not one season, unlike FI, which had a thin-era SOT series.
- The v5 reference pattern (joint ridge Poisson + Negative Binomial +
  Beta-Binomial on-target ratio) needs trailing SOT features and an
  on-target ratio input (X4). X4 is impossible here: there is no shotmap
  in any season and no xG in any season, so no on-target ratio input
  exists in dev either.
- The conveyor feasibility rule requires the target to exist AND a valid
  virgin window to contain it. The virgin (2025/2026) does contain the
  target — but a dev gate can only validate an arm against the SAME
  quantity, and the quantity exists in exactly ZERO dev seasons. No
  season-blocked walk-forward dev protocol is possible.
- No arm, window, or line is therefore frozen, nothing is fitted, and
  the virgin is not read for shots on target. If a future season adds
  stats-era dev seasons, S-RS can be pre-registered fresh at that point
  — it may not be rescued inside this prereg.
