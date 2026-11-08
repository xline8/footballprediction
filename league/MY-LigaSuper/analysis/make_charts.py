"""Make the standard MY-LigaSuper Phase A EDA charts."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent; OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
x = json.loads((HERE / "eda_summary.json").read_text()); inv = json.loads((HERE / "inventory_summary.json").read_text()); seasons = list(x["levels_by_season"])
plt.style.use("seaborn-v0_8-whitegrid")

fig, ax = plt.subplots(figsize=(9, 5)); ax.plot(seasons, [x["levels_by_season"][s]["goals_per_match"] for s in seasons], marker="o", label="Goals/match"); ax.plot(seasons, [x["levels_by_season"][s]["OU2.5"] for s in seasons], marker="o", label="OU2.5"); ax.set_title("Malaysia Liga Super levels by season"); ax.set_ylabel("Rate / goals per match"); ax.legend(); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=150); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 5)); a = x["trait_reliability"]; labels = ["Dev era GF", "Dev era GA", "Scored GF", "Scored GA"]; vals = [a["dev_era_2021_2025"]["gf_r"], a["dev_era_2021_2025"]["ga_r"], a["scored_window_2022_2025"]["gf_r"], a["scored_window_2022_2025"]["ga_r"]]; ax.bar(labels, vals); ax.axhline(0, color="black", lw=.8); ax.set_ylim(-1, 1); ax.set_ylabel("Chronological split-half r"); ax.set_title("Team trait reliability"); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=150); plt.close(fig)
fig, ax = plt.subplots(figsize=(9, 5)); shares = [x["goals_1h_share"]["per_season"][s]["share"] for s in seasons]; ratios = [x["goals_1h_share"]["per_season"][s]["variance_ratio"] for s in seasons]; ax.plot(seasons, shares, marker="o", label="1H share"); ax.plot(seasons, ratios, marker="s", label="variance / noise"); ax.axhline(x["goals_1h_share"]["dev_pooled"]["share"], ls="--", label="frozen dev constant"); ax.axhline(1, ls=":", color="black"); ax.set_title("Halves constant and variance test"); ax.legend(); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=150); plt.close(fig)
fig, ax = plt.subplots(figsize=(9, 5)); keys = ["stats", "shotmap", "lineup", "referee"]; 
for k in keys: ax.plot(seasons, [inv["seasons"][s]["n"] - inv["seasons"][s]["coverage"][k] for s in seasons], marker="o", label=f"{k} absent")
ax.set_title("Malaysia Liga Super feed absences by season"); ax.set_ylabel("Matches absent"); ax.legend(); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(OUT / "coverage_by_season.png", dpi=150); plt.close(fig)
print("wrote", ", ".join(str(OUT / n) for n in ["levels_by_season.png", "coverage_by_season.png", "trait_reliability.png", "halves_constants.png"]))
