#!/usr/bin/env python3
"""Render descriptive charts from eda_summary.json."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; CHARTS=HERE/"charts"
def main():
    data=json.load(open(HERE/"eda_summary.json")); seasons=list(data["seasons"]); x=list(range(len(seasons))); CHARTS.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(10,5))
    for key,label,marker in (("mean_total_goals","Goals","o"),("mean_event_yellows_total","Event yellows","x"),("mean_event_cards_total","All Card events","s")):
        ax.plot(x,[data["seasons"][s][key] for s in seasons],marker=marker,label=label)
    ax.set_xticks(x,seasons,rotation=30,ha="right"); ax.set_ylabel("Mean per match"); ax.set_title("PT-Liga3 levels by season"); ax.legend(); fig.tight_layout(); fig.savefig(CHARTS/"levels_by_season.png",dpi=160); plt.close(fig)
    names=["Goals for","Goals against","Event yellows\n(supplementary)"]; keys=["goals_for","goals_against","event_yellows_for"]
    fig,ax=plt.subplots(figsize=(7,5)); ax.bar(range(3),[data["trait_reliability"][k]["r"] for k in keys],color=["#315f8c","#315f8c","#b77b4c"]); ax.axhline(0,color="black",linewidth=.8); ax.set_ylim(-1,1); ax.set_ylabel("Split-half Pearson r"); ax.set_xticks(range(3),names); ax.set_title("Career-pooled trait reliability"); fig.tight_layout(); fig.savefig(CHARTS/"trait_reliability.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5)); recover=[100*data["seasons"][s]["ht_goal_matches"]/data["seasons"][s]["n"] for s in seasons]; split=[100*data["seasons"][s]["period_split_matches"]/data["seasons"][s]["n"] for s in seasons]; ax.bar(x,split,label="Period-split stats",color="#b77b4c"); ax.plot(x,recover,"o-",label="HT goals recoverable",color="#315f8c"); ax.set_ylim(0,110); ax.set_ylabel("Matches / season (%)"); ax.set_xticks(x,seasons,rotation=30,ha="right"); ax.set_title("Halves availability — descriptive only; no frozen constant"); ax.legend(); fig.tight_layout(); fig.savefig(CHARTS/"halves_constants.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4)); ref=[100*data["seasons"][s]["referee_named"]/data["seasons"][s]["n"] for s in seasons]; ax.bar(x,ref,color="#777777"); ax.set_ylim(0,100); ax.set_ylabel("Named referee (%)"); ax.set_xticks(x,seasons,rotation=30,ha="right"); ax.set_title("Referee coverage"); fig.tight_layout(); fig.savefig(CHARTS/"referee_coverage.png",dpi=160); plt.close(fig); print(f"Wrote charts to {CHARTS}")
if __name__=="__main__": main()
