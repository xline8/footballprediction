# G-ME verdict — FAIL — virgin read, nothing ships

Prereg: `prereg/PREREG_G_ME.md`, frozen 2026-11-10 (commit
`5d9d733c`), before any fitting. Primary line **OU2.5**; dev scored
n = **539** (2022/2023–2024/2025); virgin 2025/2026 n = **180**,
read ONCE after dev froze (dev passed, so the virgin read was
required). Calibration is actual minus predicted. Engine:
`league/ME-1CFL/engine/goals/` (DC pattern copied verbatim from
sibling G-LT; independently re-run and verified by the builder —
all pooled and per-season numbers recomputed from
`results_dev.csv` by a separate code path match the harness
exactly, the dev run reproduces byte-identically, and every virgin
number was recomputed from the predictions CSV / fitted params by
a separate code path, including a train-only refit that reproduces
the stored virgin fit ratings exactly).

## Dev results — pooled (n = 539)

| Arm / baseline | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.069383 | 0.219356 | 0.684857 |
| SHRINK | 1.069383 | 0.219356 | 0.684857 |
| Climatology | 1.090641 | 0.226923 | 0.689907 |

Per-season Gate Zero 1X2 LL (model vs climatology): 2022/2023
1.056302 vs 1.092648 (beats); 2023/2024 1.083493 vs 1.089167
(beats); 2024/2025 1.068348 vs 1.090106 (beats). Per-season OU2.5
LL (model vs climatology): 0.696850 vs 0.693039 (loses); 0.710763
vs 0.691387 (loses); 0.646745 vs 0.685270 (beats). SHRINK coincides
with Gate Zero exactly (0 differing predictions, max |ΔP| = 0.0),
as the prereg's thin-data arithmetic implies: the only thin teams
are brand-new ids with 0 training matches, whose SHRINK factor is
0 and whose Gate Zero prior is a = d = 0; every other team has
≥ 6 training matches (factor 1).

**Dev gate: PASS for both arms** — pooled 1X2 LL, RPS and OU2.5 LL
all beat climatology. The OU leg is thin (margin 0.0051) and is
carried entirely by 2024/2025: the model loses the totals leg in
two of three dev seasons. That fragility is recorded here because
it is exactly what the virgin window then exposes.

## Virgin results — pooled (n = 180)

| Arm / baseline | 1X2 LL | RPS | OU2.5 LL | Home-win cal. | OU2.5 cal. |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 1.100431 | 0.237812 | 0.752933 | +3.68pp (SE 3.82) | −1.49pp (SE 3.94) |
| SHRINK | 1.100431 | 0.237812 | 0.752933 | +3.68pp (SE 3.82) | −1.49pp (SE 3.94) |
| Climatology | 1.071892 | 0.229902 | 0.684552 | +4.61pp (SE 3.72) | −3.04pp (SE 3.70) |

## Gate arithmetic

- **LL leg: FAIL for both arms.** Gate Zero virgin 1X2 LL 1.100431
  ≤ Gate Zero's own 1.100431 but NOT ≤ climatology's 1.071892
  (miss by 0.0285). The model is worse than the base rate on
  results in the virgin season, and worse on totals by more
  (OU2.5 LL 0.752933 vs 0.684552).
- **Calibration leg: PROVISIONAL PASS for both arms.** Home-win
  |+3.68pp| breaches the 1.0pp boundary by 2.68pp, within 1 SE
  (3.82pp); OU2.5 |−1.49pp| breaches by 0.49pp, within 1 SE
  (3.94pp). Both breaches are within noise at n=180 — the
  calibration leg passes provisionally, but it cannot rescue the
  LL leg.
- **Dev sign check: PASS for SHRINK** (3 of 3 dev seasons arm LL
  ≤ Gate Zero LL; ties count). Gate Zero is exempt.
- **Both-pass rule: no arm passes all legs, so nothing ships.**
  `shipped_arm` is null in `results_virgin.json`.

## Reading

The failure mode is a mirror of G-LT's dev failure, one step
later: the expanding DC fit beats climatology on results and (just)
on totals in dev, then loses both on the virgin season. The virgin
season itself is unusual against the dev distribution — home wins
45.0% (dev pooled 40.1%), draws 25.0%, goals 2.37/match with a home
edge of 0.38 goals (dev pooled 0.21) — and the virgin fit's home
advantage (h = 0.161, rho 0.0, mu 1.259) underweights that home
strength: the model under-predicts home wins by 3.68pp while
over-predicting totals by 1.49pp. The OU2.5 miss is the decisive
one (0.7529 vs base 0.6846): in a season where the over-rate fell
to 42.8%, the model's totals probabilities were further from the
truth than the base rate. SHRINK cannot rescue it — there is no
thin-team signal to shrink in the virgin season (every 2025/2026
team carries ≥ 36 prior matches), and SHRINK is identical to Gate
Zero there too. This is a complete, respectable FAIL: the league's
goals candidate passed dev and failed virgin. The confirmatory
window (2026/2027, in progress) remains reserved and unread.

## What ships

Nothing. `predictions/g_me_virgin_predictions.csv` contains Gate
Zero's 180 virgin predictions (shipped_arm empty, `shipped_arm`
null in `results_virgin.json`) for the record and for future
grading reference only — they are NOT a shipped product.
`fitted_params_virgin.json` records the virgin fit (h 0.161317,
rho 0.0, mu 1.259253, training_n 718, cutoff 2025-08-04).

## Notes from verification (no gate impact)

- Codex added one `over05` key to `dc.py`'s `probs()` return (for
  the 1H OU 0.5 presentation line). It changes no existing
  probability: the dev run reproduces byte-identically under the
  final `dc.py`, and all virgin probabilities recompute from the
  stored lambdas to < 3e-16. Recorded here as a deviation from the
  "verbatim copy" instruction, verified harmless.
- The `_calibration_leg` arithmetic string in the harness reads
  "abs(...) <= 1.0pp" even when the difference exceeds 1.0pp; the
  status logic itself (excess vs SE) is correct and was verified
  independently. Cosmetic only; not fixed post-hoc (no code is
  changed after the virgin read).
- S/C/K/T remain NOT BUILDABLE per
  `prereg/PREREG_SCKT_NOT_BUILDABLE_ME.md` (no stats, no shotmap
  shots, zero Yellow events, no referee — 0/971 rows).

**Ships:** nothing. League tally: 0 PASS / 1 FAIL / 4 NOT BUILDABLE.
