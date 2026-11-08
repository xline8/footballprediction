# Verdict — G-SK2 (SK-2Liga goals, Dixon–Coles goals-only)

**FAIL — dev gate (OU2.5 leg). Virgin NOT read. Nothing ships.**

Dev (season-blocked walk-forward; train seed 2021/2022; pooled
n = 613):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | **1.023678** | **0.220911** | 0.683592 |
| SHRINK | **1.023678** | **0.220911** | 0.683592 |
| X2 | **1.022793** | **0.220546** | 0.685011 |
| Climatology | 1.045988 | 0.232024 | **0.683493** |
| Naive trailing-10 | 1.064576 | 0.233999 | 0.712217 |

Per-season Gate Zero OU2.5 LL vs climatology: 2022/2023 0.696521
vs 0.675677 ✗; 2023/2024 0.667427 vs 0.681874 ✓; 2024/2025
0.689903 vs 0.694137 ✓. The 1X2 legs pass comfortably in every
season (LL 1.046549 / 1.020832 / 1.002157 vs climatology 1.061783 /
1.049888 / 1.023680); the OU2.5 leg fails pooled and in the first
evaluation season — the DC lambdas are informative about who wins
but their total-goals level is no better than a constant base rate
at the 2.5 line, worst in 2022/2023 where the fit rests on the
single thin 163-match seed season. This is the same failure mode
as sibling G-SK (SK-1Liga), which also failed its dev gate on the
OU2.5 leg.

Gate arithmetic (PREREG_G_SK2): pooled dev 1X2 LL beats
climatology ✓ (1.023678 < 1.045988); pooled RPS beats
climatology ✓ (0.220911 < 0.232024); pooled OU2.5 LL must beat
the base-rate baseline ✗ (0.683592 > 0.683493 — worse by
0.000099). The margin is a hair, but the gate is mechanical and
was frozen before fitting: a miss is a miss. SHRINK is identical
to Gate Zero in every season (0 changed rows, 0 target teams with
1–5 prior matches — every returning club carries a full prior
season and newcomers sit at n = 0, where both arms agree; verified
independently from the CSV). X2 beats Gate Zero on 1X2 LL in 2 of
3 dev seasons (leg (iii) would have passed) and on pooled LL/RPS,
but its OU2.5 LL (0.685011) is worse than climatology too, so it
fails the same leg. Per the prereg, if Gate Zero fails its own dev
gate the variants are moot.

Virgin: **NOT read.** `results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate;
virgin not read (variants moot)"}`. No virgin metrics, no fitted
params, no predictions file. The 2025/2026 season (n = 240,
complete) is reserved as the confirmatory window for any future
re-registered attempt; 2026/2027 (in progress) was never touched.

Ships: nothing. No predictions file was written.
(`engine/goals/results_dev.json` + `results_dev.csv` are the dev
run artefacts. The independent replay in the build notes — the
production `model_v2.py` DC refit on the same splits — reproduces
every dev number exactly, including the 0.000099 OU2.5 miss, so
this is a property of the league, not an implementation error.)

Independent-verification notes (build log): Codex's dev table was
replayed with the production DC class on all three dev seasons
(all arms, plus climatology and the trailing-10 naive): every
number matched to 0.0 difference. Two Codex bugs were caught and
fixed by the operator before the verdict: (1) the EDA
split-half 1H-share reliability was first computed on match-total
goals and corrected to the team's own goals (r = −0.165, n = 29 —
conclusion unchanged: noise); (2) the EDA inventory mixed the
index parent id into the per-season sub-league id lists, and the
harness recorded shrink_bites from the wrong arm pass (both fixed,
dev table unchanged on re-run).
