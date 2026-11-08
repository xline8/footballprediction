"""Build Kazakhstan Premier League scores/event data from FotMob warehouse JSONs.

Calendar-year seasons are retained as warehouse labels.  This league is
scores-only: stats and period splits are absent in every payload (Periods
empty, shotmap empty, no xG in any season).  All 1,124 payloads are finished;
the finished filter is kept and drops nothing.  Teams are keyed by FotMob ID
and names are canonicalised per ID (Kaspyi/Kaspiy Aktau 200279 spelling
variant; Altai Semey / FC Altai Oskemen 732295 rename).

Warehouse note: the 24 GB fotmob_world tree is untracked in the repo, so a
git worktree does not contain it.  Paths in the index are resolved against
the repo root when it holds the warehouse, else against the main checkout
~/workspace/footballprediction (read-only).
"""
import csv, json, sys
from collections import Counter
from pathlib import Path

ALL_STATS = ["expected_goals", "expected_goals_open_play", "expected_goals_set_play",
             "expected_goals_non_penalty", "total_shots", "ShotsOnTarget",
             "ShotsOffTarget", "blocked_shots", "shots_inside_box",
             "shots_outside_box", "big_chance", "touches_opp_box", "corners",
             "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves",
             "BallPossesion"]

def events_of(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []

def stats_flat(content):
    out = {}
    periods = (((content or {}).get("stats") or {}).get("Periods") or {})
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for s in group.get("stats", []) or []:
                vals = s.get("stats") or []
                if len(vals) > 1: out[(period, s.get("key"))] = (vals[0], vals[1])
    return out

def phase(name):
    # Payloads do not consistently label Segunda phases; preserve the label
    # and only classify when the league name explicitly does so.
    n = name or ""
    if "Apertura" in n: return "apertura"
    if "Clausura" in n: return "clausura"
    if "Playoff" in n or "Final" in n: return "playoff_or_final"
    return "unknown"

def parse(season, path):
    d = json.load(open(path)); g = d.get("general") or {}; h = d.get("header") or {}
    c = d.get("content") or {}; st = h.get("status") or {}
    ht, at = g.get("homeTeam") or {}, g.get("awayTeam") or {}
    score = st.get("scoreStr") or ""; hg = ag = None
    if " - " in score:
        try: hg, ag = map(int, score.split(" - "))
        except ValueError: pass
    evs = events_of(c); ge = [e for e in evs if e.get("type") == "Goal"]
    cards = [e for e in evs if e.get("type") == "Card"]
    info = ((c.get("matchFacts") or {}).get("infoBox") or {})
    referee = ((info.get("Referee") or {}).get("text") or "").strip() or None
    sf = stats_flat(c)
    def val(p,k,side): return sf.get((p,k), (None,None))[side]
    row = {
      "match_id": int(g.get("matchId") or path.stem), "league":"KZ-PremierLeague",
      "season":str(season), "season_start":int(season), "date":(g.get("matchTimeUTCDate") or "")[:10],
      "kickoff_utc":g.get("matchTimeUTCDate"), "round":g.get("matchRound"),
      "league_name":g.get("leagueName"), "phase":phase(g.get("leagueName")),
      "home_team_id":ht.get("id"), "home_team":ht.get("name"), "away_team_id":at.get("id"), "away_team":at.get("name"),
      "home_goals":hg, "away_goals":ag, "finished":bool(st.get("finished")),
      "awarded":bool(st.get("awarded")), "has_events":bool(evs), "has_lineup":False,
      "referee":referee, "has_referee":referee is not None,
      "has_stats_all":bool(sf), "has_stats_half":any(p in ("FirstHalf","SecondHalf") for p,k in sf),
      "has_shotmap":bool((c.get("shotmap") or {}).get("shots")),
    }
    for side in ("home","away"):
        row[f"ev_goals_{side}"] = sum(1 for e in ge if e.get("isHome") == (side=="home")) if evs else None
    row["score_events_mismatch"] = bool(evs and hg is not None and (row["ev_goals_home"],row["ev_goals_away"]) != (hg,ag))
    htgoals = [e for e in ge if isinstance(e.get("time"),(int,float)) and e.get("isHome") is not None]
    if ge and len(htgoals) == len(ge):
        row["ht_home_goals"] = sum(1 for e in ge if e["time"] <= 45 and e["isHome"])
        row["ht_away_goals"] = sum(1 for e in ge if e["time"] <= 45 and not e["isHome"])
    elif evs: row["ht_home_goals"] = row["ht_away_goals"] = 0
    else: row["ht_home_goals"] = row["ht_away_goals"] = None
    row["goals_1h_total"] = (row["ht_home_goals"] + row["ht_away_goals"]) if row["ht_home_goals"] is not None else None
    row["ht_source"] = "events" if row["goals_1h_total"] is not None else "none"
    for kind,col in (("Red","ev_red"),("YellowRed","ev_yellowred"),("Yellow","ev_yellow")):
        for side in ("home","away"):
            row[f"{col}_{side}"] = sum(1 for e in cards if e.get("card")==kind and e.get("isHome")== (side=="home")) if evs else None
    row["ev_cards_complete"] = bool(evs)
    for k in ALL_STATS:
        row[f"{k}_home"],row[f"{k}_away"] = val("All",k,0),val("All",k,1)
    lu = c.get("lineup") or {}
    for side in ("homeTeam","awayTeam"):
        if len((lu.get(side) or {}).get("starters") or []) == 11: row["has_lineup"] = True
    for side,opp in (("home","away"),("away","home")):
        row[f"yellow_{side}"] = row[f"red_{side}"] = None
    row["cards_source"] = "none"
    return row

def team_rows(m):
    out=[]
    for side,opp,venue in (("home","away","H"),("away","home","A")):
        gf,ga=m[f"{side}_goals"],m[f"{opp}_goals"]
        out.append({"match_id":m["match_id"],"league":m["league"],"season":m["season"],"season_start":m["season_start"],"date":m["date"],"phase":m["phase"],"team_id":m[f"{side}_team_id"],"team":m[f"{side}_team"],"opponent_id":m[f"{opp}_team_id"],"opponent":m[f"{opp}_team"],"venue":venue,"goals_for":gf,"goals_against":ga,"ht_goals_for":m[f"ht_{side}_goals"],"ht_goals_against":m[f"ht_{opp}_goals"],"result":"W" if gf>ga else ("D" if gf==ga else "L"),"points":3 if gf>ga else (1 if gf==ga else 0),"has_stats_all":m["has_stats_all"],"has_stats_half":m["has_stats_half"]})
    return out

def main():
    idx=Path(sys.argv[1]) if len(sys.argv)>1 else Path("data_enrichment/fotmob_world_index.csv")
    root=Path(sys.argv[2]) if len(sys.argv)>2 else Path(".")
    out=Path(sys.argv[3]) if len(sys.argv)>3 else Path(__file__).parent
    ix=[r for r in csv.DictReader(open(idx)) if r.get("league_id") == "225"]; rows=[]; seen=set(); names={}; dropped=Counter()
    if not (root/"data_enrichment/fotmob_world/Kazakhstan").exists():
        alt=Path.home()/"workspace/footballprediction"
        if (alt/"data_enrichment/fotmob_world/Kazakhstan").exists(): root=alt
    for r in ix:
        p=root / r["path"]
        m=parse(r["season"],p)
        if m["match_id"] in seen: raise ValueError("duplicate match")
        seen.add(m["match_id"])
        if not m["finished"]: dropped[m["season"]]+=1; continue
        rows.append(m)
        for tid,n in ((m["home_team_id"],m["home_team"]),(m["away_team_id"],m["away_team"])): names.setdefault(tid,Counter())[n]+=1
    canon={tid:c.most_common(1)[0][0] for tid,c in names.items()}
    for m in rows: m["home_team"]=canon[m["home_team_id"]]; m["away_team"]=canon[m["away_team_id"]]
    rows.sort(key=lambda x:(x["date"],x["match_id"])); out.mkdir(parents=True,exist_ok=True)
    for fn,data in (("kz_premier_matches.csv",rows),("kz_premier_team_matches.csv",[x for m in rows for x in team_rows(m)])):
        with open(out/fn,"w",newline="") as f: w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    print(f"index={len(ix)} finished={len(rows)} dropped={dict(dropped)} teams={len(canon)} variants={ {k:dict(v) for k,v in names.items() if len(v)>1} }")
if __name__=="__main__": main()
