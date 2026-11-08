# Verdict — G-ESPF (ES-PrimeraFederacion goals) — **FAIL** (dev gate; virgin deliberately NOT read)

Prereg: `prereg/PREREG_G_ESPF.md` (commit 1750d713, before any
fitting). Goals-only DC by design (no xG/stats/shotmap anywhere in
the corpus). Dev n=2,322, virgin 2025/2026 n=772 **not read**.

## Dev (pooled; climatology 1X2 LL 1.0784, RPS 0.2197, OU2.5 base-rate LL 0.6766)

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev outcome |
|---|---|---|---|---|
| Gate Zero | 1.0834 | 0.2209 | **0.6856** | loses to climatology on **all three legs** |
| SHRINK | 1.0834 | 0.2209 | **0.6856** | bit-identical to Gate Zero (see below) |
| X2 | 1.0835 | 0.2207 | **0.6845** | loses to climatology on **all three legs** |

Per-season detail (model vs climatology):

| Season | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|
| 2022/2023 | Gate Zero | 1.0713 / 1.0819 | 0.2171 / 0.2194 | 0.6811 / 0.6726 |
| 2022/2023 | X2 | 1.0659 / 1.0819 | 0.2154 / 0.2194 | 0.6798 / 0.6726 |
| 2023/2024 | Gate Zero | 1.0616 / 1.0740 | 0.2180 / 0.2225 | 0.6756 / 0.6749 |
| 2023/2024 | X2 | 1.0551 / 1.0740 | 0.2159 / 0.2225 | 0.6739 / 0.6749 |
| 2024/2025 | Gate Zero | 1.1172 / 1.0794 | 0.2275 / 0.2173 | 0.7000 / 0.6824 |
| 2024/2025 | X2 | 1.1294 / 1.0794 | 0.2307 / 0.2173 | 0.6997 / 0.6824 |

Gate arithmetic: the dev gate requires all three legs pooled. Every
arm fails all three pooled legs, so the verdict is FAIL without
needing the variants-moot rule (which would end it anyway: Gate
Zero failed its own dev gate). **Virgin NOT read; nothing ships.**
The runner's per-arm gating enforced this mechanically
(`results_virgin.json`: `{"virgin_read": false, "reason": "no arm
passed the dev gate"}`).

Two construction facts, recorded plainly:

1. **SHRINK is bit-identical to Gate Zero** (max abs diff 0.0 on
   all three metrics, all seasons + pooled) — exactly as the prereg
   pre-recorded: prior in-league counts at a season start are 0 or
   ≥38 in this league, so the n/6 factor only ever takes the values
   0 or 1. It is not evidence about shrinkage at match-level
   granularity.
2. **X2 genuinely ran** (unlike the G-ES first run, where a league-id
   tuple bug silently emptied the mover set): X2 differs from Gate
   Zero in every season (ΔLL −0.0054 / −0.0065 / +0.0122). It helps
   on 1X2/RPS in 2022/2023 and 2023/2024 — and in 2023/2024 it even
   passes the OU leg (0.6739 vs climatology 0.6749, marginally) —
   but it fails the OU leg in 2022/2023 and 2024/2025, and hurts on
   1X2/RPS in 2024/2025 (OU essentially flat there, −0.0003 vs Gate
   Zero). Pooled it fails all three legs, on its own numbers. The
   id-keyed mover lists were verified to equal the EDA name-keyed
   lists exactly (4 + 10 per dev season).

## Diagnosis (what the numbers say, not a rescue plan)

- **The OU leg fails for Gate Zero in every season, and pooled for
  every arm.** The model over-predicts the over-rate in the two cold
  seasons (pred OU2.5 0.420 vs actual 0.379 in 2022/2023; 0.428 vs
  0.404 in 2023/2024) and under-predicts it in the hot season (0.395
  vs 0.425 in 2024/2025). (X2 is the one exception to the
  every-season pattern: it passes the OU leg in 2023/2024, 0.6739 vs
  climatology 0.6749 — by 0.0010, not enough to save the pooled
  leg.) The league's level swings year to year (goals/match 2.41 →
  2.22 → 2.23 → 2.41) and the expanding DC with a 270-day half-life
  lags each swing by a season: its fitted mu (1.215 / 1.136 / 1.128
  across the three fits) is always the previous regime's level.
- **2024/2025 fails on everything.** It is the draw-heavy season
  (draws 31.9%, vs 24.6–30.5% before; home wins at their lowest,
  42.8%) and the model under-predicts draws (0.285 vs 0.319) while
  the level swing above also goes against it. The pooled failure is
  not a single bad season artifact, though: the OU leg already fails
  in the two good 1X2 seasons.
- **The two-group structure is not the suspect.** Within-group
  predictions are invariant to the per-group shift (MODEL_DESIGN
  §1), and the failure is spread across all three seasons and both
  groups' worth of matches — a level/draw problem, not an
  identification problem. No rescue arm is proposed in this verdict;
  post-hoc arms are forbidden, and the prereg's gate arithmetic is
  mechanical.

## Independent checks

- Climatology recomputed from the CSV by a second script (expanding
  prior-seasons rates per season, pooled over the three seasons):
  exact match to `results_dev.json` on all three metrics, all
  seasons + pooled.
- Production `model_v2.DC` replay (goals-only 5-tuples, hl=270) on
  the same training sets reproduces Gate Zero's 1X2 LL and OU2.5 LL
  to **0.000000** on all three dev seasons (rho 0.0 / −0.05 / −0.05,
  h 0.303 / 0.308 / 0.325). The failure belongs to the reference
  pattern in this league, not to the copy — the G-J2 conclusion, in
  this league's numbers.
- `grep` confirms the engine reads no `expected_goals` or stats /
  shotmap column anywhere; the dev loader asserts it never sees
  2025/2026 or 2026/2027 rows.

## Non-buildable candidates (feasibility, for the league record)

S-ESPF (SOT), C-ESPF (corners), K-ESPF (cards), T-ESPF (total
shots) are **NOT BUILDABLE**, with payload-level evidence in
DATA_UNDERSTANDING §2 / EDA F5–F9: stats feed empty in 4,081/4,081
payloads, shotmap empty in 4,081/4,081, referee text empty in
4,081/4,081; card events total 995 across 4,081 matches
(~0.24/match, in 18–25% of matches) with no stats feed to repair
them. No prereg, engine, or virgin read exists for them. If
FotMob's coverage of this league changes, feasibility re-opens by a
new prereg.

## Ships: nothing.

G-ESPF is FAIL. **ES-PrimeraFederacion is now fully complete**: its
one buildable candidate went through its gate and failed; the other
four are not buildable on availability. No predictions file, no
fitted params, no daily-pipeline activation. Virgin 2025/2026 was
never read and stays virgin; 2026/2027 (partial) stays reserved.
