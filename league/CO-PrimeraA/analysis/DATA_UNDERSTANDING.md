# Step 1 — Data Understanding: CO-PrimeraA (Colombia Primera A, FotMob id 274)

Builder's own corpus-wide audit over all 2,582 indexed files
(0 unreadable), cross-checked through two further independent
recounts after a first pass disagreed (see "Corpus stability" below).

## Inventory

- Index n = 2,582 (league_id 274), tournament season labels
  2021-Apertura … 2026-Clausura (12 tournaments):
  185 / 226 / 226 / 226 / 226 / 226 / 216 / 216 / 226 / 226 / 204 / 179.
- **Played corpus = ALL 2,582 files: every indexed file is finished.**
  The Primera B trap does NOT occur here — there are no unfinished
  0-0 placeholder files anywhere in 2021–2025 (verified per-file from
  `header.status.finished`, not from the index score column).
- 2026 - Clausura is IN PROGRESS (179 played at pull, regular phase
  only, last match 2026-11-09 = pull date). It is in the CSV but is
  excluded from every fit, gate, constant and verdict in this build
  (TRANSITIONAL; a season-end confirmatory read is a future,
  separately-registered step).
- 20 teams per tournament (19 in 2021 - Apertura). Team identity is
  FotMob team_id everywhere downstream; display names canonicalised
  to the id's most frequent spelling by the builder.
- **Corpus stability note (honest record):** a first audit pass read
  173 files of 2026 - Clausura as unfinished; two independent recounts
  minutes later read all 2,582 as finished. The warehouse was being
  refreshed concurrently that evening. The builder therefore ASSERTS
  the finished status and the per-season counts above: any future
  warehouse mutation fails the build loudly instead of silently
  changing the corpus.

## Format / phase rule (frozen)

Each calendar year holds TWO tournaments (Apertura, Clausura). Normal
shape: single round-robin regular phase (200 matches at 20 teams;
190 in 2024 after a one-match-per-round trim), quadrangular
semi-finals (top 8, two groups of 4, 24 matches), finals (2). Two
format deviations are in the corpus:

- **2021 - Apertura**: 19 teams, no quadrangular — a knockout playoff
  instead (14 matches flagged `final`: quarter/semi/final rounds).
- **2026 - Apertura (the virgin)**: 202 regular + 2 final, NO
  quadrangular (format change in the World-Cup year). The virgin's
  phase mix therefore differs slightly from dev tournaments; the
  gates are not adjusted for it (recorded here, decided in design).

Phase counts (finished corpus): regular 2,272 / quadrangular 264 /
final 46 across the 12 tournaments; every tournament 2021-Cl…2025-Cl
is exactly 200 + 24 + 2 (2024: 190 + 24 + 2).

