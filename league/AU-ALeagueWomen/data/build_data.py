"""Build the AUW analysis CSV from the FotMob world warehouse.

The warehouse is normally kept in the main checkout; the worktree copy is
preferred when present.  Finals are retained and labelled, but downstream
designs use only phase=regular.  No model fitting is performed here.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAIN = Path("/home/hatch/workspace/footballprediction")
INDEX = ROOT / "data_enrichment/fotmob_world_index.csv"
if not INDEX.exists():
    INDEX = MAIN / "data_enrichment/fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent

STAT_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards",
             "red_cards", "touches_opp_box", "big_chance", "BallPossesion"]

def number(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).split()[0].replace("%", ""))
    except (ValueError, IndexError): return None

def flat_periods(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or [None, None]
                out[(period, stat.get("key"))] = (
                    number(vals[0]), number(vals[1]) if len(vals) > 1 else None)
    return out

def event_goals(events, first_half):
    result = [0, 0]
    for e in events:
        if e.get("type") != "Goal" or e.get("time") is None:
            continue
        minute = number(e.get("time"))
        if (minute <= 45) != first_half:
            continue
        result[0 if e.get("isHome") else 1] += 1
    return result

def main():
    rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "9495"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    output = []
    for idx in rows:
        p = ROOT / idx["path"]
        if not p.exists(): p = MAIN / idx["path"]
        d = json.load(p.open())
        general, status = d.get("general", {}), d.get("header", {}).get("status", {})
        if not status.get("finished"): continue
        content = d.get("content") or {}
        fs = flat_periods(content)
        round_name = str(general.get("leagueRoundName") or "")
        phase = "regular" if round_name.isdigit() else "finals"
        score = [int(x.strip()) for x in (status.get("scoreStr") or "0-0").split("-")]
        facts = content.get("matchFacts") or {}
        events = (facts.get("events") or {}).get("events") or []
        rec = {
            "match_id": idx["match_id"], "season": idx["season"], "date": idx["date"],
            "round": round_name, "phase": phase,
            "home_team_id": general["homeTeam"]["id"], "home_team": general["homeTeam"]["name"],
            "away_team_id": general["awayTeam"]["id"], "away_team": general["awayTeam"]["name"],
            "home_goals": score[0], "away_goals": score[1],
            "referee": ((facts.get("infoBox") or {}).get("Referee") or {}).get("text"),
            "has_period_splits": int("FirstHalf" in {p for p, _ in fs}),
            "has_xg": int(bool(((content.get("stats") or {}).get("Periods") or {}).get("All") and
                               any(s.get("key") == "expected_goals" for g in (((content.get("stats") or {}).get("Periods") or {}).get("All") or {}).get("stats", []) for s in g.get("stats", [])))),
        }
        fh = event_goals(events, True) if rec["has_period_splits"] else [None, None]
        rec["home_goals_1h"], rec["away_goals_1h"] = fh
        rec["goals_1h_source"] = "events" if rec["has_period_splits"] else "none"
        for key in STAT_KEYS:
            for period, prefix in (("All", ""), ("FirstHalf", "1h_"), ("SecondHalf", "2h_")):
                h, a = fs.get((period, key), (None, None))
                rec[f"home_{prefix}{key}"], rec[f"away_{prefix}{key}"] = h, a
        shots = ((content.get("shotmap") or {}).get("shots") or [])
        rec["shotmap_n"] = len(shots)
        output.append(rec)
    assert len(output) >= 597, len(output)
    fields = list(output[0])
    with (OUT / "auw_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(output)
    print(f"wrote {len(output)} rows to {OUT/'auw_matches.csv'}")

if __name__ == "__main__": main()
