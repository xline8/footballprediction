# EDA — MX-ExpansionMX

Computed by `analysis/eda_compute.py`; full numbers in
`analysis/eda_summary.json` + `inventory_summary.json`. Population:
regular phase only, blocks 1–10 (n=1,208) unless stated.

## Levels by block

| Block | n | Goals | Home | Away | HW% | Draw% | O2.5% | Yellows |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 - Apertura | 136 | 2.404 | 1.294 | 1.110 | 38.2 | 30.1 | 47.8 | — |
| 2021/2022 - Clausura | 136 | 2.228 | 1.287 | 0.941 | 46.3 | 27.9 | 38.2 | — |
| 2022/2023 - Apertura | 153 | 2.562 | 1.536 | 1.026 | 46.4 | 29.4 | 46.4 | — |
| 2022/2023 - Clausura | 153 | 2.477 | 1.386 | 1.092 | 44.4 | 26.8 | 45.8 | (3.86 partial) |
| 2023/2024 - Apertura | 105 | 3.029 | 1.943 | 1.086 | 56.2 | 21.0 | 61.0 | 5.086 |
| 2023/2024 - Clausura | 105 | 2.629 | 1.333 | 1.295 | 38.1 | 26.7 | 48.6 | 4.914 |
| 2024/2025 - Apertura | 105 | 2.857 | 1.857 | 1.000 | 51.4 | 30.5 | 48.6 | 4.895 |
| 2024/2025 - Clausura | 105 | 2.886 | 1.810 | 1.076 | 55.2 | 24.8 | 55.2 | 5.029 |
| 2025/2026 - Apertura | 105 | 3.048 | 1.695 | 1.352 | 40.0 | 29.5 | 57.1 | 5.838 |
| 2025/2026 - Clausura | 105 | 2.876 | 1.829 | 1.048 | 55.2 | 27.6 | 55.2 | 5.514 |

Pooled goals 2.666/match; pooled home advantage +0.475 goals —
stronger than Liga MX's and far above European norms; block-level
home-goals means swing widely (1.29–1.94), which the expanding-
window walk-forward absorbs. Goal level drifts up after 2022/2023
(2.23–2.56 → 2.63–3.05). Clean-era yellows: 4.89–5.84/match,
rising in 2025/2026 (5.51–5.84) — the cards model's decay handles
level drift the production way. 2026/2027 stats-era context levels
(excluded from modelling): SOT 10.06, corners 9.93, total shots
29.92 per match.

## Trait reliability (split-half, odd/even team appearances, sums)

- Goals for r=0.909, against r=0.948 (n=20 teams) — SIGNAL, strong.
- Yellows for r=0.957, against r=0.934 (clean cards era) — SIGNAL,
  strong. (Sums over ~equal appearance counts; read as the J1
  ratio-of-sums analogue.)
- SOT / corners / shots traits: not measurable (no stats era in
  any complete block).

## Halves (the frozen-constant question)

- Goals 1H share = **0.448** (n=1,207 complete rows). Observed
  per-match share variance 0.11351 vs binomial noise floor 0.1173
  → true variance 0.0. Per-match half share is noise around the
  constant, as in J1 and the top-5 audit: presentation via the
  frozen constant only.
- Yellows 1H share (clean era, n=630) = **0.4016 → frozen 0.402**.
  (Including the partial 2022/2023 - Clausura block would give
  0.3972; the clean-era number is the frozen one.)

## Cards capture check (decides the cards corpus start)

| Block | Yellows/match | Zero-yellow matches | Matches with ≥1 yellow |
|---|---|---|---|
| 2022/2023 - Clausura | 3.863 | 45 / 153 (29.4%) | 70.6% |
| 2023/2024 - Apertura | 5.086 | 2 / 105 | 98.1% |
| 2023/2024 - Clausura | 4.914 | 1 / 105 | 99.0% |

Decision: 2022/2023 - Clausura capture is partial (whole matches'
yellows missing). Cards corpus = 2023/2024 - Apertura onward; the
partial block is excluded entirely, not used as warm-up.

## Altitude (descriptive only)

Home-city map covers all 20 teams (0 unknown matches). ≥2,000 m
homes (Tlaxcala 2,400; Zacatecas 2,440): edge +0.207, HW 42.7%
(n=150). Rest: +0.513, HW 47.4% (n=1,058). Away<1,000 m contrast:
+0.574 (n=68) vs +0.670 (n=448). **No altitude effect is measured
in this league** — the sign is opposite to the Liga MX descriptive
finding (+0.586 vs +0.221 there), because the two high clubs are
weak at home in this window. Not adopted; no arm (R7). The Liga MX
lesson stands in reverse: a naive altitude covariate fitted here
would have imported another league's conclusion against this
league's own measurement.

## Entrants, movers, stability

Entrants after the seed block: Alacranes de Durango + Atlético La
Paz (2022/2023 - Apertura), Irapuato (2025/2026 - Apertura) — all
franchise entries, none relegated from Liga MX (same-block team-id
overlap with Liga MX = 0 in all 10 blocks; no promotion exists).
Three clubs departed after 2022/2023 (18 → 15 teams). The G-J2
failure mode (1–2-match teams in openers) can occur only for these
3 entrant team-blocks, and under tournament-blocked fitting an
entrant has exactly 0 prior in-league matches at its first block —
the SHRINK arm is pre-registered anyway (sanctioned) and its bite
is measured and reported.
