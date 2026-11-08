# Phase 2 — Preprocessing

Builder: `data/build_data.py`. It resolves index paths against the repository
warehouse, otherwise `/home/hatch/workspace/footballprediction` read-only.
The generated CSVs are gitignored; the builder is the artefact.

## Inclusion rules

- Include finished matches only. All 394 are finished, so none are dropped.
- Enforce one row per match id and use the official `scoreStr` FT score.
- Preserve warehouse season labels and add `season_start` for ordering.
- Set `phase = regular` for every row; no split-group logic is applicable.
- Key teams by FotMob id and canonicalize display names by frequency (no
  variants exist, so canonicalization is a no-op here).

## Split-source rules

HT goals come only from a `Half` marker with `halfStrShort=HT`. The marker is
cross-checked against goal-event times ≤45: 363/363 agree (31 goalless first
halves are unchecked by construction, not missing). All ALL_STATS columns are
retained and null. The CSV `has_lineup` column is hardcoded False by the
builder (inherited from the AZ template); the payload-level check in `eda.py`
finds 11 starters on both sides in 394/394, but lineups are not used as a
feature — see FEATURES R6/R8. Referee is null
except 33 matches; `has_referee` reflects that. Event-derived Red, YellowRed,
and Yellow counts are retained, while unified yellow/red columns remain null
because there is no complete target source.

The two outputs are one row per match (394) and one row per team-match (788).
No fitting, imputation, standings, h2h, playerStats, or post-match snapshots
are added. The 2022/2023 rounds-1–3 gap is preserved as-is: no matches are
synthesised to fill it.
