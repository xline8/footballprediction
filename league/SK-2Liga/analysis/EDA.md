# Step 3 — EDA (SK-2Liga)

Computed by `analysis/run_eda.py` → `analysis/eda_numbers.json`
(finished matches only; dev era for reliability/halves/movers =
2021/2022–2024/2025; events-based halves use reconciled-events
matches only). Charts: `analysis/charts/` via
`analysis/make_charts.py`.

## F1 — Levels per season (per match, finished matches)

| Season | n | Goals | Home G | H | D | A | OU1.5 | OU2.5 | OU3.5 | BTTS | Events |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 163 | 3.00 | 1.71 | 0.460 | 0.202 | 0.337 | 0.810 | 0.577 | 0.301 | 0.534 | 0 |
| 2022/2023 | 200 | 2.86 | 1.58 | 0.450 | 0.225 | 0.325 | 0.775 | 0.595 | 0.295 | 0.535 | 0 |
| 2023/2024 | 231 | 3.05 | 1.72 | 0.472 | 0.216 | 0.312 | 0.801 | 0.576 | 0.342 | 0.532 | 156 |
| 2024/2025 | 182 | 2.69 | 1.58 | 0.516 | 0.192 | 0.291 | 0.753 | 0.538 | 0.286 | 0.516 | 177 |
| 2025/2026 (virgin) | 240 | 2.95 | 1.70 | 0.475 | 0.275 | 0.250 | 0.779 | 0.554 | 0.362 | 0.617 | 230 |
| 2026/2027 (in progress) | 127 | 2.96 | 1.65 | 0.480 | 0.220 | 0.299 | 0.795 | 0.598 | 0.331 | 0.583 | 47 |

Goals run HIGHER than the sibling top tier: 2.69–3.05/match here
vs 2.61–2.82 in SK-1Liga, and the dev-pooled OU2.5 over-rate is
0.572 (n = 776) vs 0.509 in SK-1Liga. Home advantage is strong
(home win 0.45–0.52, home goals 1.58–1.72). No level break anywhere:
the short 2024/2025 season is the lowest-goals season (2.69) but
within the range of ordinary season-to-season movement, and the
virgin season (2.95) sits mid-range. The 2021/2022 seed is thin
(163 finished of 240 indexed) and the 2022/2023 evaluation season
is 200/240 — both are used as-is; the gaps are scattered pull
failures, not a format change. 2026/2027 is a partial season and is
shown for inventory only.

## F2 — Team trait reliabilities (split-half, odd/even matches,
team-season units, dev era; n = 62 units)

| Trait | r |
|---|---|
| Goals for | 0.528 |
| Goals against | 0.514 |

Both traits are real and near-symmetric — stronger than SK-1Liga's
goals-against (0.293) and in line with its goals-for (0.591). A
Dixon–Coles attack/defence model has signal to fit. (No other
traits exist: there is no stats feed to split-half.)

## F3 — Halves (event times, reconciled-events matches only):
frozen constant, team shares are noise

Pooled 1H goal share, dev era (2023/2024 + 2024/2025, the only dev
seasons with events): **0.4940** (495 of 1,002 goals, 332 matches).
Per-season: 2023/2024 0.5078 (262/516), 2024/2025 0.4794 (233/486),
2025/2026 0.4615 (324/702), 2026/2027 0.4485 (61/136); all-events
pooled 0.4783 (880/1,840, 608 matches). The share sits notably
HIGHER than SK-1Liga's 0.4448 and J1's 0.412 — nearly half of all
goals arrive before half-time in this league — and drifts down
across the four events seasons (0.508 → 0.449). The per-season
drift is within ~2 SE of noise (SE ≈ 0.022 per season) and the
programme freezes the pooled dev-era constant rather than chasing
it; the virgin season's 0.4615 is recorded as a watch item, not a
correction. Variance decomposition (per-match 1H share vs binomial
noise at the pooled share, dev era): observed 0.1046 vs noise
0.1105 → true variance ≈ **−0.0059 (≈ 0)** (327 matches with
goals). Team split-half reliability of the 1H share (team's OWN
goals, odd/even matches): r = −0.165 (n = 29 team-season units) —
**per-team half shares are pure noise** (the J1/SK-1Liga F3 result
replicates a third time). Only the league constant ships, presentation-only,
for the goals market. Every other market is FT-only by absence of
data (no period splits exist for any market).

## F4 — Movers (X2 evidence; relegated from 1. Liga, id 176,
in-warehouse)

First-season deviation from the 2. Liga per-team-match mean.
One relegated club arrives per season — a thin but complete
record, and the direction is consistent.

| Boundary | Club | n | ΔGF/match | ΔGA/match |
|---|---|---|---|---|
| →2022/2023 | FK Pohronie | 27 | −0.023 | −0.134 |
| →2023/2024 | Liptovsky Mikulas | 30 | +0.241 | +0.074 |
| →2024/2025 | Zlate Moravce | 26 | +0.234 | −0.651 |
| →2025/2026 | Dukla Banska Bystrica | 30 | +0.560 | −0.640 |

Attack: 3 of 4 arrivals score ABOVE the league mean; defence: 3
of 4 concede BELOW it. This is the mirror image of SK-1Liga's
promoted-mover pattern (promoted clubs score below and concede
above in the higher tier) — exactly the tier-gap story told from
the other side: a relegated club is stronger than its new
division. Cumulative mean offsets from transitions completed
before each target season (frozen for the prereg): before
2023/2024 (−0.023, −0.134); before 2024/2025 (+0.109, −0.030);
before 2025/2026 (+0.151, −0.237). Before 2022/2023 no transition
is completed inside the warehouse window → X2 ≡ Gate Zero for
that evaluation season by construction. Note the 2025/2026
arrival (Dukla) is a virgin-season arrival: it is recorded here
but is NOT part of any frozen offset (its transition completes
after the dev window). Verdict: **SIGNAL-CANDIDATE, thin (n = 1
transition per season) but direction-consistent** — adopted as a
preregistered arm; the gate decides. Clubs arriving from 3. Liga
(2–5 per season: e.g. Spartak Myjava, Tatran Presov, Povazska
Bystrica, Dolny Kubin, FK Raca Bratislava into 2022/2023) have no
prior-season warehouse record and start at the league mean in
every arm. For context, the reverse flow is one club per season
promoted 2. Liga → 1. Liga (Dukla, Podbrezova, Skalica in
2022/2023; FC Kosice; Komarno; Tatran Presov; Dukla again).

## F5 — Referee strictness: NOT ESTIMABLE

Referee names exist in 0/1,143 finished matches (feed defect 5).
No reliability number can be computed; X8 is dropped on data
absence, not on a failed test.

## F6 — Events audit (frozen halves-source check)

Events exist in 610 finished matches; goal totals reconcile with
the FT score in 608. The 2 defects (4553752, stale/wrong block;
4838232, duplicated 67' goal) are excluded from halves only.
No stats feed exists to audit against — there is no second source
for any target in this league.

## Primary lines (dev pooled, finished matches; over-rate closest to 0.5)

- Goals: programme-standard OU2.5 (dev over-rate 0.5722, n = 776).
  No other market has a target, so no other line is registered.
