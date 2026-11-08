# Verdict — G-HN (Honduras Liga Nacional goals model) — **FAIL**

Prereg: `prereg/PREREG_G_HN.md`, frozen before fitting at commit `d06ad93b`.
Development is expanding and tournament-blocked: 2021/2022 seed (both phases,
regular n=180), 2022/2023–2024/2025 dev (6 tournaments, pooled n=540). The
complete 2025/2026 virgin (regular n=220) and reserved 2026/2027 confirmatory
rows were not read by the dev run. Both preregistered arms failed the pooled
dev gate. No arm ships.

## Dev results

| Season | Arm | n | 1X2 LL | RPS | OU2.5 LL | Climatology LL / RPS / OU LL | Naive LL / RPS / OU LL |
|---|---|---:|---:|---:|---:|---|---|
| 2022/2023 - Apertura | Gate Zero | 90 | 0.981563276 | 0.191597571 | 0.702451991 | 1.084728272 / 0.227561728 / 0.681564792 | 1.007804544 / 0.201662183 / 0.689979618 |
| 2022/2023 - Clausura | Gate Zero | 90 | 1.015790539 | 0.191022137 | 0.723180933 | 1.093845062 / 0.215679012 / 0.708077453 | 1.038876378 / 0.199431152 / 0.691272543 |
| 2023/2024 - Apertura | Gate Zero | 90 | 0.990073237 | 0.201639229 | 0.702331040 | 1.047605241 / 0.223043981 / 0.689191344 | 1.023394739 / 0.213956088 / 0.696570503 |
| 2023/2024 - Clausura | Gate Zero | 90 | 0.959289428 | 0.193677865 | 0.706242857 | 1.035610849 / 0.218629630 / 0.705035632 | 1.015376933 / 0.213945784 / 0.688643852 |
| 2024/2025 - Apertura | Gate Zero | 90 | 1.014027675 | 0.201285099 | 0.753634917 | 1.083915635 / 0.221654664 / 0.690950849 | 1.082281133 / 0.220803205 / 0.737827466 |
| 2024/2025 - Clausura | Gate Zero | 90 | 1.020684798 | 0.184524717 | 0.659573860 | 1.111813533 / 0.212597632 / 0.711073801 | 1.053125555 / 0.192041619 / 0.712555135 |
| **Pooled** | **Gate Zero** | **540** | **0.996904826** | **0.193957770** | **0.707902600** | **1.076253099 / 0.219861108 / 0.697648979** | **1.036809880 / 0.206973339 / 0.702808186** |
| 2022/2023 - Apertura | SHRINK | 90 | 0.981563276 | 0.191597571 | 0.702451991 | 1.084728272 / 0.227561728 / 0.681564792 | 1.007804544 / 0.201662183 / 0.689979618 |
| 2022/2023 - Clausura | SHRINK | 90 | 1.015790539 | 0.191022137 | 0.723180933 | 1.093845062 / 0.215679012 / 0.708077453 | 1.038876378 / 0.199431152 / 0.691272543 |
| 2023/2024 - Apertura | SHRINK | 90 | 0.990073237 | 0.201639229 | 0.702331040 | 1.047605241 / 0.223043981 / 0.689191344 | 1.023394739 / 0.213956088 / 0.696570503 |
| 2023/2024 - Clausura | SHRINK | 90 | 0.959289428 | 0.193677865 | 0.706242857 | 1.035610849 / 0.218629630 / 0.705035632 | 1.015376933 / 0.213945784 / 0.688643852 |
| 2024/2025 - Apertura | SHRINK | 90 | 1.014027675 | 0.201285099 | 0.753634917 | 1.083915635 / 0.221654664 / 0.690950849 | 1.082281133 / 0.220803205 / 0.737827466 |
| 2024/2025 - Clausura | SHRINK | 90 | 1.020684798 | 0.184524717 | 0.659573860 | 1.111813533 / 0.212597632 / 0.711073801 | 1.053125555 / 0.192041619 / 0.712555135 |
| **Pooled** | **SHRINK** | **540** | **0.996904826** | **0.193957770** | **0.707902600** | **1.076253099 / 0.219861108 / 0.697648979** | **1.036809880 / 0.206973339 / 0.702808186** |

## Dev gate arithmetic

The frozen gate requires strict improvement on pooled 1X2 LL and RPS versus
climatology, and pooled OU2.5 LL versus the base-rate baseline. The pooled
comparisons are:

- Gate Zero 1X2 LL: **0.9969048255991344 vs 1.0762530987177952 — PASS** (−0.0794).
- Gate Zero RPS: **0.1939577698045028 vs 0.21986110790338037 — PASS** (−0.0259).
- Gate Zero OU2.5 LL: **0.7079025995634142 vs 0.6976489785135715 — FAIL** (+0.0103).
- SHRINK has exactly the same three comparisons: **PASS, PASS, FAIL**.

No arm passed all three legs. Per the preregistered stop rule, the virgin was
deliberately not read. `results_virgin.json` records
`{"virgin_read": false, "reason": "No arm passed pooled dev gate"}`. Virgin
1X2 LL, calibration, and variant sign legs are not assessed; the both-pass/tie
rule is not reached. Final verdict: **FAIL; nothing ships**.

