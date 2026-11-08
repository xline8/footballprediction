# G-AT Verdict — AT-Bundesliga goals model

Date: 2026-11-09. Branch `build/at-bundesliga`. Prereg:
`league/AT-Bundesliga/prereg/PREREG_G_AT.md` (commit c6f6cc1, frozen
before any fitting). Engine: `league/AT-Bundesliga/engine/goals/`
(DC core copied unmodified from the J1 engine). Implementation by
Codex (gpt-5.6-luna) under the two-agent flow; all numbers below are
from the coordinator's own run of the engine.

## Verdict: FAIL — at the dev gate. Virgin window NOT read.

Gate Zero beats climatology decisively on 1X2 LL and RPS, but the
prereg gates this candidate on the OU 2.5 log-loss, and there Gate
Zero **loses to climatology pooled** (0.7036 vs 0.6946). Both variant
arms lose too. Under the frozen rule (Gate Zero fails its dev gate →
variants moot, virgin not read), G-AT is FAIL and nothing ships.
Season 2025/2026 remains unread by this candidate; no virgin
predictions file exists for G-AT, deliberately.

## Dev results (season-blocked expanding fits; scored 2022/2023–2024/2025, n=585)

OU 2.5 log-loss (the gated metric; lower is better):

| Season | n | Gate Zero | SHR | X3 | Climatology |
|---|---|---|---|---|---|
| 2022/2023 | 195 | 0.6957 | 0.6949 | 0.7043 | 0.6813 |
| 2023/2024 | 195 | 0.7041 | 0.7061 | 0.7192 | 0.7135 |
| 2024/2025 | 195 | 0.7110 | 0.7084 | 0.7243 | 0.6889 |
| **Pooled** | 585 | **0.7036** | **0.7032** | **0.7159** | **0.6946** |

For the record (not gated): pooled 1X2 LL — GZ 1.0029, SHR 1.0049,
X3 1.0188 vs climatology 1.0910; pooled RPS — GZ 0.2030 vs
climatology 0.2312. The DC ratings carry real result signal in this
league; what they do not beat is the league's own OU base rate —
Austria's over-2.5 rate is high (dev 53.7%) and stable enough that
climatology is a hard OU baseline, and the model's OU probabilities
are not sharp enough to beat it in two of three dev seasons.

## Per-leg verdicts

| Leg | Gate Zero | SHR | X3 |
|---|---|---|---|
| Dev gate (pooled OU LL < climatology 0.6946) | FAIL (0.7036) | FAIL (0.7032) | FAIL (0.7159) |
| Virgin legs | not read | not read | not read |

Reading of the variants: the thin-team shrinkage arm (SHR) is a wash
(0.7032 vs 0.7036 — the promoted-team problem it targets is small in
a 12-team league with 195-match seasons, and the OU leg was never
going to be rescued by it); the set-play tilt (X3) actively hurts
(0.7159), the opposite of its dev behaviour in J1 — F5's trait is
real (r=0.477) but this tilt structure does not convert it.

## Verification notes
- Coordinator reran the dev harness end-to-end; table above is that
  run's output. Dev loader filters to seasons 2021/2022–2024/2025 in
  code (2025/2026 and 2026/2027 are never opened by the dev path).
- Arm activation checked: SHR and X3 predictions differ from Gate
  Zero (pooled LLs differ; X3 multipliers computed from the AT xG
  splits — the coordinator inspected the adapted `arms.py` league
  accumulation after a first-pass concern and found it correct).
