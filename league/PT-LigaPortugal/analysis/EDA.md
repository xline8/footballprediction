# Phase 3 — EDA: PT-LigaPortugal

Source: `eda_summary.json` (computed by `compute_eda.py` from the
built CSV; two coordinator verification fixes are marked in that
script — the half-share constant is a ratio-of-sums over *all*
split-era matches, and the team split-half of a share is a
ratio-of-sums per team, after Codex's first version averaged
per-match team-only shares).

## Levels per season

| Season | Goals | Home G | Away G | H/D/A % | SOT | Corners | Yellows | Shots | xG |
|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.64 | 1.43 | 1.21 | 39.5/28.4/32.0 | 8.41 | 9.76 | 5.66 | 24.75 | 2.55 |
| 2022/2023 | 2.49 | 1.42 | 1.08 | 49.0/18.0/33.0 | 8.61 | 10.60 | 5.25 | 25.58 | 2.76 |
| 2023/2024 | 2.87 | 1.58 | 1.28 | 43.5/24.5/32.0 | 8.71 | 10.19 | 4.75 | 25.47 | 2.71 |
| 2024/2025 | 2.57 | 1.40 | 1.17 | 43.1/25.8/31.0 | 8.10 | 9.52 | 4.87 | 23.98 | 2.53 |
| 2025/2026 | 2.68 | 1.50 | 1.19 | 41.2/27.1/31.7 | 8.23 | 9.43 | 4.76 | 24.14 | 2.63 |
| 2026/2027* | 2.63 | 1.27 | 1.37 | 39.8/20.4/39.8 | 8.04 | 8.88 | 4.21 | 24.96 | 2.59 |

*partial (98 matches). Home advantage is real but ordinary:
home sides score ~1.40–1.58 vs 1.08–1.28 away in complete seasons
(the partial virgin season is running away-hot, 39.8% away wins —
a transitional-window caveat the goals verdict must keep in view).
Yellows decline monotonically across the corpus — a level drift the
cards baselines (trailing/decay-weighted) exist to absorb. Goals sit
between J1 (~2.7) and the top-5 norm; corners (~9.5–10) are close to
J1's 9.47; yellows (~4.8–5.7) are far above J1 (~2.6–3.4) and at the
high European end.

## Trait reliabilities (team split-half, chronological halves, r)

Measured as in J1: per team, split its matches chronologically in
two, correlate the trait across teams (n_teams 25–26 unless noted).

| Trait | r | Verdict |
|---|---|---|
| goals for | 0.90 | SIGNAL |
| SOT for | 0.89 | SIGNAL |
| box touches for | 0.88 | SIGNAL |
| possession for | 0.88 | SIGNAL |
| big chances for | 0.89 | SIGNAL |
| SOT against | 0.82 | SIGNAL |
| shots for | 0.80 | SIGNAL |
| corners against | 0.75 | SIGNAL |
| box touches against | 0.74 | SIGNAL |
| corners for | 0.71 | SIGNAL |
| xG per shot (X4) | 0.63 | SIGNAL |
| yellows for | 0.61 | SIGNAL |
| xGOT per shot, attack, 2024/25+ era (X6) | 0.59 (n=20) | SIGNAL-CANDIDATE |
| goals against | 0.53 | SIGNAL |
| on-target rate | 0.43 | SIGNAL-CANDIDATE — **unlike J1 (r=0.06, noise)** |
| set-play xG share (X3) | 0.27 | WEAK |
| finishing (goals − xG) | 0.26 | WEAK/NOISE |
| referee yellow rate (X8) | 0.28 (n=25 refs) | WEAK — J1 measured 0.65 |
| yellows against | 0.17 | NOISE |

Every market's own target trait is reliable (goals, SOT, corners,
yellows-for, shots), so all five candidates clear the first
feasibility bar. Two J1 contrasts stand out: the on-target rate is a
real team trait in Portugal, and the set-play share and referee
traits are much weaker here than in J1.

## Half shares — the frozen-constant question (complete-split era 2023/24–2025/26)

| Market | 1H share (ratio of sums) | True variance | Team split-half r |
|---|---|---|---|
| Goals | 0.443 | −0.0011 | −0.37 |
| SOT | 0.449 | −0.0014 | −0.04 |
| Corners | 0.471 | +0.0017 | +0.04 |
| Yellows | 0.331 | +0.0035 | +0.25 |
| Total shots | 0.456 | +0.0006 | −0.05 |

The J1 result replicates: per-match 1H share variance is at or
barely above the binomial noise floor and team shares do not
replicate, so halves are **frozen league constants only**:
goals 0.443, SOT 0.449, corners 0.471, yellows 0.331, shots 0.456.
(Yellows' small positive true variance with team r=0.25 does not
meet the bar for per-team modelling; it is recorded, not used.)

## Referee

Coverage 53% → 99% → 100% (2023/24+). Split-half strictness
r = 0.28 over 25 referees with ≥20 matches — a weak trait, far
below J1's 0.65. The referee arm is still pre-registered for cards
(with shrinkage), but the expectation set here is low and the gate,
not optimism, decides.

## Thin-history teams

Teams whose first match of a season comes with <10 prior corpus
matches: 3 in 2022/2023, 2 in 2023/2024, 2 in 2024/2025, 1 in
2025/2026, 1 in 2026/2027 (2021/2022's 18 are the corpus-start
artefact). These are the promoted/returning clubs the G-J2
post-mortem warns about; the goals design carries the
template-sanctioned shrinkage arm for exactly this.
