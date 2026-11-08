"""Stage A visualization for US-MLS. Plots only numbers frozen in
eda_summary.json (Phase 3), so charts can never drift from EDA.md."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
eda = json.loads((HERE / "eda_summary.json").read_text())

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=130); plt.close(fig); print("wrote", name)

ss = eda["seasons"]
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharex=True)
for ax, key, title, ref in ((axes[0], "goals", "Goals / match", None), (axes[1], "sot", "SOT / match", None), (axes[2], "yellow", "Yellows / match", None)):
    xs = list(ss.keys()); ax.plot(xs, [ss[s][key] for s in xs], marker="o")
    if ref: ax.axhline(ref, color="grey", ls="--", lw=1, label=f"top-5 ref {ref}")
    ax.set_title(title); ax.tick_params(labelrotation=30)
    if ref: ax.legend()
save(fig, "levels_by_season.png")

rel = eda["reliability"]; rt = eda["ratio_traits"]
traits = [("box touches for", rel["box_touches_for"]["r"]), ("shots for", rel["shots_for"]["r"]),
          ("xG for", rel["xg_for"]["r"]), ("SOT for", rel["sot_for"]["r"]),
          ("corners for", rel["corners_for"]["r"]), ("goals for", rel["goals_for"]["r"]),
          ("yellows for", rel["yellow_for"]["r"]), ("set-play xG share", rt["setplay_xg_share"]["r"]),
          ("xG / shot", rt["xg_per_shot"]["r"]), ("referee card rate", eda["referees"]["r"]),
          ("xGOT / shot (2024+)", rt["xgot_per_shot_era2024"]["r"]),
          ("finishing (G - xG)", rt["finishing_goals_minus_xg"]["r"]),
          ("on-target rate", rt["sot_rate"]["r"])]
labels = [t[0] for t in traits][::-1]; vals = [t[1] for t in traits][::-1]
colors = ["#2e7d32" if v >= 0.4 else ("#ef6c00" if v >= 0.3 else "#c62828") for v in vals]
fig, ax = plt.subplots(figsize=(8, 5.2))
ax.barh(labels, vals, color=colors); ax.axvline(0.3, color="grey", ls="--", lw=1)
ax.set_xlim(-0.2, 1); ax.set_title("US-MLS team-trait reliability, split-half r\nred < 0.3 = noise zone")
for i, v in enumerate(vals): ax.text(v + 0.02, i, f"{v:.2f}", va="center")
save(fig, "trait_reliability.png")

h = eda["halves"]
names = ["goals", "SOT", "corners", "total shots", "yellow cards"]
shares = [h["goals"]["share"], h["sot"]["share"], h["corners"]["share"], h["shots"]["share"], h["yellow"]["share"]]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f"); ax.axhline(0.5, color="grey", ls="--", lw=1); ax.set_ylim(0, 0.6)
ax.set_title("US-MLS frozen first-half shares — presentation constants only")
for i, v in enumerate(shares): ax.text(i, v + 0.015, f"{v:.3f}", ha="center")
save(fig, "halves_constants.png")

fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
axes[0].bar(["referee card-rate\nsplit-half r"], [eda["referees"]["r"]], color="#2e7d32"); axes[0].set_ylim(0, 1)
axes[0].set_title("Referee strictness is a trait")
ct = eda["corners_territorial"]
axes[1].bar(["opp-box touches", "possession"], [ct["corr_corners_boxtouches"], ct["corr_corners_possession"]], color=["#2e7d32", "#90a4ae"])
axes[1].set_ylim(0, 0.65); axes[1].set_title("Per-match corr with team corners")
save(fig, "referee_and_territory.png")
print("charts done ->", OUT)
