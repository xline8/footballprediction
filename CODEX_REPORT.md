# Codex report

## Job 1

Added `shrunk_ev(p_shrunk, odds, p_push)` to `ta_model.py` and used it in the
candidate loop. The helper returns
`(1 - p_push) * (p_shrunk * odds - 1)`. Added two unit tests: one checks the
push correction against a hand calculation and the old formula, and one checks
bit-identical behavior when `p_push == 0`.

Impact on the live `ta/model_markets.csv`:

- 46 rows have `p_push > 0`.
- 2 rows cross the `MIN_EV = 0.03` threshold, both from pass to fail.
- The number of eligible per-game winners stays 21; 1 per-game winner changes
  (`DNB Dnb1` to `1X2 1` for game `954678`).

Tests:

- `tests/test_units.py`: **121 passed**.
- Live `test_core.py`: **all tests passed**.

## Job 2

The audit script and report are in:

- [audit_pick_teraman.py](/home/hatch/workspace/fp-ev-wt/experiments/pick_audit/audit_pick_teraman.py)
- [AUDIT_PICK_TERAMAN.md](/home/hatch/workspace/fp-ev-wt/experiments/pick_audit/AUDIT_PICK_TERAMAN.md)

Headline numbers from the same 2026-10-29 to 2026-11-08 window:

- Selected Pick Teraman: **80.0% hit rate vs 82.0% predicted, -2.0pp, n=70**.
- All settleable candidates: **50.0% vs 50.0%, 0.0pp, n=3,546**.
- Pool maximum: **81.9% vs 81.6%, +0.2pp, n=226**.
- Selection effect versus all candidates: **-2.0pp**; versus pool maximum:
  **-2.3pp**.
- OU is the negative contributor: **-4.2pp, n=56**. DC is **+6.4pp, n=14**.
- The window contains about **38%** of the headline -5.4pp gap's magnitude
  (n=70 versus headline n=170).

The full audit, including Brier score, log loss, tier breakdown, exclusions,
and the archive-format caveat, is in the linked report.
