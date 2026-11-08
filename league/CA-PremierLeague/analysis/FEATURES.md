# Phase A features — CA-PremierLeague

The causality contract is strict: features use only matches before the target kickoff, trailing windows are not backfilled, ratios are ratios of sums, and missing windows deactivate the arm.

| Feature | Verdict | Evidence |
|---|---|---|
| X1 goals-only form | **ADOPTED** | xG key absent in 699/699 payloads; goals remain complete and stable enough for the goals architecture. |
| X2 mover tier offset | **DROPPED** | No tier corpus, no pro/rel, and only one expansion instance: Vancouver 2023 (ΔGF −0.304, ΔGA +0.482). |
| X3 set-play xG | **DROPPED** | No xG. |
| X4 xG per shot | **DROPPED** | Shotmap is empty in 699/699. |
| X5 trailing target-rate means | **ADOPTED** | SOT/corners/shots are complete; cards are stats-yellows only in credible 2023–2025 era. |
| X6 xGOT per shot | **DROPPED** | No shotmap/xGOT. |
| X7 opponent-box touches | **DROPPED** | 34/115, 28/117 and 22/117 all-match availability in 2021–2023, so the eight-match trailing rule fails through most dev. |
| X8 referee yellow rate | **DROPPED** | 0/115, 91/117, 98/117, 110/117, then 40/117 named referees in 2021–2025; virgin coverage collapses. |
| X9 possession + big chance form | **ADOPTED** | Both are present 699/699; possession-for reliability is 0.873. Big chance is carried as production form despite weaker 0.127 2023–2024 reliability. |

Half shares are frozen league constants, not team features. Standings, h2h, attendance, formations, lineups, momentum and game-state variables are excluded as leakage, non-pre-match or untested. Reds are not a target or covariate.
