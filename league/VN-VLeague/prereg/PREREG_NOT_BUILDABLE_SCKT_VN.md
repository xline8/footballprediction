# Pre-registration — S/C/K/T NOT BUILDABLE (Vietnam V-League)

Frozen: 2026-11-10, before any fitting. Branch `build/vn-vleague`.
This prereg records, in Phase A, that four of the five candidate
markets are not buildable in this league, with the measured evidence
for each. No engine, no dev run, and no virgin read exists or will
exist for these markets under this prereg. If the warehouse ever gains
the missing targets (e.g. a stats feed for a future season), a new
prereg is required — this document is not amended after results.

Evidence base: `analysis/DATA_UNDERSTANDING.md` §2/§5,
`analysis/eda.py` + `analysis/inventory_summary.json` (content-measured
coverage, all 969 payloads), `analysis/EDA.md` F5/F9.

## S — shots on target: NOT BUILDABLE

- Target absent in every season: stats `Periods` empty in 969/969
  payloads; shotmap shot list empty in 969/969. No SOT value exists
  anywhere in the corpus — neither a stats-feed value nor a shotmap
  from which one could be derived.

## C — corners: NOT BUILDABLE

- Target absent in every season: no corners stat (stats feed empty),
  no corner events in any payload. Same evidence as S.

## T — total shots: NOT BUILDABLE

- Target absent in every season: no total-shots stat, no shotmap
  shots (0 shots in 969/969 payloads). Same evidence as S.

## K — cards: NOT BUILDABLE

- The only card signal is the event feed, and it is not a target:
  plain-Yellow events are **0 in 2021, 2022, 2023, and 2023/2024
  (0/556 matches)** and appear only from 2024/2025 (609, 606, 139
  events in 2024/2025, 2025/2026, 2026/2027). A cards model would
  have no yellow target at all in any dev season, so no valid virgin
  window contains the target either.
- Red / YellowRed events exist throughout but are rare (46–52 per
  season pre-2024/2025, 0.08–0.29 per match) and the production
  cards design excludes reds as a target.
- No named referee exists in any payload (infoBox Referee text is
  the empty string in 969/969), so the X8 referee arm is unavailable
  as well.

## Consequence

The only candidate is G-VN (goals), preregistered separately in
`PREREG_G_VN.md`. No S/C/K/T verdict files will be written; this
document is the verdict for those four markets.
