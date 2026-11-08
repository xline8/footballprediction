"""Build the reproducible Phase-A Torneo Federal A group-match table."""
from __future__ import annotations
import csv, json, math, os, re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
OUT = HERE.parent
LEAGUE_ID = "9213"
SEASONS = ["2021", "2022", "2023", "2024", "2025", "2026"]
EXPECTED_INDEX = 3219
EXPECTED_GROUP = {"2021":450, "2022":544, "2023":576, "2024":477, "2025":486, "2026":459}
EXPECTED_EXCLUDED = {"2021":15, "2022":15, "2023":17, "2024":61, "2025":65, "2026":54}
FEED_HOLES = {"4438620","4438584","4438589","4438594","4438599","4438645","4438842","4558776","5978435","6462025"}

def warehouse_root() -> Path:
    candidates = []
    if os.environ.get("FOTMOB_WAREHOUSE"):
        candidates.append(Path(os.environ["FOTMOB_WAREHOUSE"]))
    candidates += [REPO / "data_enrichment", Path("/home/hatch/workspace/footballprediction/data_enrichment")]
    for p in candidates:
        if (p / "fotmob_world_index.csv").is_file() and (p / "fotmob_world").is_dir(): return p
    raise FileNotFoundError("No complete FotMob warehouse found")

def payload_path(root: Path, rel: str) -> Path:
    for p in (root / Path(rel), root.parent / Path(rel), Path("/home/hatch/workspace/footballprediction") / Path(rel)):
        if p.is_file(): return p
    raise FileNotFoundError(rel)

def events(content):
    e = (content.get("matchFacts") or {}).get("events")
    return (e.get("events") or []) if isinstance(e, dict) else (e or [])

def tournament_name(x):
    c=x.get("content") or {}; ib=(c.get("matchFacts") or {}).get("infoBox") or {}
    return str((ib.get("Tournament") or {}).get("leagueName") or (x.get("general") or {}).get("leagueName") or "")

def is_excluded(x):
    n=tournament_name(x)
    return any(s in n for s in ("Playoff", "Championship Playoff", "Relegation Playoff", "Additional match"))

def phase_zone(name):
    name = name.replace("\u0410", "A")
    if "Promotion Zona" in name: return "promotion", re.search(r"Zona ([AB])", name).group(1)
    if "Relegation Zona" in name: return "relegation", re.search(r"Zona ([AB])", name).group(1)
    m=re.search(r"Zona ([ABCD])", name)
    if m: return "first",m.group(1)
    raise AssertionError(f"unclassified group league name: {name!r}")

def score(x):
    ts=(x.get("header") or {}).get("teams") or []
    assert len(ts)==2 and all(t.get("score") is not None for t in ts)
    return int(ts[0]["score"]),int(ts[1]["score"])

