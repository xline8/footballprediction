# Step 1 — Data Understanding: TH-ThaiLeague2 (FotMob id 9498)

Source: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
filtered `league_id = 9498`: **681 matches**. All numbers below are computed
by `analysis/eda_compute.py` into `eda_numbers.json` / `inventory_summary.json`
from the CSV built by `data/build_data.py`, and the headline coverage figures
were independently recomputed from the raw payloads (they agree).

## Inventory

| Season | Matches | Regular | Play-offs | Teams | Dates | Stats feed | Period splits | Shotmap | Referee text |
|---|---|---|---|---|---|---|---|---|---|
| 2024/2025 | 279 | 273 | 6 | 18 | 2024-08-09 – 2025-05-24 | 0 | 0 | 0 | 0 |
| 2025/2026 | 312 | 306 | 6 | 18 | 2025-08-15 – 2026-05-23 | 0 | 0 | 0 | 0 |
| 2026/2027 | 90 | 90 | 0 | 18 | 2026-09-04 – 2026-11-08 | 0 | 0 | 0 | 72 |

Only **two complete seasons exist** in the warehouse. 2026/2027 is in
progress (90 matches, rounds 1–10) and is the reserved confirmatory window —
never read in this build. The last COMPLETE season, **2025/2026**, is the
virgin for every buildable candidate. Because only one pre-virgin season
exists, the dev protocol is a within-season walk-forward over 2024/2025
(see PREPROCESSING) — stated plainly, not disguised as a multi-season dev.

## Format and calendar

Split-year seasons, roughly August–May. **18 teams, double round-robin
regular phase (34 rounds), then a promotion play-off**: semi-finals
(2 legs × 2 ties) and a final (2 legs) = 6 play-off matches per complete
season, labelled in the feed's `matchRound` ("Promotion Play-offs -
Semi-finals" / "Promotion Play-offs - Final"); `content.hasPlayoff` is
False in the payloads despite the play-offs existing — the round label is
the reliable marker. **Phase rule frozen: play-off ties are excluded from
every fit and every scored window** (phase = "playoffs" in the CSV).

2024/2025 quirk: **Samut Prakan City withdrew after 1 regular match.** The
remaining 17 clubs played 32–33 regular matches (one fixture imbalance:
Trat FC 33) and the regular total is 273, not 272+34. No correction is
applied; the walk-forward simply uses the matches as played.

## Team identity

29 distinct FotMob team ids across the three seasons. Verified from the
raw payloads: **no team id carries more than one name and no name maps to
more than one id**. All team logic keys on team id.

## Field coverage and quirks — the stats feed does not exist

- **The stats feed is null in all 681 payloads.** `content.stats.Periods`
  contains the key `All` with value `None` in every match; there are no
  FirstHalf/SecondHalf periods, no `expected_goals`, and the shotmap is
  empty everywhere. There is therefore **no SOT, corners or total-shots
  target anywhere in this league's data**, and no possession, big-chance
  or opp-box-touches covariate.
- **The index `has_stats` flag is a false positive for this league.**
  The warehouse puller computes it as `"All" in periods`
  (`data_enrichment/pull_fotmob_world.py`), which tests key presence, not
  a non-null value. The brief's warehouse fact "stats 678 (99.6%)" comes
  from that flag and is **wrong for the payloads**: real stats coverage
  is 0/681. Recorded here as a warehouse defect; this build trusts the
  payloads, not the flag.
- **Events are near-complete**: goal/card/substitution events in 679/681
  matches (99.7%; the 2 missing are in 2024/2025). HT goals are derivable
  from goal events in every era.
- **Referee** (`matchFacts.infoBox.Referee`): absent in both complete
  seasons (0/591), present only in the in-progress 2026/2027 (72/90).
  No referee feature can be measured, let alone used.

## The cards artefact — checked, and the parent league's flip does NOT occur

Per the parent TH-ThaiLeague warning, the artefact direction was checked
per era before freezing the target. The situation here is different in
kind:

| Season | Stats-feed yellow rows | Event plain-Yellow count | Event-unified mean/match |
|---|---|---|---|
| 2024/2025 | 0 | 1,204 | 4.412 |
| 2025/2026 | 0 | 1,309 | 4.266 |
| 2026/2027 | 0 | 424 | 4.778 |

There is **no stats feed to compare against** (0 rows in every season), so
no stats-vs-events artefact can exist. The event feed, unlike the parent
league's dev era, **does publish plain "Yellow" card events in every era**
(1,204 / 1,309 / 424), at plausible levels (4.2–4.8 unified yellows/match).

**Frozen consequence (recorded in PREPROCESSING and the cards prereg):**
the cards target is the **event-unified yellow count** (direct Yellow +
YellowRed per team) in dev AND virgin — the only cards target that exists
in this league, consistent across both windows. No sensitivity against a
stats target is possible; none is promised.
