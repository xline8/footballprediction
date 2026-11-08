# EDA — IS-2Deild

All findings use the generated CSVs and payload-derived mover JSON; no model was fitted.

## F1 — Levels, home advantage, OU2.5 and BTTS

| season | n | goals/match | HW | D | AW | OU2.5 | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 116 | 3.698 | .466 | .250 | .284 | .681 | .672 |
| 2022 | 132 | 3.492 | .477 | .235 | .288 | .705 | .636 |
| 2023 | 132 | 3.424 | .515 | .174 | .311 | .682 | .659 |
| 2024 | 132 | 3.652 | .455 | .174 | .371 | .712 | .614 |
| 2025 | 132 | 3.583 | .470 | .167 | .364 | .682 | .674 |
| 2026 | 132 | 3.894 | .538 | .197 | .265 | .735 | .705 |

## F2 — Trait reliability

Seed 7, random split within each team-season with at least 10 matches, n=72 team-seasons. Correlation of half-sample per-match means is `r=0.402` for goals-for and `r=0.370` for goals-against: usable but modest reliability for this small league.

## F3 — Halves

First-half event goals are 181/429, 215/461, 204/452, 207/482, 211/473 and 224/514. Pooled 1H share is 1,242/2,811 = **0.4418**. Observed per-match share variance is 0.08698 versus a binomial noise floor of 0.08803, for true variance **−0.00106**. Halves are frozen to the presentation constant.

## F4 — Movers

The complete per-club arrival table is below and is also machine-readable in `data/mover_teams.json`.

| season | club | source | arrival GF | arrival GA | previous 1D GF | previous 1D GA |
|---|---|---|---:|---:|---:|---:|
| 2022 | Vikingur Olafsvik | relegated | 1.955 | 1.864 | 1.273 | 3.545 |
| 2022 | Throttur Reykjavik | relegated | 2.227 | 1.227 | 1.773 | 2.409 |
| 2022 | Ægir | from below | 1.682 | 1.591 | — | — |
| 2022 | Hottur/Huginn | from below | 1.636 | 1.455 | — | — |
| 2022 | KFA | from below | 1.455 | 2.455 | — | — |
| 2023 | KV Reykjavik | relegated | .818 | 2.682 | 1.227 | 2.364 |
| 2023 | Sindri | from below | 1.136 | 2.409 | — | — |
| 2023 | Dalvik/Reynir | from below | 2.045 | 1.045 | — | — |
| 2023 | Throttur Vogar | relegated | 1.909 | 1.364 | .364 | 2.545 |
| 2023 | KFG | from below | 1.864 | 1.818 | — | — |
| 2024 | Reynir Sandgerdi | from below | 1.273 | 2.500 | — | — |
| 2024 | Selfoss | relegated | 2.318 | 1.227 | 1.682 | 2.227 |
| 2024 | Ægir | relegated | 1.318 | 1.591 | 1.045 | 3.045 |
| 2024 | Kormákur/Hvöt | from below | .864 | 1.909 | — | — |
| 2025 | Vidir | from below | 1.500 | 1.864 | — | — |
| 2025 | Grotta | relegated | 2.136 | 1.136 | 1.409 | 2.273 |
| 2025 | Dalvik/Reynir | relegated | 1.727 | 1.182 | 1.045 | 2.227 |
| 2025 | Kari | from below | 1.455 | 2.500 | — | — |
| 2026 | Fjölnir | relegated | 2.227 | 2.091 | 1.455 | 2.409 |
| 2026 | Selfoss | relegated | 2.500 | 1.636 | 1.136 | 2.000 |
| 2026 | Magni | from below | 1.591 | 2.455 | — | — |
| 2026 | Hviti Riddarinn | from below | 1.273 | 2.455 | — | — |

Against the arrival-season team-match league mean, pooled deltas are: relegated n=10, dGF **+0.109**, dGA **−0.205**; from-below n=12, dGF **−0.311**, dGA **+0.246**. These are small priors and must be estimated causally and gated in Phase B.

## F5 — Cards artefact

There are 145 Card events in 776 matches, 0.187 per match, with seasonal counts 26/23/35/19/17/25. Coverage is sporadic and there is no stats feed; cards are not a target.

## F6 — Coverage boundary

Stats are absent in 776/776, shotmap shots are empty in 776/776, and referee text is empty in 776/776. Therefore S/C/K/T cannot be built. Only goals and event-derived first-half presentation are supported.

## F7 — Virgin window

2026 is complete (132 matches, rounds 1–22). It is observed-hot at 3.894 goals/match, OU2.5 over .735 and BTTS .705. These are descriptive virgin facts only; no tuning or fitting uses them in Phase A.
