# S-GR verdict

Preregistration: `prereg/PREREG_S_GR.md`; virgin is 2025/2026,
n=236, read once. Calibration below is actual − predicted.

## Dev (scored 2022/2023–2024/2025, n=716, LL@8.5)

| arm / baseline | pooled | 2022/23 | 2023/24 | 2024/25 |
|---|---:|---:|---:|---:|
| Gate Zero | 0.681104 | 0.653750 | 0.712655 | 0.676837 |
| RS | 0.681213 | 0.653417 | 0.713600 | 0.676544 |
| league base rate | 0.693591 | | | |
| naive trailing-10 | 0.691212 | | | |

Both arms pass the dev gate (beat both baselines).

## Virgin table (LL@8.5)

| arm / baseline | LL | calibration pp ± SE |
|---|---:|---:|
| Gate Zero | 0.694952 | +1.422 ± 3.262 |
| RS | 0.694386 | +1.280 ± 3.261 |
| league base rate | 0.683442 | |
| naive trailing-10 | 0.710723 | |

## Gate arithmetic

- Gate Zero leg (i): **FAIL** — 0.694952 is not ≤ best baseline
  0.683442 (the plain league base rate beats the model on the
  virgin).
- Gate Zero leg (ii): +1.422 pp breaches 1.0 pp by 0.422 pp,
  within 1 SE (3.262 pp) → PROVISIONAL on this leg alone; moot
  given leg (i).
- RS leg (i): **FAIL** — 0.694386 is not ≤ 0.683442. Leg (ii)
  likewise provisional-only (+1.280 pp, breach 0.280 < SE).
  Leg (iii) moot.

S-GR verdict: **FAIL; nothing ships.**

Harness note (recorded, not hidden): the ported SOT harness's
`choose()` defaults to Gate Zero when no arm passes, so the virgin
run initially wrote a Gate Zero predictions file and fitted params
despite the failed legs. The coordinator deleted both; the
mechanical prereg reading above governs. `results_virgin.json`
still carries the harness's `shipped_arm: "GZ"` field — it is a
harness artefact, NOT a shipment.
