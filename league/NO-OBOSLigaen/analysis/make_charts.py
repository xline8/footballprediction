"""Charts from the frozen eda_summary.json only."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
H=Path(__file__).parent; O=H/"charts"; O.mkdir(exist_ok=True); e=json.loads((H/"eda_summary.json").read_text())
def save(fig,n): fig.tight_layout(); fig.savefig(O/n,dpi=130); plt.close(fig)
s=e["seasons"]; xs=list(s)
fig,ax=plt.subplots(figsize=(9,4));
for k in ["goals","sot","corners","shots","yellow"]: ax.plot(xs,[s[x][k] for x in xs],marker="o",label=k)
ax.set_title("OBOS levels by season"); ax.legend(); save(fig,"levels_by_season.png")
r=e["reliability"]; names=list(r); fig,ax=plt.subplots(figsize=(8,5)); ax.barh(names,[r[x]["r"] for x in names]); ax.axvline(.3,color="grey",ls="--"); ax.set_title("Career-pooled split-half reliability"); save(fig,"trait_reliability.png")
h=e["halves"]; fig,ax=plt.subplots(figsize=(6,4)); ax.bar(["goals","cards"],[h[x]["share"] for x in h]); ax.axhline(.5,color="grey",ls="--"); ax.set_ylim(0,.6); ax.set_title("Event-derived first-half shares"); save(fig,"halves_constants.png")
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(["referee yellow rate"],[e["referee_reliability"]["r"]]); ax.set_ylim(0,1); ax.set_title("Referee event-yellow reliability"); save(fig,"referee_reliability.png")
print("charts done ->",O)
