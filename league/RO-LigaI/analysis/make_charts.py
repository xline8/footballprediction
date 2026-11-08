"""Step 4 charts for RO-LigaI: levels by season, trait reliability, halves constants.
Regenerate: .venv/bin/python league/RO-LigaI/analysis/make_charts.py"""
import csv, statistics as st
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
ROWS=list(csv.DictReader(open(HERE.parent/"data"/"ro_matches.csv")))
INC=[r for r in ROWS if r["phase"]!="ecl_playoff"]
def f(r,k):
    v=r.get(k); return float(v) if v not in (None,"") else None
SEASONS=sorted(set(r["season"] for r in INC))
# levels
fig,axes=plt.subplots(2,3,figsize=(11,6))
series={"goals":lambda r:f(r,"home_goals")+f(r,"away_goals"),
 "SOT":lambda r:(f(r,"ShotsOnTarget_home")+f(r,"ShotsOnTarget_away")) if f(r,"ShotsOnTarget_home") is not None else None,
 "corners":lambda r:(f(r,"corners_home")+f(r,"corners_away")) if f(r,"corners_home") is not None else None,
 "shots (raw)":lambda r:(f(r,"total_shots_home")+f(r,"total_shots_away")) if f(r,"total_shots_home") is not None else None,
 "yellows (events)":lambda r:f(r,"yellow_home")+f(r,"yellow_away")}
for ax,(name,g) in zip(axes.flat, series.items()):
    xs,ys=[],[]
    for s in SEASONS:
        v=[g(r) for r in INC if r["season"]==s]; v=[x for x in v if x is not None]
        xs.append(s); ys.append(st.mean(v))
    ax.plot(xs,ys,marker="o"); ax.set_title(name); ax.tick_params(axis="x",rotation=45,labelsize=7)
axes.flat[5].axis("off")
fig.suptitle("RO-LigaI levels by season (shots break at 2025/2026 = feed change)")
fig.tight_layout(); fig.savefig(HERE/"charts"/"levels_by_season.png",dpi=110); plt.close(fig)
# reliability
def split_half(getter):
    by=defaultdict(list)
    for r in INC:
        for side in ("home","away"):
            v=getter(r,side)
            if v is not None: by[(r["season"],r[f"{side}_team_id"])].append(v)
    xs,ys=[],[]
    for v in by.values():
        if len(v)>=10: xs.append(st.mean(v[0::2])); ys.append(st.mean(v[1::2]))
    mx,my=st.mean(xs),st.mean(ys)
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/len(xs)
    return cov/(st.pstdev(xs)*st.pstdev(ys))
traits={"shots_for":lambda r,s:f(r,f"total_shots_{s}"),"possession":lambda r,s:f(r,f"BallPossesion_{s}"),
 "sot_for":lambda r,s:f(r,f"ShotsOnTarget_{s}"),"corners_for":lambda r,s:f(r,f"corners_{s}"),
 "goals_for":lambda r,s:f(r,"home_goals" if s=="home" else "away_goals"),
 "yellows_for":lambda r,s:f(r,f"yellow_{s}")}
names=list(traits); vals=[split_half(traits[n]) for n in names]
fig,ax=plt.subplots(figsize=(8,4)); ax.barh(names,vals); ax.set_xlabel("split-half r (team-season odd/even)")
ax.set_title("RO-LigaI trait reliability"); fig.tight_layout(); fig.savefig(HERE/"charts"/"trait_reliability.png",dpi=110); plt.close(fig)
# halves constants
labels=["goals","SOT","corners","shots","yellows"]; consts=[0.453,0.455,0.477,0.459,0.330]
fig,ax=plt.subplots(figsize=(8,4)); ax.bar(labels,consts); ax.axhline(0.5,color="grey",ls="--")
ax.set_ylabel("1H share"); ax.set_title("RO-LigaI frozen halves constants (split era n=434)")
fig.tight_layout(); fig.savefig(HERE/"charts"/"halves_constants.png",dpi=110); plt.close(fig)
print("charts written; reliabilities:", {n:round(v,3) for n,v in zip(names,vals)})
