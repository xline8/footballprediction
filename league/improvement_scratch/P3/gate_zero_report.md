# P3 Gate Zero — Variance-Component Ratings

**Test as pre-registered in `league/AUDIT.md` §6 (P3), executed
2026-11-11. Proposal: replace the shipped models' fixed ridge/prior
constants with per-market variance components estimated on dev data
(team-trait variance, era-level variance, noise), shrinking thin
leagues toward regional/global means by estimated — not asserted —
amounts. Gate: pooled dev LL must improve on the shipped Gate Zero
in ≥5 of 6 sampled thin leagues, with no league worse by >0.002.
No sealed window is read anywhere in this test — dev data only.**

## Headline verdict: FAIL — P3 DIES

| # | League | Bucket | Market | n (dev) | Shipped GZ pooled dev LL | VC pooled dev LL | Δ (VC − shipped) | Improved? |
|---|---|---|---|---:|---:|---:|---:|:--:|
| 1 | MD-NationalDivision | scores-only | Goals (OU2.5) | 258 | 0.704029 | 0.699806 | −0.004224 | ✓ |
| 2 | SG-PremierLeague | scores-only | Goals (OU2.5) | 364 | 0.550695 | 0.544510 | −0.006184 | ✓ |
| 3 | J3 | one stats season | Goals (OU2.5) | 1,066 | 0.704048 | 0.690562 | −0.013487 | ✓ |
| 4 | MX-ExpansionMX | one stats season | Goals (OU2.5) | 967 | 0.693000 | 0.685248 | −0.007752 | ✓ |
| 5 | LV-Virsliga | mid | SOT (LL@9.5) | 133 | 0.682846 | 0.684736 | +0.001890 | ✗ |
| 6 | SA-FirstDivision | mid | SOT (LL@8.5) | 214 | 0.694447 | 0.694762 | +0.000315 | ✗ |

Improvements: **4 of 6** (required ≥5). Worst regression: +0.001890
(LV-Virsliga), inside the 0.002 tolerance — so the tolerance leg
passes, but the improvement-count leg fails. Under the
pre-registered kill rule, **P3 dies**. The pattern is clean and is
itself the finding: estimated variance components beat the asserted
shrinkage mechanism in **all four goals leagues** (every thin /
scores-only case, deltas −0.004 to −0.013), and lose narrowly in
**both SOT counting leagues**, where the v5 template's asserted
constants (ridge 100, NB r 79.94, priors 8/200) turn out to already
sit close to what these panels support.

