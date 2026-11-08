"""Create the three Phase-A descriptive charts."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "eda_summary.json").read_text())
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
seasons, per = S["seasons"], S["per_season"]

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, specs in zip(axes, [("Goals / match", "goals_per_match"), ("Event yellows / match", "event_yellows_per_match")]):
    ax.bar(seasons, [per[s][specs[1]] for s in seasons], color="#37474f")
    ax.set_title(specs[0]); ax.tick_params(axis="x", labelrotation=35, labelsize=7)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=130); plt.close(fig)

traits = []
for label, key in (("goals-for", "goals"), ("goals-against", "goals"), ("yellows-for", "event_yellows"), ("yellows-against", "event_yellows")):
    direction = "for" if label.endswith("for") else "against"
    traits.append((label, S["reliability"][key][direction]["r"]))
fig, ax = plt.subplots(figsize=(7, 4)); ax.barh([x[0] for x in traits], [x[1] for x in traits], color="#2e7d32")
ax.axvline(0, color="grey", linewidth=1); ax.set_xlim(-1, 1); ax.set_title("SCO League One split-half reliability")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=130); plt.close(fig)

names = ["goals", "event yellows"]; vals = [S["halves"]["goals"]["share"], S["halves"]["event_yellows"]["share"]]
fig, ax = plt.subplots(figsize=(6, 3.8)); ax.bar(names, vals, color="#37474f"); ax.axhline(.5, color="grey", linestyle="--")
ax.set_ylim(0, .6); ax.set_title("Frozen first-half shares")
for i, v in enumerate(vals): ax.text(i, v+.015, f"{v:.4f}", ha="center")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
