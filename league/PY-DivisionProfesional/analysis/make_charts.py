"""Step 4 charts for PY-DivisionProfesional (from the built CSV / frozen EDA numbers)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE.parent / "data" / "py_matches.csv")
out = HERE / "charts"; out.mkdir(exist_ok=True)
df["tot_goals"] = df.home_goals + df.away_goals
for c in ["shotsontarget", "corners", "yellow_cards", "total_shots"]:
    df[c + "_tot"] = df[c + "_home"] + df[c + "_away"]

g = df.groupby("season", sort=False)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(g.tot_goals.mean().index, g.tot_goals.mean().values, marker="o")
ax[0].set_title("Goals per match by tournament"); ax[0].tick_params(labelrotation=45)
st = df[df.has_stats == 1].groupby("season", sort=False)
ax[1].plot(st.shotsontarget_tot.mean().index, st.shotsontarget_tot.mean().values, marker="o", label="SOT")
ax[1].plot(st.corners_tot.mean().index, st.corners_tot.mean().values, marker="o", label="corners")
ax[1].plot(st.total_shots_tot.mean().index, st.total_shots_tot.mean().values, marker="o", label="shots")
ax[1].plot(st.yellow_cards_tot.mean().index, st.yellow_cards_tot.mean().values, marker="o", label="cards (stats col)")
ax[1].set_title("Count levels — stats era only (2025+)"); ax[1].legend(); ax[1].tick_params(labelrotation=45)
fig.tight_layout(); fig.savefig(out / "levels_by_season.png", dpi=110); plt.close(fig)

traits = {"goals-for*": 0.79, "goals-against*": 0.70, "SOT-for": 0.83, "SOT-against": 0.66,
          "shots-for": 0.81, "shots-against": 0.78, "corners-for": 0.56, "corners-against": 0.47,
          "yellows-for": 0.37, "yellows-against": 0.51, "on-target rate": 0.48, "touches": 0.70}
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(list(traits), list(traits.values())); ax.set_xlabel("split-half r (*career; others stats era)")
ax.set_title("Trait reliability — PY-DivisionProfesional"); fig.tight_layout()
fig.savefig(out / "trait_reliability.png", dpi=110); plt.close(fig)

halves = {"goals": 0.418, "SOT": 0.442, "corners": 0.492, "total shots": 0.465, "cards": 0.327}
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.bar(list(halves), list(halves.values())); ax.set_ylabel("1H share (frozen constant)")
ax.set_title("Halves constants — per-match share variance ≈ noise (F3)"); fig.tight_layout()
fig.savefig(out / "halves_constants.png", dpi=110); plt.close(fig)
print("charts written", sorted(p.name for p in out.glob('*.png')))
