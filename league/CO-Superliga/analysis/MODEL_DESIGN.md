# Step 4 — Model Design: CO-Superliga

## Feasibility matrix (payload-verified)

| Candidate | Target exists? | Dev window? | Virgin window? | Verdict |
|-----------|---------------|-------------|----------------|---------|
| G-COS goals | Yes — scores 12/12 | **No** — 2 matches/season; no team ratings estimable | **No** — 2026 is n=2 | **NOT BUILDABLE** |
| S-COS SOT | Partial — stats 7/12, shotmap 4/12 | **No** | **No** — 2026 is n=2 | **NOT BUILDABLE** |
| C-COS corners | Partial — stats 7/12 | **No** | **No** — 2026 is n=2 | **NOT BUILDABLE** |
| K-COS cards | Events only, 12/12; no referee, stats `yellow_cards` zero-filled pre-2025 | **No** | **No** — 2026 is n=2 | **NOT BUILDABLE** |
| T-COS total shots | Partial — stats 7/12, shotmap empty pre-2025 | **No** | **No** — 2026 is n=2 | **NOT BUILDABLE** |

No candidate reaches the design stage. No arms are registered, no
primary line is chosen, no engine is built. The prereg
(`prereg/PREREG_CO_SUPERLIGA.md`) records this feasibility verdict
itself, committed before any fitting — and no fitting is done at all.

## Why "just fit goals anyway" fails — the gate arithmetic

The program's gate needs a season-blocked walk-forward dev and a virgin
read. Suppose, against the design, one tried dev = 2021–2025 (10
matches) and virgin = 2026 (2 matches):

- **Dev is not a walk-forward.** A Dixon-Coles fit needs attack/defence
  ratings per team. Each dev season contributes exactly one tie between
  two teams that play no other Superliga match that season; the ratings
  for a season's teams would be fitted on the very 2 matches being
  predicted (in-sample), or borrowed from elsewhere. There is no
  "trailing" inside the competition.
- **Virgin calibration is meaningless at n=2.** At the OU 2.5 line the
  base rate over all 12 matches is 4/12 = 33.3%; the binomial SE at n=2
  is √(.333×.667/2) ≈ 33pp, and at p=0.5 it is ≈35pp. The clean-PASS
  rule (|breach| ≤ 1pp) is ~1/33 of one SE: a single goal in either
  virgin match moves the observed rate by 50pp and flips any verdict.
  A "PASS" here would be a coin flip with a gate stamp on it.
- **Pooling does not rescue it.** Even treating all 12 matches as one
  sample, the OU 2.5 SE is √(.333×.667/12) ≈ 13.6pp — still 13× the
  clean threshold. No calibration claim at the program's precision is
  possible from this competition, in any window split.

## The borrowed-ratings alternative — considered and rejected

The only conceivable model is not a Superliga model at all: take the
parent league's team ratings (Colombia Primera A, FotMob league_id 274
in the warehouse — note the task brief's "FotMob 113" does not match
the warehouse id; Primera A's own config records `fotmob_id: 274`,
3 PASS / 2 FAIL) and apply them to the two Superliga legs, with a home
advantage. That design is rejected for this program, not for lack of
imagination:

1. It cannot pass the program's gates: there is no in-competition dev
   window to fit or validate the Primera-A-to-Superliga transfer (the
   transfer itself — champion-vs-champion, January, one-off tie — is
   exactly what would need validating), and no virgin window to read.
2. It would ship 2 predictions a year with no validation — the opposite
   of the program's pre-registered-gate discipline.
3. It would be a Primera A model wearing a Superliga label. The honest
   statement is that the Superliga contributes 12 matches of history
   and no learnable structure of its own.

If the coordinator ever wants a cross-league transfer experiment, it
needs its own pre-registration outside this program's per-league gates
(a pooled cup-tie design across many super cups, not a 12-match league
build). Nothing of that is started here.

## Format rule (frozen for the record)

Two-legged Final, aggregate winner; level on aggregate → straight to
penalties (2025 evidence; no extra time in any payload). No away-goals
decider observed. This rule is frozen here so that any future revisit
does not have to re-derive it — but no future revisit is scheduled: the
competition adds 2 matches a year, so it will not reach a gateable
sample (even 50 matches would need 25 years at this rate, and the
season-blocked structure would still give n=2 per season).

## What ships

Nothing. No engine, no fitted params, no predictions. The league is
complete as **0 PASS / 0 FAIL / 5 NOT BUILDABLE**.
