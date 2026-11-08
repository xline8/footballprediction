# CHECKPOINT — ES-LaLiga2 build HELD (user escalation 2026-11-09 18:30 WIB)

Coordinator order: all focus to Bulgaria Second League; this league is
held mid-Step-1. This file records exactly what was measured before the
hold so the build can resume without re-work. NO fitting has run, NO
prereg exists, NO data CSV has been built yet.

## State at hold
- Worktree: ~/workspace/wt-es-laliga2, branch build/es-laliga2 (from
  local/fotmob-source @ 2e71b52). No push, no merge.
- Step in progress when held: Step 1 (DATA_UNDERSTANDING) — raw
  warehouse inspection only. Steps 2–6 not started.

## Measured inventory (from data_enrichment/fotmob_world_index.csv, league_id=140)
- n = 2,478 matches. Seasons: 2021/2022–2025/2026 = 468 each;
  2026/2027 = 138 (in progress).
- 468/season = 462 regular (22 teams × 42 rounds) + 6 promotion
  play-off matches (matchRound "1/2" ×4 legs, "final" ×2 per index
  count) — phase-flag rule still to freeze at resume.
- has_stats: 100% in every season (2,478/2,478).
- has_period_splits: 2021/2022 = 1/468; 2022/2023 = 113/468;
  2023/2024, 2024/2025, 2025/2026, 2026/2027 = 100%.
- has_shotmap: 2021/2022 = 1, 2022/2023 = 3, 2023/2024 = 0,
  2024/2025 = 3, 2025/2026 = 468, 2026/2027 = 138 → 613/2,478 = 24.7%.
  Shotmap/xG effectively exists ONLY from 2025/2026. (Sample 2021
  JSON: stats Periods = ['All'] only, shotmap empty, Referee text
  empty.)
- LaLiga (id 87) also in warehouse: 380/season 2021/2022–2025/2026 +
  119 in 2026/2027 — mover (X2/SHRINK) analysis possible at resume.

## NOT yet measured (resume starts here, still Step 1)
- expected_goals key coverage in the stats feed per season (decides
  whether any xG arm is viable outside 2025/2026; brief's sanctioned
  fallback = goals Gate Zero on goals-only).
- Referee coverage per season; cards stats-vs-events agreement check
  (brief: run EARLY, dev-era evidence only).
- Stat-key inventory per season; HT goals source; team churn table.
- Virgin freeze choice (2025/2026 complete vs 2024/2025) — for preregs.

## Resume plan (unchanged from brief)
Full 6 steps per BRIEF_CONVEYOR_LEAGUE_TEMPLATE.md, ENG-Championship
as the worked analogue (2nd tier, play-offs, heavy churn). Preregs
before any fitting; virgin read once; gates mechanical.
