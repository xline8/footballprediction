# Verdict — K-QASD (QA-SecondDivision cards): **FAIL (dev gate)**

Frozen decision: PREREG_K_QASD.md (prereg commit
75aac0f17f333edbbb60e46a5fb8dbf3002f7577, before any fitting).
Virgin 2026/2027 was NOT read for cards: Gate Zero failed the dev
gate, so under the frozen mechanical reading the verdict is FAIL. Target
is event-unified yellows (Yellow + YellowRed), line 5.5.

Dev (within-season walk-forward over 2025/2026; warm-up rounds 1–7,
scored rounds 8–14, n = 28, date-grouped expanding fit; fit history
includes all 2024/2025 matches, 56, since card events exist throughout):

| Arm | LL @ 4.5 | LL @ 5.5 | LL @ 6.5 | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.7723 | 0.6575 | 0.5426 | FAIL |
| League base rate | 0.7687 | 0.6535 | 0.5284 | — |
| Naive trailing-10 | 0.8068 | 0.6783 | 0.5424 | — |

Gate Zero beats the naive baseline at the gate line 5.5 (0.6575 vs
0.6783) but loses to the league base rate (0.6575 vs 0.6535, by 0.0040
nats). The dev gate requires beating BOTH baselines, so the arm fails.
The margin is narrow — well inside sampling noise at n = 28 — but the
gate is mechanical and was pre-registered, so the verdict stands.

Diagnosis (recorded, not acted on): the scored block is a low-cards
block — actual over-5.5 rate 0.3214 (9/28) — and every method over-predicts
it (model mean_p 0.4581, base 0.4610, naive 0.4841; all +13.7pp or more).
The model and the league base rate are nearly identical in level (both
track the expanding league mean); the base rate's slightly flatter
per-match probs win the LL on this block by 0.0040 nats. Note also that
the estimated NB dispersion hit the seed's upper clamp (r = 500 for
model, base, and naive): the fit rows are under-dispersed relative to
Poisson (variance 4.18 vs mean 5.54), so the moment estimator has no
finite solution and the model is effectively Poisson — the seed's correct
behaviour on this data, verified independently, not a port artifact.

Correction history: the first implementation pass replaced the frozen
`State` (separate home/away attack/defence + FB_MU fallbacks) with a
single attack/defence per team and replaced per-method estimated NB r
with a fixed r = 500. It was discarded and re-ported verbatim from the
SA seed (`model.py` is now byte-identical to the seed); the r = 500
values in the corrected run come from the seed's own `estimate_r`
clamp, reproduced independently on the 84-row fit set. The corrected
dev numbers above are the ones that count; the first pass's numbers are
void and are not reported.

Verification (coordinator, independent of the builder): headline LLs
recomputed from `engine/cards/predictions_dev.csv` by a second path
match `results_dev.json` exactly (all nine numbers, full precision); the
28 scored match ids are exactly 2025/2026 rounds 8–14; dates end
2026-04-30; no `results_virgin.json` exists; the run was re-executed and
reproduced `results_dev.json` bit-identically. Latent defects found in
the (never-executed) virgin path — SA season count (94), the wrong
evaluation line (4.5 instead of the gate line 5.5), and the missing
2024/2025 history load — were fixed before this verdict (dev results
unchanged). One labelling wart was also fixed: the `baseline_league_p`
column in `predictions_dev.csv` now carries the seed's NB league-mean
baseline probs, not the flat over-rate.

Nothing ships for K-QASD. The 2026/2027 virgin stays unread for cards;
the confirmatory re-read at season end uses the corrected virgin path.
