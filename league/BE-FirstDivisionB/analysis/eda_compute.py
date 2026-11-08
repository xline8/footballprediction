"""Phase A descriptive EDA; no model fitting."""
import csv,json,math,statistics as st
from collections import defaultdict,Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent; DATA=HERE.parent/"data"; MAIN=Path("/home/hatch/workspace/footballprediction"); IDX=MAIN/"data_enrichment/fotmob_world_index.csv"
SEASONS=["2021/2022","2022/2023","2023/2024","2024/2025","2025/2026","2026/2027"]; DEV=SEASONS[:4]; VIRGIN=SEASONS[4]
ROWS=list(csv.DictReader(open(DATA/"beb_matches.csv")))
def f(r,k):
 v=r.get(k); return None if v in ("",None,"None") else float(v)
def mean(x): return round(st.mean(x),4) if x else None
def cor(x,y):
 if len(x)<3:return None
 mx,my=st.mean(x),st.mean(y); d=math.sqrt(sum((z-mx)**2 for z in x)*sum((z-my)**2 for z in y)); return round(sum((a-mx)*(b-my) for a,b in zip(x,y))/d,4) if d else None
def raw(lid):
 out=[]
 for ix in csv.DictReader(open(IDX)):
  if ix["league_id"]!=str(lid):continue
  d=json.load(open(MAIN/ix["path"])); h=(d.get("header") or {}).get("status") or {}
  if h.get("finished"):
   q=(h.get("scoreStr") or "0-0").split("-");out.append((ix,d,int(q[0]),int(q[1])))
 return out
out={"n":len(ROWS),"row_counts":dict(Counter(r["season"] for r in ROWS)),"seasons":SEASONS}
per={}
for s in SEASONS:
 rs=[r for r in ROWS if r["season"]==s]; n=len(rs)
 def level(k):return mean([f(r,k+"_home")+f(r,k+"_away") for r in rs if f(r,k+"_home") is not None and f(r,k+"_away") is not None])
 hg=mean([int(r["home_goals"]) for r in rs]);ag=mean([int(r["away_goals"]) for r in rs])
 per[s]={"n":n,"teams":len({r["home_team_id"] for r in rs}|{r["away_team_id"] for r in rs}),"goals":mean([int(r["home_goals"])+int(r["away_goals"]) for r in rs]),"home_goals":hg,"away_goals":ag,"home_advantage":round(hg-ag,4),"sot":level("ShotsOnTarget"),"corners":level("corners"),"cards":level("yellow_cards"),"total_shots":level("total_shots"),"stats_cov_pct":round(100*sum(r["has_stats_all"]=="1" for r in rs)/n,1),"half_cov_pct":round(100*sum(r["has_stats_half"]=="1" for r in rs)/n,1),"shotmap_cov_pct":round(100*sum(r["has_shotmap"]=="1" for r in rs)/n,1),"events_cov_pct":round(100*sum(r["has_events"]=="1" for r in rs)/n,1),"ref_cov_pct":round(100*sum(bool(r["referee"]) for r in rs)/n,1),"stats_cards_cov_pct":round(100*sum(f(r,"yellow_cards_home") is not None for r in rs)/n,1),"phases":dict(Counter(r["phase"] for r in rs))}
out["per_season"]=per;out["team_counts_by_id"]={s:per[s]["teams"] for s in SEASONS}
out["reserve_ids"]=sorted({int(r["home_team_id"]) for r in ROWS if r["is_reserve_home"]=="1"}|{int(r["away_team_id"]) for r in ROWS if r["is_reserve_away"]=="1"})
out["reserve_names"]={str(i):sorted({r["home_team"] for r in ROWS if r["home_team_id"]==str(i)}|{r["away_team"] for r in ROWS if r["away_team_id"]==str(i)}) for i in out["reserve_ids"]}
def series(seasons,against):
 d=defaultdict(list)
 for r in ROWS:
  if r["season"] not in seasons:continue
  d[r["home_team_id"]].append(int(r["away_goals"] if against else r["home_goals"]));d[r["away_team_id"]].append(int(r["home_goals"] if against else r["away_goals"]))
 return d
out["goal_reliability_odd_even"]={}
for name,against in [("goals_for",False),("goals_against",True)]:
 a,b=series(["2021/2022","2023/2024"],against),series(["2022/2023","2024/2025"],against); ids=sorted(set(a)&set(b));out["goal_reliability_odd_even"][name]={"r":cor([st.mean(a[i]) for i in ids],[st.mean(b[i]) for i in ids]),"n_teams":len(ids)}
