"""CLI wrapper around seal.py — how an EDA generator applies the P2 filter.

Usage (project python, from ~/workspace/footballprediction):

  # Filter a matches CSV down to dev-era rows (writes a new CSV):
  .venv/bin/python -m league.design_seal.eda_filter filter-csv \
      league/AE-ProLeague league/AE-ProLeague/data/ae_matches.csv /tmp/dev_only.csv

  # Check a JSON artefact for sealed-season references (exit 1 if any):
  .venv/bin/python -m league.design_seal.eda_filter check-json \
      league/AE-ProLeague league/AE-ProLeague/analysis/eda_numbers.json

In code, an EDA generator does instead:

    from league.design_seal.seal import load_seal, filter_rows, assert_dev_only
    seal = load_seal(LEAGUE_DIR)
    rows = filter_rows(all_rows, seal)          # sealed rows can no longer enter
    ...
    assert_dev_only(eda_numbers, seal, "eda_numbers.json")   # before writing
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from seal import assert_dev_only, count_sealed_rows, filter_rows, load_seal
else:
    from .seal import assert_dev_only, count_sealed_rows, filter_rows, load_seal


def cmd_filter_csv(league_dir: str, src: str, dst: str) -> int:
    seal = load_seal(league_dir)
    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames
    sealed_before = count_sealed_rows(rows, seal)
    kept = filter_rows(rows, seal)
    sealed_after = count_sealed_rows(kept, seal)
    with open(dst, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept)
    print(f"league={seal.league} sealed={seal.sealed_seasons} dev={seal.dev_seasons}")
    print(f"rows in={len(rows)} sealed in input={sealed_before} kept={len(kept)} sealed in output={sealed_after}")
    print(f"wrote {dst}")
    return 0 if sealed_after == 0 else 1


def cmd_check_json(league_dir: str, src: str) -> int:
    seal = load_seal(league_dir)
    obj = json.loads(Path(src).read_text(encoding="utf-8"))
    try:
        assert_dev_only(obj, seal, src)
    except AssertionError as exc:
        print(f"CONTAMINATED: {exc}")
        return 1
    print(f"CLEAN: {src} contains no sealed-season ({seal.sealed_seasons}) references")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) == 4 and argv[0] == "filter-csv":
        return cmd_filter_csv(argv[1], argv[2], argv[3])
    if len(argv) == 3 and argv[0] == "check-json":
        return cmd_check_json(argv[1], argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
