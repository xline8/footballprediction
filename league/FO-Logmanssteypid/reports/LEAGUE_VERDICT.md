# League verdict — FO-Logmanssteypid (FotMob 9523) — **0 PASS / 0 FAIL / 5 NOT BUILDABLE**

## What it is

The Faroe Islands Løgmanssteypið is a cup, not a league: 6 matches
total, exactly 1 per season, 2021–2026 — one single-match Cup Final
per year, 6 distinct clubs, no club playing more than 1 match in a
season. Format frozen from payloads: single-match Final (Sep–Dec);
draw at 90 minutes → straight to penalties (2021 Pen 3–4, 2023
Pen 3–5, 2024 Pen 3–4; no extra time in any payload). It is
scores-only in the strongest sense: no stats, no shotmap shots, no
events of any kind, no lineups, no referee — in any of the 6 payloads.

## Verdict table

| Candidate | Dev | Virgin | Verdict |
|-----------|-----|--------|---------|
| G-FOL goals | No window (1/season) | **Not read** (n=1) | **NOT BUILDABLE** |
| S-FOL SOT | No window; no target in any payload | **Not read** | **NOT BUILDABLE** |
| C-FOL corners | No window; no target in any payload | **Not read** | **NOT BUILDABLE** |
| K-FOL cards | No window; no target, no referee 0/6 | **Not read** | **NOT BUILDABLE** |
| T-FOL total shots | No window; no target in any payload | **Not read** | **NOT BUILDABLE** |

No arm passed or failed a gate, because no gate could be run: the
virgin (2026, n=1) has a calibration SE of ≈37pp at OU 2.5 (50pp at
p=0.5) against a 1pp clean-PASS threshold, and pooled n=6 still gives
≈15.2pp. A verdict there would be decided by a single goal in a
single match. Nothing was fitted, no engine was built, no predictions
were issued, no halves constants were frozen (none exist — no 1H
splits anywhere), and X1–X9 are all dropped (see
`analysis/FEATURES.md`).

## Payload-level data-quality notes

- The events feed is empty in all 6 payloads (0 events total) — the
  competition's FotMob coverage is score-only at `coverageLevel:
  "lower"` in every payload. Not even goal minutes exist, so no half
  split of any kind can be derived.
- The index flags agree with the payloads here (`has_stats: False`,
  `has_shotmap: False` on 6/6) — the flag class that lied for
  CO-Superliga does not lie for this competition.
- The brief's scouting note that index team names were NULL is wrong:
  `home`/`away` are populated on all 6 index rows and agree with the
  payloads. Team-name spelling is accent-inconsistent across years
  ("B36 Torshavn" vs "B36 Tórshavn"; "Vikingur" vs "Víkingur") —
  distinct clubs are 6 after normalisation, 8 raw.

## Note on the parent league

The only conceivable model would borrow Faroese Premier League ratings
(warehouse league_id **250** — 135 matches/season, 810 rows,
2021–2026) and apply them to the one cup final a year. That transfer
cannot be validated in-competition (no dev, no virgin), so it is
rejected for this program and not built. A pooled cross-cup design
would need a fresh preregistration outside the per-league gates; none
is scheduled — at 1 match/year this competition will not reach a
gateable sample.

## League complete

**FO-Logmanssteypid is complete: 0 PASS / 0 FAIL / 5 NOT BUILDABLE.**
Nothing joins the daily pipeline. `league/PROGRAM_STATUS.md` not
touched (coordinator owns it).
