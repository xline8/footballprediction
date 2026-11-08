# Pre-registration — G-BD (Bangladesh Football League goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/bd-football-league`.
Design authority: `analysis/MODEL_DESIGN.md`; features: `analysis/FEATURES.md`;
evidence: `analysis/EDA.md` and `analysis/eda_summary.json`. Reference
architecture: production Dixon–Coles pattern.

## Reference architecture

All arms use the production goals-only Dixon–Coles architecture, fitted home
advantage, score correction, and time decay w = 0.5 ** ((cutoff − match_date)
/ 270). The observation is official FT goals; xG is absent. Fit scope is all
finished BD-FootballLeague matches strictly before the first match date of the
target season. Unseen teams start at the league mean.

## Arms

1. **Gate Zero** — the unmodified reference architecture.
2. **SHRINK** — Gate Zero plus attack and defence ratings multiplied by n/6
   at prediction time for teams with fewer than six prior in-league matches;
   n=0 is identical to the unseen-team rule. EDA expects this arm to be
   identical to Gate Zero because zero teams are in the 1–5 band at every
   target-season start. The verdict must verify that expectation from the
   results file.

No entrant arm is registered: there is no sibling league or independent prior.
The entrant weakness is descriptive only: mean GF diff −0.49 and GA diff
+0.93 over five real entrants.

## Dev and virgin protocol

Seed = 2022/2023 (n=95, incomplete — rounds 4–22 only). Evaluation =
2023/2024–2025/2026 pooled (n=270). Virgin primary = in-progress 2026/2027
(n=29 through 2026-10-24, TRANSITIONAL). Confirmatory = the same season when
complete (season-end read, not a gate window).

Gate Zero and SHRINK use the same n/6 definition. The dev protocol compares
pooled 1X2 log loss and RPS to climatology and OU2.5 log loss to its base-rate
baseline. Virgin legs are: (i) 1X2 LL no worse than Gate Zero and climatology;
(ii) pooled home-win and OU2.5 calibration within 1.0 percentage point, with
SEs and provisional status within 1 SE; and (iii) for variants, LL no worse
than Gate Zero in at least half of dev seasons. Both-pass rule: if both pass,
ship the lower pooled virgin 1X2 LL; if only one passes, ship it; if neither
passes, verdict FAIL and nothing ships. Gate Zero is exempt from leg (iii), and
ties go to Gate Zero.

Frozen rule: if Gate Zero fails the dev gate, the variant arms are moot and
the virgin is NOT read.

No model, engine, results, or verdict is created by this preregistration.
