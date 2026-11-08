"""Reproducible LT-Toplyga inventory and six-step EDA; no fitting."""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
ROWS = list(csv.DictReader((DATA / "lt_matches.csv").open()))
SEASONS = sorted({r["season"] for r in ROWS}, key=int)
DEV = ["2022", "2023", "2024", "2025"]
PRE_VIRGIN = ["2021", "2022", "2023", "2024", "2025"]

def n(r, k):
    try: return float(r[k])
    except (TypeError, ValueError, KeyError): return None
def mean(x): return round(st.mean(x), 4) if x else None
def pct(x, d): return round(100 * x / d, 2) if d else None
def corr(a, b):
    if len(a) < 5: return None
    ma, mb = st.mean(a), st.mean(b)
    den = math.sqrt(sum((x-ma)**2 for x in a) * sum((y-mb)**2 for y in b))
    return round(sum((x-ma)*(y-mb) for x,y in zip(a,b))/den, 4) if den else None
def goals(r): return int(r["home_goals"]) + int(r["away_goals"])
def over(rs, line): return round(sum(goals(r) > line for r in rs) / len(rs), 4) if rs else None

def levels(rs):
    gs = [goals(r) for r in rs]; hg = [int(r["home_goals"]) for r in rs]; ag = [int(r["away_goals"]) for r in rs]
    return {"matches": len(rs), "goals_per_match": mean(gs), "home_goals_per_match": mean(hg), "away_goals_per_match": mean(ag),
            "home_win_rate": round(sum(x > y for x,y in zip(hg,ag))/len(rs),4),
            "draw_rate": round(sum(x == y for x,y in zip(hg,ag))/len(rs),4),
            "away_win_rate": round(sum(x < y for x,y in zip(hg,ag))/len(rs),4),
            "btts_rate": round(sum(x > 0 and y > 0 for x,y in zip(hg,ag))/len(rs),4),
            "ou1_5_over_rate": over(rs,1.5), "ou2_5_over_rate": over(rs,2.5), "ou3_5_over_rate": over(rs,3.5),
            "home_advantage_goals": mean([x-y for x,y in zip(hg,ag)]),
            "goals_variance": round(st.variance(gs),4) if len(gs)>1 else 0,
            "goals_dispersion_variance_mean": round(st.variance(gs)/st.mean(gs),4) if gs and st.mean(gs) else None,
            "coverage": {"events": pct(sum(r["has_events"]=="1" for r in rs),len(rs)),
                         "ht_derivable": pct(sum(r["ht_source"]=="events" for r in rs),len(rs)),
                         "stats_content": pct(sum(r["has_stats_content"]=="1" for r in rs),len(rs)),
                         "shotmap": pct(sum(r["has_shotmap"]=="1" for r in rs),len(rs)),
                         "lineup": pct(sum(r["has_lineup"]=="1" for r in rs),len(rs)),
                         "referee_nonempty": pct(sum(bool(r["referee"]) for r in rs),len(rs))}}

def reliability(rs):
    tm = defaultdict(list)
    for r in rs:
        for side, other in (("home","away"),("away","home")):
            tm[r[f"{side}_team_id"]].append((r["date"], int(r[f"{side}_goals"]), int(r[f"{other}_goals"])))
    out = {}
    for key, pos in (("goals_for",1),("goals_against",2)):
        a,b=[],[]
        for vals in tm.values():
            vals=sorted(vals)
            if len(vals) >= 24:
                half=len(vals)//2
                a.append(st.mean(v[pos] for v in vals[:half])); b.append(st.mean(v[pos] for v in vals[-half:]))
        out[key]={"r":corr(a,b),"n_teams":len(a),"method":"career chronological first-half vs second-half; teams with >=24 matches"}
    return out

def halves(rs):
    shares=[]; first=[]; full=[]
    for r in rs:
        a,b=n(r,"ht_home_goals"),n(r,"ht_away_goals"); total=goals(r)
        if a is None or b is None or total <= 0: continue
        shares.append((a+b)/total); first.append(a+b); full.append(total)
    p=sum(first)/sum(full) if full else None
    noise=st.mean([p*(1-p)/x for x in full]) if full else None
    obs=st.variance(shares) if len(shares)>1 else 0
    return {"n":len(shares),"share_1h":round(p,6) if p is not None else None,
            "observed_variance":round(obs,6),"noise_expectation":round(noise,6) if noise is not None else None,
            "true_variance":round(obs-noise,6) if noise is not None else None,
            "noise_ratio":round(obs/noise,6) if noise else None,"noise_model":"binomial"}

def team_ids(rs, season):
    return {r[f"{side}_team_id"] for r in rs if r["season"]==season for side in ("home","away")}

