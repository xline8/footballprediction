# Step 3 — EDA: TH-ThaiLeague2

All figures from `eda_numbers.json` (computed by `eda_compute.py` from the
league CSV; the coverage and cards figures were independently recomputed
from the raw payloads). Regular phase only unless stated.

## Levels by season

| Season | Matches (regular) | Goals/match | OU2.5 over | Event yellows/match | Cards over 4.5 |
|---|---|---|---|---|---|
| 2024/2025 (dev) | 273 | 2.707 | 0.513 | 4.388 | 0.440 |
| 2025/2026 (virgin) | 306 | 2.761 | 0.529 | 4.229 | 0.444 |
| 2026/2027 (confirmatory, partial) | 90 | 2.856 | 0.500 | 4.778 | 0.556 |

There are **no SOT, corners or total-shots levels to report**: the stats
feed is null in every payload (Step 1). Goals 2.71–2.86/match is a normal
scoring level (parent Thai League 1: 2.56–3.07; J1 ≈2.6–2.8). Home
win/draw/away in the dev season: 0.480/0.264/0.256; home goal advantage
+0.44 (virgin +0.42) — a real home edge, close to the parent's +0.44.
Event yellows run 4.39 (dev) → 4.23 (virgin): a stable cards level.

## Trait reliabilities (random split-half within the dev season, r)

| Trait | For | Against |
|---|---|---|
| Goals | 0.353 | 0.522 |
| Event yellows | 0.287 | 0.099 |

These are single-season split-halves (~16 matches per team-half), so they
are attenuated relative to the programme's career-pooled figures — the
comparison is recorded, not hidden. Goals traits carry real signal
(against 0.522, for 0.353). Yellows-for is weak (0.287) and
**yellows-against is near noise (0.099)** in this league: team identity
explains little of who gets carded against them at this sample scale.
The cards Gate Zero is still the reference pattern (its naive ensemble
component does not depend on the against-trait), but expectations are set
accordingly and the gate decides. Referee strictness is **not measurable**:
referee text exists in 0 dev/virgin matches.

## Halves (dev season, regular, event-derived)

| Market | 1H share | Obs. var | Noise var | True var |
|---|---|---|---|---|
| Goals | 0.4249 | 0.1107 | 0.1159 | −0.0052 (≈0) |
| Event yellows | 0.3322 | 0.0598 | 0.0663 | −0.0064 (≈0) |

Per-match 1H share variance is ≈ pure noise for both markets with an
event-time source — the frozen-constant treatment is correct, as in J1
and the top-5 audit. Constants frozen in `config.yaml` / FEATURES:
goals **0.4249**, yellow cards **0.3322**. SOT / corners / total shots
have **no halves source at all** (no period splits, no events for those
markets) — and no target either; they are not buildable (Step 6).

## Movers (X2 descriptives, vs the parent Thai League 1 corpus, id 8984)

Relegated from T1 into T2 for the dev season (n = 3): Chonburi FC
(GF gap +0.397, GA gap −0.416 — a strong relegated side), Police Tero FC
(−0.135 / +0.147), Trat FC (−0.172 / +0.131). Mixed signs, small n: the
evidence supports the sanctioned SHRINK arm for goals (thin-history
shrinkage, no hard-coded offset), nothing stronger. For the record, the
virgin season's entrants (n = 6: 3 relegated from T1, 3 promoted from the
unobserved T3) are listed in `eda_numbers.json`; they are context for the
virgin read, not dev evidence.

## Cards artefact

See Step 1 for the full table. Headline: there is no stats feed (0 rows
in every season), so no artefact comparison exists; the event feed
publishes plain yellows in every era, unlike the parent league's dev era.
Frozen target: **event-unified yellows** in dev and virgin.

## Line choice (scored dev block only, 183 matches, 2024-11-09 onward)

Cards over-rates: 3.5 → 0.596, **4.5 → 0.437**, 5.5 → 0.257. Primary line
**4.5** (closest to 0.50). Goals primary line is the standard OU 2.5
(scored-dev over-rate 0.519).
