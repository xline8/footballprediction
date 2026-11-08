# Step 3 — EDA: CO-PrimeraA

All numbers from `co_primeraa_matches.csv` (2,582 matches) via
`analysis/eda.py` (+ a frozen supplementary pass for era-restricted
cards/referee traits and clean-era halves constants). 2026 -
Clausura is in progress and excluded from every fit-era number;
where it appears below it is marked and contextual only.

## F1 — Levels by tournament

| tournament | n | goals | home | away | HW | draw | OU2.5 | SOT | corners | shots | cards (ev, era) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 - Apertura | 185 | 2.205 | 1.276 | 0.930 | .422 | .341 | .373 | 7.59 | 8.79 | 23.38 | — (no events) |
| 2021 - Clausura | 226 | 2.305 | 1.252 | 1.053 | .407 | .310 | .394 | 8.13 | 9.23 | 25.30 | — |
| 2022 - Apertura | 226 | 2.173 | 1.288 | 0.885 | .509 | .265 | .381 | 7.74 | 8.89 | 24.39 | — |
| 2022 - Clausura | 226 | 2.341 | 1.341 | 1.000 | .438 | .319 | .394 | 8.18 | 8.80 | 25.59 | — |
| 2023 - Apertura | 226 | 2.239 | 1.394 | 0.845 | .478 | .358 | .389 | 8.60 | 9.74 | 26.39 | 5.66 |
| 2023 - Clausura | 226 | 2.292 | 1.376 | 0.916 | .487 | .296 | .385 | 8.37 | 9.78 | 25.61 | 5.28 |
| 2024 - Apertura | 216 | 2.162 | 1.264 | 0.898 | .449 | .259 | .380 | 7.97 | 9.03 | 24.56 | 5.16 |
| 2024 - Clausura | 216 | 2.185 | 1.292 | 0.894 | .477 | .273 | .384 | 7.82 | 8.82 | 24.14 | 5.75 |
| 2025 - Apertura | 226 | 2.155 | 1.257 | 0.898 | .447 | .296 | .381 | 7.90 | 9.34 | 24.76 | 5.66 |
| 2025 - Clausura | 226 | 2.420 | 1.394 | 1.027 | .469 | .274 | .469 | 8.19 | 8.85 | 25.00 | 5.81 |
| 2026 - Apertura† | 204 | 2.529 | 1.569 | 0.961 | .485 | .299 | .475 | 8.49 | 9.04 | 25.25 | 5.75 |
| 2026 - Clausura‡ | 179 | 2.531 | 1.425 | 1.106 | .447 | .302 | .480 | 9.04 | 9.18 | 25.86 | 5.68 |

† virgin. ‡ in progress, excluded.

- A LOW-scoring league: dev-era (2022-Ap…2025-Cl) goals **2.247/match**,
  OU2.5 rate **0.395** — close to CO-PrimeraB (2.20–2.37) and well
  below J1 (≈2.66) and PY (2.45). Home advantage is solid:
  home/away goal ratio ≈ 1.42 pooled (home 1.32 vs away 0.93 per
  match in dev).
- **The level is rising at the end of the window**: 2025-Cl (2.420,
  OU .469) and the virgin 2026-Ap (2.529, OU .475) run well above the
  2022–2025-Ap band (2.16–2.34). Calibration legs will feel this;
  the gates are not moved for it.
- Count levels (dev pooled): SOT **8.10**, corners **9.16**, total
  shots **25.06** — SOT below J1 (≈9), corners above PY (8.88) and
  below J1 (9.47). Cards (event era, 2024–2025 dev blocks): **5.60**
  unified yellows/match — a high-card league (PY dev 4.89, J1 ≈ 3–4).

## F2 — Team trait reliability (split-half, career through 2025-Cl, ≥20 matches, 25 teams)

| trait | for r | against r |
|---|---|---|
| goals | **0.793** | 0.506 |
| SOT | **0.828** | **0.228** |
| corners | 0.452 | 0.565 |
| total shots | 0.684 | 0.598 |
| yellows (stats feed) | 0.547 | 0.507 |
| yellows (event-unified, 2023+ era only, 23 teams) | 0.585 | 0.289 |
| opp-box touches | 0.451 | 0.640 |
| big chances | 0.744 | — |
| possession | 0.837 | — |
| on-target rate (SOT/shots) | **0.774** | — |

