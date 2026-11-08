# C-NL Verdict — Eredivisie corners model

Date: 2026-11-09. Branch `build/nl-eredivisie`. Prereg:
`league/NL-Eredivisie/prereg/PREREG_C_NL.md` (commit 3c36b73, frozen
before any fitting). Engine: `league/NL-Eredivisie/engine/corners/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
all numbers below were reproduced by the coordinator's own rerun.

## Verdict: FAIL — Gate Zero dies at the dev gate on the frozen baseline definition; X7 dies everywhere

This verdict turns on a baseline discrepancy that is reported in
full, because it decides the outcome:

- The **frozen NL prereg text** defines the league base rate as a
  constant probability: "for target season S, P(over 10.5) = the
  over-10.5 rate of all matches in seasons strictly before S,
  scored as a constant probability."
- The **harness** (the J1 port of production `model_corners_v3`)
  implements the corners family's own base rate: one NB per season
  scored at the decay-weighted base mean with the moment ratio
  `r_base` — which is how J1's prereg defined it for J1. In this
  league that NB baseline is badly off-centre (mean P(over 10.5) =
  0.349 against an actual rate of 0.466) and therefore weak.

Judged against the baseline the prereg actually froze — the
constant over-rate, computed by the coordinator from the data —
Gate Zero's pooled dev LL@10.5 (**0.7058**) does **not** beat the
base rate (**0.7014**). The dev gate fails, the virgin window was
formally not read, and **nothing ships**. Changing the baseline
definition after seeing this table would be moving the gate; if
the program wants the corners-family NB baseline for this league,
that takes a new prereg, not a reinterpretation of this one.

Under the port's NB baseline the picture would have been the
opposite (Gate Zero beats it and the naive on dev, and posts a
provisional-pass virgin) — those numbers are tabled below so the
coordinator can judge the discrepancy with everything on the page.

## Dev results (chronological walk-forward, scored 2022/2023–2024/2025, n = 918)

LL@10.5 (binary log-loss on P(over 10.5)):

| Season | Gate Zero | X7 | Port NB base rate | Naive t-10 | **Constant base rate (frozen text)** |
|---|---|---|---|---|---|
| 2022/2023 | 0.7160 | 0.8310 | 0.7530 | 0.7357 | — |
| 2023/2024 | 0.7272 | 0.8291 | 0.7423 | — | — |
| 2024/2025 | 0.6741 | 0.6962 | 0.6701 | — | — |
| **Pooled** | **0.7058** | **0.7854** | 0.7218 | 0.7164 | **0.7014** |

(The constant-rate baseline is a single pooled figure by
construction of the check: each dev season scored at its
prior-seasons over-rate, n-weighted. Per-season constant rates
were not separately tabled; the pooled comparison is the gate's.)

Dev gate (pooled LL@10.5 beats BOTH baselines):
- Gate Zero vs the frozen-text baselines: 0.7058 > **0.7014**
  (constant base rate) → **FAIL**. (Against the port's baselines it
  would pass: 0.7058 < 0.7218 and < 0.7164.)
- X7: 0.7854 — loses to every baseline under either definition →
  **FAIL**, unconditionally. The box-touch multiplier was never
  selected (β_bt = 0 in every fit window — the F9 trait is real,
  r = 0.959, but worth zero inside this multiplier structure, the
  same outcome as C-J1), and stripped of Gate Zero's X9 multiplier
  the arm's core is badly off-centre on dev (mean P(over 10.5)
  0.576 vs actual 0.466). X7 active share (both teams, min-8 rule
  satisfied): 95.8% of dev matches — the arm was genuinely active
  and genuinely worse.

## Virgin window — formally UNREAD (harness figures recorded)

With no arm passing the dev gate as frozen, the 2025/2026 window
was not read for C-NL. The harness did evaluate Gate Zero there
while producing the labelled fallback predictions file; for the
record: Gate Zero virgin LL@10.5 **0.6929**, calibration −2.73pp
(SE 2.86pp); the frozen-text constant base rate on the virgin
window is **0.6920** — Gate Zero would fail virgin leg (i) against
it as well (by 0.0009), while beating the port NB baseline
(0.7209) and naive (0.7166). The window should be considered
burned for C-NL purposes; a future corners attempt under a new
prereg should treat 2025/2026 as dev-era data.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun (after a coordinator fix to the runner's
  selection block, which still carried J1's line 9.5 and J1 season
  labels — the fix changed no fitted number) reproduces every dev
  and virgin figure exactly.
- The engine core (`core.py`) is byte-identical to the J1 port
  apart from naming — the adaptation introduced no drift; the
  discrepancy above is a prereg-text vs reference-implementation
  definition clash, surfaced by verification, not a code bug.
- Constant-rate baselines were computed by the coordinator
  directly from `nl_matches.csv` (prior-seasons over-10.5 rates,
  per-season scoring, n-weighted pooling) — a second path,
  independent of the harness.
- Virgin isolation: the dev loader takes seasons
  2021/2022–2024/2025 only; 2026/2027 is loaded by no step.
