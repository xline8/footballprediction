# Step 3 — EDA (SK-1Liga)

Computed by `analysis/run_eda.py` → `analysis/eda_numbers.json`
(included phases only; dev era for reliability/halves/movers =
2021/2022–2024/2025). Charts: `analysis/charts/` via
`analysis/make_charts.py`.

## F1 — Levels per season (per match, included phases)

| Season | n | Goals | Home G | SOT | Corners | Total shots | Event yellows | Stats n |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 192 | 2.61 | 1.45 | 8.37 | 10.11 | 19.82 | 3.66 | 131 |
| 2022/2023 | 192 | 2.77 | 1.55 | 9.20 | 10.45 | 20.22 | 4.18 | 192 |
| 2023/2024 | 192 | 2.72 | 1.47 | 8.50 | 9.48 | 17.80 | 3.82 | 187 |
| 2024/2025 | 192 | 2.79 | 1.47 | 8.92 | 10.10 | 19.24 | 4.36 | 189 |
| 2025/2026 (virgin) | 192 | 2.82 | 1.51 | 8.83 | 9.89 | **27.10** | 4.01 | 192 |
| 2026/2027 (in progress) | 84 | 3.27 | 1.62 | 9.96 | 10.06 | 29.12 | 3.82 | 84 |

Goals are level-stable (2.61–2.82 across the complete seasons);
SOT and corners are level-stable; event yellows oscillate
3.66–4.36 with no trend. Total shots breaks at the rich-feed
boundary (+~40% into the virgin season) — DATA_UNDERSTANDING
defect 1. 2026/2027 is a partial regular phase and is shown for
inventory only.

## F2 — Team trait reliabilities (split-half, odd/even matches,
team-season units, dev era; n = 48 units)

| Trait | r (for) | r (against) |
|---|---|---|
| Goals | 0.591 | 0.293 |
| SOT | 0.549 | 0.552 |
| Corners | 0.395 | 0.435 |
| Event yellows | 0.194 | 0.474 |
| Possession | 0.784 | 0.784 |
| Total shots (report only) | 0.729 | 0.623 |

All candidate targets have real team traits. The weakest are
yellows-for (0.194 — real but modest) and goals-against (0.293).
Possession is the league's most reliable trait (0.784), supporting
the corners Gate Zero covariate (X9 reduced form). Total-shots
traits are reliable inside the dev era; the target still fails
feasibility on the cross-era definition break (F1), not on trait
quality.

## F3 — Halves (event times, dev era): frozen constants, team shares are noise

Pooled 1H shares: **goals 0.4448** (2,091 goals), **yellows
0.3357** (3,077 yellows). Variance decomposition (per-match share
variance vs binomial noise at the pooled share): goals observed
0.1123 vs noise 0.1141 → true variance ≈ **−0.0018 (≈ 0)**;
yellows observed 0.0773 vs noise 0.0758 → true variance +0.0016
(tiny). Team split-half reliability of the 1H share: goals
r = 0.035, yellows r = 0.103 — **per-team half shares are pure
noise** (the J1 F3 result replicates). Only the league constants
ship, presentation-only. Stats markets (SOT/corners/total shots)
have **no dev-era halves source** (period splits exist only from
the virgin season) → those markets are frozen **FT-only**
(RU-1Division precedent).

## F4 — Movers (X2 evidence; 2. Liga id 8973 in-warehouse)

First-season deviation from the 1. liga per-team-match mean
(included phases, 32 matches per club). 2022/2023 has THREE
arrivals, not one: the 2021/2022 licence collapses (Senica, Sered)
plus relegation opened three slots.

| Boundary | Club | ΔGF/match | ΔGA/match |
|---|---|---|---|
| →2022/2023 | Dukla Banska Bystrica | +0.180 | +0.367 |
| →2022/2023 | Zeleziarne Podbrezova | −0.008 | −0.008 |
| →2022/2023 | Skalica | −0.195 | −0.195 |
| →2023/2024 | FC Kosice | −0.518 | +0.388 |
| →2024/2025 | Komarno | −0.268 | +0.107 |
| →2025/2026 | Tatran Presov | −0.505 | −0.068 |

Attack: 5 of 6 arrivals score below the league mean — the J1 F4
direction, at smaller magnitude. Defence: mixed (3 of 6 concede
above the mean; Podbrezova/Skalica arrived as strong defensive
sides and Presov conceded below the mean). Cumulative mean offsets
from transitions completed before each target season (frozen for
the prereg): before 2023/2024 (−0.008, +0.055); before 2024/2025
(−0.135, +0.138); before 2025/2026 (−0.162, +0.132). Before
2022/2023 no transition is completed inside the warehouse window
→ X2 ≡ Gate Zero for that evaluation season by construction.
Verdict: **SIGNAL-CANDIDATE, weaker and less symmetric than CZ/J1**
— adopted as a preregistered arm; the gate decides.

## F5 — Referee strictness: NOT ESTIMABLE

Referee names exist in 0/768 dev-era included matches (feed
defect 3). No reliability number can be computed; X8 is dropped
on data absence in the dev era, not on a failed test.

## F6 — Cards artefact (frozen target check)

The stats feed carries no `yellow_cards` key in the dev era
(1 of 768 included matches), so the event target is the only
all-era source — by construction, not by preference. Virgin-era
audit where both exist (n = 192): exact total agreement 159/192
(82.8%), means 4.016 (stats) vs 4.005 (events) — a +0.010/match
stats-minus-events gap, i.e. **no era artefact and no level
shift** (contrast the era-flipped artefacts found in TH/ZA).
Event-unified yellows are frozen as the target (Step 2).

## Primary lines (dev pooled, included phases; over-rate closest to 0.5)

- SOT **8.5** (over 0.4807, n = 699; 7.5 → 0.5994, 9.5 → 0.4006)
- Corners **9.5** (over 0.5436, n = 699; 10.5 → 0.4077, 11.5 → 0.3176)
- Cards **3.5** (over 0.5794, n = 768; 4.5 → 0.3867, 5.5 → 0.2435)
- Goals: programme-standard OU2.5 (dev over-rate 0.5091, n = 768)
