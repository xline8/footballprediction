# Step 6 — Model Design: IL-Leumit

Feasibility (Step 1, frozen): **one candidate only — G-IL (goals)**.
SOT / corners / cards / total shots are NOT BUILDABLE: their targets
do not exist anywhere in the corpus (stats 0/1,581, shotmap 0/1,581).
No halves presentation: no period splits, no constants (EDA F3) —
FT only if anything ships.

## Candidate G-IL — Leumit goals model (1X2 / OU / BTTS / DC)

(a) **Reference**: production Dixon-Coles in `model_v2.py` (class
`DC`, `probs`), hl = 270, exactly as pre-registered for G-J1 /
G-ENGCH — iterative multiplicative updates, 14 sweeps, damping 0.7,
+0.25 smoothing, fitted home advantage (init 0.28), score matrix
MAXG = 10 with production `tau`, rho per fit from grid
(0.0, −0.05, −0.10, −0.15) by weighted goals log-likelihood.

(b) **Identical**: estimation pattern, rho grid, time decay
(w = 0.5 ** ((cutoff − date).days / 270), frozen), season-blocked
expanding walk-forward, LL/RPS + calibration gate legs. Observation
is goals-only throughout (X1 fallback — no xG exists; not a design
change, the reference's documented behaviour).

(c) **Arms** (cap respected; both variants pre-registered from EDA,
neither invented after results):
1. **Gate Zero** — unmodified reference. Movers/unseen teams start
   at the league mean.
2. **Arm SHRINK** — Gate Zero + the sanctioned G-J2-lesson shrinkage
   for teams with < 6 prior in-league matches (FEATURES §2).
3. **Arm X2** — Gate Zero + mover tier priors (X1/X2 features, EDA
   F4 frozen magnitudes): down-movers from Ligat ha'Al get
   attack +log((mu+0.291)/mu), defence +log((mu−0.239)/mu);
   up-movers from tier 3 get attack +log(max(mu−0.080,0.10)/mu),
   defence +log((mu+0.109)/mu); prediction-time only, entry season
   only, membership by team ID vs the immediately preceding season.

(d) **Forbidden here**: halves anything (F3); phase covariate
(FEATURES R5); any stats-derived feature (none exist).

**Windows**: dev = seed 2021/2022, evaluation 2022/2023, 2023/2024,
2024/2025 (pooled n = 888). Virgin = 2025/2026 (n = 296, complete),
read ONCE, only for dev-passing arms. 2026/2027 (in progress) is the
reserved confirmatory window, untouched. Primary line OU 2.5
(complete-season over-rates 43.2–50.3%, the line nearest 0.5).
Baselines: climatology (pooled prior-season outcome rates + OU2.5
over-rate), per the J1 goals frame.

**Gate legs**: the verbatim J1/ENGCH goals legs (dev gate vs
climatology on pooled 1X2 LL + RPS + OU2.5 LL; virgin LL leg;
calibration leg |breach| ≤ 1pp clean, ≤ 1 SE provisional, else FAIL,
on home-win rate and OU2.5 over-rate; per-season sign check for
variant arms; both-pass → lower pooled virgin 1X2 LL ships; Gate
Zero dev failure ⇒ FAIL, virgin NOT read). Frozen in the prereg
before any fitting.

**NOT built if**: no arm passes — a FAIL is a complete outcome.