**Phase rule (frozen, the CO-PrimeraB precedent judged on this
league's own data): every finished match is modelled — regular,
quadrangular and finals alike — with the phase recorded per match
(`phase` column). No phase filtering, no phase feature.** The
post-season phases are ~12% of each tournament, involve the same
clubs in the same tournament, and tournament-blocked fitting treats
train and target identically.

## Field coverage (finished corpus, share of matches per tournament)

| tournament | n | stats feed | period splits | stats xG | shotmap | referee | events exact* |
|---|---|---|---|---|---|---|---|
| 2021 - Apertura | 185 | 1.000 | 0.011 | 0.016 | 0.016 | 0.000 | 1.000 |
| 2021 - Clausura | 226 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| 2022 - Apertura | 226 | 0.996 | 0.013 | 0.000 | 0.000 | 0.996 | 0.987 |
| 2022 - Clausura | 226 | 1.000 | 0.009 | 0.004 | 0.004 | 1.000 | 1.000 |
| 2023 - Apertura | 226 | 1.000 | 0.628 | 0.004 | 0.004 | 0.978 | 1.000 |
| 2023 - Clausura | 226 | 1.000 | 1.000 | 0.000 | 0.000 | 0.942 | 1.000 |
| 2024 - Apertura | 216 | 1.000 | 1.000 | 0.014 | 0.014 | 0.949 | 0.995 |
| 2024 - Clausura | 216 | 1.000 | 1.000 | 0.019 | 0.019 | 0.958 | 1.000 |
| 2025 - Apertura | 226 | 1.000 | 1.000 | 0.044 | 0.044 | 0.987 | 1.000 |
| 2025 - Clausura | 226 | 1.000 | 1.000 | 1.000 | 1.000 | 0.912 | 0.996 |
| 2026 - Apertura† | 204 | 1.000 | 1.000 | 1.000 | 1.000 | 0.843 | 1.000 |
| 2026 - Clausura‡ | 179 | 1.000 | 1.000 | 1.000 | 1.000 | 0.827 | 1.000 |

\* goal-event count equals the header score total. † virgin.
‡ in progress, excluded.

Three era facts govern the whole design:

1. **The stats feed is present from the start** (~100% in every
   tournament: SOT, corners, total shots, yellows, big chances,
   possession). One single dev match lacks stats (2022 - Apertura;
   count targets missing there, goals present). Count markets have
   targets for the full 2021–2026 span — unlike PY, whose feed starts
   in 2025. Exception: `touches_opp_box` coverage dips to ~0.48–0.55
   in the Clausura tournaments of 2021–2023 (1.000 from 2024 on) —
   the X7 corners feature must live with the min-presence rule there.
2. **Stats-feed xG and the shotmap exist ONLY from 2025 - Clausura**
   (plus a handful of stray files earlier: ≤4.4% in any earlier
   tournament). The xG era starts at the last dev tournament / virgin
   boundary: no xG feature can be fitted or dev-gated (the ES-LaLiga2
   lesson — an era starting inside the evaluation span kills the arm).
   In its era xG under-runs goals (goals/xG = 1.172 over 2025-Cl +
   2026-Ap, n = 452) — descriptive only, used by no arm.
3. **Period splits exist only from 2023 - Clausura** (2023 - Apertura
   partial at 0.628). Halves constants for SOT/corners/shots are
   therefore measured on the 2023-Cl…2025-Cl window (see EDA F3).

Referee names exist from 2022 - Apertura (~0.94–1.00 per tournament;
0.843 in the virgin). Stadium (name + city) is present throughout;
the payload carries NO elevation field (altitude: see FEATURES).

## Cards feed check (dev-era evidence only, run BEFORE any fitting)

Two candidate targets disagree by era — this league's variant of the
programme-wide cards artefact (seventh league to show one):

| era | stats-feed yellows | event yellows | event unified (incl. 2nd yellow) | exact-match (unified vs stats) |
|---|---|---|---|---|
| 2022 - Apertura | 4.20 | 0.00 | 0.12 | 0.20 |
| 2022 - Clausura | 2.67 | 0.00 | 0.15 | 0.43 |
| 2023 - Apertura | 5.14 | 5.53 | 5.66 | 0.74 |
| 2024 - Clausura | 5.53 | 5.66 | 5.75 | 0.78 |
| 2025 - Clausura | 5.63 | 5.69 | 5.81 | 0.70 |

- **Card EVENTS are absent in 2021–2022** (event-unified mean ≈ 0.1 —
  a residue, not a count) and complete-looking from 2023 - Apertura.
- **The stats feed's own level breaks inside 2022**: 4.22 (2022-Ap)
  → 2.67 (2022-Cl) → 5.14 (2023-Ap). A near-halving and re-doubling
  within a year is a feed artefact, not football; the 2021–2022 stats
  yellows are not the same quantity as the 2023+ ones.
- From 2023 on, the two sources track each other (stats sits ~0.1–0.2
  BELOW the unified event count in every tournament — the familiar
  undercount direction).

**Decision (frozen in PREPROCESSING): the cards target is the
event-unified count, era 2023 - Apertura onward.** The cards
candidate is fitted and gated entirely inside that era. The virgin
tournament (2026 - Apertura) is inside the era. The stats-feed
yellows are used by no model.

## Movers (context for FEATURES X2)

Exactly TWO clubs are promoted from Primera B (id 9125) every year,
and every absent-from-A club is a B promotion (no other entrants in
2022–2026). The reverse flow of CO-PrimeraB's X2 question — how
promoted clubs perform in their first A season — is measured in
EDA F4: attack weaker in 8/8 dev club-years, defence weaker in 6/8.
