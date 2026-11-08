# Features and decisions — Montenegro 1. CFL

The J1 X1–X9 template is judged against this corpus. MODEL_DESIGN may use
only adopted items.

- **X1 blend — ADOPTED as the goals-only fallback.** No xG exists in any of
  971 played rows; the fallback is the whole design.
- **X2 mover prior — DROPPED.** No Montenegrin sibling league exists in the
  warehouse (only league id 232 under country Montenegro), so no
  measurable cross-tier prior exists. New ids enter at the league mean;
  SHRINK is the thin-data treatment instead.
- **X3 set-play — DROPPED; X4 xG/shot — DROPPED; X6 xGOT — DROPPED.** No xG
  or shotmap exists (coverage check n=971: stats null on all rows,
  shotmap shots list empty on all rows).
- **X5 trailing target-rate means — ADOPTED only as the naive goals baseline
  component.** It is not an extra claim about Dixon-Coles. (For the
  count markets X5 would serve — SOT, corners, yellows — the targets
  do not exist, so X5 has no other consumption here.)
- **X7 box touches — DROPPED; X9 territorial — DROPPED.** No stats feed.
- **X8 referee — DROPPED.** Referee text is empty in all 972 rows.

Rejected: half-share modelling (F3 is at/below its binomial noise floor —
observed variance 0.117898 vs noise 0.122492, true variance −0.004594),
finishing/conversion, lineup/absence, standings or H2H snapshots,
attendance, and red cards as a target (0.13/match is a rare-event count;
the production cards design excludes reds too). These lack data or
create leakage/rare-event targets. The frozen half constant (0.426643)
is presentation-only and never a feature.
