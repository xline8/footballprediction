# Step 2 — Preprocessing: FI-Veikkausliiga

Builder: `data/build_data.py` (adapted from the SE-Superettan builder), output
`data/fi_matches.csv` (1,017 rows, gitignored, reproducible) + `fi_team_matches.csv`.

Inclusion rules (frozen):
1. Played matches only (`header.status.finished`), league_id 51, seasons
   2021–2026 as labelled in the warehouse. All 1,017 index rows survive.
2. FT score from `header.status.scoreStr`. Phase from `general.leagueName`:
   regular / championship / relegation / ecl_playoff (counts per season in
   DATA_UNDERSTANDING). Phase is a flag only — no phase is excluded, and no
   cross-tier play-off rows exist in this feed to exclude.
3. Stats targets (SOT, corners, total shots, possession) from
   `content.stats.Periods.All`; period-split values from FirstHalf/SecondHalf
   where they exist (2025–2026 only). A match whose stats block is missing
   (32 regular-phase matches in 2021) gets NULL targets and is excluded from
   that market's scoring — never imputed, never fabricated.
4. Cards target = event-derived unified yellows: Card events with
   `card in {Yellow, YellowRed}` per side (a YellowRed contributes one
   yellow); reds recorded separately (`Red` + `YellowRed`) and are not part
   of the target. The stats-feed card columns are ALSO stored
   (`stats_yellow_*`, `stats_red_*`, present 2025–2026 only) so the
   stats-vs-events comparison in EDA.md is reproducible from the CSV.
   Rationale for the event target: PREREG_K_FI (stats keys absent 2021–2024;
   agreement where both exist is close, no era flip).
5. Halves inputs: 1H goals and 1H yellows counted from event times
   (`time <= 45` = first half, including 45+ stoppage, which FotMob reports
   as time 45 with overload). SOT / corners / total shots halves come only
   from the 2025 period splits — no other halves source exists for them.
6. Team key = FotMob team id (17 ids, names stable). Ordering everywhere is
   (date, match_id); same-date matches never see each other in any
   walk-forward.
7. Windows frozen pre-fitting: goals/cards warm-up 2021, dev scored
   2022–2025, virgin 2026; stats markets warm-up 2021 (130 stats rows),
   dev scored 2022–2025 (678 stats rows — every dev match carries stats),
   virgin 2026 (177 stats rows). The dev harness never loads virgin rows;
   the virgin is read once, only for dev-passing arms.
