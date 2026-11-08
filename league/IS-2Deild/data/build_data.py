"""Build the Iceland 2. Deild Phase A score/event tables and mover input."""
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
WAREHOUSE = ROOT / "data_enrichment" / "fotmob_world"
OUT = Path(__file__).resolve().parent
SEASONS = ["2021", "2022", "2023", "2024", "2025", "2026"]


def payload_path(row):
    return ROOT / row["path"]


def score_pair(score):
    left, right = score.replace("–", "-").split("-")[:2]
    return int(left.strip()), int(right.strip())


def payload_date(data):
    status = (data.get("header") or {}).get("status") or {}
    utc = status.get("utcTime")
    if not utc:
        utc = (((data.get("content") or {}).get("matchFacts") or {}).get("infoBox") or {}).get("Match Date", {}).get("utcTime")
    return datetime.fromtimestamp(utc).date().isoformat() if isinstance(utc, (int, float)) else str(utc)[:10]


def events(data):
    return (((data.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def match_rows(index_rows):
    rows = []
    for ir in sorted(index_rows, key=lambda x: (x["season"], x["date"], x["match_id"])):
        data = json.loads(payload_path(ir).read_text())
        if data.get("error"):
            continue
        header = data.get("header") or {}
        status = header.get("status") or {}
        if not status.get("finished"):
            continue
        general = data.get("general") or {}
        home = general.get("homeTeam") or {}
        away = general.get("awayTeam") or {}
        ev = events(data)
        goals = [e for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
        hg, ag = score_pair(status.get("scoreStr") or "0-0")
        assert len(goals) == hg + ag, (ir["match_id"], len(goals), hg, ag)
        hth = sum(e.get("time") is not None and e["time"] <= 45 and e.get("isHome") for e in goals)
        hta = sum(e.get("time") is not None and e["time"] <= 45 and not e.get("isHome") for e in goals)
        cards = [e for e in ev if e.get("type") == "Card"]
        rows.append({
            "match_id": ir["match_id"], "season": ir["season"], "date": payload_date(data),
            "round": str(general.get("matchRound") or ""),
            "home_team_id": home["id"], "home_team": home.get("name", ""),
            "away_team_id": away["id"], "away_team": away.get("name", ""),
            "home_goals": hg, "away_goals": ag, "ht_home_goals": hth, "ht_away_goals": hta,
            "goals_1h_total": hth + hta,
            "ev_card_home": sum(bool(e.get("isHome")) for e in cards),
            "ev_card_away": sum(not bool(e.get("isHome")) for e in cards),
            "has_stats": 0, "has_shotmap": 0, "referee": "",
        })
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def build_movers(all_index):
    by_league = {"10226": defaultdict(set), "216": defaultdict(set)}
    names = {"10226": defaultdict(dict), "216": defaultdict(dict)}
    stats = {"10226": defaultdict(lambda: defaultdict(lambda: [0, 0, 0])), "216": defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))}
    for ir in all_index:
        if ir["league_id"] not in by_league or ir["season"] not in SEASONS:
            continue
        d = json.loads(payload_path(ir).read_text())
        if d.get("error") or not ((d.get("header") or {}).get("status") or {}).get("finished"):
            continue
        g = d.get("general") or {}; h = g.get("homeTeam") or {}; a = g.get("awayTeam") or {}
        hg, ag = score_pair(((d.get("header") or {}).get("status") or {}).get("scoreStr") or "0-0")
        for team, name, gf, ga in ((h["id"], h.get("name", ""), hg, ag), (a["id"], a.get("name", ""), ag, hg)):
            by_league[ir["league_id"]][ir["season"]].add(team); names[ir["league_id"]][ir["season"]][str(team)] = name
            x = stats[ir["league_id"]][ir["season"]][team]; x[0] += 1; x[1] += gf; x[2] += ga
    seasons = {}
    transitions = []
    for s in SEASONS:
        cur = by_league["10226"][s]; one = by_league["216"][s]
        seasons[s] = {"is2deild_team_ids": sorted(cur), "is1deild_team_ids": sorted(one)}
        if s == SEASONS[0]:
            continue
        prev = str(int(s) - 1); entrants = cur - by_league["10226"][prev]
        for team in sorted(entrants):
            source = "relegated-from-1Deild" if team in by_league["216"][prev] else "from-below"
            rec = {"season": s, "team_id": team, "team": names["10226"][s].get(str(team), ""), "source": source}
            n, gf, ga = stats["10226"][s][team]
            rec.update(arrival_matches=n, arrival_gf=gf / n, arrival_ga=ga / n)
            if source == "relegated-from-1Deild":
                pn, pgf, pga = stats["216"][prev][team]
                rec.update(previous_1deild_matches=pn, previous_1deild_gf=pgf / pn, previous_1deild_ga=pga / pn)
            transitions.append(rec)
    (OUT / "mover_teams.json").write_text(json.dumps({"seasons": seasons, "transitions": transitions}, indent=2) + "\n")


def main():
    index = list(csv.DictReader((ROOT / "data_enrichment" / "fotmob_world_index.csv").open(encoding="utf-8")))
    rows = match_rows([r for r in index if r["league_id"] == "10226" and r["season"] in SEASONS])
    assert len(rows) == 776 and len({r["match_id"] for r in rows}) == 776
    assert Counter(r["season"] for r in rows) == Counter({"2021": 116, "2022": 132, "2023": 132, "2024": 132, "2025": 132, "2026": 132})
    write_csv(OUT / "is2_matches.csv", rows)
    teams = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            teams.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]})
    write_csv(OUT / "is2_team_matches.csv", teams)
    build_movers(index)
    print(json.dumps({"matches": len(rows), "team_matches": len(teams), "season_counts": dict(Counter(r["season"] for r in rows))}, sort_keys=True))


if __name__ == "__main__": main()
