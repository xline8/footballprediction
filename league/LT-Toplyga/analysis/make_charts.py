"""Make Phase-A EDA charts from eda_numbers.json; no fitting."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
D = json.loads((HERE / "eda_numbers.json").read_text())
seasons, per = D["seasons"], D["per_season"]
fig, ax = plt.subplots(figsize=(9, 5)); ax.plot(seasons, [per[s]["goals_per_match"] for s in seasons], marker="o"); ax.set_title("Lithuania Toplyga goals per match"); ax.set_xlabel("Warehouse season"); ax.set_ylabel("Goals"); fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=140); plt.close(fig)
R = D["reliability"]; fig, ax = plt.subplots(figsize=(7, 5)); keys = list(R); ax.bar(keys, [R[k]["r"] or 0 for k in keys]); ax.set_ylim(-1, 1); ax.set_title("Career split-half trait reliability"); fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=140); plt.close(fig)
H = D["halves"]; fig, ax = plt.subplots(figsize=(6, 4)); ax.bar(["Pre-virgin frozen"], [H["constant_frozen"]]); ax.axhline(.5, color="gray", lw=1); ax.set_ylim(0, 1); ax.set_title("First-half goals share (presentation constant)"); fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=140); plt.close(fig)
print("charts written")
