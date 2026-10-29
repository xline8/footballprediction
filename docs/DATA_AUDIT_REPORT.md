# Data Audit & Gap Analysis

**Date:** 2026-10-27
**Scope:** Current scraping ecosystem vs. requirements of the 1X2 meta model, the corner engine, and the live shadow tracker.
**Method:** Read every scraping/enrichment module; inspected actual column headers of `all_matches_clean.csv` (70,425 rows), `all_matches_enriched.csv`, `records_cache.jsonl`, and the live `ta/odds_markets_snapshots.csv`; verified per-column fill rates for the critical odds fields.

---

## Step 1 — Current Scraping Flow (as-built)

### Source 1: football-data.co.uk → `download.py` → `raw/` → `all_matches_clean.csv`
This is the backbone. One row per match across 21 leagues, 10 seasons. Verified columns present (with fill rates on the full file):

| Category | Columns | Verified fill |
|---|---|---|
| Result & stats | `FTHG/FTAG/FTR`, `HTHG/HTAG/HTR`, `HS/AS`, `HST/AST`, `HC/AC`, `HF/AF`, `HY/AY`, `HR/AR` | ~100% |
| 1X2 odds | `B365H/D/A`, `PSH/PSD/PSA` (Pinnacle), `MaxH/D/A`, `AvgH/D/A`, + ~15 bookmakers | 54–55k rows |
| Over/Under 2.5 | `B365<2.5/>2.5`, `P<2.5/P>2.5`, `Max<2.5/Max>2.5`, `Avg<2.5/Avg>2.5` | 48–55k |
| Asian Handicap | `B365AHH/AHA`, `PAHH/PAHA`, `MaxAHH`, `AvgAHH` | 48–54k |
| Cards O/U 2.5 | `B365C<2.5/C>2.5`, `MaxC<2.5/C>2.5`, `AvgC<2.5/C>2.5` | 54.9k |

**Critical reading of the `C` columns:** the `B365C<2.5` family is the **cards** over/under market (line 2.5), not corners. There is **no corner over/under column at any line (9.5/10.5/11.5)** anywhere in this file. Corner data here is *statistical only* (`HC`/`AC`), never priced.

### Source 2: Understat → `refresh_fixtures.py` (fixtures) + `fetch_xg.py` (xG)
- Fixtures: `xg_raw/*_2026_fixtures.json` — real, refreshed daily, used for `predict_upcoming`.
- xG: `fetch_xg.build_xg_map()` prefers local cache `XGRAW/xg_matches.csv`. **The remote path (`fetch_understat_xg`) is a stub** — it performs a GET, verifies the string `"xG"` appears in the HTML, then returns `[]` without ever parsing a single match. So xG is effectively only what the pre-existing local file has.

### Source 3: tipsterarea → `ta_scrape.py` → `ta/*.csv`
Live multi-bookmaker snapshots. Verified market distribution in `odds_markets_snapshots.csv`:

| Market | Rows |
|---|---|
| Over/Under | 9,336 |
| Standard 1X2 | 4,738 |
| Double Chance | 4,694 |
| BTS | 3,119 |
| Draw No Bet | 2,138 |
| **Corners** | **0** |

The scraper and the new `export_corner_odds()` are generic and will capture corners the moment the source lists the market — but tipsterarea's pages currently contribute **zero corner rows**. Everything below 1X2/O/U is secondary.

### Enrichment layer (`all_matches_enriched.csv`)
Adds: `ps_home/draw/away`, `mx_home`, `av_home`, `midweek_home/away_flag`, `xg_home/away`, `rolling_xg_diff`. This is the input to the 17-feature meta model. Good. But note `rolling_xg_diff` **falls back to actual goal difference when `xg_*` is absent** (see `enrich_pipeline.rolling_xg_diffs`), so at any point where xG is missing, that feature is silently re-labelled goal-differential.

---

## Step 2 — Cross-Reference with Model Requirements

### A. 1X2 meta model (`backtest_picks.py` → `make_picks_live.py`)
**Required:** historical + current 1X2 odds (B365/Pinnacle), match results, DC lambdas, T3 features, Pinnacle PS, midweek flags, rolling xG.
**Verdict: fully supplied.** `records_cache.jsonl` confirms every required key (`ph_dc`, `ph_t3`, `o`, `ps`, `mw_h/a`, `rollxg`, `ph_meta`). Backtested to log-loss 1.0013. **No data gap here.** The pipeline is data-complete for both historical backtest and live shadow.

### B. Corner engine (`model_corners_v3.py`, Phase 15/16)
**Required for the model itself:** corner counts (`HC/AC`) + shots (`HS/AS`) → **supplied** by the clean CSV. The model is built and validated on these stats, and its predictive power already beats base-rate (LL/Brier/MAE/RMSE).
**Required for ROI validation:** historical **corner over/under odds**. → **MISSING (total).** No source in the system has them; the new `export_corner_odds()` has nothing to export. This is the exact blocker T10.

### C. Derivative/BTTS engine (`matrix_pricer.py`, Phase 13)
**Required:** the model *derives* O/U 2.5 and BTTS probabilities from the calibrated scoreline matrix — no odds required to produce probabilities.
**Required for ROI backtest:** historical O/U 2.5 and BTTS odds.
- O/U 2.5: **supplied** (`B365<2.5/P<2.5`). Already backtested → no edge.
- BTTS: **missing as A clean column** (no `BTS` yes/no odds in the CSV). However, tipsterarea *does* capture BTS live (3,119 rows) — so it is obtainable, just not historical/deep.

