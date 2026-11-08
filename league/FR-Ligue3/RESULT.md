# RESULT — FR-Ligue3 [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`ef482d78560892a8026592eb7caa6d9efd039093` (branch
wip-fr-ligue3). Dev ≤ 2024/2025; virgin = 2025/2026 NOT read (G-FR failed
the dev gate); 2026/2027 untouched. Gates exactly as pre-registered; none
moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-FR goals | **FAIL** (dev gate, all three legs vs climatology) | Virgin not read. Dev pooled (n=884): DC Gate Zero 1X2 LL 1.0923 / RPS 0.2266 / OU LL 0.6994 vs climatology 1.0869 / 0.2243 / 0.6864 — loses all three pooled legs to climatology (OU leg also fails in every dev season). Beats naive trailing-10 on all three (1.2729 / 0.2390 / 0.7308), but the gate requires beating BOTH baselines. SHRINK identical (n<6 never binds under season-blocked prediction). |
| S-FR SOT | **NOT-BUILDABLE** | No stats feed in any season (0/1,570). No dev window, no trait, no line. |
| C-FR corners | **NOT-BUILDABLE** | No stats feed in any season (0/1,570). No dev window, no trait, no line. |
| K-FR cards | **NOT-BUILDABLE** | No stats yellows in any season; event plain Yellows only from 2023/2024 (target-definition break across dev); referee named in 0/1,570 matches (no X8 arm). |
| T-FR total shots | **NOT-BUILDABLE** | No stats feed in any season (0/1,570). No dev window, no trait, no line. |

**Nothing ships from FR-Ligue3.** No arm passed all legs; no
predictions directory is shipped (deliberately — cf. the CH
precedent: a FAIL at the dev gate means the virgin is never read and
nothing is predicted).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `ef482d7` (wip
   branch) predates every engine/results artifact in this folder's
   history.
2. Virgin discipline: `results_virgin.json` does NOT exist for any
   candidate — G-FR failed dev, so the virgin was never read.
   2026/2027 untouched (no engine reads any 2026/2027 row).
3. The dev-gate failure is broader than the FI/NO precedent: Gate
   Zero loses to climatology on ALL THREE pooled legs (1X2 1.0923 vs
   1.0869, RPS 0.2266 vs 0.2243, OU 0.6994 vs 0.6864), not just the
   OU leg. Diagnosis in `reports/G_FR_VERDICT.md`: weak trait
   reliability (split-half r 0.323 / 0.309) in a low-scoring league
   (2.48 goals/match dev scored) leaves the fitted ratings with no
   out-of-sample signal over pooled outcome rates. No post-hoc repair
   was attempted.
4. The X2 entrant offset was DROPPED pre-fitting (EDA F4): 21 dev
   entrant transitions, mean GF −0.010 / GA −0.011, mixed signs —
   no systematic tilt. Arms are Gate Zero + SHRINK only.
5. The cards target choice: no K model was built despite event
   Yellow events existing from 2023/2024 — the event target breaks
   across dev (0 plain Yellows in 2021/2022–2022/2023) and referee
   coverage is 0% everywhere. Evidence in `analysis/eda_summary.json`
   (`event_cards_by_season`) and EDA F5.
6. Format facts: single group (18 teams to 2023/2024, 17 from
   2024/2025). The league was the Championnat National through
   2025/2026 and was rebranded Ligue 3 for 2026/2027
   (`general.leagueName` "National" 1,462 matches, "Ligue 3" 108) —
   same competition, no split. Six awarded matches (3663409,
   3663603, 3955519, 3955521, 4125433, 4879528), kept as ordinary
   flagged rows; 4879528 sits in the virgin season, which was never
   read. Four team ids carry two spellings (accent/prefix variants);
   all logic keys by team id.
