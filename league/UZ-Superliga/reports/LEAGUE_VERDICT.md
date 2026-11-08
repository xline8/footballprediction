# League verdict — UZ-Superliga (FotMob 540) — **0 PASS / 0 FAIL / 5 NOT BUILDABLE**

## What it is

The Uzbekistan Superliga is a real 16-team top flight — but the
warehouse holds exactly one season of it: **2026, 215 matches,
2026-02-27..2026-11-08, IN PROGRESS** (rounds 1–27 of 30; round 26
short one fixture, Bunyodkor Tashkent vs Neftchi Fargona; rounds 28–30
unplayed). There is no other season for this league id and no other
Uzbek league in the warehouse at all (540 is the only Uzbekistan id).
Zero complete seasons exist, so no season-blocked dev walk-forward and
no virgin window can be constructed. This league is thinner than the
AU-Championship precedent (one complete season, 0/0/5) — it has no
complete season at all.

## Verdict table

| Candidate | Dev | Virgin | Verdict |
|-----------|-----|--------|---------|
| G-UZ goals | No window (one partial season) | **Not read** — no virgin season exists | **NOT BUILDABLE** |
| S-UZ SOT | No target in any payload | **Not read** | **NOT BUILDABLE** |
| C-UZ corners | No target in any payload | **Not read** | **NOT BUILDABLE** |
| K-UZ cards | No target; referee blank 215/215 | **Not read** | **NOT BUILDABLE** |
| T-UZ total shots | No target in any payload | **Not read** | **NOT BUILDABLE** |

No arm passed or failed a gate, because no gate could be run. Nothing
was fitted, no engine was built, no predictions were issued, no halves
constants were frozen (X1–X9 all dropped — see `analysis/FEATURES.md`).
No `results_dev.csv` exists because no dev was scored; the virgin
not-read state is recorded in `reports/results_virgin.json`.

## Levels (the only target that exists)

2026 goals: 2.628/match (n=215, 565 goals) — a touch above J1 (2.55).
Home 1.391 / away 1.237 per match; HW/D/AW 41.4 / 23.3 / 35.3%;
Over 2.5 53.5%; BTTS 56.3% (J1: 47.0% / 50.4%). Split-half within 2026
(rounds 1–13 vs 14–27, n=16 teams): attack GF/match r=0.696 (real
trait), defence GA/match r=0.179 (weak). Strongest attack Neftchi
Fargona (2.35 GF/match); weakest Mashal Muborak (0.44).

## Payload-level data-quality notes

- Index flags (`has_stats`, `has_shotmap`, `has_period_splits`,
  `has_lineup` all False, 215/215) are right about substance (stats
  null, shotmap empty, no structured splits, no lineups) but for the
  wrong reason in one case: the shotmap key is present in all 215
  payloads as an empty skeleton (`{shots: [], Periods: {All: []}}`).
- The flags also understate the data in one place: `matchFacts.events`
  is non-empty in 99/215 payloads (rounds 10 and 14–27, the
  live-coverage era). Those 99 carry a Half event at minute 45 whose
  scores are the HT score (99/99 consistent) and Goal events whose
  count equals the FT goal total (99/99). HT share of goals 0.4588
  (128/279) — descriptive only, late-season coverage, NOT frozen.
- Card events are sparse (29 in 99 matches) and the referee field is
  blank 215/215: cards are not a usable target.
- `coverageLevel` is `lower` in 215/215 payloads. Summer break between
  rounds 11 and 12 (2026-05-04 → 2026-07-16) is a calendar gap, not
  missing data.

## Revisit condition

Earliest gateable build: dev on 2026 (once complete) + 2027, virgin
2028 — needs a fresh prereg, nothing scheduled. If FotMob coverage
improves (stats blocks appearing in later seasons), S/C/K/T become
re-assessable on the same revisit — verified from payloads, never from
the index flags.

## League complete

Worktree `~/workspace/wt-uz-superliga`, branch `build/uz-superliga`.
No push, no merge, `league/PROGRAM_STATUS.md` untouched.
