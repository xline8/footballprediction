# Step 3 — EDA: BG-SecondLeague

## F1 — Levels (goals only; no other target exists)
| Season | Goals/m | Home | Away | HW% | Draw% | Over 2.5 | BTTS |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.45 | 1.47 | 0.99 | 46.8% | 27.8% | 46.8% | 46.8% |
| 2022/2023 | 2.26 | 1.35 | 0.91 | 48.4% | 26.8% | 41.2% | 42.5% |
| 2023/2024 | 2.17 | 1.30 | 0.87 | 48.4% | 24.8% | 35.3% | 39.9% |
| 2024/2025 | 2.27 | 1.33 | 0.94 | 45.3% | 26.6% | 37.6% | 37.1% |
| 2025/2026 (virgin) | 2.52 | 1.45 | 1.07 | 43.4% | 27.2% | 46.0% | 45.6% |

Low-scoring second tier by European standards (2.17–2.52 goals/m vs
J1 ≈2.5–2.7 and SCO ≈2.8); home advantage is strong (home/away goal
ratio ≈1.45). Levels drift by season → per-league fit with time decay,
as in the reference pattern. *(Design-level aggregates over the virgin
season are EDA only; no parameter is tuned on them — the virgin gate
read is separate and once-only.)*

## F2 — Team trait reliability (split-half within season, odd/even)
- Goals-for r = **0.441**, goals-against r = **0.404** (n = 109 team-seasons).
- Verdict: **SIGNAL, moderate** — weaker than J1 (0.66/0.62) and BG1
  itself (0.651/0.486 measured the same way), but far from noise. A
  scores-only Dixon-Coles ratings fit has real signal to work with;
  this is the entire justification for building G-BG2.

## F3 — Half shares
**Not measurable.** Period splits are 0% and the payloads carry no HT
score field. No frozen constant exists for this league; the goals
product is **FT-only** (no 1H/2H presentation). This is a data fact,
not a modelling choice.

## F4 — Movers from Bulgaria First Professional League (id 270)
Relegated clubs arriving in BG2, first-season performance vs league mean:
| Arrival season | n clubs | ΔGF/m | ΔGA/m |
|---|---|---|---|
| 2023/2024 | 2 | +0.48 | −0.29 |
| 2024/2025 | 2 | +0.26 | −0.07 |
| 2025/2026 | 1 | +0.02 | +0.34 |
Direction is inconsistent and the samples are 1–2 clubs per season
(compare J.League F4: n=9–13 movers per direction, symmetric at both
steps). Verdict: **NOISE / insufficient — the X2 mover offset is
DROPPED** (see FEATURES). The sanctioned alternative for the
season-opener failure mode, SHRINK, is pre-registered instead.

## F5 — Referee
Coverage 0%. Nothing to measure. Any referee feature is impossible.

## F6 — Stats markets feasibility
SOT / corners / cards / total shots targets: **0% coverage in every
season** (stats feed absent, shotmap empty). There is no virgin window
containing any of these targets, so no candidate can be gated. These
markets are **not buildable** in this league — a documented result,
not a gap to work around.
