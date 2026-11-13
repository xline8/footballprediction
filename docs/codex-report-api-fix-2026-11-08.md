# API fixes: 2026-11-08

Implemented Fix 1 and Fix 2 in worktree A on `fix/api-consistency-2026-11`.

Files changed in worktree A:

- `api_server.py`: the exact-match endpoint now includes `p_over_dc`, `p_over15_dc`, `p_over35_dc`, `p_over_bl`, `p_dc_1x`, `p_dc_x2`, `p_dc_12`, and `p_btts`. It uses the list endpoint's field mapping: present values become floats; missing or empty values become `None`.
- `api_server.py`: `load_predictions()` now raises HTTP 503 with detail `Predictions file predictions_upcoming.csv is missing` when the file is absent. Both prediction endpoints use this loader. File-present behavior stays unchanged, including an empty list for a file with no rows and HTTP 404 for an unmatched exact-match request.
- `tests/test_units.py`: added three regression tests using the existing in-process import-stub and temporary-directory pattern. They cover all eight values, empty cells, absent columns, both missing-file failures, and file-present empty results.
- `CODEX_REPORT.md`: this report.

Validation used `/home/hatch/workspace/footballprediction/.venv/bin/python`:

- `tests/test_units.py` before changes: 95 passed.
- `tests/test_units.py` after changes: 98 passed.
- `test_core.py`: passed, exit code 0.
- `git diff --check`: passed.

Worktree B was not changed or inspected. Fix 3 and its README step-count review belong to the separate worktree task.

The brief describes the missing-file exact-match baseline as HTTP 200, but the code returned HTTP 404 after the loader returned no rows. Both endpoints now raise HTTP 503 for a missing file as requested. No stale-age policy was added. Other endpoints, slip logic, models, and the pipeline were left unchanged. No network or git-remote operations were run.

Local commit was attempted with message `Fix prediction API fields and missing-file errors`, but staging and committing both failed: Git could not create `/home/hatch/workspace/footballprediction/.git/worktrees/fp-fix-wt/index.lock` because that metadata directory is read-only in this session. The three files remain uncommitted in worktree A. Completing the commit requires write access to the worktree's Git metadata.
