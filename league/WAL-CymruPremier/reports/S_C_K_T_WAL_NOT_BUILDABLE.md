# Verdict — S/C/K/T-WAL: NOT BUILDABLE

Prereg `league/WAL-CymruPremier/prereg/PREREG_SCKT_WAL_NOT_BUILDABLE.md`
(commit `9497178d`). Branch `build/wal-cymru-premier`. No engine,
results, or predictions exist for these four candidates — there is nothing
to fit.

## Evidence (all 1,103 Phase A payloads read)

- **S-WAL (shots on target):** SOT exists in **0/1,103** payloads.
  `content.stats` is null in 1,103/1,103 and `content.shotmap.shots` is
  empty in 1,103/1,103.
- **C-WAL (corners):** corners exist in **0/1,103** payloads; the stats feed
  is null and the shotmap is empty throughout.
- **K-WAL (cards):** no yellow-card target exists. The 234 card events are
  all dismissals (Red 154, YellowRed 80, 0 plain Yellow). The referee field
  is empty in 1,103/1,103. Dismissals are not yellows and are not modelled
  as a substitute target.
- **T-WAL (total shots):** total shots exist in **0/1,103** payloads; stats
  are null and the shotmap is empty in 1,103/1,103.

## Gate arithmetic

The targets do not exist, so no dev n > 0, team trait, rating, or naive
baseline can be computed for any candidate. No season or stage carries a
proxy target.

The 2025/2026 virgin window contains 192 eligible matches, but it was
**NOT READ** for S/C/K/T — deliberately unread, not read-and-failed.
Calibration SEs are therefore undefined and no virgin result is produced.

## Verdict

S-WAL, C-WAL, K-WAL, and T-WAL are **NOT BUILDABLE**. No halves constants
exist for targets that do not exist. Production code is untouched. No push.
No merge.
