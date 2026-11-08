"""Build the FI-Ykkosliiga analysis CSV from the FotMob world warehouse.

The source is league_id 251.  All finished rows are retained, including
regular, Championship, Relegation and Promotion Playoff phases.  HT goals
come from a Half event at time 45 when available, then from Goal events as a
fallback.  Stats and shotmap fields are retained as explicit empty/zero
signals so the inventory is reproducible.
"""
import csv, json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
STAT_KEYS = ["BallPossesion", "expected_goals", "expected_goals_open_play",
             "expected_goals_set_play", "expected_goals_non_penalty",
             "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "shots_inside_box", "shots_outside_box", "big_chance",
             "touches_opp_box", "corners", "yellow_cards", "red_cards", "fouls",
             "Offsides", "keeper_saves"]

def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.split()[0].replace("%", ""))
        except (ValueError, IndexError):
            return None
    return None

def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for item in group.get("stats", []) or []:
                vals = item.get("stats") or [None, None]
                out[(period, item.get("key"))] = (num(vals[0]), num(vals[1]))
    return out

def events(content):
    return ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []

def phase(name):
    n = (name or "").lower()
    if "championship" in n: return "championship"
    if "relegation" in n: return "relegation"
    if "promotion playoff" in n or "promotion play-off" in n: return "promotion_playoff"
    if "ykkonen" in n or "ykkönen" in n or "ykkosliiga" in n or "ykkösliiga" in n:
        return "regular"
    return "unknown"

def main():
    source_rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == "251"]
    source_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for ir in source_rows:
        d = json.load(open(MAIN_REPO / ir["path"]))
        general, status = d.get("general") or {}, (d.get("header") or {}).get("status") or {}
        if not status.get("finished"):
            continue
        content = d.get("content") or {}; evs = events(content); fs = flat_stats(content)
        home, away = general["homeTeam"], general["awayTeam"]
        score = (status.get("scoreStr") or "0 - 0").split("-")
        row = {"match_id": ir["match_id"], "league": "FI-Ykkosliiga", "season": ir["season"],
               "date": ir["date"], "round": str(general.get("matchRound")),
               "phase": phase(general.get("leagueName")),
               "home_team_id": home["id"], "home_team": home["name"],
               "away_team_id": away["id"], "away_team": away["name"],
               "home_goals": int(score[0]), "away_goals": int(score[1]),
               "index_has_stats": int(ir.get("has_stats") == "True"),
               "has_events": int(bool(evs)), "referee": (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""}
        half = next((e for e in evs if e.get("type") == "Half" and e.get("time") == 45
                     and e.get("homeScore") is not None and e.get("awayScore") is not None), None)
        if half is not None:
            row.update(ht_home_goals=half["homeScore"], ht_away_goals=half["awayScore"], ht_source="half_event")
        else:
            goals = [e for e in evs if e.get("type") == "Goal" and e.get("time") is not None and e["time"] <= 45]
            if evs:
                row.update(ht_home_goals=sum(1 for e in goals if e.get("isHome")),
                           ht_away_goals=sum(1 for e in goals if not e.get("isHome")), ht_source="events")
            else:
                row.update(ht_home_goals=None, ht_away_goals=None, ht_source="none")
        cards = [e for e in evs if e.get("type") == "Card"]
        is_yellow = lambda e: e.get("card") in ("Yellow", "YellowRed")
        is_red = lambda e: e.get("card") in ("Red", "YellowRed")
        for side in ("home", "away"):
            home_side = side == "home"
            row[f"ev_yellow_{side}"] = sum(1 for e in cards if is_yellow(e) and bool(e.get("isHome")) == home_side)
            row[f"ev_red_{side}"] = sum(1 for e in cards if is_red(e) and bool(e.get("isHome")) == home_side)
        row["ev_card_events"] = len(cards)
        row["ev_yellow_1h"] = sum(1 for e in cards if is_yellow(e) and e.get("time") is not None and e["time"] <= 45)
        row["goals_1h_total"] = (row["ht_home_goals"] or 0) + (row["ht_away_goals"] or 0)
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
                h, a = fs.get((period, key), (None, None))
                row[f"{prefix}{key}_home"] = h; row[f"{prefix}{key}_away"] = a
        row["yellow_home"] = row["ev_yellow_home"]; row["yellow_away"] = row["ev_yellow_away"]
        row["has_stats_all"] = int(any(k[0] == "All" and v[0] is not None for k, v in fs.items()))
        row["has_stats_half"] = int(any(k[0] == "FirstHalf" and v[0] is not None for k, v in fs.items()))
        shots = (content.get("shotmap") or {}).get("shots") or []
        row["shotmap_shots"] = len(shots); row["has_shotmap"] = int(bool(shots)); row["has_xg"] = int(any("xg" in k.lower() for k in fs))
        for side in ("home", "away"):
            side_shots = [s for s in shots if s.get("teamId") == row[f"{side}_team_id"]]
            row[f"sm_shots_{side}"] = len(side_shots)
            row[f"sm_sot_{side}"] = sum(1 for s in side_shots if s.get("isOnTarget") and not s.get("isBlocked"))
            row[f"sm_xg_{side}"] = sum(float(s.get("expectedGoals") or 0) for s in side_shots)
        out.append(row)
    assert len(out) == 895, len(out)
    assert len({r["match_id"] for r in out}) == len(out)
    fields = list(out[0]);
    with open(OUT / "yk_matches.csv", "w", newline="") as f: csv.DictWriter(f, fieldnames=fields).writeheader(); csv.DictWriter(f, fieldnames=fields).writerows(out)
    team = []
    for r in out:
        for side, other in (("home", "away"), ("away", "home")):
            t = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]}
            for k in ("total_shots", "ShotsOnTarget", "corners", "yellow", "BallPossesion"):
                t[f"{k}_for"] = r.get(f"{k}_{side}"); t[f"{k}_against"] = r.get(f"{k}_{other}")
            team.append(t)
    with open(OUT / "yk_team_matches.csv", "w", newline="") as f: csv.DictWriter(f, fieldnames=list(team[0])).writeheader(); csv.DictWriter(f, fieldnames=list(team[0])).writerows(team)
    assert all(r["has_stats_all"] == 0 for r in out)
    assert all(r["shotmap_shots"] == 0 for r in out)
    print(f"matches {len(out)} team_rows {len(team)} stats_all={sum(r['has_stats_all'] for r in out)} shotmap={sum(r['has_shotmap'] for r in out)}")

if __name__ == "__main__": main()
