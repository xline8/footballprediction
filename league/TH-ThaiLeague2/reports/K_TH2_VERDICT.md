# Verdict — K-TH2 (cards, event-unified yellows): **FAIL**

Prereg: `prereg/PREREG_K_TH2.md` (frozen and committed before fitting).
Primary line 4.5; target = event-unified yellows (frozen target-source
decision in the prereg: the stats feed is null in all 681 payloads, so
no stats target exists; the event feed publishes plain yellows in every
era — the parent league's era-flipped artefact does not occur here).
All numbers recomputed by the coordinator from the per-match dev CSV
against the league CSV (0 target mismatches).

## Dev (within-season walk-forward over 2024/2025 regular; warm-up 90, scored n = 182)

| Arm | Pooled LL@4.5 |
|---|---|
| Gate Zero | 0.6794 |
| League base rate | 0.6910 |
| Naive trailing-10 | 0.6701 |

Dev calibration (actual − predicted over-4.5 rate): −4.29 pp
(actual 0.4396, mean predicted 0.4824) — reported for the record; the
dev gate has no calibration leg.

## Gate arithmetic

Dev gate requires pooled LL@4.5 to beat BOTH baselines. Gate Zero beats
the league base rate (0.6794 < 0.6910) but **loses to naive trailing-10
(0.6794 > 0.6701)**. Gate Zero fails its dev gate; the **virgin was NOT
read** (the harness refuses the virgin run and no virgin artifact
exists).

Context: the EDA warned this was likely — event-yellow trait
reliability in this league is weak (for r = 0.287, against r = 0.099 at
single-season split-half scale), so the rating state adds little over
the trailing-10 tracker it is ensembled against. The frozen NB-size
estimator also hit its cap (r = 500 for all three methods on the
warm-up block, i.e. the counts are effectively Poisson at this scale);
that is the reference estimator behaving as specified, recorded here,
not a defect. The parent league's K-TH failed the same leg against the
same baseline.

**K-TH2 FAILS. Nothing ships.** 2025/2026 remains unread for this
candidate; 2026/2027 remains the untouched confirmatory window.
