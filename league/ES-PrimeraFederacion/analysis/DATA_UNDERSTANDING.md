# Phase 1 — Data Understanding: FotMob Spain Primera Federación Warehouse

Corpus: `data_enrichment/fotmob_world/Spain/Primera Federación/` —
4,081 full matchDetails JSONs (league_id 8968), seasons 2021/2022 →
2026/2027. Numbers from the built CSV
(`league/ES-PrimeraFederacion/data/build_data.py`) and
`analysis/eda_compute.py` → `eda_numbers.json`, every headline number
independently re-counted from the raw payloads by a second script
before any design quantity was frozen.

## 0. Integrity headline

- 4,081 index rows = 4,081 files = 4,081 built match rows; match ids
  unique; every match finished, 0 cancelled; every `scoreStr` parses.
- Index depth flags say it plainly and the payloads confirm it:
  `has_stats` 0/4,081, `has_shotmap` 0/4,081, `has_period_splits`
  0/4,081. A full payload sweep (all 4,081 JSONs) finds `content.stats`
  empty in 4,081/4,081 and shotmap `shots` empty in 4,081/4,081.
  **This is a scores-only league — no stats, no shotmap, no period
  splits, no xG, in any season.** The index flags were verified from
  payloads, not trusted (the program's has_stats false-positive
  lesson).

## 1. League format — 2 groups of 20 + cross-group play-offs

40 teams in two groups of 20, double round-robin **within** each
group: rounds 1–38 = **760 regular matches** per season (20 per
round across both groups). The regular-season fixture graph splits
into exactly two 20-team connected components every season
(recomputed from the raw payloads; zero cross-group regular
matches; group sizes 20/20, no overlap). There is no group label in
the payload (`general` carries no group field); groups are recovered
from the fixture graph and stored as `group_home` / `group_away`
in the CSV (labels are within-season only — group 1 in one season
need not correspond to group 1 in the next).

Then the promotion play-offs (2nd–5th of each group): semi-finals
`matchRound = '1/2'` and finals `matchRound = 'final'`. The ties are
**cross-group by design** — verified on the payloads: in 2022/2023
all 14 play-off matches pair teams from different groups; the only
within-group play-off match in the whole corpus is the 2021/2022
final Villarreal B vs Gimnastic. The play-off shape by season:

| Season | Semis | Finals | Total | Shape |
|---|---|---|---|---|
| 2021/2022 | 4 | 3 | 7 | single-leg ties (incl. champions final Racing Santander–FC Andorra, 3 Jun, before the semis) |
| 2022/2023 | 8 | 6 | 14 | two-legged (4 group-promotion-final legs + 2 champions-final legs between the group winners) |
| 2023/2024 | 8 | 6 | 14 | two-legged, as above |
| 2024/2025 | 8 | 6 | 14 | two-legged, as above |
| 2025/2026 | 8 | 4 | 12 | two-legged group finals only — **no champions-final rows in the warehouse** (format change or gap; season otherwise complete, last match 20 Jun 2026) |

Play-off matches are 90-minute (occasionally extra-time, §3)
league-format matches between Primera Federación clubs, so —
mirroring the ENGCH / ES-LaLiga2 decision — they are **included as
ordinary rows** with `phase='playoff'` recorded; no phase feature is
used anywhere. They are also the league's only cross-group link,
which matters for the goals fit (MODEL_DESIGN §1).

**Churn — the defining structural fact (by team_id).** Every season
exactly **14 of the 40 clubs (35%) are new**: 4 relegated from
LaLiga2 + 10 promoted from Segunda Federación replace 4 promoted +
10 relegated. 91 distinct clubs (team ids) appear across the corpus.
Only three Spanish leagues are in the warehouse — LaLiga (id 87),
LaLiga2 (id 140), Primera Federación (id 8968) — so the upper
adjacent tier is directly measurable while the lower one (Segunda
Federación, 4th tier) is not in the warehouse at all: a promoted
club is identified as a new team-id absent from LaLiga2 in the prior
season (EDA F4). Mover entry strength (dev entry seasons
2022/2023–2024/2025): clubs arriving from LaLiga2 enter at GD
**+0.231/match** (GF 1.240, GA 1.008 vs league mu 1.158), clubs
arriving from below at **−0.065** (GF 1.104, GA 1.169). The step down
from LaLiga2 is defence-led (GA −0.150, GF only +0.081) — the same
shape as ES-LaLiga2's step down from LaLiga (+0.251, GA −0.171,
GF +0.080); the step up from the fourth tier is barely below
average, far weaker than ES-LaLiga2's step up from this league
(−0.136).

**Team-identity quirk (measured, load-bearing).** 14 of the 91 FotMob
team ids carry **more than one name spelling** across seasons —
accents dropped in some payloads (`Logrones`/`Logroñés`,
`Merida`/`Mérida`, `Alcorcon`/`Alcorcón`, `Hercules`/`Hércules`,
`Deportivo La Coruna`/`Deportivo La Coruña`, …)
plus full renames on the same id (`Barcelona B` / `Barca Atletic`,
id 161774; `Celta Vigo B` / `Celta Fortuna`, id 161743;
`Athletic Club B` / `Athletic Bilbao B`, id 161850;
`Atletico Madrid B` / `Atletico Madrileno`, id 161759, which carries
four spellings). (An early probe counted 12 — it kept only the last
spelling per team per season; the full CSV recount is 14.) Raw-name set arithmetic therefore invents phantom
clubs. The truth, by team_id: exactly 40 per season, 91 overall,
14 entries per season. Spellings map 1:1 onto ids with no collisions
— except the renames above, which no accent-normalisation can bridge
— so **all state in this league is keyed on team_id; names are
display only**, and the X2 mover membership in the engine is keyed
on team_id recovered from warehouse payloads, not on names
(MODEL_DESIGN §2; the EDA name-keyed mover lists were verified to
match the id-keyed lists exactly).

