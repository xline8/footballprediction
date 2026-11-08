# K-CH verdict — FAIL

Prereg: `prereg/PREREG_K_CH.md` (frozen ccf74a9, before fitting).
Primary line **4.5** (dev over-rate 0.467). Dev pooled n = 636;
virgin 2025/2026 n = 228, read once, for both dev-passing arms.

## Dev results — pooled LL@4.5

| Arm / baseline | LL@4.5 |
|---|---|
| Gate Zero | 0.6766 |
| X8 (referee) | 0.6746 |
| League base rate | 0.6880 |
| Naive trailing-10 | 0.6798 |

Both arms beat both baselines → both pass the dev gate. X8
per-season sign check vs Gate Zero: 2/3 (better 2022/2023 and
2023/2024, worse 2024/2025).

## Virgin results (2025/2026, n = 228)

| Arm / baseline | LL@4.5 | Calibration (mean P − actual) |
|---|---|---|
| Gate Zero | 0.6845 | −5.14pp (SE 3.27pp) |
| X8 | 0.6788 | −5.38pp (SE 3.25pp) |
| League base rate | 0.6974 | — |
| Naive trailing-10 | 0.6833 | — |

## Gate arithmetic

- Leg (i): X8 passes (0.6788 ≤ Gate Zero 0.6845 and ≤ best baseline
  0.6833). **Gate Zero FAILS leg (i)** — its virgin LL loses to the
  naive trailing-10 baseline (0.6845 > 0.6833).
- Leg (ii): **both arms FAIL.** |−5.14pp| and |−5.38pp| breach the
  1.0pp boundary by 4.14pp / 4.38pp, each beyond 1 SE (3.27 / 3.25).
  The virgin season's card volume ran far above what either arm
  predicted at the 4.5 line, and no SE cushion covers it.
- Leg (iii): X8 sign check 2/3 — moot under the leg (ii) failure.

**Verdict: FAIL. Nothing ships.** The referee arm genuinely helped
(dev −0.0020 LL; virgin LL best of all arms) and the candidate still
dies on calibration — the mirror of K-J1, where the LL leg failed
instead. CH's weak team yellows trait (EDA F2, r=0.256) is part of
the story: there is little stable team signal for either arm to
price the level with.
