# Step 3 — EDA: IT-SerieC

All EDA level and reliability numbers below use **regular-phase rows only**.
The complete machine-readable detail is in `eda_summary.json`.

## F1 — Levels

| Season | n | Goals/m | Home | Away | HW% | Draw% | Over 2.5 | BTTS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 1,102 | 2.34 | 1.34 | 1.00 | 42.3% | 31.1% | 41.9% | 48.2% |
| 2022/2023 | 1,140 | 2.32 | 1.28 | 1.04 | 40.1% | 29.6% | 41.9% | 46.9% |
| 2023/2024 | 1,140 | 2.33 | 1.28 | 1.05 | 41.8% | 28.9% | 41.5% | 46.8% |
| 2024/2025 | 1,066 | 2.37 | 1.30 | 1.06 | 40.5% | 29.2% | 43.2% | 49.7% |
| 2025/2026 (virgin) | 1,102 | 2.37 | 1.30 | 1.07 | 40.6% | 30.2% | 42.8% | 50.0% |
| 2026/2027 (in progress) | 386 | 2.59 | 1.42 | 1.18 | 43.3% | 29.8% | 49.2% | 53.4% |

Group-level values for every season are in the JSON. The group structure is
real: Girone A is persistently the lowest-scoring group (2.19–2.33 goals/m
vs B 2.26–2.43 and C 2.36–2.41) and Girone C carries the strongest home edge
(home-win 43–46%). Because groups never meet in the regular season, a pooled
fit's team ratings absorb these level differences exactly; `group` stays an
EDA dimension, not a feature. The pooled home/away goal ratio is **1.241** —
the weakest home advantage in the program so far (BG2 ≈1.45, J1 ≈1.35),
with a high draw rate (29–31%).

## F2 — Trait reliability

Odd/even match-order split-half correlations, requiring at least five matches
per half, are pooled **r = 0.377 for goals-for** and **r = 0.435 for
goals-against** across 339 team-seasons. By-season pairs (GF / GA) are:
2021/22 .437/.520; 2022/23 .590/.409; 2023/24 .497/.435; 2024/25 .495/.577;
2025/26 .295/.492; 2026/27 .114/.246. Verdict: **SIGNAL, modest**; enough to
justify a goals-only rating model, with thin-data shrinkage pre-registered.

## F3 — Half shares

Not measurable in the complete seasons. Splits exist only in part of the
in-progress 2026/2027 payloads, so presentation is FT-only and no halves
constant is frozen.

## F4 — Movers vs Serie B (league_id 86)

Relegated arrivals from Serie B (in Serie B in S−1, in Serie C in S, not in
Serie C in S−1; plain name matching — the aliases `Pordenone`/`Pordenone
Calcio` are distinct strings and Brescia's 2025 renaming to Union Brescia is
missed by matching in 2025/2026), measured in their first Serie C regular
season versus that season's Serie C regular per-team mean:

| Arrival | n clubs | ΔGF/m | ΔGA/m |
|---|---:|---:|---:|
| 2022/2023 | 5 | +0.20 | −0.08 |
| 2023/2024 | 3 | −0.03 | −0.22 |
| 2024/2025 | 5 | +0.07 | −0.23 |
| 2025/2026 | 3 | +0.16 | −0.09 |

(These values were recomputed independently by the builder from the raw CSV
after a first pass used a wrong reference base; the corrected figures are
also in `eda_summary.json`.) The pattern is a small, mostly consistent
defensive edge (≈ −0.15 GA/m) and a weak attack edge (≈ +0.10 GF/m) — real in
direction, but on 3–5 clubs per season with fragile name identity it is too
small and too uncertain to freeze as an offset. Verdict: **insufficient —
X2 dropped; SHRINK is the pre-registered thin-data arm instead**.

## F5 — Referee

Zero referee coverage in every complete season; no referee feature is possible.

## F6 — Stats-market feasibility

Stats exist only in the in-progress season, with no development window and no
complete virgin window containing a count target. SOT, corners, cards, and total
shots are **not buildable**. This is a documented data result.