Secondary metric (goals, 1X2 LL) agrees with the primary in all
four goals leagues: MD 0.953848 → 0.920596; SG 0.960650 → 0.956105;
J3 1.084815 → 1.078668; MX 1.042 → 1.039699. SOT full ladders
(shipped GZ → VC): LV 8.5: 0.676487 → 0.679180; 9.5 (primary):
0.682846 → 0.684736; 10.5: 0.635370 → 0.640151 — VC worse at every
LV line. SA 7.5: 0.658655 → 0.659740 (worse); 8.5 (primary):
0.694447 → 0.694762 (worse); 9.5: 0.610238 → 0.609394 (better).
The verdict uses each league's pre-registered primary line only,
as the Gate Zero text specifies ("pooled dev LL … on the shipped
Gate Zero" for that candidate's gated metric).

## Sample and qualification

Chosen from `league/audit_scratch/class_batch*.jsonl`
(`stats_seasons` field) intersected with leagues whose data and dev
artefacts are persisted on disk in `league/<L>/`:

| League | stats_seasons (JSONL) | Qualification |
|---|---|---|
| MD-NationalDivision | 0 | Scores-only: stats feed absent in every season (0/556 payloads, config-verified); only market built is Goals. Persisted: `data/md_matches.csv`, `engine/goals/results_dev.json`. Thinnest clean case in the programme (dev n=258). |
| SG-PremierLeague | 0 | Scores-only: stats feed absent in every season (0/555); only Goals built. Persisted CSVs + `results_dev.json`. Dev n=364. |
| J3 | 1 | One stats season: scores-only outside a 62-match 2025 stats window (config note; the stats window is the sealed season and is not used); only Goals built. Persisted CSVs + `engine/goals/results/dev_results.json`. Dev n=1,066. |
| MX-ExpansionMX | 1 | One stats season: stats era exists only in the in-progress 2026/2027 season (128 rows, untouched); dev is scores (Goals, plus Cards which is not used here). Dev rows via the league's own loader restricted to seed + scored blocks. Dev n=967. |
| LV-Virsliga | 2 | Mid: two stats seasons; all five markets built, counting dev panel is a single season (2025, scored n=133 for SOT). Persisted CSVs + SOT `results_dev.json` with GZ arm. SOT is the counting-stat Gate Zero family (v5 pattern). |
| SA-FirstDivision | 2 | Mid: two stats seasons (2024/2025 scores-only, 2025/2026 full stats); all five markets built, SOT dev n=214. Persisted CSVs + SOT `results_dev.json` with GZ arm. |

"Mid" is defined for this test as stats_seasons 2–3 (between the
one-season bucket and the rich 4+ group of AUDIT.md §1); both mid
picks sit at 2, the thin end of mid, which is where P3's shrinkage
question bites hardest. IT-SerieC (the third stats_seasons=1
league) was not used: its dev panel (n=3,346) is the largest in the
thin set and its data CSV is not persisted; MX-ExpansionMX was
preferred on both counts.

## Estimator

**Goals family** (`code/vc_goals.py`). Per dev fold, training
matches only, with the shipped 270-day half-life weights:

```
yh ~ Pois(lh),  log lh = mu + h + a[home] + d[away] + s[season]
ya ~ Pois(la),  log la = mu + a[away] + d[home] + s[season]
a ~ N(0, tau_a^2),  d ~ N(0, tau_d^2),  s ~ N(0, sigma_era^2)
```

Variance components by **Laplace-EM**: alternate a penalised
weighted-Poisson Newton fit with EM updates
`tau^2 <- mean(theta_hat^2 + posterior_var)` per random-effect
group, posterior variances from the inverse penalised Hessian.
The target season's era effect is predicted as 0 (an unobserved
era level is shrunk fully, as a random effect must be). Identical
to shipped and unchanged: fold structure, decay, the rho grid
{0, −0.05, −0.10, −0.15} selected on the training slice, MAXG=10
score matrix, scoring formulas. What is replaced is the shipped
shrinkage *mechanism* — 14 damped (×0.7) multiplicative sweeps with
+0.25 pseudo-count smoothing and no era component — which is the
goals engine's asserted-constant complex.

**SOT family** (`code/vc_sot.py`). One re-implementation of the
shipped v5-pattern engine with a mode switch; mode `gz` (asserted
constants) reproduces the shipped engine's dev LL exactly, then
mode `vc` swaps each constant for an estimate computed only from
data available at that point of the walk:

- ridge λ=100 → **Laplace-EM** per 7-day refit, separate
  `tau_att`/`tau_def`; λ = 1/tau² per group.
- shots-mean prior K=8 → **Gamma-Poisson method of moments**
  across teams per rating group: `tau_m² = Var(team decayed means)
  − mean(mu/w_t)`, `K = mu/tau_m²`.
- on-target ratio prior 200 → **Beta-Binomial method of moments**
  across teams: `m = rho(1−rho)/tau_rho² − 1` with
  `tau_rho² = Var(team ratios) − mean(rho(1−rho)/n_t)`.
- NB size r=79.94 → **method of moments** on match totals seen so
  far: `r = mu²/(var − mu)`.
- era variance: single-season dev panels cannot identify a
  season-level component; the month-level SD of log league totals
  is estimated and reported (LV 0.057, SA 0.069) but, as in the
  goals model, an unobserved period's effect is predicted as 0.

Unchanged from shipped: HL=365 decay, 7-day refits, date-grouped
predict-then-update walk, warmups (LV 47 matches before 2025-05-01;
SA first 90), the 0.5 regression / 0.5 ratings blend, the 0.5
model / 0.5 naive probability blend, lines, scoring.

Numerical guards (clips on estimated quantities, e.g. tau² floors,
λ ∈ [1, 10⁴], m ∈ [5, 5000], r ∈ [5, 500]) are stated in the code;
where an estimate is inestimable (no data yet — warmup only), the
placeholder provably cannot affect a scored prediction (with
w = 0 the shrunk value equals the league mean for any K; with no
shots the ratio equals the league ratio for any prior).

