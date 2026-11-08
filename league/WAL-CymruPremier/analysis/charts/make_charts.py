"""Render Wales Phase A charts."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent.parent; OUT=HERE/"charts"; OUT.mkdir(exist_ok=True); D=json.loads((HERE/"eda_numbers.json").read_text()); S=[s for s in D["levels"] if s != "pooled"]; L=D["levels"]
fig,ax=plt.subplots(1,3,figsize=(12,3.8))
for a,k,t in zip(ax,("goals_per_match","home_win","over25"),("goals per match","home-win rate","over 2.5 rate")): a.bar(S,[L[s][k] for s in S],color="#37474f"); a.set_title(t); a.tick_params(axis="x",rotation=35,labelsize=7)
fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png",dpi=130); plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4)); ss=list(D["trait_reliability"]); ax.plot(ss,[D["trait_reliability"][s]["attack"] for s in ss],"o-",label="goals for"); ax.plot(ss,[D["trait_reliability"][s]["defence"] for s in ss],"o-",label="goals against"); ax.set_ylim(0,1); ax.legend(); ax.set_title("Team-trait split-half reliability"); ax.tick_params(axis="x",rotation=35); fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png",dpi=130); plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4)); ax.bar(S,[D["halves"]["by_season"][s]["share"] for s in S],color="#37474f"); ax.axhline(D["halves"]["goals_1h_share"],color="#c62828",ls="--",label="pooled 0.4444"); ax.legend(); ax.set_ylim(0,.65); ax.set_title("First-half goal share"); ax.tick_params(axis="x",rotation=35); fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=130); plt.close(fig); print("charts written")
