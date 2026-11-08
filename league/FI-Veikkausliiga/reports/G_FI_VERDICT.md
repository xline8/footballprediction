# Verdict — G-FI (FI-Veikkausliiga goals): **FAIL (dev gate, OU leg)**

Frozen gates: PREREG_G_FI.md (1889033, before any fitting).

## Dev (season-blocked walk-forward, scored 2022–2025, pooled n = 678)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.026105 | 0.218280 | 0.723094 |
| SHRINK | 1.026105 | 0.218280 | 0.723094 |
| X2 | 1.026981 | 0.218720 | 0.718562 |
| Climatology (baseline) | 1.070861 | 0.235166 | **0.692059** |

Gate Zero passes the 1X2 LL and RPS legs but **fails the OU2.5 leg**:
0.723094 > climatology 0.692059. The OU leg fails in every dev season
(2022: 0.767879 vs 0.711695; 2023: 0.717562 vs 0.693501; 2024: 0.724686 vs
0.690540; 2025: 0.684555 vs 0.673606) — it is not one bad season.
→ Candidate FAILS at the dev gate. **Virgin 2026 NOT read**
(`results_virgin.json` records `virgin_read: false`). Nothing ships.

Independent verification: the climatology baseline (all three metrics,
pooled and per season) was recomputed from the league CSV with a separate
implementation — exact to all printed digits (1.070861 / 0.235166 /
0.692059). The model's OU failure is therefore in the DC probabilities,
not in the baseline.

## The variant arms (moot, stated plainly)
- SHRINK is numerically identical to Gate Zero in every season. Under
  season-blocked fitting this is mechanical: at each season's fit every
  team has either 0 prior in-league matches (entrant; its DC ratings are
  the unseen defaults, and multiplying a rating by n/6 changes nothing
  that Gate Zero does not already do) or ≥27 (a full prior season). No
  team ever sits in the 1–5 match band the arm targets.
- X2 (in-corpus entrant offset, corrected construction — see the defect
  note in the engine commit): the offset first fires in 2025 (only 1–2
  completed entrant transitions exist before 2023/2024, below the frozen
  minimum of 3; by 2025 there are 4). In 2025 it made 1X2 LL *worse*
  (1.005540 vs Gate Zero 1.002186) while improving OU LL (0.667199 vs
  0.684555) — a wash that changes nothing: Gate Zero failed dev, so
  variants are moot and no rescue arm may be invented in this prereg.

Diagnosis (recorded, not acted on): a goals-only DC (no xG exists in this
feed in any season) beats climatology on 1X2/RPS here but its implied
totals are worse than a constant over-rate in all four dev seasons — the
lambdas are too tightly clustered for a league whose season goal level
swings 2.52–3.29 per match.
