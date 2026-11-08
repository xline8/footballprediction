"""Reproducible Bulgaria First League inventory and EDA; deliberately no fitting."""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "bg_matches.csv").open()))
WAREHOUSE = Path.home() / "workspace" / "footballprediction"
SEASONS = sorted({r["season"] for r in ROWS})
GOALS_DEV = set(SEASONS)
STATS_DEV = {"2022/2023", "2023/2024", "2024/2025"}
VIRGIN, CONFIRMATORY = "2025/2026", "2026/2027"

def f(r, k):
    try: return None if r.get(k) in (None, "", "None") else float(r[k])
    except (TypeError, ValueError): return None
def avg(v): return round(st.mean(v), 3) if v else None
def pct(n, d): return round(100*n/d, 1) if d else None
def corr(xs, ys):
    if len(xs) < 5: return None
    mx, my = st.mean(xs), st.mean(ys); den = math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return round(sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den, 3) if den else None
def total(r, key):
    a,b=f(r, key+"_home"),f(r,key+"_away")
    return a+b if a is not None and b is not None else None
def goals(r): return int(r["home_goals"])+int(r["away_goals"])
def rates(v, lines): return {str(x): {"over_rate": round(sum(n>x for n in v)/len(v),3), "n":len(v)} for x in lines} if v else {str(x): {"over_rate":None,"n":0} for x in lines}

def levels(rows):
    g=[goals(r) for r in rows]
    out={"matches":len(rows),"goals_per_match":avg(g),"home_win_rate":round(sum(int(r["home_goals"])>int(r["away_goals"]) for r in rows)/len(rows),3) if rows else None,"draw_rate":round(sum(r["home_goals"]==r["away_goals"] for r in rows)/len(rows),3) if rows else None,"away_win_rate":round(sum(int(r["home_goals"])<int(r["away_goals"]) for r in rows)/len(rows),3) if rows else None,"ou2_5_over_rate":round(sum(x>2.5 for x in g)/len(g),3) if g else None,"home_advantage":{"goals":avg([int(r["home_goals"])-int(r["away_goals"]) for r in rows]) if rows else None},"coverage":{"stats_all":pct(sum(r["has_stats_all"]=="1" for r in rows),len(rows)),"period_splits":pct(sum(r["has_period_splits_content"]=="1" for r in rows),len(rows)),"shotmap":pct(sum(r["has_shotmap"]=="1" for r in rows),len(rows)),"referee":pct(sum(bool(r["referee"]) for r in rows),len(rows))}}
    for name,key,lines in (("sot","ShotsOnTarget",[8.5,9.5,10.5]),("corners","corners",[8.5,9.5,10.5]),("cards","yellow",[3.5,4.5,5.5]),("total_shots","total_shots",[24.5,25.5,26.5,27.5,28.5])):
        v=[total(r,key) for r in rows if total(r,key) is not None]; out[name]={"mean":avg(v),"n":len(v),"over_rates":rates(v,lines),"home_advantage":avg([f(r,key+"_home")-f(r,key+"_away") for r in rows if f(r,key+"_home") is not None and f(r,key+"_away") is not None])}; out["coverage"][name]=pct(len(v),len(rows))
    return out
def season_inventory(rows, s):
    x=[r for r in rows if r["season"]==s]; teams=defaultdict(int)
    for r in x: teams[r["home_team_id"]]+=1; teams[r["away_team_id"]]+=1
    return {"distinct_team_ids":len(teams),"matches_per_team":{"min":min(teams.values()),"max":max(teams.values())},"referee_coverage":pct(sum(bool(r["referee"]) for r in x),len(x)),"phase_counts":dict(sorted((p,sum(r["phase"]==p for r in x)) for p in {r["phase"] for r in x}))}
def trait_values(rows,key,against=False):
    out=defaultdict(list)
    for r in rows:
        for side,other in (("home","away"),("away","home")):
            v=f(r,key+"_"+(other if against else side))
            if v is not None: out[(r[side+"_team_id"],r["season"])].append(v)
    return out
def goal_values(rows,against=False):
    out=defaultdict(list)
    for r in rows:
        for side,other in (("home","away"),("away","home")): out[(r[side+"_team_id"],r["season"])].append(float(r[other+"_goals"] if against else r[side+"_goals"]))
    return out
