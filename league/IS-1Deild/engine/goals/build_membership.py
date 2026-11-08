"""Build Iceland tier membership from the shared FotMob index and payloads.

This script only extracts team IDs.  It does not read scores for fitting or
scoring.  The 2. Deild store contains a small number of malformed payloads
without general.homeTeam; those rows are deliberately skipped.
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN_REPO = ROOT.parents[2] / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = ROOT / "data" / "tier_membership.json"
LEAGUES = {"216": "1. Deild", "215": "Besta deildin", "10226": "2. Deild"}


def payload_path(path):
    p = Path(path)
    return p if p.is_absolute() else MAIN_REPO / p


def build(index_path=INDEX):
    teams = {lid: {} for lid in LEAGUES}
    with Path(index_path).open(newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["league_id"] in LEAGUES and r["season"] in {str(x) for x in range(2021, 2027)}]
    for row in rows:
        with payload_path(row["path"]).open(encoding="utf-8") as fh:
            data = json.load(fh)
        general = data.get("general") or {}
        home = general.get("homeTeam") or {}
        away = general.get("awayTeam") or {}
        # Some 2. Deild payloads are index placeholders with no team IDs.
        if not home.get("id") or not away.get("id"):
            continue
        season = row["season"]
        teams[row["league_id"]].setdefault(season, set()).update((int(home["id"]), int(away["id"])))

    membership = {
        "league_ids": {name: lid for lid, name in LEAGUES.items()},
        "seasons": {name: {s: sorted(ids) for s, ids in sorted(by_season.items())}
                    for lid, name in LEAGUES.items() for by_season in [teams[lid]]},
        "entrants": [],
        "source": "data_enrichment/fotmob_world_index.csv and payload team IDs",
    }
    one = membership["seasons"]["1. Deild"]
    besta = membership["seasons"]["Besta deildin"]
    deild2 = membership["seasons"]["2. Deild"]
    for season in map(str, range(2022, 2027)):
        prev = str(int(season) - 1)
        for team_id in sorted(set(one.get(season, [])) - set(one.get(prev, []))):
            origins = []
            if team_id in set(besta.get(prev, [])):
                origins.append("Besta deildin")
            if team_id in set(deild2.get(prev, [])):
                origins.append("2. Deild")
            if len(origins) != 1:
                raise ValueError(f"entrant {season}/{team_id} has origins {origins}")
            membership["entrants"].append({"season": season, "team_id": team_id, "origin": origins[0]})

    expected_path = ROOT / "analysis" / "eda_summary.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))["f4"]["entrants"]
    got = [{k: row[k] for k in ("season", "team_id", "origin")} for row in membership["entrants"]]
    want = [{k: row[k] for k in ("season", "team_id", "origin")} for row in expected]
    if got != want:
        raise ValueError(f"entrant cross-check failed; got={got!r} expected={want!r}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(membership, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return membership


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=Path, default=INDEX)
    args = parser.parse_args()
    m = build(args.index)
    print(json.dumps({"teams": {k: {s: len(v) for s, v in x.items()} for k, x in m["seasons"].items()},
                      "entrants": len(m["entrants"])}, indent=2))


if __name__ == "__main__":
    main()
