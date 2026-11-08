# Phase A — Exploratory Data Analysis: SCO Championship

All numbers are from `eda_summary.json`; this document is descriptive only.

## Findings

1. **Levels vary by season.** Goals range from 2.40 to 2.80 per match, SOT from 7.0 to 8.0, corners from 8.7 to 10.3, and feed total shots from 13.3 to 15.7. Event yellows rise from 3.21 in 2021/2022 to 4.34 in 2025/2026 (3.74 in the partial 2026/2027 season).
2. **Home scoring share is stable but elevated.** The seasonal range is 0.51–0.57.
3. **Split-half reliability is trait-specific.** Mean for/against r values are goals 0.295/0.296, SOT 0.197/0.414, corners 0.321/0.480, total shots 0.367/0.509, event yellows 0.301/0.231, and possession 0.638/0.638.
4. **Halves are presentation constants only.** The pooled first-half goal share is 0.4553 with true variance −0.0027, so it is NOISE and frozen as a constant. Yellow share is 0.3121 with small positive true variance +0.0063. SOT, corners, and total shots are FT-only and have null halves constants.
5. **Referee reliability is insufficient.** The split-half referee result is r=0.3318 across 16 referees, below the program adoption standard of about 0.45+.
6. **Cards are an artefact check, not a mixed target.** On all 19 rich matches, stats yellows equal event yellows exactly (19/19; mean difference 0.0). The other 950 matches have no stats `yellow_cards` key, so event yellows are the unified target by construction.
7. **Mover evidence supports an X2 arm.** Across four pooled seasons, teams from Premiership show ΔGF +0.3875 and ΔGA −0.4077 versus the Championship league mean. Teams from League One show ΔGF +0.0160 and ΔGA +0.0646, negligible in comparison.
8. **Primary lines are selected by closeness to a 0.5 dev over-rate.** Goals OU2.5: 0.5167 (n=540); SOT 7.5: 0.5152 (n=427); corners 9.5: 0.5386 (n=427); event yellows 3.5: 0.5407 (n=540); total shots 15.5: 0.4754 (n=427). The total-shots ladder is 13.5/14.5/15.5/16.5.

The charts in `charts/` show levels by season, trait reliabilities, and the frozen halves constants.
