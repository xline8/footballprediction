# Step 6 — Model Design — CL-LigaDePrimera

Windows (frozen for every candidate): warm-up/seed **2021**;
dev = walk-forward scored **2022, 2023, 2024**; virgin = **2025**
(last complete season, read ONCE, only for dev-passing arms);
confirmatory **2026** (in progress, 216/240) never read in this
build. Phase rule: all rows `regular`. Calibration =
actual − predicted everywhere. Gate rule (program-wide, verbatim in
each prereg): dev gate vs baselines; virgin legs (i) LL, (ii)
calibration |breach| ≤ 1.0pp clean PASS, ≤ 1 SE PROVISIONAL, else
FAIL; (iii) per-season sign check for variant both-pass.

Feasibility matrix: goals — target exists everywhere → candidate.
SOT / corners / total shots — stats target exists 2021+ and the
2025 virgin contains it (240/240) → candidates. Cards —
event-unified target exists everywhere and the virgin contains it
→ candidate (stats target rejected, Step 1 artefact). All five
candidates are buildable; none is excluded by feasibility.

| candidate | reference pattern | arms | primary line (dev over-rate) |
|---|---|---|---|
| G-CL goals | production Dixon-Coles (model_v2 `DC`), goals-only, hl=270 | Gate Zero; SHRINK (sanctioned G-J2 arm) | OU 2.5 (0.515) + 1X2 LL/RPS |
| S-CL SOT | production model_sot v5 | Gate Zero; RS (BB prior 200→20,000) | 8.5 (0.520) |
| C-CL corners | production corners_v3 pattern | Gate Zero; BOXT (X7 box-touch multiplier) | 9.5 (0.508) |
| K-CL cards | production model_cards pattern, event-unified target | Gate Zero only (X8 dropped) | 5.5 (0.464) |
| T-CL total shots | shots family (J1 T engine pattern) | A v1; B v2 level layer; C E9 trailing-r | 25.5 (0.529) |

Dev scored n: goals/cards 720; SOT/corners/total shots 719 (one
2022 match has no stats). Virgin n: 240 per candidate (2025 stats
coverage 240/240).

Baselines per candidate: league base rate (prior-seasons rate at
the primary line, constant within target season) and naive
trailing-10 through the candidate's own distribution family.
Nothing ships on FAIL; on PASS the winning arm's fitted params +
virgin predictions CSV ship.
