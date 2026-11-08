# Verdict — G-ENGCH (England Championship goals) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_G_ENGCH.md` (frozen bff7782, before fitting).
Dev = walk-forward 2022/2023–2024/2025 (n=1,671); virgin = 2025/2026
(n=555), **deliberately NOT read** — no arm passed the dev gate.

## Dev (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL | vs climatology (1.0752 / 0.2283 / 0.6926) |
|---|---|---|---|---|
| Gate Zero | 1.0529 | 0.2206 | 0.6991 | beats 1X2 + RPS; **OU leg FAIL** |
| SHRINK | 1.0529 | 0.2206 | 0.6991 | numerically identical to GZ (see below); **OU leg FAIL** |
| X2 (mover offset) | **1.0454** | **0.2181** | 0.6968 | best arm on every metric; **OU leg still FAIL** |
| Climatology | 1.0752 | 0.2283 | **0.6926** | — |

Gate arithmetic: the dev gate requires 1X2 LL + RPS to beat
climatology AND OU2.5 LL to beat the base-rate baseline. Every arm
clears the first two legs and loses the third — the DC's totals are
mis-scaled for this league even though its 1X2 is clearly skilful.
Per the frozen rule the verdict is FAIL, the virgin window was NOT
read (`engine/goals/results_virgin.json` records the guard's
`virgin_read: false`), and nothing ships.

Two honest footnotes, neither of which changes the verdict:
- **X2 works as designed.** The mover offset (mover lists
  hand-verified per season: e.g. 2024/2025 = Luton/Burnley/Sheffield
  Utd from PL, Portsmouth/Derby/Oxford from L1) improved pooled dev
  1X2 LL by −0.0074 and OU LL by −0.0023 over Gate Zero. The
  Championship's mover question has a real answer; it is the totals
  leg, not the movers, that kills this candidate. A future prereg
  could pair X2 with a totals-recalibration question — that is a
  new prereg's business, not a rescue arm here.
- **SHRINK ≡ Gate Zero by construction** in this league: with
  season-blocked fits, a club's prior in-league match count at
  prediction time is either 0 (identical rule) or ≥46 (factor 1.0)
  — the 1–5-match band the arm targets is empty. Same structural
  outcome as SCO.
