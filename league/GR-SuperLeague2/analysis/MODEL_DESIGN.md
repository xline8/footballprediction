# Phase 4 — Model Design: GR-SuperLeague2 Candidates

This is a candidate design only. No fitting or dev/virgin evaluation
has been performed. The dev window is a season-blocked walk-forward
over the dev period 2021/2022–2024/2025 (1,591 matches including the
2021/2022 training seed; scored seasons 2022/2023–2024/2025, 1,045
matches). The primary virgin is 2025/2026 (265 matches, last complete
season), read once only after dev gates. 2026/2027 (79 matches, single
16-team group, in progress) is confirmatory and must not be read in
this build; it is also a different competition shape from the
dev/virgin seasons.

**Phase rule (frozen):** phase is flagged from `general.leagueName`
(`regular`, `playoff_promotion`, `playoff_relegation`, `playoff`,
`supercup`); all phases are ordinary rows in every fit and every
window; B teams are ordinary rows; no phase feature and no B-team
feature anywhere. Calibration is defined as **actual minus
predicted** everywhere.

| Candidate | Reference / Gate Zero | Primary .5 line (dev over-rate) | Candidate arms |
|---|---|---|---|
| G-GR2 goals | Dixon–Coles goals pattern with the X1 blend (goals-only throughout: xG exists in zero payloads) | OU 2.5 (0.422 full-dev; 0.427 scored-dev) | Gate Zero; SHRINK for thin-data team priors. X2 NOT run: measured (+0.314/−0.288 for SL1-relegated, −0.198/+0.108 for Gamma/other) but not consumed — 5 dev movers cannot carry an offset, and one pooled offset would be wrong-signed for both origin groups |
| S-GR2 SOT | — | — | NOT A CANDIDATE: zero stats rows in 1,935 payloads |
| C-GR2 corners | — | — | NOT A CANDIDATE: zero stats rows in 1,935 payloads |
| K-GR2 cards | — | — | NOT A CANDIDATE: zero stats rows; event cards too sparse (337 in 1,935) and un-unifiable |
| T-GR2 total shots | — | — | NOT A CANDIDATE: zero shotmap rows in 1,935 payloads |

X1 honesty note: stats-feed xG exists in zero payloads in this
league. Gate Zero's blend therefore runs goals-only through dev and
through the virgin fit; the blend weight is the production pattern
with its documented goals-only fallback, not a fitted xG effect.
There is no xG era anywhere in this corpus (unlike GR, where the xG
era starts inside the virgin).

Frozen halves constant (validated event subset, complete seasons
2021/2022–2025/2026, n=1,617, presentation only): goals 0.4596.
No other market has a halves constant.

Gates (frozen programme standard, repeated verbatim in the prereg):
dev — goals beats climatology on 1X2 LL AND RPS AND base rate on
OU2.5 LL, else FAIL and variants are moot; virgin, read ONCE and
only for dev-passers: PASS if LL ≤ best baseline AND
|calibration| ≤ 1pp; PROVISIONAL if a calibration breach is within
1 SE of the boundary; else FAIL. No dev pass ⇒ virgin NOT read.
Gates never move.
