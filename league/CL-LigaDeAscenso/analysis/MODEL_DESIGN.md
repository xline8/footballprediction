# Step 6 — Model Design — CL-LigaDeAscenso

Windows (frozen for the one buildable candidate): warm-up/seed
**2021** (finished regular only, n = 178); dev = walk-forward
scored **2022, 2023, 2024** (finished regular, n = 752); virgin =
**2025** (finished regular, n = 240; last complete season, read
ONCE, only for dev-passing arms); confirmatory **2026**
(incomplete, 233/240 regular) never read in this build. Phase
rule: play-off ties excluded everywhere. Population rule:
`finished = 1 AND phase = regular` everywhere. Calibration =
actual − predicted everywhere. Gate rule (program-wide, verbatim
in the prereg): dev gate vs baselines; virgin legs (i) LL,
(ii) calibration |breach| ≤ 1.0pp clean PASS, ≤ 1 SE PROVISIONAL,
else FAIL; (iii) per-season sign check for variant both-pass.

## Feasibility matrix

| candidate | target exists in data? | valid virgin contains target? | scorable dev window contains target? | verdict at design |
|---|---|---|---|---|
| G-CLA goals | yes — scores, all seasons | yes (240) | yes (752) | **BUILD** |
| S-CLA SOT | **no** — stats block is an empty shell in all 1,515 payloads (Periods.All null in all 483 flagged; stats None elsewhere) | no (0 rows) | no (0 rows) | **NOT BUILDABLE** |
| C-CLA corners | **no** — same stats shell | no (0 rows) | no (0 rows) | **NOT BUILDABLE** |
| T-CLA total shots | **no** — same stats shell; shotmap empty everywhere | no (0 rows) | no (0 rows) | **NOT BUILDABLE** |
| K-CLA cards | only 2025–2026 — event feed carries zero plain Yellow events in 2021 (no events at all), 2022, 2023, 2024; no stats yellow source exists in any season | yes (2025) | **no** — dev seasons 2022–2024 contain zero plain-yellow events | **NOT BUILDABLE** |

S/C/T/K get verdict documents recording NOT BUILDABLE with the era
evidence (TH-ThaiLeague2 / ID-SuperLeague precedent); no prereg is
written and nothing is fitted for them. A market whose stats era
leaves no scorable dev window is not forced.

## G-CLA — goals (the only candidate)

| candidate | reference pattern | arms | primary line (dev over-rate) |
|---|---|---|---|
| G-CLA goals | production Dixon-Coles (model_v2 `DC`), goals-only, hl=270 | Gate Zero; SHRINK (sanctioned G-J2 arm); X2 (mover transplant from the parent Primera corpus, DK-1Division definition) | OU 2.5 (0.473) + 1X2 LL/RPS |

Dev scored n = 752 (272 + 240 + 240). Virgin n = 240.
Baselines: climatology — for target season S, pooled outcome rates
+ OU2.5 over-rate of all seasons strictly before S (finished
regular rows only).

Halves: FT + 1H/2H presentation via the frozen goals constant
0.4273 only. No other market ships, so no other halves constant
exists (`halves_share_1h: null` for S/C/K/T in config).

Nothing ships on FAIL; on PASS the winning arm's fitted params +
virgin predictions CSV ship.