def turnover():
    out={}; arrival=[]
    for i,s in enumerate(SEASONS):
        cur=team_ids(ROWS,s); prev=team_ids(ROWS,SEASONS[i-1]) if i else set()
        ins=sorted(cur-prev); outs=sorted(prev-cur)
        out[s]={"team_count":len(cur),"in_ids":ins,"out_ids":outs,"in_count":len(ins),"out_count":len(outs)}
        if i and s in DEV:
            sr=[r for r in ROWS if r["season"]==s]; league_gf=sum(goals(r) for r in sr)/(2*len(sr))
            league_ppg=sum(3 if r["home_goals"]!=r["away_goals"] else 1 for r in sr)/(2*len(sr))
            for tid in ins:
                tr=[r for r in sr if tid in (r["home_team_id"],r["away_team_id"])]
                gf=sum(int(r["home_goals"] if r["home_team_id"]==tid else r["away_goals"]) for r in tr)/len(tr)
                ga=sum(int(r["away_goals"] if r["home_team_id"]==tid else r["home_goals"]) for r in tr)/len(tr)
                ppg=sum(3 if (int(r["home_goals"])>int(r["away_goals"]) and r["home_team_id"]==tid) or (int(r["away_goals"])>int(r["home_goals"]) and r["away_team_id"]==tid) else 1 if r["home_goals"]==r["away_goals"] else 0 for r in tr)/len(tr)
                arrival.append({"season":s,"team_id":tid,"matches":len(tr),"gf":round(gf,4),"ga":round(ga,4),"ppg":round(ppg,4),"league_gf":round(league_gf,4),"league_ppg":round(league_ppg,4)})
    return out,arrival

def thin_data():
    out={}
    for s in SEASONS[1:]:
        prior=defaultdict(int)
        for r in ROWS:
            if int(r["season"]) < int(s): prior[r["home_team_id"]]+=1; prior[r["away_team_id"]]+=1
        ids=team_ids(ROWS,s); out[s]={"team_count_lt6":sum(prior[t]<6 for t in ids),"counts":{t:prior[t] for t in sorted(ids)}}
    return out

def main():
    per={s:levels([r for r in ROWS if r["season"]==s]) for s in SEASONS}
    dev=[r for r in ROWS if r["season"] in DEV]; pre=[r for r in ROWS if r["season"] in PRE_VIRGIN]
    turns, arrivals=turnover()
    names=defaultdict(set)
    for r in ROWS:
        names[r["home_team_id"]].add(r["home_team"]); names[r["away_team_id"]].add(r["away_team"])
    inv={"league":"LT-Toplyga","league_id":"228","rows":len(ROWS),"team_rows":len(ROWS)*2,"seasons":per,
         "distinct_team_ids":len(names),"team_id_name_map":{k:sorted(v) for k,v in sorted(names.items())},
         "multi_name_team_ids":{k:sorted(v) for k,v in names.items() if len(v)>1},"turnover":turns,
         "coverage_by_season":{s:per[s]["coverage"] for s in SEASONS},
         "stats_null_rows":sum(r["has_stats_content"]=="0" for r in ROWS),"shot_count_zero_rows":sum(r["has_shotmap"]=="0" for r in ROWS),
         "lineup_null_rows":sum(r["has_lineup"]=="0" for r in ROWS),"referee_nonempty_rows":sum(bool(r["referee"]) for r in ROWS),
         "coverage_levels":sorted({r["coverage_level"] for r in ROWS}),"events_present_rows":sum(r["has_events"]=="1" for r in ROWS),
         "empty_event_rows":sum(r["has_events"]=="0" for r in ROWS),"goal_score_mismatch_rows":[r["match_id"] for r in ROWS if r["score_events_mismatch"]=="1"],
         "awarded_matches":[r["match_id"] for r in ROWS if r["awarded"]=="1"],"card_event_counts":{k:sum(int(r[f"card_{k}_count"]) for r in ROWS) for k in ("yellow","yellowred","red")},
         "has_playoff_values":dict(__import__('collections').Counter(r["has_playoff_value"] for r in ROWS)),
         "format":{s:{"rounds":len({r["round"] for r in ROWS if r["season"]==s}),"round_match_count_distribution":dict(__import__('collections').Counter(__import__('collections').Counter(r["round"] for r in ROWS if r["season"]==s).values())),"teams":len(team_ids(ROWS,s)),"date_range":[min(r["date"] for r in ROWS if r["season"]==s),max(r["date"] for r in ROWS if r["season"]==s)]} for s in SEASONS}}
    lines={str(x):{"over_rate":over(dev,x),"n":len(dev)} for x in (1.5,2.5,3.5)}
    primary=min(lines,key=lambda x:abs(lines[x]["over_rate"]-0.5))
    out={"league":"LT-Toplyga","league_id":"228","seasons":SEASONS,"per_season":per,"pooled_levels":levels(ROWS),"pooled_dev_levels":levels(dev),
         "reliability":reliability(ROWS),"halves":{"pre_virgin":halves(pre),"virgin_2026_descriptive":halves([r for r in ROWS if r["season"]=="2026"]),"constant_frozen":halves(pre)["share_1h"]},
         "turnover":turns,"arrival_metrics":arrivals,"sibling_league_available":False,"thin_data":thin_data(),"dev_line_tables":{"lines":lines,"primary_line":float(primary),"n":len(dev)},
         "windows":{"seed":"2021","eval_seasons":DEV,"dev_n":len(dev),"virgin":"2026","virgin_n":sum(r["season"]=="2026" for r in ROWS),"confirmatory_reserved":"2027"},"inventory":inv}
    (HERE/"eda_numbers.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)); (HERE/"inventory_summary.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False))
    print(json.dumps({"season_counts":{s:per[s]["matches"] for s in SEASONS},"F1":{s:per[s]["goals_per_match"] for s in SEASONS},"F2":out["reliability"],"F3":out["halves"],"F4":turns,"F5":out["thin_data"],"primary":out["dev_line_tables"]},indent=2))
if __name__=="__main__": main()
