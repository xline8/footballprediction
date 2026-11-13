# Senior developer audit, 2026-11-13

Scope: the top-five daily pipeline, its API and file contracts, the repository
documentation, and read-only checks of the world-league programme. The frozen
league engines were not changed. Model mathematics, thresholds, gates, and the
recommendation and grading rules were not changed.

## Findings

### FIXED

1. **A failed market-date fetch was reported as a healthy product.**
   `ta_scrape.sync_dates()` returns `failed_dates` when a current or past date
   cannot be fetched or parsed. Step 14 of `run_daily_shadow.py` printed that
   list, then unconditionally stored `market_sync=OK` and allowed the run to
   exit 0. This contradicted the per-product status contract and hid missing
   odds pages from monitoring. A regression drives the actual daily-chain
   `main()` with a failed-date result. Before the fix it exited normally and
   stored `OK`; afterwards it exits 1 and stores `FAILED`. Future unpublished
   pages remain non-fatal because the scraper classifies them as
   `empty_dates`, not `failed_dates`.

   Commit: **NOT AVAILABLE**. The linked worktree's Git administration path is
   `/home/hatch/workspace/footballprediction/.git/worktrees/fp-codex-audit-wt`,
   outside the writable roots supplied to this session. `git commit` failed
   while creating `index.lock` with `Read-only file system`.

2. **The README's world-index count was stale.** The checked-in CSV has
   233,619 data rows and 233,619 unique `match_id` values across 158 FotMob
   league IDs. The README said 233,618. Corrected to the data in this tree.

   Commit: **NOT AVAILABLE** for the same worktree-permission reason.

3. **The README overstated launcher setup on Unix.** `start.bat` creates
   `.venv` and installs `requirements.txt`; `football_cli.py` does neither.
   The quick start now distinguishes the Windows bootstrap from the Unix CLI.

   Commit: **NOT AVAILABLE** for the same worktree-permission reason.

4. **The README documented an API-Football runtime integration that is not in
   this tree.** No current Python or shell entry point reads
   `API_FOOTBALL_KEY`; the only repository references are historical prose in
   `CHANGELOG.md` and `MUSE_SNAPSHOT.md`. The environment section no longer
   tells operators to configure a non-existent optional feed.

   Commit: **NOT AVAILABLE** for the same worktree-permission reason.

5. **The README voice obscured who runs the system and decorated list labels
   instead of stating results.** Rewritten using the requested no-ai-slop
   rules: the opening is in the operator's voice, claims are concrete, bold
   run-in labels were removed where they added no structure, and the existing
   section order and single coverage table were retained.

   Commit: **NOT AVAILABLE** for the same worktree-permission reason.

### NOT FIXED

6. **The API freshness rule covers league predictions only.**
   `load_predictions()` returns 503 after 48 hours, but
   `load_corner_predictions()` falls back to `predictions_corners.csv` and
   serves either corner file without an age check. `/api/odds` also reads the
   season files rather than a run-stamped product. This audit did not impose a
   new product-wide freshness policy because the acceptable ages and fallback
   behavior are not defined in code or tests.

7. **A fresh but empty or malformed prediction CSV can look healthy.** The API
   checks only existence and mtime before returning `csv.DictReader` rows. It
   does not require the prediction schema or a non-empty set of relevant
   fixtures. The producer checks its own status, but the API has no contract
   tying the file to the latest successful `run_status` record. Not fixed
   because an empty schedule can be valid; the product needs an explicit
   manifest or expected-row contract rather than a guessed `len(rows) > 0`
   rule.

8. **The daily pipeline still has file contracts encoded as ad hoc checks.**
   Some products check subprocess return code and mtime, corners additionally
   check row count, while market comparison and recommendation steps trust
   return dictionaries and process-global file names. There is no common
   manifest carrying schema version, generation timestamp, report date,
   producer status, and row count. This is the main stale-data seam left in
   the top-five chain. A shared contract would touch many products and was too
   broad for an evidence-led tidy-up.

