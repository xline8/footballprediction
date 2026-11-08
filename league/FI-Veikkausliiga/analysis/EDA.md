# Step 3 — EDA: FI-Veikkausliiga

All numbers from `analysis/eda.py` → `eda_summary.json` / `inventory_summary.json`
(run on `data/fi_matches.csv` before any fitting). Charts in `analysis/charts/`.

## F1 — Levels per season (per match)

| Season | Goals | Home G | Away G | SOT | Corners | Total shots | Yellows (events) |
|---|---|---|---|---|---|---|---|
| 2021 | 2.519 | 1.315 | 1.204 | 8.485 | 10.308 | 19.377 | 4.173 |
| 2022 | 2.958 | 1.509 | 1.449 | 8.880 | 10.479 | 16.898 | 4.287 |
| 2023 | 2.563 | 1.353 | 1.210 | 8.311 | 9.928 | 15.940 | 4.359 |
| 2024 | 2.946 | 1.665 | 1.281 | 8.198 | 10.048 | 15.162 | 4.431 |
| 2025 | 3.294 | 1.661 | 1.633 | 9.463 | 10.955 | **26.395** | 3.503 |
| 2026 (virgin) | 2.610 | 1.475 | 1.136 | 8.701 | 10.006 | **26.305** | 3.650 |

- Goals swing 2.52–3.29 across seasons in a 12-team league — season-level
  noise is large relative to the virgin n (177). 2025 (3.294) is the dev
  era's last season and its highest; the virgin falls back to 2.610.
- Home advantage is present but modest and unstable (2025: 1.661 vs 1.633,
  nearly zero; 2024: 1.665 vs 1.281).
- **Total shots break eras** (see DATA_UNDERSTANDING): thin-era 15.2–19.4 vs
  rich-era 26.3–26.4 with SOT flat — a feed definition change, not football.
- Event yellows drop from 4.43 (2024) to 3.50 (2025); the 2025 stats feed
  (3.46) corroborates its own era's event level (3.50).

## F2 — Team-trait reliability (split-half, career-pooled, 17 teams)

| Trait | r | Note |
|---|---|---|
| goals for | 0.674 | SIGNAL |
| SOT for | 0.532 | SIGNAL (weakest of the count traits) |
| corners for | 0.708 | SIGNAL |
| total shots for | 0.932 | overstated — era-mixed pooling across the definition break |
| yellows for | 0.778 | SIGNAL |
| possession | 0.898 | SIGNAL |

2025-only traits (12 teams, single season — read with care): touches_opp_box
for r = 0.835, fouls for r = 0.772, big_chance for r = 0.503. Reliable where
measured, but the keys exist in ONE dev season only (see FEATURES X7/X9).

## F3 — Halves shares (the frozen-constant question)

Event-time shares, dev era 2021–2025: goals 1H share **0.4295** (n = 790
matches with goals; observed share variance 0.1072 vs binomial 0.0805 —
excess +0.0267, larger than the top-5/J1 near-zero finding; the constant is
still the only halves mechanism the program allows, presentation only);
yellows 1H share **0.3109** (excess +0.0213, same caveat).
Period-split shares, 2025 only (the sole dev season with splits, n = 177):
SOT **0.4400**, corners **0.4631**, total shots 0.4527. Cards from splits
(stats target) would be 0.2969; the frozen cards constant is the event-based
0.3109, consistent with the event target.

## F4 — Entrants (X2 measurement)

8 entrant transitions 2022–2026 (club absent the previous season, in-corpus
identification; FI is tier 1, entrants are promoted clubs). Their first-season
GF/GA per match vs that season's league team mean: **GF −0.210, GA +0.159**
(n = 8) — the classic promoted-team pattern (score less, concede more),
same sign as J1's F4 and SE2's entrant measurement. SIGNAL for a goals arm.

## F5 — Dev-era distributions (primary-line evidence)

Dev scored seasons 2022–2025 (n = 678, all with stats):
- SOT mean 8.72; over-rates: 7.5 → 0.612, **8.5 → 0.481**, 9.5 → 0.373.
- Corners mean 10.36; over-rates: **9.5 → 0.547**, 10.5 → 0.445, 11.5 → 0.330.
- Yellows mean 4.14; over-rates: **3.5 → 0.587**, 4.5 → 0.395.
- Goals over-2.5 rate (dev era 2021–2025 pooled in EDA): 0.561.
Primary lines are the ones closest to 0.5 (frozen in the preregs):
SOT 8.5, corners 9.5, cards 3.5, goals OU 2.5.

## F6 — Cards artefact (pre-freeze check)

Stats vs events yellows, 2025: exact 81.9%, mean Δ −0.040/match.
2026: exact 76.8%, mean Δ −0.096/match. No era flip, no systematic gap of
the TH/ZA kind. The event target is forced by coverage (no stats keys
2021–2024), not by disagreement — see PREREG_K_FI.

## F7 — Reference points

Goals level (2.5–3.3) sits above J1 (2.4–2.7 era) and near SE-Allsvenskan;
corners ~10.0–11.0 are European-normal; SOT 8.2–9.5 is on the low side;
the virgin season (2026) is a LOW season on goals (2.61) and SOT (8.70)
relative to the dev era — calibration legs will feel that, and the gates
decide mechanically.
