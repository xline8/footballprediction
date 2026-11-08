# Verdict — G-BG2 (Bulgaria Second Professional League goals) — **FAIL** (dev gate, OU2.5 leg; virgin NOT read)

Prereg: `prereg/PREREG_G_BG2.md` (frozen dce6351, before fitting).
Dev = walk-forward 2022/2023–2024/2025 (pooled n=992), seed 2021/2022.
Virgin = 2025/2026 (n=272) — **deliberately NOT read**: no arm passed
the dev gate, per the prereg's mechanical reading.

## Dev (per season)
| Season | Arm | 1X2 LL | RPS | OU2.5 LL | Climatology LL / RPS / OU LL |
|---|---|---|---|---|---|
| 2022/2023 (n=306) | Gate Zero | 1.0355 | 0.2130 | 0.6970 | 1.0513 / 0.2183 / 0.6887 |
| 2023/2024 (n=306) | Gate Zero | 1.0510 | 0.2227 | 0.6805 | 1.0506 / 0.2230 / 0.6688 |
| 2024/2025 (n=380) | Gate Zero | 1.0501 | 0.2189 | 0.6591 | 1.0700 / 0.2258 / 0.6660 |
| **Pooled (n=992)** | **Gate Zero** | **1.0459** | **0.2183** | **0.6774** | **1.0582 / 0.2226 / 0.6739** |
| Pooled (n=992) | SHRINK | 1.0459 | 0.2183 | 0.6774 | identical to Gate Zero (see below) |

## Gate arithmetic (pooled dev, verbatim legs)
- 1X2 LL leg: 1.0459 < climatology 1.0582 ✓
- RPS leg: 0.2183 < climatology 0.2226 ✓
- **OU2.5 LL leg: 0.6774 > base-rate 0.6739 ✗ — FAIL.** The model
  beats climatology on results but is *worse than the base rate* at
  pricing the primary line (OU 2.5), losing the OU leg in two of
  three dev seasons (2022/2023 and 2023/2024, the league's two
  lowest-scoring seasons at 2.26 and 2.17 goals/match).
- SHRINK is numerically identical to Gate Zero in every dev season:
  under season-blocked expanding fits, no dev target-season team has
  1–5 prior in-league matches (verified directly: teams are either
  unseen, n=0 — 5/3/5 per season — or carry a full prior season), so
  the arm reduces to the n=0 case by construction, exactly as in
  G-SCO. It therefore fails the same OU leg; variants are moot.

**Verdict: FAIL. Nothing ships.** No fitted params, no predictions
CSV. `engine/goals/results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}` —
the 2025/2026 season remains untouched for a future pre-registered
attempt, and 2026/2027 remains reserved as confirmatory.

## Verification (coordinator-side, independent of the engine author)
- Climatology pooled dev LL (1.0582414703695666) and OU LL
  (0.6738545792983436) recomputed from the raw CSV by a separate
  script — exact match to the engine's results.
- `dc.py` is byte-identical to the proven SCO-Premiership reference;
  the dev harness loads only 2021/2022–2024/2025 (virgin seasons are
  unreachable in dev code paths).

## League completion state
S/C/K/T are documented **not buildable** (stats feed 0%, shotmap 0%,
referee 0% in all 1,735 warehouse files — see analysis/EDA.md F6 and
MODEL_DESIGN.md feasibility matrix). G-BG2, the only buildable
candidate, has run its full gate honestly to FAIL. **BG-SecondLeague
is complete: 0 PASS / 1 FAIL, 4 markets not buildable.** No market
joins the daily runner.
