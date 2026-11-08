# IS-1Deild goals engine — Phase B1

This is the development-only G-IS1 engine. Run from this directory with:

```sh
python3 run_g_is1.py dev
```

The harness reads only `league/IS-1Deild/data/is1_matches.csv`, filters to
2021–2025, and asserts that no 2026 row is loaded. It uses season-blocked
expanding fits for target seasons 2022–2025: one fit on dates strictly before
the first target-season match, then scores the complete target season. Playoffs
remain included, with phase retained in the per-match output.

`dc.py` is the sibling Dixon–Coles reference copied verbatim except for its
module docstring naming IS-1Deild: 14 sweeps, damping 0.7, +0.25 smoothing,
h=0.28, rho grid `(0.0, -0.05, -0.10, -0.15)`, 270-day decay, MAXG=10, and
goals-only observations. IS-1Deild passes no xG columns, so the goals-only
fallback is always used.

## Arms and deliberate divergences

Gate Zero uses the fitted ratings unchanged. SHRINK multiplies each fitted
attack and defence rating by `min(1, training_window_match_count / 6)`; the
count is from all matches in the fit training window. This is deliberately not
the sibling engine’s target-season-history variant. With these blocked fits,
the diagnostic in `results_dev.json` shows zero SHRINK lambda differences from
Gate Zero in every dev season: teams have at least six training matches, or
zero fitted rating for a new team, so the shrink factor changes nothing.

X2 is also deliberately different from the sibling. It is direction-specific
and origin-specific. For each target season S, completed entrant transitions
have entry season E < S, are keyed by the committed team-ID membership file,
and use the entrant’s 1. Deild GF/match and GA/match in E minus that season’s
league mean goals per team per match. The deviations are pooled separately by
origin. An origin with fewer than three completed transitions has zero offsets.
Using fitted decay-weighted `mu`, each side is converted as:

```text
att_o = clamp(log(max(mu + gf_dev_o, 0.10) / mu), log(0.8), log(1.25))
con_o = clamp(log(max(mu + ga_dev_o, 0.10) / mu), log(0.8), log(1.25))
```

In the entrant’s entry season only, its own scoring lambda is multiplied by
`exp(att_o)` and the opponent’s scoring lambda against it by `exp(con_o)`. The
membership generator reads only warehouse index/payload team IDs, guards
missing `general.homeTeam`/away-team blocks, and cross-checks the resulting 21
entrants against frozen F4 exactly.

## Outputs

`results_dev.csv` contains exactly one row per scored match per arm (543 × 3 =
1,629), with lambdas, 1X2, OU 1.5/2.5/3.5 and BTTS probabilities. Summary
metrics, expanding climatology, the frozen 0.6814 OU2.5 base-rate baseline,
sign checks, X2 offsets and lambda diagnostics are in `results_dev.json`.

## Mechanical dev-gate reading

The frozen dev gate requires pooled 1X2 LL and RPS better than the expanding
climatology and OU2.5 LL better than the 0.6814 base-rate baseline. (The
per-season sign check is virgin leg (iii) for the both-pass rule, not part of
the dev gate; it is reported separately in `results_dev.json` under the
prereg's at-least-half rule — X2 passes it 2/4 on ties in 2022–2023, SHRINK
4/4.) On the generated dev output, Gate Zero, SHRINK and X2 all FAIL the dev
gate mechanically: each misses the pooled 1X2/RPS climatology legs and the
OU2.5 base-rate leg. Gate Zero's dev failure makes the variants moot and the
virgin is not read. No virgin computation or 2026 scoring is part of this phase.
