"""P2 self-test on AE-ProLeague — proves the filter bites.

AE-ProLeague is the AUDIT.md section 3 exemplar: its shipped EDA table
(analysis/EDA.md, F1) prints a row "2025/2026 (virgin)" — the sealed
season's levels sat in front of the builder at design time.

This test shows, on the league's real data (data/ae_matches.csv):
  1. PRE-FILTER contamination is possible: an EDA-style per-season level
     table computed the way the old generator did (all seasons) contains
     the sealed season 2025/2026 (and its shipped eda_numbers.json does too).
  2. POST-FILTER: the same computation over filter_rows(...) output
     contains ZERO sealed rows, and assert_dev_only passes on it while
     raising SealViolation on the unfiltered table.

Run: .venv/bin/python -m league.design_seal.self_test   (exit 0 = pass)
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from seal import SealViolation, assert_dev_only, count_sealed_rows, filter_rows, load_seal
else:
    from .seal import SealViolation, assert_dev_only, count_sealed_rows, filter_rows, load_seal

ROOT = Path(__file__).resolve().parents[2]
LEAGUE = ROOT / "league" / "AE-ProLeague"


def level_table(rows):
    """EDA F1-style per-season level table (mean total goals per season)."""
    by_season = {}
    for r in rows:
        by_season.setdefault(r["season"], []).append(int(r["home_goals"]) + int(r["away_goals"]))
    return {s: {"n": len(v), "goals": statistics.mean(v)} for s, v in sorted(by_season.items())}


def main() -> int:
    seal = load_seal(LEAGUE)
    assert seal.sealed_seasons == ["2025/2026", "2026/2027"], seal.sealed_seasons
    rows = list(csv.DictReader((LEAGUE / "data" / "ae_matches.csv").open(encoding="utf-8")))
    print(f"league={seal.league} dev={seal.dev_seasons} sealed={seal.sealed_seasons}")
    print(f"raw rows={len(rows)} sealed rows in raw data={count_sealed_rows(rows, seal)}")

    # 1) Pre-filter: contamination is possible (and in fact shipped).
    unfiltered = level_table(rows)
    assert "2025/2026" in unfiltered, "expected sealed season in unfiltered table"
    try:
        assert_dev_only(unfiltered, seal, "unfiltered level table")
        raise SystemExit("FAIL: assert_dev_only did not raise on the unfiltered table")
    except SealViolation as exc:
        print(f"pre-filter table contains sealed season 2025/2026 (n={unfiltered['2025/2026']['n']}, "
              f"goals={unfiltered['2025/2026']['goals']:.2f}); assert_dev_only correctly raised: {exc}")
    shipped = json.loads((LEAGUE / "analysis" / "eda_numbers.json").read_text(encoding="utf-8"))
    try:
        assert_dev_only(shipped, seal, "shipped eda_numbers.json")
        print("shipped eda_numbers.json: no sealed reference found (unexpected)")
    except SealViolation as exc:
        print(f"shipped analysis/eda_numbers.json is contaminated, as AUDIT.md §3/§4b record: {exc}")

    # 2) Post-filter: zero sealed rows, checker passes.
    kept = filter_rows(rows, seal)
    assert count_sealed_rows(kept, seal) == 0
    filtered = level_table(kept)
    assert_dev_only(filtered, seal, "filtered level table")
    assert set(filtered) <= set(seal.dev_seasons), filtered.keys()
    assert "2025/2026" not in filtered and "2026/2027" not in filtered
    print(f"post-filter rows={len(kept)} sealed rows=0; table seasons={list(filtered)}")
    print("SELF-TEST PASS: pre-filter contamination demonstrated; post-filter output is dev-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
