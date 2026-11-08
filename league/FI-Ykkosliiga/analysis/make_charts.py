"""Simple matplotlib charts for the pre-fit FI-Ykkosliiga EDA."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; S=json.load(open(HERE/"eda_summary.json")); CH=HERE/"charts"; CH.mkdir(exist_ok=True)
seasons=S["seasons"]
fig,ax=plt.subplots(figsize=(8,4))
for key,label in (("goals","goals"),("home_win_rate","home win"),("over_2_5_rate","over 2.5")):
    ax.plot(seasons,[S["levels"][s][key] for s in seasons],marker="o",label=label)
ax.legend(); ax.set_title("FI-Ykkosliiga levels by season"); fig.tight_layout(); fig.savefig(CH/"levels_by_season.png",dpi=110); plt.close(fig)
tr=S["traits_odd_even"]
fig,ax=plt.subplots(figsize=(7,4)); keys=["goals_for","goals_against","yellow_for"]
ax.bar(keys,[tr[k]["r"] for k in keys]); ax.axhline(0,color="k",lw=.8); ax.set_title("Odd/even team-trait reliability"); fig.tight_layout(); fig.savefig(CH/"trait_reliability.png",dpi=110); plt.close(fig)
shares=S["halves_goals_by_season"]
fig,ax=plt.subplots(figsize=(7,4)); ax.plot(list(shares),[shares[s]["share"] for s in shares],marker="o"); ax.axhline(S["halves_goals_pooled"]["share"],ls="--",color="k",label="pooled"); ax.legend(); ax.set_title("Goals first-half share"); fig.tight_layout(); fig.savefig(CH/"halves_constants.png",dpi=110); plt.close(fig)
cov=S["cards_coverage"]
fig,ax=plt.subplots(figsize=(7,4)); ax.plot(seasons,[100*cov[s]["coverage"] for s in seasons],marker="o",label="Card-event coverage"); ax.plot(seasons,[100*S["inventory"][s]["referee_named"]/S["inventory"][s]["matches"] for s in seasons],marker="s",label="referee named"); ax.legend(); ax.set_ylim(0,105); ax.set_title("Referee and Card coverage (%)"); fig.tight_layout(); fig.savefig(CH/"referee_and_territory.png",dpi=110); plt.close(fig)
e=S.get("x2_entrants",[]); by={s:sum(1 for x in e if x["season"]==s) for s in seasons[1:]}
fig,ax=plt.subplots(figsize=(7,4)); ax.bar(list(by),list(by.values())); ax.set_title("Ykkösliiga entrants by season"); ax.set_ylabel("entrants"); fig.tight_layout(); fig.savefig(CH/"tier_gap.png",dpi=110); plt.close(fig)
print("charts done")
