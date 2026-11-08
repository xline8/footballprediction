# Phase 4 — Model Design: US-USLLeagueOne Candidates

Each candidate mirrors the sibling production/J1 reference. Phase is frozen:
playoff rows are retained in the CSV but excluded from every fitting and
scoring window.

## Shared validation frame (all candidates)

- **Dev**: walk-forward over 2022–2024 regular matches, n=489; 2021 is
  warm-up and never scored. Cards use 2023–2024 valid regular rows, n=313,
  with a cold start at the 2023 opener. Count markets predict then update.
- **Virgin**: season **2025**, complete regular n=210, read once and only for
  arms that pass the dev gate. 2026 is reserved/transitional and never read.
- **Baselines**: league base rate at the primary line and naive trailing-10
  count-market baselines / climatology for goals.
- **Gate Zero**: the unmodified reference architecture, fitted per league,
  is itself an arm.
- **Gate legs (verbatim, frozen for every candidate)**: Dev gate — pooled
  dev LL at the primary line beats BOTH baselines, else arm dead, no virgin
  read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's;
  (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach
  within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for
  both-pass (variant's dev LL ≤ Gate Zero's in at least half the dev
  seasons). Both-pass: lowest pooled virgin LL ships; ties → simpler arm.
  If Gate Zero fails its own dev gate, the candidate verdict is FAIL
  regardless of variant dev numbers and the virgin is not read.
- **Calibration = actual − predicted** throughout this league.
- **Primary lines**: goals 2.5, SOT 8.5, corners 9.5, cards 5.5, total
  shots 24.5. The corners 9.5 choice is the exact-distance convention;
  cards 5.5 is the closer dev line arithmetically.
- Halves are FT plus frozen presentation constants only.

## Candidates

### G-USLL1 — goals DC goals-only

Gate Zero + SHR. A team with fewer than 8 training matches has lambda shrunk
50% toward league level. This handles the five 2025 expansion entrants in
their virgin season. No X2 offset or xG arm exists.

### S-USLL1 — SOT v5 pattern

Gate Zero + RS, with ratio prior 200→20000. No shotmap/xG quality arms exist.

### C-USLL1 — corners v3 pattern

Gate Zero with X9 possession and big-chance covariates + X7 box touches. X7
uses the minimum-8 trailing rule and Gate Zero fallback.

### K-USLL1 — cards

Target is valid stats-feed yellows only. Gate Zero + X8 referee arm. Dev is
2023–2024 valid rows with the 2023 opener as a cold start. Missing referee
falls back to Gate Zero without imputation.

### T-USLL1 — total shots family

Arms A (v1), B (v2 level layer, M̄ = 24.8 frozen, approximately the dev mean
24.837), and C (E9 trailing-r). Tuning season is 2022; gate pool is
2023–2024. Primary line is 24.5.

## Global forbidden list

No halves modelling, finishing/form, absence/lineup features, post-match
snapshots, conference features, imported tier offsets, or features without a
USL reliability check. No playoff row enters a fit or score.