Calendar: autumn–spring (Aug–Jun, play-offs into June); 2026/2027 is
partial (220 matches, rounds 1–11, through 2026-11-08) and is
reserved as the confirmatory window.

**Virgin-window choice (frozen here, before fitting):** 2025/2026 is
complete in the warehouse (760 regular + 12 play-offs, last match
20 Jun 2026; the 2 missing champions-final legs are noted above, not
imputed). We freeze **virgin = 2025/2026 (complete, n=772)**, with
dev = 2021/2022 seed + 2022/2023–2024/2025 evaluation (pooled
n=2,322) and partial 2026/2027 reserved un-read as confirmatory.
One era fact shapes the whole design: there is no stats/shotmap era
at all (§2), so only the goals candidate is buildable.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | Referee text | Events | Goal events complete |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 767 | 0% | 0% | 0% | 0% | 90.2% | 97.9% |
| 2022/2023 | 774 | 0% | 0% | 0% | 0% | 90.8% | 100% |
| 2023/2024 | 774 | 0% | 0% | 0% | 0% | 90.8% | 100% |
| 2024/2025 | 774 | 0% | 0% | 0% | 0% | 92.4% | 100% |
| 2025/2026 (virgin) | 772 | 0% | 0% | 0% | 0% | 90.9% | 100% |
| 2026/2027 (partial) | 220 | 0% | 0% | 0% | 0% | 94.5% | 100% |

- **No stats era exists.** `content.stats` is `{}` in every payload;
  there is no `Periods` block, no `expected_goals`, no `corners`,
  no `total_shots`, nothing. The SOT / corners / cards / total-shots
  candidates are not buildable on availability (FEATURES) — this is
  a property of the league's FotMob coverage (`coverageLevel: lower`
  in all 4,081 payloads), not a gap in the pull.
- **Referee: present as an object, empty as data.** `matchFacts.
  infoBox.Referee` exists in all 4,081 payloads but its `text` is
  `''` in 4,081/4,081 (full sweep). Referee coverage is 0% in the
  only sense that matters (a name). X8 is dropped twice over: no
  referee data and no cards target.
- **Events are the only per-match content beyond the score** — and
  they are thin. Event types across the corpus: Goal 9,500, Half
  7,455, Card 995. Events are present in ~90–92% of matches per
  season; the 358 zero-event matches are all 0–0 draws (goal-event
  count equals the score total in every match except the 16 awarded
  matches of 2021/2022). Goal events carry a `time` in every case,
  so first-half goals are recoverable from events for 4,065/4,081
  matches (99.6%) — the only halves source in the league, used for
  the frozen goals constant only (EDA F3).
- **Cards: the event feed is a sparse subset, not a target.** Card
  events total 995 across 4,081 matches (0.22/match; 0.207–0.285 by
  season), present in only 18.1–24.7% of matches. A real third-tier
  Spanish season runs ~4–5 cards/match; the feed carries roughly one
  twentieth of that, with no stats feed to cross-check or repair it.
  No cards model is built (MODEL_DESIGN §3).

**Stat-key inventory (All period):** there is none. No modelled key
exists in any payload of any season.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth; parses in 4,081/4,081 |
| HT score | goal events `time ≤ 45` | complete (event count == score total) in 4,065/4,081; the 16 exceptions are awarded matches with no events |
| SOT / corners / total shots / cards | — | do not exist in this league's payloads |
| Team xG | — | does not exist in this league's payloads |
| Referee | `infoBox.Referee.text` | empty string in 4,081/4,081 |

**Awarded matches (17).** 16 in 2021/2022 — 15 involving
Extremadura UD, which folded mid-season (its remaining fixtures were
awarded 2–0 to the opponent, or 3–0 in two cases), plus one unrelated
award, DUX Internacional–Unionistas 3–0. One more in 2023/2024
(Sestao–Rayo Majadahonda 3–0).
Awarded matches are included as ordinary rows: they are official
results, they are 0.4% of the corpus, and the 16 Extremadura
walkovers sit in the seed season only — Extremadura exits the league,
so no ongoing rating pollution. Excluding them would break round
completeness for no modelling gain.

**Extra time (9 matches).** All 9 are play-off matches whose
`scoreStr` is the after-extra-time score (e.g. Deportivo–Albacete
1–2 AET, 11 Jun 2022). They are included as ordinary rows, as-is:
9/4,081 = 0.2% of the corpus, and excluding them would break
play-off completeness. The goals model predicts 90-minute outcomes;
the ET goals in these 9 training rows are recorded here rather than
corrected away.

**Penalties.** `whoLostOnPenalties` is never set in the corpus (0
matches) — no play-off tie in the warehouse was decided on
penalties; the AET scores above are the final scores.
