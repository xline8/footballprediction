# Step 5 — Features: RS-SuperLiga (J1 template X1–X9)

Causality contract as in the J1 template: features for match M use only matches strictly before M;
ratios are ratios of sums; NaN ⇒ the arm needing the feature is inactive for that match, never
silently filled. Every verdict below is measured on the DEV era (2021/2022–2024/2025) or is a
data-absence fact; no virgin row chose any feature. Sources: `eda_summary.json: traits_dev`,
`eda_summary.json: levels`, `inventory_summary.json`.

| Feature | Verdict | Reason (measured in THIS league) |
|---|---|---|
| X1 blend pair (goals+xG) | **PARTIAL — goals-only** | No `expected_goals*` key in any season's stats keys and no shotmap in 1,488/1,488 in-scope matches (`inventory_summary.json: has_expected_goals_key` = false, `shotmap_matches` = 0 every season). The DC reference runs goals-only, its documented fallback — same ruling as FI. |
| X2 mover tier offset | **ADOPTED (goals arm)** | 7 genuine dev entrant transitions measured in-corpus (EDA.md F4): GF −0.326, GA +0.242 vs league team mean — promoted-team pattern, stronger than FI's, same sign as J1. RS is tier 1: entrants are promoted clubs, identified by absence from the previous season's regular-phase teams (the plain-absence rule is contaminated here by cross-tier qualification opponents — see EDA.md F4; no tier-2 corpus is built in-system; the offset itself is estimated inside the fit from completed transitions only). |
| X3 set-play xG share | **DROPPED** | No xG at all in the feed (data absent); no set-play split key exists either. |
| X4 xG per shot / on-target ratio inputs | **DROPPED** | No shotmap in any season (0/1,488); SOT itself exists only in the virgin season, so no dev on-target ratio can be formed. S-RS therefore has no X4 arm — and no S-RS at all (MODEL_DESIGN.md). |
| X5 trailing target-rate means | **ADOPTED — goals only** | Goals target exists all seasons and its trait is reliable (EDA.md F2: split-half r = 0.906; season-to-season 0.850–0.888). For SOT/corners/yellows/total-shots the target does not exist in dev, so no trailing mean exists for them. |
| X6 xGOT per shot / shot volume | **DROPPED** | No shotmap / no xGOT (data absent); `total_shots` exists only in the virgin season. No dev shot-volume feature can be formed. |
| X7 opp-box touches / territory for corners | **DROPPED** | `touches_opp_box` exists ONLY in the virgin season (36-key rich feed, 296 matches). Its trait cannot be measured on dev (null, `eda_summary.json: traits_dev.touches_for`) and a corners arm needing trailing touches across the dev walk-forward would be NaN for every dev season. Dropped on window grounds, not trait grounds — the same ruling as FI's X7, one era more severe (FI had one dev rich season; RS has none). `BallPossesion` is in the same position (virgin-only), so the FI fallback of a possession-only corners covariate is also unavailable here. |
| X8 referee yellow rate | **DROPPED** | Referee name empty in 1,192/1,192 dev payloads; named in 197/296 virgin matches across 23 referees (`inventory_summary.json`). The trait cannot be measured on the dev era, and no referee data exists for any dev match. K-RS is not built in any case (see X5/cards below). |
| X9 keeper saves / territorial covariates | **DROPPED** | `keeper_saves`, `big_chance`, `fouls`, `BallPossesion` all exist only in the virgin season; traits null on dev (`eda_summary.json: traits_dev`). No reference territorial covariate survives into a dev-evaluable arm. |

## Cards (X5/X8 interaction, recorded explicitly)

The J1 template's cards features assume a usable yellows target. RS has none: the stats-feed
yellows exist only in the virgin (4.230/match) and the event-derived yellows in dev are
YellowRed-only (0.041–0.120/match, no plain Yellow Card events in 1,192 dev matches;
`eda_summary.json: levels[].yellows_event`, `inventory_summary.json: card_detail`). The
event-yellows split-half trait is r = 0.060 on that broken feed (EDA.md F2) — not a team trait.
No cards feature is adopted, and no cards target is frozen.

## Halves constants (presentation only; to be frozen in Phase 6 config, not here)

Measured shares, dev era (`eda_summary.json`): goals **0.4606** from event times over
league-member dev matches (n = 1,087, excluding the awarded match 4271663 and the 8 cross-tier
qualification ties). Yellows 1H 0.1238 is measured but NOT a usable constant (13 1H cards on a
broken feed). SOT / corners / total shots / yellows split shares are **null** — no dev splits
exist, and the virgin splits are not borrowed. There is therefore exactly one frozen halves
constant for this league (goals), to be set in Phase 6 config.
