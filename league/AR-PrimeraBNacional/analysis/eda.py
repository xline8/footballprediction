"""Phase-A EDA for BNAC.  Deliberately excludes 2026 from every statistic."""
from __future__ import annotations
import csv, json, math, unicodedata
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; DATA = HERE.parent / "data"
M = list(csv.DictReader((DATA / "bnac_matches.csv").open(encoding="utf-8")))
T = list(csv.DictReader((DATA / "team_matches.csv").open(encoding="utf-8")))
EDA_SEASONS = ["2021", "2022", "2023", "2024", "2025"]
DEV = [r for r in M if r["season"] in EDA_SEASONS]

def f(r, k):
    try: return float(r.get(k, ""))
    except (TypeError, ValueError): return np.nan
def finite(a): return np.asarray(a, float)[np.isfinite(a)]
def mean(a):
    z = finite(a); return float(np.mean(z)) if len(z) else None
def ratio(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); z = np.isfinite(a)&np.isfinite(b)
    return float(np.sum(a[z])/np.sum(b[z])) if np.sum(b[z]) else None
def corr(a, b):
    a,b=np.asarray(a,float),np.asarray(b,float); z=np.isfinite(a)&np.isfinite(b)
    return float(np.corrcoef(a[z],b[z])[0,1]) if z.sum()>2 and np.std(a[z]) and np.std(b[z]) else None
def disp(a):
    z=finite(a); return float(np.var(z,ddof=1)/np.mean(z)) if len(z)>1 and np.mean(z) else None
def pct(a): return 100*float(np.mean(np.asarray(a, float)))

def levels(rs):
    g=np.array([f(r,"hg")+f(r,"ag") for r in rs]); h=np.array([f(r,"hg") for r in rs]); a=np.array([f(r,"ag") for r in rs])
    y=np.array([f(r,"yellow_home")+f(r,"yellow_away") for r in rs])
    reds=np.array([f(r,"red_home")+f(r,"red_away")+f(r,"yellowred_home")+f(r,"yellowred_away") for r in rs])
    return {"n_matches":len(rs),"goals_per_match":mean(g),"home_goals":mean(h),"away_goals":mean(a),
      "home_draw_away_pct":[pct(h>a),pct(h==a),pct(h<a)],"btts_pct":pct((h>0)&(a>0)),
      "over_1_5_pct":pct(g>1.5),"over_2_5_pct":pct(g>2.5),"over_3_5_pct":pct(g>3.5),
      "yellows_per_match":mean(y),"reds_per_match":mean(reds),
      "dispersion_var_mean":{"goals":disp(g),"yellows":disp(y)}}

def split_r(groups, fn, min_matches=24, seed=8965):
    rng=np.random.default_rng(seed); vals=[]
    for _ in range(60):
        x=[];y=[]
        for z in groups.values():
            a=np.asarray([fn(q) for q in z],float); a=a[np.isfinite(a)]
            if len(a)<min_matches: continue
            ix=rng.permutation(len(a)); n=len(a)//2; x.append(np.mean(a[ix[:n]])); y.append(np.mean(a[ix[n:]]))
        q=corr(x,y)
        if q is not None: vals.append(q)
    odd=[];even=[]
    for z in groups.values():
        a=np.asarray([fn(q) for q in z],float); a=a[np.isfinite(a)]
        if len(a)>=min_matches: odd.append(np.mean(a[::2])); even.append(np.mean(a[1::2]))
    return {"r":mean(vals),"n_splits":len(vals),"career_pooled_teams":len(odd),"odd_even_r":corr(odd,even)}

def split_ratio(groups, num, den, min_matches=24):
    def fn(q):
        u,v=f(q,num),f(q,den); return u/v if np.isfinite(u) and np.isfinite(v) and v>0 else np.nan
    # ratio of sums inside every split, not average of row ratios
    rng=np.random.default_rng(8965); vals=[]
    for _ in range(60):
        x=[];y=[]
        for z in groups.values():
            a=[(f(q,num),f(q,den)) for q in z if np.isfinite(f(q,num)) and np.isfinite(f(q,den)) and f(q,den)>0]
            if len(a)<min_matches: continue
            ix=rng.permutation(len(a)); n=len(a)//2
            x.append(sum(a[i][0] for i in ix[:n])/sum(a[i][1] for i in ix[:n])); y.append(sum(a[i][0] for i in ix[n:])/sum(a[i][1] for i in ix[n:]))
        q=corr(x,y)
        if q is not None: vals.append(q)
    return {"r":mean(vals),"n_splits":len(vals),"method":"ratio_of_sums"}

def coverage(rs):
    return {"events_pct":pct([r["has_events"]=="True" for r in rs]),
            "referee_pct":pct([bool(r["referee"]) for r in rs]),
            "stats_nonempty_pct":0.0,"shotmap_nonempty_pct":0.0,
            "period_splits":"none"}

