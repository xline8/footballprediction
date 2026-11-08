# BRIEF — K-CO join proof (CO-PrimeraA cards, arm X8, PROVISIONAL)

Issued by the improvement-program watchdog, 2026-11-12 ~16:58 WIB.
Worker: Codex luna (`~/.local/bin/codex`, stdin closed). No push, ever.
No touching top-5 production, other crons, or the morning report.

## Why now

- K-CO passed Lane 1 provisionally on 2026-11-11 19:08 WIB (verdict in
  `league/IMPROVEMENT_STATUS.md`; prereg commit 6557938e; dev X8
  LL@5.5 0.691751 vs base 0.695579 / naive 0.707987; single sealed read
  2026-Apertura n=204: leg (i) PASS — X8 LL@5.5 0.665796, best of four;
  calibration −1.574pp, SE 3.413pp → PROVISIONAL; sign 5/5).
- Shipping was BLOCKED only by the referee operational gate (user
  decision 2026-11-11 19:47 WIB: HOLD AND RECHECK — join as PROVISIONAL
  when ≥1 upcoming fixture carries a named referee).
- **Gate NOW PASSED, rechecked 2026-11-12 16:58 WIB: 2/10 upcoming
  Clausura Round 19 fixtures carry named referees** — Deportivo Pasto
  vs Junior FC (2026-11-12, match 1000014235, referee Diego Alejandro
  Ruíz Casas) and Llaneros FC vs Chicó FC (2026-11-13, match
  1000014232, referee Carlos Márquez). Evidence:
  `league/improvement_scratch/KCO_RECHECK/recheck_2026-11-12_1658.json`
  in the main checkout (verify it yourself before starting — re-run
  `league/improvement_scratch/KCO_RECHECK/recheck_referees_1658.py`
  with the main checkout's `.venv` if you want an independent read).
- Join prep is already done on branch `build/lane1-kco` (commit
  423d37b7): `league/runner/active.yaml` cards block (arm x8,
  primary 5.5, ladder [3.5, 4.5, 5.5, 6.5], halves 0.3543,
  `exclude_seasons` 2021–2022 Apertura/Clausura, `cards_target:
  event_unified_yellows`, `cards_actual:
  [ev_yellow_inc2nd_home, ev_yellow_inc2nd_away]`) + `run_daily.py`
  adapter + README. Worktree: `~/workspace/wt-lane1-kco`.

## Task: standard join proof, then merge iff MERGE-READY

Follow the established join-proof pattern exactly as recorded for
G-TZ (merged c979d05a), K-FO (885a27bb) and K-ID (8f8b4b00) in
`league/IMPROVEMENT_STATUS.md` and `league/PROGRAM_STATUS.md`:

1. Work in `~/workspace/wt-lane1-kco` on branch `build/lane1-kco`.
   Confirm the worktree is at 423d37b7 and its
   `data_enrichment/fotmob_world` symlink points at the main
   checkout's warehouse (restore it if missing — git-ignored, no
   commit impact). Use the worktree's `.venv` if present, else the
   main checkout's `.venv`. Run with `MALLOC_ARENA_MAX=2`.
   NOTE: CO's builder also reads Primera B warehouse JSONs — the
   fresh-worktree trap did NOT trigger for CO in any prior proof run
   (warehouse present via the symlinked main-checkout warehouse);
   do NOT copy warehouse data into the worktree.
2. Two full end-to-end runner runs from the worktree. Each takes
   ~30 min. Record predictions/errors/fetched_new per run. Run 2
   must show fetched_new=0 in every league.
3. Byte-compare ALL prediction/state snapshot files between the two
   runs. Only `run_log.jsonl` may differ by design. Any other diff
   must be explained concretely as a live-feed change (fixture
   added/moved/renamed) with numeric proof that predicted values
   are bit-equal — never hand-waved.
4. CO must predict its upcoming fixtures (expect ~10, 12–14 Nov)
   with 0 errors; independent recompute of ALL CO live predictions
   must be diff 0.0 on every float field. Verify the cards history
   row count loads exactly as the frozen harness expects.
5. Inertness: other leagues' outputs unchanged vs the HEAD runner
   (byte-identical on a probe set covering the cards adapter and
   neighbouring arms). Any adapter change you need must be proven
   no-op for existing leagues.
6. Synthetic settlement on one finished CO match: settles exactly
   once, a second settle pass settles nothing, files restored
   byte-identical afterwards.
7. Write the full proof report to
   `league/improvement_scratch/KCO_JOIN/report.md` on the branch and
   commit it there.

## Merge (ONLY if every check above passes = MERGE-READY)

- Merge `build/lane1-kco` into the main checkout
  (`~/workspace/footballprediction`, branch `local/fotmob-source`,
  currently 740c6316). The main checkout currently carries
  uncommitted runner-output modifications (daily CSVs, settled_keys
  sidecars, xg_raw, fotmob_world_index) — do NOT commit, discard,
  or touch them; merge only the branch.
- Resolve any `active.yaml` / README / `run_daily.py` conflicts as
  the UNION of both sides' league entries (the TZ/FO/ID precedent).
- Verify the merged state: `active.yaml` parses via the runner's
  own parser to **63 leagues / 123 markets**, `run_daily.py`
  compiles, CO cards history loads under the merged code.
- Commit the merge in the main checkout. Then append the join event
  to `league/IMPROVEMENT_STATUS.md` (heartbeat line + event-log
  entry, same format as the G-TZ/K-FO/K-ID entries) and commit that
  too. No push.
- Report back: MERGE-READY + merge commit hash + runner counts
  (63/123) + CO upcoming/predicted/errors + recompute diff.

## If NOT MERGE-READY

Stop. Do NOT merge. Report exactly which check failed, with the
numbers and file evidence. Leave the branch and worktree as they are.

## Rules

- Gates never move; no retroactive passes; the sealed window stays
  burned for this candidate (it was already read once — do NOT read
  any sealed data again; this proof uses live/future fixtures only).
- Never push. Never edit `~/MEMORY.md` or `~/workspace/goals/`.
- Log progress with timestamps to
  `league/improvement_scratch/KCO_JOIN/codex.log` in the worktree
  (append as you go) so the watchdog can follow it.
