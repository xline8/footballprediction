# Step 6 — Model Design: HR-HNL

Windows (frozen for every candidate): training seed 2021/2022;
**dev = walk-forward, scored seasons 2022/2023–2024/2025 (pooled
n = 540)**; **virgin = 2025/2026 (n = 180), read ONCE, only for
dev-passing arms**. 2026/2027 is in progress and excluded (reserved as
a future confirmatory read). Calibration convention in this league:
diff = mean predicted − actual (FI convention); gates use |diff|.

Gate legs (identical across the programme): dev gate — pooled dev LL
at the primary line beats BOTH baselines (league base rate;
naive trailing-10), else the arm is dead and the virgin is not read
for it; if Gate Zero fails its dev gate the candidate FAILS and the
virgin is NOT read at all. Virgin legs — (i) LL ≤ Gate Zero's and
≤ best baseline's; (ii) calibration |breach| ≤ 1.0pp clean PASS,
breach within 1 SE of the boundary PROVISIONAL PASS, else FAIL;
(iii) dev per-season sign check for the both-pass rule (variant dev
LL ≤ Gate Zero's in at least half the dev seasons — ≥2 of 3).
Both-pass: lower pooled virgin LL ships; ties → simpler arm.

## Candidates

### G-HR — goals (Dixon-Coles, goals-only)
Reference: production `model_v2.py` DC pattern (14 sweeps, damping 0.7,
+0.25 smoothing, home init 0.28, MAXG = 10, production tau, rho grid
(0.0, −0.05, −0.10, −0.15) by goals LL, decay HL = 270 days), goals-only
observations in every match (X1 fallback — no xG exists here).
Arms: **Gate Zero**; **SHRINK** (sanctioned G-J2 lesson: prediction-time
rating shrink × n/6 for teams with n < 6 prior in-league matches);
**X2** (SHRINK + entrant offset, FEATURES X2). Metrics: 1X2 LL, RPS,
OU2.5 LL vs climatology (prior-seasons pooled rates). Dev gate: all
three pooled metrics beat climatology (FI G pattern).

### S-HR — shots on target (v5 pattern)
Reference: production `model_sot.py` v5, programme-frozen constants
(ridge λ = 100, HL = 365, lazy refit 7 days, total-shots ratings prior
K = 8, Beta-Binomial prior P = 200, 50/50 ensemble with naive
trailing-10, NB size r = 79.94). Arms: **Gate Zero**; **RS** (BB prior
P = 200 → 20,000). Target: total SOT (stats feed, present 540/540 dev
+ 180/180 virgin). Primary line **7.5** (dev over-rate 0.552), ladder
6.5 / 7.5 / 8.5. No X4/X6 arms — no shotmap (FEATURES).

### C-HR — corners (corners_v3 pattern)
Reference: production `model_corners_v3.py` as frozen in PREREG_C_J1
(HL = 270 base rates, rolling-5 relative factors clamped [0.6, 1.7],
NB pmf grid 0..50, per-season gamma/beta/r fitting on prior-season
walk-forward rows only, gamma grid (0.0, 0.15, 0.3, 0.45, 0.6, 0.8),
r clamped [1.02, 5.0], territorial multiplier clamped [0.70, 1.43],
min-8-of-last-10 validity, date-grouped predict-then-update).
Arms: **Gate Zero** (X9 full: possession + big-chance betas);
**X7** (opp-box-touches multiplier replacing the territorial
multiplier, J1 pattern). Primary line **8.5** (dev over-rate 0.509),
ladder 7.5 / 8.5 / 9.5.

### T-HR — total shots (shots family)
Reference: the programme shots family (joint Poisson ratings store +
NB over-probabilities) as in the J1/CY T engines. Arms: **A** (v1
pattern), **B** (v2 level layer), **C** (E9 trailing-200 r). Target:
total shots (stats feed; definition stable — EDA F1 on-target share
0.320–0.343 all seasons). Primary line **23.5** (dev over-rate 0.524),
ladder 22.5 / 23.5 / 24.5.

### K-HR — cards: NOT BUILT
Feasibility fails on the target, not the virgin: the stats-vs-events
check (EDA F6) shows an era-flipped artefact — no credible cards
target exists before 2023/2024 in either source, leaving at most one
scored rich-era dev season (2024/2025) before the virgin, below the
programme's walk-forward minimum (warm-up + ≥3 scored seasons; T-FI
precedent). No arm, window, or line is frozen; nothing is fitted; the
virgin is not read for cards. PREREG_K_HR records the decision.

## Halves presentation (built markets)

FT + 1H/2H via the frozen constants of EDA F3 (goals 0.4320, SOT
0.4729, corners 0.4793, total shots 0.4661), presentation only, on
PASS only.
