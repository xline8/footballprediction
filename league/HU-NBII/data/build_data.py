"""Build the finished-score analysis dataset for Hungary NB II (FotMob 9117).

The warehouse is intentionally not part of the worktree.  Resolve it from the
repository first and from ~/workspace/footballprediction as the fallback,
matching the AU-Championship builder pattern.
"""

import csv
import json
import math
import os
import re
import unicodedata
from collections import Counter, defaultdict

LEAGUE_ID = "9117"
EXPECTED_INDEX_ROWS = 344
SEASONS = ("2025/2026", "2026/2027")


def ascii_fold(value):
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()


# FotMob alternates accented and unaccented spellings.  The canonical output
# deliberately uses NFKD ASCII folding so a team is one entity in both years.
TEAM_NAME_MAP = {
    "Aqvital FC Csakvar": "Aqvital FC Csakvar",
    "Aqvital FC Csákvár": "Aqvital FC Csakvar",
    "BVSC Zuglo": "BVSC Zuglo",
    "BVSC Zugló": "BVSC Zuglo",
    "Bekescsaba": "Bekescsaba",
    "Budafoki MTE": "Budafoki MTE",
    "Budapest Honved": "Budapest Honved",
    "Diosgyori VTK": "Diosgyori VTK",
    "FC Ajka": "FC Ajka",
    "Gyirmot": "Gyirmot",
    "Gyirmót": "Gyirmot",
    "Karcagi SE": "Karcagi SE",
    "Kazincbarcikai BSC": "Kazincbarcikai BSC",
    "Kecskemeti TE": "Kecskemeti TE",
    "Kecskeméti TE": "Kecskemeti TE",
    "Kozarmisleny": "Kozarmisleny",
    "Kozármisleny": "Kozarmisleny",
    "Mezokovesd SE": "Mezokovesd SE",
    "Mezőkövesd SE": "Mezokovesd SE",
    "Nagykanizsa": "Nagykanizsa",
    "Soroksár SC": "Soroksar SC",
    "Szeged-Csanad Grosics Akademia": "Szeged-Csanad Grosics Akademia",
    "Szeged-Csanád Grosics Akademia": "Szeged-Csanad Grosics Akademia",
    "Szentlorinc": "Szentlorinc",
    "Szentlőrinc": "Szentlorinc",
    "Tiszakecske": "Tiszakecske",
    "Tiszakécske": "Tiszakecske",
    "Vasas Budapest": "Vasas Budapest",
    "Videoton FC Fehervar": "Videoton FC Fehervar",
    "Videoton FC Fehérvár": "Videoton FC Fehervar",
}


def find_warehouse():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    candidates = [repo_root, os.path.expanduser("~/workspace/footballprediction")]
    for candidate in candidates:
        index = os.path.join(candidate, "data_enrichment", "fotmob_world_index.csv")
        if not os.path.isfile(index):
            continue
        with open(index, newline="") as handle:
            first = next(csv.DictReader(handle))
        if os.path.isfile(os.path.join(candidate, first["path"])):
            return candidate, index
    raise FileNotFoundError("warehouse (index + payloads) not found: " + ", ".join(candidates))


def parse_score(score_str):
    match = re.match(r"^\s*(\d+)\s*[-:]\s*(\d+)\s*$", score_str or "")
    if not match:
        raise ValueError(f"unparseable scoreStr: {score_str!r}")
    return int(match.group(1)), int(match.group(2))


