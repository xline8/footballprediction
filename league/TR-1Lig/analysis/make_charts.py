"""Create Phase-A charts from eda_numbers.json; never fits models."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
N = json.load(open(HERE / "eda_numbers.json", encoding="utf-8")); S = N["corpus"]["seasons"]; P = N["per_season"]
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
def save(name): plt.tight_layout(); plt.savefig(OUT / name, dpi=160); plt.close()
plt.figure(figsize=(9,4.5)); plt.plot(S,[P[s]["goals"] for s in S],marker="o",label="goals"); plt.plot(S,[P[s]["stats"]["ShotsOnTarget"] or float("nan") for s in S],marker="o",label="SOT"); plt.plot(S,[P[s]["stats"]["corners"] or float("nan") for s in S],marker="o",label="corners"); plt.ylabel("mean per match"); plt.title("TR-1Lig levels by season"); plt.xticks(rotation=25); plt.legend(); save("levels_by_season.png")
R=N["reliability_dev"]; K=list(R); plt.figure(figsize=(8,4.5)); plt.bar(K,[R[k]["r"] or 0 for k in K]); plt.ylim(-.2,1); plt.ylabel("split-half r"); plt.title("DEV career-pooled trait reliability"); plt.xticks(rotation=30,ha="right"); save("trait_reliability.png")
G=N["goals_halves"]; plt.figure(figsize=(6,4)); plt.bar(["observed","binomial noise"],[G["obs_var"],G["binomial_noise_var"]]); plt.ylabel("variance"); plt.title("Goals halves: observed vs noise floor"); save("halves_constant.png")
