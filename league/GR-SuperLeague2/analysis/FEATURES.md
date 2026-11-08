# Phase 3.5 — Feature Engineering: GR-SuperLeague2 X1–X9

The global causality contract is unchanged: a target match may use
only strictly earlier matches; windows are trailing; ratios are
ratios of sums; missing windows make an arm inactive. Ratings, home
advantage, Dixon–Coles parameters, and the halves constant are
architecture or presentation components, not covariates. All
reliabilities are the GR2 measurements in EDA.md. The defining fact
of this league is that **no stats feed exists in any payload**, so
every stats-fed feature is dropped on data absence before any
reliability question arises.

| ID | Feature | GR2 verdict | Evidence and use |
|---|---|---|---|
| X1 | Goals plus stats-feed xG blend | ADOPTED as goals-only | Goals exist for all 1,935 rows. Stats xG exists in **zero**
payloads, so the production blend's goals-only fallback fires on
every match in dev and in the virgin fit; Gate Zero is the
goals-only DC, with the production blend pattern intact. No xG
reliability can be measured here. |
| X2 | Mover tier offset | MEASURED, NOT CONSUMED | 33 newcomers over 5 transitions, split by origin (EDA F4):
SL1-relegated (n=8; dev n=5) GF gap +0.314, GA gap −0.288;
Gamma/other (n=25) GF gap −0.198, GA gap +0.108. Not consumed:
(1) 5 dev movers cannot carry an estimated offset parameter;
(2) a single pooled newcomer offset would be wrong-signed for
both origin groups; (3) Gamma Ethniki is not in the warehouse, so
promoted clubs have no prior-tier data to anchor an offset.
SHRINK is the goals thin-data arm (G-J2 lesson). X2 stays a
documented future candidate once more transitions accumulate. |
| X3 | Set-play xG share/rate | DROPPED (no data) | No stats xG in any payload; the feature cannot be computed,
let alone reliability-tested. |
| X4 | Shotmap xG per shot | DROPPED (no data) | No shotmap in any payload. |
| X5 | Trailing target means | DROPPED (no data) | No SOT / corners / yellows / shots target exists in any
payload, so there is no trailing target history to average. The
goals trait itself lives inside the DC ratings (architecture,
§2), not as an X5 covariate. Event-card counts are descriptive
only (337 Card events in 1,935 matches, no stats feed to unify
against). |
| X6 | Attacking xGOT per shot | DROPPED (no data) | No shotmap, no xGOT field, in any payload. |
| X7 | Opp-box touches | DROPPED (no data) | No stats feed in any payload. |
| X8 | Referee yellow rate | DROPPED (no data) | No referee is named in any payload (`infoBox.Referee`
absent throughout); no yellows target exists either. |
| X9 | Possession and big chances for corners | DROPPED (no data) | No stats feed; no corners candidate. |

Rejected inherited items remain rejected: team half shares are a
presentation constant (goals true variance −0.0025, i.e. zero);
finishing and standalone conversion are outcome-contaminated and
have no xG to be computed from; on-target rate cannot be computed;
defensive xGOT is not eligible; lineup, formation, coach,
standings, h2h, attendance, game-state, momentum, and red-card
features have no admissible pre-match evidence here. The B-team
flag (`is_b_home` / `is_b_away`) is a descriptive column, **not**
a feature: no arm conditions on it (frozen B-team rule — B teams
are ordinary rows).

## Consumption map

- G-GR2: X1 (goals-only blend fallback); SHRINK is the thin-data
  arm; X2 measured but not consumed; X3–X9 not run (no data).
- S-GR2 / C-GR2 / K-GR2 / T-GR2: **not candidates** — no target
  exists in any payload (DATA_UNDERSTANDING §6).
