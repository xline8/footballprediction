"""F14 measurement: J1 yellow-card first-half share (frozen-constant check).

Mirrors the F3 instrument exactly (eda.py): stats-feed period splits from
the Phase 2 match table (rows with has_stats_half == True), per-match
share fh/ft on matches with ft > 0, true variance = observed variance of
the share minus the binomial noise floor mean(p(1-p)/ft), and team-level
split-half reliability via ratio-of-sums (min 24 matches/team, 60 reps,
odd/even first rep) -- the same helper and seed as eda.py.

Cross-check on the SAME match set: event-feed yellows (card == 'Yellow',
first half = time <= 45, the verified FotMob convention) from the raw
warehouse JSONs.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from jleague_lib import events_of, iter_files, load

DATA = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "cards_halves_summary.json"
rng = np.random.default_rng(20261109)


def load_csv(name):
    with open(DATA / name) as f:
        return list(csv.DictReader(f))


def num(rows, k):
    return np.array([np.nan if r[k] == "" else float(r[k]) for r in rows])


def split_half_ratio(num_by_team, den_by_team, min_matches=24, reps=60):
    """Split-half for ratio traits (ratio of sums, not mean of ratios).
    Copied verbatim from eda.py."""
    teams = [t for t in num_by_team if len(num_by_team[t]) >= min_matches]
    if len(teams) < 8:
        return len(teams), None
    rs = []
    for rep in range(reps):
        a, b = [], []
        ok = True
        for t in teams:
            n, d = num_by_team[t], den_by_team[t]
            idx = np.arange(len(n))
            mask = idx % 2 == 0 if rep == 0 else rng.random(len(n)) < 0.5
            if mask.sum() == 0 or (~mask).sum() == 0 or d[mask].sum() == 0 or d[~mask].sum() == 0:
                ok = False; break
            a.append(n[mask].sum() / d[mask].sum()); b.append(n[~mask].sum() / d[~mask].sum())
        if ok and np.std(a) > 0 and np.std(b) > 0:
            rs.append(np.corrcoef(a, b)[0, 1])
    return len(teams), (round(float(np.mean(rs)), 3) if rs else None)


S = {}
tm = load_csv("j1_matches.csv")
rows = [r for r in tm if r["has_stats_half"] == "True"]
S["population"] = {
    "source": "Phase 2 table j1_matches.csv, has_stats_half == True "
              "(FotMob stats-feed period splits; complete from 2024, 86% in 2023)",
    "n_matches_flagged": len(rows),
    "by_season": dict(sorted(Counter(r["season"] for r in rows).items())),
}

fh = num(rows, "fh_yellow_cards_home") + num(rows, "fh_yellow_cards_away")
sh = num(rows, "sh_yellow_cards_home") + num(rows, "sh_yellow_cards_away")
ft = num(rows, "yellow_cards_home") + num(rows, "yellow_cards_away")
S["coverage"] = {
    "fh_present": int(np.sum(~np.isnan(fh))),
    "ft_present": int(np.sum(~np.isnan(ft))),
    "split_sum_mismatch_rows": int(np.sum(~np.isnan(fh) & ~np.isnan(ft)
                                          & ((fh + sh) != ft))),
}
ok = (~np.isnan(fh)) & (~np.isnan(ft)) & (ft > 0)
fh_o, ft_o = fh[ok], ft[ok]
share = fh_o / ft_o
p = share.mean()
excess = share.var() - np.mean(p * (1 - p) / ft_o)
S["primary_stats_feed"] = {
    "n_matches": int(ok.sum()),
    "n_yellows": int(ft_o.sum()),
    "n_yellows_1h": int(fh_o.sum()),
    "constant_ratio_of_sums": round(float(fh_o.sum() / ft_o.sum()), 5),
    "mean_of_shares": round(float(p), 5),
    "share_sd": round(float(share.std()), 5),
    "true_var_excess": round(float(excess), 5),
    "noise_floor": round(float(np.mean(p * (1 - p) / ft_o)), 5),
    "observed_var": round(float(share.var()), 5),
}

# per-season decomposition (era mixing inflates the pooled excess if the
# share itself drifts by season -- check before reading the pooled number)
per_season = {}
for season in sorted({r["season"] for r in rows}):
    sr = [r for r in rows if r["season"] == season]
    sfh = num(sr, "fh_yellow_cards_home") + num(sr, "fh_yellow_cards_away")
    sft = num(sr, "yellow_cards_home") + num(sr, "yellow_cards_away")
    sok = (~np.isnan(sfh)) & (~np.isnan(sft)) & (sft > 0)
    ssh = sfh[sok] / sft[sok]
    sp = ssh.mean()
    per_season[season] = {
        "n_matches": int(sok.sum()),
        "n_yellows": int(sft[sok].sum()),
        "constant_ratio_of_sums": round(float(sfh[sok].sum() / sft[sok].sum()), 5),
        "true_var_excess": round(float(ssh.var() - np.mean(sp * (1 - sp) / sft[sok])), 5),
    }
S["per_season_stats_feed"] = per_season

# variance decomposition inside the complete era (2024+) alone
fh24v = num([r for r in rows if int(r["season_start"]) >= 2024],
            "fh_yellow_cards_home")
rows24b = [r for r in rows if int(r["season_start"]) >= 2024]
fh24b = num(rows24b, "fh_yellow_cards_home") + num(rows24b, "fh_yellow_cards_away")
ft24b = num(rows24b, "yellow_cards_home") + num(rows24b, "yellow_cards_away")
ok24b = (~np.isnan(fh24b)) & (~np.isnan(ft24b)) & (ft24b > 0)
sh24 = fh24b[ok24b] / ft24b[ok24b]
p24 = sh24.mean()
S["decomposition_2024plus"] = {
    "n_matches": int(ok24b.sum()),
    "mean_of_shares": round(float(p24), 5),
    "observed_var": round(float(sh24.var()), 5),
    "noise_floor": round(float(np.mean(p24 * (1 - p24) / ft24b[ok24b])), 5),
    "true_var_excess": round(float(sh24.var() - np.mean(p24 * (1 - p24) / ft24b[ok24b])), 5),
}

# sensitivity: 2024+ only (era where per-half stats are complete)
rows24 = [r for r in rows if int(r["season_start"]) >= 2024]
fh24 = num(rows24, "fh_yellow_cards_home") + num(rows24, "fh_yellow_cards_away")
ft24 = num(rows24, "yellow_cards_home") + num(rows24, "yellow_cards_away")
ok24 = (~np.isnan(fh24)) & (~np.isnan(ft24)) & (ft24 > 0)
S["sensitivity_2024plus"] = {
    "n_matches": int(ok24.sum()),
    "n_yellows": int(ft24[ok24].sum()),
    "constant_ratio_of_sums": round(float(fh24[ok24].sum() / ft24[ok24].sum()), 5),
}

# team-level split-half reliability, ratio of sums (fh yellows / ft yellows
# per team-match), built from the match table (team table has no fh yellow)
n_map, d_map = defaultdict(list), defaultdict(list)
for r in rows:
    for side in ("home", "away"):
        if r[f"fh_yellow_cards_{side}"] != "" and r[f"yellow_cards_{side}"] != "":
            n_map[r[f"{side}_team_id"]].append(float(r[f"fh_yellow_cards_{side}"]))
            d_map[r[f"{side}_team_id"]].append(float(r[f"yellow_cards_{side}"]))
nt, r = split_half_ratio({t: np.array(v) for t, v in n_map.items()},
                         {t: np.array(v) for t, v in d_map.items()},
                         min_matches=24)
S["team_1h_yellow_share_split_half"] = {"n_teams": nt, "r": r}

# cross-check: event-feed yellows on the SAME matches (time <= 45 = 1H)
primary_ids = {r["match_id"] for r, keep in zip(rows, ok) if keep}
ev_1h = ev_tot = 0
ev_matches = 0
ev_missing_time = 0
season_of = {r["match_id"]: r["season"] for r, keep in zip(rows, ok) if keep}
ev_season = defaultdict(lambda: [0, 0])
for lg, season, path in iter_files():
    if lg != "J1" or path.stem not in primary_ids:
        continue
    d = load(path)
    content = d.get("content") or {}
    cards = [e for e in events_of(content)
             if e.get("type") == "Card" and e.get("card") == "Yellow"]
    if not events_of(content):
        continue
    ev_matches += 1
    for e in cards:
        if e.get("time") is None:
            ev_missing_time += 1
            continue
        ev_tot += 1
        ev_season[season_of[path.stem]][1] += 1
        if e["time"] <= 45:
            ev_1h += 1
            ev_season[season_of[path.stem]][0] += 1
S["crosscheck_events"] = {
    "n_matches_with_events": ev_matches,
    "n_yellows_events": ev_tot,
    "n_yellows_1h_events": ev_1h,
    "share_1h_ratio_of_sums": round(ev_1h / ev_tot, 5) if ev_tot else None,
    "card_events_missing_time": ev_missing_time,
    "by_season": {s: {"n_1h": v[0], "n_total": v[1],
                      "share": round(v[0] / v[1], 5) if v[1] else None}
                  for s, v in sorted(ev_season.items())},
}

OUT.write_text(json.dumps(S, indent=1, ensure_ascii=False))
print(json.dumps(S, indent=1, ensure_ascii=False))
