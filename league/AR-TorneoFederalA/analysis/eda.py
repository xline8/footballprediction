"""Phase-A descriptive analysis; 2026 is inventory-only and never enters EDA."""
from __future__ import annotations
import csv, json, math, statistics
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent; DATA=HERE.parent/"data"/"feda_matches.csv"
EDA_SEASONS=["2021","2022","2023","2024","2025"]

def f(x): return float(x) if x not in ("",None,"nan","NaN") else math.nan
def pct(xs): return round(100*sum(xs)/len(xs),3) if xs else None
def mean(xs): return round(float(np.mean(xs)),5) if xs else None
def levels(rows):
    out={}
    for s in EDA_SEASONS:
        q=[r for r in rows if r["season"]==s]
        def lev(z):
            return {"n":len(z),"goals_per_match":mean([f(r["home_goals"])+f(r["away_goals"]) for r in z]),"home_goals":mean([f(r["home_goals"]) for r in z]),"away_goals":mean([f(r["away_goals"]) for r in z]),"home_win_pct":pct([f(r["home_goals"])>f(r["away_goals"]) for r in z]),"draw_pct":pct([f(r["home_goals"])==f(r["away_goals"]) for r in z])}
        out[s]={"overall":lev(q),"by_phase":{p:lev([r for r in q if r["phase"]==p]) for p in ("first","promotion","relegation")}}
    return out