def halves(rs, num_h, num_a, den_h, den_a, complete_only=True):
    z=[]
    for r in rs:
        n,d=f(r,num_h)+f(r,num_a),f(r,den_h)+f(r,den_a)
        if np.isfinite(n) and np.isfinite(d) and d>0: z.append((n,d))
    p=sum(x for x,_ in z)/sum(y for _,y in z) if z else None
    shares=np.array([x/y for x,y in z]); floor=float(np.mean(p*(1-p)/np.array([y for _,y in z]))) if z else None
    groups=defaultdict(list)
    for r in rs:
        n,d=f(r,num_h)+f(r,num_a),f(r,den_h)+f(r,den_a)
        if np.isfinite(n) and np.isfinite(d) and d>0:
            groups[r["home_id"]].append(n/d); groups[r["away_id"]].append(n/d)
    g={k:[{"v":x} for x in v] for k,v in groups.items() if len(v)>=24}
    return {"n_matches":len(z),"share_1h":p,"observed_variance":float(np.var(shares,ddof=1)),"noise_floor_per_match":floor,
            "true_variance":float(np.var(shares,ddof=1)-floor),"team_split_half_r":split_r(g,lambda q:q["v"])["r"] if g else None}

def normalize(s): return "".join(c for c in unicodedata.normalize("NFKD",s).lower() if not unicodedata.combining(c))
def clean(x):
    if isinstance(x, float) and not math.isfinite(x): return None
    if isinstance(x, dict): return {k: clean(v) for k,v in x.items()}
    if isinstance(x, list): return [clean(v) for v in x]
    return x

def lp_ids():
    """Read LP team ids from its reachable warehouse payloads for mover direction."""
    idx=Path("/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv")
    if not idx.exists(): return {}
    out=defaultdict(set); base=idx.parent.parent
    for r in csv.DictReader(idx.open()):
        if r.get("league_id")!="112" or r.get("season") not in EDA_SEASONS: continue
        p=base/r["path"]
        if not p.exists(): continue
        x=json.load(p.open()); ts=(x.get("header") or {}).get("teams") or []
        out[r["season"]].update(str(t["id"]) for t in ts if t.get("id") is not None)
    return out

def movers():
    by=defaultdict(set)
    for r in M: by[r["season"]].update((r["home_id"],r["away_id"]))
    lp=lp_ids(); out={}; pooled=[]
    for i in range(1,5):
        prev,cur=EDA_SEASONS[i-1],EDA_SEASONS[i]; new=sorted(by[cur]-by[prev]); lp_prev=lp.get(prev,set())
        rr=[r for r in M if r["season"]==cur]; league_gf=np.mean([f(r,"hg") for r in rr]+[f(r,"ag") for r in rr])
        records=[]
        for tid in new:
            tr=[r for r in T if r["season"]==cur and r["team_id"]==tid]
            gf=np.mean([f(r,"goals_for") for r in tr]); ga=np.mean([f(r,"goals_against") for r in tr]); direction="relegated_from_LP" if tid in lp_prev else "promoted_from_below"
            rec={"team_id":tid,"team_name":tr[0]["team_name"],"direction":direction,"n_matches":len(tr),"gf_gap":float(gf-league_gf),"ga_gap":float(ga-league_gf)}; records.append(rec); pooled.append(rec)
        lp_cur=lp.get(cur,set())
        departures=[]
        for tid in sorted(by[prev]-by[cur]):
            if tid in lp_cur:
                old=[r for r in T if r["season"]==prev and r["team_id"]==tid]
                departures.append({"team_id":tid,"team_name":old[0]["team_name"] if old else tid,"direction":"BNAC_to_LP"})
        out[cur]={"newcomers":records,"n_teams":len(records),"departures_to_LP":departures,"lp_crosscheck_ids":sorted(lp_prev)}
    out["pooled_2022_2025"]={"n_team_transitions":len(pooled),"gf_gap":mean([x["gf_gap"] for x in pooled]),"ga_gap":mean([x["ga_gap"] for x in pooled]),"by_direction":{}}
    for d in ("relegated_from_LP","promoted_from_below"):
        q=[x for x in pooled if x["direction"]==d]; out["pooled_2022_2025"]["by_direction"][d]={"n":len(q),"gf_gap":mean([x["gf_gap"] for x in q]),"ga_gap":mean([x["ga_gap"] for x in q])}
    return out

