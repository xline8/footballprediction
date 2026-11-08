# K-AT Verdict — AT-Bundesliga cards model (yellows)

Date: 2026-11-09. Branch `build/at-bundesliga`. Prereg:
`league/AT-Bundesliga/prereg/PREREG_K_AT.md` (commit c6f6cc1).
Engine: `league/AT-Bundesliga/engine/cards/` (J1 cards seed; referee
read directly from the AT CSV's `referee` column). Numbers from the
coordinator's own run. Primary line 4.5 (this league averages 4.07
yellows/match; J1's 2.5 line would be meaningless here).

## Verdict: FAIL — at the dev gate. Virgin window NOT read.

Gate Zero beats the league base rate but **loses to naive
trailing-10** pooled (0.6654 vs 0.6636) — the same failure shape as
K-J2. The referee arm X8 passes the dev gate outright (0.6561, best
of all), but the frozen rule is mechanical: *if Gate Zero fails its
own dev gate, the variants are moot — verdict FAIL regardless of
variant dev numbers, and the virgin window is not read.* K-AT is
therefore FAIL, nothing ships, and season 2025/2026 remains unread
by this candidate (no K-AT virgin predictions file exists,
deliberately). The X8 dev result is recorded below as the standing
diagnosis for any future prereg — it authorises nothing now.

## Dev results (per-match online walk-forward; scored 2022/2023–2024/2025, n=585)

LL@4.5:

| Season | n | Gate Zero | X8 | Base rate | Naive t-10 |
|---|---|---|---|---|---|
| 2022/2023 | 195 | 0.6527 | 0.6488 | 0.6556 | 0.6501 |
| 2023/2024 | 195 | 0.6779 | 0.6645 | 0.6834 | 0.6785 |
| 2024/2025 | 195 | 0.6657 | 0.6550 | 0.7018 | 0.6623 |
| **Pooled** | 585 | **0.6654** | **0.6561** | 0.6803 | 0.6636 |

(The pooled row is the gated one. The harness's own gate flags
agree: gate_zero False, x8 True. Note Gate Zero loses to naive in
all three dev seasons individually, not just pooled.)

Referee coverage in the scored dev seasons: ≥82% (virgin season
would have been 91.8% — the K-J1 failure mode, a referee-less
virgin window, does not occur here; it changes nothing under the
frozen rule).

## Per-leg verdicts

| Leg | Gate Zero | X8 |
|---|---|---|
| Dev gate (pooled LL@4.5 beats BOTH baselines) | FAIL (0.6654 > naive 0.6636) | PASS (0.6561) — moot |
| Virgin legs | not read | not read (rule) |

Reading: as in K-J2, the trailing-10 adapts to card-level shifts in
weeks while the ratings state carries the old regime for months;
Austria's yellows stepped between dev seasons (3.88–4.49/match).
The referee trait (F8, r=0.547) genuinely helps on dev — X8's
0.0093 LL gain over Gate Zero is the largest variant gain in this
league's whole build — and it still does not ship, because the gate
order is the gate order.

## Verification notes
- Coordinator ran the dev harness; its printed gate flags match the
  table. The harness reads referees from the CSV column (the J1
  warehouse-table dependency was removed in adaptation; the
  coordinator restored the seed's kickoff-UTC ordering key after
  Codex had downgraded it to date-only). Virgin isolation: dev
  loader's season set excludes 2025/2026 and 2026/2027 in code.
