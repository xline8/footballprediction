"""NI-Premiership charts, adapted from LU-NationalDivision."""
import csv, math
from collections import defaultdict
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent; CSV=HERE.parent/"data"/"ni_matches.csv"; OUT=HERE/"charts"; OUT.mkdir(exist_ok=True)
rows=list(csv.DictReader(open(CSV)))
for r in rows:
    for k in ("home_goals","away_goals"): r[k]=int(r[k])
    r["g"]=r["home_goals"]+r["away_goals"]; r["regular"]=r["phase"]=="regular"
    r["g1"]=None if r["goals_1h"]=="" else int(r["goals_1h"])
seasons=sorted({r["season"] for r in rows}); short={s:s.replace("20", "", 1).replace("/", "-") for s in seasons}
def pearson(x,y):
    mx,my=sum(x)/len(x),sum(y)/len(y); return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
def rel(ss):
    x1=[];x2=[];y1=[];y2=[]
    for s in ss:
        rs=sorted([r for r in rows if r["regular"] and r["season"]==s],key=lambda r:(r["date"],r["match_id"])); f=defaultdict(list);a=defaultdict(list)
        for r in rs: f[r["home_team_id"]].append(r["home_goals"]);a[r["home_team_id"]].append(r["away_goals"]);f[r["away_team_id"]].append(r["away_goals"]);a[r["away_team_id"]].append(r["home_goals"])
        for t in f:
            h=len(f[t])//2
            if h>=5: x1.append(sum(f[t][:h])/h);x2.append(sum(f[t][h:])/(len(f[t])-h));y1.append(sum(a[t][:h])/h);y2.append(sum(a[t][h:])/(len(a[t])-h))
    return pearson(x1,x2),pearson(y1,y2),len(x1)

fig,ax=plt.subplots(figsize=(8,4.5)); tot=[];hw=[];ou=[]
for s in seasons:
    rs=[r for r in rows if r["regular"] and r["season"]==s]; n=len(rs);tot.append(sum(r["g"] for r in rs)/n);hw.append(sum(r["home_goals"]>r["away_goals"] for r in rs)/n);ou.append(sum(r["g"]>2 for r in rs)/n)
x=range(len(seasons));ax.plot(x,tot,"o-",label="goals/match");ax.plot(x,ou,"s-",label="OU2.5 over-rate");ax.plot(x,hw,"^-",label="home-win rate");ax.set_xticks(list(x));ax.set_xticklabels([short[s] for s in seasons]);ax.set_ylim(0,4);ax.set_title("NI-Premiership: levels by season (2026/27 partial)");ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(OUT/"levels_by_season.png",dpi=120);plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5)); cov={"scores":[],"goal events":[],"stats feed":[],"shotmap":[],"referee named":[],"yellows":[]}
for s in seasons:
    rs=[r for r in rows if r["season"]==s];n=len(rs);cov["scores"].append(100);cov["goal events"].append(100*sum(int(r["goal_events"])==r["g"] for r in rs)/n);cov["stats feed"].append(0);cov["shotmap"].append(0);cov["referee named"].append(0);cov["yellows"].append(0)
for k,v in cov.items():ax.plot(x,v,"o-",label=k)
ax.set_xticks(list(x));ax.set_xticklabels([short[s] for s in seasons]);ax.set_ylim(-5,105);ax.set_ylabel("% of matches");ax.set_title("NI-Premiership: field coverage by season (scores-only league)");ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(OUT/"coverage_by_season.png",dpi=120);plt.close(fig)

rd=rel(seasons[:4]);rs=rel(seasons[1:4]);fig,ax=plt.subplots(figsize=(8,4.5));vals=[rd[0],rd[1],rs[0],rs[1]];labels=["GF dev-era\n(n=48)","GA dev-era\n(n=48)","GF scored\n(n=36)","GA scored\n(n=36)"];ax.bar(labels,vals,color=["#2c7bb6","#d7191c"]*2);ax.set_ylim(0,1);ax.set_ylabel("split-half r");ax.set_title("NI-Premiership: team trait reliability (goals)");[ax.text(i,v+.03,f"{v:.3f}",ha="center") for i,v in enumerate(vals)];ax.grid(axis="y",alpha=.3);fig.tight_layout();fig.savefig(OUT/"trait_reliability.png",dpi=120);plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5));shares=[];ses=[];ns=[]
for s in seasons:
    rs0=[r for r in rows if r["regular"] and r["season"]==s and r["g1"] is not None];g1=sum(r["g1"] for r in rs0);g=sum(r["g"] for r in rs0);p=g1/g;shares.append(p);ses.append(math.sqrt(p*(1-p)/g));ns.append(g)
ax.errorbar(x,shares,yerr=ses,fmt="o-",capsize=4,label="1H share ± 1 SE");ax.axhline(.4376,color="red",linestyle="--",label="dev scored constant 0.4376");ax.set_xticks(list(x));ax.set_xticklabels([f"{short[s]}\n(n={n})" for s,n in zip(seasons,ns)]);ax.set_ylim(.30,.55);ax.set_ylabel("1H share of goals");ax.set_title("NI-Premiership: goals 1H share by season");ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(OUT/"halves_constants.png",dpi=120);plt.close(fig)
print("charts written:",sorted(p.name for p in OUT.glob("*.png")));print("split-half dev-era GF/GA:",round(rd[0],3),round(rd[1],3));print("split-half scored GF/GA:",round(rs[0],3),round(rs[1],3))
