"""Generate plain matplotlib charts from the generated UZ match CSV/EDA JSON."""

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent
CSV_PATH = ANALYSIS.parent / "data" / "uz_superliga_matches.csv"
EDA_PATH = ANALYSIS / "eda_summary.json"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(HERE / name, dpi=150)
    plt.close(fig)


def main():
    with CSV_PATH.open(newline="") as fh:
        ms = list(csv.DictReader(fh))
    eda = json.loads(EDA_PATH.read_text())
    rounds = eda["round_goals_per_match"]
    xs = [int(r) for r in rounds]
    ys = [rounds[str(r)]["goals_per_match"] for r in xs]
    mean = eda["levels"]["goals_per_match"]
    fig, ax = plt.subplots(figsize=(8, 4.5)); ax.plot(xs, ys, marker="o"); ax.axhline(mean, color="black", linestyle="--", label=f"Pooled mean {mean:.3f}")
    ax.set(xlabel="Round", ylabel="Goals per match", title="UZ Superliga 2026 goals per match by round"); ax.legend(); save(fig, "goals_per_round.png")

    team = eda["team_attack_defence"]
    fig, ax = plt.subplots(figsize=(7, 6))
    for t, d in team.items(): ax.scatter(d["gf_per_match"], d["ga_per_match"]); ax.annotate(t, (d["gf_per_match"], d["ga_per_match"]), xytext=(3, 3), textcoords="offset points", fontsize=8)
    ax.set(xlabel="Attack: GF per match", ylabel="Defence: GA per match", title="UZ Superliga team attack vs defence"); save(fig, "team_attack_defence.png")

    teams = sorted(team)
    # Recompute split rates from match rows so chart remains directly data-driven.
    split = {"first": {t: [0, 0] for t in teams}, "second": {t: [0, 0] for t in teams}}
    for m in ms:
        s = "first" if int(m["round"]) <= 13 else "second"
        for side, opp in (("home", "away"), ("away", "home")):
            split[s][m[side]][0] += int(m[f"{side}_goals"]); split[s][m[side]][1] += 1
    fig, ax = plt.subplots(figsize=(7, 6))
    for t in teams:
        x = split["first"][t][0] / split["first"][t][1]; y = split["second"][t][0] / split["second"][t][1]
        ax.scatter(x, y); ax.annotate(t, (x, y), xytext=(3, 3), textcoords="offset points", fontsize=8)
    ax.set(xlabel="GF per match, rounds 1–13", ylabel="GF per match, rounds 14–27", title="UZ Superliga split-half attack reliability"); save(fig, "split_half_attack_reliability.png")

    l = eda["levels"]; ref = eda["reference_points"]
    labels = ["Home win", "Draw", "Away win", "Over 2.5", "BTTS"]
    uz = [l["home_win_rate"], l["draw_rate"], l["away_win_rate"], l["over_2_5_rate"], l["btts_rate"]]
    j1 = [ref["J1_home_win_rate"], ref["J1_draw_rate"], ref["J1_away_win_rate"], ref["J1_over_2_5_rate"], ref["J1_btts_rate"]]
    pos = range(len(labels)); width = 0.38
    fig, ax = plt.subplots(figsize=(8, 4.5)); ax.bar([p - width / 2 for p in pos], uz, width, label="UZ Superliga 2026"); ax.bar([p + width / 2 for p in pos], j1, width, label="J1 reference")
    ax.set_xticks(list(pos), labels); ax.set_ylabel("Rate"); ax.set_ylim(0, 0.65); ax.set_title("Results and scoring traits: UZ vs J1 reference"); ax.text(0.01, 0.02, f"Goals/match: UZ {l['goals_per_match']:.3f}; J1 program reference {ref['J1_goals_per_match']:.2f}", transform=ax.transAxes, fontsize=9); ax.legend(); save(fig, "result_mix_vs_j1.png")


if __name__ == "__main__":
    main()
