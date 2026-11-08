# Verdict — G-IEFD (Ireland First Division goals) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_G_IEFD.md`. Goals-only Dixon-Coles (no xG exists
anywhere in this corpus, so the blend is goals-only throughout).
Arms: Gate Zero + X2 (relegated-mover prior offset, frozen +0.23/−0.27).
Regular-season matches only; playoffs excluded from fitting and
evaluation. Dev = season-blocked walk-forward, 2021 as seed, eval
2022–2025 (pooled n = 683).

## Dev (season-blocked walk-forward, eval 2022–2025, n = 683)

| | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | **1.0587** | **0.2235** | 0.7251 |
| X2 | 1.0623 | 0.2236 | 0.7307 |
| Climatology | 1.0829 | 0.2331 | **0.6908** |

Per-season detail (model vs climatology, OU2.5 LL):

| Season | Gate Zero LL / RPS / OU | Climatology LL / RPS / OU | X2 LL / RPS / OU |
|---|---|---|---|
| 2022 (n=144) | 1.0179 / 0.2118 / 0.7457 | 1.0859 / 0.2377 / 0.6777 | 0.9939 / 0.2037 / 0.7514 |
| 2023 (n=180) | 1.0873 / 0.2360 / 0.7237 | 1.0764 / 0.2354 / 0.6810 | 1.1087 / 0.2425 / 0.7261 |
| 2024 (n=180) | 1.0726 / 0.2173 / 0.7446 | 1.1014 / 0.2269 / 0.7122 | 1.1059 / 0.2249 / 0.7594 |
| 2025 (n=179) | 1.0487 / 0.2267 / 0.6904 | 1.0684 / 0.2333 / 0.6897 | 1.0269 / 0.2192 / 0.6896 |

Gate Zero passes the 1X2 LL leg (1.0587 < 1.0829) and the RPS leg
(0.2235 < 0.2331), but **fails the OU2.5 LL leg: 0.7251 > climatology
0.6908** — and it fails that leg in all four dev seasons, not on a
pooled fluke (margins: +0.068, +0.043, +0.032, +0.001). The DC's
totals distribution is systematically worse than the flat prior-season
over-rate at pricing Over/Under 2.5 in this league, whose season goal
levels swing 2.63–3.06 and whose 2022 season is an away-edge outlier.
X2 fails the same leg (0.7307 pooled; worse than Gate Zero in 3 of 4
seasons on OU LL) and is also worse than Gate Zero on pooled 1X2 LL
(1.0623 vs 1.0587). The X2 per-season sign check (leg iii) is moot:
X2 beats Gate Zero on 1X2 LL in 2 of 4 seasons (2022, 2025), but the
gate fails at Gate Zero.

**Dev gate: FAIL for both arms. Per the prereg, the variant is moot
when Gate Zero fails dev, and the virgin is NOT read.**

## Virgin (2026, n = 180 regular) — NOT READ

`engine/goals/results_virgin.json` contains only the marker
`{"virgin_read": false, "reason": "gate zero failed dev gate"}`,
written by the `virgin-metrics` guard after re-running dev (identical
hashes). No 2026 row was fitted, scored, or predicted; no predictions
CSV and no fitted-params file exist. The 2026 season remains a virgin
window for any future design.

## Independent verification (by the builder, not the implementor)

- Climatology rows recomputed from the CSVs by an independent script:
  per-season LL/RPS/OU match `results_dev.json` to 6dp, and pooled
  rows match the n-weighted means of the per-season rows exactly.
- Model side replayed against the production DC (`model_v2.py`, class
  `DC`) on the 2022 fit (train = 2021 regular only): fitted rho
  (−0.10) and home advantage (0.1434) identical; per-match
  probabilities identical (max diff 0.0 over 144 matches); 2022
  scores identical to the filed row (1.017911 / 0.211801 / 0.745717).
- Codex's first run crashed mid-task (Rust stderr panic after writing
  dc.py + arms.py only); the second run completed harness/runner/README
  + dev. Both files were reviewed line by line; dc.py is verbatim the
  sibling's (one docstring word differs); arms.py's X2 offsets apply
  to the mover's own attack and defence exactly as the prereg freezes.
- One builder-side defect found and fixed during Phase A: the
  `has_extra_time` flag first used key presence on `status.halfs`,
  which carries empty extra-half keys in every match — it flagged
  ~all of 2021. Fixed to require a non-empty timestamp (3 matches:
  the 2023/2024/2025 playoff finals). No analysis number depended on
  it (playoffs are out of scope).

## What ships

**Nothing.** G-IEFD verdict is FAIL. No predictions, no fitted
parameters, no runner entry.

## League completion state

- G-IEFD: FAIL (dev gate, OU2.5 leg). Virgin deliberately unread.
- S-IEFD / C-IEFD / K-IEFD / T-IEFD: NOT buildable (no target exists
  for any of them in any season — see `prereg/PREREG_NOT_BUILDABLE.md`).
- The league is complete: its one buildable candidate has passed
  through its gate, and the four not-buildable markets are on record.
  0 of 5 candidates ship; 1 failed at the dev gate, 4 not buildable.
