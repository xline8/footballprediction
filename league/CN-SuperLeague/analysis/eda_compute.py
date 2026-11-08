"""China Super League Phase-A EDA. No fitting, walk-forward, or parameter estimation."""
import csv, json, math, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "cn_matches.csv").open()))
SEASONS = sorted({r["season"] for r in ROWS}, key=int)
MARKETS = {"goals":"goals", "sot":"ShotsOnTarget", "corners":"corners", "cards":"yellow_cards", "total_shots":"total_shots", "fouls":"fouls", "touches_opp_box":"touches_opp_box"}

def num(v):
    try: return None if v in (None, "", "None") else float(v)
    except (TypeError, ValueError): return None
def mean(x): return round(st.mean(x), 4) if x else None
def corr(x, y):
    if len(x) < 5: return None
    mx, my = st.mean(x), st.mean(y)
    den = math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return round(sum((a-mx)*(b-my) for a,b in zip(x,y))/den, 4) if den else None
def total(r, key):
    if key == "goals": return num(r["home_goals"])+num(r["away_goals"])
    a,b=num(r[f"{key}_home"]),num(r[f"{key}_away"])
    return a+b if a is not None and b is not None else None
def pct(n,d): return round(100*n/d,2) if d else None
def vals(rs,key): return [total(r,key) for r in rs if total(r,key) is not None]

def levels(rs):
    goals = vals(rs,"goals")
    out={"matches":len(rs), "goals_per_match":mean(goals),
         "home_goals_per_match":mean([num(r["home_goals"]) for r in rs]),
         "away_goals_per_match":mean([num(r["away_goals"]) for r in rs]),
         "home_advantage_goals":mean([num(r["home_goals"])-num(r["away_goals"]) for r in rs]),
         "home_win_rate":pct(sum(num(r["home_goals"])>num(r["away_goals"]) for r in rs),len(rs)),
         "draw_rate":pct(sum(num(r["home_goals"])==num(r["away_goals"]) for r in rs),len(rs)),
         "away_win_rate":pct(sum(num(r["home_goals"])<num(r["away_goals"]) for r in rs),len(rs)),
         "coverage": {"score":pct(len(rs),len(rs)), "stats":pct(sum(r["has_stats"]=="1" for r in rs),len(rs)),
                      "splits":pct(sum(r["has_splits"]=="1" for r in rs),len(rs)),
                      "events":pct(sum(r["has_events"]=="1" for r in rs),len(rs)),
                      "referee":pct(sum(bool(r["referee"]) for r in rs),len(rs)),
                      "shotmap":pct(sum(r["has_shotmap"]=="1" for r in rs),len(rs)),
                      "xg":0.0}}
    for name,key in MARKETS.items():
        vv=vals(rs,key)
        if key == "goals":
            ha=[num(r["home_goals"])-num(r["away_goals"]) for r in rs]
        else:
            ha=[num(r[f"{key}_home"])-num(r[f"{key}_away"]) for r in rs if num(r[f"{key}_home"]) is not None and num(r[f"{key}_away"]) is not None]
        out[name]={"mean":mean(vv),"n":len(vv),"coverage_pct":pct(len(vv),len(rs)),"home_advantage":mean(ha)}
    out["cards"]["event_mean"] = mean([num(r["ev_yellow_home"])+num(r["ev_yellow_away"]) for r in rs])
    out["cards"]["event_n"] = sum(num(r["ev_yellow_home"]) is not None for r in rs)
    return out

def team_series(rs,key,against=False):
    d=defaultdict(list)
    for r in rs:
        for side,other in (("home","away"),("away","home")):
            chosen=other if against else side
            k=f"{key}_{chosen}" if key != "goals" else None
            v=(num(r[f"{chosen}_goals"]) if key=="goals" else num(r[k]))
            if v is not None: d[(r[f"{side}_id"],r["season"])].append(v)
    return d
