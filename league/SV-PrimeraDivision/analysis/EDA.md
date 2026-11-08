# Step 3 — EDA: El Salvador Primera Division (FotMob 335)

All numbers are on **regular-phase** matches unless stated otherwise,
from `eda_numbers.json` (re-derived from the payloads via
`eda_numbers.py`; inventory in `inventory_summary.json`). Reference
points: J1 goals 2.68/match, home-win rate ~.44; GH goals 2.02/match,
home-win .571; NG goals 2.11/match, home-win .652.

## 1. Levels per tournament (regular phase)

| tournament | n | mean goals | H / D / A | O2.5 | BTTS | 0-0 |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 - Apertura | 132 | 2.67 | .409 / .318 / .273 | .500 | .591 | .053 |
| 2021/2022 - Clausura | 132 | 2.29 | .402 / .341 / .258 | .409 | .492 | .129 |
| 2022/2023 - Apertura | 67 | 2.49 | .493 / .299 / .209 | .478 | .507 | .119 |
| 2022/2023 - Clausura | 132 | 2.36 | .371 / .311 / .318 | .424 | .477 | .129 |
| 2023/2024 - Apertura | 132 | 2.72 | .402 / .288 / .311 | .508 | .568 | .091 |
| 2023/2024 - Clausura | 132 | 2.52 | .447 / .227 / .326 | .462 | .477 | .121 |
| 2024/2025 - Apertura | 110 | 2.40 | .418 / .218 / .364 | .445 | .427 | .073 |
| 2024/2025 - Clausura | 110 | 2.17 | .336 / .291 / .373 | .382 | .409 | .155 |
| 2025/2026 - Apertura | 132 | 2.73 | .379 / .280 / .341 | .545 | .568 | .098 |
| 2025/2026 - Clausura | 132 | 2.61 | .386 / .280 / .333 | .455 | .508 | .076 |
| 2026/2027 - Apertura (partial) | 115 | 2.70 | .400 / .330 / .270 | .496 | .565 | .113 |
| **Pooled, completed tournaments** | **1,211** | **2.51** | **.400 / .286 / .314** | **.462** | **.505** | **.103** |
| Playoffs (for the record) | 122 | 2.23 | .410 / .295 / .295 | .393 | .525 | .090 |

Reference reading:

- **El Salvador sits mid-table on scoring: 2.51 goals/match pooled**
  (vs GH 2.02, NG 2.11, J1 2.55–2.68). Home teams score 1.34 vs away
  1.17 per match, win **40.0%** and lose 31.4% — a much flatter home
  advantage than Ghana (57.1% home wins) or Nigeria (65.2%), and
  close to the J1 shape. Over-2.5 sits at 38–55% per tournament
  (pooled 46.2%) — near the top-5 level, so the OU2.5 base rate is
  not the near-automatic bar it is in Ghana.
- **No tournament is an outlier on level**: the range is 2.17–2.73
  goals/match, with the two low tournaments (2021/2022 Clausura
  2.29, 2024/2025 Clausura 2.17) both Clausuras — but 2023/2024 and
  2025/2026 Clausuras are 2.52 and 2.61, so there is no Clausura
  effect to fit; tournaments are scored as-is in dev.
- **Playoffs score lower (2.23) and go over-2.5 less (39.3%)** than
  the regular phase — one more reason the regular-phase-only rule
  is right: mixing them in would drag the level down and blur the
  ratings with knockout football.
- The in-progress 2026/2027 Apertura (n=115) sits on the pooled
  levels (2.70 goals, 40.0% home wins) — a partial-tournament
  sample, not a trend claim; it is the reserved confirmatory
  window, not interpreted here.

SOT / corners / cards / total shots: **no levels exist** — the targets
are absent from every payload (DATA_UNDERSTANDING.md §2/§4). There is
nothing to tabulate, and no proxy is constructed.

## 2. Team trait reliability (the J1 checklist, goals only)

Split-half by tournament: each team's regular-phase matches split
chronologically into halves; Pearson r of per-match rates across
halves (teams ≥10 matches, ≥5 per half); pooled across tournaments.

| trait | 21/22 Ap | 21/22 Cl | 22/23 Ap | 22/23 Cl | 23/24 Ap | 23/24 Cl | 24/25 Ap | 24/25 Cl | 25/26 Ap | 25/26 Cl | 26/27 Ap* | pooled |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| goals for | .549 | .632 | .219 | −.317 | .041 | .555 | .574 | .507 | .475 | .479 | .259 | **.372** |
| goals against | .447 | .081 | .321 | .675 | .673 | .296 | −.015 | .574 | .508 | .404 | .326 | **.360** |

