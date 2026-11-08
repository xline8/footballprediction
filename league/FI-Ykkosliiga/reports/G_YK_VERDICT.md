# Verdict — G-YK (FI-Ykkosliiga goals) — **FAIL at the dev gate**

No arm passes the dev gate, so the virgin window (2026) was **NOT read**,
no virgin predictions exist, no virgin fit was made, and **nothing ships**.
This is a complete outcome under the frozen preregistration
(`prereg/PREREG_G_YK.md`, commit e4f14952, before any fitting).
`engine/goals/results_virgin.json` records `{"virgin_read": false}` — the
runner enforced the gate mechanically (per-arm check) and returned without
touching 2026.

Independent verification: the dev walk-forward was replayed by the
coordinator with the repo venv python — all 30 rows of `results_dev.json`
reproduced exactly. The climatology baseline (all three metrics, pooled and
per season) was recomputed from `yk_matches.csv` with a separate
implementation — exact to all printed digits (pooled 1.069923 / 0.230189 /
0.680043). The OU failure is therefore in the DC probabilities, not in the
baseline.

## Dev gate (mechanical, pooled dev seasons 2022–2025, n = 598)

An arm passes iff pooled dev 1X2 LL and RPS beat climatology AND OU2.5 LL
beats the base-rate baseline (the climatology row's OU2.5 LL).

| Arm | 1X2 LL | vs clim 1.069923 | RPS | vs clim 0.230189 | OU2.5 LL | vs base 0.680043 | Dev gate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Gate Zero | 1.069708 | beats by 0.000215 | 0.227815 | beats | 0.704101 | **loses by 0.024058** | **FAIL** |
| SHRINK | 1.069708 | beats by 0.000215 | 0.227815 | beats | 0.704101 | **loses by 0.024058** | **FAIL** |
| X2 | 1.077159 | **loses by 0.007236** | 0.229762 | beats | 0.699736 | **loses by 0.019693** | **FAIL** |

## Dev table (per season)

| Season | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|---:|
| 2022 | climatology | 1.053385 | 0.232552 | 0.681108 |
| 2022 | Gate Zero | 1.044220 | 0.226728 | 0.745516 |
| 2022 | SHRINK | 1.044220 | 0.226728 | 0.745516 |
| 2022 | X2 | 1.044220 | 0.226728 | 0.745516 |
| 2023 | climatology | 1.070193 | 0.225214 | 0.694261 |
| 2023 | Gate Zero | 1.074245 | 0.227561 | 0.713975 |
| 2023 | SHRINK | 1.074245 | 0.227561 | 0.713975 |
| 2023 | X2 | 1.052370 | 0.219459 | 0.704911 |
| 2024 | climatology | 1.082128 | 0.233695 | 0.677424 |
| 2024 | Gate Zero | 1.130224 | 0.243860 | 0.664524 |
| 2024 | SHRINK | 1.130224 | 0.243860 | 0.664524 |
| 2024 | X2 | 1.188062 | 0.261542 | 0.661781 |
| 2025 | climatology | 1.077480 | 0.229856 | 0.664095 |
| 2025 | Gate Zero | 1.034643 | 0.213399 | 0.681374 |
| 2025 | SHRINK | 1.034643 | 0.213399 | 0.681374 |
| 2025 | X2 | 1.036385 | 0.214184 | 0.675789 |

Gate Zero beats climatology on 1X2 LL in only two of four dev seasons
(2022, 2025) and on RPS in three (2022, 2024, 2025); its pooled 1X2 edge
over climatology is 0.000215 — effectively a tie. It beats the OU base rate
in only one season (2024) and loses pooled by 0.024058.

## The variant arms (moot, stated plainly)

- SHRINK is numerically identical to Gate Zero in every season. Under
  season-blocked fitting this is mechanical (the FI precedent): at each
  season's fit every team has either 0 prior in-league matches (entrant;
  its DC ratings are the unseen defaults, and multiplying a rating by n/6
  changes nothing that Gate Zero does not already do) or ≥27 (a full prior
  season). No team ever sits in the 1–5 match band the arm targets.
- X2 (in-corpus entrant offset): inactive in 2022 (fewer than 3 completed
  entrant transitions exist), active from 2023. The pooled offset is
  g = −0.0752, c = +0.2053 for 2023 (entrants score less, concede more) and
  g = −0.0995, c = +0.2027 for 2024. In 2023 it improves 1X2 LL
  (1.052370 vs Gate Zero 1.074245) but still fails the OU leg. In 2024 it
  badly worsens 1X2 LL (1.188062 vs 1.130224): the pooled tilt treats the
  2024 entrants (FC KTP, JIPPO, PK-35) as average entrants, but FC KTP is a
  relegated Veikkausliiga club — stronger than the pooled entrant average —
  so the mixed-origin caveat recorded in MODEL_DESIGN bites in exactly the
  direction warned about. In 2025 the offset is near zero
  (g = +0.0087, c = +0.0440) and X2 ≈ Gate Zero. Pooled, X2 fails all three
  legs except RPS. Gate Zero failed dev, so variants are moot and no rescue
  arm may be invented in this prereg.

## Why the OU leg fails (diagnostic, not a rescue)

The model's mean P(over 2.5) sits in a narrow band while the actual
over-rate swings with the season goal level (dev seasons 2.809–3.281
goals/match; over-2.5 rate 0.525–0.637). The DC lambdas are too tightly
clustered for a league whose season goal level swings this much — the same
failure mode as G-FI and G-EE, and the third consecutive Finnish-tier goals
candidate to fail on exactly this leg. A goals-only DC (no xG exists in this
feed in any season) cannot price the totals line here. Nothing ships.
