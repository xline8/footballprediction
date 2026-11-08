# Step 5 — Features: GE-Erovnuli (J1 X1–X9 template applied)

Global causality contract as in `league/J1/analysis/FEATURES.md`
(features use only matches strictly before kickoff; no fabrication).

| # | J1 feature | GE verdict | Reason (with number) |
|---|---|---|---|
| X1 | Blend observation (goals + xG) | **ADOPTED, reduced** | goals present 1,059/1,059; xG absent everywhere (stats null 1,059/1,059) → the reference blend's own documented goals-only fallback. |
| X2 | Mover cross-tier prior | **DROPPED** | Feeder tier (Erovnuli Liga 2) is not in the warehouse corpus — no prior-season feeder scoring exists to estimate an offset from. Movers handled by SHRINK instead (design-sanctioned alternative). |
| X3 | Set-play xG decomposition | **DROPPED** | No xG at all (0/1,059). |
| X4 | Box touches / SOT-adjacent rates | **DROPPED** | No stats feed (0/1,059). |
| X5 | Referee strictness | **DROPPED** | Referee text empty in 1,059/1,059. |
| X6 | Corner traits | **DROPPED** | No corner data in any source (0/1,059). |
| X7 | Card traits | **DROPPED** | Card events fragmentary (233 events / 205 matches only). |
| X8 | (fixture-static facts) | team ids + venue only | Used as DC inputs, as in every goals engine. |
| X9 | Shot-volume traits | **DROPPED** | Shotmap empty in 1,059/1,059. |

## Adopted variant mechanism (not an X-feature; the template's sanctioned arm)

- **SHRINK** (G-J2 post-mortem lesson, named pre-fitting per the
  conveyor template): at prediction time, a team with fewer than 6
  prior in-league matches in the training window has its fitted
  attack/defence ratings scaled toward the league mean:
  `a *= n/6`, `d *= n/6`, n = prior in-league matches (n=0 ⇒ league
  mean, identical to Gate Zero). Bites exactly for 1–5-match teams —
  the season-opener / new-club failure mode (F4).

## Halves constant

- Goals: **0.4516** (pooled dev 2021–2024 1H share from goal-event
  times; EDA F3). Presentation only, frozen in the prereg.
- No other market exists, so no other constant is recorded.
