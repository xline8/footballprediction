# Step 3 — EDA: BG-FirstLeague

Computed by `analysis/eda_compute.py` → `analysis/eda_numbers.json`
(no fitting). Headline levels independently recomputed from the raw
JSONs by a second path — identical to 4 decimal places.

## Levels (pooled)

| Market | Pre-virgin 2021/22–2024/25 (n=1,081) | Scored dev 2022/23–2024/25 (n=859) |
|---|---|---|
| Goals / match | 2.414 | 2.405 |
| OU2.5 over-rate | 0.434 | 0.435 |
| Home win / draw / away win (dev) | — | 0.453 / 0.231 / 0.317 |
| SOT / match (stats rows) | 8.170 | 8.155 |
| Corners / match | 9.427 | 9.423 |
| Total shots / match | 17.349 | 17.228 |
| Event-unified yellows / match | 5.193 | 5.113 |

This is a low-scoring, low-shot-volume league by programme standards
(goals 2.41 vs J1 ≈2.6–2.7; total shots 17.3 — the feed's
`total_shots` level is what it is, taken as published) and a
high-card league (5.19 yellows/match, the highest card level in the
programme so far). Home advantage in goals is modest (dev home−away
goal difference +0.27/match).

Virgin-season levels (for the record; not used in any fitting
decision): 2025/2026 goals 2.297, yellows 4.597 — a cooler season.

## Primary-line candidates (scored-dev over-rates, closest to 0.5)

- SOT: 8.5 → 0.458 (7.5 → 0.584) ⇒ primary **8.5**, ladder 7.5/8.5/9.5.
- Corners: 9.5 → 0.467 ⇒ primary **9.5**, ladder 8.5/9.5/10.5.
- Total shots: 17.5 → 0.473 (16.5 → 0.548) ⇒ primary **17.5**,
  ladder 16.5/17.5/18.5.
- Cards: 4.5 → 0.561 (5.5 → 0.421) ⇒ primary **4.5**,
  ladder 3.5/4.5/5.5.

## Trait reliability (split-half by team-season, career-pooled, n=92 team-seasons)

| Trait | for r | against r |
|---|---|---|
| Goals | 0.535 | 0.532 |
| SOT | 0.746 | 0.645 |
| Corners | 0.659 | 0.583 |
| Total shots | 0.700 | 0.737 |
| Event yellows | 0.229 | 0.334 |
| Possession | 0.822 | 0.822 |

Count traits (SOT/corners/shots) are strongly reliable; goals
moderate; team yellow traits are the weakest in the table (0.23/0.33)
— recorded plainly: the cards candidate rests on a weak team trait
and the dev gate is the judge. Possession is highly reliable (0.822),
which is what licenses the corners possession arm in Step 6 (the
production pair covariate `big_chance` does not exist here).

## Referee strictness

Referee text coverage is ~100% (one missing row in 2024/2025).
Split-half correlation of per-referee mean unified yellows:
**r = 0.379** over 20 referees with ≥20 pre-virgin matches (921
matches). A moderate, real signal — far above ZA's 0.080 (dropped
there), below J1's 0.65. Sufficient for a pre-registered variant arm
(X8), not for the base design.

## Halves (frozen-constant test, pre-virgin, event-derived)

| Market | 1H share | Observed share var. | Binomial noise exp. | True var. |
|---|---|---|---|---|
| Goals | **0.4542** | 0.12712 | 0.12838 | −0.00126 (≈0) |
| Yellow cards | **0.3183** | 0.06263 | 0.05510 | +0.00753 |

Goals: per-match 1H share variance is pure noise around the constant
— the frozen-constant presentation is justified. Cards carry a small
true variance (same pattern as ZA) but stay constant-presented per
programme rule. SOT, corners and total shots have **no halves source
at all** (no period splits, no event feed for those quantities) —
they are FT-only in this league (RU-1Division precedent).

## Movers (X2 evidence, measured against the real tier-2 corpus, id 9096)

Entrants whose previous season was in the Second Professional League
(keyed by team id): 7 pre-virgin entrants (2022/2023: Hebar,
Spartak Varna, Septemvri Sofia; 2023/2024: Etar, Krumovgrad;
2024/2025: Spartak Varna, Septemvri Sofia again). Pooled first-season
gaps vs that season's league mean: **GF −0.205 / match, GA +0.399 /
match** — the classic promoted-club pattern (weaker attack, much
weaker defence), direction supporting the programme-sanctioned
SHRINK arm for goals. (The two 2025/2026 entrants, Dobrudzha and
Montana, show the same direction, GF −0.49 / GA +0.30 pooled, but are
virgin-season rows and are not used as design evidence.)
