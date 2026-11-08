# Features and decisions — Lithuania Toplyga

The J1 X1–X9 template is judged against this corpus. MODEL_DESIGN may use
only adopted items.

- **X1 blend — ADOPTED as the goals-only fallback.** No xG exists in any of
  1,044 rows; the fallback is the whole design.
- **X2 mover prior — DROPPED.** No Lithuanian sibling/1 Lyga warehouse data
  exists, so no measurable cross-tier prior exists. New ids enter at the
  league mean; SHRINK is the thin-data treatment instead.
- **X3 set-play — DROPPED; X4 xG/shot — DROPPED; X6 xGOT — DROPPED.** No xG
  or shotmap exists (coverage check n=1,044).
- **X5 trailing target-rate means — ADOPTED only as the naive goals baseline
  component.** It is not an extra claim about Dixon-Coles.
- **X7 box touches — DROPPED; X9 territorial — DROPPED.** No stats feed.
- **X8 referee — DROPPED.** Referee text is empty in all 1,044 rows.

Rejected: half-share modelling (F3 is at/below its binomial noise floor),
finishing/conversion, lineup/absence, standings or H2H snapshots, attendance,
and red cards as a target. These lack data or create leakage/rare-event
targets. The frozen half constant is presentation-only and never a feature.
