# Features

The feature contract is strictly pre-match, trailing/expanding and keyed by FotMob team id. No feature is computed from the target match.

| feature | status | reason |
|---|---|---|
| X1 xG blend | DROPPED | No expected_goals exists in any development row; goals-only DC is required. |
| X2 mover tier offset | DROPPED | No promotion/relegation tier system exists; expansion clubs are not tier movers. Replaced by sanctioned goals SHRINK, with a*=n/6 and d*=n/6 for n<6 prior matches. |
| X3 set-play xG | DROPPED | No development xG, hence no dev window. |
| X4 xG/shot | DROPPED | No development shotmap/xG. |
| X5 trailing target rates | ADOPTED | Stats-feed targets are available across the development and virgin regular windows; trailing-10 reference feature. |
| X6 xGOT | DROPPED | xGOT/shotmap begins only in 2025/2026, so no development window. |
| X7 box touches | ADOPTED | Development split-half r=0.876 for touches-for; two missing rows are handled by the minimum-observation rule. |
| X8 referee strictness | ADOPTED | Stats-yellow referee split-half r=0.424 across 9 referees with >=20 assignments; missing referee falls back to base arm. |
| X9 possession + big chance | ADOPTED | Gate Zero covariates; possession-for r=0.923 and big-chance-for r=0.662. |

Rejected: event yellows (era-flipped under-recording), red-card rates (rare and not the target), first-half team shares (noise test), standings/table snapshots (leakage), attendance (post-match), lineups/absence, formations and momentum (not an established pre-match reliability feature). Cards target is stats-feed yellow_cards only.

Frozen presentation constants are goals 0.459, SOT 0.469, corners 0.480, total shots 0.467 and yellows 0.314 for FT→1H; 2H is one minus the constant.
