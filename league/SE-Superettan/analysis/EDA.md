# Step 3 — EDA: SE-Superettan

Numbers from `analysis/eda.py` → `analysis/eda_summary.json` (recompute, do not copy by hand).

## F1 — Levels and drift
Goals/match: 2.55 (2021), 2.90, 2.80, 2.64, 2.86, 2.90 (2026). Home goals exceed
away goals every season (home 1.41–1.63, away 1.14–1.35). SOT: 9.79 / 9.67 / 9.50 /
**12.33 (2025)** / 8.57 (2026). Corners: 10.42 / 10.59 / 10.23 / 9.67 / 10.13.
Total shots: 19.98 / 20.07 / 19.63 / 21.58 / 19.52. Yellows: 3.67 / 4.24 / 4.04 /
3.92 / 3.53 / 3.17 — a steady decline; a trailing/adaptive component matters for cards.
The 2025 SOT level is a one-season regime spike (SOT/shot 0.571 vs 0.439–0.484
elsewhere) and the 2026 virgin SOT level (8.57) sits below every dev season:
both facts are frozen into the record before fitting; the SOT gate will decide.

## F2 — Team trait reliability (split-half, career-pooled, stats era 2022–2026)
SOT-for r = 0.589 (31 teams); corners-for r = 0.752; total-shots-for r = 0.756;
yellows-for r = 0.624 (33 teams, all seasons); goals-for r = 0.501;
possession r = 0.605. All real signal, corners/shots strongest — the reference
architectures (ratings + trailing components) are justified in this league.

## F3 — Halves (event times only; no splits exist)
Goals 1H share, dev era 2021–2025: **0.4317** (n = 1,112 matches with goals).
Yellows 1H share, dev era: **0.3344** (n = 1,180). Per-match share variance exceeds
the naive binomial floor, as it mechanically does with small counts and mixed
denominators; per the program's settled finding (per-match half share is noise
around a league constant), these are frozen as presentation constants only.
SOT / corners / total shots have NO halves source → FT-only, frozen.

## F4 — X2 movers (parent corpus exists: league/SE-Allsvenskan/data/)
12 relegated-entrant transitions 2022–2026 (a club whose previous season was in
Allsvenskan and which was not in Superettan): in their first Superettan season
they score **+0.117 goals/match above** the league team mean and concede
**−0.192/match below** it — relegated entrants are stronger than the average
Superettan side, in the expected direction, on a small n. 13 further entrants
arrive from Division 1, for which no corpus exists in-system (their X2 offset is
not measurable; the SHRINK arm covers thin-data entrants generically).

## F5 — Feed absences (all verified by full-corpus scan)
No xG (any key, any season), no shotmap, no big_chance, no touches_opp_box,
no period splits, no referee names (0/1,440), no stats card keys.
Possession is the only territorial covariate the feed carries.

## Primary lines (dev distribution, frozen in the preregs)
Goals OU 2.5 (dev over-rate 0.532). SOT 9.5 (over 0.511). Corners 10.5
(over 0.461; 9.5 gives 0.573, farther from 0.5). Total shots 20.5 (over 0.474).
Yellows 3.5 (over 0.519).
