"""Make the scores-only Stage 1 I Liga charts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
D=json.loads((HERE/"eda_numbers.json").read_text()); OUT=HERE/"charts"; OUT.mkdir(exist_ok=True)
ss=D["seasons"]
fig,ax=plt.subplots(figsize=(10,5))
x=range(len(ss)); ax.bar([i-.18 for i in x],[D["per_season"][s]["mean_home_goals"] for s in ss],.36,label="home")
ax.bar([i+.18 for i in x],[D["per_season"][s]["mean_away_goals"] for s in ss],.36,label="away")
ax.set_xticks(list(x),ss,rotation=30); ax.set_ylabel("goals per match"); ax.set_title("I Liga goals and home/away split")
ax.legend(); fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png",dpi=130); plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4)); names=["goals-for","goals-against"]; vals=[D["reliability"]["goals_for"]["r"],D["reliability"]["goals_against"]["r"]]
ax.bar(names,vals,color="#2e7d32"); ax.set_ylim(0,1); ax.set_ylabel("split-half r"); ax.set_title("I Liga goals trait reliability (60 splits)")
for i,v in enumerate(vals): ax.text(i,v+.02,f"{v:.3f}",ha="center")
fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png",dpi=130); plt.close(fig)
h=D["half_shares"]["goals"]; fig,ax=plt.subplots(figsize=(5,4)); ax.bar(["goals 1H share"],[h["share_ratio_of_sums"]],color="#37474f"); ax.axhline(.5,color="grey",ls="--"); ax.set_ylim(0,.6); ax.set_title("I Liga goals first-half constant")
ax.text(0,h["share_ratio_of_sums"]+.02,f'{h["share_ratio_of_sums"]:.4f}',ha="center"); fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=130); plt.close(fig)
print("charts written",sorted(p.name for p in OUT.glob("*.png")))

