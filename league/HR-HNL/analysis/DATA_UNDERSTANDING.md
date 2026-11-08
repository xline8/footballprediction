# Step 1 — Data Understanding: HR-HNL (Croatia, FotMob id 252)

Source: FotMob world warehouse, `data_enrichment/fotmob_world/Croatia/HNL/<season>/<id>.json`,
index filter league_id = 252. One row per played match; 964 matches.
Measured by `analysis/eda.py` (`inventory_summary.json`, `eda_summary.json`).

## Inventory

| Season | Matches | Dates | Stats rows | Period splits | Referee named | Payload leagueName |
|---|---|---|---|---|---|---|
| 2021/2022 | 180 | 2021-07-16 – 2022-05-21 | 180 | 0 | 81 | 1. Division |
| 2022/2023 | 180 | 2022-07-15 – 2023-05-28 | 180 | 51 | 177 | 1. Division → HNL |
| 2023/2024 | 180 | 2023-07-21 – 2024-05-26 | 180 | 180 | 164 | HNL |
| 2024/2025 | 180 | 2024-08-02 – 2025-05-25 | 180 | 180 | 157 | HNL |
| 2025/2026 | 180 | 2025-08-01 – 2026-05-23 | 180 | 180 | 149 | HNL |
| 2026/2027 | 64 | 2026-07-31 – 2026-11-08 | 64 | 64 | 64 | HNL — IN PROGRESS |

- **Format — no split, no play-offs.** Every complete season is 10 teams ×
  36 rounds = 180 matches: a straight quadruple round-robin (each pair meets
  4×). `general.matchRound` runs 1..36 in every complete season and there is
  no phase field anywhere in the payloads — `general.leagueName` is the
  league's own name, not a phase (contrast FI-Veikkausliiga). All rows are
  regular-season rows; nothing is excluded on format grounds.
- **League size.** The task brief hypothesised a 12→10 contraction inside
  the window. It is NOT in this corpus: all five complete seasons (and the
  in-progress one) have exactly 10 FotMob team ids and 180 matches. The
  contraction predates 2021/2022. One club is relegated and one promoted
  per season (entrant list in EDA F4).
- **Rename.** The league was renamed 1. HNL → HNL during the corpus:
  payload `general.leagueName` is "1. Division" for all of 2021/2022,
  mixed "1. Division"/"HNL" inside 2022/2023, and "HNL" from 2023/2024 on.
  The warehouse directory already calls every season "HNL". Recorded per
  row as `league_name`; it has no modelling effect.
- **2025/2026 is the last COMPLETE season** (180/180 with scores, final
  round 2026-05-23) → frozen as the virgin window. **2026/2027 is in
  progress** (64/180, rounds 1–13 at the warehouse snapshot) → excluded
  from every fitting-relevant quantity; reserved as a future confirmatory
  read once complete.
- **Stats feed — rich in every season.** All 964 matches carry a stats
  block (36 keys: BallPossesion, total_shots, ShotsOnTarget/OffTarget,
  blocked_shots, shots inside/outside box, big_chance, corners,
  yellow_cards, red_cards, fouls, keeper_saves, …). `touches_opp_box` is
  present in a subset (114/180 in 2021/2022, 102/180 in 2022/2023,
  144/180 in 2023/2024, 180/180 from 2024/2025). Period splits
  (FirstHalf/SecondHalf) arrive during 2022/2023 (51/180) and are complete
  from 2023/2024; splits are internally consistent — All = 1H + 2H with
  0 mismatches on corners/SOT/total shots over 655 split matches
  (yellow_cards: 24 mismatches, see the cards note).
- **No xG, no shotmap — anywhere.** No `expected_goals*` key appears in
  any of the 964 payloads and `has_shotmap` is False for 964/964. Goals
  are a goals-only problem (X1 blend falls back to goals-only, its
  documented fallback); X3/X4/X6 are impossible by data absence.
- **Events — two eras.** 2021/2022–2022/2023 event feeds carry only Goal,
  Half and red-card events (no substitutions, no yellow cards). From
  2023/2024 the feed is full (Card incl. Yellow, Substitution, …).
  Event times are the halves source for goals in the dev era.
- **Cards — the stats-vs-events artefact is REAL and era-flipped here**
  (checked before any target freeze, per programme rule; full numbers in
  EDA F6):
  - Stats `yellow_cards` keys exist in every season, but the early-era
    (2021/2022–2022/2023) series is defective: mean 2.767 / 2.517 per
    match with **37.8% of matches showing zero total yellows in both
    seasons**, while fouls are stable (24.3 / 24.2 per match) and the
    rich era (2023/2024+) shows 4.144 / 4.250 / 3.961 stats yellows with
    a zero-share of only 1.1–5.0% at the same fouls level (25.4–26.6).
    The early-era 1H yellow share in the 51 split matches of 2022/2023
    is 0.145 — not a plausible football quantity (rich era ≈ 0.327).
  - Event yellows cannot rescue the early era: the event feed contains
    no yellow-card events at all before 2023/2024 (mean event "yellows"
    0.128/match = reds only).
  - In the rich era the two sources agree well (exact 83.3% / 78.3% /
    85.0%; mean stats − events −0.217 / −0.278 / −0.133) — the rich-era
    quantity is coherent; it is the early era that is a different,
    broken quantity.
  - Consequence: no single cards target spans a warm-up season + ≥3
    scored dev seasons + the virgin. The rich era offers only warm-up
    2023/2024 + one scored season (2024/2025) before the 2025/2026
    virgin. **K-HR is NOT BUILT** (T-FI precedent; see PREREG_K_HR).
- **Referee**: `infoBox.Referee.text` named in 81/180 (2021/2022),
  177/180, 164/180, 157/180, 149/180 — coverage is good from 2022/2023,
  but the trait itself fails reliability in this league (EDA F7,
  r = 0.239), so X8 is dropped on the number, not on coverage.
- **Team identity**: 13 distinct FotMob team ids across the corpus.
  Two ids carry two name spellings — 10165 "NK Varazdin" / "NK Varaždin"
  and 187866 "Rudes" / "Rudeš" (diacritic variants appearing from
  2025/2026). All logic keys on team id.
- **Levels** (per match, EDA F1): goals 2.356–2.800 (a low-scoring
  league; 2024/2025 only 2.356), SOT 7.478–8.722, corners 8.500–9.494,
  total shots 23.372–25.878 with a stable on-target share 0.320–0.343 —
  no total-shots definition break of the FI kind.
