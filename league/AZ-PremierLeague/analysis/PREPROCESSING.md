# Phase 2 — Preprocessing

Builder: `data/build_data.py`. It resolves index paths against the repository
warehouse, otherwise `/home/hatch/workspace/footballprediction` read-only.
The generated CSVs are gitignored; the builder is the artefact.

## Inclusion rules

- Include finished matches only. All 914 are finished, so none are dropped.
- Enforce one row per match id and use the official `scoreStr` FT score.
- Preserve warehouse season labels and add `season_start` for ordering.
- Set `phase = regular` for every row; no split-group logic is applicable.
- Key teams by FotMob id and canonicalize display names by frequency.

## Split-source rules

HT goals come only from a `Half` marker with `halfStrShort=HT`. They are not
fabricated for the 70 event-less matches. The marker is cross-checked against
goal-event times ≤45: 844/844 agree. All ALL_STATS columns are retained and
null. `has_lineup` is always false; referee is null and `has_referee` false.
Event-derived Red, YellowRed, and Yellow counts are retained, while unified
yellow/red columns remain null because there is no complete target source.

The two outputs are one row per match (914) and one row per team-match (1,828).
No fitting, imputation, standings, h2h, playerStats, or post-match snapshots
are added.
