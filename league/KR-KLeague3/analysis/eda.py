"""Reproducible score-only EDA for K League 3 (FotMob 9537)."""
import csv, json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
MAIN = Path("/home/hatch/workspace/footballprediction")
SEED = 90210
INDEX = MAIN / "data_enrichment" / "fotmob_world_index.csv"

def read(p):
    with open(p, newline="") as f: return list(csv.DictReader(f))
def num(r, k):
    try: return float(r[k])
    except (KeyError, TypeError, ValueError): return np.nan
def mean(x): return float(np.mean(np.asarray(x, float)))
def split_r(groups, key, min_matches=24):
    rng = np.random.default_rng(SEED); vals=[]
    for _ in range(60):
        a=[]; b=[]
        for z in groups.values():
            x=np.asarray([key(q) for q in z],float); x=x[np.isfinite(x)]
            if len(x)<min_matches: continue
            ix=rng.permutation(len(x)); n=len(x)//2; a.append(np.mean(x[ix[:n]])); b.append(np.mean(x[ix[n:]]))
        if len(a)>2 and np.std(a)>0 and np.std(b)>0: vals.append(float(np.corrcoef(a,b)[0,1]))
    return {"r": float(np.mean(vals)), "n_splits": len(vals), "seed": SEED, "min_matches": min_matches}
def level(rs):
    h=np.array([num(r,"home_goals") for r in rs]); a=np.array([num(r,"away_goals") for r in rs]); g=h+a
    return {"n":len(rs),"goals":mean(g),"home_goals":mean(h),"away_goals":mean(a),
            "hw_pct":float(np.mean(h>a)),"draw_pct":float(np.mean(h==a)),
            "over25_pct":float(np.mean(g>2.5)),"goal_variance":float(np.var(g,ddof=1))}
