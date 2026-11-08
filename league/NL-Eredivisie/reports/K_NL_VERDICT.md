# K-NL Verdict — Eredivisie cards model

Date: 2026-11-09. Branch `build/nl-eredivisie`. Prereg:
`league/NL-Eredivisie/prereg/PREREG_K_NL.md` (commit 3c36b73, frozen
before any fitting). Engine: `league/NL-Eredivisie/engine/cards/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
all numbers below were reproduced by the coordinator's own rerun.
(This file replaces a stub the ported harness auto-writes; its gate
flags agreed with the reading below.)

## Verdict: FAIL — both arms die at the dev gate (base-rate leg)

Gate Zero loses the pooled dev LL@2.5 to the league base rate. The
referee arm (X8) is better than Gate Zero in **every** dev season
and better than the naive — and still loses to the base rate, by
0.00004. Under the frozen legs both arms are dead, the virgin
window was formally **not read**, and nothing ships. The
predictions CSV on file is the labelled Gate Zero fallback
(`arm = gate_zero`).

## Dev results (per-match walk-forward, warm-up 2021/2022, scored 2022/2023–2024/2025, n = 918)

LL@2.5 (binary log-loss on P(over 2.5)):

| Season | Gate Zero | X8 (referee) | Base rate | Naive t-10 |
|---|---|---|---|---|
| 2022/2023 | 0.6992 | 0.6961 | — | — |
| 2023/2024 | 0.6995 | 0.6878 | — | — |
| 2024/2025 | 0.6911 | 0.6844 | — | — |
| **Pooled** | **0.6966** | **0.689443** | **0.689401** | 0.7093 |

Dev gate (pooled LL@2.5 beats BOTH baselines): Gate Zero **FAIL**
(0.6966 > 0.6894; it beats only the naive). X8 **FAIL** (0.689443 >
0.689401 — a margin of 0.00004, but the leg is mechanical and it
is a loss). The harness's own `dev_gate_pass` flags record False
for both arms.

Reading: F8's referee trait is real in this league (split-half
r = 0.512, coverage 100%) and X8 captures something genuine — it
improves on Gate Zero by 0.0071 pooled and wins all three dev
seasons head-to-head. What it cannot do is beat simply predicting
the league's prior over-2.5 rate: Eredivisie yellows are stable
enough at league level (2.84–3.12 per season) that the base rate
is a hard hurdle at line 2.5, and neither ratings nor referee
signal clear it. That is a finding, not a near-miss to be rescued:
no rescue arm is permitted under this prereg.

## Virgin window — formally UNREAD (harness fallback figures recorded)

The ported runner's fallback path computed Gate Zero on 2025/2026
while writing the labelled predictions file. For the record
(n = 306): Gate Zero LL@2.5 **0.6604** vs base rate 0.6732 and
naive 0.6717 (it would pass leg (i)); calibration **−4.26pp**
(SE 2.76pp — breach of 3.26pp beyond the 1.0pp boundary, beyond
1 SE → would FAIL leg (ii): the virgin season ran hot on cards,
over-2.5 rate 61.4%, and the model under-predicted it). So the
fallback figures fail on their own terms too; the formal verdict
rests on the dev gate. The window should be considered burned
for K-NL; a future attempt needs a new prereg and should treat
2025/2026 as dev-era data.

Referee operational check (design §4c condition ii): warehouse
referee coverage is 100% in dev and virgin, and on the virgin
window X8 recorded 0 unknown-identity and 3 thin-history fallbacks
— but warehouse records are post-match snapshots with no
publication timestamp, so whether appointments are public before
kickoff in the live pipeline remains unproven, exactly as in
K-J1. The point is moot for this candidate (the arm is dead), and
recorded so a future prereg inherits the caveat.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun reproduces every dev and virgin number
  exactly; pooled LLs above were recomputed by the coordinator
  from the per-season results (n-weighted) and match the harness's
  gate flags.
- Ordering note: the ported harness processes matches by kickoff
  timestamp (tie-break match_id) rather than the prereg's
  (date, match_id) — an inherited port behaviour, causally
  stricter within a day except for simultaneous kickoffs, where
  sequence order applies. Recorded for transparency; it does not
  change any gate reading (both arms fail by margins of opposite
  character: GZ by 0.0072, X8 by 0.00004 — the X8 margin is small
  enough that ordering could matter in principle, which is itself
  a reason the frozen FAIL stands as the honest outcome rather
  than a re-run under a friendlier order).
- Virgin isolation: scored dev seasons are 2022/2023–2024/2025;
  2026/2027 is never scored by any step.
