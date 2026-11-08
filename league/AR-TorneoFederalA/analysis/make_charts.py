"""Make the Phase-A chart set from eda_summary.json (never includes 2026)."""
from pathlib import Path
import json
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; OUT=HERE/"charts"
def main():
    x=json.loads((HERE/"eda_summary.json").read_text()); seasons=list(x["seasons"])
    OUT.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(8,4.5)); ax.plot(seasons,[x["seasons"][s]["overall"]["goals_per_match"] for s in seasons],marker="o",label="goals/match"); ax.plot(seasons,[x["seasons"][s]["overall"]["home_goals"] for s in seasons],marker="o",label="home goals"); ax.plot(seasons,[x["seasons"][s]["overall"]["away_goals"] for s in seasons],marker="o",label="away goals"); ax.set_title("Federal A levels by season (EDA window)"); ax.set_ylabel("goals per match"); ax.legend(); fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4)); vals=[x["reliability"]["goals_for"]["split_half_r"],x["reliability"]["goals_against"]["split_half_r"]]; ax.bar(["attack / GF","defence / GA"],vals,color=["#2563eb","#dc2626"]); ax.set_ylim(0,1); ax.set_ylabel("split-half Pearson r"); ax.set_title("Team-trait reliability"); fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png",dpi=160); plt.close(fig)
    h=x["halves_goals"]; fig,ax=plt.subplots(figsize=(6,4)); ax.bar(["observed variance","noise floor"],[h["variance"],h["noise_floor"]],color=["#0f766e","#94a3b8"]); ax.set_ylabel("variance of 1H goal share"); ax.set_title("Goals halves frozen-constant test"); fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=160); plt.close(fig)
if __name__=="__main__": main()