\* 2026/2027 Apertura partial (12 teams qualify on a 19-round split);
shown for completeness, not used in any decision.

**Both goal traits are moderately reliable.** Goals-for split-half r
is **.372 pooled** (130 team-tournaments) — positive in 10 of 11
tournaments, above .47 in six of them; the two weak readings
(22/23 Clausura −.317, 23/24 Apertura .041) are single-tournament
noise on ~11-match halves, not a refutation. Goals-against is
**.360 pooled**, positive in 9 of 11. The season-year check (Apertura
+ Clausura pooled per team, n=71 team-years) is stronger still:
attack **.464**, defence **.407**. That is a different league from
Ghana (attack r=−.03 pooled): Salvadoran attacking strength persists
within a tournament while Ghanaian attacking output does not. The DC
ratings therefore have real signal to work with here — which is what
the dev gate will adjudicate. **No trait-based feature is adopted on
this evidence** — the goals model uses only the DC ratings
themselves, which are the §2 architectural component, not a
covariate claim.

## 3. Home advantage

Home goals 1.34 vs away 1.17 pooled (ratio 1.14:1); home-win rate
40.0% vs away-win 31.4%. The fitted DC home parameter will absorb
this; no separate home-advantage feature is needed or used. Note the
one odd tournament: 2025/2026 Apertura away teams outscored home
teams (1.38 vs 1.36) — a single-tournament fluctuation, not a
structural fact.

## 4. Half shares (the frozen-constant question)

HT goals from Half events (1,115 trusted HT rows over completed
tournaments; the 2 event-less non-0-0 matches have no HT).

| tournament | HT coverage | 1H share (ratio of sums) |
|---|---:|---:|
| 2021/2022 - Apertura | 126/132 | 0.4160 |
| 2021/2022 - Clausura | 120/132 | 0.4205 |
| 2022/2023 - Apertura | 60/67 | 0.4611 |
| 2022/2023 - Clausura | 123/132 | 0.4391 |
| 2023/2024 - Apertura | 122/132 | 0.4262 |
| 2023/2024 - Clausura | 117/132 | 0.4347 |
| 2024/2025 - Apertura | 103/110 | 0.4394 |
| 2024/2025 - Clausura | 95/110 | 0.4603 |
| 2025/2026 - Apertura | 124/132 | 0.4488 |
| 2025/2026 - Clausura | 125/132 | 0.4116 |
| 2026/2027 - Apertura (partial) | 104/115 | 0.4290 |
| **Pooled, completed** | **1,115/1,211** | **0.4335** |

- **Frozen goals constant: 0.4335** (pooled ratio of sums; 1,313 HT
  goals / 3,029 FT goals over the trusted HT rows of completed
  tournaments).
- **The per-match 1H share is noise**: observed variance of the
  per-match 1H share 0.11581 vs the binomial noise floor 0.12005 —
  excess variance **−0.0042**, i.e. below the floor, exactly the
  finding that closed the halves book in production. Team-level
  1H-share split-half r = **−0.076** (125 team-tournaments) — no team
  tendency. The constant is presentation only, never fitted, never
  per-team.
- **Level note**: El Salvador scores 43.3% of its goals before
  half-time — between J1 (0.412) and Ghana (0.462), close to RU2
  (0.439). That is a league-level fact, not a modelling input beyond
  the constant.

## 5. Turnover / movers

New team ids per Apertura (Clausura always fields the identical set
— 0 new ids in every Clausura): 2022/2023: 1 (CD Dragon in,
Municipal Limeno out); 2023/2024: 2 (Municipal Limeno back, Fuerte
San Francisco in; AD Chalatenango and Atletico Marte out);
2024/2025: 1 (CD Cacahuatique in; Santa Tecla FC and Jocoro FC out,
and the league drops to 11 teams); 2025/2026: 2 (Inter FA and
Zacatecoluca in; CD Dragon out); 2026/2027: 2 (Atletico Balboa and
Inca Aruba in; Once Deportivo/Hercules and Zacatecoluca out). Every
season-year brings 1–2 promoted sides from the Salvadoran Segunda
Division (not in the warehouse, unbuilt). They enter the DC fit at
the league mean in Gate Zero; the SHRINK arm (MODEL_DESIGN §2) is
the sanctioned thin-data treatment. No cross-league mover prior
exists (no built Salvadoran sibling), so no X2 offset is estimated.
