# G-NLTD Verdict — Tweede Divisie goals model

Date: 2026-11-10. Branch `build/nl-tweede-divisie`. Prereg:
`league/NL-TweedeDivisie/prereg/PREREG_G_NLTD.md` (commit c3380916,
frozen before any fitting). Engine:
`league/NL-TweedeDivisie/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; every number below was
recomputed independently by the coordinator: the climatology
baseline was recomputed from the CSV with fresh code and matches
the engine exactly to 6 decimals on all three metrics (pooled and
per season); `dc.py` was diffed against the reference and is
mathematically identical (formatting only, plus an assert that xG
is None); the X2 lambda-change count (256) equals the entrant
team-match count in scored dev exactly. The dev run was repeated
and reproduced identical numbers. Calibration is stated as actual
− predicted throughout this build.

## Verdict: FAIL — every arm dies at the dev gate (OU2.5 leg); virgin NOT read

All three arms beat climatology on pooled 1X2 LL and RPS, and all
three lose the OU2.5 leg to the base-rate baseline on pooled dev —
the same shape as G-NLE (Eerste Divisie), G-ESPF, and most of the
program. Under the frozen legs no arm passes dev, so the virgin
window was **not read** (the runner wrote
`results_virgin.json`: `{"virgin_read": false, "reason": "no arm
passed the dev gate"}`; no 2025/2026 outcome was evaluated, no
predictions file exists, no fitted params exist) and **nothing
ships**.

## Dev results (expanding season-blocked walk-forward, scored 2022/2023–2024/2025, n = 918)

| Season | GZ LL / RPS / OU | SHRINK LL / RPS / OU | X2 LL / RPS / OU | Climatology LL / RPS / OU |
|---|---|---|---|---|
| 2022/2023 | 1.0409 / 0.2295 / 0.6984 | 1.0409 / 0.2295 / 0.6984 | 1.0340 / 0.2270 / 0.6961 | 1.0603 / 0.2375 / 0.6688 |
| 2023/2024 | 1.0654 / 0.2336 / 0.6955 | 1.0654 / 0.2336 / 0.6955 | 1.0726 / 0.2360 / 0.6909 | 1.0899 / 0.2422 / 0.6643 |
| 2024/2025 | 0.9996 / 0.2235 / 0.6730 | 0.9996 / 0.2235 / 0.6730 | 0.9996 / 0.2237 / 0.6683 | 1.0433 / 0.2421 / 0.6552 |
| **Pooled** | **1.0353 / 0.2289 / 0.6890** | **1.0353 / 0.2289 / 0.6890** | **1.0354 / 0.2289 / 0.6851** | **1.0645 / 0.2406 / 0.6628** |

Dev gate (pooled 1X2 LL **and** RPS beat climatology **and** OU2.5
LL beats the base-rate baseline): Gate Zero **FAIL** (OU 0.6890 >
0.6628). SHRINK **FAIL** (identical numbers — see below). X2
**FAIL** (OU 0.6851 > 0.6628; its pooled 1X2 LL 1.0354 and RPS
0.2289 are essentially tied with Gate Zero — LL +0.0001, RPS
+0.0000 — so it does not fix the totals distribution).

Two plain findings:

- **SHRINK is vacuous in this harness.** Under season-blocked
  fitting every non-mover team has ≥ 34 training matches (shrink
  factor 1.0) and every mover has 0 (rating 0 × 0 = 0, the league
  mean it starts from anyway). The arm can never bind; its
  byte-identical results (max abs diff 0.0 on all metrics) are
  correct, not a bug. A shrink arm only has content under
  per-match refits.
- **X2 genuinely ran and helps a little on results, not on
  totals.** It changed lambdas in 256/918 scored matches —
  exactly the entrant team-match count — and beats Gate Zero on
  1X2 LL and RPS in 2022/2023 (1.0340 vs 1.0409; 0.2270 vs
  0.2295), but loses on 1X2/RPS in 2023/2024 and is flat in
  2024/2025. Pooled it is a wash on results (LL +0.0001 vs Gate
  Zero) and still loses the OU leg by 0.0223. The below-tier
  entrant prior carries weak result signal at best, consistent
  with the EDA's weak pooled gaps (GF −0.093, GA +0.181).
- The DC ratings again carry genuine 1X2 signal (LL ~1.035 vs
  1.064 climatology, RPS clearly better) while the total-goals
  distribution loses to the league's own over-rate in a league
  whose OU2.5 over-rate sits at 59–66% every season (pooled dev
  62.4%). The gate is doing its job.

## Virgin window — NOT read

No arm passed dev. No virgin metrics, no fitted params, no
predictions file for G-NLTD. 2026/2027 was never touched.

## Other candidates — NOT buildable (no verdict files)

- S (SOT), C (corners), T (total shots): no target exists anywhere
  in the corpus — no stats feed, no shotmap — in any season,
  including the virgin window. Building them would break the gate
  rule.
- K (cards): no yellows exist (0 Yellow events in 1,638 matches);
  reds are 0.145/match with split-half r = −0.09 — a rare-event
  count with no reliability evidence.

## League completion state

League complete: the single buildable candidate (G-NLTD) has been
through its gate (FAIL at dev, virgin deliberately unread) and the
four non-buildable candidates are documented as such with the
measured reason. Nothing ships; nothing joins the daily pipeline.
