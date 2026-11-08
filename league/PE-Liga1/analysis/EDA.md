# Step 3 — EDA: PE-Liga1

Computed by `analysis/eda.py` from the built CSV (modelling corpus:
regular phase, non-awarded, n = 1,836 unless stated). Charts:
`analysis/charts/` (step 4). Raw numbers: `analysis/eda_summary.json`.

## F1 — Levels by block (regular, non-awarded)

| Block | n | goals | home gls | away gls | home win% | SOT | corners | raw shots | ev. yellows |
|---|---|---|---|---|---|---|---|---|---|
| 2021 - Fase 1 | 81 | 2.52 | 1.36 | 1.16 | 43.2% | 8.38 | 10.11 | 21.71 | — (feed broken) |
| 2021 - Fase 2 | 153 | 2.79 | 1.35 | 1.44 | 32.7% | 8.29 | 9.66 | 18.35 | — |
| 2022 - Apertura | 171 | 2.74 | 1.63 | 1.11 | 50.9% | 9.11 | 10.68 | 26.76 | — |
| 2022 - Clausura | 171 | 2.70 | 1.69 | 1.01 | 53.8% | 9.17 | 10.25 | 20.34 | — |
| 2023 - Apertura | 165 | 2.73 | 1.73 | 1.01 | 55.8% | 9.17 | 10.35 | 26.30 | 6.07 |
| 2023 - Clausura | 169 | 2.33 | 1.43 | 0.91 | 47.3% | 7.81 | 9.26 | 19.16 | 4.84 |
| 2024 - Apertura | 153 | 2.72 | 1.71 | 1.01 | 53.6% | 8.38 | 9.43 | 25.31 | 4.71 |
| 2024 - Clausura | 153 | 2.60 | 1.57 | 1.03 | 51.6% | 8.00 | 8.50 | 19.11 | 3.94 |
| **2025 - Apertura (virgin)** | 171 | 2.71 | 1.65 | 1.06 | 48.5% | 8.26 | 8.51 | 21.46 | 4.70 |
| **2025 - Clausura (virgin)** | 152 | 2.55 | 1.52 | 1.03 | 48.7% | 8.53 | 9.05 | 25.72 | 4.68 |
| 2026 - Apertura (reserved) | 153 | 2.63 | 1.65 | 0.98 | 53.6% | 8.83 | 8.41 | 25.75 | 4.52 |
| 2026 - Clausura (reserved) | 144 | 2.94 | 1.75 | 1.19 | 49.3% | 9.49 | 9.54 | 29.53 | 4.64 |

(SOT/corners/shots on stats rows only; raw shots mixes the two
feed definitions — F-feed-2.) Dev pooled (2021–2024): goals 2.647,
SOT 8.557 (median 8), corners 9.792 (median 10). Home advantage is
large from 2022 on (home goals ~1.6–1.7 vs away ~1.0); 2021 is the
odd year (Fase 2 away goals 1.44 > home 1.35 — the pandemic-era
season, neutral-venue contamination is plausible but not verifiable
from the payload; recorded, not modelled).

## F2 — Team trait reliability (career split-half, odd/even matches)

| Trait | r | | Trait | r |
|---|---|---|---|---|
| goals for | 0.666 | | corners against | 0.634 |
| goals against | 0.862 | | shots for (raw) | 0.643 |
| SOT for | 0.598 | | shots against (raw) | 0.610 |
| SOT against | 0.536 | | touches for (rich) | 0.666 |
| corners for | 0.731 | | touches against (rich) | 0.614 |
| possession for | 0.801 | | big chances for (rich) | 0.446 |

All count traits are real. Per-match corr with corners:
touches 0.571 vs possession 0.447 → X7's premise holds here.

**Cards traits must be era-restricted** (F-feed-1): on 2023+ only,
event yellows for r = 0.518, against r = 0.354 (26 teams) — real,
moderate. (The all-era computation gives a spurious 0.92/0.90
because 2021–22 are structural zeros; it is not used anywhere.)

## F-feed-1 — THE CARDS FEED ARTEFACT (present, era-flipped)

On rich dev matches (n = 507), stats-feed yellows vs event yellows:

| Era | exact match (inc-2nd) | mean events − stats |
|---|---|---|
| 2021 (n=40) | 0.0% | −4.88 |
| 2022 (n=156) | 1.9% | −4.90 |
| 2023 (n=159) | 68.6% | +0.32 |
| 2024 (n=152) | 77.6% | +0.23 |

Diagnosis: in 2021–2022 the event feed carries **no plain-yellow
Card events at all** (a 400-file raw scan finds only YellowRed and
Red), so events undercount by ~4.9/match — the events are the broken
source. From 2023 the direction flips to the programme's usual
shape: events slightly **exceed** the stats feed (+0.23…+0.32/match),
i.e. the stats feed undercounts modestly. Stats yellows cannot be
the target either: they exist only in rich matches, which are
**zero in every dev Clausura block**.

