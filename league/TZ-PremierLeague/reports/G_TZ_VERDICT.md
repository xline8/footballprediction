# Verdict — G-TZ (Tanzania Premier League goals model)

**FAIL at the dev gate. Nothing ships. Virgin 2025/2026 deliberately NOT read.**

Prereg `league/TZ-PremierLeague/prereg/PREREG_G_TZ.md` (commit
`de16ef20`) precedes all fitting. Branch `build/tz-premier-league`.
Engine `league/TZ-PremierLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV, `predictions_dev.csv`).

## Dev results (season-blocked expanding walk-forward, n=720)

| arm | season | kind | n | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---:|---:|---:|---:|
| Gate Zero | 2022/2023 | model | 240 | 0.928407 | 0.187585 | 0.728351 |
| Gate Zero | 2022/2023 | climatology | 240 | 1.073080 | 0.229884 | 0.709023 |
| Gate Zero | 2022/2023 | naive trailing-10 | 240 | 0.960959 | 0.197116 | 0.744904 |
| Gate Zero | 2023/2024 | model | 240 | 1.022600 | 0.186772 | 0.731056 |
| Gate Zero | 2023/2024 | climatology | 240 | 1.076021 | 0.216873 | 0.669352 |
| Gate Zero | 2023/2024 | naive trailing-10 | 240 | 1.000961 | 0.193376 | 0.667564 |
| Gate Zero | 2024/2025 | model | 240 | 0.917829 | 0.182538 | 0.689072 |
| Gate Zero | 2024/2025 | climatology | 240 | 1.058140 | 0.225075 | 0.699786 |
| Gate Zero | 2024/2025 | naive trailing-10 | 240 | 0.969415 | 0.194349 | 0.733890 |
| **Gate Zero** | **pooled** | **model** | **720** | **0.956279** | **0.185632** | **0.716160** |
| **Gate Zero** | **pooled** | **climatology** | **720** | **1.069080** | **0.223944** | **0.692720** |
| **Gate Zero** | **pooled** | **naive trailing-10** | **720** | **0.977112** | **0.194947** | **0.715453** |
| SHRINK | 2022/2023 | model | 240 | 0.928407 | 0.187585 | 0.728351 |
| SHRINK | 2023/2024 | model | 240 | 0.944276 | 0.175377 | 0.652661 |
| SHRINK | 2024/2025 | model | 240 | 0.903820 | 0.177513 | 0.687199 |
| **SHRINK** | **pooled** | **model** | **720** | **0.925501** | **0.180158** | **0.689404** |

SHRINK is identical to Gate Zero in 2022/2023 (0 changed rows — no team
in the 1–5 prior-match band that fold) and differs in the other two folds:
30 changed rows in 2023/2024 (Fountain Gate FC, n=1 prior match under its
own name — 29 more as Singida Big Stars, not merged) and 30 changed rows
in 2024/2025 (Singida Black Stars, n=2 — 28 more as Ihefu FC, not merged).
Unlike GH, the SHRINK band genuinely occurs here, and the arm is a real
test, not a structural no-op.

## Gate arithmetic (mechanical, per prereg)

Dev gate — pooled model must beat climatology on 1X2 LL and RPS, and
beat the base rate on OU2.5 LL:

- 1X2 LL: 0.956279 vs 1.069080 — model **wins by −0.112801** ✓
- RPS: 0.185632 vs 0.223944 — model **wins by −0.038312** ✓
- OU2.5 LL: 0.716160 vs 0.692720 — model **loses by +0.023440** ✗

Gate Zero fails one of the three legs (the OU2.5 leg), so Gate Zero
fails its dev gate. Per the frozen rule in the prereg ("If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin NOT
read" — the same sentence as GH/NG/RU2, enforced mechanically by the
harness: `virgin()` raises `RuntimeError` unless Gate Zero passed dev),
**no virgin leg is evaluated and the virgin window stays unread** — no
`results_virgin.json`, no `fitted_params_virgin.json`, no virgin
predictions file exists, and no `league/TZ-PremierLeague/predictions/`
directory exists.

## The SHRINK fork (recorded plainly, not acted on)

SHRINK passes all three pooled dev legs on its own numbers (1X2 LL
0.925501 < 1.069080; RPS 0.180158 < 0.223944; OU2.5 LL 0.689404 <
0.692720, winning the OU leg by −0.003316) and beats Gate Zero on every
pooled leg. It does NOT proceed to the virgin window, because the frozen
prereg makes Gate Zero's dev pass a precondition for any virgin read —
the virgin leg (i) itself compares a variant's virgin LL against Gate
Zero's virgin LL, which can only exist if Gate Zero passed dev. Letting
SHRINK through now would mean re-interpreting the gate after seeing
the results, which the gate discipline forbids. The numbers are recorded
here in full so the coordinator (or the user, for a future league) can
judge whether the "variants are moot" rule should ever be revisited;
this build does not revisit it.

Fold reading: Gate Zero beats climatology on 1X2 LL and RPS in all three
folds, and beats the naive trailing-10 on LL and RPS pooled (LL
0.956 vs 0.977; RPS 0.186 vs 0.195) — but on OU2.5 it loses to the
naive baseline pooled as well (0.716 vs 0.715, by +0.000707, effectively
a tie). Against the base rate it loses in 2022/2023 (0.728 vs 0.709) and badly
in 2023/2024 (0.731 vs 0.669 — the season where the base-rate OU
baseline is strongest, climatology OU LL 0.669, the lowest of the
three folds), winning only in 2024/2025 (0.689 vs 0.700). The
failure is therefore not a fluke fold: the DC totals distribution is
systematically worse than the pooled over-rate at 2.5 in two of three
seasons. Note the contrast with Ghana, where the attack trait was
absent (split-half r=−.03) and the model lost all three legs: Tanzania's
traits are strong (EDA §2: attack r=.575, defence r=.490 pooled), the
model duly wins LL and RPS by wide margins, and it is the totals leg
alone that kills the candidate — the ratings carry result signal but
the Poisson totals shape does not beat the base rate at 2.5.

## Verification (independent of the implementor)

- `dc.py` is byte-identical to GH's `dc.py` except the docstring;
  `arms.py` likewise. Its lambdas reproduce the **production
  `model_v2.DC` class exactly** (max diff 0.0 over all 240 matches
  of the 2022/2023 fold; seed fit h=0.403403, rho=−0.1, mu=0.989250
  on both implementations).
- `harness.py` differs from GH's only in the sanctioned constants
  (data file, seasons/counts, halves constant 0.4867818118 /
  0.5132181882, virgin filename) plus one added load-time assert that
  the dev load contains exactly the seed + dev folds — verified by
  diff.
- Dev re-run reproduces `results_dev.json` exactly (SHA-256
  `198c646398c50b3c46055d431df2bba78ba1cb8c19c2c61a4c43b05d9e622e87`
  before and after re-run); an independent second-path recomputation
  (fresh code, CSVs only) reproduces every per-fold and pooled model
  and climatology metric to 0.00e+00 (max diff over all 11 checked
  rows).
- Dev predictions contain only the three dev seasons (1,440 rows =
  720 × 2 arms); no 2025/2026 or 2026/2027 row was read (harness
  asserts the loaded seasons; `virgin()` raises `RuntimeError`
  before any virgin read — exercised and confirmed).
- Data builder re-run regenerates identical CSVs (1,284 rows, 1,282
  eligible, per-season counts as frozen in the prereg).
- No implementor artifacts needed correction: the engine port was
  clean on first review (the only diffs from GH are the frozen TZ
  constants).

## What ships

Nothing. No fitted params, no predictions, no daily-runner
activation. The virgin window 2025/2026 (239 eligible matches) stays
reserved and unread, as does the confirmatory window 2026/2027 (84
matches in progress). League completion state: **complete** — the only
buildable candidate (G-TZ) ran its full gate and failed; S/C/K/T are
not buildable (separate report).
