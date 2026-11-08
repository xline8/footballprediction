# Step 6 — Model Design: BG-SecondLeague

## Feasibility matrix
| Candidate | Target exists? | Virgin window contains target? | Buildable |
|---|---|---|---|
| **G-BG2 goals** | Yes — FT score 1,722/1,722 | Yes — 2025/2026, n=272 | **YES** |
| S-BG2 SOT | No — stats 0%, shotmap 0% | No | **NO — documented not-buildable** |
| C-BG2 corners | No — stats 0% | No | **NO — documented not-buildable** |
| K-BG2 cards | No — stats 0%, referee 0% (event lists in 70% are not a settlement-grade target) | No | **NO — documented not-buildable** |
| T-BG2 total shots | No — stats 0%, shotmap 0% | No | **NO — documented not-buildable** |

## Candidate G-BG2 — goals model (1X2 / OU / BTTS / DC)
- **Reference**: production Dixon-Coles pattern (as in G-J1/G-SCO):
  iterative multiplicative fit, 14 sweeps, damping 0.7, +0.25 smoothing,
  fitted home advantage, rho from grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood, MAXG = 10, time decay half-life 270 days.
- **Observation**: goals-only throughout (X1 degraded — no xG exists).
  This is the production blend's documented fallback applied to 100%
  of matches, not a new architecture.
- **Arms** (frozen in the prereg, at most the sanctioned set):
  1. **Gate Zero** — the unmodified reference. Unseen teams start at
     the league mean.
  2. **SHRINK** — Gate Zero + the sanctioned G-J2-lesson shrinkage for
     teams with <6 prior in-league matches (ratings × n/6 at
     prediction time). X2 mover offsets were considered and dropped
     on EDA F4 evidence (1–2 clubs/season, inconsistent direction).
- **Windows**: dev = season-blocked walk-forward, seed 2021/2022
  (n=329), evaluation 2022/2023 + 2023/2024 + 2024/2025 (pooled
  n=992). Virgin = **2025/2026 (complete, n=272)**, read ONCE, only
  for arms passing the dev gate. 2026/2027 (in progress, n=129 at
  pull) is reserved as the confirmatory window and is NOT read.
- **Primary line**: OU **2.5** (dev over-rates 0.35–0.47; the central
  line of the dev distribution).
- **Baselines**: climatology (expanding, prior-seasons-only outcome
  rates + OU2.5 over-rate). Naive trailing-10 applies to count
  markets; no count market is buildable here.
- **Gate legs**: identical to the program's goals gates (dev gate vs
  climatology on 1X2 LL + RPS + OU2.5 LL; virgin legs (i) LL ≤ Gate
  Zero and ≤ climatology, (ii) calibration |breach| ≤ 1pp clean PASS,
  ≤ 1 SE PROVISIONAL PASS, else FAIL, on home-win and OU2.5;
  (iii) per-season sign check for variants; both-pass rule → lower
  virgin LL ships, ties to the simpler arm).
- **Presentation**: FT only — no halves constants exist (F3).
