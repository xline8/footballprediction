# K-IS verdict — FAIL — virgin not read

Prereg: `prereg/PREREG_K_IS.md`. Dev pooled n=324. Virgin 2026 was **NOT read** because Gate Zero failed the dev gate; no arm ships.

| Arm / baseline | LL@4.5 |
|---|---:|
| Gate Zero | 0.707406 |
| X8 | 0.703960 |
| League baseline | 0.700078 |
| Naive trailing-10 | 0.711031 |

Gate arithmetic: Gate Zero fails the required pooled comparison because 0.707406 > league baseline 0.700078. X8 is moot despite being better than Gate Zero (0.703960) and still worse than the league baseline (0.700078). Per preregistration, variants are moot and the virgin was not read.

Cards target freeze: stats yellows are the frozen target; the 2025 event feed is defective and is not substituted. X8 is therefore recorded only as a moot dev result.

**Verdict: FAIL. Nothing ships.**
