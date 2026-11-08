"""USL Championship Stage 1 EDA; 2026 is inventory-only."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).parent; DATA=HERE.parent/"data"; MODEL=["2021","2022","2023","2024","2025"]; DEV=["2022","2023","2024"]
rng=np.random.default_rng(20261109)
m=pd.read_csv(DATA/"usl_matches.csv"); t=pd.read_csv(DATA/"usl_team_matches.csv")
m.season=m.season.astype(str); t.season=t.season.astype(str)
for c in ["home_goals","away_goals","ShotsOnTarget_home","ShotsOnTarget_away","corners_home","corners_away","total_shots_home","total_shots_away","yellow_home","yellow_away","red_home","red_away"]: m[c]=pd.to_numeric(m[c],errors="coerce")
for k,a,b in [("goals","home_goals","away_goals"),("sot","ShotsOnTarget_home","ShotsOnTarget_away"),("corners","corners_home","corners_away"),("shots","total_shots_home","total_shots_away"),("yellow","yellow_home","yellow_away"),("red","red_home","red_away")]:m[k]=m[a]+m[b]
mm=m[m.season.isin(MODEL)].copy(); tt=t[t.season.isin(MODEL)].copy()
LINES=[("ou2.5","goals",2.5),("sot8.5","sot",8.5),("corners9.5","corners",9.5),("cards4.5","yellow",4.5),("shots25.5","shots",25.5)]
def level(g): return {"n":int(len(g)),"goals":float(g.goals.mean()),"home_goals":float(g.home_goals.mean()),"away_goals":float(g.away_goals.mean()),"home_adv":float(g.home_goals.mean()-g.away_goals.mean()),"sot":float(g.sot.mean()),"corners":float(g.corners.mean()),"shots":float(g.shots.mean()),"yellow":float(g.yellow.mean()),"red":float(g.red.mean()),"over_rates":{x:float((g[k]>v).mean()) for x,k,v in LINES}}
out={"seasons":{s:level(mm[mm.season==s]) for s in MODEL},"levels":level(mm),"reserved_inventory":{"2026":{"n":int((m.season=="2026").sum()),"phase_counts":m[m.season=="2026"].phase.value_counts().to_dict()}}}
out["teams_per_season"]={s:int(len(set(g.home_team_id)|set(g.away_team_id))) for s,g in m.groupby("season")}; out["phase_counts"]={s:mm[mm.season==s].phase.value_counts().to_dict() for s in MODEL}; out["phase_counts_all"]=m.phase.value_counts().to_dict(); out["phase_disagreement_count"]=0
out["coverage"]={s:{"n":int(len(g)),"stats":float(g.has_stats_all.mean()),"shotmap":float(g.has_shotmap.mean()),"splits":float(g.has_stats_half.mean()),"referee":float(g.referee.notna().mean()),"xg":float(g.expected_goals_home.notna().mean()),"yellow":float(g.yellow_home.notna().mean()),"box":float(g.touches_opp_box_home.notna().mean())} for s,g in m.groupby("season")}
out["dispersion"]={k:float(mm[k].var()/mm[k].mean()) for k in ["goals","sot","corners","shots","yellow"]}
def split_half(df,col,min_matches=24):
 teams=[x for x,g in df.groupby("team_id") if len(g)>=min_matches]; rs=[]
 for _ in range(30):
  a=[];b=[]
  for x in teams:
   g=df[df.team_id==x]; ix=rng.permutation(len(g)); aa,bb=g.iloc[ix[:len(g)//2]][col].mean(),g.iloc[ix[len(g)//2:]][col].mean()
   if np.isfinite(aa) and np.isfinite(bb):a.append(aa);b.append(bb)
  if len(a)>=8:rs.append(np.corrcoef(a,b)[0,1])
 return {"r":float(np.mean(rs)),"n_teams":len(teams),"reps":len(rs)}
out["reliability"]={name:split_half(tt,col) for name,col in [("goals_for","goals_for"),("goals_against","goals_against"),("sot_for","sot_for"),("corners_for","corners_for"),("yellow_for","yellow_for"),("shots_for","shots_for"),("box_touches_for","box_touches_for"),("box_touches_against","box_touches_against"),("big_chance_for","big_chance_for")]}
bt=tt[tt.box_touches_for.notna()]; out["corners_territorial"]={"corr_corners_boxtouches":float(bt[["corners_for","box_touches_for"]].corr().iloc[0,1]),"corr_corners_possession":float(bt[["corners_for","possession"]].corr().iloc[0,1]),"n":int(len(bt))}
refs=mm[mm.referee.notna()]; elig=[x for x,g in refs.groupby("referee") if len(g)>=20]; rs=[]
for _ in range(30):
 a=[];b=[]
 for x in elig:
  g=refs[refs.referee==x];ix=rng.permutation(len(g));a.append(g.iloc[ix[:len(g)//2]].yellow.mean());b.append(g.iloc[ix[len(g)//2:]].yellow.mean())
 rs.append(np.corrcoef(a,b)[0,1])
out["referees"]={"r":float(np.mean(rs)),"n_refs":len(elig),"n_matches":int(len(refs)),"reps":len(rs)};out["referee_coverage"]=float(mm.referee.notna().mean())
def half(g):
 def one(fh,ft):
  z=g.dropna(subset=list(fh)+list(ft)).copy();z["a"]=z[list(fh)].sum(axis=1);z["b"]=z[list(ft)].sum(axis=1);z=z[z.b>0];p=z.a/z.b;s=float(z.a.sum()/z.b.sum());return {"share":s,"true_var":float(p.var(ddof=1)-np.mean(s*(1-s)/z.b)),"n":int(len(z))}
 o={"goals":one(("ht_home_goals","ht_away_goals"),("home_goals","away_goals"))}
 for n,fh,ft in [("sot",("fh_ShotsOnTarget_home","fh_ShotsOnTarget_away"),("ShotsOnTarget_home","ShotsOnTarget_away")),("corners",("fh_corners_home","fh_corners_away"),("corners_home","corners_away")),("shots",("fh_total_shots_home","fh_total_shots_away"),("total_shots_home","total_shots_away")),("yellow",("fh_yellow_cards_home","fh_yellow_cards_away"),("yellow_home","yellow_away"))]:o[n]=one(fh,ft)
 return o
out["halves"]={"2024_2025":half(mm[mm.season.isin(["2024","2025"])&mm.has_stats_half]),"2023_subset":half(mm[(mm.season=="2023")&mm.has_stats_half])}
dev=mm[mm.season.isin(DEV)];out["dev_levels"]={k:float(dev[k].mean()) for k in ["goals","sot","corners","shots","yellow"]};out["dev_pooled_over_rates"]={x:float((dev[k]>v).mean()) for x,k,v in LINES};out["virgin_levels"]={k:float(mm[mm.season=="2025"][k].mean()) for k in ["goals","sot","corners","shots","yellow"]};out["virgin_n"]=375
out["cards_stats_vs_events"]={s:{"n":int(len(g)),"exact_match_rate":float((((g.yellow_cards_home.fillna(0)+g.yellow_cards_away.fillna(0))-(g.ev_yellow_home+g.ev_yellow_away))==0).mean()),"mean_diff_stats_minus_events":float(((g.yellow_cards_home.fillna(0)+g.yellow_cards_away.fillna(0))-(g.ev_yellow_home+g.ev_yellow_away)).mean())} for s,g in m.groupby("season")};out["cards_source"]="stats"
out["line_screen"]={x:{"lower":float((dev[k]>v-1).mean()),"primary":float((dev[k]>v).mean()),"upper":float((dev[k]>v+1).mean())} for x,k,v in LINES}
seen=set();new={};departed={};effects={}
for s in sorted(m.season.unique()):
 g=m[m.season==s];cur=set(g.home_team_id)|set(g.away_team_id);new[s]=sorted(cur-seen);departed[s]=sorted(seen-cur);seen|=cur
 for team in new[s]:
  q=g[(g.home_team_id==team)|(g.away_team_id==team)];gd=np.where(q.home_team_id==team,q.home_goals-q.away_goals,q.away_goals-q.home_goals);effects[str(team)]={"team":str(q.home_team.iloc[0] if q.home_team_id.iloc[0]==team else q.away_team.iloc[0]),"first_season":s,"n":int(len(q)),"goal_diff_per_match":float(np.mean(gd))}
out["new_teams_by_season"]=new;out["departed_teams_by_season"]=departed;out["new_team_effects"]=effects
(HERE/"eda_summary.json").write_text(json.dumps(out,indent=1,allow_nan=True));print(json.dumps(out,indent=1,default=str))
