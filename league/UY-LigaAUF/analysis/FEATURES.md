# Step 5 — Feature Engineering: UY-LigaAUF

J1-template features X1–X9, disposition for THIS league. A feature
is adopted only if its data exists AND its reliability passes in
EDA; every dropped template feature is recorded with its reason.
Evidence keys (F1–F7) are in `analysis/EDA.md`; numbers in
`analysis/eda_summary.json`.

| # | Template feature | Disposition for UY | Reason |
|---|---|---|---|
| X1 | xG blend (goals + xG) | ADOPTED as **goals-only fallback** | No `expected_goals*` key in any of 1,717 payloads, no shotmap (F1). The X1 blend's documented fallback: the observation is goals-only in every match. Goals trait reliable (F2: split-half r 0.588 attack / 0.809 defence). |
| X2 | Promoted/entrant handling | ADOPTED (entrant offset) | 9 dev entrant transitions (F4): mean GF −0.128 (8/9 negative), GA +0.145 (5/9 positive). Frozen log offsets in the prereg: attack −0.1178, defence −0.1188 (applied to the defence exponent). Noisier than the QA analogue — recorded, not adjusted. |
| X3 | Set-play share (xG split) | DROPPED | No xG, no set-play split exists in any season (F1). |
| X4 | On-target ratio inputs (SOT model) | DROPPED | No SOT target in any season (F1, F6). |
| X5 | Home advantage (goals) | ADOPTED | Dev scored window: home-win 0.381 vs away-win 0.337; fitted as the Dixon-Coles home parameter (init 0.25, per the reference). |
| X6 | Shot volume (total shots) | DROPPED | No total-shots target in any season (F1, F6). |
| X7 | Box touches / territory (corners) | DROPPED | No corners target, no touches_opp_box in any season (F1, F6). |
| X8 | Referee (cards) | DROPPED | Referee named in 0/1,717 matches in every season (F1, F6); no cards target either. |
| X9 | Keeper saves | DROPPED | No keeper_saves key in any season (F1). |

## Adopted feature set (goals only)

- **X1 goals-only:** per-match home/away goals from scoreStr
  (authoritative; 4,040 goals, 1,717 matches). No xG anywhere.
- **X2 entrant offset:** at prediction time, a team in its entrant
  season (absent in the immediately preceding season) has its
  attack exponent shifted by −0.1178 and its defence exponent
  shifted by −0.1188 (frozen, from EDA F4 against the dev scored
  mean team goals 1.1520/match). Applies to the team's fitted
  rating if it has one from an earlier season (returning team),
  otherwise to the league-mean fallback (0.0).
- **X5 home advantage:** single fitted home parameter in the
  Dixon-Coles likelihood.
- **Frozen halves constant (goals only): 0.4276** — the dev-era 1H
  share of goals from event times (F3, n=2,664 goals). Per-match
  half shares are noise; the constant is the only legal halves
  model. No constant exists for any count market.

## Dropped-template summary

X3, X4, X6, X7, X8, X9 are dropped on **absence** (the feed does
not exist in any season), not on a failed reliability test — there
is nothing to test. X1 survives only in its goals-only fallback
form. The goals engine therefore uses exactly X1 (goals-only) +
X2 + X5.