9. **Broad exception handling remains in reporting and compatibility paths.**
   Examples include `_cup_fixture_ids()` returning an empty list for every
   exception and the API status endpoint ignoring an unreadable
   `last_full_pipeline.json`. Some of these fallbacks are deliberate, but they
   erase the difference between "no data" and "data could not be read". They
   were not changed without product decisions about which failures should
   change exit status or HTTP status.

10. **No files or functions were removed as dead code.** The tree has nearly
    20,000 tracked files and about 1,980 Python files, most of them frozen
    world-league evidence and engines. A text search alone cannot prove that a
    standalone script is dead because cron, systemd, and operator invocations
    are external callers. Removing such files without deployment inventory
    would violate the brief's proof requirement.

### NEEDS DECISION

11. **Should every published API product use one freshness contract?** Decide
    whether corners, odds, picks, cards, SOT, and half splits should all return
    503 based on the latest successful daily manifest, and choose a maximum age
    for each. The current 48-hour prediction rule cannot safely be copied to
    every product without that decision.

12. **Should partial market coverage fail the run?** This fix treats
    `failed_dates` as failure. `unresolved_market_ids` and same-day
    `empty_dates` are still visible but non-fatal. If every model fixture must
    have a TipsterArea mapping and odds page, define the allowed coverage ratio
    and make it a gate; zero tolerance may be wrong for unpublished fixtures.

13. **Git permissions must be repaired before handoff.** The requested commit
    history cannot be created while the linked worktree administration
    directory is read-only. The changes are present in the requested worktree,
    but they remain uncommitted.

## Highest-priority gaps

The missing producer-to-consumer manifest is the largest operational risk. A
file mtime says that something wrote a path; it does not say which run wrote
it, which schema it used, or whether it contains the expected report date.
Second is API freshness outside `predictions_upcoming.csv`. Third is explicit
coverage policy for market sync: monitoring now catches failed date pages, but
it still does not decide how many unresolved fixtures are acceptable.

## Verification evidence

- Focused before/after reproduction: the new daily-chain regression failed
  before the fix with exit code `None` and `market_sync=OK`; it passes after
  the fix with exit code 1 and `market_sync=FAILED`.
- README count: `data_enrichment/fotmob_world_index.csv` contains 233,619 data
  rows, all with unique `match_id` values, and 158 distinct `league_id` values.
- No-ai-slop self-check: passed after the final edit. The settled section order
  and one coverage table remain; no new research claim or metric was added.
- Unit suite: `tests/test_units.py` passed all 121 tests with the required
  production virtualenv.
- Data-dependent core suite: `test_core.py` passed every check (`SEMUA TES
  LULUS`) with the required production virtualenv.
- Changed Python byte-compilation: `run_daily_shadow.py` and
  `tests/test_units.py` compiled successfully.

Test count is now 121 rather than 120 because one regression was added for the
market-sync status bug. No test was removed.

## Closing update, 2026-11-13 — fix-all order

The implementation below is complete in the `fixall` working tree, but it
could not be committed. This clone's `.git` directory and index are mounted
read-only (`root:nogroup`); `git commit` failed with `Unable to create
'.git/index.lock': Read-only file system`. Therefore no honest commit hash
exists. The findings are marked **FIXED IN WORKTREE (COMMIT BLOCKED)** rather
than inventing a hash. This is the one remaining handoff blocker.

6. **FIXED IN WORKTREE (COMMIT BLOCKED) — product-wide API freshness.**
   `api_server.py` now has one shared missing/stale product-file check using
   `MAX_PREDICTIONS_AGE_HOURS = 48`. It covers league predictions, the corner
   primary file or whichever fallback is actually served, and the picks
   ledger. `/api/odds` is derived from football-data season files through
   `load_fd_odds`; those are historical/reference inputs and are explicitly
   outside the new daily-product gate. This API has no cards, SOT, or half
   split endpoint.

7. **FIXED IN WORKTREE (COMMIT BLOCKED) — malformed/empty CSVs.** League and
   corner loaders require their endpoint identity columns (`div`, `date`,
   `home`, `away`) and at least one data row. Missing file, stale file,
   missing columns, and empty product now produce distinct HTTP 503 details.
   Model-output columns remain nullable as the existing endpoint contract
   requires.

