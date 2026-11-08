# Verdict — K-J2 (J2 cards model)

Date: 2026-11-09. Branch `build/k-j2`. Pre-registration:
`league/J2/prereg/PREREG_K_J2.md` (commit `79d284d`, frozen before
any fitting). Engine: `league/J2/engine/cards/k_j2.py` (J2's own
engine, seeded from the production `model_cards.py` pattern).
Implementation by Codex (gpt-5.6-luna) under coordinator brief;
two implementer bugs were caught and fixed in verification (§4);
verification is independent (§4).

## 1. Dev results (walk-forward, sequential by date, expanding; 2021–2024, n=1,764 scored, Feb 2021 warm-up excluded)

NB size from the prereg MoM route on scored dev: **r = 82.32**.

| Arm / baseline | LL@2.5 pooled | LL@3.5 pooled |
|---|---|---|
| Gate Zero | 0.6564 | **0.4623** |
| X8 (referee) | 0.6564 | 0.4623 |
| League base rate | 0.6668 | 0.4754 |
| Naive trailing-10 | **0.6554** | 0.4630 |

Per season, LL@2.5:

| Season | n | Gate Zero / X8 | Base rate | Naive t-10 |
|---|---|---|---|---|
| 2021 | 451 | 0.5777 | **0.5657** | 0.5771 |
| 2022 | 465 | **0.6358** | 0.6360 | 0.6419 |
| 2023 | 465 | 0.7198 | 0.7668 | **0.6996** |
| 2024 | 383 | **0.6968** | 0.7018 | 0.7101 |

X8's predictions are **identical to Gate Zero's on all 1,764
scored matches** (fallback count 1,764/1,764) — see the
operational check (§3): there is no referee identity for any J2
match in the warehouse, so the covariate never activates. X8 as
run is a Gate Zero clone, not a referee model, and is reported
as such.

## 2. Gate legs

Dev gate — pooled dev LL@2.5 beats BOTH baselines (league base
rate; naive trailing-10), else arm dead, no virgin read:

- vs base rate: **PASS** both arms (0.6564 < 0.6668).
- vs naive trailing-10: **FAIL** both arms (0.6564 > 0.6554,
  margin +0.0010).

**Both arms are dead at the dev gate.** Per the prereg, the
virgin window was **not read**: no virgin predictions were
generated (`league/J2/predictions/` holds no K-J2 file), season
2025 remains untouched by this candidate, and the virgin legs
(i)–(ii) are moot. Leg (iii) for the record: Gate Zero beats
both baselines in only **2 of 4** dev seasons (2022, 2024), so
it would not have been both-pass-eligible anyway.

**Shipped arm: none. Verdict: FAIL.**

Why the model loses (diagnosed from the per-season table, not
assumed): the failure is concentrated in 2023, when the J2
yellow level jumped (season mean 2.06 → 2.66). The naive
trailing-10 — a plain mean of each team's last 10 match totals —
re-prices to the new regime within weeks; the decayed ratings
(HL 270 days, the frozen production pattern) carry the old
regime for months, and the expanding base rate is worst of all
that year (0.7668). In the stable seasons the ratings win
(2022, 2024, and at the 3.5 line pooled the model is in fact
best) — but the gate is at 2.5, pooled, against both baselines,
and it is binding. The events-based J2 target itself is not the
problem: coverage is 100% in every season and the model beats
the base rate pooled and in 3 of 4 seasons.

## 3. Operational check — pre-match referee availability (prereg §9)

