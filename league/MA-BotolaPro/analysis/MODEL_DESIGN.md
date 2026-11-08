# Step 6 — Model Design: MA-BotolaPro

No fitting in this step. Calibration = actual − predicted
everywhere in this build. Gate legs are the program-standard legs
(RU-1Division pattern): dev gate vs baselines; virgin LL leg +
calibration leg (|breach| ≤ 1pp clean PASS, ≤ 1 SE PROVISIONAL,
else FAIL); Gate Zero dev failure ⇒ candidate FAILS, virgin NOT
read; gates never move after results.

## Feasibility matrix

| candidate | target exists | scorable dev window | virgin contains target | verdict |
|---|---|---|---|---|
| G-MA goals | all seasons | 2022/2023–2024/2025 (n=720) | yes (240) | BUILDABLE |
| S-MA SOT | rich era only | rich 2024/2025 scored Jan–May (109 stats) | yes (226) | BUILDABLE |
| C-MA corners | rich era only | same (109) | yes (226) | BUILDABLE |
| K-MA cards | rich era only (event yellows) | rich 2024/2025 scored Jan–May (112) | yes (240) | BUILDABLE |
| T-MA total shots | rich era only | same (109) | yes (226) | BUILDABLE |

Unlike BE-FirstDivisionB (target only inside the virgin ⇒ NOT
BUILDABLE), this league's rich era covers the last dev season, so a
genuine pre-virgin dev window exists for every count market. The
count dev windows are short (109–112 scored matches) — recorded as
a limitation, not papered over: baselines face the same window.

## Candidates

- **G-MA** — production DC pattern, goals-only (X1 dropped), hl=270.
  Arms: Gate Zero; SHRINK (sanctioned entrant arm: ratings of teams
  with <6 prior in-league matches shrunk a,d *= n/6; EDA entrant
  gaps ΔGF −0.107 / ΔGA +0.283). Season-blocked: seed 2021/2022,
  dev scored 2022/2023–2024/2025 (n=720), virgin 2025/2026 (n=240).
  Primary OU 2.5.
- **S-MA** — production v5 pattern. Arms: Gate Zero; RS (BB prior
  200 → 20,000). Per-match walk-forward over the rich era: warm-up
  Nov–Dec 2024 (never scored), dev scored 2025-01-01–2025-05-12
  (109 stats matches), virgin 2025/2026 (226). Primary line 7.5,
  ladder 6.5/7.5/8.5.
- **C-MA** — production corners_v3 pattern, possession-only
  territorial multiplier (X9 partial; big_chance absent, X7
  dropped). Arms: Gate Zero only. Same windows as S-MA (109 dev /
  226 virgin). Primary line 8.5, ladder 7.5/8.5/9.5.
- **K-MA** — production cards pattern on event-unified yellows.
  Arms: Gate Zero only (X8 dropped — no referee data). Same
  windows (112 dev / 240 virgin; cards scores every rich match).
  Primary line 4.5, ladder 3.5/4.5/5.5. Halves via frozen 0.3465.
- **T-MA** — shots family. Arms: A (v1), B (v2 level layer), C (E9
  trailing-r). Same windows as S-MA. Primary line 16.5, ladder
  15.5/16.5/17.5.

## Halves presentation

Goals FT + 1H/2H via 0.4274; cards via 0.3465 (event-time sources).
SOT / corners / total shots FT-only (null shares).