def payload_inventory(index_rows):
    out=defaultdict(lambda: Counter())
    all_flags=Counter(); card=Counter(); names=defaultdict(set); teams=defaultdict(set)
    for ir in index_rows:
        d=json.loads((MAIN/ir["path"]).read_text()); g=d.get("general") or {}; c=d.get("content") or {}
        s=ir["season"]; started=bool((d.get("header",{}).get("status") or {}).get("started",g.get("started")))
        finished=bool((d.get("header",{}).get("status") or {}).get("finished",g.get("finished")))
        played=started and finished
        phase="playoff" if g.get("leagueName")=="K3 League Playoff" else "regular"
        out[s]["index"]+=1; out[s]["played" if played else "unplayed"]+=1; out[s][phase]+=int(played)
        stats=c.get("stats"); shots=(c.get("shotmap") or {}).get("shots") or []
        out[s]["stats_present"]+=int(stats is not None); out[s]["splits_present"]+=0
        out[s]["events_present"]+=int(bool((d.get("header") or {}).get("events")))
        out[s]["referee_present"]+=int(bool((((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")))
        out[s]["shotmap_present"]+=int(bool(shots)); out[s]["xg_present"]+=int(bool(shots))
        all_flags["stats"]+=int(stats is not None); all_flags["shotmap"]+=int(bool(shots)); all_flags["lineup"]+=int(bool(c.get("lineup"))); all_flags["splits"]+=int(bool((stats or {}).get("Periods")))
        for side in ("home","away"):
            t=g.get(side+"Team") or {}; teams[s].add(str(t.get("id"))); names[str(t.get("id"))].add(t.get("name"))
        for e in (((c.get("matchFacts") or {}).get("events") or {}).get("events") or []):
            if e.get("type")=="Card": card[e.get("card")]+=1
    return out, all_flags, card, names, teams
def main():
    MALL=read(DATA/"kr3_matches.csv"); M=[r for r in MALL if r["phase"]=="regular"]
    idx=[r for r in read(INDEX) if r["league_id"]=="9537"]
    inv, flags, cards, names, teams=payload_inventory(idx)
    seasons=sorted({r["season"] for r in M})
    levels={s:level([r for r in M if r["season"]==s]) for s in seasons}
    levels_pooled=level(M)
    groups=defaultdict(list)
    for r in read(DATA/"kr3_team_matches.csv"):
        if r["phase"]=="regular": groups[r["team_id"]].append(r)
    reliability={"goals_for":split_r(groups,lambda r:num(r,"goals_for")),"goals_against":split_r(groups,lambda r:num(r,"goals_against"))}
    # Read event times directly so the EDA is independent of builder HT fields.
    byid={r["match_id"]:r for r in M}; halves=[]; reconcile=Counter()
    for ir in idx:
        if ir["match_id"] not in byid: continue
        d=json.loads((MAIN/ir["path"]).read_text()); h=d.get("header",{}); st=h.get("status") or {}
        if not (st.get("started") and st.get("finished")): continue
        p=byid[ir["match_id"]]; ev=[]
        for side,key in (("home","homeTeamGoals"),("away","awayTeamGoals")):
            for vals in ((h.get("events") or {}).get(key) or {}).values():
                for e in vals or []:
                    if e.get("type")=="Goal" and not e.get("isPenaltyShootoutEvent"): ev.append((side,e))
        fg=(sum(x=="home" for x,e in ev),sum(x=="away" for x,e in ev)); ft=(int(p["home_goals"]),int(p["away_goals"]))
        ok=fg==ft; reconcile["reconciled" if ok else "failed"]+=1
        if ok and sum(ft)>0:
            one=sum(1 for side,e in ev if (e.get("time") or 999)<=45); halves.append((one,sum(ft)))
    shares=np.array([x/y for x,y in halves]); p=sum(x for x,y in halves)/sum(y for x,y in halves)
    observed=float(np.var(shares,ddof=1)); noise=float(np.mean(p*(1-p)/np.array([y for x,y in halves]))); truevar=observed-noise
    name_variants={k:sorted(v) for k,v in names.items() if len(v)>1}
    summary={"seed":SEED,"inventory":{},"levels":levels,"levels_pooled":levels_pooled,
             "reliability":reliability,"halves":{"event_reconciled_regular":reconcile["reconciled"],"event_failed_regular":reconcile["failed"],"scoring_matches_complete_events":len(halves),"share_1h":float(p),"observed_variance":observed,"noise_floor":noise,"true_variance":truevar,"season_share_1h":{}},
             "cards":dict(cards),"flags_absent_all_payloads":dict(flags),"team_name_variants":name_variants,
             "team_ids":len(names),"teams_per_season":{s:len(teams[s]) for s in seasons},
             "regular_counts":{s:sum(r["season"]==s for r in M) for s in seasons},"playoff_counts":{s:sum(r["season"]==s for r in MALL if r["phase"]=="playoff") for s in seasons},
             "dev_over25_2022_2024":float(np.mean([num(r,"home_goals")+num(r,"away_goals")>2.5 for r in M if r["season"] in ("2022","2023","2024")])),"virgin_over25_2025":float(np.mean([num(r,"home_goals")+num(r,"away_goals")>2.5 for r in M if r["season"]=="2025"]))}
    for s in seasons:
        z=[(x,y) for ir in idx if ir["season"]==s and ir["match_id"] in byid for d in [json.loads((MAIN/ir["path"]).read_text())] for x,y in []]
        ss=[]
        for ir in idx:
            if ir["season"]!=s or ir["match_id"] not in byid: continue
            d=json.loads((MAIN/ir["path"]).read_text()); ev=[]; h=d.get("header",{})
            for side,key in (("home","homeTeamGoals"),("away","awayTeamGoals")):
                for vals in ((h.get("events") or {}).get(key) or {}).values():
                    for e in vals or []:
                        if e.get("type")=="Goal" and not e.get("isPenaltyShootoutEvent"): ev.append((side,e))
            ft=(int(byid[ir["match_id"]]["home_goals"]),int(byid[ir["match_id"]]["away_goals"]))
            if (sum(x=="home" for x,e in ev),sum(x=="away" for x,e in ev))==ft and sum(ft)>0: ss.append((sum(1 for x,e in ev if (e.get("time") or 999)<=45),sum(ft)))
        summary["halves"]["season_share_1h"][s]=float(sum(x for x,y in ss)/sum(y for x,y in ss)) if ss else None
    summary["inventory"]={s:{"index":c["index"],"regular":c["regular"],"playoff":c["playoff"],"unplayed":c["unplayed"],"stats":c["stats_present"],"events":c["events_present"],"referee":c["referee_present"],"shotmap":c["shotmap_present"],"xg":c["xg_present"]} for s,c in inv.items()}
    expected={"2021":(2.307,.381,.317,.391),"2022":(2.275,.400,.283,.433),"2023":(2.343,.400,.290,.438),"2024":(2.617,.388,.263,.487),"2025":(2.400,.405,.210,.481),"2026":(2.714,.401,.291,.489)}
    for s,(g,hw,dr,ov) in expected.items():
        got=levels[s]
        if not (abs(got["goals"]-g)<.001 and abs(got["hw_pct"]-hw)<.001 and abs(got["draw_pct"]-dr)<.001 and abs(got["over25_pct"]-ov)<.001): raise SystemExit(f"VERIFIED LEVEL DISCREPANCY {s}: {got}")
    (HERE/"eda_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
