# Verdict — K-CLA (Chile Liga de Ascenso cards) — **NOT BUILDABLE**

No prereg was written and nothing was fitted (TH-ThaiLeague2 /
ID-SuperLeague precedent for not-buildable candidates).

Era evidence (computed from payload content — the stats-vs-events
artefact check the program requires was run first, before any
fitting decision; `analysis/DATA_UNDERSTANDING.md`):

- **Stats source: does not exist.** The stats block is an empty
  shell in all 1,515 payloads (Periods.All null in all 483 flagged
  payloads; stats `None` elsewhere), so there is no stats
  `yellow_cards` value in any season to compare against — the
  comparison itself has no left-hand side.
- **Event source: era-truncated in the wrong direction.** The
  event feed is completely empty in 2021 (0 events in 246
  payloads). In 2022–2024 it carries card events **only of type
  Red and YellowRed — zero plain Yellow events in three full
  seasons** (YellowRed totals 51 / 50 / 38). Plain Yellow events
  exist only from 2025 (1,514 in 2025; 1,111 in the incomplete
  2026). This is the mirror image of the parent Primera artefact:
  there the *stats* feed undercounted; here the *event* feed
  omits plain yellows entirely for the whole dev era.
- An event-unified yellow target therefore exists only in 2025
  (the virgin candidate) and 2026 (incomplete). **No scorable dev
  window contains the target**, and a candidate cannot be gated
  without a dev window. No target definition is frozen, because
  no candidate is built; if a future warehouse refresh adds
  pre-2025 stats or plain-yellow events, the artefact check must
  be re-run and the target frozen in a new prereg before fitting.

K-CLA = NOT BUILDABLE (no dev window), recorded plainly, not forced.
