"""Build the Lithuania Toplyga scores/events analysis tables.

This is deliberately a Phase-A builder: official FT scores come from
``scoreStr``; first-half goals come from credited Goal events.  The two
awarded matches are retained and flagged, but their contradictory event
feed is not used to fabricate an HT split.
"""
import argparse, csv, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEFAULT_WAREHOUSE = REPO
LEAGUE_ID = "228"
EXPECTED = {"2021": 180, "2022": 180, "2023": 180, "2024": 180, "2025": 180, "2026": 144}


def event_minute(e):
    try:
        return float(e.get("time"))
    except (TypeError, ValueError):
        return None


def score(s):
    a, b = (s or "").split("-")[:2]
    return int(a.strip()), int(b.strip())


def load_row(index_row, root):
    path = root / index_row["path"].rstrip("\r")
    d = json.loads(path.read_text())
    g, h, c = d.get("general") or {}, d.get("header") or {}, d.get("content") or {}
    status = h.get("status") or {}
    home, away = g.get("homeTeam") or {}, g.get("awayTeam") or {}
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    events = (((c.get("matchFacts") or {}).get("events") or {}).get("events") or [])
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    evh = sum(e.get("isHome") is True for e in goals)
    eva = sum(e.get("isHome") is False for e in goals)
    awarded = bool(status.get("awarded"))
    ht = [e for e in goals if event_minute(e) is not None and event_minute(e) <= 45]
    ht_known = (not awarded) and bool(events)
    row = {
        "match_id": index_row["match_id"], "season": index_row["season"],
        "date": (g.get("matchTimeUTCDate") or status.get("utcTime") or index_row.get("date", ""))[:10],
        "kickoff_utc": g.get("matchTimeUTCDate") or status.get("utcTime"),
        "round": str(g.get("matchRound") or ""),
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "ht_home_goals": "" if not ht_known else sum(e.get("isHome") is True for e in ht),
        "ht_away_goals": "" if not ht_known else sum(e.get("isHome") is False for e in ht),
        "ht_source": "awarded_unknown" if awarded else ("events" if events else "none"),
        "awarded": int(awarded), "has_events": int(bool(events)),
        "finished": int(bool(status.get("finished"))),
        "ev_goals_home": evh, "ev_goals_away": eva,
        "score_events_mismatch": int((evh, eva) != (hg, ag)),
        "coverage_level": g.get("coverageLevel"),
        "has_stats_content": int(c.get("stats") is not None),
        "has_shotmap": int(bool((c.get("shotmap") or {}).get("shots"))),
        "has_lineup": int(c.get("lineup") is not None),
        "referee": (((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "",
        "has_playoff_value": json.dumps(c.get("hasPlayoff"), ensure_ascii=False),
    }
    cards = [e for e in events if e.get("type") == "Card"]
    for kind in ("Yellow", "YellowRed", "Red"):
        row[f"card_{kind.lower()}_count"] = sum(e.get("card") == kind for e in cards)
    return row


def team_rows(m):
    out = []
    for side, other, venue in (("home", "away", "H"), ("away", "home", "A")):
        gf, ga = int(m[f"{side}_goals"]), int(m[f"{other}_goals"])
        out.append({
            "match_id": m["match_id"], "season": m["season"], "date": m["date"],
            "round": m["round"], "team_id": m[f"{side}_team_id"], "team": m[f"{side}_team"],
            "opponent_id": m[f"{other}_team_id"], "opponent": m[f"{other}_team"],
            "venue": venue, "goals_for": gf, "goals_against": ga,
            "ht_goals_for": m[f"ht_{side}_goals"], "ht_goals_against": m[f"ht_{other}_goals"],
            "result": "W" if gf > ga else ("D" if gf == ga else "L"),
            "points": 3 if gf > ga else (1 if gf == ga else 0), "awarded": m["awarded"],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path, default=DEFAULT_WAREHOUSE)
    args = ap.parse_args()
    idx = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [load_row(r, args.warehouse_root) for r in csv.DictReader(idx.open()) if r["league_id"] == LEAGUE_ID]
    assert len(rows) == sum(EXPECTED.values()), len(rows)
    assert all(r["finished"] for r in rows)
    # Most payloads carry the expected Half/Card event list.  A measured
    # 90-match exception has an empty list; preserve that missing HT source.
    rows.sort(key=lambda r: (r["date"], str(r["match_id"])))
    counts = Counter(r["season"] for r in rows)
    assert dict(counts) == EXPECTED, counts
    assert all(r["coverage_level"] == "lower" for r in rows)
    assert sum(r["score_events_mismatch"] for r in rows) == 2
    assert sum(r["awarded"] for r in rows) == 2
    out = HERE
    with (out / "lt_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    teams = [x for r in rows for x in team_rows(r)]
    with (out / "lt_team_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(teams[0])); w.writeheader(); w.writerows(teams)
    print("season_counts=" + json.dumps(dict(sorted(counts.items()))))
    print(f"matches={len(rows)} team_rows={len(teams)} awarded={sum(r['awarded'] for r in rows)} mismatches={sum(r['score_events_mismatch'] for r in rows)}")


if __name__ == "__main__":
    main()
