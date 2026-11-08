# BRIEF — K-CO join proof, run 2 (CO-PrimeraA cards, arm X8, PROVISIONAL)

Issued by the join coordinator, 2026-11-12 ~17:40 WIB.
Worker: Codex luna (`~/.local/bin/codex`, stdin closed). No push, ever.
You do the PROOF ONLY. You do NOT merge — merging is the coordinator's
job after it verifies your evidence.

## Starting state (already done by the coordinator — verify, do not redo)

- Worktree `~/workspace/wt-lane1-kco`, branch `build/lane1-kco`, at
  commit `d42ab8d1`: the runner prep (old `423d37b7`) cherry-picked onto
  live HEAD `740233d6` ("Fix league settle double grading").
  Cherry-pick conflicts in `league/runner/run_daily.py` and
  `league/runner/README.md` were resolved as UNIONS: live HEAD's
  TZ/FO/ID adapter features (goals `shrink` arm + `team_key: name`,
  cards `exclude_excluded` + `exclude_phases`, cards arms `shrink`/`x5`,
  the `_predict` dispatch) AND the settle dedup fix are intact, plus
  CO's `event_unified_yellows` target + `kickoff_utc` additions.
  Verify before starting: `git diff 740233d6 --stat` must show exactly
  3 files (README +1 line, active.yaml +11, run_daily.py 38+/5−).
  If it shows anything else, STOP and report.
- `data_enrichment/fotmob_world` in the worktree is a symlink resolving
  to the main checkout's warehouse (verified by the coordinator). Do NOT
  re-create it. The worktree has no `.venv` — use the main checkout's
  `.venv` (`~/workspace/footballprediction/.venv/bin/python`) for every
  run. Run every runner invocation with `MALLOC_ARENA_MAX=2`.
- The referee operational gate PASSED 2026-11-12 16:58 WIB: 2/10 upcoming
  Clausura Round 19 fixtures carry named referees — Deportivo Pasto vs
  Junior FC (2026-11-12, match 1000014235, Diego Alejandro Ruíz Casas)
  and Llaneros FC vs Chicó FC (2026-11-13, match 1000014232,
  Carlos Márquez). Evidence:
  `league/improvement_scratch/KCO_RECHECK/recheck_2026-11-12_1658.json`
  (in the main checkout; the worktree has the same file via the branch).
- The FIRST proof attempt (2026-11-12 ~10:00) stalled at the missing
  symlink and ran ZERO proof runs. Its log is the existing
  `league/improvement_scratch/KCO_JOIN/codex.log` (153 KB, mostly a
  grep dump). APPEND your progress to that file with a clear timestamped
  separator line ("=== PROOF RUN 2 starts 2026-11-12 HH:MM WIB ===").
  Do NOT delete the old log.

## Task: standard join proof (the G-TZ / K-FO / K-ID pattern)

Follow the methodology of `~/workspace/kfo-proof/` exactly (snapshot
layout `pre/` / `run1/` / `run2/`, `diff -r` compare,
`synth_settle_fo.py` pattern). Full spec is in
`league/improvement_scratch/KCO_JOIN/brief.md` — read it. Snapshot
directory for THIS proof: `~/workspace/kco-proof/` (persistent; never
/tmp — /tmp is wiped on runtime restarts).

1. Pre-run snapshot of the worktree's current prediction outputs
   (`league/*/predictions/` daily CSVs + ledgers + settled-keys sidecars,
   `league/*/reports/grading_ledger.jsonl`,
   `league/runner/run_log.jsonl`) to `~/workspace/kco-proof/pre/`.
