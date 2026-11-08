# Phase 3.5 — DE-3Liga Features

All features are strictly pre-match, trailing, and computed from prior DE-3Liga matches only. Missing windows are NaN and deactivate the arm; no current-match or future information is filled in.

| J1 analogue | Verdict | DE-3Liga evidence |
|---|---|---|
| X1 xG blend | DROPPED | shotmap absent in 1,992/1,992 and no xG column; goals-only DC fallback is mandatory |
| X2 mover tier offset | DROPPED | entrant deltas across dev transitions −0.059/+0.057, +0.015/−0.053, −0.072/+0.007 GF/GA; Regionalliga is absent |
| X3 set-play xG | DROPPED | no xG or set-play xG |
| X4 xG per shot | DROPPED | no shotmap and no xG |
| X5 trailing target rates | ADOPTED | SOT, corners, event yellows and total shots are available in dev and virgin; trailing-10, min 6/10 valid |
| X6 xGOT | DROPPED | no shotmap/xGOT |
| X7 opponent-box touches | ADOPTED | split-half r 0.848 for / 0.821 against; coverage 64.5–100% |
| X8 referee yellows | ADOPTED | referee coverage 41.5% in seed, 88.2–100% later; referee split-half r 0.483; missing appointment falls back |
| X9 possession/big-chance territorial covariates | ADOPTED | possession r 0.901; big-chance r 0.689 for / 0.743 against; used only in corners Gate Zero |

Ratings, home advantage, count-distribution size, and the frozen half constants are architectural components, not covariates. Red cards, attendance, standings, h2h, formations, lineups, momentum, and in-match game-state fields are rejected as rare, post-match, or untested.
