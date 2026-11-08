# Step 3 — EDA: RS-SuperLiga

All numbers from `analysis/eda.py` → `eda_summary.json` / `inventory_summary.json`
(run on `data/rs_matches.csv` + `data/rs_team_matches.csv` + raw JSONs for inventory only,
dev + virgin; the 2026/2027 reserve season is excluded from every computation).
Charts in `analysis/charts/`. Every number below cites its JSON key.

## F1 — Levels per season (per match)

| Season | Goals | Home G | Away G | SOT | Corners | Total shots | Yellows (events) | Yellows (stats) | Over-2.5 rate |
|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.563 | 1.357 | 1.207 | — | — | — | 0.100 | — | 0.500 |
| 2022/2023 | 2.430 | 1.357 | 1.073 | — | — | — | 0.120 | — | 0.447 |
| 2023/2024 | 2.770 | 1.544 | 1.226 | — | — | — | 0.091 | — | 0.544 |
| 2024/2025 | 2.882 | 1.527 | 1.355 | — | — | — | 0.041 | — | 0.564 |
| 2025/2026 (virgin, inventory) | 2.662 | 1.493 | 1.169 | 8.831 | 9.003 | 25.084 | 4.662 | 4.230 | 0.500 |

Source: `eda_summary.json: levels`. "—" = the feed does not exist that season, not zero.

- Goals swing 2.43–2.88 across dev seasons — season-level noise is large relative to the
  virgin n (296). The virgin (2.662) sits mid-range, not at an extreme.
- Home advantage is present every season (home 1.357–1.544 vs away 1.073–1.355) and larger
  than FI's unstable home edge.
- Dev pooled over-2.5 rate 0.513, median total goals 3.0 (`eda_summary.json: dev_medians`).
- The stats columns are virgin-only inventory: SOT 8.831, corners 9.003, total shots 25.084
  are single-season levels with no dev series behind them. They describe the virgin feed;
  they are not baselines for any gate.
- Event yellows in dev (0.041–0.120) vs virgin (4.662) is a ~40–100x break: the dev feed
  does not measure yellow cards at all (see F6).

## F2 — Team-trait reliability (split-half, career-pooled over dev, 23 teams)

| Trait | r | n teams | Verdict |
|---|---|---|---|
| goals for | 0.906 | 23 | SIGNAL — strong |
| event yellows for | 0.060 | 23 | NO SIGNAL — and the feed is YellowRed-only (see F6) |
| SOT for | null | 0 | NOT MEASURABLE — no dev data |
| corners for | null | 0 | NOT MEASURABLE — no dev data |
| total shots for | null | 0 | NOT MEASURABLE — no dev data |
| possession | null | 0 | NOT MEASURABLE — no dev data |
| touches_opp_box for | null | 0 | NOT MEASURABLE — no dev data |
| big_chance for | null | 0 | NOT MEASURABLE — no dev data |
| fouls for | null | 0 | NOT MEASURABLE — no dev data |
| keeper saves for | null | 0 | NOT MEASURABLE — no dev data |

Source: `eda_summary.json: traits_dev`. The split-half method is FI's (odd/even appearances
pooled over the seasons, teams with ≥8 matches per half).

- Goals is the only trait that exists and is reliable in dev — and it is very reliable:
  split-half r = 0.906, and season-to-season correlations of team goals-for per match are
  0.850 / 0.888 / 0.858 across the three consecutive dev-season pairs (n = 14 / 14 / 13 teams,
  `eda_summary.json: traits_season_to_season_goals_for_dev`). Team attacking strength persists
  strongly across seasons in this league. That is the entire evidential basis for G-RS.
- Every stats trait is null because the stats feed does not exist in dev. No virgin split-half
  was computed for these traits: measuring reliability on the virgin to adopt a feature would
  be virgin-driven feature selection, which the task forbids. The nulls are the finding.
- The event-yellows trait (r = 0.060) is computed on the broken YellowRed-only feed and is
  reported only to document the break — a near-zero correlation on ~0.09 cards/match is what
  a missing feed looks like, not a measured team trait.

## F3 — Halves shares (the frozen-constant question)

| Share | Value | n matches | Source |
|---|---|---|---|
| Goals 1H (league-only dev) | **0.4606** | 1,087 | event times, dev, excl. qualification + awarded match |
| Goals 1H (all dev, excl. awarded) | 0.4605 | 1,095 | event times, dev |
| Goals 1H (all dev, incl. awarded) | 0.4617 | 1,096 | event times, dev — reported for transparency |
| Yellows 1H (dev) | 0.1238 | 101 | event times, dev — NOT usable (see below) |
| SOT 1H | null | 0 | no dev splits — NOT borrowed from virgin |
| Corners 1H | null | 0 | no dev splits — NOT borrowed from virgin |
| Total shots 1H | null | 0 | no dev splits — NOT borrowed from virgin |
| Yellow cards 1H (splits) | null | 0 | no dev splits — NOT borrowed from virgin |