def main():
    seasons={s:levels([r for r in M if r["season"]==s]) for s in EDA_SEASONS}
    inv={}
    formats={"2021":"Zona A 17 teams (8x34) + Zona B 18 teams (9x34)","2022":"single table, 37 teams, 37 rounds x18","2023":"Zona A 19 teams (38x9) + Zona B 18 teams (34x9)","2024":"single table, 38 teams, 38 rounds x19","2025":"Zona A/B, 18 teams each, 34 rounds x9","2026":"virgin: single table, 36 teams, 36 rounds x18"}
    for s in EDA_SEASONS:
        rs=[r for r in M if r["season"]==s]; inv[s]={"n_matches":len(rs),"distinct_teams":len({r["home_id"] for r in rs}|{r["away_id"] for r in rs}),"date_range":[min(r["date"] for r in rs),max(r["date"] for r in rs)],"coverage":coverage(rs),"format":formats[s],"zones":dict(__import__('collections').Counter(r["zone"] or "single" for r in rs))}
    inv["2026"]={"n_matches":648,"virgin":True,"format":formats["2026"],"completeness_basis":"inventory count; no outcomes/statistics used"}
    groups=defaultdict(list)
    for r in T:
        if r["season"] in EDA_SEASONS: groups[r["team_id"]].append(r)
    groups={k:v for k,v in groups.items() if len(v)>=24}
    rel={}
    for label,k in (("goals_for","goals_for"),("goals_against","goals_against"),("yellows_for","yellow_for"),("yellows_against","yellow_against")):
        q={tid:[r for r in rs if r["season"] in EDA_SEASONS and (s:=r["team_id"])] for tid,rs in groups.items()}
        rel[label]=split_r(groups,lambda r,k=k:f(r,k)) if "yellow" not in k or True else None
    # Cards reliability is explicitly 2023+ only.
    card_groups=defaultdict(list)
    for r in T:
        if r["season"] in ("2023","2024","2025"): card_groups[r["team_id"]].append(r)
    card_groups={k:v for k,v in card_groups.items() if len(v)>=24}
    rel["yellows_for_2023_2025"]=split_r(card_groups,lambda r:f(r,"yellow_for")); rel["yellows_against_2023_2025"]=split_r(card_groups,lambda r:f(r,"yellow_against"))
    goal_halves=halves([r for r in DEV if r["season"]>="2023"],"ht_hg","ht_ag","hg","ag")
    goal_events_halves=halves([r for r in DEV if r["season"] in ("2021","2022") and r["has_events"]=="True"],"ht_hg","ht_ag","hg","ag")
    yellow_halves=halves([r for r in DEV if r["season"]>="2023"],"ht_yellow_home","ht_yellow_away","yellow_home","yellow_away")
    assert yellow_halves["n_matches"] <= 1982
    refs=defaultdict(list)
    for r in DEV:
        if r["referee"] and r["season"]>="2023": refs[r["referee"]].append(r)
    refs={k:v for k,v in refs.items() if len(v)>=8}
    referee={"coverage_by_season":{s:inv[s]["coverage"]["referee_pct"] for s in EDA_SEASONS},"eligible_referees_ge8":len(refs),"split_half_r":split_r(refs,lambda r:f(r,"yellow_home")+f(r,"yellow_away"),min_matches=8),"strictness_range":[float(min(np.mean([f(r,'yellow_home')+f(r,'yellow_away') for r in v]) for v in refs.values())),float(max(np.mean([f(r,'yellow_home')+f(r,'yellow_away') for r in v]) for v in refs.values()))]}
    devg=levels(DEV); line={"goals":{"OU2.5":pct([f(r,"hg")+f(r,"ag")>2.5 for r in DEV]),"OU1.5":pct([f(r,"hg")+f(r,"ag")>1.5 for r in DEV]),"OU3.5":pct([f(r,"hg")+f(r,"ag")>3.5 for r in DEV])},"yellows_2023_plus":{"OU4.5":pct([f(r,"yellow_home")+f(r,"yellow_away")>4.5 for r in DEV if r["season"]>="2023"])}}
    summary={"scope":{"eda_seasons":EDA_SEASONS,"virgin_excluded":"2026; no descriptive statistics computed"},"seasons":seasons,"pooled":levels(DEV),"reliability":rel,"halves":{"goals_2023_2025_complete_feed":goal_halves,"goals_2021_2022_with_events_only":goal_events_halves,"yellows_2023_2025":yellow_halves},"movers":movers(),"referees":referee,"primary_lines":line,"absent":{"xg":0,"shotmap_shots":0,"stats_payloads_nonempty":0,"F5_set_play":0,"F6_xg_shot":0,"F7_xgot":0,"F9_box_touches_possession_big_chances":0}}
    (HERE/"inventory_summary.json").write_text(json.dumps(clean(inv),indent=2,ensure_ascii=False))
    (HERE/"eda_summary.json").write_text(json.dumps(clean(summary),indent=2,ensure_ascii=False,allow_nan=False))
    print(json.dumps({"eda_matches":len(DEV),"pooled_goals":summary["pooled"]["goals_per_match"],"primary_lines":line},indent=2))
if __name__=="__main__": main()
