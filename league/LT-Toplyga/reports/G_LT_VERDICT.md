# G-LT verdict — FAIL — virgin NOT read

Prereg: `prereg/PREREG_G_LT.md`, frozen 2026-11-10 (commit
`2bd771ea`), before any fitting. Primary line **OU2.5**; dev scored
n = **720** (2022–2025); calibration is actual minus predicted.
Engine: `league/LT-Toplyga/engine/goals/` (DC pattern copied from
sibling G-CY2; independently re-run and verified by the builder —
all pooled and per-season numbers recomputed from
`results_dev.csv` by a separate code path match the harness
exactly, and the run reproduces byte-identically on re-execution).

## Dev results — pooled (n = 720)

| Arm / baseline | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.033968 | 0.213597 | 0.703992 |
| SHRINK | 1.033968 | 0.213597 | 0.703992 |
| Climatology | 1.083879 | 0.232674 | 0.693432 |

Per-season Gate Zero 1X2 LL (model vs climatology): 2022
0.975049 vs 1.079910 (beats); 2023 1.006679 vs 1.080485 (beats);
2024 1.117187 vs 1.095175 (loses); 2025 1.036958 vs 1.079947
(beats). Per-season OU2.5 LL (model vs climatology): 0.720873 vs
0.693147; 0.697728 vs 0.693147; 0.674405 vs 0.688128 (beats);
0.722963 vs 0.699307 — the model loses the totals leg in three of
four seasons. SHRINK coincides with Gate Zero exactly (0 differing
predictions, max |ΔP| = 0.0), as the prereg's thin-data arithmetic
implies: the only thin teams are brand-new ids with 0 training
matches, whose SHRINK factor is 0 and whose Gate Zero prior is
a = d = 0; every other team has ≥ 6 training matches (factor 1).

## Gate arithmetic

Dev gate requires pooled 1X2 LL **and** RPS **and** OU2.5 LL all to
beat climatology. Gate Zero beats climatology on 1X2 LL (1.033968
vs 1.083879) and on RPS (0.213597 vs 0.232674) but loses on OU2.5
LL (0.703992 vs 0.693432). **Gate Zero fails its dev gate.** Per
the frozen rule (Gate Zero fails dev ⇒ variants moot), SHRINK is
moot regardless of its own numbers, the virgin window was NOT
read, and nothing ships. No virgin predictions file and no
fitted-params file exist; `engine/goals/results_virgin.json` is
the not-read marker (`{"virgin_read": false, ...}`).

## Reading

The failure mode mirrors sibling G-CY2 (pooled OU2.5 LL 0.7302 vs
base rate 0.6989): in a 10-team top tier with 1–2 team turnover
every season, the expanding DC fit beats the base rate on results
but cannot beat it on totals — the model's over/under
probabilities are worse than climatology in three of four dev
seasons. The base rate itself is hard to beat here: the dev
over-rate at OU2.5 is 0.4681, so climatology's OU LL (0.6934)
sits almost at the binary-entropy floor and any totals
miscalibration is punished in full. SHRINK cannot rescue it —
there is no fitted-rating signal to shrink for a brand-new team,
and returning teams already carry full training histories. This
is a complete, respectable FAIL: the league's goals candidate is
not buildable under the frozen gates. The virgin window (2026,
n = 144, complete) and the confirmatory window (2027) remain
reserved and unread.

Observation for the record (not a gate change, not a rescue):
the fitted rho sits at the grid boundary −0.15 in three of four
dev fits (2022–2024; 2025 picks 0.0), and fitted home advantage
is small (0.07–0.15 vs the 0.28 init, consistent with the
measured +0.17-goal home edge). The rho grid is the frozen
production grid and was not widened after seeing this.

## Defect found and fixed during verification

The first engine draft gave unseen teams the fitted mean rating
(`mean_a`/`mean_d`, e.g. −0.163/+0.128 for the 2024 fit) as
their prior instead of the prereg-literal a = d = 0, which
changed Gate Zero on the 104 dev matches involving new teams
and manufactured a spurious SHRINK-vs-Gate-Zero difference on
exactly those matches. The builder caught it by comparing the
arm code against the G-CY2 seed (`defaultdict(float)` = 0.0),
fixed the fallback to 0.0, and re-ran: the numbers in this
verdict are the corrected ones, reproduced byte-identically on
re-execution and recomputed independently from the CSV.

**Ships:** nothing.