## Constants replaced — asserted vs estimated

**Goals** (per fold; full series in `details/*.json`). Asserted:
+0.25 pseudo-count, 14 sweeps × 0.7 damping, home init 0.28, no era
component. Estimated (range across folds):

| League | tau_a (attack SD) | tau_d (defence SD) | sigma_era (season-level SD) |
|---|---|---|---|
| MD | 0.254–0.388 | 0.489–0.612 | 0.000–0.105 |
| SG | 0.132–0.280 | 0.246–0.283 | 0.000–0.070 |
| J3 | 0.108–0.195 | 0.073–0.134 | 0.000–0.034 |
| MX | 0.089–0.144 | 0.082–0.227 | 0.000–0.082 |

(sigma_era = 0 in each first fold by construction: one training
season cannot identify an era variance.)

**SOT.** Asserted: ridge λ=100 (both groups), K=8, ratio prior 200,
NB r=79.94. Estimated:

| League | ridge λ_att (final; range over refits) | ridge λ_def | K (final, 4 groups) | ratio prior (final H/A) | NB r (scored mean) |
|---|---|---|---|---|---|
| LV | 13.0 (10.4–112.2) | 22.0 (9.7–86.3) | 1.1–2.3 | 5000 (cap) / 244 | 41.8 |
| SA | 16.8 (16.8–96.6) | 39.2 (24.5–97.9) | 2.0–3.9 | 708 / 318 | 168.5 |

Reading: the data consistently want *less* shrinkage than the
templates assert for SOT ratings (λ ≈ 13–39 vs 100; K ≈ 1–4 vs 8)
but *more* pooling of the on-target ratio (244–5000 vs 200), and
league-specific dispersion (r 42 in LV, 169 in SA, vs the copied
79.94). In the goals engines the estimated components instead
supply shrinkage the sweep mechanism never had. Net dev-LL effect
is positive for goals everywhere and slightly negative for SOT in
both mid leagues — hence the verdict.

## Validation that the comparison is apples-to-apples

Before any VC number was taken, the shipped Gate Zero was
replicated through this test's own adapters (each league's own DC
class / SOT engine, shipped fold protocols):

| League | Shipped artefact LL | Replication LL | Abs diff |
|---|---:|---:|---:|
| MD | 0.704029 | 0.704029 | 0.000000 |
| SG | 0.550695 | 0.550695 | 0.000000 |
| J3 | 0.704048 | 0.704048 | 0.000000 |
| MX | 0.693000 | 0.693003 | 0.000003 |
| LV | 0.682846 | 0.682846 | 0.000000 |
| SA | 0.694447 | 0.694447 | 0.000000 |

(MX's artefact stores only 4 decimals — see the note in its
`results_dev.json` — so 3e-6 is rounding, not drift.) The SOT
re-implementation in `gz` mode also reproduces the shipped engine
run through the shipped walk to the same precision. VC deltas are
computed against the artefact values.

## Sealed-window hygiene

Dev data only, enforced at load: MD/SG/J3 loaders filter to the
dev season sets before constructing any row used downstream; the
MX loader is the league's own `common_mxe.load` restricted to the
seed + 8 scored blocks (virgin block never requested); LV loads
season "2025" capped at 2025-11-09; SA loads season "2025/2026"
only. No sealed row enters any fit, aggregate, variance estimate
or score in this test.

## Artefacts

- `results.csv` — the headline table, machine-readable.
- `results.json` — summary + rows + full per-league details.
- `details/<league>.json` — per-league replication, per-fold VC
  metrics and estimated components.
- `code/vc_goals.py`, `code/vc_sot.py`, `code/run_p3.py` —
  reproducible implementation (see `code/README.md`).

**Bottom line for the programme:** P3's Gate Zero fails on its own
pre-registered terms (4/6 < 5/6) and the proposal dies. The split
result — goals 4/4 improved, SOT 0/2 — is recorded as evidence,
not as a licence to re-scope P3 post hoc: any future
goals-only variance-component candidate would be a new proposal
needing its own pre-registration.
