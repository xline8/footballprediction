# Step 5 — Features: BG-SecondLeague (J1 template X1–X9 analogues)

Causality contract as in the J1 FEATURES.md (features computed only
from matches strictly before the target; nothing fabricated; a failed
reliability check means DROPPED).

| # | Feature | Verdict | Reason |
|---|---|---|---|
| X1 | Blend observation (goals + xG) | **ADOPTED, degraded** | xG coverage is 0% in every season, so the production blend's documented goals-only fallback applies to 100% of matches. The DC fit is goals-only by data, not by choice. |
| X2 | Mover tier offset (BG1↔BG2) | **DROPPED** | EDA F4: 1–2 relegated clubs per season, direction inconsistent (+0.48/−0.29, +0.26/−0.07, +0.02/+0.34). No reliable magnitude exists to freeze. |
| X3 | Set-play xG decomposition | **DROPPED** | No xG at all (0%). |
| X4 | xG-per-shot / ratio features | **DROPPED** | No shotmap (0%), no xG. |
| X5 | Finishing / form features | **DROPPED** | Forbidden program-wide (J1 F6 noise) and no data beyond goals. |
| X6 | xGOT era features | **DROPPED** | No shotmap/xGOT (0%). |
| X7 | Box touches (corners) | **DROPPED** | No stats feed (0%); corners market not buildable. |
| X8 | Referee covariate (cards) | **DROPPED** | Referee coverage 0%; cards market not buildable. |
| X9 | Territorial / corners base pattern | **DROPPED** | No stats feed (0%); corners market not buildable. |
| SHRINK | Thin-data rating shrinkage (sanctioned G-J2-lesson arm) | **ADOPTED as a pre-registered arm** | Addresses the documented DC failure mode (extreme lambdas for 1–5-match teams in season openers) without needing any absent data. Rule frozen in the prereg: ratings scaled by n/6 for teams with n<6 prior in-league matches. |

## Halves constants
**None.** No period splits exist (F3), so no market in this league
gets 1H/2H presentation. FT only.
