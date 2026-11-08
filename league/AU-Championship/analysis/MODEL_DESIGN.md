# Step 6 — Model design: AU-Championship

Reference patterns (unmodified, as in J1): goals = production
Dixon-Coles (`model_v2.py`, DC + xG blend pattern); SOT = `model_sot.py`
v5; corners = `model_corners_v3.py`; cards = `model_cards.py`;
total shots = the shots family in `experiments/` + the J1 engine.
**None of these is built for this league**, for the reasons below.
This design records the feasibility matrix and the frozen decision,
so a future build (after more seasons exist) starts from evidence,
not from re-discovery.

## 1. Feasibility matrix

| Candidate | Target exists? | Dev window? | Virgin window? | Verdict |
|---|---|---|---|---|
| G-AUCH goals | Yes — scores 87/87 | **No** — one complete season only | 2026 transitional, n=32, SE ~8.6pp | **NOT BUILDABLE** |
| S-AUCH SOT | No — stats null 87/87, shotmap empty | No | No target in virgin either | **NOT BUILDABLE** |
| C-AUCH corners | No — stats null 87/87 | No | No target in virgin either | **NOT BUILDABLE** |
| K-AUCH cards | No — no yellows anywhere; reds near-zero-filled | No | No target in virgin either | **NOT BUILDABLE** |
| T-AUCH total shots | No — stats null 87/87, shotmap empty | No | No target in virgin either | **NOT BUILDABLE** |

## 2. Why goals is not buildable (the only candidate with a target)

The program's gate frame is season-blocked walk-forward: dev =
evaluation seasons, each predicted from all prior seasons, against
climatology baselines from prior seasons; virgin = the most recent
season, read once. That frame needs **at least one training season
plus at least one evaluation season**. This league has exactly one
complete season (2025, n=55):

- 2025 can only be the training window — the analogue of J1's 2021,
  which was the initial window and never an evaluation season.
  There is no prior season (the competition launched in October
  2025), so there is no prior-season climatology either.
- There is no evaluation season: 2026 is transitional (rounds 1–4
  of 6, n=32, final stage unplayed). It cannot serve as dev (it is
  the most recent season, i.e. the virgin slot) and it cannot serve
  as virgin for evaluation either, because no arm can pass a dev
  gate first — there is no dev gate to pass.
- Inventing a round-blocked within-season dev (train on rounds 1–2,
  predict round 3, …) would deviate from the frozen frame. The
  frame is program-level, not mine to change in a league build, and
  the deviation would not help anyway: teams play 6 group matches,
  so a rating after rounds 1–2 rests on 2 matches per team, and the
  G-J2 post-mortem shrinkage arm exists precisely because such
  ratings are extreme — but a shrinkage arm still needs a dev
  window to validate, which is the thing that does not exist.
- Even if a gate could be run, it could not discriminate. The
  virgin (2026, n=32) has a calibration SE at OU 2.5 of
  √(0.625·0.375/32) ≈ 8.6pp and at home-win rate ≈ 8.7pp — ~9× the
  1pp clean-PASS threshold, so the PROVISIONAL band (±1 SE) would
  pass almost any arm. Pooled n=87 still gives SE ≈ 5.3pp (5× the
  threshold). One goal in the virgin swings the over-rate by
  3.1pp. A PASS/FAIL there would be decided by one or two goals —
  the same coin-flip the CO-Superliga prereg refused at n=2, at
  larger n but the same ratio to the gate.
- Per-team data is thinner than the frame assumes: finalists play
  9 matches in a season, everyone else 6–8. Dixon-Coles attack /
  defence ratings (32 parameters on 55 matches, most teams with
  6 observations) are not estimable to gate standard.

## 3. Why S/C/K/T are not buildable

The target does not exist in any payload, in any season, including
the virgin season: `content.stats` is null in 87/87 Championship
payloads, `content.shotmap.shots` is empty in 87/87,
`content.matchFacts.events.events` is empty in 87/87, the referee
field is blank. There is no SOT total, no corners total, no
yellow-card total, no total-shots total to model, and no dev or
virgin window could ever contain one without FotMob changing its
coverage of this competition (coverageLevel `lower`, 1,333/1,333).
Cards specifically: the only card-adjacent signal is red-card
counts in `header.status`, near-zero-filled (≥1 red in 12/1,333
parent matches) — not a yellow/total-cards target, and not a line
any market is priced on.

## 4. Rejected transfers (recorded so they are not re-proposed)

- **Pooled 1,333-match model (parent id as one league):** invalid.
  Ten disjoint competitions, no cross-state play, block-diagonal
  design; state scores 48% unrecorded. Rejected on structure, not
  on sample size.
- **State-league ratings as Championship priors (X2 analogue):**
  rejected. State form is same-season concurrent (Feb–Sep → Oct–Dec),
  not a prior-season mover offset; 48% of state scores are missing;
  and any offset would be unvalidatable (no dev/virgin window
  in-competition). A future design that wants state-league priors
  needs a new program-level prereg, not a league-build improvisation.
- **A-League ratings as priors:** no overlap (0 clubs), so there is
  nothing to transfer.
- **Within-season round-blocked dev:** a frame change, not a league
  decision (see §2). Not run.

## 5. What a future build needs (revisit condition)

Earliest gateable build: once the 2026 season completes, dev =
2025+2026 (n≈110, one evaluation season) with virgin = 2027
(n≈55) — still thin (virgin SE ≈ 6.6pp), so provisional outcomes
are likely. A proper multi-season dev needs 2025–2027 as dev with
2028 as virgin. Either revisit needs a **new preregistration**;
nothing is scheduled, and no virgin read under this prereg is
permitted to pre-empt it. If FotMob's coverage of the competition
improves (stats blocks appearing), S/C/K/T become re-assessable on
the same revisit — verify from payloads, never from the index flags.

## 6. Charts

No `charts/` directory (same as CO-Superliga, the program's other
0/0/5 league): with two seasons of scores-only data and no traits
or halves, the J1 chart set has nothing to plot beyond the two-row
levels table in EDA.md §F1. A chart of two bars would be decoration,
not evidence.

## 7. What ships

Nothing — no engine, no fitted parameters, no predictions, no halves
constants, no daily-runner join. The league is complete on this
verdict: **0 PASS / 0 FAIL / 5 NOT BUILDABLE**.
