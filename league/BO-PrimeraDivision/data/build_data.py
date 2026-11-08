"""Build Bolivia Primera División analysis CSVs from the local FotMob warehouse."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "144"
STAT_KEYS = ["total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "touches_opp_box", "big_chance", "BallPossesion", "accurate_passes",
             "yellow_cards", "red_cards", "fouls", "corners", "passes", "keeper_saves"]

def number(value):
    if value is None: return None
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        try: return float(value.split()[0].replace("%", ""))
        except (ValueError, IndexError): return None
    return None

def flat_stats(content):
    out = {}
    periods = ((content.get("stats") or {}).get("Periods") or {})
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or [None, None]
                out[(period, stat.get("key"))] = (number(vals[0]), number(vals[1]))
    return out

def events_list(content):
    return (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])

def event_count(events, cards, home=None, period=None):
    total = 0
    for e in events:
        if e.get("type") != "Card" or e.get("card") not in cards: continue
        if home is not None and bool(e.get("isHome")) != home: continue
        t = e.get("time")
        if period == "1h" and not (isinstance(t, (int, float)) and t <= 45): continue
        if period == "2h" and not (isinstance(t, (int, float)) and t > 45): continue
        total += 1
    return total

def main():
    with INDEX.open() as fh: index = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    index.sort(key=lambda r: (r["date"], r["match_id"]))
    rows, variants = [], defaultdict(Counter)
    for idx in index:
        path = ROOT / idx["path"]
        d = json.loads(path.read_text())
        gen, status = d.get("general") or {}, (d.get("header") or {}).get("status") or {}
        if status.get("finished") is not True: continue
        content = d.get("content") or {}; facts = content.get("matchFacts") or {}
        info = facts.get("infoBox") or {}; events = events_list(content)
        round_name = str(gen.get("matchRound", ""))
        phase = "regular" if round_name.isdigit() else "playoff"
        score = (status.get("scoreStr") or "0 - 0").split("-")
        hgoals, agoals = int(score[0].strip()), int(score[1].strip())
        def stat(period, key, side):
            pair = flat.get((period, key), (None, None)); return pair[0 if side == "home" else 1]
        flat = flat_stats(content)
        goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
        rec = {"match_id": idx["match_id"], "season": idx["season"], "date": idx["date"],
               "round": round_name, "phase": phase,
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"],
               "home_goals": hgoals, "away_goals": agoals,
               "ht_home_goals": sum(1 for e in goals if e.get("isHome") and isinstance(e.get("time"), (int,float)) and e["time"] <= 45),
               "ht_away_goals": sum(1 for e in goals if not e.get("isHome") and isinstance(e.get("time"), (int,float)) and e["time"] <= 45),
               "ht_source": "events" if goals else "none",
               "events_complete": int(any(e.get("type") == "Half" for e in events) and any(e.get("type") == "Substitution" for e in events)),
               "events_incomplete": int(not (any(e.get("type") == "Half" for e in events) and any(e.get("type") == "Substitution" for e in events))),
               "stats_present": int(bool((content.get("stats") or {}).get("Periods"))),
               "period_splits_present": int(all(("FirstHalf", "SecondHalf") and flat.get((p, "total_shots")) is not None for p in ("FirstHalf", "SecondHalf"))),
               "referee": ((info.get("Referee") or {}).get("text") or ""),
               "shotmap_n": len((content.get("shotmap") or {}).get("shots") or [])}
        for key in STAT_KEYS:
            for per, suffix in (("All", ""), ("FirstHalf", "_1h"), ("SecondHalf", "_2h")):
                for side in ("home", "away"): rec[f"{key}_{side}{suffix}"] = stat(per, key, side)
        for prefix, cards in (("event_yellow", ("Yellow",)), ("event_yellow_unified", ("Yellow", "YellowRed")), ("event_red", ("Red", "YellowRed"))):
            for side in (True, False):
                label = "home" if side else "away"
                rec[f"{prefix}_{label}"] = event_count(events, cards, side)
                if prefix == "event_yellow_unified":
                    for per in ("1h", "2h"): rec[f"{prefix}_{label}_{per}"] = event_count(events, cards, side, per)
        for side in ("home", "away"):
            rec[f"stats_yellow_{side}"] = rec[f"yellow_cards_{side}"]
        rows.append(rec)
        for side in ("home", "away"): variants[gen[f"{side}Team"]["id"]][gen[f"{side}Team"]["name"]] += 1
    assert len(rows) == 1603, len(rows)
    canon = {tid: names.most_common(1)[0][0] for tid, names in variants.items()}
    for r in rows:
        r["home_team"] = canon[r["home_team_id"]]; r["away_team"] = canon[r["away_team_id"]]
    fields = list(rows[0])
    with (OUT / "bo_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    team_rows = []
    for r in rows:
        for side, opp in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "date": r["date"], "round": r["round"], "phase": r["phase"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side}
            for key, a, b in (("goals", "goals", "goals"), ("sot", "ShotsOnTarget", "ShotsOnTarget"), ("corners", "corners", "corners"), ("total_shots", "total_shots", "total_shots"), ("box_touches", "touches_opp_box", "touches_opp_box"), ("possession", "BallPossesion", "BallPossesion"), ("big_chances", "big_chance", "big_chance")):
                x[f"{key}_for"] = r[f"{a}_{side}"] if key != "goals" else r[f"{side}_goals"]
                x[f"{key}_against"] = r[f"{b}_{opp}"] if key != "goals" else r[f"{opp}_goals"]
            x["yellow_for"] = r[f"event_yellow_unified_{side}"]; x["yellow_against"] = r[f"event_yellow_unified_{opp}"]
            team_rows.append(x)
    with (OUT / "bo_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    print(f"matches={len(rows)} team_rows={len(team_rows)} playoff={sum(r['phase']=='playoff' for r in rows)}")
    print("team_name_variants=" + json.dumps({str(k): dict(v) for k,v in variants.items()}, ensure_ascii=False))

if __name__ == "__main__": main()
