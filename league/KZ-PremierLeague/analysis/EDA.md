# Exploratory data analysis

All fitting-relevant values below are generated in
[eda_summary.json](eda_summary.json) from finished 2021–2025 data.
2026 is shown only in inventory and levels tables; it does not select
lines, arms, constants, or windows.

## Findings

**F1 — levels and drift.** Finished goals/match by season are 2021
2.571, 2022 2.626, 2023 2.445, 2024 2.365, 2025 2.725; 2026 inventory
level is 2.567. Home goals / away goals by season: 1.357/1.214,
1.593/1.033, 1.346/1.099, 1.346/1.019, 1.522/1.203 (2026: 1.450/1.117).
Home edge is +0.32 goals pooled over dev (+0.14…+0.56 by season; the
2022 edge of +0.56 is the outlier, driven by away goals of 1.03).
Pooled dev evaluation seasons 2022–2025 (n=702, `pooled_eval`) have
home/draw/away rates 0.453/0.256/0.291 and BTTS 0.48–0.55 by season.
Goals dispersion (variance/mean of the match total) is 0.85–1.22 by
season — near-Poisson, the same regime as the top-5 production
markets. Context: KZ scores at about the J.League level (2.55) and
below the top-5 spine (2.84), with a stronger home edge than J1
(+0.20).

**F2 — trait reliability.** Split-half reliability is chronological
odd/even matches pooled by team over 2021–2025: goals-for r=**0.802**
(n=20 teams), goals-against r=0.296 (n=20). SOT, corners, shots, and
yellows are null with n=0. Consecutive season correlations for
goals-for are 0.736, 0.316, 0.613, 0.704; goals-against are 0.251,
0.503, 0.570, 0.599 (2021–22 through 2024–25). The attack trait is
unusually strong for a scores-only league (contrast UY-SegundaDivision
goals-for r=0.187) — a ratings architecture has real, persistent team
signal to capture here, concentrated on the attack side. The defence
trait is weak-moderate: present in every season pair, but noisier.

**F3 — halves.** Event-time rule is minute `<=45`; the Half-event
cross-check agrees 1,040/1,040, and no added-time field is available.
Dev event goals give a pooled 1H share of **0.454** across 2,243 goals
and 824 matches; per-season shares are 2021 0.444, 2022 0.463, 2023
0.462, 2024 0.436, 2025 0.460 — stable, no season more than ~1 SE from
the pooled share. Per-match share variance is 0.1202. The career
team-share split-half is r=0.086 (n=20), and the de-confounded checks
are r=−0.239 within team-season (n=69 team-seasons) and r=0.077
season-demeaned (n=20), neither significant — team 1H share is
noise, and the constant must not become a fitted covariate. The frozen
goals 1H constant is 0.4539, presentation-only. No SOT/corners/shots/
card constant exists.

**F4 — entrants (descriptive only, no arm).** The 6 dev entrants —
teams with no prior-season record in this league, 2022–2025 — are
compared with the same-season finished KZ team-match mean. Mean GF
difference is −0.215 (5 negative, 1 positive); mean GA difference is
+0.162 (0 negative, 6 positive). The opposite-sign pattern is clean
and in the expected direction for promoted sides, but with n=6 it is
descriptive only: no Kazakh sibling league exists in the warehouse,
so no X2 mover prior can be estimated and no mover arm is registered
(brief). Entrants by season: 2022 Maktaaral FC, Aksu; 2023 Okzhetpes;
2024 FC Yelimay, Zhenis; 2025 Ulytau — see `eda_summary.json`
`entrants_dev` for ids (the single positive GF deviation is Yelimay
+0.28 in 2024). The 2026 entrants are inventory only: two genuinely
new ids (2539, 732295 Altai) with no prior-season record.

**F5 — coverage.** Stats, shotmap, splits, lineups (starter sense),
playerStats, and named referees are 0 in every season. Events cover
170/182, 172/182, 172/182, 145/156, 169/182, and 230/240 payloads in
2021–2026. The event feed has 127 Red and 68 YellowRed cards in dev,
zero plain Yellow; these rare/incomplete event counts are not a card
target.

**F6 — identity.** ID-keying merges the two display-name variant
pairs recorded in inventory (200279 Kaspyi/Kaspiy Aktau; 732295 Altai
Semey / FC Altai Oskemen); no name-based team split is permitted.

**F7 — calendar / format.** Calendar-year labels are retained.
Single round-robin table, no split group or playoff phase: rounds
1–26 (2021–2025) and 1–30 (2026), uniform matches per round, balanced
schedules (26 / 24 in the 13-team 2024 season / 30 in 2026).
`hasPlayoff` is `False` in all 2025/2026 payloads. 2026 is complete
(Mar 7 – Oct 31, 240/240), so the virgin window is complete, not
transitional.

**F8 — virgin.** 2026 is the virgin window: 240 matches, 16 teams,
last match 2026-10-31, complete. It is read ONCE, only for arms
passing the dev gate, after dev results are frozen.

**F9 — target feasibility.** Goals are the only observed consistent
target. SOT, corners, total shots, and yellows cannot be measured.

**F10 — event completeness.** Empty event payloads occur in every
season (66 total); score-derived FT goals remain usable, while
event-derived half/card fields are conditional on events.

**F11 — line selection.** On pooled 2022–2025 dev (`n=702`),
OU1.5/2.5/3.5 over-rates are 0.708/0.474/0.246. OU2.5 is closest to
50% and is the primary line.

**F12 — home advantage.** Dev pooled home edge is +0.32 goals;
home advantage is left to the fitted DC parameter.

**F13 — SHRINK bite.** At every target-season start 2022–2026,
each team has either 0 prior in-league matches (the entrants) or
≥24 (min nonzero 24–52); zero teams fall in the 1–5 prior-match band
the SHRINK arm targets. SHRINK is therefore expected to be
byte-identical to Gate Zero — registered anyway as the sanctioned
G-J2-lesson arm, and the verdict must verify the identity from the
results file rather than assume it.

**F14 — 2026 restriction.** Any 2026 number in inventory/levels is
descriptive only; no 2026 row informed F2–F4, F11, or design choices.

Charts are generated by `make_charts.py` from this JSON and the built
CSV.
