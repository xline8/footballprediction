# Step 5 — Features: CO-PrimeraB (J1 X1–X9 template applied)

Global causality contract as in `league/J1/analysis/FEATURES.md`
(features use only matches strictly before kickoff; no fabrication).

| # | J1 feature | CO verdict | Reason (with number) |
|---|---|---|---|
| X1 | Blend observation (goals + xG) | **ADOPTED, reduced** | goals present 1,639/1,639 finished; xG absent everywhere (stats null 1,773/1,773) → the reference blend's own documented goals-only fallback. |
| X2 | Mover cross-tier prior | **ADOPTED as arm X2** | Primera A (id 274) IS in the warehouse. Dev-era relegated arrivals (2023–2024, 4 club-seasons) show ΔGF +0.11/m and ΔGA −0.30/m vs the B mean, same direction 4/4 on both sides (EDA F4). Frozen form: for a club flagged mover_down (absent from B in S−1, present in A in S−1), its fitted ratings are replaced at prediction time by a = ln(1.10), d = ln(0.73) for that season's predictions. Offset estimated from dev-era arrivals ONLY. |
| X3 | Set-play xG decomposition | **DROPPED** | No xG at all (0/1,773). |
| X4 | Box touches / SOT-adjacent rates | **DROPPED** | No stats feed (0/1,773). |
| X5 | Referee strictness | **DROPPED** | Referee text empty in every dev season (0/1,053 finished 2021–2024); appears only in 2025 (141/308) and 2026 — no dev-era trait can be estimated. |
| X6 | Corner traits | **DROPPED** | No corner data in any source (0/1,773). |
| X7 | Card traits | **DROPPED** | Card events fragmentary in 2022–2025 (77–96 events/season); complete-looking only in in-progress 2026, which cannot fit or gate a model. |
| X8 | (fixture-static facts) | team ids + venue only | Used as DC inputs, as in every goals engine. Phase (regular/quadrangular/final) is recorded per match but is NOT a feature and NOT a filter (frozen phase rule, DATA_UNDERSTANDING). |
| X9 | Shot-volume traits | **DROPPED** | Shotmap empty in 1,773/1,773. |

## Adopted variant mechanisms (pre-registered in PREREG_G_CO)

- **X2** (above) — cross-tier mover prior, the FEATURES-sanctioned
  use of the Primera A warehouse data.
- **SHRINK** (G-J2 post-mortem lesson, named pre-fitting per the
  conveyor template): at prediction time, a team with fewer than 6
  prior in-league matches in the training window has its fitted
  attack/defence ratings scaled toward the league mean:
  `a *= n/6`, `d *= n/6`, n = prior in-league matches (n=0 ⇒ league
  mean, identical to Gate Zero). In this league the arm is LIVE, not
  degenerate: the partial 2021 seed leaves two 2022 target clubs at
  3 and 5 priors (EDA F4).

## Halves constant

- Goals: **0.4875** (pooled dev 2022–2024 1H share from goal-event
  times on event-exact matches; EDA F3). Presentation only, frozen
  in the prereg.
- No other market exists, so no other constant is recorded.
