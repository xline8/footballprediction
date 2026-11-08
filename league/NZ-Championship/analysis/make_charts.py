import csv, json
from pathlib import Path
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
data = list(csv.DictReader((HERE.parent / "data" / "nz_matches.csv").open()))
eda = json.load((HERE / "eda_summary.json").open())
out = HERE / "charts"; out.mkdir(exist_ok=True)
seasons = list(eda["levels"])
goals = [eda["levels"][s]["goals_per_match"] for s in seasons]
home = [eda["levels"][s]["home_goals_per_match"] for s in seasons]
away = [eda["levels"][s]["away_goals_per_match"] for s in seasons]
fig, ax = plt.subplots(figsize=(8, 4.5)); ax.plot(seasons, goals, "o-", label="total"); ax.plot(seasons, home, "o-", label="home"); ax.plot(seasons, away, "o-", label="away"); ax.set(ylabel="Goals per match", title="NZ-Championship levels by season"); ax.legend(); fig.tight_layout(); fig.savefig(out / "levels_by_season.png", dpi=160); plt.close(fig)
labels = ["Goals for", "Goals against"]; vals = [eda["f2"]["goals_for"]["r"], eda["f2"]["goals_against"]["r"]]
fig, ax = plt.subplots(figsize=(6, 4)); ax.bar(labels, vals, color=["#356cb6", "#e07a5f"]); ax.axhline(0, color="black", lw=.7); ax.set_ylim(-1, 1); ax.set_ylabel("Pearson r"); ax.set_title("Trait split-half reliability"); fig.tight_layout(); fig.savefig(out / "trait_reliabilities.png", dpi=160); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4)); ss = [eda["f3"]["by_season"][s]["share"] for s in ("2023", "2024", "2025", "2026")]; ax.plot(["2023", "2024", "2025", "2026"], ss, "o-", label="season 1H share"); ax.axhline(eda["f3"]["goals_1h_share"], color="black", ls="--", label="frozen pooled share"); ax.set_ylim(0, 1); ax.set_ylabel("1H goals / FT goals"); ax.set_title("Goals halves constant"); ax.legend(); fig.tight_layout(); fig.savefig(out / "halves_constants.png", dpi=160); plt.close(fig)
print("wrote", out / "levels_by_season.png", out / "trait_reliabilities.png", out / "halves_constants.png")
