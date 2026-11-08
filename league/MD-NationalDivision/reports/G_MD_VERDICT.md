# Verdict — G-MD (MD-NationalDivision goals): **FAIL (virgin legs i + ii)**

Frozen decision: PREREG_G_MD.md (prereg commit 72b4199, branch
wip-md-nationaldivision, before any fitting). Gate Zero PASSED the
dev gate — the first dev pass in this scores-only batch — so the
virgin 2025/2026 was read ONCE for all three dev-passing arms. All
three arms then failed the virgin legs; nothing ships.

Dev (pooled 2022/2023–2024/2025, n=258, season-blocked expanding fit):

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev gate |
|---|---|---|---|---|
| Gate Zero | 0.9538 | 0.1869 | 0.7040 | PASS |
| SHRINK | 0.9538 | 0.1869 | 0.7040 | PASS |
| X2 | 0.9538 | 0.1869 | 0.7040 | PASS |
| Climatology | 1.0856 | 0.2342 | 0.7163 | — |
| Naive trailing-10 | 1.1618 | 0.1947 | 0.8078 | — |

All three arms are numerically identical on dev, exactly as the
prereg recorded: SHRINK never binds under season-blocked prediction
(no team sits in the 1–5 prior-match band), and the X2 offset is 0
in every scored season (2022/2023 entrant: 0 prior transitions;
2023/2024 entrants: 1 prior transition < 3; 2024/2025: no
entrants). Per season (model 1X2 LL / RPS / OU2.5 LL): 2022/2023
0.9383 / 0.1795 / 0.6808 (climatology 1.1383 / 0.2349 / 0.7552,
naive 1.2897 / 0.1970 / 0.7399); 2023/2024 0.9885 / 0.2050 / 0.7524
(climatology 1.0393 / 0.2386 / 0.7015, naive 1.2346 / 0.1995 /
0.8481 — the model loses the OU leg to climatology and the RPS leg
to naive in this season, but the frozen dev gate is pooled, and
pooled the model beats both baselines on all three legs);
2024/2025 0.9348 / 0.1763 / 0.6789 (climatology 1.0791 / 0.2292 /
0.6922, naive 0.9611 / 0.1875 / 0.8352). Re-run of the dev harness
reproduces results_dev.json exactly (md5
24702632b8419d0596f42d978e0be1a4).

Virgin (2025/2026, n=114, read ONCE; fit on all matches ≤ 2024/2025):

| Arm | 1X2 LL | RPS | OU2.5 LL | Cal HW (pp) | Cal OU (pp) |
|---|---|---|---|---|---|
| Gate Zero | 0.8400 | 0.1662 | 0.7048 | −2.26 (SE 3.96) | −11.69 (SE 4.62) |
| SHRINK | 0.8400 | 0.1662 | 0.7048 | −2.26 (SE 3.96) | −11.69 (SE 4.62) |
| X2 | 0.8097 | 0.1576 | 0.6948 | −2.22 (SE 3.88) | −11.30 (SE 4.58) |
| Climatology | 1.0390 | 0.2418 | **0.6880** | — | — |
| Naive trailing-10 | 0.8463 | 0.1669 | 0.8156 | — | — |

- **Leg (i) LL — FAIL for every arm.** On 1X2 every arm beats Gate
  Zero (X2), climatology and naive (Gate Zero only narrowly beats
  naive, 0.8400 vs 0.8463). But on OU2.5 every arm LOSES to
  climatology: Gate Zero / SHRINK 0.7048 and X2 0.6948 against the
  constant base rate's 0.6880. The frozen leg requires OU2.5 LL ≤
  each baseline's; no arm satisfies it.
- **Leg (ii) calibration — FAIL for every arm.** Home-win: −2.26pp
  (Gate Zero/SHRINK) and −2.22pp (X2) breach the 1.0pp boundary but
  sit within 1 SE of it — that component alone would be
  PROVISIONAL. OU2.5: −11.69pp / −11.69pp / −11.30pp against SEs of
  4.62 / 4.62 / 4.58 — the breach is more than 1 SE beyond the
  boundary, so leg (ii) FAILS outright. The model under-predicts
  the virgin over-rate by ~11.5pp (mean predicted ≈ 0.471 vs
  actual 0.588).
- **Leg (iii) sign check (variants)**: SHRINK and X2 equal Gate
  Zero's dev 1X2 LL in 3/3 seasons (identical numbers) — moot,
  since legs (i) and (ii) already failed.

Diagnosis (recorded, not acted on): the ratings carry real 1X2
signal (virgin 1X2 LL beats both baselines; X2's entrant tilt,
live for the first time on the virgin season, improved every
metric: 1X2 0.8097 vs 0.8400). The failure is totals calibration:
the virgin season's over-rate (0.588) ran well above the dev
scored rate (0.488) at a similar goals level (2.947 vs 2.682–2.965
goals/match in late dev seasons), and the fitted model's totals
distribution stayed too low/narrow — the same failure shape as
IL-LigatHaAl's virgin calibration miss (−11.70pp on OU). No
post-hoc repair was attempted inside this prereg; the virgin is
not re-read.

Nothing ships for G-MD. No predictions directory is shipped
(deliberately — no arm passed, so there is no virgin predictions
output to ship). The confirmatory reserve 2026/2027 was never
read by any harness (dev and virgin loads both exclude it).
