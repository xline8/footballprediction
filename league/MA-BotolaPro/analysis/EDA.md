# Step 3 — EDA: MA-BotolaPro

All computations in `analysis/eda_compute.py` → `eda_summary.json`.
Dev-era data only; the virgin 2025/2026 is never read here. Count
traits are measured on the rich dev era (2024-11-01 – 2025-05-12)
because that is the only dev-era window where the targets exist.

## Levels

Goals per match by season: 2021/2022 **2.1625**, 2022/2023
**2.1333**, 2023/2024 **2.2250**, 2024/2025 **2.3125** — a very
low-scoring league (J1 ~2.7, top-5 Europe ~2.8), slowly rising.
Home goals 1.18–1.24 vs away 0.95–1.07 (home win rate 0.41–0.43);
the home edge is real but modest. OU2.5 over-rate 0.383–0.413.

Rich-era count levels (n=164 stats matches): SOT **7.195**/match,
corners **8.628**, total shots **16.543** — all low versus the
European references (SOT ~9–10, corners ~10, shots ~25), consistent
with the low goals level. Unified yellows **4.443**/match (n=176) —
a normal-to-high card level. Home possession mean 51.1%.

Primary lines (from these dev distributions, closest over-rate to
0.5): SOT **7.5** (0.433; 6.5 is 0.567 — 7.5 frozen), corners
**8.5** (0.476), total shots **16.5** (0.518), yellows **4.5**
(0.494), goals OU **2.5**.

## Trait reliability (split-half by team, random halves)

| trait | window | n teams | r |
|---|---|---|---|
| goals for / against | dev seasons 2021–2025 | 20 | 0.641 / 0.552 |
| SOT for / against | rich dev era | 16 | 0.402 / 0.446 |
| corners for / against | rich dev era | 16 | 0.604 / 0.432 |
| total shots for / against | rich dev era | 16 | 0.651 / 0.512 |
| possession for | rich dev era | 16 | 0.608 |
| yellows for / against | rich dev era | 16 | **0.010** / 0.310 |

Goals, corners, shots and possession traits are genuinely reliable.
SOT is moderate (attenuated by the short ~10-match half-samples).
**Yellows-for is NOISE at r=0.010** in this league's rich dev era —
recorded plainly: the cards Gate Zero (which leans on team yellow
ratings + naive ensemble) starts with weak evidence here, and the
dev gate is exactly the test of whether the architecture still
extracts signal. No referee covariate exists to rescue it (referee
field empty in 1,255/1,255 payloads).

## Halves

- Goals 1H share (goal-event times, dev seasons, 2,120 goals):
  **0.4274**. Per-match share variance decomposition: observed
  0.12079 vs binomial noise 0.12835 → true variance **0.0**. The
  frozen-constant treatment is correct for goals.
- Yellows 1H share (card-event times, rich dev era): **0.3465** —
  frozen constant for cards presentation.
- SOT / corners / total shots: NO halves source exists (no period
  splits in any payload; these stats have no event feed). FT-only,
  halves share null (RU-1Division precedent).

## Entrants (mover evidence)

Entrant clubs (in the league after a season out; n=6 across
2022/2023–2024/2025) vs their first season's league mean:
ΔGF **−0.107**, ΔGA **+0.283** per match — entrants concede more,
score slightly less. This motivates the sanctioned SHRINK arm for
goals. A J1-style X2 tier-offset arm cannot be built: Botola 2 is
not in the warehouse at all (Morocco has exactly one league in the
index), so neighbour-tier membership is unobservable.

## Reference points

Botola Pro is the lowest-scoring league built in this program so
far (2.13–2.31 goals vs J1 ~2.7), with correspondingly low SOT /
corners / shots levels, but a full-strength yellows level (4.44).
Goals trait reliability (0.64/0.55) is in the normal program range.
