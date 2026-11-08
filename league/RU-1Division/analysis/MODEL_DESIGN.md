# Phase 4 — Candidate model design: RU-1Division

This is a design-only document. No model is fitted and no preregistration file
is created in Phase A. Calibration is actual minus predicted.

## Validation frame

The dev period uses seed 2021/2022 and scores 2022/2023–2024/2025, with
1,235 stats observations for SOT, corners, and total shots and 1,298
observations for goals and event yellows. The virgin primary window is
2025/2026 with 305 matches, read once and only for dev-passers. The
2026/2027 window has 153 matches and is confirmatory only; it is never read
for design or gate decisions in this build.

The production analogue is Gate Zero for every candidate. The frozen format is
20 teams in 2021/2022, 18 teams from 2022/2023, one regular phase, double
round-robin, and `phase=regular` on every row. The 2025/2026 missing fixture
is recorded in the inventory JSON and does not change the format definition.

## Candidates

| candidate | target | Gate Zero | allowed arms | primary line |
|---|---|---|---|---|
| G-RU1 | home/away goals, DC | production goals/DC pattern, goals-only | SHRINK for thin histories and mover evidence | OU 2.5, over 0.414 |
| S-RU1 | stats SOT total | production SOT pattern | RS arm, as in RU-Premier | 7.5, over 0.466 |
| C-RU1 | stats corners total | production corners pattern with possession-only covariate | possession covariate only; no unsupported big-chance arm | 8.5, over 0.530 |
| K-RU1 | event-unified yellows | production cards pattern on event target | none; Gate Zero only | 4.5, over 0.461 |
| T-RU1 | stats total shots total | production total-shots pattern | arms A/B/C as in RU-Premier | 15.5, over 0.512 |

### Goals

The goals candidate is a goals-only Dixon-Coles analogue because X1 is
dropped. The SHRINK arm is eligible because the entrant evidence is thin and
relegated movers (n=9) show prior RU-Premier GF/GA of 0.941/1.707 with
first-season RU-1Division gaps of +0.233/-0.126. Promoted/other movers (n=11)
show -0.136/+0.059 and returning movers (n=3) show -0.139/+0.087. No common
offset is hard-coded.

### SOT and total shots

SOT keeps the RU-Premier production analogue and tests the harder-shrinkage RS
arm. Total shots keeps the three reference arms A/B/C. Both use the stats
feed target and only pre-match trailing observations.

### Corners and cards

Corners carries possession-only as the adopted X9 covariate. Big chance is
absent, so the RU-Premier pair cannot be reproduced. Cards has no variant:
stats `yellow_cards` is absent, and event-unified yellows are the target by
construction. Referee features are forbidden.

## Halves

Goals use the frozen event-derived first-half constant 0.4599. The observed
share variance is 0.12752 versus binomial noise 0.12939, ratio 0.986, across
1,415 positive-goal matches. SOT, corners, cards, and total shots remain FT
presentation only because the payload has no period splits.