2. Two full end-to-end runner runs from the worktree:
   `cd ~/workspace/wt-lane1-kco && MALLOC_ARENA_MAX=2
   ~/workspace/footballprediction/.venv/bin/python league/runner/run_daily.py`
   Each takes ~30 min. Run them SEQUENTIALLY, never in parallel with
   other heavy jobs (this VM OOM-kills under parallel load — the RU
   join lost five attempts that way). Record per run: exit code,
   duration, total predictions, settled, errors (from
   `league/runner/run_log.jsonl`), fetched_new per league.
   Run 2 must show fetched_new=0 in every league. Snapshot outputs
   after each run to `~/workspace/kco-proof/run1/` and `run2/`.
   Keep the runner's stdout logs as `run1.log` / `run2.log` there.
3. Byte-compare ALL prediction/state snapshot files between the two
   runs (`diff -r run1 run2`, save to `diff_run1_run2.txt`).
   Only `run_log.jsonl` may differ by design. Any other diff must be
   explained concretely as a live-feed change (fixture added/moved/
   renamed) with numeric proof that predicted values are bit-equal —
   never hand-waved.
4. CO checks: CO cards must predict its upcoming fixtures (expect ~10,
   12–14 Nov) with 0 errors. Independent recompute of ALL CO live
   predictions (separate process, through the frozen engine/harness
   path) must be diff 0.0 on every float field. Verify the cards
   history row count the amended adapter loads matches the frozen
   harness expectation (1,336 dev-era rows per the prep README).
5. Inertness: the amended adapter must be proven no-op for existing
   leagues. Re-run the prep's probes against the CURRENT worktree
   code (which now also carries the FO/ID adapter features the prep
   predates): AR-PrimeraBNacional cards (`x8`) and AU-ALeague cards
   (`gate_zero`) — HEAD-vs-amended `predict_cards` on fixed fixtures
   byte-identical. The run1-vs-run2 byte-compare covers all other
   leagues. Any adapter change you need must be proven no-op the
   same way before the proof runs.
6. Synthetic settlement on one finished CO match (suggested: 5121316,
   2026-01-16 Deportivo Pereira–Llaneros FC, the prep replay fixture
   — verify its event-unified yellow actuals are complete first, else
   pick another finished CO match with complete actuals). Follow the
   `synth_settle_fo.py` pattern: adapter predict + write_predictions
   + settle → settles exactly once, a second settle pass settles
   nothing, touched files restored byte-identical afterwards (verify
   against sha256 snapshots taken before). NOTE the live `settle()`
   semantics (cherry-picked fix 740233d6): canonical prediction =
   LAST run_date ≤ match date, grading key `market:match_id` — use
   `settle()` as-is and verify 1-then-0 under those semantics.
7. Update the README CO paragraph from "PREPARED BUT BLOCKED" to
   joined state: gate passed 2/10 on 2026-11-12 16:58 (names above),
   proof numbers from this run, PROVISIONAL status. Keep the prep's
   verification claims that remain true.
8. Write the full proof report to
   `league/improvement_scratch/KCO_JOIN/report.md` on the branch and
   commit it together with the README update (and this brief) on
   branch `build/lane1-kco`, using explicit `git add` paths.
   Commit message: `K-CO join proof: <one-line verdict + key numbers>`.

## MERGE-READY means every check above passes with evidence

If any check fails, STOP. Do NOT merge, do NOT "fix" a gate, do NOT
re-read sealed data (this proof uses live/future fixtures only).
Report exactly which check failed, with the numbers and file evidence.

## Rules

- Gates never move; no retroactive passes; the sealed window stays
  sealed (already read once for the verdict — do NOT read it again).
- Never push. Never touch the main checkout
  (`~/workspace/footballprediction`), top-5 production code, other
  leagues, or the morning report. The main checkout carries
  uncommitted runner-output modifications — leave them untouched.
- Never edit `~/MEMORY.md` or `~/workspace/goals/`.
- Do not copy warehouse data into the worktree (the CO fresh-worktree
  trap did not trigger in any prior proof run — the symlinked
  warehouse covers CO's Primera B reads).
- If a run is killed by a runtime restart or OOM, relaunch it from
  scratch and say so plainly in the log and report; a partial run is
  not a proof.
