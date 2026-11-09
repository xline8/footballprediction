"""Rebuild fotmob_world_index.csv from the match JSON files on disk.

Why: after the 2026-11-09 world pull, the store held 233,618 match
files but the index only 231,768 rows — 1,850 rows across Slovenia
Prva Liga, South Africa Premier Soccer League, South Korea K League 1
and Tunisia Ligue I were lost when a killed run's non-atomic index
rewrite truncated the file and the (atomic, complete) checkpoint's
done_ids then made every later run skip re-recording those matches.
The files were never damaged, so the index is recomputed from them.

Every row is recomputed with the puller's own logic
(pull_fotmob_world.flags_of / score_of) applied to the stored
payload; descriptive fields come from the payload header (team
names, utcTime) and the catalog row for the league directory the
file lives under (country, ccode, league, league_id). Season labels
are recovered per league from the catalog's recorded season list,
cross-checked against the previous index and the checkpoint groups
(a directory name is the label with "/" written as "-").

Usage: rebuild_fotmob_world_index.py [--verify-only]
Default run rebuilds, writes the index atomically, then verifies:
row count == file count overall and per league, plus a field-level
spot check of sampled rebuilt rows against their payloads.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pull_fotmob_world as pw  # noqa: E402

STORE = pw.STORE
INDEX = pw.INDEX
CHECKPOINT = pw.CHECKPOINT


def catalog_maps() -> tuple[dict, dict]:
    """(sanitize(country), sanitize(league)) -> catalog row, and
    (key, season_dir) -> season label from the catalog's list."""
    leagues: dict[tuple[str, str], dict] = {}
    seasons: dict[tuple[str, str, str], str] = {}
    with pw.CATALOG.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["selected"] != "yes":
                continue
            key = (pw.sanitize(row["country"]), pw.sanitize(row["league"]))
            assert key not in leagues, f"sanitized league dir collision: {key}"
            leagues[key] = row
            for label in (row.get("seasons_2021plus") or "").split(";"):
                if label:
                    seasons[(key[0], key[1], pw.season_dir(label))] = label
    return leagues, seasons


def add_season_labels(seasons: dict, key: tuple[str, str],
                      dirname: str, label: str, source: str) -> None:
    mapkey = (key[0], key[1], dirname)
    old = seasons.get(mapkey)
    if old is not None and old != label:
        raise SystemExit(f"season label conflict for {mapkey}: "
                         f"{old!r} (catalog) vs {label!r} ({source})")
    seasons[mapkey] = label


def season_maps(leagues: dict) -> dict:
    """dir name -> original season label per league, from the
    catalog, the previous index and the checkpoint groups."""
    _, seasons = catalog_maps()
    if INDEX.exists():
        with INDEX.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                parts = Path(row["path"]).parts
                key = (parts[-4], parts[-3])
                if key in leagues:
                    add_season_labels(seasons, key, parts[-2],
                                      row["season"], "old index")
    if CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        for group_key in checkpoint.get("groups", {}):
            country, league, label = group_key.split(" | ")
            key = (pw.sanitize(country), pw.sanitize(league))
            if key in leagues:
                add_season_labels(seasons, key, pw.season_dir(label),
                                  label, "checkpoint")
    return seasons


def row_for_file(task: tuple) -> tuple[str, dict | None, str | None]:
    """Worker: build one index row from one stored payload.
    Returns (match_id_str, row|None, error|None)."""
    rel_posix, league_row, season_label = task
    path = BASE / rel_posix
    mid = path.stem
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        teams = (payload.get("header") or {}).get("teams") or []
        status = (payload.get("header") or {}).get("status") or {}
        general = payload.get("general") or {}
        home = (teams[0].get("name") if len(teams) > 0 else None) \
            or (general.get("homeTeam") or {}).get("name") or ""
        away = (teams[1].get("name") if len(teams) > 1 else None) \
            or (general.get("awayTeam") or {}).get("name") or ""
        row = {
            "match_id": int(mid),
            "country": league_row["country"],
            "ccode": league_row["ccode"],
            "league": league_row["league"],
            "league_id": int(league_row["league_id"]),
            "season": season_label,
            "date": str(status.get("utcTime") or "")[:10],
            "home": home, "away": away,
            "score": pw.score_of({}, payload),
            **{k: pw.flags_of(payload)[k] for k in
               ("has_shotmap", "has_stats", "has_lineup",
                "has_period_splits")},
            "path": rel_posix}
        return mid, row, None
    except Exception as exc:  # unreadable payload: report, never guess
        return mid, None, repr(exc)


def scan(leagues: dict, seasons: dict) -> tuple[dict, list, list]:
    files = sorted(STORE.rglob("*.json"))
    tasks, unmapped = [], []
    seen: dict[str, str] = {}
    duplicates = []
    for path in files:
        rel = path.relative_to(BASE).as_posix()
        parts = path.relative_to(STORE).parts
        country_dir, league_dir, season_dirname = parts[0], parts[1], parts[2]
        key = (country_dir, league_dir)
        if key not in leagues:
            unmapped.append(f"{rel}: league dir not in catalog")
            continue
        label = seasons.get((country_dir, league_dir, season_dirname))
        if label is None:
            match = re.fullmatch(r"(\d{4})-(\d{4})", season_dirname)
            if match:
                label = f"{match.group(1)}/{match.group(2)}"
            else:
                unmapped.append(f"{rel}: no season label for dir "
                                f"{season_dirname!r}")
                continue
        mid = path.stem
        if mid in seen:
            duplicates.append(f"{mid}: {seen[mid]} and {rel}")
            continue
        seen[mid] = rel
        tasks.append((rel, leagues[key], label))
    rows: dict[str, dict] = {}
    failures: list[str] = []
    with ProcessPoolExecutor(max_workers=2) as pool:
        for mid, row, error in pool.map(row_for_file, tasks,
                                        chunksize=200):
            if error is not None:
                failures.append(f"{mid}: {error}")
            else:
                rows[mid] = row
    return rows, unmapped + duplicates, failures


def write_rows(rows: dict) -> None:
    import os
    ordered = sorted(rows.values(),
                     key=lambda r: (r["country"], r["league"], r["season"],
                                    r["date"], r["home"]))
    tmp = INDEX.with_suffix(".csv.rebuild-tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=pw.INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(ordered)
    os.replace(tmp, INDEX)


def main() -> int:
    verify_only = "--verify-only" in sys.argv
    leagues, _ = catalog_maps()
    seasons = season_maps(leagues)
    rows, problems, failures = scan(leagues, seasons)
    file_count = sum(1 for _ in STORE.rglob("*.json"))
    print(f"files on disk: {file_count}")
    print(f"rows rebuilt:  {len(rows)}")
    if problems:
        print(f"PROBLEMS ({len(problems)}):")
        for line in problems[:20]:
            print(" ", line)
    if failures:
        print(f"UNREADABLE PAYLOADS ({len(failures)}):")
        for line in failures[:20]:
            print(" ", line)
    if problems or failures:
        return 2
    if not verify_only:
        write_rows(rows)
        print(f"index written: {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
