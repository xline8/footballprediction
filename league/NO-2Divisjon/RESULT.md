# RESULT — NO-2Divisjon [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`2901fa0f01c5067619bd0048fba00cee84d53c11` (branch
wip-no-2divisjon). Dev ≤ 2024; virgin = 2025 NOT read (G-NO failed
the dev gate); 2026 untouched. Gates exactly as pre-registered; none
moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-NO goals | **FAIL** (dev gate, OU leg) | Virgin not read. Dev pooled (n=1,066): DC Gate Zero 1X2 LL 1.0046 / RPS 0.2188 / OU LL 0.6835 vs climatology 1.0392 / 0.2332 / 0.6501 — passes 1X2 and RPS, fails OU2.5 (0.6835 > 0.6501) in every dev season. Beats naive trailing-10 on all three (1.1274 / 0.2368 / 0.7052), but the gate requires beating BOTH baselines. SHRINK identical (n<6 never binds under season-blocked prediction). |
| S-NO SOT | **NOT-BUILDABLE** | No stats feed in any season (0/2,158). No dev window, no trait, no line. |
| C-NO corners | **NOT-BUILDABLE** | No stats feed in any season (0/2,158). No dev window, no trait, no line. |
| K-NO cards | **NOT-BUILDABLE** | No stats yellows in any season; event plain Yellows only from 2024 (target-definition break across dev); referee named in 0/2,158 matches (no X8 arm). |
| T-NO total shots | **NOT-BUILDABLE** | No stats feed in any season (0/2,158). No dev window, no trait, no line. |

**Nothing ships from NO-2Divisjon.** No arm passed all legs; no
predictions directory is shipped (deliberately — cf. the CH
precedent: a FAIL at the dev gate means the virgin is never read and
nothing is predicted).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `2901fa0` (wip
   branch) predates every engine/results artifact in this folder's
   history.
2. Virgin discipline: `results_virgin.json` does NOT exist for any
   candidate — G-NO failed dev, so the virgin was never read.
   2026 untouched (no engine reads any 2026 row).
3. The dev-gate failure is the same mode as the FI reference
   itself (G-FI: Gate Zero OU 0.7231 vs climatology 0.6921, FAIL dev
   gate OU leg). The verbatim FI sweep engine under-predicts totals
   here too: predicted mean total goals 3.00 / 2.99 / 2.86 vs actual
   3.39 / 3.33 / 3.45 per dev season. Diagnosis in
   `reports/G_NO_VERDICT.md`; no post-hoc repair was attempted.
4. The X2 entrant offset was DROPPED pre-fitting (EDA F4): 25 dev
   entrant transitions, mean GF +0.057 / GA +0.035, mixed signs —
   no systematic tilt. Arms are Gate Zero + SHRINK only.
5. The cards target choice: no K model was built despite event
   Yellow events existing from 2024 — the event target breaks
   across dev (0 plain Yellows in 2021–2023) and referee coverage
   is 0% everywhere. Evidence in `analysis/eda_summary.json`
   (`event_cards_by_season`) and EDA F5.
6. Format facts: two parallel groups (Avd. 1 / Avd. 2); 2022 is
   short (338 matches, Avd. 1 had 13 teams). One awarded match
   (4696470, 2025-03-31, played 4-3 → awarded 0-3) sits in the
   virgin season, kept as an ordinary flagged row — it was never
   read. Team id 10232 carries two spellings (Ullensaker/Kisa vs
   Ull/Kisa); all logic keys by team id.
