# Pre-registration — S/C/K/T-WAL: NOT BUILDABLE

Frozen: 2026-11-10, before any fitting. Branch `build/wal-cymru-premier`.
This prereg records the NOT BUILDABLE decisions for the four non-goals
candidates. All 1,103 Phase A payloads were read for this evidence.

**No fitting is done for these candidates.**

## Evidence (payload-verified 2026-11-10, all 1,103 payloads read)

- **S-WAL (shots on target):** SOT exists in **0/1,103** payloads.
  `content.stats` is null in 1,103/1,103; `content.shotmap.shots` is empty
  in 1,103/1,103. No SOT target exists.
- **C-WAL (corners):** corners exists in **0/1,103** payloads (same empty
  stats feed). No corners target exists.
- **K-WAL (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/1,103 payloads. Card events number 234
  in total — **all of them dismissals** (Red 154, YellowRed 80; **0 plain
  Yellow events**). The referee field is empty in 1,103/1,103 payloads
  (`infoBox.Referee` text always `''`), so referee strictness (X8) is
  unmeasurable as well. Dismissals are not yellows and are not modelled as
  a substitute target.
- **T-WAL (total shots):** `total_shots` / shot counts exist in **0/1,103**
  payloads (same empty stats feed and shotmap). No total-shots target exists.

Stats are null and shotmaps empty in all 1,103 payloads; coverage was
measured by payload content, regardless of index flags.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: there is no dev n > 0 because the
  targets do not exist. No team trait, rating or naive baseline can be
  computed.
- Virgin = season 2025/2026 (192 eligible matches): **NOT READ** for S/C/K/T,
  deliberately unread. Calibration is not attempted.
- No pooled or proxy rescue: no season and no stage carries the targets, so
  no subset of the warehouse rescues any candidate.

## Registered decisions

- Arms: **none**.
- Primary lines: **none chosen**.
- Virgin window (2025/2026): **NOT READ** for S/C/K/T — deliberately unread.
- Halves constants: **none** for SOT/corners/cards/total shots (no splits
  exist for targets that do not exist).

## Verdict

S-WAL, C-WAL, K-WAL, T-WAL are **NOT BUILDABLE**. No engine, results, or
predictions are produced for these four candidates.
Production code untouched. No push. No merge.
