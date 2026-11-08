# FO-PremierLeague League Verdict — Faroe Islands Premier League (FotMob 250)

Date: 2026-11-10. Branch `build/fo-premier-league`. The true last
league in the local queue (0 remain after this one).

## Verdict: 0 PASS / 2 FAIL / 3 NOT BUILDABLE — league complete

| Candidate | Verdict | Headline |
|---|---|---|
| G-FO goals | FAIL | Dev pooled 1X2 LL 0.8080 / RPS 0.1633 beat climatology (1.0239 / 0.2426), but OU2.5 LL 0.6602 lost to climatology 0.6458. Virgin NOT read. |
| K-FO cards | FAIL | Gate Zero LL@3.5 0.6847 lost to base rate 0.6824 on dev. SHRINK passed its own dev gate (0.6810) but is moot per the frozen rule (Gate Zero fails dev ⇒ variants moot). Virgin NOT read. |
| S-FO shots on target | NOT BUILDABLE | Stats 0/810, shotmap 0/810. |
| C-FO corners | NOT BUILDABLE | Stats 0/810, no corner events. |
| T-FO total shots | NOT BUILDABLE | Stats 0/810, shotmap 0/810. |

Nothing ships. No engine joins the daily pipeline from this
league. The league is complete on this verdict: all buildable
candidates ran through their gates, and the not-buildable ones are
decided on payload evidence, not on sample size.

## Corpus (for the record)

810 index rows, seasons 2021–2026, 135/season; 809 played matches
after excluding the single awarded match 3822183 (2022-09-04,
official 0-3 AW vs played 3-1). 10 teams/season by FotMob id
(triple round robin, rounds 1–27); 13 distinct ids, 7 with spelling
variants, keyed by id. Goals 3.30/match pooled; unified yellows
3.94/match. Team traits reliable (GF r=0.876, GA r=0.928, YCF
r=0.869, YCA r=0.851, odd-vs-even-season split-half). Halves
constants frozen for presentation only: goals 1H share 0.441,
yellows 0.348 (per-team 1H shares are noise: true variance
≈0.0011). 2026, the virgin season, ran cold on goals (2.82/match,
OU2.5 0.541 vs dev 0.659) — observed at design level only, never
used for fitting or gating.

## Commits (branch `build/fo-premier-league`, local only, no push)

- `263c0e84` — Phase A: data + analysis.
- `4c162d84` — Prereg, frozen before any fitting.
- `c6dd5584` — Phase B: engines + dev walk-forward.
- Verdicts + virgin-not-read markers — the verdict commit on this
  branch (see `git log`).
