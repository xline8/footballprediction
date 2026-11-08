# Pre-registration — T-RS (RS-SuperLiga total-shots model): NOT BUILT

Frozen: 2026-11-10, before any fitting. Branch `wip-rs-superliga`.

T-RS is **not built**, by feasibility, recorded here so the absence is an
auditable decision and not an omission:

- Total shots exist ONLY in the virgin season. The stats feed is absent
  in every dev season (2021/2022–2024/2025: 0 stats rows in 1,192
  matches); `total_shots` first appears in 2025/2026 (inventory level
  25.084/match, `inventory_summary.json`). There is no dev total-shots
  series at all — not even a definition break to diagnose, because there
  is nothing on the dev side of the break.
- This is the FI T-FI precedent with ZERO rich-era dev seasons instead of
  one: FI ruled T-FI not-buildable because the rich-era quantity existed
  in exactly one dev season (2025), which cannot support the programme's
  season-blocked walk-forward dev protocol. RS has zero such seasons, so
  the ruling is stronger here — no dev definition check is even possible,
  and pooling is impossible because there is nothing to pool.
- No arm, window, or line is therefore frozen, nothing is fitted, and
  the virgin is not read for total shots. If a future season adds
  stats-era dev seasons, T-RS can be pre-registered fresh at that point
  — it may not be rescued inside this prereg.