Source: `eda_summary.json: halves_goals_dev_league_only`, `halves_goals_dev`,
`halves_goals_dev_incl_awarded`, `halves_yellows_dev`, `halves_splits_dev`.

- The goals constant 0.4606 (1,449 1H goals / 3,146 FT goals over league-member dev matches
  with events) is the only frozen halves constant this league produces. Observed share variance
  0.11159 vs binomial 0.08584 (excess +0.02575) — same order as FI's excess (+0.0267); per-match
  half shares are noise, the constant is the only halves mechanism the program allows, and it
  is presentation only.
- The awarded match 4271663 moves the share by +0.0012 when included; the qualification ties
  move it by −0.0001. Both exclusions are documented, neither matters numerically — the
  exclusions are a matter of correctness (cross-tier rows, FT score vs events), not tuning.
- Yellows 1H (0.1238) is computed on 13 first-half cards out of 105 dev event cards total
  (`eda_summary.json: halves_yellows_dev_note`). It is not a constant: the underlying feed is
  broken, the n is trivial, and there is no cards product. It is reported so the absence is
  auditable.
- SOT / corners / total shots / yellows split shares are null. The virgin splits exist and
  would give numbers, but using them as frozen constants would be fitting the presentation
  layer to the virgin — forbidden. No constant is frozen for S/C/K/T.

## F4 — Entrants (X2 measurement, dev only)

11 entrant transitions were first listed by plain absence-from-previous-season; 2 of them are
cross-tier qualification opponents (FK Graficar, Indjija — 2 matches each, never regular members)
and are removed by the regular-phase rule (see DATA_UNDERSTANDING.md). Genuine entrants
(`eda_summary.json: x2_entrants`): Javor + FK Mladost Novi Sad (2022/2023), FK IMT Beograd +
Železničar Pančevo (2023/2024), OFK Beograd + Tekstilac Odzaci + Jedinstvo Ub (2024/2025),
Javor (returning) + FK Radnik Surdulica (2025/2026, inventory only — performance not measured).

Dev transitions (n = 7, `eda_summary.json: x2_entrant_gf_ga_diff_vs_league_team_mean_dev`):
first-season GF/GA per match vs that season's league team mean: **GF −0.326, GA +0.242** —
a stronger promoted-team pattern than FI's (−0.210 / +0.159) and the same sign as J1's F4.
SIGNAL for a goals arm. RS is tier 1: entrants are promoted clubs, identified by absence from
the previous season's regular-phase teams (no tier-2 corpus is built in-system; the offset
itself is estimated inside the fit from completed transitions only).

## F5 — Dev-era distributions (primary-line evidence)

- Goals: dev pooled over-2.5 rate 0.513, median 3.0 (`eda_summary.json: dev_medians`).
  Primary line is OU 2.5 (frozen in the prereg), as in every goals candidate.
- SOT / corners / total shots / yellows: **no dev medians, no dev over-rates, no primary line**
  (`eda_summary.json: dev_medians` — all null). No line can be set from dev for S/C/K/T,
  because no dev data exists for their targets. This is a feasibility fact, not a choice.

## F6 — Cards artefact (pre-freeze check — and why it does not rescue K-RS)

Stats vs events yellows, virgin only (the only season where both exist):
exact agreement 72.6%, mean events 4.662 vs mean stats 4.230, mean stats − events = −0.432/match,
81 matches ev > stats, 0 matches stats > ev (`eda_summary.json: cards_stats_vs_events`).
The stats feed systematically undercounts yellows against events — the FI precedent for
preferring the event target. But here the event target is itself broken in dev (YellowRed-only,
0.041–0.120/match; no plain Yellow Card events in 1,192 dev matches). There is no cards target
with the same meaning in dev and virgin, so no target is frozen and K-RS is not built.
The virgin-only check is recorded for the record.

## F7 — Reference points

Goals level (2.43–2.88 dev) sits in the normal European band, below FI's high 2025 (3.29);
the virgin (2.662) is unremarkable. Home advantage is stable and material. The one reliable
team trait in the entire corpus is goals-for (r = 0.906 split-half, 0.85–0.89 season-to-season).
Everything else a J1-template model would want — SOT, corners, shots, touches, fouls, saves,
referee, xG, shotmap — exists only in the virgin season or nowhere, and therefore cannot be
gated. The virgin is a normal season on goals and a rich season on feeds; the gates decide
for G-RS alone.