def referee(c):
    r=(((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {})
    return str(r.get("text") or "").strip() if isinstance(r,dict) else ""

def write_csv(path,rows):
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    root=warehouse_root()
    with (root/"fotmob_world_index.csv").open(newline="",encoding="utf-8") as f:
        parent=[r for r in csv.DictReader(f) if r.get("league_id")==LEAGUE_ID]
    selected=[]; canonical={}; excluded_by_season=Counter(); group_by_season=Counter(); full_cards=Counter(); full_red=Counter(); full_stats=full_shots=full_refs=0
    for ir in parent:
        x=json.load(payload_path(root,ir["path"]).open(encoding="utf-8")); name=str((x.get("general") or {}).get("leagueName") or "")
        if not name.startswith("Federal A"): continue
        c=x.get("content") or {}; full_stats += int(bool((c.get("stats") or {}).get("Periods",{}).get("All") is not None)); full_shots += int(bool((c.get("shotmap") or {}).get("shots"))); full_refs += int(bool(referee(c)))
        for e in events(c):
            if e.get("type")=="Card": full_cards[e.get("card")]+=1
            if e.get("type")=="Card" and e.get("card")=="Red": full_red[ir["season"]]+=1
        for t in (x.get("header") or {}).get("teams") or []:
            if t.get("id") is not None and t.get("name"):
                old=canonical.get(str(t["id"]))
                if old is None or ir["date"]>=old[0]: canonical[str(t["id"])]=(ir["date"],t["name"])
        if is_excluded(x): excluded_by_season[ir["season"]]+=1; continue
        selected.append((ir,x,name)); group_by_season[ir["season"]]+=1
    assert len(parent)==5455
    assert len(selected)+sum(excluded_by_season.values())==EXPECTED_INDEX
    assert dict(group_by_season)==EXPECTED_GROUP,dict(group_by_season)
    assert dict(excluded_by_season)==EXPECTED_EXCLUDED,dict(excluded_by_season)
    assert full_stats==full_shots==full_refs==0
    assert full_cards.get("Yellow",0)==0 and set(full_cards)-{"Red","YellowRed"}==set()
    assert dict(full_red)=={"2021":121,"2022":150,"2023":213,"2024":149,"2025":169,"2026":136},dict(full_red)
    rows=[]; mismatches=[]; boundary=Counter(); cards=Counter(); red_by_season=Counter(); no_events=Counter(); empty_zero=Counter()
    stats_nonempty=shots_any=refs=0
    for ir,x,name in selected:
        c=x.get("content") or {}; evs=events(c); hg,ag=score(x); ts=(x.get("header") or {}).get("teams") or []
        goals=[e for e in evs if e.get("type")=="Goal" and not e.get("isPenaltyShootoutEvent",False)]
        eh=sum(e.get("isHome") is True for e in goals); ea=sum(e.get("isHome") is False for e in goals); mismatch=(eh!=hg or ea!=ag)
        if mismatch: mismatches.append((ir,x,goals))
        if ir["match_id"] in FEED_HOLES: assert mismatch,ir["match_id"]
        has_events=bool(evs)
        if not has_events: no_events[ir["season"]]+=1
        if not has_events and hg==0 and ag==0: empty_zero[ir["season"]]+=1
        for e in goals:
            if e.get("time") in (45,46): boundary[e["time"]]+=1
        for e in evs:
            if e.get("type")=="Card": cards[e.get("card")]+=1
            if e.get("type")=="Card" and e.get("card")=="Red": red_by_season[ir["season"]]+=1
        stats_nonempty += int(bool((c.get("stats") or {}).get("Periods",{}).get("All") is not None)); shots_any += int(bool((c.get("shotmap") or {}).get("shots"))); refs += int(bool(referee(c)))
        phase,zone=phase_zone(name); h,a=ts
        def half(side):
            if mismatch or not has_events: return math.nan
            return sum(1 for e in goals if e.get("isHome") is side and isinstance(e.get("time"),int) and e["time"]<=45)
        rows.append({"match_id":ir["match_id"],"season":ir["season"],"date":ir["date"],"phase":phase,"zone":zone,"tournament":name,"home_team_id":str(h["id"]),"home_team":canonical[str(h["id"])][1],"away_team_id":str(a["id"]),"away_team":canonical[str(a["id"])][1],"home_goals":hg,"away_goals":ag,"ht_home_goals":half(True),"ht_away_goals":half(False),"ht_source":"events" if not mismatch and has_events else "unavailable","event_home_goals":eh,"event_away_goals":ea,"score_event_mismatch":mismatch,"has_events":has_events,"referee":referee(c) or "","stats_nonempty":bool((c.get("stats") or {}).get("Periods",{}).get("All") is not None),"shots_any":bool((c.get("shotmap") or {}).get("shots"))})
    assert len(rows)==2992 and len(mismatches)==9,len(mismatches)
    assert {ir["match_id"] for ir,_,_ in mismatches}==FEED_HOLES-{"6462025"}
    assert stats_nonempty==shots_any==refs==0
    assert cards.get("Yellow",0)==0 and set(cards)-{"Red","YellowRed"}==set()
    write_csv(OUT/"feda_matches.csv",sorted(rows,key=lambda r:(r["date"],int(r["match_id"]))))
    inv={"index_rows_parent_9213":len(parent),"index_rows_federal_a":EXPECTED_INDEX,"date_range":["2021-04-10","2026-11-08"],"group_rows":len(rows),"excluded_rows":sum(excluded_by_season.values()),"group_by_season":dict(group_by_season),"excluded_by_season":dict(excluded_by_season),"distinct_teams_by_season":{s:len({r["home_team_id"] for r in rows if r["season"]==s}|{r["away_team_id"] for r in rows if r["season"]==s}) for s in SEASONS},"stats_nonempty":full_stats,"shots_any":full_shots,"referee_nonempty":full_refs,"card_types":dict(full_cards),"red_by_season":dict(full_red),"group_mismatches":len(mismatches),"group_mismatch_ids":[ir["match_id"] for ir,_,_ in mismatches],"empty_events_by_season":dict(no_events),"empty_0_0_by_season":dict(empty_zero),"goal_times_45_46":dict(boundary),"canonical_team_count":len(canonical)}
    print(json.dumps(inv,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
