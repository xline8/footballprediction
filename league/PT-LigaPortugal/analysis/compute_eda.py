#!/usr/bin/env python3
"""Compute descriptive and split-half reliability statistics for Liga Portugal."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CSV = BASE / "data/pt_matches.csv"
OUT = Path(__file__).resolve().parent / "eda_summary.json"

def f(x):
    try: return float(x) if x != "" else None
    except (TypeError, ValueError): return None

def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None

def pearson(a, b):
    if len(a) < 2: return None
    ma, mb = mean(a), mean(b); da = [x-ma for x in a]; db = [x-mb for x in b]
    den = math.sqrt(sum(x*x for x in da) * sum(x*x for x in db))
    return sum(x*y for x,y in zip(da,db)) / den if den else None

def vals(rows, col): return [f(r[col]) for r in rows if f(r[col]) is not None]
def total(rows, a, b): return [f(r[a])+f(r[b]) for r in rows if f(r[a]) is not None and f(r[b]) is not None]

def split_corr(groups, metric, min_half=20):
    a, b = [], []
    for rs in groups.values():
        rs = sorted(rs, key=lambda r: (r["date"], int(r["match_id"])))
        rs = [r for r in rs if metric(r) is not None]
        mid = len(rs)//2
        if mid < min_half or len(rs)-mid < min_half: continue
        a.append(mean(metric(r) for r in rs[:mid])); b.append(mean(metric(r) for r in rs[mid:]))
    return {"r": pearson(a,b), "n_teams": len(a)}

def half_share(rows, h, t, threshold):
    # Coordinator fix (verification): the frozen constant is the
    # ratio-of-sums over ALL matches with split data; the threshold
    # subset is used only for the variance decomposition.
    all_pairs = [(f(r[h]), f(r[t])) for r in rows if f(r[h]) is not None and f(r[t]) is not None and f(r[t]) > 0]
    pairs = [(x, y) for x, y in all_pairs if y >= threshold]
    if not pairs: return {"n": 0, "ratio_of_sums": None, "observed_variance": None, "binomial_noise": None, "true_variance": None}
    shares = [x/y for x,y in pairs]; bar = mean(shares)
    obs = sum((x-bar)**2 for x in shares)/len(shares)
    noise = mean(bar*(1-bar)/y for _,y in pairs)
    return {"n": len(pairs), "n_all": len(all_pairs),
            "ratio_of_sums": sum(x for x,_ in all_pairs)/sum(y for _,y in all_pairs),
            "observed_variance": obs, "binomial_noise": noise, "true_variance": obs-noise}

def main():
    with open(CSV, newline="") as q: rows = list(csv.DictReader(q))
    seasons = sorted({r["season"] for r in rows})
    summary = {"n_matches": len(rows), "seasons": {}, "half_shares": {}, "team_split_half": {},
               "trait_split_half": {}, "referee_reliability": {}, "referee_coverage": {}, "thin_history_teams": {}}
    for s in seasons:
        rs = [r for r in rows if r["season"] == s]
        hg, ag = vals(rs,"home_goals"), vals(rs,"away_goals")
        n=len(rs); results=[(f(r["home_goals"]),f(r["away_goals"])) for r in rs]
        summary["seasons"][s] = {"n":n, "teams":len({r["home_id"] for r in rs}|{r["away_id"] for r in rs}),
          "mean_home_goals":mean(hg),"mean_away_goals":mean(ag),"mean_total_goals":mean([x+y for x,y in results]),
          "home_win_rate":sum(x>y for x,y in results)/n,"draw_rate":sum(x==y for x,y in results)/n,"away_win_rate":sum(x<y for x,y in results)/n,
          "mean_sot_total":mean(total(rs,"sot_home","sot_away")),"mean_corners_total":mean(total(rs,"corners_home","corners_away")),
          "mean_yellows_total":mean(total(rs,"yellow_home","yellow_away")),"mean_total_shots":mean(total(rs,"shots_home","shots_away")),"mean_xg_total":mean(total(rs,"xg_home","xg_away")),
          "period_split_coverage":sum(any(r.get(c,"")!="" for c in r if c.endswith("_1h")) for r in rs),
          "referee_coverage":sum(bool(r["referee"].strip()) for r in rs),"touches_coverage":sum(bool(r["touches_home"] or r["touches_away"]) for r in rs)}
    complete=[s for s in seasons if s in {"2023/2024","2024/2025","2025/2026"}]
    cr=[r for r in rows if r["season"] in complete]
    for label,h,t,threshold in [("goals","ht_home","home_goals",2),("sot","sot_home_1h","sot_home",5),("corners","corners_home_1h","corners_home",5),("yellows","yellow_home_1h","yellow_home",5),("shots","shots_home_1h","shots_home",5)]:
        # home and away are combined into one match-level total.
        hh={"goals":("ht_home","ht_away","home_goals","away_goals"),"sot":("sot_home_1h","sot_away_1h","sot_home","sot_away"),"corners":("corners_home_1h","corners_away_1h","corners_home","corners_away"),"yellows":("yellow_home_1h","yellow_away_1h","yellow_home","yellow_away"),"shots":("shots_home_1h","shots_away_1h","shots_home","shots_away")}[label]
        synthetic=[dict(r, _h=(f(r[hh[0]])+f(r[hh[1]]) if f(r[hh[0]]) is not None and f(r[hh[1]]) is not None else ""), _t=(f(r[hh[2]])+f(r[hh[3]]) if f(r[hh[2]]) is not None and f(r[hh[3]]) is not None else "")) for r in cr]
        summary["half_shares"][label]=half_share(synthetic,"_h","_t",threshold)
    # Coordinator fix (verification): team split-half of the 1H share,
    # per market, as a ratio-of-sums over the team's matches (match
    # totals) in each chronological half — not a mean of per-match
    # team-only shares.
    share_cols = {"goals": ("ht_home", "ht_away", "home_goals", "away_goals"),
                  "sot": ("sot_home_1h", "sot_away_1h", "sot_home", "sot_away"),
                  "corners": ("corners_home_1h", "corners_away_1h", "corners_home", "corners_away"),
                  "yellows": ("yellow_home_1h", "yellow_away_1h", "yellow_home", "yellow_away"),
                  "shots": ("shots_home_1h", "shots_away_1h", "shots_home", "shots_away")}
    tsh = {}
    for label, (h1, h2, t1, t2) in share_cols.items():
        tg = defaultdict(list)
        for r in cr:
            if any(f(r[c]) is None for c in (h1, h2, t1, t2)):
                continue
            tot1 = f(r[h1]) + f(r[h2]); tot = f(r[t1]) + f(r[t2])
            tg[r["home_id"]].append((r, tot1, tot)); tg[r["away_id"]].append((r, tot1, tot))
        aa, bb = [], []
        for id_, lst in tg.items():
            lst.sort(key=lambda x: (x[0]["date"], int(x[0]["match_id"])))
            m = len(lst) // 2
            if m < 10 or len(lst) - m < 10:
                continue
            s1 = sum(x[1] for x in lst[:m]) / max(1e-9, sum(x[2] for x in lst[:m]))
            s2 = sum(x[1] for x in lst[m:]) / max(1e-9, sum(x[2] for x in lst[m:]))
            aa.append(s1); bb.append(s2)
        tsh[label] = {"r": pearson(aa, bb), "n_teams": len(aa)}
    summary["team_split_half"] = tsh
    # Reliability traits, with team-side rows to keep identity keyed by IDs.
    tr=defaultdict(list)
    for r in rows:
        for side,id_ in (("home",r["home_id"]),("away",r["away_id"])):
            x=dict(r, _side=side, _id=id_); tr[id_].append(x)
    metrics={"goals_for":lambda r:f(r[f"{r['_side']}_goals"]),"goals_against":lambda r:f(r["away_goals" if r["_side"]=="home" else "home_goals"]),
      "sot_for":lambda r:f(r[f"sot_{r['_side']}"]),"sot_against":lambda r:f(r[f"sot_away" if r["_side"]=="home" else "sot_home"]),"corners_for":lambda r:f(r[f"corners_{r['_side']}"]),"corners_against":lambda r:f(r[f"corners_away" if r["_side"]=="home" else "corners_home"]),"yellow_for":lambda r:f(r[f"yellow_{r['_side']}"]),"yellow_against":lambda r:f(r[f"yellow_away" if r["_side"]=="home" else "yellow_home"]),"shots_for":lambda r:f(r[f"shots_{r['_side']}"]),"touches_for":lambda r:f(r[f"touches_{r['_side']}"]),"touches_against":lambda r:f(r[f"touches_away" if r["_side"]=="home" else "touches_home"]),"poss_for":lambda r:f(r[f"poss_{r['_side']}"]),"bigchance_for":lambda r:f(r[f"bigchance_{r['_side']}"])}
    for name, fn in metrics.items(): summary["trait_split_half"][name]=split_corr(tr,fn,15)
    # Aggregate traits requiring sums across each half.
    summary["trait_split_half"]["xg_per_shot"]={"r":None,"n_teams":0}; summary["trait_split_half"]["setplay_share"]={"r":None,"n_teams":0}; summary["trait_split_half"]["ontarget_rate"]={"r":None,"n_teams":0}; summary["trait_split_half"]["finishing"]={"r":None,"n_teams":0}; summary["trait_split_half"]["xgot_per_shot_attack"]={"r":None,"n_teams":0}
    # These aggregate metrics are calculated by the same chronological halves.
    for name in ["xg_per_shot","setplay_share","ontarget_rate","finishing","xgot_per_shot_attack"]:
        def agg(rs, name=name):
            if name=="xgot_per_shot_attack": rs=[r for r in rs if r["season"] in {"2024/2025","2025/2026","2026/2027"}]
            if name=="xg_per_shot": return sum(f(r["xg_"+r["_side"]]) or 0 for r in rs)/sum(f(r["shots_"+r["_side"]]) or 0 for r in rs) if sum(f(r["shots_"+r["_side"]]) or 0 for r in rs) else None
            if name=="setplay_share": return sum(f(r["xg_set_"+r["_side"]]) or 0 for r in rs)/sum(f(r["xg_"+r["_side"]]) or 0 for r in rs) if sum(f(r["xg_"+r["_side"]]) or 0 for r in rs) else None
            if name=="ontarget_rate": return sum(f(r["sot_"+r["_side"]]) or 0 for r in rs)/sum(f(r["shots_"+r["_side"]]) or 0 for r in rs) if sum(f(r["shots_"+r["_side"]]) or 0 for r in rs) else None
            if name=="finishing": return mean([(f(r[r["_side"]+"_goals"]) or 0)-(f(r["xg_"+r["_side"]]) or 0) for r in rs])
            return sum(f(r["xgot_"+r["_side"]]) or 0 for r in rs)/sum(f(r["shots_"+r["_side"]]) or 0 for r in rs) if sum(f(r["shots_"+r["_side"]]) or 0 for r in rs) else None
        halfs={k:[dict(x) for x in v] for k,v in tr.items()}; aa=[];bb=[]
        for rs in halfs.values():
            if name == "xgot_per_shot_attack":
                rs = [r for r in rs if r["season"] in {"2024/2025","2025/2026","2026/2027"}]
            rs.sort(key=lambda r:(r["date"],int(r["match_id"]))); m=len(rs)//2
            if m<15 or len(rs)-m<15: continue
            x,y=agg(rs[:m]),agg(rs[m:]);
            if x is not None and y is not None: aa.append(x);bb.append(y)
        summary["trait_split_half"][name]={"r":pearson(aa,bb),"n_teams":len(aa)}
    refs=defaultdict(list)
    for r in rows:
        if r["referee"].strip(): refs[r["referee"].strip()].append(r)
    rr=[]
    for rs in refs.values():
        rs.sort(key=lambda r:(r["date"],int(r["match_id"]))); m=len(rs)//2
        if len(rs)>=20: rr.append((mean([sum(f(r[x]) for x in ("yellow_home","yellow_away")) for r in rs[:m]]),mean([sum(f(r[x]) for x in ("yellow_home","yellow_away")) for r in rs[m:]])))
    summary["referee_reliability"]={"r":pearson([x for x,y in rr],[y for x,y in rr]),"n_refs":len(rr)}
    summary["referee_coverage"]={s:summary["seasons"][s]["referee_coverage"] for s in seasons}
    prior=defaultdict(int)
    for s in seasons:
        ids={r["home_id"] for r in rows if r["season"]==s}|{r["away_id"] for r in rows if r["season"]==s}; thin=[]
        for id_ in ids:
            first=min((r for r in rows if r["season"]==s and id_ in (r["home_id"],r["away_id"])),key=lambda r:(r["date"],int(r["match_id"])))
            n=sum(id_ in (r["home_id"],r["away_id"]) and (r["date"],int(r["match_id"]))<(first["date"],int(first["match_id"])) for r in rows)
            if n<10: thin.append(id_)
        summary["thin_history_teams"][s]={"teams":sorted(thin),"count":len(thin)}
    with open(OUT,"w") as out_f: json.dump(summary,out_f,indent=2,sort_keys=True)
    print(f"Wrote {OUT}")
if __name__=="__main__": main()
