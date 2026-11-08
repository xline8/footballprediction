# RESULT — SE-Ettan [Muse-2]

Prereg frozen and pushed BEFORE any fitting: commit
`2fc8d51c13736643f6156b1c71abb11e21b7de08` (branch `wip-se-ettan`).
Dev ≤ 2024 (goals scored 2022–2024, warm-up 2021 partial, 262 played
matches); virgin = 2025 (n=480) read ZERO times — no arm passed dev,
so no virgin was scored; 2026 untouched confirmatory reserve. Gates
exactly as pre-registered; none moved.

## Verdicts

| Candidate | Verdict | Gate numbers |
|---|---|---|
| G-SE goals | **FAIL** (dev gate) | Virgin not read. Dev pooled (n=1440): DC Gate Zero 1X2 LL 1.0625 / RPS 0.2354 / OU2.5 LL 0.7126 vs climatology 1.0596 / 0.2380 / 0.6834 and naive trailing-10 1.1268 / 0.2333 / 0.7426 — passes 3/6 legs (1X2 vs naive, RPS vs climatology, OU2.5 vs naive) and loses 1X2 LL to climatology (+0.0029), RPS to naive (+0.0021), OU2.5 LL to climatology (+0.0291), so the dev gate (all three metrics vs BOTH baselines) fails. SHRINK identical: 1.0625 / 0.2354 / 0.7126 (no team with 1–5 prior in-league matches in any scored season's training data; sign check 3/3 by equality, moot). |
| S-SE SOT | **NOT-BUILDABLE** | No dev window: stats feed 0% in 2021–2025, shotmap 0/2,880. No trait reliability, no 1H share, no line selectable on dev. |
| C-SE corners | **NOT-BUILDABLE** | Same stats-era cause as S-SE: no dev season with a stats feed. |
| K-SE cards | **NOT-BUILDABLE** | No canonical cards target in dev: stats yellows 0% in every season. Event yellows exist 2022–2024 (4,745 plain Yellow; trait r 0.549; 1H share 0.2841) but 2021 has no events and referee coverage is 0% — revisiting needs a Jarvis decision (see reports/K_SE_VERDICT.md). |
| T-SE total shots | **NOT-BUILDABLE** | Same stats-era cause as S-SE: no dev season with a stats feed; shotmap 0/2,880. |

**Nothing ships from SE-Ettan.** No arm passed all legs; no
predictions directory is shipped (deliberately — there is no virgin
output to ship, and no `results_virgin.json` exists anywhere in this
folder).

## What Jarvis should check specifically

1. Prereg-before-fitting order: prereg commit `2fc8d51` predates
   every engine/results artifact. Dev results reproduce exactly
   (md5 of `engine/goals/results_dev.json` =
   `6f0054f0f9760df9f2308ff14bcf3d8c`).
2. Virgin discipline: there is NO `results_virgin.json`, no
   `virgin_rows_*.csv`, no `fitted_params_virgin.json` in this folder.
   G-SE failed the dev gate, so under the frozen mechanical reading
   the virgin was never read. 2026 was not scored or fitted on.
3. CSV vs raw counts: `se_matches.csv` played-match counts agree
   with the raw JSON in every season (2021: 262/480 index rows, 2022–
   2025: 480 each). The 218 unplayed 2021 fixtures all carry
   placeholder index scores "0-0" (Norra 95, Södra 123; rounds 1–12:
   136/192 unplayed, rounds 13–30: 82/288) and were excluded from
   every fit and metric.
4. Match awarded 4398485: the only score-vs-events mismatch
   (awarded 0–3, events 3–1); excluded from the halves-goals share
   only (goals_1h_share 0.4385 from 4,299 goals, 1,439 matches).
5. SHRINK identical to Gate Zero: verified, not a code error — no
   team had 1–5 prior in-league matches in any scored season's
   training data (entrants enter with n = 0 and sit at the
   league-mean fallback in both arms; every other team had n ≥ 9 in
   2022 and n ≥ 14 in 2023/2024), and a synthetic test proved the
   SHRINK scaling itself is active.
6. The cards flag: K-SE is not-buildable under the frozen split, but
   the event-yellows evidence (trait r 0.549, 1H share 0.2841,
   3.28–3.44 yellows/match 2022–2024) is materially better than QA's
   (zero plain Yellows in dev). Revisiting K needs a program decision
   to (i) adopt event-derived yellows as the target by definition and
   (ii) re-split dev to start in 2022. No K engine is built without
   that decision.
7. Halves constants: only `goals_1h_share: 0.4385` is frozen (dev-era
   event times, 4,299 goals, 1,439 matches). All four count-market
   halves constants are `null` — 0 dev matches have period splits,
   so none is computable. No halves model was built for any count
   market.
8. Diagnosis, recorded not acted on: the DC score matrix
   systematically under-predicts total goals — mean predicted OU2.5
   over-rate 0.5065 vs actual 0.5833 pooled (per season 0.5013 vs
   0.5854, 0.5043 vs 0.5646, 0.5138 vs 0.6000), computed from
   `engine/goals/results_dev.csv` — and over-predicts home wins
   (mean predicted home-win probability 0.4906 vs actual 0.4313).
   Fitted home intercept falls by season (0.4822 / 0.3506 / 0.3321;
   rho 0.0 in all three fits). Hypothesis (not established): with a
   single home intercept and no group term, the fitted lambdas
   compress the total-goals level toward the league mean while
   over-weighting the home side. No post-hoc repair was attempted
   inside this prereg.
