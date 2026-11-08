# Step 1 — Data Understanding: FI-Ykkonen

Finland Ykkönen / Kakkonen (tier 3 faktual), FotMob league_id 8969.
Calendar-year seasons 2021–2026, 1,730 played matches in the bundle
index (`index_8969.csv`, 1,730 rows). Warehouse mirror:
`data_enrichment/fotmob_world/Finland/Ykkonen/`.

## Identity break — the central fact of this league

FotMob league_id 8969 **changes identity mid-corpus** (from
`general.leagueName` in the raw JSONs):

- **2021–2023 = Kakkonen** (tier 3 lama): three parallel groups
  Lohko A/B/C, 12–13 teams per group, 36–37 teams per season,
  396/438/410 matches incl. promotion groups + playoffs in
  2022–2023. The three groups never meet in the regular season.
- **2024–2026 = Ykkönen** (tier 3 pasca-restrukturisasi): 12 teams,
  132 regular + 15 championship + 15 relegation = 162/musim.

Tier faktual sama (tier 3) di kedua era. Kontinuitas tim tinggi:
11/12 tim Ykkönen 2024 pernah main Kakkonen 2021–2023 (10/12 di
2023); 9/12 tim 2025 ada di 2024 (inventory). Detail kuantitatif
di EDA.md (F7–F9); implikasi split di MODEL_DESIGN.md.

## Format

- Kakkonen regular: `kakkonen_a/b/c` (132 match per grup per musim;
  2022 grup B 13 tim, 156 match). Promotion groups 2022:
  `kakkonen_promo_a/b/c` (6 match tiap grup, top-4 tiap Lohko,
  masih intra-grup). 2023: `kakkonen_promo_playoff` (10 match) +
  `kakkonen_playoff` (4 match) — satu-satunya match lintas grup
  di era Kakkonen (lihat EDA F8).
- Ykkönen: `ykkonen` (132), `ykkonen_championship` (15),
  `ykkonen_relegation` (15). Semua baris adalah baris biasa
  berflag fase, tidak pernah difilter.
- Musim kalender (Mei–Okt approx.). 57 distinct FotMob team id
  sepanjang korpus; 54 di era Kakkonen, 12 di Ykkönen 2024.

## Feeds (measured, `eda_summary.json` / `inventory_summary.json`)

- **Stats feed: 0/1,730 matches in every season.**
  `content.stats` carries no `Periods` key anywhere. No xG, no SOT,
  no corners, no shots, no yellows from stats. Period splits: 0.
  This is a **scores-only league** — confirmed, not assumed.
- **Shotmap: 0/1,730.** No xG anywhere.
- **Events: 1,675/1,730** (2021: 381/396, 2022: 427/438, 2023:
  396/410, 2024: 155/162, 2025: 159/162, 2026: 157/162). The 55
  matches without events are all scoreless (0 goals in them) —
  their events-derived fields are missing, never zero.
- **Lineups: 0/1,730** in every season. Not used by any candidate.
- **Referee: named in 0/1,730 matches, every season.** X8 is
  impossible by data absence.
- Event goals agree with the header score in all but 7 matches —
  the 7 awarded matches (header wins). Header `scoreStr` is
  authoritative throughout.

## Scores

- Goals/match by season: 3.32 / 3.43 / 3.33 / 3.51 (dev 2021–2024),
  3.48 in the virgin 2025 (inventory), 3.62 in the reserve 2026
  (inventory). OU2.5 over-rate 0.63–0.71 dev; home-win rate
  0.44–0.49; draw rate 0.19–0.20.
- Total goals in corpus: 5,898. Dev-era (2021–2024) goals: 4,748
  (n=1,406); dev scored window 2022–2024: 3,435 goals (n=1,010).
- Seven awarded matches (2021: 1, 2022: 2, 2023: 2, 2024: 1,
  2025: 1 inventory): header score is the awarded score
  (0-3 / 3-0) and differs from event goals. Kept as ordinary rows
  with `awarded=true` (never silently dropped); excluded from dev
  halves by construction. Detail in `eda_summary.json`
  (`awarded_detail`).

## Identity

- All logic keys by FotMob team id. One id carries two spellings:
  112425 = "GrIFK Grankulla" vs "GrIFK" (same club). No other
  name conflicts. Team names in the CSVs are as published per
  match; the engine keys by id.

## Split (SUGGESTED by the brief — NOT frozen; see MODEL_DESIGN.md)

- Dev: seasons ≤ 2024 (warm-up 2021, scored 2022–2024, n=1,010).
- Virgin: 2025 (complete, n=162) — read ONCE per dev-passing
  candidate (G only can pass).
- Reserve: 2026 (n=162) — untouched, confirmatory reserve.
- **Fase 3 DITAHAN**: the split is undecided because 3 of the 4
  dev seasons are a different competition (Kakkonen) from the
  virgin (Ykkönen). Options + evidence in MODEL_DESIGN.md;
  Jarvis decides.
