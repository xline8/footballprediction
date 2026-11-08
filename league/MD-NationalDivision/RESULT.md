# RESULT — MD-NationalDivision [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`72b4199a9c0c104b96f1ea52214166c73b28cb10` (branch
wip-md-nationaldivision). Dev ≤ 2024/2025 (warm-up 2021/2022, scored
2022/2023–2024/2025); virgin = 2025/2026 READ ONCE (G-MD passed the
dev gate — the first dev pass in this batch); 2026/2027 untouched
confirmatory reserve. Gates exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-MD goals | **FAIL** (virgin legs i + ii) | Dev gate PASSED (pooled n=258): Gate Zero = SHRINK = X2 at 1X2 LL 0.9538 / RPS 0.1869 / OU2.5 LL 0.7040 vs climatology 1.0856 / 0.2342 / 0.7163 and naive 1.1618 / 0.1947 / 0.8078. Virgin (n=114, read once): Gate Zero 1X2 LL 0.8400 / OU 0.7048, X2 0.8097 / 0.6948 — every arm beats both baselines on virgin 1X2 but LOSES the OU leg of leg (i) to climatology (0.6880), and every arm fails leg (ii) on OU calibration (−11.69pp Gate Zero/SHRINK, −11.30pp X2; SE ≈ 4.6; home-win component −2.26pp is provisional-band only). |
| S-MD SOT | **NOT-BUILDABLE** | No stats feed in any season (0/556); shotmap 0/556. No dev window, no trait, no line. |
| C-MD corners | **NOT-BUILDABLE** | No stats feed in any season (0/556); X7 input absent too. No dev window, no trait, no line. |
| K-MD cards | **NOT-BUILDABLE** | No yellows target in any season: stats absent AND event plain Yellows 0 in EVERY season (only YellowRed + Red, YellowRed total 25); referee named in 0/556 matches (no X8 arm). |
| T-MD total shots | **NOT-BUILDABLE** | No stats feed in any season (0/556); shotmap empty in every season. No dev window, no trait, no line. |

**Nothing ships from MD-NationalDivision.** No arm passed all
virgin legs; no predictions directory is shipped (deliberately —
there is no passing arm to predict with).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `72b4199` (wip
   branch, snapshot "[Muse-2] WIP snapshot MD-NationalDivision
   fase 3-prereg") predates every engine/results artifact. WIP
   history: fase 2 `52b0941`, prereg `72b4199`, fase 4 (dev results)
   `a26b2e7`.
2. Virgin discipline: the virgin 2025/2026 was read exactly ONCE,
   by a single `run_g_md.py` invocation after the dev gate passed —
   `results_virgin.json` + `virgin_rows_{gate_zero,shrink,x2}.csv`
   + `fitted_params_virgin.json` are the outputs of that one read.
   The dev harness never reads 2025/2026 or 2026/2027 rows
   (allow-list load), and a dev re-run reproduces
   `results_dev.json` byte-identically (md5
   24702632b8419d0596f42d978e0be1a4) before and after the virgin
   read. 2026/2027 was never loaded by any harness.
3. This is the batch's first dev-gate PASS, and it still fails:
   the failure is totals calibration, not ratings. Virgin 1X2 LL
   beats both baselines for every arm (X2 best at 0.8097), but the
   model under-predicts the virgin OU2.5 over-rate by ~11.5pp
   (predicted ≈ 0.471 vs actual 0.588) — the same failure shape as
   IL-LigatHaAl's virgin OU calibration miss (−11.70pp). The
   virgin over-rate jumped from the dev scored 0.488 at a similar
   goals level (2.947/match). Recorded in
   `reports/G_MD_VERDICT.md`; no post-hoc repair attempted, virgin
   not re-read.
4. X2 was KEPT pre-fitting on thinner evidence than BY/FI (only 3
   dev transitions, GF −0.363 at 3/3 signs, GA +0.780 at 2/3) under
   the frozen rule (offset from completed transitions only, <3 →
   0, clamped [0.8, 1.25]). As pre-registered, X2 is numerically
   identical to SHRINK/Gate Zero on the whole dev window; it fired
   for the first time on the virgin season and improved every
   metric (1X2 0.8097 vs 0.8400, OU 0.6948 vs 0.7048) — but not
   enough to pass legs (i) or (ii). SHRINK never binds anywhere.
5. One documented port adaptation: `arms.py` season arithmetic
   compares season start years instead of parsing the label as a
   calendar year (MD uses split-season labels "2021/2022"). `dc.py`
   is verbatim; `harness.py` differs from the BY line only in
   paths, season labels, and the fit_on string. See
   `engine/goals/README.md`.
6. Format facts: 8 teams every season; 2021/2022 single phase
   (112) under leagueName "National Division"; from 2022/2023 the
   league is renamed "Super Liga" with a championship group
   (56 main + 30 championship = 86); 2025/2026 main phase expanded
   (84 + 30 = 114). Phase is a flag, never filtered. Ten awarded
   matches (9 in 2021/2022, 1 in 2024/2025), ordinary flagged rows,
   none in the virgin season. Zero score-vs-event mismatches in
   the corpus. Twelve team ids; two carry diacritic spelling
   variants (FC Balti/Bălți, Real Sireți/Sireti) — all logic keyed
   by team id. The 52 event-less matches are not all scoreless
   (10 contain 30 goals); their event-derived fields are missing,
   never zero.