### D. Live shadow (`run_daily_shadow.py`)
Uses the 1X2 meta path → supplied. Corner and derivative paths are idle because the ROI gate can't be run.

---

## Step 3 — The Missing Pieces, Impact, and Sources

### Gap 1 — Historical corner over/under odds (blocks Phase 15/16)
- **Missing:** any line of corner O/U odds (9.5/10.5/11.5), any bookmaker, any season.
- **Impact:** the corner model is *qualified* (predictive signal proven) but **cannot be validated for ROI**. Per protocol, no live/shadow corner strategy may activate until the dual gate (significance + N≥500) runs against real odds. This is the single most concrete blocker in the project.
- **Recommendations:**
  1. **API-Football** (first choice): `/odds` endpoint with `market="Corners Over/Under"` — it covers the top-5 leagues historically and returns bookmaker odds per line. This matches the pre-built `MockCornerOddsClient` signature in `fetch_corner_odds.py` exactly; replace the mock with a real client (it already expects `lines=(9.5, 10.5, 11.5)`).
  2. **Sportmonks** — premium football odds API with corner-market coverage; alternative if API-Football quota/price is a problem.
  3. **OddsPortal** — scrape `football/.../corners` pages; CSV lines `9.5/10.5/11.5`, ship as `external_corner_odds.csv`. This feeds the already-working `parse_corner_odds_csv` → `merge_to_records` path with zero code change.
  4. Note on football-data.co.uk: it does **not** carry corner pricing; do not spend cycles re-checking it.

### Gap 2 — Historical BTTS odds (blocks Phase 13 BTTS backtest)
- **Missing:** clean historical `BTS yes/no` odds column.
- **Impact:** BTTS backtest is skipped (logged as T9); the matrix pricer still prices BTTS live, but with no ROI validation.
- **Recommendations:** extend `ta_scrape` capture for BTS on more historical days (the parser already handles the market; it's a data-depth issue, not a code issue). Or pull the `BTS` columns from a football-data-style feed that carries them; API-Football `market="Both Teams To Score"` is the clean route.

### Gap 3 — Opening vs. closing odds / odds movement (limits true CLV)
- **Missing:** only one snapshot per match (closing) exists in the clean CSV. `fetch_closing_odds.py` documents this explicitly. `ta_scrape` does multi-snapshot, so it can build movement — but only for matches it happened to poll early enough.
- **Impact:** you cannot compute the *opening-to-closing* drift — the standard sharpness/limit test and the best predictor of efficient-market alpha. You currently measure *level*, not *movement*.
- **Recommendations:** for the top-5 leagues, use `ta_scrape` to capture odds in a **window** (e.g. t-48h and t-1h) so closing-vs-opening becomes derivable. That's the highest-leverage new signal your current stack can already produce with no new vendor.

### Gap 4 — xG is effectively local-only (silent degradation)
- **Missing:** remote xG ingestion is a stub (`fetch_understat_xg` returns `[]`).
- **Impact:** the `xg_home/away` and `rolling_xg_diff` meta features silently fall back to *actual goals* when xG is absent. You may be feeding goal-differential into a feature labelled "xG" — a labelling/leakage hazard that quietly weakens the meta model's apparent edge.
- **Recommendations:** either (a) implement the real Understat `getLeagueData` JSON parse (the fixtures scraper already proves the endpoint is reachable), or (b) buy/use a proper xG feed (API-Football has xG per match; Sportmonks too). Do not trust the local cache to cover full history.

### Gap 5 — No real European club fixtures (UCL/UEL/UECL)
- **Missing:** authentic inter-club European fixtures.
- **Impact:** `synthesize_european.py` fabricates midweek flags; the `midweek_*` features are approximations. This sits *adjacent* to — not in front of — the primary alpha path.
- **Recommendations:** API-Football fixtures endpoint for `Champions League/Europa League/Conference League`; merge before next midweek window.

### Is the pipeline "100% complete for true alpha"?
No. The **1X2 and O/U 2.5 search spaces are data-complete** — and the honest conclusion is that both are already shown efficient. The remaining *unexplored* alpha is precisely where the data is thinnest:
- **Corner ROI** (Gap 1) and **BTTS ROI** (Gap 2) are the two concrete, quantitative bets sitting on missing odds.
- **Odds movement** (Gap 3) is the most promising *direction* you have not yet been able to test at all.

So "completion" is not about polishing the 1X2 path — that is done. It is about acquiring **corner odds, BTTS odds, and two-point odds snapshots**. Those three acquisitions are what turn the corner/BTTS engines from *validated predictors* into *validated, testable strategies*.

---

## Priority order to fund

1. **Corner O/U odds** (API-Football → replaces `MockCornerOddsClient`; or OddsPortal → `external_corner_odds.csv`). Unblocks T10 and activates the corner ROI gate.
2. **Two-point odds snapshots** via `ta_scrape` windowed capture. Unblocks CLV/opening-closing analysis on the 1X2 space.
3. **BTTS historical odds** (API-Football or extended ta capture). Unblocks T9.
4. **Real xG ingestion** (implement Understat parse or vendor feed). Removes the silent goals-fallback hazard in the meta feature set.
5. **Real European fixtures** (API-Football). Hardens midweek fatigue.

*All five plug into existing scaffolding — `fetch_corner_odds.py`, `ta_scrape.py`, `enrich_pipeline.py` — with no architectural change.*
