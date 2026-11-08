# C-NLE Verdict — Eerste Divisie corners model

Date: 2026-11-09. Branch `build/nl-eerste`. Prereg:
`league/NL-EersteDivisie/prereg/PREREG_C_NLE.md` (commit f267312,
frozen before any fitting). Engine:
`league/NL-EersteDivisie/engine/corners/`. Implementation by
Codex (gpt-5.6-luna); dev and virgin headline numbers were
recomputed independently by the coordinator from the per-match
predictions CSVs. Calibration = actual − predicted.

## Verdict: FAIL — Gate Zero passes dev and the virgin LL leg, then fails the virgin calibration leg; X7 fails dev everywhere

Gate Zero is a genuinely good corners model in this league on
log-loss (dev and virgin both beat every baseline), and the
frozen calibration leg still kills it: the virgin season ran
very hot on corners (actual over-9.5 rate 64.5% vs a dev-era
~54–55%) and the model's mean probability of 60.0% leaves a
+4.47pp breach, beyond 1 SE. **Nothing ships.** No rescue arm is
permitted under this prereg.

## Dev results (chronological walk-forward, scored 2022/2023–2024/2025, n = 1140)

LL@9.5 (binary log-loss on P(over 9.5)):

| Season | Gate Zero | X7 | Base rate (constant, frozen text) | Naive t-10 (core NB) |
|---|---|---|---|---|
| 2022/2023 | 0.6954 | 0.9252 | — | — |
| 2023/2024 | 0.6953 | 0.7753 | — | — |
| 2024/2025 | 0.6817 | 0.6954 | — | — |
| **Pooled** | **0.6908** | 0.7986 | **0.6955** | 0.7446 |

Baseline note, reported in full because the C-NL verdict turned
on exactly this: the ported harness's internal `league_base_rate`
is the corners family's NB at the season base mean (pooled dev LL
0.7464), **not** the constant prior-seasons over-rate the NLE
prereg froze. The coordinator recomputed the frozen constant
baseline from the league CSV: pooled **0.6955**. Gate Zero beats
both definitions (0.6908 < 0.6955 and < 0.7464) and beats the
naive under both the core's NB scoring (0.7446) and the
coordinator's independent trailing-10 recomputation (0.702–0.707
across NB-size choices, min-6 window, date-grouped). The dev gate
outcome is definition-invariant here; the frozen-text numbers are
the ones tabled above.

Dev gate: Gate Zero **PASS**. X7 **FAIL** (0.7986 loses to every
baseline under every definition — the box-touch multiplier was
never competitive in this league despite touches reliability of
0.875/0.918 in EDA; with coverage at 72–85% in the early seasons
its active share and fitted betas never stabilised). Only Gate
Zero was read on the virgin window.

## Virgin results (season "2025/2026", n = 380, read once after dev froze)

Actual over-9.5 rate 64.47%; mean total corners 10.78 (dev mean
10.07 — a hot virgin season).

| Arm | LL@9.5 | Mean P(over 9.5) | Calib (actual − pred) | Calib SE |
|---|---|---|---|---|
| Gate Zero | **0.6553** | 60.00% | +4.47pp | 2.46pp |
| Base rate (constant) | 0.6691 | 55.00% | +9.47pp | — |
| Naive t-10 (core NB) | 0.7611 | — | — | — |

## Per-leg verdicts

| Leg | Gate Zero |
|---|---|
| Dev gate | PASS |
| Virgin (i) LL ≤ best baseline (0.6691) | PASS (0.6553) |
| Virgin (ii) calibration ≤1.0pp (breach ≤1 SE = provisional) | **FAIL** (breach 3.47pp > SE 2.46pp) |
| **Overall** | **FAIL — nothing ships** |

Reading: discrimination is not the problem — 0.6553 is the best
virgin LL posted by any candidate in this league — level is.
The model under-predicted a structural-looking hot season by
4.5pp at the primary line, outside the frozen tolerance. If a
future prereg wants this market, 2025/2026 is now dev-era data
and the level question has to be answered there, not by moving
this gate.
