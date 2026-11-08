# S-TR1 / C-TR1 / K-TR1 / T-TR1 — NOT BUILDABLE (complete outcomes)

Ruling frozen in `analysis/MODEL_DESIGN.md` before any fitting.
No engine was built, no model was fitted, and the 2025/2026 virgin
was NOT read for any of these candidates.

## Era facts (from `analysis/eda_numbers.json`, full corpus)

Stats-feed coverage by season (index rows): 2021/2022 0/347,
2022/2023 0/347, 2023/2024 2/311, 2024/2025 179/385 (Aug 2024–
Jan 2025 only; the feed dies in Feb 2025), 2025/2026 385/385,
2026/2027 139/139 (partial, reserved). Shotmap exists only in the
2024/2025 fragment (177) and is zero in the virgin season.

## Per candidate

- **S-TR1 (SOT), C-TR1 (corners), T-TR1 (total shots):** the target
  exists only in the ≤179-row Aug24–Jan25 fragment plus the virgin
  season. There is no stats seed season, trailing-10 features
  cannot fill across the fragment boundary, and no season-blocked
  dev window exists. A market whose only scorable history sits in
  a partial fragment + the virgin is not buildable under the
  program's gate structure — recorded, not forced.
- **K-TR1 (cards):** the stats target has the same fragment
  problem, and the event-feed fallback is invalid in this league:
  event yellows are 0.0 per match in every season including the
  overlap era; in the 558 overlap matches with stats, stats−events
  mean difference is +4.272 yellows, exact agreement 2.3%, stats
  higher in 97.7%. The event feed carries no usable card signal
  here (unlike J2/TR-SuperLig), so no all-season target exists.

A future build becomes possible only if FotMob backfills stats
for a full pre-virgin season (giving a seed + dev window) or a new
complete season closes as a fresh virgin under a new prereg.
