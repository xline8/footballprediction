# Verdict — G-RO (RO-LigaI goals)

**FAIL — dev gate (OU2.5 leg). Virgin NOT read.**

Dev (walk-forward, pooled n = 945; per-season n = 315):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero (model) | 1.0539 | 0.2140 | 0.7036 |
| SHRINK (model) | 1.0539 | 0.2140 | 0.7036 |
| Climatology | 1.0834 | 0.2234 | **0.6859** |

Gate arithmetic (PREREG_G_RO): 1X2 LL and RPS beat climatology,
but OU2.5 LL 0.7036 > 0.6859 → Gate Zero fails its dev gate →
variants moot, virgin not read (`engine/goals/results_virgin.json`
records `virgin_read: false`). Per-season OU LL also loses in
2022/2023 (0.7259 vs 0.6800) and 2023/2024 (0.7067 vs 0.7061).

SHRINK is numerically identical to Gate Zero in every season —
verified mechanically, not a bug: in the season-blocked fit scope
every team's prior in-league match count is either 0 (promoted;
shrink factor 0 = the unseen rule) or ≥39 (factor 1). The arm can
never bite under this protocol in this league.

Nothing ships.
