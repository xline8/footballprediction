# Pre-registration — S/C/K/T NOT BUILDABLE (Montenegro 1. CFL)

Frozen: 2026-11-10, in Phase A, before any fitting. This record is
committed alongside `PREREG_G_ME.md` so the not-buildable status of
the four non-goals candidates is on record BEFORE the dev harness
runs — it is not a post-hoc verdict written after results were seen.

Evidence authority: `analysis/DATA_UNDERSTANDING.md` §§1–2/§5 and
`analysis/EDA.md` (feasibility paragraph), measured on all 972
warehouse payloads (971 played matches) by `analysis/eda_compute.py`
(raw counts in `analysis/inventory_summary.json`).

## S-ME (shots on target) — NOT BUILDABLE

- Target does not exist. `content.stats` is None on all 972 rows,
  so there is no stats-feed `ShotsOnTarget` column.
- `content.shotmap` is `{"shots": [], "Periods": {"All": []}}` on
  all 972 rows: the shots list is empty everywhere (0/972 rows
  with shots > 0). There is no per-shot record from which SOT
  could be derived, in any season. The virgin window (2025/2026)
  contains no SOT target either, so the candidate could never be
  validated. NOT BUILT.

## C-ME (corners) — NOT BUILDABLE

- Target does not exist. No stats feed on any row (see S-ME), and
  no corner events exist in the payload — corners appear in this
  corpus only via the stats feed, which is absent. 0/971 rows carry
  a corner target. NOT BUILT.

## K-ME (cards) — NOT BUILDABLE

- Target does not exist. No stats feed (no `yellow_cards` key
  anywhere), and the event feed carries NO Yellow card events at
  all: across 971 played matches the Card events total 125 — Red
  74, YellowRed 51, Yellow 0. The provider omits yellows by design
  (same pattern as J3). The referee identity that the K-arm
  variant would need is also absent (`Referee.text` empty on all
  972 rows). Red-family counts (0.13/match) are a rare-event count
  and are not a modelling target. NOT BUILT.

## T-ME (total shots) — NOT BUILDABLE

- Target does not exist. Same evidence as S-ME: no stats feed, and
  the shotmap shots list is empty on all 972 rows. The v1/v2/E9
  reference family has no observation to fit on, and the virgin
  window contains no total-shots target. NOT BUILT.

## Consequence

The only buildable candidate in this league is G-ME (goals), frozen
in `PREREG_G_ME.md`. No engine, dev run, virgin read, predictions
file, or verdict file will be produced for S/C/K/T. If a future
FotMob pull ever populates stats/shotmap for this league, these four
candidates would need their own fresh six-step pass and prereg —
this record does not pre-authorize them.