def reliability(rows):
    specs={"goals_for":(None,False),"goals_against":(None,True),"ShotsOnTarget_for":("ShotsOnTarget",False),"ShotsOnTarget_against":("ShotsOnTarget",True),"corners_for":("corners",False),"corners_against":("corners",True),"total_shots_for":("total_shots",False),"total_shots_against":("total_shots",True),"yellow_for":("yellow",False),"yellow_against":("yellow",True),"BallPossesion_for":("BallPossesion",False),"BallPossesion_against":("BallPossesion",True)}
    out={}
    for name,(key,against) in specs.items():
        series=goal_values(rows,against) if key is None else trait_values(rows,key,against); a=[];b=[]
        for v in series.values():
            if len(v)>=8 and v[::2] and v[1::2]: a.append(st.mean(v[::2]));b.append(st.mean(v[1::2]))
        out[name]={"r":corr(a,b),"n_team_seasons":len(a)}
    return out
def half_stats(rows, fh, ft):
    shares=[]; first=[]; full=[]
    for r in rows:
        a,b=total(r,fh),total(r,ft)
        if a is not None and b is not None and b>0 and a>=0: shares.append(a/b);first.append(a);full.append(b)
    if not shares:return {"n":0,"share_1h":None,"observed_variance":None,"noise_expectation":None,"true_variance":None}
    p=sum(first)/sum(full); noise=st.mean([p*(1-p)/x for x in full]); obs=st.variance(shares) if len(shares)>1 else 0
    return {"n":len(shares),"share_1h":round(p,4),"observed_variance":round(obs,5),"noise_expectation":round(noise,5),"true_variance":round(obs-noise,5),"noise_ratio":round(obs/noise,3) if noise else None,"noise_model":"binomial"}

PRE=[r for r in ROWS if r["season"] in {"2021/2022","2022/2023","2023/2024","2024/2025"}]
for r in ROWS:
    r["ht_goals_home"],r["ht_goals_away"]=r["ht_home_goals"],r["ht_away_goals"]
    r["goals_home"],r["goals_away"]=r["home_goals"],r["away_goals"]
halves={"goals":half_stats(PRE,"ht_goals","goals"),"yellow_cards":half_stats(PRE,"ht_yellow","yellow"),"sot":{"n":0,"reason":"no period splits, no event source"},"corners":{"n":0,"reason":"no period splits, no event source"},"total_shots":{"n":0,"reason":"no period splits, no event source"},"definition":"pooled pre-virgin seasons; event-derived first halves"}
def referee_reliability(rows):
    groups=defaultdict(list)
    for r in sorted(rows,key=lambda x:(x["referee"],x["date"],x["match_id"])):
        if r["referee"] and total(r,"yellow") is not None: groups[r["referee"]].append(total(r,"yellow"))
    pairs=[(st.mean(v[::2]),st.mean(v[1::2])) for v in groups.values() if len(v)>=20]
    return {"r":corr([a for a,b in pairs],[b for a,b in pairs]),"n_referees":len(pairs),"n_matches":sum(len(v) for v in groups.values() if len(v)>=20),"minimum_matches":20}
def team_record(rows,s,tid):
    gf=[];ga=[]
    for r in rows:
        if r["season"]!=s:continue
        if str(r["home_team_id"])==tid:gf.append(int(r["home_goals"]));ga.append(int(r["away_goals"]))
        elif str(r["away_team_id"])==tid:gf.append(int(r["away_goals"]));ga.append(int(r["home_goals"]))
    return {"matches":len(gf),"gf_per_match":avg(gf),"ga_per_match":avg(ga)}
def second_ids(folder, season):
    ids=set()
    index=WAREHOUSE/"data_enrichment"/"fotmob_world_index.csv"
    paths=[WAREHOUSE/r["path"] for r in csv.DictReader(index.open()) if r["league_id"]=="9096" and r["season"]==season]
    for p in paths:
        if p.parent != folder: continue
        try:
            x=json.loads(p.read_text()); g=x.get("general") or {}
            for k in ("homeTeam","awayTeam"):
                if g.get(k,{}).get("id") is not None: ids.add(str(g[k]["id"]))
        except (OSError, json.JSONDecodeError): pass
    return ids
