# Step 3 — EDA: UAE Pro League

All numbers from `analysis/eda_compute.py` → `eda_numbers.json`, computed
on the complete seasons (awarded matches excluded). Charts in `charts/`.

## F1 — Levels and drift

| Season | Goals | SOT | Corners | Shots | Yellows (stats) | Home win | OU2.5 over |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.85 | 8.51 | 10.51 | 25.31 | 3.19 | 0.456 | 0.566 |
| 2022/2023 | 3.02 | 8.91 | 10.48 | 25.47 | 3.82 | 0.396 | 0.571 |
| 2023/2024 | 3.42 | 9.61 | 10.60 | 26.87 | 3.81 | 0.374 | 0.665 |
| 2024/2025 | 3.20 | 9.06 | 9.54 | 25.67 | 3.91 | 0.434 | 0.637 |
| 2025/2026 (virgin) | 2.82 | 8.18 | 9.15 | 24.48 | 3.89 | 0.385 | 0.522 |

Levels move season to season (goals ±0.3, corners −1.4 over the last two
seasons) — per-league fitting with time decay is justified; no single
structural break is frozen (the corner decline is gradual, the
2023/2024 goals spike reverted). The virgin season ran **cold on every
count stat except cards** relative to the dev window — recorded here as
an EDA fact (it is what the virgin calibration legs will judge).

## F2 — Team trait reliability (split-half, career-pooled, 18 teams ≥20 matches)

| Trait | r | Verdict |
|---|---|---|
| Total shots for | 0.893 | SIGNAL |
| Box touches for / against | 0.951 / 0.864 | SIGNAL (strongest in this EDA) |
| Big chances for | 0.912 | SIGNAL |
| Possession | 0.970 | SIGNAL |
| Corners for / against | 0.848 / 0.736 | SIGNAL |
| SOT for / against | 0.840 / 0.780 | SIGNAL |
| Goals for / against | 0.833 / 0.610 | SIGNAL |
| On-target rate (SOT/shots) | 0.637 | SIGNAL here (unlike J1's 0.06) — noted, not consumed: v5's ratio is an internal fitted component, and no arm may add a standalone trailing on-target covariate (J1 R4 logic stands as design discipline) |
| Yellows for (stats) | 0.318 | WEAK SIGNAL — the cards ratings have something to work with, but far less than other markets |

Per-match correlation of box touches with corners is 0.320 (possession
0.286-analogue in J1 was weaker than box touches there too; here the
box-touch trait reliability, 0.951, is the argument for the X7 arm).

## F3 — Halves: frozen constants (splits era 2023/2024–2025/2026, n≈545)

| Market | 1H share (ratio of sums) | Source |
|---|---|---|
| Goals | 0.4463 | goal-event minutes, all complete seasons, n=866 with goals |
| SOT | 0.4618 | period splits |
| Corners | 0.4801 | period splits |
| Total shots | 0.4608 | period splits |
| Yellows (stats) | 0.3724 | period splits |

Per-match share variance is dominated by count noise (total shots:
observed var 0.0103 vs a binomial-noise floor of ≈0.0098 at the mean
count) — per-match/per-team half shares are not modelled anywhere in
this program; these constants are presentation-only, exactly as frozen.

## F4 — Referee

Coverage 25–67% in dev seasons but **3% in the virgin**; strictness
split-half r=0.43 over just 9 referees with ≥16 named matches. The
trait cannot be validated in the virgin window → X8 dropped (FEATURES).

## F5 — Home advantage

Home goals 1.46–1.73 vs away 1.29–1.73; 2023/2024 is the one season
where away scoring exceeded home. Home-win rates 0.37–0.46 — low by
program standards (J1 ≈0.42–0.45, Europe ≈0.45).

## F6 — Cards artefact

See DATA_UNDERSTANDING §3. Target frozen: stats-feed yellows. The
dev-window stats level (3.81–3.91 in the last three dev-era seasons)
matches the virgin level (3.89), so the target definition is stable
across the gate boundary even though it undercounts the (dead) event
feed in earlier seasons.
