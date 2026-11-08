# Phase 1 — preprocessing

The source is data_enrichment/fotmob_world_index.csv, filtered to league_id == "71"; each index path is resolved against the main checkout. Rows are sorted by date and match id. Finished rows with header.status.awarded == true are excluded before any table is made.

Team identity uses FotMob ids throughout. Names are display labels only, so Fatih Karagümrük/Karagumruk (2088), Gaziantep/Gaziantep FK (4081), Göztepe/Goztepe (1925), and Istanbul Başakşehir/Başakşehir (1933) cannot split a team history.

Full-time goals come from header.status.scoreStr; first-half goals come from Goal events with time ≤45. Stats are flattened from content.stats.Periods for All, FirstHalf, and SecondHalf. The match table preserves stat-feed values, event ev_* audit counts, source flags, referee text, coverage flags, and regulation-only shotmap aggregates. The team-match table is two rows per played match with for/against targets.

Cards follow the BE template: stats-feed yellow_cards is the unified target; when that block is absent, event yellow counts are the fallback, while event counts remain explicit cross-check columns. TR adds one frozen extension (dev-era evidence, see DATA_UNDERSTANDING): when stats yellows are 0–0 but the event feed records yellows, the stats discipline block is broken and event yellows are the fallback (`cards_source='events_broken_stats'`, 47 rows). No played score-only/stub row was found. Shotmap aggregates exclude penalty-shootout attempts. expectedGoalsOnTarget is retained with a population count so its era break can be measured rather than imputed.

No imputation, cross-season name matching, phase split, odds join, or model fitting is performed in this phase. The output files are tr_matches.csv and tr_team_matches.csv.