def split_reliability(rs,key,minimum=8):
    x=[];y=[]; n=0
    for sequence in team_series(rs,key).values():
        if len(sequence)<minimum: continue
        a,b=sequence[::2],sequence[1::2]
        if a and b: x.append(sum(a)/len(a)); y.append(sum(b)/len(b)); n+=1
    return {"r":corr(x,y),"n_team_seasons":n,"min_matches":minimum}
def reliability(rs):
    spec=["goals","ShotsOnTarget","corners","total_shots","yellow_cards","fouls","touches_opp_box"]
    out={}
    for key in spec:
        label=key if key=="goals" else key
        out[f"{label}_for"]=split_reliability(rs,key)
        d=defaultdict(list)
        for r in rs:
            for side,other in (("home","away"),("away","home")):
                v=num(r[f"{key}_{other}"]) if key != "goals" else num(r[f"{other}_goals"])
                if v is not None: d[(r[f"{side}_id"],r["season"])].append(v)
        x=[];y=[];n=0
        for a in d.values():
            if len(a)>=8:
                x.append(mean(a[::2])); y.append(mean(a[1::2])); n+=1
        out[f"{label}_against"]={"r":corr(x,y),"n_team_seasons":n,"min_matches":8}
    # Event yellows are a separate target, not a substitute for the stats target.
    d=defaultdict(list)
    for r in rs:
        for side in ("home","away"): d[(r[f"{side}_id"],r["season"])].append(num(r[f"ev_yellow_{side}"]))
    x=[];y=[];n=0
    for a in d.values():
        if len(a)>=8:
            x.append(mean(a[::2]));y.append(mean(a[1::2]));n+=1
    out["event_yellow_for"]={"r":corr(x,y),"n_team_seasons":n,"min_matches":8}
    return out
def referee_rel(rs):
    d=defaultdict(list)
    for r in sorted(rs,key=lambda z:(z["referee"],z["date"],z["match_id"])):
        if r["referee"] and num(r["ev_yellow_home"]) is not None: d[r["referee"]].append(num(r["ev_yellow_home"])+num(r["ev_yellow_away"]))
    x=[];y=[];n=0
    for a in d.values():
        if len(a)>=8: x.append(mean(a[::2]));y.append(mean(a[1::2]));n+=1
    return {"r":corr(x,y),"n_referees_min8":n,"min_matches":8,"n_matches":sum(len(a) for a in d.values())}
def half(rs, fhkey, ftkey, event=False):
    shares=[]; first=[]; full=[]
    for r in rs:
        if event:
            fh=num(r[fhkey[0]])+num(r[fhkey[1]]); ft=num(r[ftkey[0]])+num(r[ftkey[1]])
        else: fh,ft=total(r,fhkey),total(r,ftkey)
        if fh is not None and ft is not None and ft>0: shares.append(fh/ft);first.append(fh);full.append(ft)
    if not shares:return {"n":0,"share_1h":None,"observed_variance":None,"noise_expectation":None,"true_variance":None}
    p=sum(first)/sum(full); noise=mean([p*(1-p)/v for v in full]); obs=st.variance(shares) if len(shares)>1 else 0
    return {"n":len(shares),"share_1h":round(p,5),"observed_variance":round(obs,6),"noise_expectation":round(noise,6),"true_variance":round(obs-noise,6),"variance_ratio":round(obs/noise,3) if noise else None}

per_season={s:levels([r for r in ROWS if r["season"]==s]) for s in SEASONS}
for s in SEASONS: per_season[s]["teams_by_id"]=len({r[k] for r in ROWS if r["season"]==s for k in ("home_id","away_id")})
dev_stats=[r for r in ROWS if r["season"] in ("2023","2024","2025")]
blocks={"2021-2022":[r for r in ROWS if r["season"] in ("2021","2022")],"2023-2024":[r for r in ROWS if r["season"] in ("2023","2024")],"2025-2026":[r for r in ROWS if r["season"] in ("2025","2026")],"dev_2023-2025":dev_stats}
halves_stats={}
for name,key in (("sot","ShotsOnTarget"),("corners","corners"),("total_shots","total_shots"),("yellow_cards","yellow_cards"),("fouls","fouls"),("touches_opp_box","touches_opp_box")):
    halves_stats[name]=half([r for r in ROWS if r["season"] in ("2023","2024","2025","2026") and r["has_splits"]=="1"],f"fh_{key}",key)
