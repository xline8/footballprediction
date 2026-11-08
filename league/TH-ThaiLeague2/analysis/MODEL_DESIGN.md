# Step 6 — Model Design: TH-ThaiLeague2

Feasibility matrix (target exists in the data AND a valid virgin window
contains it):

| Candidate | Target in data? | In virgin 2025/2026? | Buildable |
|---|---|---|---|
| Goals | Yes — score, all eras | Yes (306 regular) | **YES** |
| Cards | Yes — event-unified yellows, all eras | Yes (306 regular) | **YES** |
| SOT | **No** — stats feed null in 681/681 payloads | No | **NO** |
| Corners | **No** — stats feed null in 681/681 payloads | No | **NO** |
| Total shots | **No** — stats feed null in 681/681 payloads | No | **NO** |

The three not-buildable candidates get verdict documents recording the
evidence (Step 1 / EDA); no prereg, no fitting, no virgin read for them.
This follows the programme rule that stats markets build only where the
target exists — the warehouse index's `has_stats` flag (a key-presence
test) claimed otherwise and is wrong for this league (Step 1).

Windows frozen in PREPROCESSING: warm-up = first 90 regular matches of
2024/2025; dev scored = remaining 183 regular matches (cards 182 — one
row has no event feed); virgin = 2025/2026 regular (306). Play-off ties
excluded everywhere. Calibration = actual − predicted. Gate legs
identical in form to the parent build (dev gate vs baselines; virgin LL
leg + calibration leg |breach| ≤ 1pp clean, ≤ 1 SE provisional, else
FAIL; both-pass → lower virgin LL ships; Gate Zero dev failure ⇒
candidate FAILS, virgin NOT read).

## G-TH2 (goals) — Dixon-Coles, goals-only (X1 dropped)

- Reference: production `model_v2.py` DC pattern as frozen in the parent
  TH goals prereg (hl=270, 14 sweeps, damping 0.7, +0.25 smoothing, rho
  grid, expanding fit on matches strictly before each scored date —
  date-grouped within the dev season, since only one pre-virgin season
  exists).
- Arms: **Gate Zero**; **SHRINK** (sanctioned G-J2-lesson arm: ratings of
  teams with <6 prior in-league matches shrunk a,d *= n/6; motivated by
  the X2 mover measurement, n=3 relegated clubs with mixed gaps).
  Note: under date-grouped expanding fits inside one season, teams pass
  through the 1–5 prior-match band early in the scored block (unlike the
  season-blocked RU1 case where SHRINK never bit), so the arm is live.
- Dev: warm-up 90, scored 183. Virgin: 2025/2026 regular (306).
  Primary metrics 1X2 LL/RPS + OU2.5 LL vs climatology (expanding,
  prior-matches-only). Halves via frozen goals constant 0.4249.

## K-TH2 (cards) — production cards pattern, event-unified target

- Target: total **event-unified yellows** (frozen in Step 1/2: the stats
  feed is null in every payload, so no stats target exists; the event
  feed carries plain yellows in every era — the parent league's era flip
  does not occur here). Primary line **4.5** (scored-dev over-rate
  0.437). Ladder 3.5/4.5/5.5.
- Arms: **Gate Zero only** (X8 dropped — not measurable, FEATURES).
  Architecture as the parent TH cards prereg (decayed team yellow
  ratings, NB count, naive trailing-10 ensemble), on the event target.
- Warm-up 90 (state updates, never scored); dev scored 182; virgin 306.
  Baselines: league base rate; naive trailing-10. Halves constant 0.3322.

## Not buildable: S-TH2 / C-TH2 / T-TH2

No target exists in any season, so there is nothing to fit and no gate
to run. Each gets a `reports/<X>_TH2_VERDICT.md` marked NOT BUILDABLE
with the Step 1 evidence. If FotMob ever populates this league's stats
feed, these candidates would need a fresh six-step pass over the new
data — nothing in this build pre-registers them.
