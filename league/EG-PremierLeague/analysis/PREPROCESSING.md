# Phase 1 — Preprocessing: Egypt Premier League

The builder is complete and its CSV outputs are treated as immutable in this phase. It keeps finished FotMob rows, uses team IDs for identity, stores the 2024/2025 onward split as split_pooled, and stores all phases as ordinary match rows downstream.

- FT goals come from the header score.
- HT goals come from timed goal events; goal_event_time_coverage is retained and measured per season.
- Stats targets are the all-period stats feed: SOT, corners, total shots, stats yellows, reds, touches, possession, and big chances.
- Cards target is stats-feed yellow cards. Event yellow/yellow-red counts are audit columns only.
- Shotmap and stats xG are retained but are era-guarded: their usable era begins in virgin 2025/2026.
- Half fields are consumed only when present; no missing half is fabricated.
- eg_team_matches.csv is keyed by team ID and supplies for/against fields for reliability checks.

The output has **1,545** match rows and **3,090** team-match rows, as measured from the built files.
