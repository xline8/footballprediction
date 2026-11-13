"""Replication of the closed V10 star-absence question on J1 (2022+),
run because the corpus has lineups + shotmap the top-5 test also had --
the agreed standard for reopening would be NEW reliability evidence.
Protocol mirrors V10: star = player with the largest share of his team's
SOT over the trailing 10 team matches, share >= 25%; absence = not in the
matchday squad (starters + subs); expectation = team's trailing-10 mean
SOT (stats feed); residual = actual - expected; control = star starts.
Result (2026-11-09): absent n=107, residual +0.035 (95% CI -0.34..+0.41)
vs control +0.042; no dose pattern. Null replicated -- book stays closed.
"""
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from jleague_lib import flat_stats, iter_files, load, shots_of


def main():
    records = []
    for lg, season, path in iter_files():
        if lg != "J1" or season == "2021":
            continue
        d = load(path)
        g, c = d.get("general") or {}, d.get("content") or {}
        fs = flat_stats(c)
        shots = shots_of(c)
        lu = c.get("lineup") or {}
        for side, oside in (("homeTeam", 0), ("awayTeam", 1)):
            tid = (g.get(side) or {}).get("id")
            sot = (fs.get(("All", "ShotsOnTarget")) or (None, None))[oside]
            ps = defaultdict(int)
            for s in shots:
                if s.get("teamId") == tid and s.get("isOnTarget") and not s.get("isBlocked"):
                    ps[s.get("playerId")] += 1
            team = lu.get(side) or {}
            starters = {p.get("id") for p in team.get("starters") or []}
            subs = {p.get("id") for p in team.get("subs") or []}
            records.append({"date": (g.get("matchTimeUTCDate") or "")[:10],
                            "team": tid, "sot": sot, "ps": dict(ps),
                            "starters": starters, "squad": starters | subs})
    records.sort(key=lambda r: r["date"])
    hist = defaultdict(list)
    cases, controls = [], []
    for r in records:
        h = hist[r["team"]]
        if len(h) >= 8 and r["sot"] is not None:
            win = h[-10:]
            exp = np.mean([x["sot"] for x in win])
            tot = defaultdict(int)
            for x in win:
                for pid, v in x["ps"].items():
                    tot[pid] += v
            team_sot = sum(tot.values())
            if team_sot > 0:
                star, share = max(tot.items(), key=lambda kv: kv[1])
                share = share / team_sot
                if share >= 0.25:
                    resid = r["sot"] - exp
                    if star not in r["squad"]:
                        cases.append((resid, share))
                    elif star in r["starters"]:
                        controls.append((resid, share))
        hist[r["team"]].append(r)

    def summ(name, arr):
        if not arr:
            print(name, "n=0"); return
        v = np.array([a[0] for a in arr])
        se = v.std(ddof=1) / np.sqrt(len(v))
        print(f"{name}: n={len(v)} mean residual={v.mean():+.3f} "
              f"(95% CI [{v.mean() - 1.96 * se:+.3f}, {v.mean() + 1.96 * se:+.3f}])")

    summ("ABSENT", cases)
    summ("CONTROL", controls)
    summ("ABSENT share>=0.30", [c for c in cases if c[1] >= 0.30])
    summ("ABSENT 0.25<=share<0.30", [c for c in cases if c[1] < 0.30])


if __name__ == "__main__":
    main()
