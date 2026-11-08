# G-NL Verdict — Eredivisie goals model

Date: 2026-11-09. Branch `build/nl-eredivisie`. Prereg:
`league/NL-Eredivisie/prereg/PREREG_G_NL.md` (commit 3c36b73, frozen
before any fitting). Engine: `league/NL-Eredivisie/engine/goals/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
all numbers below were reproduced by the coordinator's own rerun
(results files byte-identical, params stripped).

## Verdict: FAIL — every arm dies at the dev gate (OU2.5 leg)

All three arms beat climatology comfortably on 1X2 LL and RPS, and
all three **lose the OU2.5 leg to the base-rate baseline** on pooled
dev. Under the frozen gate legs no arm passes dev, so the virgin
window was formally **not read**. The harness's fallback path did
evaluate Gate Zero on 2025/2026 (recorded below for transparency —
it changes nothing: Gate Zero's virgin OU calibration also fails).
Nothing ships. The predictions CSV on file is the labelled Gate
Zero fallback (`arm = gate_zero`).

## Dev results (expanding season-blocked walk-forward, scored 2022/2023–2024/2025, n = 918)

| Season | GZ LL / OU | X2 LL / OU | X3 LL / OU | Climatology LL / OU |
|---|---|---|---|---|
| 2022/2023 | 0.9662 / 0.6891 | 0.9451 / 0.6978 | 0.9735 / 1.0683 | 1.0707 / 0.6788 |
| 2023/2024 | 0.9403 / 0.6849 | 0.9417 / 0.6906 | 0.9916 / 1.2113 | 1.0751 / 0.6634 |
| 2024/2025 | 0.9708 / 0.6754 | 0.9773 / 0.6789 | 1.0106 / 1.0272 | 1.0689 / 0.6914 |
| **Pooled** | **0.9591 / 0.6831** | **0.9547 / 0.6891** | **0.9919 / 1.1023** | 1.0715 / **0.6778** |

Pooled RPS: GZ 0.1934, X2 0.1917, X3 0.1977, climatology 0.2309.

Dev gate (pooled 1X2 LL **and** RPS beat climatology **and** OU2.5
LL beats the base-rate baseline): Gate Zero **FAIL** (OU 0.6831 >
0.6778). X2 **FAIL** (OU 0.6891 > 0.6778 — the newcomer priors help
1X2/RPS, LL 0.9547 is the best of the three, but they make the OU
leg worse, not better). X3 **FAIL** (OU 1.1023 — the set-play tilt
is catastrophic on totals in this league: its multipliers push
lambdas in exactly the wrong direction for the over/under split,
in every dev season).

Reading: this is the G-J1 pattern one step earlier — the DC
ratings carry real 1X2 signal (LL ~0.96 vs 1.07 climatology) but
the model's total-goals distribution is not better than the
league's own base rate at OU2.5 in a league whose over-rate swings
55–64% between seasons (EDA F1). The gate is doing its job.

## Virgin window — formally UNREAD (harness fallback figures recorded)

No arm passed the dev gate, so under the prereg the 2025/2026
window was not read for G-NL. The ported runner's fallback path
nevertheless computed Gate Zero on the virgin window while
producing the labelled predictions file; those figures are
recorded here so the partial burn is explicit, not hidden:

- Gate Zero virgin (n = 306): 1X2 LL 0.9834 (climatology 1.0736),
  RPS 0.1976, OU LL 0.6641.
- Calibration: home-win diff **+0.59pp** (SE 2.64pp — clean);
  OU2.5 diff **−6.56pp** (SE 2.76pp — breach of 5.56pp beyond the
  1.0pp boundary, i.e. beyond 1 SE → would FAIL leg (ii) as well:
  2025/2026 ran hot, over 61.8%, and the model under-predicted it).

So even under the most generous reading — treating the fallback
evaluation as a read — G-NL fails two independent legs. The
2025/2026 window should be considered burned for G-NL purposes;
any future goals attempt needs a new prereg and should treat
2025/2026 as dev-era data, with 2026/2027 (once complete) as its
virgin.

## Verification notes (coordinator, independent of Codex)

- Full harness rerun reproduces every dev and virgin number
  exactly (results JSONs identical with runtime/params stripped).
- Dev/virgin isolation confirmed in code: the dev loader takes
  seasons 2021/2022–2024/2025 only; 2026/2027 is never loaded by
  any step.
- X2 activation: 3 newcomer clubs per season get the offset in
  their first season (the arm's pooled 1X2 improvement over Gate
  Zero, 0.9547 vs 0.9591, is consistent with a real but small
  effect concentrated in those clubs' matches).
- Codex could not commit from its sandbox; the commits on
  `build/nl-eredivisie` were made by the coordinator, as in the
  J.League flow.
