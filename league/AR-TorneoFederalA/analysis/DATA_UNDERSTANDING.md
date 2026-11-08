# Argentina Torneo Federal A — data understanding

## Inventory

The parent FotMob index contains 5,455 rows. Filtering payload `general.leagueName` to `Federal A*` gives 3,219 rows from 2021-04-10 through 2026-11-08. All are finished and scored. The Federal A group-phase table contains 2,992 matches: 450, 544, 576, 477, 486, and 459 by season. The 227 exclusions are 15, 15, 17, 61, 65, and 54 by season (promotion playoff, championship/relegation playoff, and the 2026 Additional match).

The group format is: 2021 two zones (240 + 210); 2022 two 17-team zones (272 + 272); 2023 four nine-team zones (144 each); 2024 first phase 324 plus promotion 72 and relegation 81; 2025 first phase 324 plus promotion 72 and relegation 90; and the virgin window is defined only by its inventory count of 459 group matches, consisting of first phase 306 plus second phase 153. Second-phase zones are ordinary league rows and are retained, consistent with the DK-Superligaen precedent.

Distinct team ids by season are 31, 34, 36, 38, 38, and 37. Identity is the FotMob id; canonical spelling is the latest spelling observed for that id. The 2023 Zona A feed has 135 rows named `Federal A Zona A` and 9 named `Federal A Zona А`, where the final A is Cyrillic U+0410. The builder merges them by zone interpretation while retaining the original tournament label.

## Field coverage and quirks

Stats are absent: zero of 3,219 payloads has a non-empty `content.stats.Periods.All`. Shotmap shots are absent in all 3,219. Referee text is empty in all 3,219. Events are represented on every payload, but cards are only `Red` and `YellowRed`; there are zero Yellow events. Federal A red-event counts in the full inventory are 121 / 150 / 213 / 149 / 169 / 136 by season. Therefore SOT, corners, total shots, xG, and Yellow-card targets do not exist.

There are no period-split stats. Halves can only be recovered from integer goal event times, with time <=45 treated as first half; events at exactly 45 and 46 are recorded rather than silently reassigned. The EDA uses no 2026 outcomes or descriptive statistics.

## Header/event feed holes

There are ten header/event goal mismatches in the Federal A inventory. Nine have empty event lists and one is the malformed 2026-08-12 payload below. Header scores are authoritative, and all ten are excluded from halves estimation. The ten are:

| match id | date | home | away | header |
|---|---|---|---|---|
| 4438620 | 2024-06-09 | Sansinena BB | Germinal | 0–1 |
| 4438584 | 2024-06-16 | Deportivo Rincon | Sansinena BB | 1–0 |
| 4438589 | 2024-06-23 | Sansinena BB | Sol de Mayo | 0–1 |
| 4438594 | 2024-06-30 | Circulo Deportivo | Sansinena BB | 1–0 |
| 4438599 | 2024-07-07 | Sansinena BB | Kimberley | 0–1 |
| 4438645 | 2024-07-14 | Santamarina | Sansinena BB | 1–0 |
| 4438842 | 2024-07-14 | Sarmiento de Resistencia | Union de Sunchales | 0–1 |
| 4558776 | 2024-07-28 | Gimnasia y Esgrima de Concepcion | Douglas Haig | 0–1 |
| 5978435 | 2026-08-12 | Defensores de Belgrano de Villa Ramallo | Douglas Haig | 0–0 |
| 6462025 | 2026-10-25 | Boca Unidos | Gimnasia y Esgrima de Chivilcoy | 0–3 |

The 5978435 payload is the inventory detail that did not verify literally: its event list is not empty, but contains a `<TBD>` goal while the header remains 0–0. The corrected statement is “nine empty-event feed holes plus one malformed event/header hole.” Nine of the ten are group-phase rows (ht NaN in the CSV); 6462025 is a Promotion Playoff row, excluded from the group CSV as a playoff. The PBM-named 2024 Tercer Ascenso final is excluded from both league builds and is not in this CSV.

Empty event lists also occur on 0–0 rows; the Federal A group CSV has 48 / 60 / 60 / 59 / 49 empty-event 0–0 rows for the first five seasons. They contribute header FT goals of zero and no event-time halves.
