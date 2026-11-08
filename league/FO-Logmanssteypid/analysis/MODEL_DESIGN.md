# Step 4 — Model Design: FO-Logmanssteypid

## Feasibility matrix (payload-verified)

| Candidate | Target exists? | Dev window? | Virgin window? | Verdict |
|-----------|---------------|-------------|----------------|---------|
| G-FOL goals | Yes — scores 6/6 | **No** — 1 match/season; no team ratings estimable | **No** — 2026 is n=1 | **NOT BUILDABLE** |
| S-FOL SOT | No — stats 0/6, shotmap 0/6 | **No** | **No** — 2026 is n=1 | **NOT BUILDABLE** |
| C-FOL corners | No — stats 0/6 | **No** | **No** — 2026 is n=1 | **NOT BUILDABLE** |
| K-FOL cards | No — no events, no stats, no referee (0/6 on all three) | **No** | **No** — 2026 is n=1 | **NOT BUILDABLE** |
| T-FOL total shots | No — stats 0/6, shotmap empty | **No** | **No** — 2026 is n=1 | **NOT BUILDABLE** |

No candidate reaches the design stage. No arms are registered, no
primary line is chosen, no engine is built. The prereg
(`prereg/PREREG_FO_LOGMANSSTEYPID.md`) records this feasibility
verdict itself, committed before any fitting — and no fitting is done
at all.

## Why "just fit goals anyway" fails — the gate arithmetic

The program's gate needs a season-blocked walk-forward dev and a
virgin read. Suppose, against the design, one tried dev = 2021–2025
(5 matches) and virgin = 2026 (1 match):

- **Dev is not a walk-forward.** A Dixon-Coles fit needs attack/defence
  ratings per team. Each dev season contributes exactly one final
  between two teams that play no other Løgmanssteypið match that
  season; the ratings for a season's teams would be fitted on the very
  1 match being predicted (in-sample), or borrowed from elsewhere.
  There is no "trailing" inside the competition.
- **Virgin calibration is meaningless at n=1.** At the OU 2.5 line the
  base rate over all 6 matches is 1/6 = 16.7%; the binomial SE at n=1
  is √(.167×.833/1) ≈ 37pp, and at p=0.5 it is 50pp. The clean-PASS
  rule (|breach| ≤ 1pp) is ~1/37 of one SE: the single virgin match's
  goal count alone decides the observed rate (0% or 100% at the
  Over/Under line), and flips any verdict. A "PASS" here would be a
  coin flip with a gate stamp on it.
- **Pooling does not rescue it.** Even treating all 6 matches as one
  sample, the OU 2.5 SE is √(.167×.833/6) ≈ 15.2pp — still 15× the
  clean threshold. No calibration claim at the program's precision is
  possible from this competition, in any window split.

## The borrowed-ratings alternative — considered and rejected

The only conceivable model is not a Løgmanssteypið model at all: take
the Faroese Premier League's team ratings (warehouse league_id **250**
— 135 matches per season, 2021–2026, 810 rows) and apply them to the
one cup final a year, with a home advantage. That design is rejected
for this program, not for lack of imagination:

1. It cannot pass the program's gates: there is no in-competition dev
   window to fit or validate the Premier-League-to-cup-final transfer
   (the transfer itself — one-off final, nominal home team, penalties
   after a draw — is exactly what would need validating), and no
   virgin window to read.
2. It would ship 1 prediction a year with no validation — the opposite
   of the program's pre-registered-gate discipline.
3. It would be a Premier League model wearing a cup label. The honest
   statement is that the Løgmanssteypið contributes 6 matches of
   history and no learnable structure of its own.

If the coordinator ever wants a cross-league transfer experiment, it
needs its own pre-registration outside this program's per-league gates
(a pooled cup-final design across many cups, not a 6-match league
build). Nothing of that is started here. Note the Premier League
itself is a separate programme matter: it is not part of this brief,
and this build does not touch it.

## Format rule (frozen for the record)

Single-match Final, one per calendar year (Sep–Dec); draw at 90
minutes → straight to penalties (2021, 2023, 2024 evidence; no extra
time in any payload). This rule is frozen here so that any future
revisit does not have to re-derive it — but no future revisit is
scheduled: the competition adds 1 match a year, so it will not reach
a gateable sample (even 50 matches would need 44 more years at this
rate, and the season-blocked structure would still give n=1 per
season).

## What ships

Nothing. No engine, no fitted params, no predictions. The league is
complete as **0 PASS / 0 FAIL / 5 NOT BUILDABLE**.