**Frozen consequence (prereg, before fitting):** the cards target
is **event-derived yellows including second yellows
(`ev_yellow_inc2nd`)**, and the cards candidate lives in the
**2023+ era only**: seed 2023 (n = 334), dev eval 2024 (n = 306),
virgin 2025 (n = 323). Cards-era dev mean 4.909, median 5 →
primary line **4.5**.

## F-feed-2 — Total shots is two quantities; unified target

Rich matches satisfy `total_shots = SOT + off + blocked` exactly
(100%). Sparse-block means (18–20) track rich `SOT + off`
(19.6–20.8), not the rich total (25–27). The sparse key therefore
measures shots **excluding blocked shots**. **Unified target:**
rich → `SOT + off-target`; sparse → `total_shots` as-is. Unified
dev mean 19.727, median 20 → primary line **19.5**; unified virgin
mean 19.593 (level-stable, unlike the raw key).

## F3 — Halves: frozen constants only

Pooled 1H shares + variance decomposition (per-match share):

| Market | share | n | true SD |
|---|---|---|---|
| goals (HT events, all eras) | **0.4377** | 1,704 | team-share split-half r = 0.151 (noise-grade) |
| SOT (splits era 2025–26) | **0.4611** | 503 | 0.081 |
| corners (splits era) | **0.4817** | 503 | 0.078 |
| total shots (splits era) | **0.4662** | 503 | 0.007 |
| cards (event times, 2023+) | **0.3818** | 1,232 | — |

No per-team or per-match half modelling: constants are
presentation-only splits of FT predictions. Note honestly: the
count-market constants are measurable only in the splits era
(2025–2026, which includes the virgin year) because the feed
carries no earlier splits; they are never a gate input.

## F-alt — Altitude: measured, NO league-wide premium

Home-city altitude classes (modal home city per club; elevations
are standard geographic values): high ≥ 2,300 m — 12 clubs (Cusco
3,400 ×3 clubs, Juliaca 3,825, Huancayo 3,259, Tarma 3,053,
Andahuaylas 2,926, Ayacucho 2,761, Cajamarca 2,750 ×2, Cutervo
2,649, Arequipa 2,335), n = 861 home matches; low < 700 m — 13
clubs, n = 911.

| Class | home goals | away goals | home win% | home GD |
|---|---|---|---|---|
| high ≥2,300 m | 1.635 | 1.080 | 49.2% | **+0.555** |
| low <700 m | 1.596 | 1.032 | 51.4% | **+0.564** |

The aggregate home edge at altitude is **identical** to sea level
— unlike the MX measurement (+0.586 vs +0.221). Individual
altitude clubs split by squad strength, not altitude: Melgar home
GD +1.08, Cusco FC +0.88, Cienciano +0.79, but UTC Cajamarca +0.10,
Comerciantes Unidos +0.06, Ayacucho −0.17; altitude clubs are
simply much worse away (Binacional −1.14, Los Chankas −1.08,
Comerciantes −0.96), which team attack/defence ratings already
absorb. Altitude is a fixed attribute of the home club, so in a
single-table league any altitude term would be collinear with
team identity on top of showing no class-level effect. **Recorded
and dropped** — the MX discipline, applied to a stronger null
(MODEL_DESIGN / FEATURES R-alt).

## F4 — Entrants (absent previous calendar year)

Dev-era entrants (7): 2022 Grau (GF 1.39 / GA 1.17), Tarma (1.08 /
1.36); 2023 Unión Comercio (1.17 / 2.00), Cusco FC (1.20 / 1.20),
Garcilaso (1.51 / 1.34); 2024 Comerciantes Unidos (1.06 / 1.76),
Los Chankas (1.24 / 1.38). Pooled vs the league per-team-match mean
(1.317): **ΔGF −0.082, ΔGA +0.142** → frozen X2 replacement ratios
attack ×0.9375 (ln = −0.0645), concession ×1.1078 (ln = +0.1024),
estimated from dev-era arrivals only. Virgin 2025 has four entrants
(Ayacucho FC, Alianza Universidad, Binacional, Juan Pablo II), so
the arm is live on the virgin, not decorative.

## F8 — Referee trait (cards era)

Coverage: 2023 97.9%, 2024 84.6%, virgin 2025 80.5%. Split-half
reliability of a referee's mean event yellows per match on
2023–2024: **r = 0.769** (16 referees with ≥ 12 matches) — the
strongest referee trait measured in the programme so far. X8 is
adopted; K-PE carries the standard pre-match availability
operational condition.

## Feasibility matrix

| Candidate | Target exists? | Virgin contains target? | Windows |
|---|---|---|---|
| G-PE goals | yes, all matches | yes | seed 2021, dev 2022–2024, virgin 2025 |
| S-PE SOT | stats rows (dev 1,111/1,216; virgin 280/323) | yes | same |
| C-PE corners | stats rows | yes | same |
| K-PE cards | events, **2023+ only** | yes | seed 2023, dev 2024, virgin 2025 |
| T-PE total shots | unified target (F-feed-2) | yes | same as S |

Primary lines from dev distributions: goals OU **2.5**; SOT
**8.5** (mean 8.557); corners **9.5** (mean 9.792); cards **4.5**
(mean 4.909, cards era); total shots **19.5** (unified mean 19.727).
