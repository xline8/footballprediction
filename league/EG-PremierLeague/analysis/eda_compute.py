"""Egypt Premier League phase-1 EDA; writes frozen evidence JSON."""
import csv, json, math, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "eg_matches.csv")))
ROWS.sort(key=lambda r: (r["date"], r["match_id"]))
SEASONS = ["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026","2026/2027"]
DEV = ["2021/2022","2022/2023","2023/2024","2024/2025"]
HALF_DEV = ["2023/2024","2024/2025"]

def f(r, k):
    v = r.get(k)
    return None if v in (None, "", "None") else float(v)

def pct(n, d): return round(100*n/d, 1) if d else None
def avg(xs): return round(st.mean(xs), 3) if xs else None

def corr(xs, ys):
    if len(xs) < 5: return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return round(sum((x-mx)*(y-my) for x,y in zip(xs,ys))/den, 3) if den else None

def split_rel(series, min_n=10):
    xs, ys = [], []
    for vals in series.values():
        if len(vals) >= min_n:
            xs.append(st.mean(vals[0::2])); ys.append(st.mean(vals[1::2]))
    return {"r": corr(xs, ys), "n_entities": len(xs), "min_n": min_n}

def team_series(fn, seasons=None):
    d = defaultdict(list)
    for r in ROWS:
        if seasons and r["season"] not in seasons: continue
        for side, opp in (("home","away"),("away","home")):
            v = fn(r, side, opp)
            if v is not None: d[r[f"{side}_team_id"]].append(v)
    return d

def stat(key):
    return lambda r, side, opp: f(r, f"{key}_{side}")

def goal(against=False):
    return lambda r, side, opp: f(r, f"{opp if against else side}_goals")

def reliability(seasons=None):
    specs = {
        "goals_for":goal(), "goals_against":goal(True),
        "sot_for":stat("ShotsOnTarget"), "sot_against":lambda r,s,o:f(r,f"ShotsOnTarget_{o}"),
        "corners_for":stat("corners"), "corners_against":lambda r,s,o:f(r,f"corners_{o}"),
        "yellows_for":stat("yellow_cards"), "yellows_against":lambda r,s,o:f(r,f"yellow_cards_{o}"),
        "shots_for":stat("total_shots"), "shots_against":lambda r,s,o:f(r,f"total_shots_{o}"),
        "touches_for":stat("touches_opp_box"), "touches_against":lambda r,s,o:f(r,f"touches_opp_box_{o}"),
        "possession":stat("BallPossesion"), "big_chance":stat("big_chance"),
    }
    return {k:split_rel(team_series(fn, seasons)) for k,fn in specs.items()}

def total(r, key):
    a,b = f(r,f"{key}_home"), f(r,f"{key}_away")
    return a+b if a is not None and b is not None else None

def team_dist(rs):
    c=Counter()
    for r in rs: c[r["home_team_id"]]+=1; c[r["away_team_id"]]+=1
    return {"team_count":len(c), "matches_per_team":dict(sorted(Counter(c.values()).items())), "team_ids":sorted(c)}

def levels(rs):
    def field(k): return avg([v for r in rs if (v:=total(r,k)) is not None])
    ev = [sum(int(r[f"ev_yellow{s}_{side}"]) for side in ("home","away") for s in ("","red")) for r in rs]
    return {
        "n":len(rs), "goals":avg([int(r["home_goals"])+int(r["away_goals"]) for r in rs]),
        "home_goals":avg([int(r["home_goals"]) for r in rs]), "away_goals":avg([int(r["away_goals"]) for r in rs]),
        "xg":field("expected_goals"), "sot":field("ShotsOnTarget"), "corners":field("corners"),
        "shots":field("total_shots"), "yellows_stats":field("yellow_cards"), "yellows_events":avg(ev), "reds":field("red_cards"),
        "coverage":{
            "stats_all_pct":pct(sum(r["has_stats_all"]=="1" for r in rs),len(rs)),
            "half_splits_pct":pct(sum(r["has_stats_half"]=="1" for r in rs),len(rs)),
            "shotmap_pct":pct(sum(r["has_shotmap"]=="1" for r in rs),len(rs)),
            "xg_pct":pct(sum(f(r,"expected_goals_home") is not None and f(r,"expected_goals_away") is not None for r in rs),len(rs)),
            "touches_pct":pct(sum(f(r,"touches_opp_box_home") is not None and f(r,"touches_opp_box_away") is not None for r in rs),len(rs)),
            "referee_pct":pct(sum(bool(r["referee"]) for r in rs),len(rs)),
            "goal_event_time_pct":pct(sum(r["goal_event_time_coverage"]=="1" for r in rs),len(rs))},
        "teams":team_dist(rs)}

