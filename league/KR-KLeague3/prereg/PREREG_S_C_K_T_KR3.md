# Pre-registration — S/C/K/T-KR3 (K League 3 non-goals markets):
# NOT BUILDABLE (frozen before any fitting)

Frozen 2026-11-10 before any fitting. No model is fitted, no dev
gate is run, and the virgin is not read for any of these four
candidates. Reason, verified from payloads (see
`analysis/DATA_UNDERSTANDING.md` and `analysis/eda_summary.json`):

- S-KR3 (shots on target): the target exists in NO season at all —
  0 of 1,296 payloads carry a stats feed (0 in dev, 0 in the virgin,
  0 in the reserve); the shotmap is empty in all 1,296 payloads. No dev season, no warm-up season, no scored
  dev window, no trait reliability, no 1H share.
- C-KR3 (corners): same — corners exist in NO season (stats null in
  all 1,296 payloads).
- T-KR3 (total shots): same — total shots exist in NO season (stats
  null and shotmap empty in all 1,296 payloads).
- K-KR3 (cards / yellows): the yellows target exists in NO season
  under either source. The stats feed carries no `yellow_cards` key
  in any payload (stats null in all 1,296). The event feed carries
  ZERO plain Yellow card events in all 1,296 matches — only Red (84)
  and YellowRed (57) events, 141 red-card events in 1,288 played
  matches (~0.11/match), far too rare for a 2.5 line. An
  event-unified yellow target is therefore impossible, exactly as in
  the CN-LeagueOne precedent.

Windows that would have applied (for the record only): dev seed 2021,
scored 2022–2024; virgin complete 2025; confirmatory 2026 in progress
and reserved. Nothing ships for S/C/K/T-KR3.