def goals_and_half_marker(payload):
    events = payload["content"]["matchFacts"]["events"].get("events") or []
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    half_index = next((i for i, e in enumerate(events) if e.get("type") == "Half"), None)
    if half_index is None:
        return goals, None, None, None
    first_half = goals[:]
    # Event order is chronological in these payloads; the marker is the
    # reliable boundary even when stoppage-time values are represented oddly.
    first_half = [e for i, e in enumerate(events) if i < half_index and e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    h = sum(1 for e in first_half if e.get("isHome"))
    a = len(first_half) - h
    return goals, h, a, half_index


def main():
    warehouse, index_path = find_warehouse()
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    with open(index_path, newline="") as handle:
        index = [row for row in csv.DictReader(handle) if row["league_id"] == LEAGUE_ID]
    assert len(index) == EXPECTED_INDEX_ROWS, (len(index), EXPECTED_INDEX_ROWS)

    rows = []
    classes = Counter()
    per_round = defaultdict(Counter)
    score_event_mismatches = []
    half_marker_matches = 0
    half_marker_goals = 0
    finished_half_marker_matches = 0
    finished_half_marker_goals = 0
    payload_inventory = Counter()
    season_inventory = defaultdict(Counter)
    raw_names = set()

    for index_row in index:
        with open(os.path.join(warehouse, index_row["path"])) as handle:
            payload = json.load(handle)
        status = payload["header"]["status"]
        season = index_row["season"]
        score_str = status.get("scoreStr") or ""
        finished = bool(status.get("finished"))
        if not score_str:
            cls = "missing"
            reason = "no_scoreStr"
        elif not finished:
            cls = "partial"
            reason = "finished_false_partial_score"
        else:
            cls = "genuine"
            reason = ""
        classes[cls] += 1
        round_name = str(payload["general"].get("leagueRoundName") or "")
        per_round[season][round_name or "(blank)"] += 1
        season_inventory[season][cls] += 1

        facts = payload["content"]["matchFacts"]
        events = facts["events"].get("events") or []
        payload_inventory[(season, "events")] += int(bool(events))
        payload_inventory[(season, "referee")] += int(bool((facts.get("infoBox") or {}).get("Referee", {}).get("text")))
        payload_inventory[(season, "stats")]+= int(bool(payload["content"].get("stats")))
        payload_inventory[(season, "shotmap")]+= int(bool((payload["content"].get("shotmap") or {}).get("shots")))
        payload_inventory[(season, "lineup")]+= int(bool(payload["content"].get("lineup")))
        payload_inventory[(season, "period_splits")]+= int(bool((payload["content"].get("stats") or {}).get("Periods")))

        if score_str:
            score_h, score_a = parse_score(score_str)
            score_goals, score_gh, score_ga, score_half_index = goals_and_half_marker(payload)
            if score_half_index is not None:
                half_marker_matches += 1
                half_marker_goals += score_gh + score_ga
            event_h = sum(1 for e in score_goals if e.get("isHome"))
            event_a = len(score_goals) - event_h
            if (event_h, event_a) != (score_h, score_a):
                score_event_mismatches.append({"match_id": index_row["match_id"], "season": season, "score": f"{score_h}-{score_a}", "event_goals": f"{event_h}-{event_a}"})
        if cls != "genuine":
            continue
        hg, ag = parse_score(score_str)
        goals, gh, ga, half_index = goals_and_half_marker(payload)
        if half_index is not None:
            finished_half_marker_matches += 1
            finished_half_marker_goals += gh + ga
        raw_home = payload["general"]["homeTeam"]["name"]
        raw_away = payload["general"]["awayTeam"]["name"]
        raw_names.update((raw_home, raw_away))
        if hg + ag == 0:
            gh, ga = 0, 0
        elif half_index is None:
            gh, ga = "", ""
        rows.append({
            "match_id": index_row["match_id"], "season": season, "date": index_row["date"], "round": round_name,
            "home_team": TEAM_NAME_MAP.get(raw_home, ascii_fold(raw_home)), "away_team": TEAM_NAME_MAP.get(raw_away, ascii_fold(raw_away)),
            "home_goals": hg, "away_goals": ag, "total_goals": hg + ag,
            "home_win": int(hg > ag), "draw": int(hg == ag), "away_win": int(hg < ag),
            "over_1_5": int(hg + ag > 1.5), "over_2_5": int(hg + ag > 2.5), "over_3_5": int(hg + ag > 3.5),
            "btts": int(hg > 0 and ag > 0), "goals_1h_home": gh, "goals_1h_away": ga,
            "has_half_marker": int(half_index is not None), "excluded_reason": reason,
        })

    rows.sort(key=lambda row: (row["date"], row["match_id"]))
    assert classes == Counter({"genuine": 200, "missing": 103, "partial": 41}), classes
    assert len(rows) == 200
    assert sum(1 for r in rows if r["season"] == "2025/2026") == 96
    assert sum(1 for r in rows if r["season"] == "2026/2027") == 104
    assert len(score_event_mismatches) == 4
    assert len(raw_names) == 30
    out_path = os.path.join(here, "hu_nbii_matches.csv")
    with open(out_path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

    print(json.dumps({
        "warehouse": warehouse, "index_rows": len(index), "classes": classes,
        "written": len(rows), "per_season": {s: dict(season_inventory[s]) for s in SEASONS},
        "score_event_mismatches": score_event_mismatches,
        "half_marker_matches_scorestr": half_marker_matches,
        "half_marker_goals_scorestr": half_marker_goals,
        "half_marker_matches_finished": finished_half_marker_matches,
        "half_marker_goals_finished": finished_half_marker_goals,
        "rounds": {s: dict(sorted(per_round[s].items())) for s in SEASONS},
        "raw_name_count": len(raw_names), "output": out_path,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