8. **FIXED IN WORKTREE (COMMIT BLOCKED) — run manifest.** The real
   `_write_run_status()` path also writes `logs/run_manifest.json` and
   `logs/run_manifest_<date>.json` atomically. Each product records `name`,
   `status`, `detail`, canonical single `file` or null, UTC file mtime as
   `generated_at`, and CSV data-row count or null. Top-level fields are
   `schema_version: 1`, `report_date`, and `run_finished_at`. `/api/status`
   adds report date, OK/FAILED counts, and manifest age when available; an
   absent manifest remains harmless.

9. **FIXED IN WORKTREE (COMMIT BLOCKED) — visible fallbacks.**
   `_cup_fixture_ids()` in `pipeline_orchestrator.py` now warns with exception
   type and message before retaining its existing empty-list fallback.
   `/api/status` warns and reports `last_full_pipeline.status=unreadable` when
   that JSON cannot be parsed. The requested sweep of `api_server.py` and
   `run_daily_shadow.py` found no other exception handler that silently
   returns empty/None: the numeric/date parsing handlers are intentional
   per-value conversions, while `_Tee` handlers are best-effort stream writes
   and do not manufacture product data. Manifest parse/count failures now
   print warnings too.

11. **FIXED IN WORKTREE (COMMIT BLOCKED) — one freshness contract.** This is
    implemented by the shared helper described under finding 6, with no new
    dependency and no stricter existing product rule weakened.

12. **FIXED IN WORKTREE (COMMIT BLOCKED) — market coverage rule.** Every
    completed market-sync product detail includes
    `unresolved_market_ids=<count>` on success and failure. A result with
    `markets == 0` and unresolved fixtures now marks `market_sync=FAILED` and
    fails the run. Zero markets with zero unresolved remains OK and explicitly
    says the window is genuinely empty. Existing failed-date behavior remains
    a hard failure.

### Closing verification evidence

- Required unit command: **126 unit tests passed** (five new regressions;
  previously 121). Coverage includes shared API freshness/schema/empty-file
  behavior, corner fallback freshness, picks freshness, the production
  manifest writer, unresolved-zero-market failure, and the genuine-empty
  success case.
- Required core command: `test_core.py` finished with **SEMUA TES LULUS**.
- Byte compilation passed for every changed Python file:
  `api_server.py`, `run_daily_shadow.py`, `pipeline_orchestrator.py`, and
  `tests/test_units.py`.
- API evidence used the real FastAPI app and real product files through an
  in-process ASGI transport. Socket-based startup reached application startup
  but this managed environment rejected binds on both spare loopback ports
  8765 and 18765. With fresh files, `/api/predictions`, `/api/corners`, and
  `/api/picks` returned 200. After setting each served file to 72 hours old,
  the same endpoints returned 503 with `umur 72.0 jam > batas 48.0 jam`.
  Replacing `predictions_upcoming.csv` with a header-only CSV returned 503
  with `kosong (tidak ada baris data)`. Original contents and mtimes were
  restored afterward.
- Status evidence with deliberately unreadable `last_full_pipeline.json`
  reported `{'status': 'unreadable'}` and logged the `JSONDecodeError`; the
  same response summarized the manifest as report date `2026-11-13`, one OK
  product, one FAILED product, and its age.
- A focused harness called the production `_write_run_manifest()` code path
  (not a full 23-step chain). The resulting real
  `logs/run_manifest.json` contained:

      predictions: status=OK, file=predictions_upcoming.csv,
      generated_at=2026-11-13T12:48:06.960160+00:00, rows=1275
      market_sync: status=FAILED, detail="markets=0;
      unresolved_market_ids=2", file=null, generated_at=null, rows=null

- No model mathematics, fitted parameters, thresholds, gates,
  recommendation/slip logic, graders, or `league/` engine files changed.

### Handoff completed by Jarvis, 2026-11-13

The commit blocker above was a sandbox mount restriction, not a code
problem. Jarvis re-verified the working tree independently (126 unit tests
and `test_core.py` pass; no model, gate, slip, or league files touched),
created the commits on the `fixall` branch, and pushed them to `main`.
The same changes were then ported to the production deployment and
verified live there.
