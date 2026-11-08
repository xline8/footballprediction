# Phase A — EDA: BE-FirstDivisionB

All values below are emitted by eda_compute.py from the built CSV and raw event payloads. No model is fit.

## Goal levels

| Season | n | Goals | Home | Away | Home advantage |
|---|---:|---:|---:|---:|---:|
| 2021/2022 | 112 | 2.8571 | 1.4911 | 1.3661 | 0.1250 |
| 2022/2023 | 192 | 3.0000 | 1.6198 | 1.3802 | 0.2396 |
| 2023/2024 | 246 | 2.8293 | 1.4146 | 1.4146 | 0.0000 |
| 2024/2025 | 216 | 2.8380 | 1.4907 | 1.3472 | 0.1435 |
| 2025/2026 | 278 | 2.8381 | 1.4640 | 1.3741 | 0.0899 |
| 2026/2027 | 70 | 3.0857 | 1.7857 | 1.3000 | 0.4857 |

Virgin/confirmatory rows are levels only.

## Reliability and halves

Dev odd/even season correlation by team ID is goals-for r=0.5020 (17 teams) and goals-against r=0.7148 (17 teams). The dev event population is 726 matches in eda_compute.py's payload pass; the built CSV's ht_source=events covers 734 matches and yields the identical constant (957 HT goals / 2,205 FT goals = 0.434014, coordinator-verified from the CSV), which is the canonical figure. The frozen goals 1H share is 0.434014. Per-match observed variance 0.102295 is below the binomial noise floor 0.109344; estimated true variance is -0.007049, so a constant is retained.

## Movers

Strict ID rule finds Beerschot (2022/2023), Zulte Waregem, RFC Seraing and Oostende (2023/2024), and Eupen and RWD Molenbeek (2024/2025). Pooled first-season BE-B gaps versus that season’s league mean are GF -0.0982 and GA -0.1106. Their prior BE-A gaps are GF -0.4385 and GA +0.6394. RWD Molenbeek is the surprise relative to the brief’s expected list; it satisfies the stated previous-season BE-A/absent-from-B rule. New entrants and reserves are listed in the JSON; they are not movers.

## Cards feed forensics

On 277 2025/2026 matches with both sources (recomputed by the
coordinator from the built CSV's own columns): stats-feed yellows vs
plain Yellow events agree exactly in 72.20% (200/277); the stats feed
is LOWER in 27.80% (77/277) and HIGHER in 0.00%; mean difference
(stats - events) = -0.3466 yellows per match. The artefact is present
and one-directional: **the stats feed undercounts yellows**.

Mechanism, verified by the coordinator on this league's own payloads:
match 4862622 (Seraing-Beerschot) - a player dismissed via a second
yellow (Yellow at 43', YellowRed at 58') contributes ZERO yellows to
the stats feed (stats home = 2 = only the two other plain yellows),
while the event feed carries both cautions. Match 4862626 (Patro
Eisden-Lokeren, no YellowRed at all) still shows stats one yellow
short per side (6/3 vs 7/4 event yellows), so isolated misses in
multi-card minutes occur as well.

Frozen conclusion for any future cards preregistration: the
presumptive target is EVENT-UNIFIED (plain Yellow events, YellowRed
kept as its own category per the program convention), because in the
only era where both sources exist the event feed is the complete one
and the stats feed's shortfall is systematic. (This corrects Phase
A's initial stats-feed recommendation, which rested on the
structured-source argument alone and did not survive the payload
spot-check.) The freeze is moot for this build: the dev era's event
feed carries Card events in only 32-60 matches per season and the
stats feed does not exist there, so cards has no dev window under
EITHER source - K-BEB is NOT BUILDABLE regardless (see
MODEL_DESIGN.md).

## Count-stat levels

Single-season, no dev window exists: in 2025/2026 SOT=8.9711, corners=9.6029, cards=4.0000 and total shots=26.2708 per match. These descriptive values do not authorize fitting.

