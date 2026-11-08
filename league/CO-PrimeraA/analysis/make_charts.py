"""Charts for CO-PrimeraA EDA (Step 4). Reads eda data from the built CSV."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
rows = list(csv.DictReader(open(HERE.parent / "data" / "co_primeraa_matches.csv", encoding="utf-8")))
SEASONS = ["2021 - Apertura", "2021 - Clausura", "2022 - Apertura", "2022 - Clausura",
           "2023 - Apertura", "2023 - Clausura", "2024 - Apertura", "2024 - Clausura",
           "2025 - Apertura", "2025 - Clausura", "2026 - Apertura", "2026 - Clausura"]
LAB = [s.replace(" - ", "\n") for s in SEASONS]

def fnum(r, k):
    v = r.get(k); return None if v in (None, "") else float(v)
def mean(xs):
    xs = [x for x in xs if x is not None]; return sum(xs) / len(xs) if xs else None
def tot(r, kh, ka):
    a = fnum(r, kh); return None if a is None else a + (fnum(r, ka) or 0)

def save(fig, name):
    fig.savefig(OUT / name, dpi=130); plt.close(fig); print("wrote", name)

# levels by season
fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for ax, title, fn in (
    (axes[0, 0], "Goals per match", lambda r: int(r["home_goals"]) + int(r["away_goals"])),
    (axes[0, 1], "SOT per match", lambda r: tot(r, "shotsontarget_home", "shotsontarget_away")),
    (axes[1, 0], "Corners per match", lambda r: tot(r, "corners_home", "corners_away")),
    (axes[1, 1], "Total shots per match", lambda r: tot(r, "total_shots_home", "total_shots_away"))):
    vals = [mean([fn(r) for r in rows if r["season"] == s]) for s in SEASONS]
    ax.plot(LAB, vals, marker="o"); ax.set_title(title); ax.tick_params(labelsize=7)
    ax.axvline(10.5, color="grey", ls="--", lw=0.8)
fig.suptitle("CO-PrimeraA levels by tournament (dashed = in-progress 2026-Cl, excluded)")
fig.tight_layout(); save(fig, "levels_by_season.png")

# trait reliability (split-half r, from EDA)
traits = [("goals for", 0.793), ("goals against", 0.506), ("SOT for", 0.828), ("SOT against", 0.228),
          ("corners for", 0.452), ("corners against", 0.565), ("shots for", 0.684), ("shots against", 0.598),
          ("yellows(stats) for", 0.547), ("yellows(ev,era) for", 0.585), ("opp-box touches for", 0.451),
          ("big chances for", 0.744), ("on-target rate", 0.774), ("referee strictness (era)", 0.487)]
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh([t[0] for t in traits][::-1], [t[1] for t in traits][::-1])
ax.axvline(0.3, color="red", ls="--"); ax.set_xlabel("split-half r")
ax.set_title("CO-PrimeraA team-trait reliability (red < 0.3 = noise zone)")
fig.tight_layout(); save(fig, "trait_reliability.png")

# halves constants
fig, ax = plt.subplots(figsize=(8, 4))
names = ["goals", "SOT", "corners", "total shots", "cards"]
vals = [0.4706, 0.4862, 0.4956, 0.4850, 0.3543]
ax.bar(names, vals); ax.set_ylabel("1H share")
ax.set_title("CO-PrimeraA frozen first-half shares — presentation only\nper-match true variance of the share ≈ 0 for every market")
fig.tight_layout(); save(fig, "halves_constants.png")

# movers
fig, ax = plt.subplots(figsize=(8, 4.5))
clubs = ["2022\nIntl Palmira", "2022\nU. Magdalena", "2023\nAtl. Huila", "2023\nChico",
         "2024\nPatriotas", "2024\nFortaleza", "2025\nLlaneros", "2025\nU. Magdalena"]
dgf = [-0.303, -0.353, -0.183, -0.154, -0.271, -0.008, -0.219, -0.244]
dga = [+0.247, +0.272, +0.292, -0.046, +0.334, -0.034, +0.181, +0.356]
x = range(len(clubs))
ax.bar([i - 0.2 for i in x], dgf, width=0.4, label="ΔGF/match")
ax.bar([i + 0.2 for i in x], dga, width=0.4, label="ΔGA/match")
ax.axhline(0, color="black", lw=0.8); ax.set_xticks(list(x)); ax.set_xticklabels(clubs, fontsize=7)
ax.legend(); ax.set_title("Promoted clubs' first Primera A year vs league mean (dev era 2022–2025)\nattack weaker in 8/8, defence weaker in 6/8 → X2 arm")
fig.tight_layout(); save(fig, "movers.png")
