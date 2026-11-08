# Phase A2 — Preprocessing

`data/build_data.py` creates `data/cn_matches.csv` (one row per match) and
`data/cn_team_matches.csv` (two rows per match). Existing Phase A outputs are
consumed as frozen inputs here; they are not rebuilt.

## Derivation rules

1. Full-time goals come from the official score. First-half goals come from
   goal events at minute ≤45. Team statistics are taken from the `All`,
   `FirstHalf`, and `SecondHalf` stats periods without imputation.
2. Missing feed content is missing, not zero. The phase flag is retained.
3. Team identity is the provider team id, so display renames do not create
   artificial teams. The examples are listed in `inventory_summary.json`.
4. Stats conflicts are counted and preserved; the inventory reports zero
   conflicts. Score/event agreement is 99.17% overall.

## Cards artefact and frozen target

The target is stats-feed `yellow_cards_home + yellow_cards_away` in both dev
and virgin. This is deliberate and frozen. In 2023–2026 stats and event
counts agree in 82.5–90.42% of matches, with mean stats-minus-events
differences from −0.15 to −0.03 per match. In 2021–2022 the feed undercounts
by −0.81 and −0.57 per match and agrees only 69.32% and 73.49% of the time.
The event-unified count remains a documented sensitivity analysis, not the
gate target. Cards half shares use the stats split constant 0.3328; the
all-season event check is 0.3398.

## Coverage caveats

Referee identity coverage collapses from 92.08% in 2024 to 64.58% in 2025
and 48.75% in 2026, so referee features cannot be used at prediction time.
Opp-box touches cover 54.58% of 2023 warm-up matches and 100% from 2024.
The X7 arm therefore needs at least eight prior matches carrying the stat;
otherwise the match falls back to Gate Zero.

No expected-goals key or shotmap exists in this corpus. There is no silent
repair, cross-era imputation, or FT-only halves exception.
