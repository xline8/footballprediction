# Phase 3.5 — Feature Engineering: PL-Ekstraklasa X1–X9

The global causality contract is unchanged: a target match may use only strictly earlier matches; windows are trailing; ratios are ratios of sums; missing windows make an arm inactive. Ratings, home advantage, Dixon–Coles parameters, count distributions, and halves constants are architecture or presentation components, not covariates.

| ID | Feature | PL verdict | Evidence and use |
|---|---|---|---|
| X1 | Goals plus stats-feed xG blend | ADOPTED with era guard | Goals exist for all 1,654 rows. Stats xG exists sparsely in 2023/2024–2024/2025 and fully in 2025/2026–2026/2027; xG reliability is 0.610 on that era. Earlier observations fall back to goals-only. |
| X2 | Mover tier offset | MEASURED, NOT CONSUMED | 15 newcomers, 3 per transition: GF gap −0.142 (weak) and GA gap +0.288 versus the pooled league team mean. No I Liga corpus is built in this build, so no true tier offset is estimated; the goals candidate's pre-registered thin-data mechanism is SHRINK instead (BE precedent). The magnitudes stay recorded here if a future build estimates the offset properly. |
| X3 | Set-play xG share/rate | DROPPED for this stage | Set-play-share reliability is 0.482, but coverage is only 1.3%, 2.0%, 100.0%, 100.0% across the stats-xG era. The broad pre-virgin history is too sparse to support a stable trailing arm. Re-open only with a usable xG era. |
| X4 | Shotmap xG per shot | DROPPED | Usable shotmap-xG era is 2025/2026–2026/2027; reliability is 0.102, below the ~0.35 design threshold. |
| X5 | Trailing target means | ADOPTED | SOT, corners, and unified yellows are available as target histories. Reliability is SOT 0.779/0.729, corners 0.646/0.625, yellows 0.370/0.227 for/against. |
| X6 | Attacking xGOT per shot | DROPPED | Era-guarded reliability is −0.016 on 2025/2026–2026/2027. The era does not start inside the virgin, but it still fails the reliability gate. |
| X7 | Opp-box touches | ADOPTED conditionally | For/against reliability is 0.808/0.764. Coverage is 0.0%, 61.1%, 76.8%, then 100.0%, 100.0%, 100.0%; the min-8 trailing-window rule controls availability. |
| X8 | Referee yellow rate | ADOPTED conditionally | Referee reliability is 0.501 across the 20 referees meeting the split-half sample threshold (42 distinct referees named in total); coverage is 72.9%, 100.0%, 100.0%, 100.0%, 86.6%, 100.0% by season. Use only pre-match referee identities and a league-mean fallback for thin referee histories. |
| X9 | Possession and big chances for corners | ADOPTED as Gate Zero reference | Possession reliability is 0.894 and big-chance reliability is 0.705. They remain the reference territorial covariates; X7 is tested as the additional arm. |

Rejected inherited items remain rejected: team half shares are presentation constants (goals/SOT/corners/shots true variance approximately zero); finishing and standalone conversion are outcome-contaminated; on-target rate reliability is 0.246; defensive xGOT is not eligible; lineup, formation, coach, standings, h2h, attendance, game-state, momentum, and red-card features have no admissible pre-match evidence here.

## Consumption map

- G-PL: X1 (blend with goals-only fallback); SHRINK is the thin-data arm; X2 measured but not consumed; X3 is not active at this stage.
- S-PL: X5; X4 and X6 are rejected.
- C-PL: X5 and X9 Gate Zero; X7 conditional arm.
- K-PL: X5; X8 conditional arm.
- T-PL: no new feature arm is adopted at Stage 1.
