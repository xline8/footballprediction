# Step 3 — EDA: CO-PrimeraB (goals only; other markets have no data)

All numbers on the finished corpus (n = 1,639). 2026 is in progress
and is shown for context only; it enters no fit, gate or constant.

## F1 — Levels by season (SIGNAL: per-league fit with decay justified)

| season | n | goals/match | home | away | HW | draw | OU2.5 | BTTS | 1H share* |
|---|---|---|---|---|---|---|---|---|---|
| 2021 (partial seed) | 144 | 2.340 | 1.375 | 0.965 | .472 | .292 | .417 | .479 | — (no events) |
| 2022 | 289 | 2.197 | 1.263 | 0.934 | .433 | .318 | .377 | .460 | .5047 |
| 2023 | 310 | 2.200 | 1.284 | 0.916 | .442 | .313 | .371 | .432 | .4809 |
| 2024 | 310 | 2.371 | 1.423 | 0.948 | .510 | .239 | .426 | .416 | .4787 |
| 2025 (virgin) | 308 | 2.360 | 1.403 | 0.958 | .461 | .253 | .429 | .448 | .4834 |
| 2026 (in progress) | 278 | 2.180 | 1.151 | 1.029 | .367 | .327 | .363 | .478 | .4637 |

*1H share from goal-event times, event-exact matches only.

This is a LOW-scoring league: 2.20–2.37 goals/match in complete
seasons, OU2.5 rate .37–.43 — well below J1 (≈2.7 gpm) and the
European band (GE 2.54–3.15). Home advantage is proportionally
strong (home/away goal ratio ≈ 1.35–1.48 pooled). Levels are stable
enough across 2022–2025 that a decayed per-league fit is justified,
with 2024–2025 running slightly hotter than 2022–2023.

## F2 — Team trait reliability, goals (SIGNAL)

Split-half (random halves of each team's 2021–2024 matches, teams
with ≥40 matches, n = 19 team ids): goals-for r = 0.532,
goals-against r = 0.714. Defensive traits are solidly reliable,
attacking traits moderately so — a scores-only Dixon-Coles fit has
genuine signal. This is the entire justification for building G-CO.

## F3 — Halves: frozen constant, presentation only

1H goal share by season: .479–.505 (2022–2024), no trend; pooled dev
(2022–2024, event-exact matches, 2,043 goals) share = **0.4875** —
unusually high vs J1 (0.412) and GE (0.4516): nearly half of this
league's goals arrive before half-time. Per the program's standing
finding (per-match half share ≈ noise around a league constant),
halves are NEVER fitted: FT lambdas are split by the frozen constant
0.4875 for presentation only. The constant is frozen from dev
seasons only — the virgin 2025 share (.4834) was not used to set it.

## F4 — Movers from Primera A (id 274) — the X2 question (SIGNAL)

Relegated-from-A clubs, first season in B, per-match goals for /
against vs that season's league mean per team (GF/m mean = gpm/2):

| arrival | club | ΔGF/m | ΔGA/m |
|---|---|---|---|
| 2023 | Cortulua | +0.03 | −0.10 |
| 2023 | Patriotas | +0.07 | −0.34 |
| 2024 | Union Magdalena | +0.29 | −0.35 |
| 2024 | Atletico Huila | +0.06 | −0.41 |

Dev-era mean (2023–2024 arrivals, 4 club-seasons): **ΔGF +0.11/m,
ΔGA −0.30/m — same direction in 4/4 club-seasons on both sides**,
unlike BG-SecondLeague where the mover effect was inconsistent and
X2 was dropped. Relegated clubs defend far better than the B mean
and score slightly more. This justifies ONE pre-registered X2 arm
with the offset frozen from these dev-era numbers only (FEATURES):
attack ×1.10, concession ×0.73 (≈ −0.30 on a ~1.10 GA/m base), in
log-rating terms a = ln 1.10, d = ln 0.73, replacing the fitted
ratings of a mover-down club for its first B season. (The 2025
arrivals — Patriotas returning and CD Jaguares — are the virgin
season's movers; their outcomes are part of the virgin read and
were NOT used to set the offset.)

New-club context for SHRINK: because 2021 is a partial seed, two
2022 target-season clubs carry only 3 and 5 prior in-league matches
in the training window, and each later target season has exactly one
club with 0 priors — so the template's SHRINK arm (1–5 prior
matches) genuinely bites in this league (2022 dev season), unlike
GE/BG where it was degenerate by construction.

## F5 — Referee / cards / SOT / corners / shots: ABSENT in dev+virgin

Coverage numbers in DATA_UNDERSTANDING (stats null 1,773/1,773;
shotmap empty 1,773/1,773; referee 0 in all dev seasons; card
events fragmentary 2022–2025, complete-looking only in the
in-progress 2026). No EDA is possible and none is faked.
