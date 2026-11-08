#!/usr/bin/env python3
import csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); rows=list(csv.DictReader(open(os.path.join(HERE,"..","data","ge_matches.csv"))))
seasons=sorted({r["season"] for r in rows})
def agg(fn): return [fn([r for r in rows if r["season"]==s]) for s in seasons]
fig,ax=plt.subplots(1,2,figsize=(10,4))
ax[0].plot(seasons, agg(lambda m: sum(int(r["home_goals"])+int(r["away_goals"]) for r in m)/len(m)), marker="o"); ax[0].set_title("Goals per match by season"); ax[0].grid(alpha=.3)
ax[1].plot(seasons, agg(lambda m: sum(1 for r in m if int(r["home_goals"])>int(r["away_goals"]))/len(m)), marker="o", label="home win")
ax[1].plot(seasons, agg(lambda m: sum(1 for r in m if int(r["home_goals"])+int(r["away_goals"])>2)/len(m)), marker="s", label="over 2.5"); ax[1].legend(); ax[1].set_title("Outcome rates by season"); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(os.path.join(HERE,"charts","levels_by_season.png"), dpi=110)
fig,ax=plt.subplots(figsize=(5,4)); ax.bar(["GF","GA"],[0.817,0.963]); ax.set_title("Split-half trait reliability (dev 2021-2024)"); ax.set_ylim(0,1); plt.tight_layout(); plt.savefig(os.path.join(HERE,"charts","trait_reliability.png"), dpi=110)
fig,ax=plt.subplots(figsize=(6,4)); ax.plot(seasons, agg(lambda m: sum(int(r["goals_1h"]) for r in m)/max(1,sum(int(r["home_goals"])+int(r["away_goals"]) for r in m))), marker="o"); ax.axhline(0.4516, ls="--", color="r", label="frozen dev constant 0.4516"); ax.legend(); ax.set_title("1H goal share by season (event times)"); ax.grid(alpha=.3); plt.tight_layout(); plt.savefig(os.path.join(HERE,"charts","halves_constant.png"), dpi=110)
print("charts done")