out={"n":len(ROWS),"team_rows":len(ROWS)*2,"seasons":SEASONS,"dev_seasons":DEV,"virgin_inventory_season":"2025/2026"}
out["per_season"]={s:levels([r for r in ROWS if r["season"]==s]) for s in SEASONS}

out["cards_agreement_all_seasons"]={}
for s in SEASONS:
    rs=[r for r in ROWS if r["season"]==s]
    diffs=[total(r,"yellow_cards")-sum(int(r[f"ev_yellow{x}_{side}"]) for side in ("home","away") for x in ("","red")) for r in rs if total(r,"yellow_cards") is not None]
    out["cards_agreement_all_seasons"][s]={"n":len(rs),"n_with_both_feeds":len(diffs),"stats_missing_count":len(rs)-len(diffs),"exact_pct":pct(sum(x==0 for x in diffs),len(diffs)),
        "stats_low_count":sum(x<0 for x in diffs),"stats_high_count":sum(x>0 for x in diffs),
        "mean_stats_minus_events":round(st.mean(diffs),3)}

out["reliability_career"]=reliability()
out["reliability_2023_2025"]=reliability(set(HALF_DEV))
refs=defaultdict(list)
for r in ROWS:
    if r["season"] in DEV and r["referee"] and total(r,"yellow_cards") is not None: refs[r["referee"]].append(total(r,"yellow_cards"))
out["referee_reliability_dev"]=split_rel(refs)
out["referees_ge10_dev"]=sum(len(v)>=10 for v in refs.values())

def half_record(name, key):
    shares=[]; weights=[]
    for r in ROWS:
        if r["season"] not in HALF_DEV or r["has_stats_half"]!="1": continue
        if name=="goals":
            if r["goal_event_time_coverage"]!="1": continue
            n=int(r["ht_home_goals"])+int(r["ht_away_goals"]); d=int(r["home_goals"])+int(r["away_goals"])
        else:
            n=(f(r,f"fh_{key}_home") or 0)+(f(r,f"fh_{key}_away") or 0); d=total(r,key)
        if d and d>0: shares.append(n/d); weights.append(d)
    p=st.mean(shares); ov=st.variance(shares); noise=st.mean([p*(1-p)/w for w in weights])
    return {"n":len(shares),"share":round(p,4),"observed_variance":round(ov,6),
            "binomial_noise_variance":round(noise,6),"true_sd":round(math.sqrt(max(ov-noise,0)),4)}
out["half_shares_complete_dev"]={k:half_record(k, v) for k,v in
    {"goals":None,"sot":"ShotsOnTarget","corners":"corners","shots":"total_shots","yellows":"yellow_cards"}.items()}

def home_edge(seasons):
    rs=[r for r in ROWS if r["season"] in seasons]
    return {"n":len(rs),"home_edge":round(st.mean([int(r["home_goals"])-int(r["away_goals"]) for r in rs]),3),
            "home_win_pct":pct(sum(int(r["home_goals"])>int(r["away_goals"]) for r in rs),len(rs))}
out["home_edge"]={s:home_edge([s]) for s in SEASONS}; out["home_edge"]["pooled_dev"]=home_edge(DEV)

def over(vals,line): return round(sum(v>line for v in vals)/len(vals),3)
def primary(seasons):
    rs=[r for r in ROWS if r["season"] in seasons]; ans={"n":len(rs),"seasons":seasons}
    for name,key in {"sot":"ShotsOnTarget","corners":"corners","shots":"total_shots","yellows":"yellow_cards"}.items():
        vals=[total(r,key) for r in rs if total(r,key) is not None]
        cands=[x+.5 for x in range(math.floor(min(vals)),math.ceil(max(vals)))]
        line=min(cands,key=lambda x:(abs(over(vals,x)-.5),x))
        ans[name]={"mean":round(st.mean(vals),3),"primary_line":line,"over_rate":over(vals,line),
                   "ladder":{str(x):over(vals,x) for x in (line-1,line,line+1)}}
    goals=[int(r["home_goals"])+int(r["away_goals"]) for r in rs]
    ans["goals_ou25_over_rate"]=over(goals,2.5)
    return ans
out["primary_lines"]={"pooled_2022_2025":primary(["2022/2023","2023/2024","2024/2025"]),
                      "pooled_2023_2025":primary(HALF_DEV)}
json.dump(out,open(HERE/"eda_numbers.json","w"),indent=2)
print(json.dumps(out,indent=2))
