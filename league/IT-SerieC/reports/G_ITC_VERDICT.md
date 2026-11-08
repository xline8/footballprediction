# Verdict — G-ITC (Italy Serie C goals) — **FAIL** (dev gate, OU2.5 leg; virgin NOT read)

Prereg: `prereg/PREREG_G_ITC.md` (frozen abd5a8e, before fitting).
Modeling set: regular-phase matches only (5,936 of 6,184 finished;
playoffs/playouts/Super Cup excluded per the frozen design).
Dev = walk-forward 2022/2023–2024/2025 (pooled n=3,346), seed 2021/2022.
Virgin = 2025/2026 (regular n=1,102) — **deliberately NOT read**: no arm
passed the dev gate, per the prereg's mechanical reading.

## Dev (per season)

| Season | Arm | 1X2 LL | RPS | OU2.5 LL | Climatology LL / RPS / OU LL |
|---|---|---|---|---|---|
| 2022/2023 (n=1,140) | Gate Zero | 1.0654 | 0.2178 | 0.6795 | 1.0920 / 0.2265 / 0.6801 |
| 2023/2024 (n=1,140) | Gate Zero | 1.0884 | 0.2259 | 0.7006 | 1.0834 / 0.2253 / 0.6786 |
| 2024/2025 (n=1,066) | Gate Zero | 1.0653 | 0.2188 | 0.7030 | 1.0878 / 0.2263 / 0.6844 |
| **Pooled (n=3,346)** | **Gate Zero** | **1.0732** | **0.2209** | **0.6942** | **1.0877 / 0.2260 / 0.6810** |
| Pooled (n=3,346) | SHRINK | 1.0732 | 0.2209 | 0.6942 | identical to Gate Zero (see below) |

## Gate arithmetic (pooled dev, verbatim legs)

- 1X2 LL leg: 1.0732 < climatology 1.0877 ✓
- RPS leg: 0.2209 < climatology 0.2260 ✓
- **OU2.5 LL leg: 0.6942 > base-rate 0.6810 ✗ — FAIL.** The model beats
  climatology on results but is *worse than the base rate* at pricing
  the primary line, losing the OU leg in two of three dev seasons
  (2023/2024 and 2024/2025). In 2023/2024 the model also lost all three
  legs to climatology outright (LL 1.0884 vs 1.0834) — Serie C's levels
  are so stable (2.32–2.37 goals/match, over-rate 41.5–43.2% in every
  complete season) that the base rate is a hard OU baseline here, the
  same failure shape as G-BG2.
- SHRINK is numerically identical to Gate Zero in every dev season:
  under season-blocked expanding fits, target-season teams are either
  unseen (n=0) or carry full prior seasons, so no team ever sits at
  1–5 prior matches — the arm reduces to the n=0 case by construction,
  exactly as in G-BG2 and G-SCO. It fails the same OU leg; variants
  are moot.

**Verdict: FAIL. Nothing ships.** No fitted params, no predictions
CSV. `engine/goals/results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}` — the
2025/2026 season remains untouched for a future pre-registered
attempt, and 2026/2027 remains reserved as confirmatory.

## Verification (builder-side, independent of the engine author)

- Climatology pooled dev (LL 1.087745 / RPS 0.226027 / OU LL 0.680970)
  recomputed from the raw CSV by a separate script — exact match to
  the engine's results.
- A full independent rerun of `run_g_itc.py dev` reproduced
  `results_dev.json` bit-for-bit.
- `dc.py` and `arms.py` are byte-identical to the proven
  BG-SecondLeague reference; the harness filters `phase == regular`
  and its dev path loads only 2021/2022–2024/2025; 2026/2027 is
  unreachable in every code path.
- One EDA defect was caught and corrected before the prereg: the
  first-pass Serie B mover deltas used a wrong reference base
  (ΔGF −0.42…−0.65); independent recomputation gave +0.20/−0.03/+0.07/
  +0.16 (ΔGA −0.08…−0.23). The correction did not change the X2
  decision (DROPPED — small effect, 3–5 clubs/season, fragile name
  identity) and is documented in EDA.md F4.

## League completion state

S/C/K/T are documented **not buildable**: the stats feed exists ONLY
in the in-progress 2026/2027 season (386/386 there; 0 in every
complete season), shotmap is 0% everywhere, and referee coverage is 0
in every complete season — no dev window and no complete virgin
window contains any count target (analysis/EDA.md F6,
MODEL_DESIGN.md feasibility matrix). G-ITC, the only buildable
candidate, has run its full gate honestly to FAIL. **IT-SerieC is
complete: 0 PASS / 1 FAIL, 4 markets not buildable.** No market joins
the daily runner; tonight's 02:30 WIB Serie C fixture therefore gets
no prediction from this build (a FAIL ships nothing).
