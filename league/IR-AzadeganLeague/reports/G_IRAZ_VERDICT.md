# G-IRAZ Verdict — Azadegan League goals model

Date: 2026-11-10. Branch `build/ir-azadegan-league`. Prereg:
`league/IR-AzadeganLeague/prereg/PREREG_G_IRAZ.md` (commit 3eab6893,
frozen before any fitting). Engine:
`league/IR-AzadeganLeague/engine/goals/`. Implementation: Codex
(gpt-5.6-luna) copied `dc.py` and adapted `arms.py` (X2 removed),
then its session was blocked by a sandbox mount failure
(`failed to register synthetic bubblewrap mount target /tmp/.git`)
before writing `harness.py` or running anything; the coordinator
completed `harness.py` and the README from the NL-TweedeDivisie
pattern (documented in the engine README) and ran dev. Every number
below was verified independently by the coordinator: the climatology
baseline was recomputed from the CSV with fresh code and matches
the engine exactly to 6 decimals on all three metrics (pooled and
per season); `dc.py` is byte-identical to NL-TweedeDivisie's
`dc.py`; the SHRINK lambda-change count (0) was measured by
re-running the arm comparison over all scored dev matches; a hand
spot-check recomputed one match's lambdas from the fitted ratings
and matched exactly; the dev run was repeated and reproduced
identical numbers (identical md5 of the full results JSON).
Calibration is stated as actual − predicted throughout this build.

## Verdict: FAIL — every arm dies at the dev gate (OU2.5 leg); virgin NOT read

Both arms beat climatology on pooled 1X2 LL and RPS, and both lose
the OU2.5 leg to the base-rate baseline on pooled dev — the same
shape as G-NLTD, G-NLE, and G-ESPF, but mirrored: there the league
was high-scoring and the over-rate baseline was strong; here the
league is low-scoring (scored-dev over-2.5 rate 29.4%) and the
under-rate baseline is strong. Under the frozen legs no arm passes
dev, so the virgin window was **not read** (the runner wrote
`results_virgin.json`:
`{"virgin_read": false, "reason": "no arm passed the dev gate"}`;
no 2025/2026 outcome was evaluated, no predictions file exists, no
fitted params exist) and **nothing ships**.

## Dev results (expanding season-blocked walk-forward, scored 2022/2023–2024/2025, n = 884)

| Season | GZ LL / RPS / OU | SHRINK LL / RPS / OU | Climatology LL / RPS / OU |
|---|---|---|---|
| 2022/2023 | 1.0530 / 0.2042 / 0.6324 | 1.0530 / 0.2042 / 0.6324 | 1.0482 / 0.2019 / 0.6247 |
| 2023/2024 | 1.0274 / 0.2027 / 0.6599 | 1.0274 / 0.2027 / 0.6599 | 1.0650 / 0.2148 / 0.6248 |
| 2024/2025 | 1.0617 / 0.2024 / 0.6087 | 1.0617 / 0.2024 / 0.6087 | 1.0880 / 0.2121 / 0.5762 |
| **Pooled** | **1.0471 / 0.2031 / 0.6337** | **1.0471 / 0.2031 / 0.6337** | **1.0678 / 0.2099 / 0.6079** |

Dev gate (pooled 1X2 LL **and** RPS beat climatology **and** OU2.5
LL beats the base-rate baseline): Gate Zero **FAIL** (OU 0.6337 >
0.6079). SHRINK **FAIL** (identical numbers — see below).

Three plain findings:

- **The ratings carry genuine 1X2 signal, and the totals
  distribution does not.** Pooled LL 1.0471 vs 1.0678 and RPS
  0.2031 vs 0.2099 are real wins, driven by 2023/2024 and
  2024/2025 (the model beats climatology on LL and RPS in both).
  But the model loses the OU2.5 leg in **all three** seasons
  (by 0.0077, 0.0352, and 0.0325), not just pooled: its predicted
  totals are systematically too high for a league whose over-2.5
  rate sits at 25–32%. The 2022/2023 season is the worst of both
  worlds for the model — it loses LL and RPS there too
  (1.0530 vs 1.0482; 0.2042 vs 0.2019) — the first season after
  the one-club-short year, with six new entrants starting at the
  league mean.
- **SHRINK is vacuous in this harness, as pre-recorded.** Under
  season-blocked fitting every non-entrant team has ≥ 32 training
  matches (shrink factor 1.0) and every entrant has 0 (rating 0 ×
  0 = 0, the league mean it starts from anyway). The arm changed
  0 of 884 scored lambdas; its byte-identical results are
  correct, not a bug. A shrink arm only has content under
  per-match refits.
- **The virgin regime would have been harder still, but the gate
  decided first.** The virgin season (2025/2026) is the
  lowest-scoring complete season in the corpus (1.60 goals/match,
  22.6% over-2.5, vs 1.87 / 29.4% in scored dev). The calibration
  leg was never reached, so no claim is made about it — the dev
  OU failure alone is the verdict.

## Virgin window — NOT read

No arm passed dev. No virgin metrics, no fitted params, no
predictions file for G-IRAZ. 2025/2026 and 2026/2027 were never
touched by any fit (the dev loader asserts the loaded season set).

## Other candidates — NOT buildable (no verdict files)

- S (SOT), C (corners), T (total shots): no target exists anywhere
  in the corpus — no stats feed, no shotmap — in any season,
  including the virgin window. Building them would break the gate
  rule.
- K (cards): no yellows exist (0 Yellow events in 1,564 matches);
  reds are 0.085/match with split-half r = 0.07 — a rare-event
  count with no reliability evidence.

## League completion state

League complete: the single buildable candidate (G-IRAZ) has been
through its gate (FAIL at dev, virgin deliberately unread) and the
four non-buildable candidates are documented as such with the
measured reason. Nothing ships; nothing joins the daily pipeline.
The 2026/2027 season (partial, n = 68) remains reserved as the
confirmatory window and was never touched.
