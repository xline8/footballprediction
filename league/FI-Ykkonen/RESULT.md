# RESULT — FI-Ykkonen [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`e5874b8d62f005abf9a79e8ee2b5641069cf1f2a` (branch
wip-fi-ykkonen). Split: Jarvis OPSI A (board comment 6761468990) —
dev ≤ 2024 as-is on the brief split. Dev ≤ 2024; virgin = 2025 NOT
read (G-FI failed the dev gate); 2026 untouched. Gates exactly as
pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-FI goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=1,010): DC Gate Zero 1X2 LL 1.0747 / RPS 0.2437 / OU LL 0.7026 vs climatology 1.0420 / 0.2355 / 0.6485 — loses to climatology on all three; beats naive trailing-10 on 1X2 (1.1023) and OU (0.7208) but loses RPS (0.2288). Gate requires beating BOTH baselines on all three. SHRINK identical (n<6 never binds under season-blocked prediction). X2 improves all three pooled metrics (1.0660 / 0.2404 / 0.6940) but fails the dev gate itself. |
| S-FI SOT | **NOT-BUILDABLE** | No stats feed in any season (0/1,730). No dev window, no trait, no line. |
| C-FI corners | **NOT-BUILDABLE** | No stats feed in any season (0/1,730). No dev window, no trait, no line. |
| K-FI cards | **NOT-BUILDABLE** | No stats yellows in any season; 0 plain Yellow events in the whole corpus; referee named in 0/1,730 matches (no X8 arm). |
| T-FI total shots | **NOT-BUILDABLE** | No stats feed or shotmap in any season (0/1,730). No dev window, no trait, no line. |

**Nothing ships from FI-Ykkonen.** No arm passed all legs; no
predictions directory is shipped (deliberately — cf. the CH
precedent: a FAIL at the dev gate means the virgin is never read and
nothing is predicted).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `e5874b8` (wip
   branch) predates every engine/results artifact in this folder's
   history.
2. Virgin discipline: `results_virgin.json` does NOT exist for any
   candidate — G-FI failed dev, so the virgin was never read.
   2026 untouched (no engine reads any 2026 row).
3. Split decision: Jarvis OPSI A, board comment 6761468990 — dev ≤
   2024 as-is. The Kakkonen/Ykkönen structure + the split-phase
   composition effect are recorded in `prereg/PREREG_G_FI.md`
   (regular-phase 3.329 vs 3.326; halves 0.4445 vs 0.4594; groups A
   3.470 / B 3.639 / C 3.034; 22 cross-group matches, all 2023).
4. The dev-gate failure is the same mode as the FI-Veikkausliiga
   reference league itself (its goals candidate: Gate Zero OU 0.7231
   vs climatology 0.6921, FAIL dev gate OU leg). The verbatim FI
   sweep engine under-predicts totals here too: predicted mean total
   goals 2.68 / 2.99 / 2.85 vs actual 3.43 / 3.33 / 3.51 per dev
   season. Diagnosis in `reports/G_FI_VERDICT.md`; no post-hoc
   repair was attempted.
5. X2 was ADOPTED pre-fitting (EDA F4): 22 dev entrant transitions,
   mean GF −0.182 / GA +0.235, g_log −0.182 / c_log +0.223 (c clamped
   at log 1.25). It improves all three pooled dev metrics but fails
   the dev gate itself, so it is moot under the frozen mechanical
   reading. Arms are Gate Zero + SHRINK + X2.
6. Format facts: FotMob 8969 is Kakkonen 2021–2023 (three parallel
   groups) and Ykkönen 2024–2026 (12 teams, 132 + 15 + 15). Seven
   awarded matches in the corpus (6 in dev, 1 in the virgin), kept
   as ordinary flagged rows. Team id 112425 carries two spellings
   (GrIFK Grankulla / GrIFK); all logic keys by team id.
