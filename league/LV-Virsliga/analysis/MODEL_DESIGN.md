# Step 6 — Model Design: LV-Virsliga

No fitting in this step. Calibration = actual − predicted
everywhere in this build. Gate legs are the program-standard legs
(RU-1Division pattern): dev gate vs baselines; virgin LL leg +
calibration leg (|breach| ≤ 1pp clean PASS, ≤ 1 SE PROVISIONAL,
else FAIL); Gate Zero dev failure ⇒ candidate FAILS, virgin NOT
read; gates never move after results.

## Feasibility matrix

| candidate | target exists | scorable dev window | virgin contains target | verdict |
|---|---|---|---|---|
| G-LV goals | all seasons | 2022–2025 (n=720) | yes (179) | BUILDABLE |
| S-LV SOT | stats era only | 2025-05-01–11-09 (133) | yes (179) | BUILDABLE |
| C-LV corners | stats era only | same (133) | yes (179) | BUILDABLE |
| K-LV cards | stats era only (event yellows) | same (133) | yes (179) | BUILDABLE |
| T-LV total shots | stats era only | same (133) | yes (179) | BUILDABLE |

The count dev windows are short (133 scored matches after a
47-match warm-up) — recorded as a limitation, not papered over:
baselines face the same window. The goals dev window is a full
four seasons (720).

## Candidates

- **G-LV** — production DC pattern, goals-only (X1 dropped), hl=270.
  Arms: Gate Zero; SHRINK (sanctioned entrant arm: ratings of teams
  with <6 prior in-league matches shrunk a,d *= n/6; EDA entrant
  gaps ΔGF −0.453 / ΔGA +0.255, n=6 — the largest entrant gap in
  the program so far). Season-blocked: seed 2021, dev scored
  2022–2025 (n=720), virgin 2026 (n=179 played; the RFS–Riga FC
  round-36 fixture is absent from the warehouse). Primary OU 2.5.
- **S-LV** — production v5 pattern. Arms: Gate Zero; RS (BB prior
  200 → 20,000). Per-match walk-forward over the stats era:
  warm-up 2025-03-05–04-30 (47 matches, never scored), dev scored
  2025-05-01–11-09 (133), virgin 2026 (179). Primary line 9.5,
  ladder 8.5/9.5/10.5.
- **C-LV** — production corners_v3 pattern, possession-only
  territorial multiplier (X9 partial; big_chance identically 0,
  X7 dropped). Arms: Gate Zero only. Same windows as S-LV (133
  dev / 179 virgin). Primary line 9.5, ladder 8.5/9.5/10.5.
- **K-LV** — production cards pattern on event-unified yellows
  (Yellow + YellowRed). Arms: Gate Zero only (X8 dropped —
  referee coverage 22%). Same windows (133 dev / 179 virgin).
  Primary line 4.5, ladder 3.5/4.5/5.5. Halves via frozen 0.3306.
- **T-LV** — shots family. Arms: A (v1), B (v2 level layer), C (E9
  trailing-r). Same windows as S-LV. Primary line 26.5, ladder
  25.5/26.5/27.5.

## Halves presentation

All five markets FT + 1H/2H via frozen 2025 constants: goals
0.4569, SOT 0.4637, corners 0.4816, total shots 0.4685, yellows
0.3306 (presentation only; true per-match share variance = 0 in
every market).
