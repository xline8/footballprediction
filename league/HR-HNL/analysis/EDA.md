# Step 3 — EDA: HR-HNL

Measured by `analysis/eda.py` → `eda_summary.json`; charts in `charts/`
(`make_charts.py`). Complete seasons only for fitting-relevant numbers;
2026/2027 (in progress, 64 matches) is inventoried in Step 1 and excluded
everywhere below.

## F1 — Levels per season (per match)

| Season | Goals | Home G | Away G | SOT | Corners | Shots | Yellows (stats) | Yellows (events) | SOT/Shots |
|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.800 | 1.511 | 1.289 | 8.722 | 9.494 | 25.878 | 2.767 † | 0.128 † | 0.337 |
| 2022/2023 | 2.472 | 1.361 | 1.111 | 8.206 | 8.500 | 23.900 | 2.517 † | 0.128 † | 0.343 |
| 2023/2024 | 2.661 | 1.478 | 1.183 | 8.478 | 9.228 | 25.017 | 4.144 | 4.361 | 0.339 |
| 2024/2025 | 2.356 | 1.394 | 0.961 | 7.478 | 9.017 | 23.372 | 4.250 | 4.528 | 0.320 |
| 2025/2026 (virgin) | 2.661 | 1.461 | 1.200 | 8.156 | 9.367 | 24.528 | 3.961 | 4.094 | 0.333 |

† defective early-era card series — see F6. Home advantage is present in
every season (home goals 1.36–1.51 vs away 0.96–1.29). Goals are low by
programme standards (J1 ≈ 2.6–2.7; the top-5 reference ≈ 2.8–3.0) and
2024/2025 (2.356) is the low outlier dev season; the virgin returns to
2.661. Total shots are stable in definition: the on-target share stays
in 0.320–0.343 across all five seasons — no FI-style break, so T-HR is
buildable. SOT dips with goals in 2024/2025 (7.478).

Dev (2022/2023–2024/2025) over-rates → primary lines: SOT over-7.5
0.552 / over-8.5 0.411 → **primary 7.5**; corners over-8.5 0.509 →
**primary 8.5**; total shots over-23.5 0.524 → **primary 23.5**;
goals OU2.5 over-rate 0.476, home-win rate 0.435. Dev medians:
SOT 8, corners 9, shots 24, yellows 4.

## F2 — Team trait reliability (split-half, career pooled, 13 teams)

| Trait | r (for) | r (against) |
|---|---|---|
| Goals | 0.927 | 0.809 |
| SOT | 0.922 | 0.810 |
| Corners | 0.823 | 0.885 |
| Total shots | 0.897 | 0.807 |
| Yellows (stats) | 0.795 | 0.883 |
| Possession | 0.949 | — |
| Opp-box touches | 0.925 | 0.853 |
| Big chances | 0.818 | 0.769 |
| Fouls | 0.796 | — |

Every target trait is strongly reliable — this is a 10-team league where
the same clubs meet 4× a season, so career samples are deep (≈90 matches
per ever-present team). X5 (trailing target means / ratings inputs) is
adopted for every built candidate.

## F3 — Halves: frozen constants, presentation only

1H shares measured on the dev era (warm-up + dev for events; split
seasons pooled for period splits):

| Market | Source | 1H share | n matches |
|---|---|---|---|
| Goals | event times, 2021/2022–2024/2025 | **0.4320** | 653 (with ≥1 goal) |
| SOT | period splits, dev split matches | **0.4729** | 411 |
| Corners | period splits, dev split matches | **0.4793** | 411 |
| Total shots | period splits, dev split matches | **0.4661** | 411 |
| Yellows | period splits (rich era only) | 0.3272 | 389 — recorded, unused (K-HR not built) |

Goals share variance check: observed per-match share variance 0.11417
vs binomial expectation 0.08652 (excess +0.02765). The decomposition is
crude at these denominators (many 1–2-goal matches), and the programme
rule is unchanged: halves are frozen league constants, presentation
only, never per-team or per-match quantities. Splits consistency:
All = 1H + 2H exact for corners/SOT/shots on all 655 split matches;
yellow_cards mismatches on 24/655 (a minor feed defect, recorded).

## F4 — Entrants (X2 evidence)

One promoted club per season, identified in-corpus by absence from the
previous season: NK Varaždin (2022/2023), Rudeš (2023/2024), Šibenik
(2024/2025), Vukovar 91 (2025/2026, the virgin entrant). Entrant
first-season differentials vs that season's league team mean (n = 4):
GF −0.380/match, GA +0.599/match — the classic promoted-team tilt, same
sign pattern as J1's F4 and FI's entrants. X2 is adopted as a
pre-registered goals arm (offset estimated only from transitions
completed before the predicted season; fires once ≥3 exist, i.e. first
in the virgin season — the FI pattern).

## F5 — Territorial covariates (X7/X9 evidence)

Opp-box touches: for-trait r = 0.925, against r = 0.853 (n = 720
complete-era matches carrying the key); per-match correlation with
total corners 0.376. Possession: trait r = 0.949 but per-match
correlation with corners only 0.058 — possession stands on its
production (X9) evidence, not on this correlation. Big chances:
for-trait r = 0.818. Coverage caveat for X7: touches_opp_box exists in
only 102–144 of 180 matches in the 2022/2023–2023/2024 dev seasons
(180/180 from 2024/2025); the corners engine's min-8-of-last-10 rule
makes the X7 arm inactive where the window cannot be filled — its
active share is reported in the dev results, not hidden.

## F6 — Cards artefact (the decisive check, run before target freeze)

Stats-vs-events unified yellows, by season (stats keys exist in all):

| Season | Exact agree | Mean events | Mean stats | Mean stats − events |
|---|---|---|---|---|
| 2021/2022 | 0.344 | 0.128 | 2.767 | +2.639 |
| 2022/2023 | 0.356 | 0.128 | 2.517 | +2.389 |
| 2023/2024 | 0.833 | 4.361 | 4.144 | −0.217 |
| 2024/2025 | 0.783 | 4.528 | 4.250 | −0.278 |
| 2025/2026 | 0.850 | 4.094 | 3.961 | −0.133 |

Diagnosis: **both** sources change at the 2023/2024 boundary. Before
it, the event feed carries no yellow events at all (its 0.128/match is
reds), and the stats series is itself not credible (37.8% zero-yellow
matches in both early seasons at a stable ~24 fouls/match; 1H share
0.145 in the 2022/2023 split subset). From 2023/2024 both sources are
coherent and agree. This is the TH/ZA-class artefact: the early-era
quantity is a different, broken measurement. No target definition
covers warm-up + ≥3 scored dev seasons + virgin → **K-HR not built**
(PREREG_K_HR records the freeze and the reason).

## F7 — Referee trait (X8 check)

Referees named in 728/900 complete-era matches (30 distinct names).
Split-half strictness (stats yellows per match, referees with ≥5
matches in each half, n = 17 referees): **r = 0.239** — far below J1's
0.65 and below any usable signal bar. X8 is DROPPED on reliability
(and would in any case have no candidate to serve: K-HR is not built).