**What the data proves.** The FEATURES X8 source field,
`content.matchFacts.infoBox.Referee.text`, is **empty for every
J2 match in the warehouse: 0/2,318** — 2021: 0/462, 2022: 0/465,
2023: 0/465, 2024: 0/383, 2025: 0/383, 2026-2027: 0/160
(`league/J2/engine/cards/referee_table.csv`, one row per match,
verified against the CSV match-id set). This is not a parser
artefact: the identical extraction path finds referee names in
the same warehouse for J1 (2021: 216/380, 2022: 194/306, 2023:
165/306, 2024: 217/380, 2025: 165/380) and even for recent J3
(2025: 31/383; 2026-2027: 153/160, against 0 in J3 2021–2024).
FotMob simply does not publish a referee for J2 fixtures in this
corpus — not post-match in the archived payload, and therefore
not pre-match through this pipeline either. A direct
consequence for the program's evidence base: the F8 referee
trait (split-half r = 0.646 pooled, 0.649 on the "J1+J2"
recheck) was in practice measured on the matches where the
field exists — effectively J1. It was never measurable for J2.

**What the data cannot prove.** Whether the J.League or any
other external source publishes J2 referee appointments before
kickoff. This build checked no external source and claims
nothing about one.

**Operating rule.** The design's own rule stands and is, for
J2, the whole story: a fixture whose referee is not known falls
back to Gate Zero; referees are never imputed. For J2 that
fallback covers 100% of fixtures, so **X8 is inactive by
construction** — if K-J2 is ever revived, the referee arm needs
a referee source that actually carries J2 appointments, named
in a new pre-registration, before it can be anything other than
a clone.

## 4. Verification (independent of the implementer)

- The coordinator re-ran the whole dev harness using the
  **production `model_cards.CardsState` class itself** on the
  J2 data (with only the engine's zero-mean guard added to
  `league_mu` — production's top-5 warm-up never produces a zero
  league mean, J2's cold start does): it reproduces the engine
  **exactly** (difference 0.00 on pooled LL@2.5/@3.5 for both
  arms and both baselines, and on the MoM NB r = 82.324625).
  Five engine predictions spot-checked by hand against that
  replay (2021-03-06, 2021-11-07, 2022-10-16, 2024-03-03,
  2024-12-07) match to 1e-6.
- Referee causality, tested on synthetic data through the
  engine's own `walk`: fallback below 8 strictly-prior matches,
  activation at exactly 8, a same-date second match for the same
  referee does **not** count toward that date's threshold, and a
  strict referee (6 yellows/match against a ~2 league mean)
  raises the total by exactly the clamped factor 1.40. (In the
  real data the path never fires — coverage is zero.)
- Virgin isolation: the 2025 load in the engine sits inside the
  `if any(gate.values())` branch only; the gate was False, the
  branch never ran, and no virgin predictions file exists. The
  referee table does include 2025 rows — identity/date/teams
  only, as prereg §4 explicitly provides; no 2025 yellows were
  scored or fitted anywhere.
- Determinism: a full re-run reproduces `dev_results.json`,
  `fitted_params.json`, and `referee_table.csv` byte-identically
  (md5 checked).
- Two implementer bugs were caught in verification and fixed
  before this verdict: (1) the naive baseline's team history
  deque was **unbounded** — it computed a trailing-*career* mean,
  not the prereg's trailing-10 (reported naive LL 0.6562; the
  true trailing-10 is stronger, 0.6554, so the fix widened the
  model's losing margin — the gate outcome is unchanged);
  (2) the excluded-season constant read `"2026/2027"` while the
  CSV label is `"2026-2027"` — inert for fitting (every load
  filters seasons explicitly) but fixed, and referee extraction
  was made independent of that filter so the table stays
  complete over all 2,318 matches.
- Codex also generated a stub verdict from inside the engine;
  it has been replaced by this document. Its run otherwise
  followed the brief, including not reading the virgin window.

## 5. What would have to change (for the record, not done)

Nothing here is a tuning suggestion to apply silently. The
honest reading: on J2's events-based yellows, the production
cards pattern prices team card traits well in stable regimes
but adapts more slowly than a trailing-10 mean when the league
level jumps, and 2023 was exactly such a jump. Any revival
needs a new pre-registration (e.g. a faster-adapting level
component, with the mechanism named in advance) — and, for the
referee arm, a J2 referee source that exists. Season 2025 is
still virgin and available for exactly one such future read.
