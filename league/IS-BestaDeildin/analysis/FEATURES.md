# Features — IS-BestaDeildin

The X1–X9 decisions are frozen before any engine work.

| Feature | Verdict | Evidence and operational rule |
|---|---|---|
| X1 | **ADOPTED as goals-only fallback** | No xG key exists; goals are the complete observation pair. |
| X2 | **ADOPTED (in-corpus entrant)** | Team ids identify entrants by absence in the preceding season; use only causal prior seasons. |
| X3 | **DROPPED** | No xG splits exist. |
| X4 | **DROPPED** | No shotmap/xG exists. |
| X5 | **ADOPTED** | Team ratings/trailing target means remain measurable in the stats era. |
| X6 | **DROPPED** | No shotmap exists. |
| X7 | **ADOPTED with 2024+ restriction (artefact)** | 2023 `touches_opp_box` is a different scale (mean 10.4 versus 51.1 in 2024 and 52.3 in 2025); trailing windows may use only 2024+ box values. |
| X8 | **ADOPTED for cards** | Referee split-half r is .394 in this deterministic recomputation; the coordinator’s seed-fixed value is r≈.71. Coverage is 337/486 dev stats matches and 65/162 virgin matches; virgin coverage is a risk note. |
| X9 | **ADOPTED** | Possession plus `big_chance`; per-season coverage is recorded in `inventory_summary.json`. |

Team logic is keyed on FotMob id, never on published name. There are 17 ids
and nine ids with two diacritic spellings.
