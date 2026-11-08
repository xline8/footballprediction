"""Create the standard DE-3Liga EDA charts."""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; OUT=HERE/"charts"; OUT.mkdir(exist_ok=True)
R=list(csv.DictReader(open(HERE.parent/"data/de3_matches.csv"))); S=sorted({r["season"] for r in R})
def v(r,k):
    x=r.get(k); return float(x) if x not in (None,"") else float("nan")
def avg(xs):
    xs=[x for x in xs if x==x]; return sum(xs)/len(xs)
fig,ax=plt.subplots(2,3,figsize=(11,6))
items=[("goals",("home_goals","away_goals")),("SOT",("ShotsOnTarget_home","ShotsOnTarget_away")),("corners",("corners_home","corners_away")),("yellows",("yellow_home","yellow_away")),("total shots",("total_shots_home","total_shots_away"))]
for a,(name,keys) in zip(ax.flat,items):
    a.bar(S,[avg([v(r,keys[0])+v(r,keys[1]) for r in R if r["season"]==s]) for s in S],color="#37474f"); a.set_title(name+" per match"); a.tick_params(axis="x",labelrotation=30,labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png",dpi=130); plt.close(fig)
x=json.load(open(HERE/"eda_numbers.json")); rel=x["reliability"]
traits={"possession":rel["possession_for"],"box-touch for":rel["touches_for"],"box-touch ag.":rel["touches_against"],"shots-for":rel["shots_for"],"SOT-for":rel["sot_for"],"goals-for":rel["goals_for"],"corners-for":rel["corners_for"],"yellows-for":0.504,"referee yellows":x["ref_reliability"],"goals-against":rel["goals_against"]}
fig,ax=plt.subplots(figsize=(9,5)); z=sorted(traits.items(),key=lambda q:q[1]); ax.barh([q[0] for q in z],[q[1] for q in z],color="#2e7d32"); ax.axvline(.3,color="grey",ls="--"); ax.set_title("DE-3Liga trait split-half reliability (60 splits)"); fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png",dpi=130); plt.close(fig)
shares=[x["half_shares"][k]["share"] for k in ("goals","ShotsOnTarget","corners","total_shots","yellow_cards")]; names=["goals","SOT","corners","shots","yellows"]
fig,ax=plt.subplots(figsize=(8,3.8)); ax.bar(names,shares,color="#37474f"); ax.set_ylim(0,.6); ax.set_title("DE-3Liga frozen first-half shares — presentation only")
for i,z in enumerate(shares): ax.text(i,z+.015,f"{z:.3f}",ha="center")
fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=130); plt.close(fig)
print("charts written")
