# Pre-registration — FO-Logmanssteypid (FotMob 9523)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Is there enough data for a season-blocked walk-forward dev + a virgin
window at all? **No — for every candidate.** This prereg records the
NOT BUILDABLE verdict with its payload-level evidence, so that no
fitting, no virgin read, and no post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 6/6 payloads read)

- 6 matches total, exactly 1 per season, seasons 2021–2026. One
  single-match Cup Final per year (`leagueRoundName` / `matchRound`:
  `"final"`, `leagueName: "Cup"`); no other rounds. Three of the six
  finals were decided on penalties (2021 Pen 3–4, 2023 Pen 3–5,
  2024 Pen 3–4); no extra time in any payload.
- Scores 6/6; `content.stats` 0/6; shotmap with shots > 0 in 0/6
  (the key exists, the list is empty in every payload); events feed
  empty in 6/6 (0 events of any type — not even goal minutes);
  referee field 0/6; lineup 0/6; player stats 0/6. The competition
  is scores-only in the strongest sense.
- 6 distinct clubs (accent-normalised); no club plays more than 1
  match in any season; each season's two teams arrive with zero prior
  in-competition matches that season.
- Scope check: the warehouse holds exactly two Faroese competitions —
  Løgmanssteypið (9523, 6 rows) and the Premier League (250, 810
  rows). No other Faroese cup id exists and no cup rounds hide under
  another id. Scope is not widened.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: a "season" is 1 match between 2
  teams. Dixon-Coles / Poisson / NB ratings are not estimable — every
  season's teams have zero prior Løgmanssteypið matches, and the most
  frequent clubs hold 3 matches in 6 years.
- Virgin = 2026, n=1. Calibration SE at OU 2.5 ≈ 37pp (base rate 1/6),
  50pp at p=0.5 — ~37–50× the 1pp clean-PASS threshold. One goal in
  the single virgin match flips the observed rate between 0% and
  100%. A PASS/FAIL at n=1 would be a coin flip.
- Pooled n=6 does not rescue it: OU 2.5 SE ≈ 15.2pp, still 15× the
  clean threshold.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026): **NOT READ** for any candidate — deliberately
  unread, because no arm passes (or can pass) a dev gate. Reading it
  would be a result in search of a gate.
- Format rule (frozen for the record): single-match Final, one per
  year; draw at 90 minutes → straight to penalties (2021, 2023, 2024
  evidence; no extra-time halves in any payload).
- Halves constants: **none frozen** (no 1H splits exist anywhere —
  no stats, no goal-minute events).
- Features X1–X9: **all DROPPED** (see `analysis/FEATURES.md`).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**0 PASS / 0 FAIL / 5 NOT BUILDABLE.** G-FOL, S-FOL, C-FOL, K-FOL,
T-FOL are all NOT BUILDABLE on thinness. The league is complete on
this verdict. Any future revisit (e.g. a pooled cross-cup transfer
design) needs a new preregistration outside this program's
per-league gates; nothing is scheduled — at 1 match/year the
competition will not reach a gateable sample.
