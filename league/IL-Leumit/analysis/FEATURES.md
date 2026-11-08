# Step 5 — Features: IL-Leumit

Consumption rule as in the J1 template: MODEL_DESIGN may use only
features defined ADOPTED here, plus architectural components in §2.
The global causality contract is the J1 one (features for target
match M use only matches strictly before M; trailing/expanding
windows as specified; ratios of sums; fitted state never from after
M). This is a goals-only corpus, so most of the J1 template fails on
coverage — dropped for absence of data, never faked.

## §1 Template features (X1–X9 analogues)

| # | Feature | Verdict | Reason |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED, goals-only** | Goals exist 1,581/1,581; xG exists nowhere (stats 0%). The production blend's documented goals-only fallback is the whole observation here — same situation as G-J2/G-J3. F1/F2 justify the DC fit with time decay. |
| X2 | Mover tier offset | **ADOPTED as a gated arm** | EDA F4 (SIGNAL-CANDIDATE): down-movers from Ligat ha'Al GF +0.291 / GA −0.239 vs mu (n=8 team-seasons); up-movers from tier 3 GF −0.080 / GA +0.109 (n=8). Membership keyed by FotMob team ID; ha'Al membership from league_id 127 in the same warehouse; tier-3 membership = entrant absent from both leagues the prior season. Magnitudes frozen from EDA in the prereg. |
| X3 | Set-play xG share | **DROPPED** | No stats feed (0%). |
| X4 | xG per shot | **DROPPED** | No shotmap (0%). |
| X5 | Trailing target-rate means | **DROPPED for this league** | Its targets (SOT/corners/cards) do not exist; the goals harness baseline is climatology, not a trailing-10 feature. |
| X6 | xGOT per shot | **DROPPED** | No shotmap (0%). |
| X7 | Opp-box touches | **DROPPED** | No stats feed (0%). |
| X8 | Referee yellow rate | **DROPPED** | No cards target exists to model; referee detail was not audited at Step 1 and cannot create a market. |
| X9 | Territorial covariates (possession, big chances) | **DROPPED** | Corners not buildable; no stats feed (0%). |

## §2 Architectural components (not features)

- Ratings, home advantage, Dixon-Coles rho are fitted parameters of
  the reference architecture (justified by F1/F2), under the
  signed-age rule.
- **SHRINK arm** (sanctioned cross-league lesson, G-J2 post-mortem,
  named in the template brief): for a team with fewer than 6 prior
  in-league matches in the training window, shrink its fitted ratings
  toward the league mean (`a *= n/6`, `d *= n/6`). Legitimate here as
  a PRE-REGISTERED variant: Leumit has 4 mover entrants every season
  whose early-season ratings are exactly the failure mode named.
- League base rates / climatology belong to the harness, not a model.
- **No halves constants exist** (F3): no period splits → nothing to
  freeze → FT presentation only.

## §3 Rejected

| # | Item | Reason |
|---|---|---|
| R1 | Team/league half shares | NOT TESTABLE — no period splits (F3); halves book cannot even be opened. |
| R2 | Trailing finishing / conversion | No xG/shots; also NOISE in J1 (F6 analogue). |
| R3 | Standalone on-target rate | No SOT data; NOISE in J1. |
| R4 | Lineup/absence features | CLOSED program-wide (V10/J1 F10); no lineups here anyway (0%). |
| R5 | Phase (regular/split) as a covariate | Descriptive level gap exists (EDA), but phase is not in the reference architecture and no reliability check supports it as a feature; adding it would be an unregistered invention. Both phases remain in the fit as matches. |
| R6 | Standings / h2h / form snapshots | LEAKAGE (post-match snapshots), as in J1 R9. |