def split_reliability(rows,key):
    teams=defaultdict(list)
    for r in rows:
        for side,tid,sign in (("home",r["home_team_id"],1),("away",r["away_team_id"],-1)):
            val=(f(r["home_goals"]) if side=="home" else f(r["away_goals"])) if key=="home_goals" else (f(r["away_goals"]) if side=="home" else f(r["home_goals"])) if key=="away_goals" else f(r[key+"_home"] if side=="home" else r[key+"_away"])
            against=f(r["away_goals"] if key=="goals" and side=="home" else r["home_goals"] if key=="goals" else "")
            teams[(r["season"],tid)].append((r["date"],val,against))
    vals=[]
    for _,q in teams.items():
        q.sort(); n=len(q)
        if n<8: continue
        a=q[:n//2]; b=q[n//2:]
        vals.append((sum(x[1] for x in a)/len(a),sum(x[1] for x in b)/len(b)))
    return {"n_team_seasons":len(vals),"split_half_r":round(float(np.corrcoef(np.array(vals).T)[0,1]),5) if len(vals)>2 else None}

def halves(rows):
    q=[r for r in rows if r["ht_source"]=="events"]
    shares=[]
    num=0.0; den=0.0
    for r in q:
        ft=f(r["home_goals"])+f(r["away_goals"]); h=f(r["ht_home_goals"])+f(r["ht_away_goals"])
        num+=h; den+=ft
        if ft: shares.append(h/ft)
    # Program convention (BNAC/AR/J1): the frozen constant is the RATIO OF SUMS,
    # not the mean of per-match shares. Variance diagnostics still use per-match shares.
    p=num/den if den else None; var=float(np.var(shares,ddof=1)); noise=float(np.mean([p*(1-p)/max(1,(f(r["home_goals"])+f(r["away_goals"]))) for r in q if f(r["home_goals"])+f(r["away_goals"])>0]))
    return {"n_matches_with_event_halves":len(q),"n_nonzero_goal_matches":len(shares),"share_1h":round(p,6),"variance":round(var,8),"noise_floor":round(noise,8),"variance_minus_noise":round(var-noise,8),"frozen_constant_pass":bool(var<=noise)}

def movers(rows):
    by=defaultdict(list)
    for r in rows:
        for side in ("home","away"):
            tid=r[side+"_team_id"]; by[(r["season"],tid)].append((f(r[side+"_goals"]),f(r["away_goals"] if side=="home" else r["home_goals"])))
    # Same-corpus prior-season newcomer blocks; Nacional membership is cross-checked by ids from its payload index.
    nat=Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")
    natids=defaultdict(set)
    if nat.exists():
        with nat.open() as fh:
            for ir in csv.DictReader(fh):
                if ir.get("league_id")!="8965": continue
                p=Path("/home/hatch/workspace/footballprediction")/ir["path"]
                try:
                    x=json.loads(p.read_text()); natids[ir["season"]].update(str(t.get("id")) for t in (x.get("header") or {}).get("teams") or [])
                except FileNotFoundError: pass
    out=[]; season_mean={}
    for s in ("2022","2023","2024","2025"):
        blocks=[v for (ss,_),v in by.items() if ss==s]
        season_mean[s]=(sum(x[0] for v in blocks for x in v)/sum(len(v) for v in blocks),sum(x[1] for v in blocks for x in v)/sum(len(v) for v in blocks))
        current={tid for ss,tid in by if ss==s}; prior={tid for ss,tid in by if ss==str(int(s)-1)}
        for tid in sorted(current-prior):
            q=by[(s,tid)]; direction="from_nacional" if tid in natids.get(str(int(s)-1),set()) else "from_below_or_cross_competition"
            out.append({"season":s,"team_id":tid,"direction":direction,"n_matches":len(q),"gf_gap":round(sum(x[0] for x in q)/len(q)-season_mean[s][0],5),"ga_gap":round(sum(x[1] for x in q)/len(q)-season_mean[s][1],5)})
    # Pooled magnitudes are TEAM-BLOCK means (BNAC/AR F4 convention: one
    # observation per newcomer team-season), NOT match-weighted means.
    pooled={"n_team_blocks":len(out),
            "gf_gap":round(sum(x["gf_gap"] for x in out)/len(out),5) if out else None,
            "ga_gap":round(sum(x["ga_gap"] for x in out)/len(out),5) if out else None,
            "by_direction":{d:{"n":sum(1 for x in out if x["direction"]==d),
                               "gf_gap":round(sum(x["gf_gap"] for x in out if x["direction"]==d)/max(1,sum(1 for x in out if x["direction"]==d)),5),
                               "ga_gap":round(sum(x["ga_gap"] for x in out if x["direction"]==d)/max(1,sum(1 for x in out if x["direction"]==d)),5)} for d in ("from_nacional","from_below_or_cross_competition")}}
    return {"blocks":out,"pooled_2022_2025":pooled,"pooled_by_direction":pooled["by_direction"]}

def main():
    with DATA.open(newline="",encoding="utf-8") as fh: allrows=list(csv.DictReader(fh))
    rows=[r for r in allrows if r["season"] in EDA_SEASONS]
    inv={"group_rows":len(allrows),"group_by_season":{s:sum(r["season"]==s for r in allrows) for s in ("2021","2022","2023","2024","2025","2026")},"index_rows_federal_a":3219,"excluded_rows":227,"stats_nonempty":0,"shots_any":0,"referee_nonempty":0}
    inv.update({s:{"n_matches":sum(r["season"]==s for r in allrows),"distinct_teams":len({r["home_team_id"] for r in allrows if r["season"]==s}|{r["away_team_id"] for r in allrows if r["season"]==s}),"date_range":[min(r["date"] for r in allrows if r["season"]==s),max(r["date"] for r in allrows if r["season"]==s)]} for s in EDA_SEASONS})
    inv["2026"]={"n_matches":459,"virgin":True,"completeness_basis":"group-phase inventory count only; no outcomes used"}
    summary={"scope":{"eda_seasons":EDA_SEASONS,"virgin_excluded":"2026; no descriptive statistics computed"},"seasons":levels(rows),"pooled":levels(rows),"home_advantage":{"overall":pct([f(r["home_goals"])>f(r["away_goals"]) for r in rows]),"by_phase":{p:pct([f(r["home_goals"])>f(r["away_goals"]) for r in rows if r["phase"]==p]) for p in ("first","promotion","relegation")}},"reliability":{"goals_for":split_reliability(rows,"home_goals"),"goals_against":split_reliability(rows,"away_goals")},"halves_goals":halves(rows),"referee":{"coverage_pct":0.0,"adopt":False},"movers":movers(rows),"primary_lines":{"OU1.5":pct([f(r["home_goals"])+f(r["away_goals"] )>1.5 for r in rows]),"OU2.5":pct([f(r["home_goals"])+f(r["away_goals"] )>2.5 for r in rows]),"OU3.5":pct([f(r["home_goals"])+f(r["away_goals"] )>3.5 for r in rows])},"absent":{"stats_payloads_nonempty":0,"shotmap_shots":0,"sot":0,"corners":0,"yellow_cards":0,"total_shots":0,"xg":0}}
    (HERE/"inventory_summary.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False)+"\n")
    (HERE/"eda_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
    print(json.dumps(summary["primary_lines"],indent=2))
if __name__=="__main__": main()