halves_stats["goals_events_all_seasons"]=half(ROWS,("goals_1h_home","goals_1h_away"),("home_goals","away_goals"),True)
halves_stats["yellow_cards_events_all_seasons"]=half(ROWS,("ev_yellow_1h_home","ev_yellow_1h_away"),("ev_yellow_home","ev_yellow_away"),True)
cards_compare={}
for s in SEASONS:
    rs=[r for r in ROWS if r["season"]==s]; pairs=[(total(r,"yellow_cards"),num(r["ev_yellow_home"])+num(r["ev_yellow_away"])) for r in rs if total(r,"yellow_cards") is not None]
    cards_compare[s]={"n_both":len(pairs),"agreement_rate_pct":pct(sum(a==b for a,b in pairs),len(pairs)),"mean_stats_minus_events":mean([a-b for a,b in pairs]),"stats_total":sum(a for a,b in pairs),"events_total":sum(b for a,b in pairs)}
regime={}
for key in MARKETS:
    base=per_season["2021"][key]["mean"]
    regime[key]={s:{"mean":per_season[s][key]["mean"],"pct_vs_2021":round(100*(per_season[s][key]["mean"]-base)/base,2) if base and per_season[s][key]["mean"] is not None else None,"break_gt_10pct":bool(base and per_season[s][key]["mean"] is not None and abs(per_season[s][key]["mean"]-base)/base>0.1)} for s in SEASONS}
team_names=defaultdict(set)
for r in ROWS:
    team_names[str(r["home_id"])].add(r["home_name"]);team_names[str(r["away_id"])].add(r["away_name"])
renames={k:sorted(v) for k,v in team_names.items() if len(v)>1}
out={"seasons":SEASONS,"per_season":per_season,"reliability_by_block":{k:reliability(v) for k,v in blocks.items()},"referee_reliability_by_block":{k:referee_rel(v) for k,v in blocks.items()},"halves":halves_stats,"cards_stats_vs_events":cards_compare,"regime_break":regime,"team_renames":renames,"stats_conflicts":{"total":sum(int(r["stats_conflicts"]) for r in ROWS),"matches_with_conflict":sum(int(r["stats_conflicts"])>0 for r in ROWS)},"score_event_agreement_pct":pct(sum(r["score_event_agreement"]=="1" for r in ROWS),len(ROWS))}
(HERE/"eda_summary.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def md_table(rows, headers):
    s="| " + " | ".join(headers) + " |\n|"+"|".join("---" for _ in headers)+"|\n"
    return s+"\n".join("| "+" | ".join(str(x) for x in row)+" |" for row in rows)

inventory={"league":"China Super League","fotmob_league_id":120,"index_rows":len(ROWS),"seasons":{s:{"matches":len([r for r in ROWS if r["season"]==s]),"teams_by_id":per_season[s]["teams_by_id"],"date_range":[min(r["date"] for r in ROWS if r["season"]==s),max(r["date"] for r in ROWS if r["season"]==s)],"coverage":per_season[s]["coverage"]} for s in SEASONS},"phase_2021":Counter(r["phase"] for r in ROWS if r["season"]=="2021"),"format_history":{"2021":"two 8-team groups plus championship/relegation playoffs; 176","2022":"18-team double round-robin; 306","2023+":"16-team seasons; 240"},"team_rename_examples":dict(list(renames.items())[:30]),"quirks":{"2022_no_stats":sum(r["season"]=="2022" and r["has_stats"]=="0" for r in ROWS),"stats_conflicts_total":out["stats_conflicts"],"shotmap":"absent","expected_goals":"absent"}}
(HERE/"inventory_summary.json").write_text(json.dumps(inventory,indent=2,sort_keys=True)+"\n")
print(json.dumps({"seasons":{s:per_season[s]["matches"] for s in SEASONS},"cards":cards_compare,"score_agreement_pct":out["score_event_agreement_pct"]},indent=2))