t1={s:{str(r[k]) for r in ROWS if r["season"]==s for k in ("home_team_id","away_team_id")} for s in SEASONS}; means={s:avg([int(r[k+"_goals"]) for r in ROWS if r["season"]==s for k in ("home","away")]) for s in SEASONS}; movers=[]
for s in ["2022/2023","2023/2024","2024/2025","2025/2026"]:
    y=str(int(s[:4])-1)+"-"+str(int(s[5:])-1); prior=second_ids(WAREHOUSE/"data_enrichment/fotmob_world/Bulgaria/Second Professional League"/y,y.replace("-","/"))
    for tid in sorted(t1[s]&prior):
        rec=team_record(ROWS,s,tid); name=next((r["home_team"] if str(r["home_team_id"])==tid else r["away_team"] for r in ROWS if r["season"]==s and tid in (str(r["home_team_id"]),str(r["away_team_id"]))),tid)
        movers.append({"season":s,"team_id":tid,"team":name,"direction":"entrant","first_t1":rec,"gap_vs_t1_mean":{"gf":round(rec["gf_per_match"]-means[s],3),"ga":round(rec["ga_per_match"]-means[s],3)},"previous_tier":"Second Professional League"})
name_sets=defaultdict(set)
for r in ROWS:name_sets[str(r["home_team_id"])].add(r["home_team"]);name_sets[str(r["away_team_id"])].add(r["away_team"])
multi={k:sorted(v) for k,v in name_sets.items() if len(v)>1}; per={s:{**levels([r for r in ROWS if r["season"]==s]),**season_inventory(ROWS,s),"date_range":[min(r["date"] for r in ROWS if r["season"]==s),max(r["date"] for r in ROWS if r["season"]==s)]} for s in SEASONS}
inventory={"league":"BG-FirstLeague","league_id":"270","rows":len(ROWS),"team_rows":len(ROWS)*2,"seasons":per,"distinct_team_ids":len(name_sets),"multi_name_team_ids":multi,"phase_values":sorted({r["phase"] for r in ROWS}),"phase_counts":{s:season_inventory(ROWS,s)["phase_counts"] for s in SEASONS},"cards_source_counts":{"events":sum(r["cards_source"]=="events" for r in ROWS)},"dev_definitions":{"goals":sorted(GOALS_DEV),"stats_markets":sorted(STATS_DEV)},"virgin":VIRGIN,"confirmatory":CONFIRMATORY}
DEV=[r for r in ROWS if r["season"] in STATS_DEV]; line_tables={}
for n,k,ls in (("sot","ShotsOnTarget",[8.5,9.5,10.5]),("corners","corners",[8.5,9.5,10.5]),("cards","yellow",[3.5,4.5,5.5]),("total_shots","total_shots",[24.5,25.5,26.5,27.5,28.5])):
    v=[total(r,k) for r in DEV if total(r,k) is not None]; line_tables[n]={"candidate_lines":rates(v,ls),"primary_line":min(ls,key=lambda x:abs(sum(a>x for a in v)/len(v)-.5)) if v else None,"n":len(v)}
line_tables["goals"]={"candidate_lines":rates([goals(r) for r in ROWS if r["season"] in GOALS_DEV],[2.5]),"primary_line":2.5,"n":len(ROWS)}
out={"league":"BG-FirstLeague","league_id":"270","n":len(ROWS),"seasons":SEASONS,"per_season":per,"pooled_levels":levels(ROWS),"pooled_dev_levels":levels(DEV),"reliability":reliability(ROWS),"referee_reliability":referee_reliability(PRE),"halves":halves,"movers":movers,"dev_line_tables":line_tables,"windows":{"goals_dev":sorted(GOALS_DEV),"stats_market_dev":sorted(STATS_DEV),"virgin":VIRGIN,"confirmatory":CONFIRMATORY},"inventory":inventory}
(HERE/"eda_numbers.json").write_text(json.dumps(out,indent=2)+"\n");(HERE/"inventory_summary.json").write_text(json.dumps(inventory,indent=2)+"\n")
print(json.dumps({"n":len(ROWS),"seasons":SEASONS,"phase_counts":inventory["phase_counts"],"reliability":out["reliability"],"halves":halves,"movers":len(movers)},indent=2))
