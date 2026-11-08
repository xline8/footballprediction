# G-CY2 verdict — FAIL — virgin NOT read

Prereg: `prereg/PREREG_G_CY2.md`, frozen 2026-11-10 (commit
`3a2d6f0a`), before any fitting. Primary line **OU2.5**; dev scored
n = **682** (2022/2023–2024/2025); calibration is actual minus
predicted. Engine: `league/CY-2Division/engine/goals/` (DC pattern
copied from sibling G-CY; independently re-run and verified by the
builder — climatology recomputed from the CSV by a separate code
path matches the harness exactly).

## Dev results — pooled (n = 682)

| Arm / baseline | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.074895 | 0.239335 | 0.721043 |
| X2 | 1.084642 | 0.241676 | 0.724094 |
| SHRINK | 1.074895 | 0.239335 | 0.721043 |
| Climatology | 1.064304 | 0.239718 | 0.695637 |

Per-season Gate Zero 1X2 LL (model vs climatology): 2022/2023
1.060066 vs 1.080591 (beats); 2023/2024 1.120043 vs 1.073148
(loses); 2024/2025 1.043681 vs 1.040154 (loses). Per-season OU2.5
LL (model vs climatology): 0.694581 vs 0.687076; 0.731072 vs
0.695362; 0.735881 vs 0.703956 — the model loses the totals leg in
all three seasons. X2's dev sign check vs Gate Zero is 1/3
(2022/2023 only). SHRINK coincides with Gate Zero exactly, as
the prereg expected (every non-new team has ~30 training matches;
new teams are already at the league mean).

## Gate arithmetic

Dev gate requires pooled 1X2 LL **and** RPS **and** OU2.5 LL all to
beat climatology. Gate Zero beats climatology only on RPS
(0.239335 vs 0.239718, by 0.0004) and loses on 1X2 LL (1.074895
vs 1.064304) and on OU2.5 LL (0.721043 vs 0.695637). **Gate Zero
fails its dev gate.** Per the frozen rule (Gate Zero fails dev ⇒
variants moot), X2 and SHRINK are moot regardless of their own
numbers, the virgin window was NOT read, and nothing ships. No
virgin predictions file and no fitted-params file exist;
`engine/goals/results_virgin.json` is the not-read marker
(`{"virgin_read": false, ...}`).

## Reading

The failure mode mirrors sibling G-CY (pooled OU2.5 LL 0.7302 vs
base rate 0.6989): in a 16-team second tier with 2–4 team
turnover every season and only 29–30 matches per team-season,
the expanding DC fit cannot beat the base rate on totals — the
model's over/under calibration is worse than climatology in every
dev season. The X2 mover offset does not rescue it (X2 is worse
than Gate Zero pooled on all three metrics). This is a complete,
respectable FAIL: the league's goals candidate is not buildable
under the frozen gates. The confirmatory window (2026/2027)
remains reserved and unread.

**Ships:** nothing.
