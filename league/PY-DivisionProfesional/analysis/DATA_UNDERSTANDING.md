# Step 1 — Data Understanding: PY-DivisionProfesional (Paraguay, FotMob id 199)

Warehouse: `data_enrichment/fotmob_world_index.csv` filter `league_id = 199`
→ **1,480 played matches**, all present as per-match JSONs under
`Paraguay/Division Profesional/<season>/`. Verified 2026-11-09 against the
built CSV (builder asserts n = 1,480, unique match_ids).

## Calendar and format (measured, not assumed)

- **Split tournaments**: each calendar year has an **Apertura** and a
  **Clausura** tournament; the warehouse season label carries the phase
  (`2025 - Apertura`). Each tournament is a free-standing double
  round-robin; there is **no playoff bracket inside these files** (the
  `hasPlayoff` content flag exists but every indexed row is a regular
  tournament match — per-team match counts confirm it, below).
- **2021 anomaly**: both 2021 tournaments had **10 teams → 90 matches**
  (18 rounds). From 2022 on: **12 teams → 132 matches** (22 rounds).
  2021 is also the COVID-era season (played Feb–Dec 2021 with no
  relegation in 2020–21 per the brief; the corpus itself shows only the
  10-team contraction). 2021 is used as training seed only, never as an
  evaluation block for goals, and is outside the stats era entirely.
- 2026 - Clausura is **in progress**: 112 played at pull (2026-07-24 →
  2026-11-08); 20 fixtures remain. It is the count markets' TRANSITIONAL
  virgin and is reserved (unread) for goals.
- Promotion/relegation is annual (aggregate table), so team churn enters
  at Apertura. 20 distinct team_ids appear across 2021–2026.
- **Team-name quirk (real)**: FotMob spells the same team_id differently
  across eras — Guarani/Guaraní (1893), Luqueno/Luqueño (49687),
  Cerro Porteno/Cerro Porteño (6295), Atletico/Atlético Tembetary
  (1299349). Identity is **team_id**; the builder canonicalises the
  display name to the id's most frequent spelling. Any name-keyed join
  across eras silently splits four clubs — engines must key on the
  canonicalised CSV names (safe after canonicalisation) or ids.

## Field coverage by season (share of matches)

| Season | n | stats feed | period splits | referee named | shotmap |
|---|---|---|---|---|---|
| 2021 - Apertura | 90 | 0% | 0% | 0% | 0% |
| 2021 - Clausura | 90 | 0% | 0% | 0% | 0% |
| 2022 - Apertura | 132 | 0% | 0% | 0% | 0% |
| 2022 - Clausura | 132 | 0% | 0% | 0% | 0% |
| 2023 - Apertura | 132 | 0% | 0% | 0% | 0% |
| 2023 - Clausura | 132 | 0% | 0% | 0% | 0% |
| 2024 - Apertura | 132 | 0% | 0% | 0% | 0% |
| 2024 - Clausura | 132 | 0% | 0% | 0% | 0% |
| 2025 - Apertura | 132 | 100% | 100% | 11.4% | 0% |
| 2025 - Clausura | 132 | 100% | 100% | 20.5% | 0% |
| 2026 - Apertura | 132 | 99.2% | 99.2% | 1.5% | 0% |
| 2026 - Clausura | 112 | 100% | 100% | 73.2% | 0% |

- **The stats era starts abruptly at 2025 - Apertura.** Before that the
  payloads carry score + events only. Count markets (SOT/corners/cards/
  total shots) therefore have targets only for 2025 onward: 507 matches.
- **Shotmap is empty in every file (0%) → there is NO xG anywhere in
  this league.** The goals model is Dixon-Coles goals-only (production
  blend's documented goals-only fallback for 100% of observations);
  all xG-derived features (X3/X4/X6 analogues) are dead by construction.
- The single stats-missing match is Olimpia–Cerro Porteño, 2026-04-19
  (the clásico): no stats **and no events** — count targets missing,
  goals target present.
- Events (goals/cards with minute + isHome) exist for 95.1% of all
  matches and ~100% of the stats era, which is what makes the
  event-unified cards target and the goals HT share possible.
- **Referee coverage is unusable in the dev era**: 11.4% / 20.5% / 1.5%
  across the three stats-era dev tournaments, jumping to 73.2% only in
  the virgin tournament (2026 - Clausura). An X8 referee arm cannot be
  fitted or validated on dev — see FEATURES (X8 DROPPED, K-J2 precedent).

## Cards feed check (dev-era evidence only, run BEFORE any fitting)

Stats-feed `yellow_cards` vs event-derived yellows, dev era
(2025-Ap + 2025-Cl + 2026-Ap, n = 396):

| target candidate | mean/match | exact-match vs stats |
|---|---|---|
| stats feed yellows | 4.572 | — |
| events, Yellow only | 4.801 | 80.1% |
| events, Yellow + YellowRed (unified) | 4.922 | 79.8% |

The stats feed **undercounts in every dev season** (mean diff vs the
unified event count: −0.356 / −0.386 / −0.344). This is the AR/BR/NO/KR
artefact in a fifth league. **Decision (frozen in PREPROCESSING): the
cards target is the event-unified count** (`ev_yellow_inc2nd_*`: each
Yellow = 1, each YellowRed = 1 additional yellow). The virgin window
was not touched by this check.
