"""Reproducible content-based inventory for FotMob Malaysia Liga Super."""
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parents[3]
INDEX = BASE / "data_enrichment" / "fotmob_world_index.csv"
OUT = HERE / "inventory_summary.json"
SEASONS = ["2021", "2022", "2023", "2024/2025", "2025/2026", "2026/2027"]


def main():
    irs = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "8985"]
    seasons = defaultdict(list); names = defaultdict(set); teams = defaultdict(set)
    league_names = Counter(); parent = Counter(); awarded = []; rows = []
    for ir in irs:
        d = json.loads((BASE / ir["path"]).read_text()); g, h, c = d["general"], d["header"], d["content"]
        mf = c.get("matchFacts") or {}; ev = ((mf.get("events") or {}).get("events") or [])
        cards = [e for e in ev if e.get("type") == "Card"]; shot = c.get("shotmap") or {}
        ref = (mf.get("infoBox") or {}).get("Referee") or {}
        row = {
            "match_id": ir["match_id"], "season": ir["season"], "date": ir["date"], "score": True,
            "stats": c.get("stats") is not None, "shotmap": bool(shot.get("shots")),
            "lineup": c.get("lineup") is not None, "player_stats": c.get("playerStats") is not None,
            "referee": bool(ref.get("text")), "events": bool(ev), "half": any(e.get("type") == "Half" for e in ev),
            "cards": bool(cards), "yellow": sum(e.get("card") == "Yellow" for e in cards),
            "red": sum(e.get("card") == "Red" for e in cards), "yellowred": sum(e.get("card") == "YellowRed" for e in cards),
            "goals": sum(e.get("type") == "Goal" for e in ev), "teams": [t["id"] for t in h["teams"]],
            "team_names": [t["name"] for t in h["teams"]], "league_name": g["leagueName"],
            "parent": g["parentLeagueId"], "round": g.get("leagueRoundName") or "",
            "awarded": bool(h["status"].get("awarded")),
        }
        rows.append(row); seasons[ir["season"]].append(row); league_names[g["leagueName"]] += 1; parent[str(g["parentLeagueId"])] += 1
        for tid, name in zip(row["teams"], row["team_names"]): teams[ir["season"]].add(tid); names[str(tid)].add(name)
        if row["awarded"]: awarded.append(ir["match_id"])
    canonical = {}
    for r in rows:
        for tid, name in zip(r["teams"], r["team_names"]):
            if str(tid) not in canonical or (r["date"], r["match_id"]) > canonical[str(tid)][0]:
                canonical[str(tid)] = ((r["date"], r["match_id"]), name)
    entrants = {}; prior = set()
    for s in SEASONS:
        entrants[s] = sorted(teams[s] - prior, key=int); prior |= teams[s]
    out = {
        "league": "MY-LigaSuper", "fotmob_id": 8985, "index_rows": len(irs), "payloads_present": len(rows),
        "country_distribution": dict(Counter(r["country"] for r in irs)), "parentLeagueId_distribution": dict(parent),
        "leagueName_distribution": dict(league_names), "phase_distribution": {"regular": len(rows)},
        "league_scope_note": "single table, double round-robin, regular phase; no split or playoff",
        "team_count_total": len(set().union(*(teams[s] for s in SEASONS))),
        "team_counts_by_season": {s: len(teams[s]) for s in SEASONS},
        "team_ids_by_season": {s: sorted(teams[s], key=int) for s in SEASONS},
        "team_name_variants": {k: sorted(v) for k, v in names.items() if len(v) > 1},
        "canonical_team_names": {k: v[1] for k, v in canonical.items()},
        "entrants_by_team_id": {s: entrants[s] for s in SEASONS}, "awarded_match_ids": sorted(awarded, key=int),
        "date_ranges": {s: [min(r["date"] for r in seasons[s]), max(r["date"] for r in seasons[s])] for s in SEASONS},
        "rounds_by_season": {s: sorted({r["round"] for r in seasons[s]}, key=lambda x: int(x) if str(x).isdigit() else str(x)) for s in SEASONS},
        "seasons": {},
    }
    for s in SEASONS:
        rs = seasons[s]
        out["seasons"][s] = {
            "n": len(rs), "teams": len(teams[s]), "round_count": len({r["round"] for r in rs}),
            "date_range": out["date_ranges"][s], "model_rows": sum(not r["awarded"] for r in rs),
            "awarded": sum(r["awarded"] for r in rs),
            "coverage": {k: sum(r[k] for r in rs) for k in ["score", "stats", "shotmap", "lineup", "player_stats", "referee", "events", "half", "cards"]},
            "eventless": sum(not r["events"] for r in rs), "card_event_rows": sum(r["cards"] for r in rs),
            "card_events": sum(r["red"] + r["yellowred"] + r["yellow"] for r in rs),
            "red_events": sum(r["red"] for r in rs), "yellowred_events": sum(r["yellowred"] for r in rs),
            "yellow_events": sum(r["yellow"] for r in rs), "goal_events": sum(r["goals"] for r in rs),
            "lineup_nonnull": sum(r["lineup"] for r in rs),
        }
    out["events_total"] = {"goals": sum(r["goals"] for r in rows), "half": sum(r["half"] for r in rows),
                            "cards": sum(r["red"] + r["yellowred"] + r["yellow"] for r in rows),
                            "yellow": sum(r["yellow"] for r in rows), "red": sum(r["red"] for r in rows),
                            "yellowred": sum(r["yellowred"] for r in rows)}
    out["content_absence_zero_counts_by_season"] = {s: {k: len(seasons[s]) - sum(r[k] for r in seasons[s]) for k in ["stats", "shotmap", "lineup", "player_stats", "referee", "yellow"]} for s in SEASONS}
    allidx = list(csv.DictReader(INDEX.open()))
    out["malaysia_league_ids_in_index"] = sorted({r["league_id"] for r in allidx if r["country"] == "Malaysia"}, key=int)
    out["has_playoff_distribution"] = dict(Counter(str(json.loads((BASE / r["path"]).read_text())["content"].get("hasPlayoff")) for r in irs))
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__": main()