Attacking traits are real for every market. Two honest weaknesses:
**SOT-against (0.228) and event-yellows-against (0.289) sit in the
noise-adjacent zone** — the defensive side of the SOT and cards
models has little trait to find, and their gates may fail for it.
Corners traits (0.45/0.57) are weaker than J1's (0.65/0.64) but the
territorial covariates are strong: per-match corr(touches-for,
corners-for) = **0.503** (J1: 0.471), corr(possession, corners) =
0.406, big-chances trait 0.744.

## F3 — Halves: frozen constants, presentation only

| market | 1H share | obs var | noise var | true var |
|---|---|---|---|---|
| goals (events, fit era) | **0.4706** | 0.131 | 0.133 | ≈ 0 (−0.002) |
| SOT (splits, 2023-Cl…2025-Cl) | **0.4862** | 0.037 | 0.036 | ≈ 0 |
| corners (splits, same window) | **0.4956** | 0.035 | 0.032 | 0.003 |
| total shots (splits, same window) | **0.4850** | 0.011 | 0.011 | ≈ 0 |
| cards (events unified, fit era*) | **0.3543** | 0.066 | 0.064 | 0.002 |

\* dominated by the 2023+ event era (2021–22 contribute ≈0 events).

Per-match 1H-share variance is ≈ noise everywhere — the programme's
standing result. Halves are NEVER fitted: FT lambdas are split by
these frozen constants for presentation only. The goals share
(0.4706) and corners share (0.4956 — nearly half of all corners arrive
before half-time) are both high vs J1 (0.412 / 0.447).

## F4 — Movers from Primera B (the X2 question, reverse of CO-B)

Promoted clubs, first season in A, per-match goals for/against vs
that season's league mean per team (base ≈ 1.12):

| arrival | club | ΔGF/m | ΔGA/m |
|---|---|---|---|
| 2022 | Internacional de Palmira | −0.303 | +0.247 |
| 2022 | Union Magdalena | −0.353 | +0.272 |
| 2023 | Atletico Huila | −0.183 | +0.292 |
| 2023 | Chico FC | −0.154 | −0.046 |
| 2024 | Patriotas | −0.271 | +0.334 |
| 2024 | Fortaleza FC | −0.008 | −0.034 |
| 2025 | Llaneros FC | −0.219 | +0.181 |
| 2025 | Union Magdalena | −0.244 | +0.356 |

Dev-era mean (2022–2025, 8 club-years): **ΔGF −0.217/m (8/8
negative), ΔGA +0.200/m (6/8 positive)**. Promoted clubs attack far
below the A mean and concede above it — a consistent, one-directional
tier gap, the mirror image of CO-PrimeraB's relegated arrivals
(ΔGF +0.11, ΔGA −0.30 there). This justifies ONE pre-registered X2
arm with offsets frozen from these dev-era numbers only (FEATURES):
attack ×0.81, concession ×1.18 (multipliers vs the per-team base
1.1235). The 2026 arrivals (CD Jaguares, Cúcuta — the virgin's
movers, already running ΔGF −0.16 / ΔGA +0.52 pooled in the part of
2026 visible outside the virgin) were NOT used to set the offset.

SHRINK context: at every dev tournament start, the only clubs with
<6 prior in-league matches are the two promoted clubs at exactly 0
priors (incumbents all carry ≥38). A 1–5-prior shrinkage arm would be
identical to Gate Zero on every dev and virgin prediction —
**degenerate by construction (the GE/BG2 situation), so no SHRINK
arm is registered**; the promoted-club failure mode is addressed by
X2 instead, which is the arm with actual evidence here.

## F5 — Referee (cards era)

Referee names: 0% in 2021, ~0.94–1.00 from 2022 - Apertura (0.94 in
the cards dev era 2023-Cl…2025-Cl; 0.843 in the virgin). On the
cards era only (2023-Ap…2025-Cl + virgin excluded from trait fitting;
36 referees with ≥8 matches): split-half strictness **r = 0.487** —
a real but moderate trait (J1: 0.65). Coverage is high enough that an
X8 arm would be active for ~94% of dev rows — unlike PY (11.1%
coverage → dropped). **X8 is adoptable as the cards variant arm**;
the gate decides whether the moderate trait pays.

## F6 — xG era (descriptive, no arm)

Stats-feed xG and shotmap exist only from 2025 - Clausura. In-era
(452 matches): mean xG 2.108 vs mean goals 2.471 (goals/xG 1.172).
No reliability or arm can be built on an era that starts at the
virgin boundary; X1 stays goals-only and X3/X4/X6 are dropped in
FEATURES with this as the stated reason.
