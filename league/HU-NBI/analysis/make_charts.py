#!/usr/bin/env python3
"""Create the Phase-A HU-NBI EDA charts from the built CSV."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "league/HU-NBI/analysis/charts"
CSV = ROOT / "league/HU-NBI/data/hu_nbi.csv"
OUT.mkdir(parents=True, exist_ok=True)
d = pd.read_csv(CSV)
d["cards_h"], d["cards_a"] = d.event_yellow_h, d.event_yellow_a
labels = list(d.season.drop_duplicates())

def levels():
    specs = [("goals", ["home_goals", "away_goals"]), ("sot", ["sot_h", "sot_a"]),
             ("corners", ["corners_h", "corners_a"]), ("cards", ["cards_h", "cards_a"]),
             ("total_shots", ["total_shots_h", "total_shots_a"])]
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, cols in specs:
        vals = [d.loc[d.season == s, cols].sum(axis=1).mean() for s in labels]
        ax.plot(labels, vals, marker="o", label=name)
    ax.set_ylabel("mean per match"); ax.set_title("HU-NBI market levels by season"); ax.legend(); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=150); plt.close(fig)

def reliability():
    specs = [("Goals for", ["home_goals", "away_goals"]), ("SOT for", ["sot_h", "sot_a"]),
             ("Corners for", ["corners_h", "corners_a"]), ("Cards for", ["cards_h", "cards_a"]),
             ("Shots for", ["total_shots_h", "total_shots_a"])]
    out = {}
    for name, cols in specs:
        vals=[]
        for s in labels:
            g=d[d.season==s]; a=[]
            for t in set(g.home_id)|set(g.away_id):
                x=pd.concat([g.loc[g.home_id==t,cols[0]],g.loc[g.away_id==t,cols[1]]]).dropna().reset_index(drop=True); n=len(x); k=n//2
                if n>=4: a.append((x.iloc[:k].mean(),x.iloc[k:].mean()))
            vals.append(pd.DataFrame(a).corr().iloc[0,1] if len(a)>2 else float("nan"))
        out[name]=vals
    fig, ax=plt.subplots(figsize=(10,5))
    for k,v in out.items(): ax.plot(labels,v,marker="o",label=k)
    ax.axhline(0,color="black",lw=.7); ax.set_ylim(-1,1); ax.set_ylabel("split-half Pearson r"); ax.set_title("Trait reliability by season"); ax.legend(ncol=2); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=150); plt.close(fig)

def halves():
    rows=[]
    for s,g in d[d.season!="2026/2027"].groupby("season",sort=False):
        for name,h,t in [("goals",["goals_1h_h","goals_1h_a"],["home_goals","away_goals"]),("cards",["cards_1h_h","cards_1h_a"],["cards_h","cards_a"])]:
            total=g[t].sum(axis=1); valid=total>0; p=g[h].sum(axis=1).sum()/total.sum(); var=(g.loc[valid,h].sum(axis=1)/total[valid]).var(); floor=(p*(1-p)/total[valid]).mean(); rows.append((s,name,p,var,floor))
    z=pd.DataFrame(rows,columns=["season","market","share","variance","noise_floor"])
    fig,ax=plt.subplots(figsize=(10,5));
    for market, q in z.groupby("market"): ax.plot(q.season,q.variance/q.noise_floor,marker="o",label=market)
    ax.axhline(1,color="black",ls="--",lw=.8); ax.set_ylabel("observed variance / binomial floor"); ax.set_title("Frozen-constant halves check"); ax.legend(); ax.grid(alpha=.25); fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=150); plt.close(fig)

if __name__ == "__main__": levels(); reliability(); halves()
