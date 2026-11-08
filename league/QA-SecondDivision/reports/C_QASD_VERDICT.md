# Verdict — C-QASD (QA-SecondDivision corners): **FAIL (dev gate)**

Frozen decision: PREREG_C_QASD.md (prereg commit
75aac0f17f333edbbb60e46a5fb8dbf3002f7577, before any fitting).
Virgin 2026/2027 was NOT read for corners: Gate Zero failed the dev
gate, so under the frozen mechanical reading the verdict is FAIL. (The
prereg specifies Gate Zero only; no X7 arm was built.)

Dev (within-season walk-forward over 2025/2026; warm-up rounds 1–7,
scored rounds 8–14, n = 28, date-grouped expanding fit; fit history
includes the 2024/2025 stats era, 38 matches):

| Arm | LL @ 8.5 | LL @ 9.5 | LL @ 10.5 | Dev gate |
|---|---|---|---|---|
| Gate Zero (X9) | 0.6519 | 0.6956 | 0.5821 | FAIL |
| League base rate | 0.7665 | 0.6516 | 0.5775 | — |
| Naive trailing-10 | 0.7638 | 0.6508 | 0.5808 | — |

Gate Zero loses LL @ 9.5 to BOTH baselines (0.6956 vs 0.6516 / 0.6508,
by 0.0440 / 0.0447 nats), so the dev gate fails. The margin is large —
this is a genuine fail, not a borderline one.

Diagnosis (recorded, not acted on): the scored block is a low-corners
block — actual over-9.5 rate 0.3571 (10/28) — and the model over-predicts
it badly (mean predicted over-9.5 rate 0.4689, +11.2pp), while both
baselines sit close to the actual rate (0.3663 / 0.3787). The model's
fitted territorial/feature structure, carried over from the SA reference,
pushes its totals too high on this thin corpus. Notably the model is
much better than both baselines at 8.5 (0.6519 vs 0.7665 / 0.7638) and
roughly level at 10.5 — the failure is specific to the gate line 9.5,
but the gate is at 9.5 and was pre-registered, so the verdict stands.

Correction history: the first implementation pass replaced the frozen
`core.py` (GAMMAS, BP/BBC/BBT grids, FeatureBuilder, territorial min-8
rule, mu_cs, multiplier, fit_params) with a different file, and its
model LL @ 9.5 equalled the base-rate LL to full precision — an
impossible coincidence that indicated the model probs had been
overwritten by baseline probs. It was discarded and re-ported verbatim
from the SA seed; the corrected model now differs from the base rate
(max |Δp| = 0.2295 at 9.5). The corrected dev numbers above are the ones
that count; the first pass's numbers are void and are not reported.

Verification (coordinator, independent of the builder): headline LLs
recomputed from `engine/corners/predictions_dev.csv` by a second path
match `results_dev.json` exactly (all nine numbers, full precision); the
28 scored match ids are exactly 2025/2026 rounds 8–14; dates end
2026-04-30; no `results_virgin.json` exists; the run was re-executed and
reproduced `results_dev.json` bit-identically. Latent defects found in
the (never-executed) virgin path — SA season counts (304/94) and the
missing 2024/2025 history load — were fixed before this verdict (dev
results unchanged). One labelling wart was also fixed: the
`baseline_league_p` column in `predictions_dev.csv` now carries the
seed's NB league-mean baseline probs, not the flat over-rate.

Nothing ships for C-QASD. The 2026/2027 virgin stays unread for
corners; the confirmatory re-read at season end uses the corrected
virgin path.
