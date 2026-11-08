# Verdict — S/C/K/T-SV: NOT BUILDABLE

**No fitting was done, and no virgin read follows, for any of these
four candidates. The verdicts are payload-level facts.**

Prereg `league/SV-PrimeraDivision/prereg/PREREG_SCKT_SV_NOT_BUILDABLE.md`
(frozen 2026-11-10, before any fitting). Branch
`build/sv-primera-division`.

## Evidence (payload-verified 2026-11-10, all 1,448 payloads read by content)

| candidate | evidence |
|---|---|
| S-SV (shots on target) | `ShotsOnTarget` in **0/1,448** payloads. `content.stats` empty in 1,448/1,448; `content.shotmap` empty in 1,448/1,448. No SOT target exists in any tournament. |
| C-SV (corners) | `corners` in **0/1,448** payloads (same empty stats feed). No corners target exists in any tournament. |
| K-SV (cards) | No yellow-card target exists anywhere. `yellow_cards` stats in 0/1,448 payloads. Card events number 593 across 1,334 event-bearing matches — **all dismissals** (Red 449, YellowRed 144; **0 plain Yellow events**). Referee text is empty in 1,448/1,448 payloads, so X8 is unmeasurable as well. Dismissals are not yellows and are not modelled as a substitute target. |
| T-SV (total shots) | `total_shots` / shot counts in **0/1,448** payloads (same empty stats feed and shotmap). No total-shots target exists in any tournament. |

The index `has_stats` / `has_shotmap` flags are `False` for all 1,448
rows and the payloads confirm that by content. No proxy is
constructed for any target.

## Consequence

- No dev window exists for S/C/K/T (no dev n > 0); no virgin window
  exists (the targets are absent from the 2025/2026 tournaments
  too). The virgin window is **deliberately unread** for S/C/K/T —
  not read-and-failed.
- No arms, no primary lines, no halves constants for SOT/corners/
  cards/total shots.
- The league's only buildable candidate is G-SV (goals) — see
  `G_SV_VERDICT.md` (FAIL at the dev gate, OU2.5 leg; virgin not
  read). League completion state: **complete**.
