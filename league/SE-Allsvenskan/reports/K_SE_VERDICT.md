# K-SE verdict — FAIL

Prereg: `league/SE-Allsvenskan/prereg/PREREG_K_SE.md` (frozen in
commit 62320f5, before any fitting). Primary line 3.5. Dev =
per-match walk-forward, warm-up 2021, scored seasons 2022–2024
(pooled n = 720); virgin = 2025.

## Dev results (pooled LL@3.5)

| Arm / baseline | LL@3.5 | Dev gate |
|---|---|---|
| Gate Zero (model) | 0.6917 | **FAIL** |
| X8 (model) | 0.6770 | pass (vs baselines) |
| League base rate | 0.6884 | |
| Naive trailing-10 | 0.6871 | |

## Gate arithmetic

The dev gate requires the pooled model LL@3.5 to beat **both**
baselines. Gate Zero beats neither: 0.6917 > 0.6884 (base rate)
and 0.6917 > 0.6871 (naive). **Gate Zero fails its own dev gate.**
Per the prereg's NOT-built clause, the variants are then moot —
X8's dev numbers (0.6770, better than both baselines) do not
rescue the candidate, because the design ships a variant only on
top of a Gate Zero that passes its own gate. **The virgin window
was deliberately NOT read** (`results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}`;
2025 stays usable only under a future new prereg's terms, and
2026 remains untouched as the confirmatory window).

Referee coverage in dev (for the record): named referees in 0/240
matches in 2021 (warm-up), 210/240 in 2022, 204/240 in 2023,
170/240 in 2024 — the X8 arm's fallbacks were exercised as
pre-registered and are recorded in `results_dev.json`.

**Verdict: FAIL. Nothing ships.** No predictions CSV, no fitted
virgin parameters. The reference cards pattern does not beat its
own naive component in SE dev — the referee trait (F8, r = 0.616)
helps the X8 arm on dev, but the gate structure forbids shipping
it over a failed Gate Zero, and no rescue arm may be invented
inside this prereg.