The OU2.5 failure is systematic, not one bad block: the model beats the
base-rate OU2.5 LL in only 1 of 6 dev tournaments (2024/2025 Clausura,
0.6596 vs 0.7111). It loses in the other five, worst in 2024/2025 Apertura
(0.7536 vs 0.6910). The model's 1X2 and RPS edge over climatology is real in
every tournament, but its total-goals distribution is worse than the pooled
over-rate at the 2.5 line. This mirrors G-GT (same scores-only shape), which
also failed its dev gate on OU2.5 LL.

## SHRINK identity check

SHRINK changed **0 of 540 dev predictions**, with maximum absolute delta
**0.0** in lambdas. This is structural, not dead code. Prior-match counts per
target team are always 0 or ≥18 (whole-tournament participation): each
Apertura has exactly one debutant with 0 prior matches — Olancho FC
(2022/2023), Génesis FC (2023/2024), Juticalpa (2024/2025) — while every
other target team has ≥36 prior matches. A team with 0 prior matches has
a = d = 0 under Gate Zero's unseen-team rule, and SHRINK scaling by 0/6 = 0
leaves a = d = 0 unchanged; teams with ≥36 matches get factor 1.0. So SHRINK
is provably identical to Gate Zero on every HN dev match.

The per-tournament maximum training dates were 2022-05-01, 2022-11-19,
2023-04-29, 2023-11-25, 2024-04-28, and 2024-12-01, each before its target
tournament's first kickoff. The dev loader read 720 regular rows (seed +
dev) and rejects virgin/reserved rows.

## Independent verification

- Climatology recomputed from scratch from `hn_matches.csv` (own script, no
  harness code): all six per-tournament and the pooled LL/RPS/OU2.5 LL match
  the engine to <1e-9.
- DC fit reconstructed independently from the MODEL_DESIGN spec for
  2022/2023 Apertura (train n=180, cutoff 2022-07-31; fitted h = 0.300378,
  rho = 0.0, mu = 1.387885): LL 0.981563276, RPS 0.191597571,
  OU2.5 LL 0.702451991 — exact match with the engine.
- Naive trailing-10 recomputed independently under the brief definition
  (most recent 10 eligible regular-phase matches strictly before each
  target date, full pre-virgin history): all seven rows match the engine
  to <1e-9.
- `dc.py` and `arms.py` are byte-identical to the GT reference copies
  (`cmp` clean).

## Defects found and fixed during the build

1. Phase A: EDA hardcoded the wrong halves verdict and a wrong share
   denominator (0.4566); fixed, EDA rerun reproduced the frozen constant
   0.4572 with the variance decomposition (observed 0.1163 vs expected
   binomial 0.1161, excess 0.0002).
2. Engine loader: the dev read-boundary assert fired before the
   season-allow filter, tripping on virgin rows that would have been
   filtered out; fixed by asserting only over loaded rows.
3. Engine halves probabilities: an early version computed the 1.5 line from
   an independent-Poisson formula instead of the fitted score matrix; fixed
   to compute all half lines from `model.matrix()` with the fitted rho.
4. Engine naive baseline: history was built from the pre-tournament
   training window only, so trailing-10 windows went stale within a
   tournament; fixed to use all pre-virgin rows as history (league-mean
   fallback still from the training window), per the brief definition.
   Only the 14 naive rows changed; all 28 model/climatology rows are
   byte-identical to the pre-fix run. A dead no-op loop in the pooled
   section was also removed.
5. Note (no action, recorded for the record): the prereg's calibration leg
   reads "a breach within 1 SE of the boundary", i.e. provisional iff
   |diff| ≤ 0.01 + SE; the harness implements that literal reading. The leg
   was never exercised because the virgin was not read.

## Reproducibility

Two clean runs from the final code produced identical SHA-256 hashes for all
three generated result artifacts:

- `results_dev.json`: `76fea1029bba6e3184f44a99fa7ef9c3d3680b8cff36c43cd9eade42b51972aa`
- `results_dev.csv`: `35d3d11d7f6aad5346d81edb583ebb99a45e7ee6240584d4023da5a382d022a9`
- `results_virgin.json`: `e5e32478742c1ece68432c977be5abf2da4708e0ce8dea0aeec3b3f7bceab3e5`

## Files produced

- `engine/goals/dc.py`
- `engine/goals/arms.py`
- `engine/goals/harness.py`
- `engine/goals/run_g_hn.py`
- `engine/goals/README.md`
- `engine/goals/results_dev.json`
- `engine/goals/results_dev.csv`
- `engine/goals/results_virgin.json`
- `reports/G_HN_VERDICT.md`

No `fitted_params_virgin.json` or virgin predictions CSV was produced because
the virgin was not read. The 2026/2027 Apertura confirmatory window remains
reserved and unread. S-HN, C-HN, K-HN, T-HN were not buildable (0/1,132
targets each) and have no verdicts.
