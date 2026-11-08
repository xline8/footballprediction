# G-NO Verdict — NO-Eliteserien goals model

Date: 2026-11-09. Branch `build/no-eliteserien`. Prereg:
`league/NO-Eliteserien/prereg/PREREG_G_NO.md` (commit 48330b5).
Engine: `league/NO-Eliteserien/engine/goals/` (J1 goals engine seed
via AT). Numbers from the coordinator's own runs (dev rerun
reproduces the implementer's exactly). Predictions-only scope.

## Verdict: FAIL — every arm fails the dev gate. Nothing ships. Virgin NOT read.

All three arms beat climatology on 1X2 LL (pooled 1.0149 vs 1.0606)
but the frozen gate is read on **OU 2.5 log-loss**, and there the
league's high, stable over-rate (dev 60.4%) makes climatology brutal:
every arm loses to it pooled, driven by 2022–2023 (in 2024 every arm
beats climatology). Per the frozen rule — Gate Zero fails its own dev
gate ⇒ verdict FAIL regardless of variant numbers, virgin not read —
season 2025 remains unburned by this candidate.

## Dev results (season-blocked expanding fits; scored 2022–2024, n=720)

OU 2.5 log-loss:

| Season | n | Gate Zero | SHR | X3 | Climatology |
|---|---|---|---|---|---|
| 2022 | 240 | 0.6876 | 0.6775 | 0.6860 | 0.6475 |
| 2023 | 240 | 0.6947 | 0.6947 | 0.7201 | 0.6731 |
| 2024 | 240 | 0.6617 | 0.6650 | 0.6717 | 0.7015 |
| **Pooled** | 720 | **0.6813** | **0.6791** | **0.6926** | **0.6740** |

Dev gate (pooled OU LL beats climatology): GZ FAIL, SHR FAIL,
X3 FAIL. 1X2 LL pooled (record only): GZ 1.0149, SHR 1.0173,
X3 1.0255, climatology 1.0606.

## Per-leg verdicts

| Leg | Gate Zero | SHR | X3 |
|---|---|---|---|
| Dev gate | FAIL (0.6813 > 0.6740) | FAIL (0.6791 > 0.6740) | FAIL (0.6926 > 0.6740) |
| Virgin (i)–(iii) | not read | not read | not read |
| **Overall** | **FAIL** | **FAIL** | **FAIL** |

## Notes
- The SHR shrinkage arm did what it was designed to do in 2022 (the
  season of promoted-club openers: 0.6775 vs GZ 0.6876) but gave it
  back in 2024 (0.6650 vs 0.6617); pooled it still loses to
  climatology. The X3 set-play tilt hurt in 2023 (0.7201).
- Recorded caveat (F11): the 2022 xG feed runs low (goals/xG 1.216),
  which handicaps the blend in exactly the dev season where the gate
  was lost by the widest margin. That is context, not a rescue: the
  gate is frozen and no corrected-xG arm may be invented under this
  prereg.
- This is the program's recurring goals pattern (G-AT, G-US, G-AU,
  G-DK, G-BR, G-AR all failed; the DC pattern keeps losing an OU gate
  to a strong climatology in high-over-rate leagues). Norway's 60.4%
  dev over-rate is the highest of those.

## Verification notes
- Coordinator reran dev from the committed engine; pooled LLs match
  the implementer's run to 6 decimals. Pooled = simple mean of the
  three season LLs (equal n=240), checked arithmetically.
- Virgin isolation: the dev loader's season set is {2021, 2022, 2023,
  2024} in code; no 2025/2026 row was loaded by any G-NO run.
