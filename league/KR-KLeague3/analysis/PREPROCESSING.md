# Phase 2 — Preprocessing: KR-KLeague3

Source and inventory checks are recorded in `DATA_UNDERSTANDING.md`; measured
values are from `eda_summary.json`.

Inclusion rules are frozen as follows:

- The warehouse index is the starting population. Retain a match only when
  `started=True` and `finished=True`, with a played final score. This yields
  1,288 played rows from 1,296 index rows.
- Cross-check the index score against the payload/header score and the header
  home/away teams before retaining a row. A disagreement is an audit failure,
  not an imputation opportunity.
- Keep playoff rows in the CSV with `phase=playoff`, but use
  `phase=regular` as the population for every model, level, reliability,
  fitting, and scoring calculation. The four 2021 playoff rows are therefore
  frozen out of all modelling populations.
- Use the warehouse season labels unchanged: calendar years 2021–2026.
- Team identity is the FotMob team ID. Names are canonicalized to the most
  frequent observed name for each ID; variants remain auditable in the raw
  row/source inventory.
- Derive half-time goals from event times only when the goal-event lists
  reconcile to the final score. Never fabricate half-time goals for the 55
  unreconciled early-2021 regular matches, and never infer them from a score
  alone.
- Stats, period splits, shotmaps, xG, lineups, and referee fields are absent
  in the verified corpus and are not imputed or synthesized.

The goals model population is therefore regular, played, score-checked rows
only. The 2021 unplayed placeholders are excluded before any target or phase
calculation.

