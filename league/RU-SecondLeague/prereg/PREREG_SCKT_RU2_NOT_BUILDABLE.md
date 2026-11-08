# Pre-registration — S/C/K/T-RU2: NOT BUILDABLE

Frozen: 2026-11-10, before any fitting. Branch `build/ru-second-league`.
Design authority: `league/RU-SecondLeague/analysis/MODEL_DESIGN.md`
(§1 feasibility matrix); features per `analysis/FEATURES.md` (§4).
This prereg records the NOT BUILDABLE verdicts with payload-level
evidence, so that no fitting, no virgin read, and no post-hoc arm can
follow from it for any of these four candidates.

**Committed before any fitting. No fitting is done under this prereg.**

## Evidence (payload-verified 2026-11-10, all 6,558 payloads read)

- **S-RU2 (shots on target):** `ShotsOnTarget` exists in **0/6,558**
  payloads. `content.stats` is empty in 6,558/6,558; `content.shotmap`
  is empty in 6,558/6,558. No SOT target exists in any season, so no
  dev window and no virgin window exist.
- **C-RU2 (corners):** `corners` exists in **0/6,558** payloads
  (same empty stats feed). No corners target exists in any season.
- **K-RU2 (cards):** no yellow-card target exists anywhere.
  `yellow_cards` stats exist in 0/6,558 payloads. Card events exist
  only in the events era (2021/2022–2024) and number 959 in total —
  **all of them dismissals** (YellowRed 624, Red 335; **0 plain
  Yellow events**). Events-era matches with ≥1 card event: 835/3,773;
  mean 0.254 cards/match; 77.9% of events-era matches show zero
  cards. Events are absent entirely from all 2,402 rows from
  2024/2025 onward, so no card target exists in any virgin window.
  The referee field is empty in 6,558/6,558 payloads, so referee
  strictness (X8) is unmeasurable as well. Dismissals are not
  yellows and are not modelled as a substitute target.
- **T-RU2 (total shots):** `total_shots` / shot counts exist in
  **0/6,558** payloads (same empty stats feed and shotmap). No total-
  shots target exists in any season.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: the targets do not exist, so no
  team trait, no rating and no naive baseline can be computed for any
  candidate in any season. There is no dev n > 0.
- Virgin = labels 2026 + 2026/2027 (888 finished non-awarded
  matches): the targets do not exist there either (stats/shotmap
  empty in all 888; events absent in all 888). Calibration SEs are
  undefined — there is nothing to calibrate.
- No pooled or proxy rescue: no season, no track and no stage carries
  the targets, so no subset of the warehouse rescues any candidate.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026 + 2026/2027): **NOT READ** for S/C/K/T —
  deliberately unread, not read-and-failed.
- Halves constants: **none** for SOT/corners/cards/total shots
  (no splits exist for targets that do not exist).

## Verdict

S-RU2, C-RU2, K-RU2, T-RU2 are **NOT BUILDABLE**. Report:
`league/RU-SecondLeague/reports/S_C_K_T_RU2_NOT_BUILDABLE.md`.
Production code untouched. No push. No merge.
