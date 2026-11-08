# Verdict — G-HR (HR-HNL goals): **FAIL (dev gate, OU leg)**

Frozen gates: PREREG_G_HR.md (e9872c4, before any fitting).

## Dev (season-blocked walk-forward, scored 2022/2023–2024/2025, pooled n = 540)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.013865 | 0.205195 | 0.709474 |
| SHRINK | 1.013865 | 0.205195 | 0.709474 |
| X2 | 1.013865 | 0.205195 | 0.709474 |
| Climatology (baseline) | 1.080194 | 0.226715 | **0.697649** |

Gate Zero passes the 1X2 LL and RPS legs but **fails the OU2.5 leg**:
0.709474 > climatology 0.697649. The OU leg fails in two of three dev
seasons (2022/2023: 0.735773 vs 0.704861; 2023/2024: 0.721146 vs
0.692916; 2024/2025 passes: 0.671504 vs 0.695171).
→ Candidate FAILS at the dev gate. **Virgin 2025/2026 NOT read**
(`results_virgin.json` records `virgin_read: false`). Nothing ships.

Independent verification: the climatology OU2.5 baseline was recomputed
from the league CSV with a separate implementation (expanding
prior-seasons over-rate per dev season, pooled) — 0.697649, exact to
all printed digits. The failure is in the DC probabilities, not the
baseline. (Same failure mode as G-FI: a goals-only DC beats
climatology on 1X2/RPS but its implied totals are worse than a
constant over-rate.)

## The variant arms (moot, stated plainly)
- SHRINK is numerically identical to Gate Zero in every season — the
  FI mechanism: under season-blocked fitting every team at a season
  fit has either 0 prior in-league matches (entrant; ratings are the
  unseen defaults) or ≥36 (a full prior season). No team sits in the
  1–5 match band the arm targets.
- X2 is likewise identical in dev — by construction, not by bug: the
  offset requires ≥3 completed entrant transitions before the
  predicted season, and the dev seasons have at most 2 (Varaždin
  2022/2023, Rudeš 2023/2024 completed before 2024/2025). X2 would
  first have fired in the virgin season (3 transitions, Vukovar 91
  the entrant). Gate Zero failed dev, so this is moot and no rescue
  arm may be invented in this prereg.