halves=[];diffs=[];dev_events=0
for ix,d,hg,ag in raw(264):
 evs=(((d.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
 if ix["season"] in DEV and evs:dev_events+=1
 if ix["season"] in DEV and evs and hg+ag:
  first=0
  for e in evs:
   if e.get("type")!="Goal" or e.get("isPenaltyShootoutEvent"):continue
   p=e.get("period") or (e.get("shotmapEvent") or {}).get("period"); first+=int(p=="FirstHalf" or (p is None and e.get("time") is not None and e["time"]<=45))
  halves.append((first/(hg+ag),hg+ag))
 if ix["season"]==VIRGIN and evs:
  stx={}
  for g in (((d.get("content") or {}).get("stats") or {}).get("Periods") or {}).get("All",{}).get("stats",[]) or []:
   for z in g.get("stats",[]) or []:stx[z.get("key")]=z.get("stats") or []
  y=stx.get("yellow_cards")
  if y and len(y)>1:
   plain=sum(e.get("type")=="Card" and e.get("card")=="Yellow" for e in evs);yr=sum(e.get("type")=="Card" and e.get("card")=="YellowRed" for e in evs);diffs.append((float(y[0])+float(y[1])-plain,float(y[0])+float(y[1])-plain-yr))
out["dev_event_matches"]=dev_events;m=st.mean(x for x,w in halves);noise=st.mean(m*(1-m)/w for x,w in halves);obs=st.variance(x for x,w in halves)
out["halves"]={"n":len(halves),"constant":round(sum(x*w for x,w in halves)/sum(w for x,w in halves),6),"observed_variance":round(obs,6),"binomial_noise":round(noise,6),"true_variance":round(obs-noise,6),"rule":"event period FirstHalf when present; otherwise minute <=45; no fabricated goals"}
out["cards_forensics"]={"n_both":len(diffs),"exact_agreement_pct":round(100*sum(x==0 for x,y in diffs)/len(diffs),4),"mean_stats_minus_plain_events":round(st.mean(x for x,y in diffs),4),"stats_lower_pct":round(100*sum(x<0 for x,y in diffs)/len(diffs),4),"stats_higher_pct":round(100*sum(x>0 for x,y in diffs)/len(diffs),4),"exact_agreement_pct_including_yellowred":round(100*sum(y==0 for x,y in diffs)/len(diffs),4),"yellowred_is_separate":True}
a=raw(40);aid=defaultdict(set);ameans=defaultdict(list)
for ix,d,hg,ag in a:
 g=d.get("general") or {};h=g.get("homeTeam",{});v=g.get("awayTeam",{});aid[ix["season"]]|={str(h.get("id")),str(v.get("id"))};ameans[ix["season"]].append((h,v,hg,ag))
bid={s:{r["home_team_id"] for r in ROWS if r["season"]==s}|{r["away_team_id"] for r in ROWS if r["season"]==s} for s in SEASONS}
def teammean(rs,tid):
 gf=[];ga=[]
 for r in rs:
  if r["home_team_id"]==tid:gf.append(int(r["home_goals"]));ga.append(int(r["away_goals"]))
  elif r["away_team_id"]==tid:gf.append(int(r["away_goals"]));ga.append(int(r["home_goals"]))
 return mean(gf),mean(ga),len(gf)
def amean(rs,tid):
 gf=[];ga=[]
 for h,v,hg,ag in rs:
  if str(h.get("id"))==tid:gf.append(hg);ga.append(ag)
  elif str(v.get("id"))==tid:gf.append(ag);ga.append(hg)
 return mean(gf),mean(ga),len(gf)
movers=[];new=[]
for s,p in [("2022/2023","2021/2022"),("2023/2024","2022/2023"),("2024/2025","2023/2024")]:
 for tid in sorted(bid[s]-bid[p]):
  name=next((r["home_team"] for r in ROWS if r["season"]==s and r["home_team_id"]==tid),next(r["away_team"] for r in ROWS if r["season"]==s and r["away_team_id"]==tid))
  if tid in aid[p]:movers.append({"entry_season":s,"team_id":tid,"team":name,"b":teammean([r for r in ROWS if r["season"]==s],tid),"a":amean(ameans[p],tid)})
  else:new.append({"entry_season":s,"team_id":tid,"team":name,"reserve":int(int(tid) in out["reserve_ids"])})
for z in movers:
 s=z["entry_season"];p={"2022/2023":"2021/2022","2023/2024":"2022/2023","2024/2025":"2023/2024"}[s];br=[r for r in ROWS if r["season"]==s];ar=ameans[p];bm=mean([int(r["home_goals"])+int(r["away_goals"]) for r in br]);am=mean([hg+ag for h,v,hg,ag in ar]);z["b_gap"]=(round(z["b"][0]-bm/2,4),round(z["b"][1]-bm/2,4));z["a_gap"]=(round(z["a"][0]-am/2,4),round(z["a"][1]-am/2,4))
out["movers"]=movers;out["new_entries"]=new;out["mover_pooled"]={"n":len(movers),"b_gf_gap":mean([z["b_gap"][0] for z in movers]),"b_ga_gap":mean([z["b_gap"][1] for z in movers]),"a_gf_gap":mean([z["a_gap"][0] for z in movers]),"a_ga_gap":mean([z["a_gap"][1] for z in movers])}
out["count_levels_virgin"]={k:per[VIRGIN][k] for k in ("sot","corners","cards","total_shots")}
json.dump(out,open(HERE/"eda_summary.json","w"),indent=2)
print(json.dumps({"row_counts":out["row_counts"],"coverage":per,"halves":out["halves"],"movers":movers,"mover_pooled":out["mover_pooled"],"cards_forensics":out["cards_forensics"]},indent=2))

