# Pre-registration — G-SCO-L1 (Scotland League One goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/sco-league-one`.
Design authority: `league/SCO-LeagueOne/analysis/MODEL_DESIGN.md`
(G-SCO-L1); features per `analysis/FEATURES.md` (X2 mover ADOPTED;
X1/X3 DROPPED — no xG exists in this league); evidence per
`analysis/EDA.md`. Reference: production Dixon-Coles in
`model_v2.py` (class `DC`, hl = 270); sibling analogues:
`league/SCO-Championship/prereg/PREREG_G_SCOCH.md` (goals-only)
and `league/IE-FirstDivision/prereg/PREREG_G_IEFD.md`.
Phase rule (frozen): every row is phase `regular` — the feed
contains NO play-off rows (each complete season is exactly the 180
regular-season matches; play-off ties fall after the feed's last
dates). Cross-tier play-off ties are therefore absent by
construction, not modelled. No phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only (no xG in any of the 969 payloads; the X1
  blend cannot exist here).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all League One matches dated
  strictly before the first match date of S (expanding,
  season-blocked). Teams keyed on team ids (id 4130 carries two
  feed names; names are never keys).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6`, n = prior in-league match count.
   Nothing else changes.
3. **Arm X2** — Gate Zero plus direction-specific mover priors
   (feature X2, EDA). A club is a *mover* for target season S when
   its team id plays League One in S, did not play it in S−1, and
   played S−1 in a neighbour tier — direction `down` if in the
   Championship (FotMob id 123), `up_other` if in neither League
   One nor the Championship in S−1 (promoted from below; League
   Two is NOT in the warehouse, so this direction's tier is
   unverified and it is NEVER labelled "from League Two") —
   classified in the frozen table `analysis/movers.json` (built by
   `analysis/eda_compute.py` from warehouse index membership by
   team id). For a mover, at prediction time in season S only:
   - attack: `a += log(max(mu + ΔGF_dir, 0.10) / mu)`
   - defence: `d += log(max(mu + ΔGA_dir, 0.10) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and ΔGF_dir / ΔGA_dir are **estimated
   inside the fit**: pooled over all entrant first seasons
   strictly before S present in the training window (entrant GF
   per team-match minus the same seasons' league GF per
   team-match; likewise GA). If a direction has fewer than 2 clubs
   of such history, its offset is 0 (inactive). By construction
   there are no prior transitions before 2022/2023, so X2 ≡ Gate
   Zero for the 2022/2023 dev season; the arm first bites in
   2023/2024 and in the virgin (EDA pooled values: down ΔGF
   +0.1762 / ΔGA −0.2881 on 7 club-seasons, up_other −0.1361 /
   +0.2007 on 8 club-seasons — the virgin fit must reproduce
   these).
   - **Correctness note (frozen, do not repeat the G-SCOCH
     defect):** the offsets apply ONLY to the target season S's
     own entrants. The G-SCOCH implementation built the mover set
     from all entrant seasons strictly before S and applied the
     offsets to those past entrants; that is NOT this arm. The
     harness must select movers from `movers.json` for season S
     only, and estimate magnitudes from entrant seasons strictly
     before S.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023,
  2023/2024, 2024/2025 (pooled n = 540) under the season-blocked
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS,
  mean OU2.5 LL. Baselines: climatology — for target season S,
  pooled outcome rates + OU2.5 over-rate of all seasons strictly
  before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 180, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean actual −
  predicted for home-win rate and OU2.5 over-rate, SE = sd(y_i −
  p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat
climatology, and OU2.5 LL must beat the base-rate baseline, else
the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤
Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual −
predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5
over-rate, SEs reported; a breach within 1 SE of the boundary is
recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign
check on dev (arm LL ≤ Gate Zero LL in at least half the dev
seasons) for the both-pass rule. Both-pass rule: if Gate Zero and
a variant both pass all legs, the lower pooled virgin 1X2 LL
ships; if only one passes, it ships; if none passes, G-SCO-L1
verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `league/SCO-LeagueOne/engine/goals/`; dev results
`results_dev.json` (+ per-match `results_dev.csv`, force-added:
one row per scored match with per-match probabilities — NOT a
per-season summary table); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/SCO-LeagueOne/predictions/g_sco_l1_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant
0.4295). Verdict: `league/SCO-LeagueOne/reports/G_SCO_L1_VERDICT.md`.
Production code untouched. No push. No merge.
