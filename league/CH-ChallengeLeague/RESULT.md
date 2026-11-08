# RESULT — CH-ChallengeLeague [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`157f99171de875ed933723340f4ac055b2aba19d` (main). Dev ≤ 2024/2025;
virgin = 2025/2026 read ONCE per dev-passing candidate (C, T only);
2026/2027 untouched. Gates exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Virgin gate numbers |
|---|---|---|
| G-CH goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=540): DC Gate Zero 1X2 LL 1.1225 / RPS 0.2391 / OU LL 0.7169 vs climatology 1.0926 / 0.2312 / 0.6856 — loses all three legs. SHRINK identical (never binds under season-blocked prediction). |
| S-CH SOT | **FAIL** (dev gate) | Virgin not read. Dev (n=180) LL @ 8.5: model 0.7166 vs base rate 0.6915, naive-10 0.7292 — fails the base-rate leg. |
| C-CH corners | **FAIL** (virgin legs i+ii) | Dev passed (0.6866 vs 0.7027 naive, 0.7406 base). Virgin (n=181) LL @ 8.5: model 0.7144 vs base 0.6897 → leg (i) FAIL. Calibration −6.97pp (SE 3.77) → leg (ii) FAIL. |
| K-CH cards | **FAIL** (dev gate) | Virgin not read. Dev (n=180) LL @ 4.5: model 0.6877 vs base rate 0.6847, naive-10 0.7043 — fails the base-rate leg by 0.0030. |
| T-CH total shots | **FAIL** (virgin leg ii) | Dev passed (0.6826 vs 0.6859 base, 0.7198 naive). Virgin (n=181) leg (i) PASS: LL @ 26.5 model 0.6757 ≤ base 0.6969, ≤ naive 0.7163. Leg (ii) calibration −6.37pp (SE 3.63) → beyond 1 SE of the boundary → FAIL. |

**Nothing ships from CH-ChallengeLeague.** No arm passed all legs;
no predictions directory is shipped (deliberately — cf. the FI S
verdict's shipped-file defect, avoided here by construction).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `157f991` predates every
   engine/results artifact in this folder's history.
2. Virgin discipline: `results_virgin.json` exists ONLY for C and T
   (the two dev-passers). G/S/K have dev results only.
3. The cards target choice: stats yellows, because the CH event feed
   carries almost no card events in 2021/2022–2025/2026 (85 event
   yellows in the whole dev era; stats ≈4.8/match). Evidence in
   `analysis/eda_summary.json` (`yell_agreement`) and EDA F5 — the
   mirror image of FI's coverage-forced choice.
4. The stats-era window for S/C/K/T (warm-up 2023/2024, dev scored
   2024/2025 only): forced by the feed starting in 2023/2024
   (0% stats in 2021/2022–2022/2023, verified — the brief's "rich from
   2024/2025" is one season late). Gates were not softened for the
   thinner dev.
5. Engine divergence, recorded pre-fitting in MODEL_DESIGN.md: the
   engines are documented minimal ports of the programme patterns
   (production engine code is not runnable from the bundle);
   constants are in each prereg.
6. Pattern across C and T virgin failures: both under-predicted a
   virgin-season level rise (corners 8.49→8.87, shots 25.30→27.01
   per match). Recorded as diagnosis in the verdict files; no
   post-hoc repair was attempted inside these preregs.
