# Verdict — K-SAFD (SA-FirstDivision unified event yellows) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_K_SAFD.md`, frozen 2026-11-10. Target is
`yellow_home + yellow_away`, the event-feed Yellow + YellowRed count.
Gate Zero is the only arm. The dev walk-forward used 90 warm-up matches
and 214 scored matches, date-grouped predict-then-update.

## Dev gate (LL@4.5)

| Scope | Gate Zero | League base rate | Naive trailing-10 |
|---|---:|---:|---:|
| 2025/2026 scored block, pooled | 0.711231 | 0.694486 | 0.704901 |

Gate arithmetic: 0.711231 is worse than both required baselines
(0.694486 and 0.704901). `dev_gate_pass = false`. Gate Zero therefore
fails and the virgin was **deliberately unread**; 2026/2027 remains
TRANSITIONAL and reserved for a later confirmatory read.

**Ships: nothing.** `engine/cards/results_virgin.json` records
`{"virgin_read": false, "reason": "Gate Zero failed dev gate"}` and
`fitted_params_virgin.json` is an explicit unfitted stub with zero
training rows and empty params. No prediction CSV was written.

Verification: dev n=214, ladder 3.5/4.5/5.5, Gate Zero only, no referee
arm, and no virgin data was loaded after the failed gate.

Verifier's note (coordinator, 2026-11-10): the league-base-rate
baseline implemented here follows the SA reference port — the
decay-weighted league-mean total (mh+ma) passed through the
warm-up-fitted NB (r = 500) — rather than the raw expanding
over-4.5 rate written in the prereg's baseline parenthetical.
Recomputed prereg-literal baselines: base rate 0.697605, naive
0.704901 (identical to the harness naive, which IS the
prereg-literal trailing-10 construction). The model (0.711231)
loses to both baselines under either construction, so the FAIL
verdict is unaffected. The prereg text is left frozen; this note
records the discrepancy. Independent replay of the dev gate from
the engine code reproduces all three LLs exactly (model 0.711231,
base 0.694486, naive 0.704901).
