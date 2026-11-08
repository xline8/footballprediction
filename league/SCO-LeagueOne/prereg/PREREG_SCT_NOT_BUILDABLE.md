# Pre-registration — NOT BUILDABLE: S-SCO-L1 / C-SCO-L1 / T-SCO-L1

Frozen: 2026-11-10, in Phase A, **before any fitting**. Branch
`build/sco-league-one`. This record exists so that three candidate
markets are closed by measurement, not by omission — no engine is
built for any of them, no dev run is attempted, and no virgin read
is ever made for them. (K-SCO-L1 is NOT in this file: its target
exists in the event feed and it has its own prereg.)

Design authority: `league/SCO-LeagueOne/analysis/MODEL_DESIGN.md`;
evidence per `league/SCO-LeagueOne/analysis/DATA_UNDERSTANDING.md`,
`EDA.md`, `FEATURES.md` (X4/X6/X7/X9 DROPPED) and
`inventory_summary.json`.

## The measurement (content, not index flags)

All 969 payloads (seasons 2021/2022–2026/2027, FotMob league 124)
were read:

| Target | Source checked | Result |
|---|---|---|
| Shots on target (S-SCO-L1) | `content.stats.Periods` + `content.shotmap.shots` | Stats `Periods` is empty in 969/969 matches; shot list is empty in 969/969. **No SOT target exists in any season.** |
| Corners (C-SCO-L1) | `content.stats.Periods` | Same: empty in 969/969. **No corners target exists in any season.** |
| Total shots (T-SCO-L1) | `content.stats.Periods` + `content.shotmap.shots` | Same: no stats, empty shot list. **No total-shots target exists in any season.** |

## Why "not buildable" rather than "failed"

- The virgin window (2025/2026) contains **no target for any of
  these three markets** — SOT 0/180, corners 0/180, total shots
  0/180 — so no virgin read could ever validate a model, and no
  dev window contains a target either (0/540 on dev seasons).
- The index flags (`has_stats: False`, `has_shotmap: False` on all
  969 rows) happen to agree with the payloads here, but the
  verdict rests on the payload content check above, not the flags.
- No fallback source exists in-system for these targets in this
  league (no stats feed, no shotmap, no xG).

## Consequence

S-SCO-L1, C-SCO-L1 and T-SCO-L1 are closed as NOT BUILDABLE. No
engine directory, no results files, no predictions, and no verdict
beyond this record and the MODEL_DESIGN table. If FotMob ever
populates stats for this league, the candidates reopen only under
a new preregistration.
