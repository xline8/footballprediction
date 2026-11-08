import json,matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
HERE=Path(__file__).resolve().parent;X=json.load(open(HERE/"eda_summary.json"));out=HERE/"charts";out.mkdir(exist_ok=True);ss=X["seasons"]
fig,ax=plt.subplots(figsize=(10,5));ax.plot(ss,[X["per_season"][s]["goals"] for s in ss],marker="o");ax.set_title("BE-FirstDivisionB goals per match");ax.tick_params(axis="x",rotation=30);ax.grid(alpha=.25);fig.tight_layout();fig.savefig(out/"goals_levels_by_season.png",dpi=140);plt.close(fig)
fig,ax=plt.subplots(figsize=(6,4));ks=list(X["goal_reliability_odd_even"]);ax.bar(ks,[X["goal_reliability_odd_even"][k]["r"] for k in ks],color="#3f6f8f");ax.set_ylim(0,1);ax.set_title("Goal-trait odd/even dev reliability");fig.tight_layout();fig.savefig(out/"trait_reliability.png",dpi=140);plt.close(fig)
h=X["halves"];fig,ax=plt.subplots(figsize=(5,4));ax.bar(["constant","binomial noise","observed"],[h["constant"],h["binomial_noise"],h["observed_variance"]],color=["#37474f","#90a4ae","#2e7d32"]);ax.set_title("Dev-era 1H goal share / variance");fig.tight_layout();fig.savefig(out/"halves_constant.png",dpi=140);plt.close(fig)
ms=X["movers"];labels=[m["team"]+" "+m["entry_season"] for m in ms];fig,ax=plt.subplots(figsize=(9,4));ax.bar(labels,[m["b_gap"][0] for m in ms],label="B GF gap");ax.bar(labels,[m["b_gap"][1] for m in ms],bottom=[m["b_gap"][0] for m in ms],alpha=.65,label="B GA gap");ax.axhline(0,color="black",lw=.7);ax.tick_params(axis="x",rotation=45,labelsize=7);ax.set_title("Mover first-season BE-B gaps");ax.legend();fig.tight_layout();fig.savefig(out/"mover_gap.png",dpi=140);plt.close(fig)
print("charts written",sorted(p.name for p in out.glob("*.png")))
