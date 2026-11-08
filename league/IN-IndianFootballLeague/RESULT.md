# RESULT — IN-IndianFootballLeague [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`83d1b1f590f459abc0417c895c55a3793068bec2` (branch `wip-in-indianfootballleague`).
Dev ≤ 2024/2025 (goals scored 2022/2023–2024/2025, warm-up 2021/2022);
virgin = 2025/2026 (n=66, complete season) read ZERO times — no arm
passed dev, so no virgin was scored; 2026/2027 untouched confirmatory
reserve. Gates exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-IN goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=418): DC Gate Zero 1X2 LL 1.0861 / RPS 0.2337 / OU2.5 LL 0.7568 vs climatology 1.0813 / 0.2365 / 0.6903 and naive trailing-10 1.1344 / 0.2320 / 0.7399 — passes only 2 of 6 legs (RPS vs climatology; 1X2 LL vs naive). The OU leg is lost to BOTH baselines, driven by the first scored season (OU 0.8303 vs climatology 0.6948 in 2022/2023) as the expanding fit chased the rising goals level (2.579 → 3.331 across dev); by 2024/2025 the model won OU outright but the pooled gate is frozen. SHRINK identical (n<6 never binds under season-blocked prediction). X2 NOT RUN — dropped pre-fitting (EDA F4: 6 entrant transitions, GF −0.110 / GA +0.025, signs mixed). |
| S-IN SOT | **NOT-BUILDABLE** | No target in any season: stats feed 0% in 2021/2022–2026/2027 (0/608 matches, 0 stats keys in any raw JSON), no shotmap, no event-derived SOT substitute. No trait reliability, no 1H share, no line selectable on dev. |
| C-IN corners | **NOT-BUILDABLE** | Same stats-absence cause as S-IN: no corners target in any season under any source; X7 input (`touches_opp_box`) absent too. |
| K-IN cards | **NOT-BUILDABLE** | No consistent yellows target in dev under either source: stats yellows absent in every season; event feed carries zero plain Yellow events in every dev season AND in the virgin (YellowRed + Red only) — plain Yellows exist only in the untouched reserve (27 in 2026/2027), a definition break outside the modelled eras. Referee named in 91.3% of dev matches but only 4/66 in the virgin, so no X8 arm could ship regardless. |
| T-IN total shots | **NOT-BUILDABLE** | Same stats-absence cause as S-IN: no total-shots target in any season, no shotmap. |

**Nothing ships from IN-IndianFootballLeague.** No arm passed all
legs; no predictions directory is shipped (deliberately — there is no
virgin output to ship, and no `results_virgin.json` exists anywhere in
this folder).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `83d1b1f`
   predates every engine/results artifact. Full snapshot history on
   branch `wip-in-indianfootballleague`: fase 1 `52b0941`, fase 2
   `64ed459`, prereg `83d1b1f`, fase 6–7 snapshot after this RESULT.
2. Virgin discipline: there is NO `results_virgin.json`, no
   `virgin_rows_*.csv`, no `fitted_params_virgin.json` in this folder.
   G-IN failed the dev gate, so under the frozen mechanical reading
   the virgin was never read. 2026/2027 was not scored or fitted on.
3. The central EDA finding — this is a scores-only league in the
   strongest sense: stats feed 0% in EVERY season (0/608 matches,
   0 stats keys in any raw JSON), shotmap 0/608, period splits
   0/608. No `expected_goals` key anywhere, so the X1 blend runs in
   its documented goals-only fallback. The frozen split was NOT
   moved to manufacture a dev window for S/C/K/T.
4. X2 was dropped pre-fitting, not post-hoc: 6 dev entrant
   transitions with mean GF −0.110 / GA +0.025 and mixed signs
   (EDA F4) — the CH/NO/FR/SE drop pattern. G-IN ran Gate Zero +
   SHRINK only; SHRINK is bit-identical to Gate Zero (results_dev
   md5 reproducible on re-run).
5. Identity/rebrand: the league is the I-League (tier 2) renamed
   "Indian Football League" from 2025/2026 — same FotMob id 8982,
   `general.leagueName` is the only marker. Split-phase groups
   exist in 2021/2022 (Championship/Relegation) and in the virgin
   2025/2026 (Promotion/Relegation); all are ordinary rows, phase
   flag carried, never filtered.
6. Virgin completeness (checked in EDA, not assumed): 2025/2026
   has its full structure — 45 regular (single round-robin of 10
   teams) + 15 promotion-group + 6 relegation-group matches — and
   2026/2027 has already begun, so 2025/2026 is a complete season.
   Its n=66 is small; the gate was applied as written.
7. Cards nuance for the ledger: referee coverage is REAL in dev
   (453/496, 91.3%) — unlike BY — but K-IN still dies on target
   absence in dev (plain Yellow = 0 in dev and virgin), and virgin
   referee coverage collapses to 4/66.
8. The 4 score/event mismatches are exactly the 4 awarded matches
   (disciplinary 0-3/3-0 awards; header score used). The 34
   no-event matches are all 0-0 draws per the header (0 goals in
   them); their events-derived fields are missing, never zero.
