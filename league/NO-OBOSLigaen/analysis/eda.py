"""Phase-A descriptive EDA; no fitting or gate evaluation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).parent
m=pd.read_csv(HERE.parent/"data/no_obos_matches.csv",dtype={"season":str},parse_dates=["date"])
t=pd.read_csv(HERE.parent/"data/no_obos_team_matches.csv",dtype={"season":str},parse_dates=["date"])
rng=np.random.default_rng(20261110)
for c in ["home_goals","away_goals"]: m[c]=pd.to_numeric(m[c],errors="coerce")
m["goals"]=m.home_goals+m.away_goals; m["sot"]=m.ShotsOnTarget_home+m.ShotsOnTarget_away; m["corners"]=m.corners_home+m.corners_away; m["shots"]=m.total_shots_home+m.total_shots_away; m["yellow"]=m.yellow_home+m.yellow_away
out={"seasons":{}}
for s,g in m.groupby("season"):
    out["seasons"][s]={"n":int(len(g)),"first":str(g.date.min().date()),"last":str(g.date.max().date()),"teams":int(len(set(g.home_team_id)|set(g.away_team_id))),"goals":float(g.goals.mean()),"home_goals":float(g.home_goals.mean()),"away_goals":float(g.away_goals.mean()),"home_win":float((g.home_goals>g.away_goals).mean()),"draw":float((g.home_goals==g.away_goals).mean()),"sot":float(g.sot.mean()),"corners":float(g.corners.mean()),"shots":float(g.shots.mean()),"yellow":float(g.yellow.mean())}
out["levels"]={k:float(m[k].mean()) for k in ["goals","sot","corners","shots","yellow"]}; out["home_advantage"]=float(m.home_goals.mean()-m.away_goals.mean()); out["dispersion"]={k:float(m[k].var()/m[k].mean()) for k in ["goals","sot","corners","shots","yellow"]}
out["coverage"]={s:{"n":int(len(g)),"stats_block":int(g.has_stats_block.sum()),"stats_keys":int(g.has_stats_all.sum()),"events":int(g.has_events.sum()),"referee":int(g.referee.notna().sum()),"shotmap":int(g.has_shotmap.sum()),"awarded":int(g.awarded.sum()),"ht_events":int((g.ht_source=="events").sum())} for s,g in m.groupby("season")}
out["keyless_stats_block_2026"]=[{"match_id":int(x.match_id),"date":str(x.date.date()),"home_team":x.home_team,"away_team":x.away_team} for _,x in m[(m.season=="2026") & m.has_stats_block & ~m.has_stats_all].iterrows()]
out["stats_index_content"]={"index_has_stats":{"2021":149,"2022":240,"2023":240,"2024":240,"2025":239,"2026":240},"content_has_four_keys":{s:int(g.has_stats_all.sum()) for s,g in m.groupby("season")}}
out["integrity"]={"rows":int(len(m)),"unique_ids":int(m.match_id.nunique()),"score_event_mismatch":int(m.score_events_mismatch.sum()),"card_yellow":int(m.ev_yellow_home.sum()+m.ev_yellow_away.sum()),"card_yellowred":int(m.ev_yellowred_home.sum()+m.ev_yellowred_away.sum()),"card_red":int(m.ev_red_home.sum()+m.ev_red_away.sum())}

def split_half(df,col,min_matches=24,reps=30):
    grouped={x:g[col].to_numpy(dtype=float) for x,g in df.groupby("team_id")}; teams=[x for x,g in grouped.items() if len(g)>=min_matches]; rs=[]
    for _ in range(reps):
        a=[];b=[]
        for tid in teams:
            g=grouped[tid]; ix=rng.permutation(len(g)); a.append(g[ix[:len(g)//2]].mean()); b.append(g[ix[len(g)//2:]].mean())
        rs.append(np.corrcoef(a,b)[0,1])
    return {"r":float(np.mean(rs)),"n_teams":len(teams),"reps":reps}
out["reliability"]={c:split_half(t,c) for c in ["goals_for","goals_against","sot_for","sot_against","corners_for","corners_against","shots_for","shots_against","yellow_for","yellow_against","possession","possession_against"]}
mm=m[m.referee.notna()]; refs=[x for x,g in mm.groupby("referee") if len(g)>=20]; rr=[]
for _ in range(30):
    a=[];b=[]
    for ref in refs:
        g=mm[mm.referee==ref]; ix=rng.permutation(len(g)); a.append(g.iloc[ix[:len(g)//2]].yellow.mean()); b.append(g.iloc[ix[len(g)//2:]].yellow.mean())
    rr.append(np.corrcoef(a,b)[0,1])
rr2=[]; rng2=np.random.default_rng(20261111)
for _ in range(30):
    a=[];b=[]
    for ref in refs:
        g=mm[mm.referee==ref]; ix=rng2.permutation(len(g)); a.append(g.iloc[ix[:len(g)//2]].yellow.mean()); b.append(g.iloc[ix[len(g)//2:]].yellow.mean())
    rr2.append(np.corrcoef(a,b)[0,1])
out["referee_reliability"]={"r":float(np.mean(rr)),"r_second_seed":float(np.mean(rr2)),"seed":20261110,"second_seed":20261111,"n_refs":len(refs),"matches":int(len(mm))}
def half_stat(fh,ft):
    g=m.dropna(subset=[fh,ft]); g=g[g[ft]>0]; p=g[fh]/g[ft]; share=float(g[fh].sum()/g[ft].sum()); floor=float(np.mean(share*(1-share)/g[ft])); return {"share":share,"observed_var":float(p.var(ddof=1)),"binomial_floor":floor,"true_var":float(p.var(ddof=1)-floor),"n":int(len(g))}
m["card_fh"]=m.ev_yellow_fh_home+m.ev_yellowred_fh_home+m.ev_yellow_fh_away+m.ev_yellowred_fh_away; m["card_ft"]=m.yellow; m["goal_fh"]=m.ht_home_goals+m.ht_away_goals; m["goal_ft"]=m.goals; out["halves"]={"goals":half_stat("goal_fh","goal_ft"),"cards":half_stat("card_fh","card_ft")}
parent=Path.home()/"workspace/footballprediction/league/NO-Eliteserien/data/no_matches.csv"; pm=pd.read_csv(parent,dtype={"season":str}); entry=[]; below={}
for s in ["2022","2023","2024","2025","2026"]:
    prev=str(int(s)-1); ob=set(m[m.season==s].home_team_id)|set(m[m.season==s].away_team_id); prior_ob=set(m[m.season==prev].home_team_id)|set(m[m.season==prev].away_team_id); elite=set(pm[pm.season==prev].home_team_id)|set(pm[pm.season==prev].away_team_id); entrants=ob-prior_ob; ent=entrants&elite; g=m[m.season==s]; vals=[]
    for tid in ent:
        x=g[(g.home_team_id==tid)|(g.away_team_id==tid)]; gf=sum(np.where(x.home_team_id==tid,x.home_goals,x.away_goals)); ga=sum(np.where(x.home_team_id==tid,x.away_goals,x.home_goals)); vals.append((gf/len(x),ga/len(x)))
    entry.append({"season":s,"count":len(ent),"entrants":len(entrants),"gf_per_match":float(np.mean([x[0] for x in vals])) if vals else None,"ga_per_match":float(np.mean([x[1] for x in vals])) if vals else None}); below[s]=int(len(entrants-ent))
out["movers"]={"from_eliteserien":entry,"from_below_count":below,"pooled_gf":float(np.mean([x["gf_per_match"] for x in entry if x["gf_per_match"] is not None])),"pooled_ga":float(np.mean([x["ga_per_match"] for x in entry if x["ga_per_match"] is not None])),"league_mean_team_goals":float(m.goals.mean()/2)}
dev=m[m.season.isin(["2022","2023","2024","2025"])]
out["dev_levels"]={k:float(dev[k].mean()) for k in ["goals","sot","corners","shots","yellow"]}; rates={"goals":[2.5],"sot":[8.5,9.5],"corners":[9.5,10.5],"yellow":[2.5,3.5],"shots":[20.5,21.5,22.5,23.5,24.5,25.5,26.5]}; out["primary_lines"]={k:{str(x):float(dev.loc[dev[k].notna(),k].gt(x).mean()) for x in xs} for k,xs in rates.items()}; out["primary_lines_n"]={k:int(dev[k].notna().sum()) for k in rates}; out["xg"]="not measurable: no expected_goals key in OBOS stats feed"
(HERE/"eda_summary.json").write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
