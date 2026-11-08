#!/usr/bin/env python3
"""EDA for IL-Leumit (goals-only corpus). Writes eda_summary.json.
Mover measurement uses Ligat ha'Al (league_id 127) team membership by
FotMob team ID, parsed from that league's warehouse JSONs (scores only).
Liga Alef (tier 3) is NOT in the warehouse, so up-movers into Leumit
are identified as entrants whose immediately preceding season was in
neither Leumit nor Ligat ha'Al; their entry-season performance in
Leumit (vs that season's league mean) is the measurable quantity.
"""
import csv, json, os, random, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "il_leumit_matches.csv")
MAIN = os.path.expanduser("~/workspace/footballprediction")
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
COMPLETE = SEASONS[:5]

rows = list(csv.DictReader(open(DATA)))
for r in rows:
    r["hg"], r["ag"] = int(r["home_goals"]), int(r["away_goals"])
    r["home_team_id"], r["away_team_id"] = int(r["home_team_id"]), int(r["away_team_id"])

def levels(rs):
    n = len(rs); g = [r["hg"] + r["ag"] for r in rs]
    return dict(n=n, goals_per_match=round(st.mean(g), 3),
                home_goals=round(st.mean([r["hg"] for r in rs]), 3),
                away_goals=round(st.mean([r["ag"] for r in rs]), 3),
                home_adv=round(st.mean([r["hg"] for r in rs]) - st.mean([r["ag"] for r in rs]), 3),
                hw_pct=round(100 * sum(r["hg"] > r["ag"] for r in rs) / n, 1),
                draw_pct=round(100 * sum(r["hg"] == r["ag"] for r in rs) / n, 1),
                aw_pct=round(100 * sum(r["hg"] < r["ag"] for r in rs) / n, 1),
                btts_pct=round(100 * sum(r["hg"] > 0 and r["ag"] > 0 for r in rs) / n, 1),
                over25_pct=round(100 * sum(x > 2.5 for x in g) / n, 1),
                dispersion=round(st.pvariance(g) / st.mean(g), 3))

by_season = {s: levels([r for r in rows if r["season"] == s]) for s in SEASONS}
phase = {p: levels([r for r in rows if r["phase"] == p and r["season"] in COMPLETE]) for p in ("regular", "split")}

# split-half reliability, career-pooled per team (goals for/against)
tm = defaultdict(list)  # team_id -> list of (gf, ga)
for r in rows:
    if r["season"] in COMPLETE:
        tm[r["home_team_id"]].append((r["hg"], r["ag"]))
        tm[r["away_team_id"]].append((r["ag"], r["hg"]))
rng = random.Random(42)
def split_half(idx):
    xs, ys = [], []
    for _ in range(60):
        a, b = [], []
        for tid, ms in tm.items():
            if len(ms) < 24: continue
            idxs = list(range(len(ms))); rng.shuffle(idxs)
            h = len(idxs) // 2
            a.append((tid, st.mean([ms[i][idx] for i in idxs[:h]])))
            b.append((tid, st.mean([ms[i][idx] for i in idxs[h:]])))
        bd = dict(b)
        xs += [v for t, v in a]; ys += [bd[t] for t, _ in a]
    # correlation per split then average is cleaner: redo per-split
    rs_ = []
    for _ in range(60):
        a, b = {}, {}
        for tid, ms in tm.items():
            if len(ms) < 24: continue
            idxs = list(range(len(ms))); rng.shuffle(idxs)
            h = len(idxs) // 2
            a[tid] = st.mean([ms[i][idx] for i in idxs[:h]])
            b[tid] = st.mean([ms[i][idx] for i in idxs[h:]])
        ks = sorted(a)
        xa = [a[k] for k in ks]; xb = [b[k] for k in ks]
        ma, mb = st.mean(xa), st.mean(xb)
        cov = sum((x - ma) * (y - mb) for x, y in zip(xa, xb))
        rs_.append(cov / (sum((x - ma) ** 2 for x in xa) * sum((y - mb) ** 2 for y in xb)) ** 0.5)
    return round(st.mean(rs_), 3), len([1 for ms in tm.values() if len(ms) >= 24])
rel = {"goals_for": split_half(0), "goals_against": split_half(1)}

# --- movers ---
idx = [r for r in csv.DictReader(open(os.path.join(MAIN, "data_enrichment/fotmob_world_index.csv"))) if r["league_id"] == "127"]
haal_teams = defaultdict(set)  # season -> team ids
for r in idx:
    d = json.load(open(os.path.join(MAIN, r["path"])))
    haal_teams[r["season"]].add(d["general"]["homeTeam"]["id"]); haal_teams[r["season"]].add(d["general"]["awayTeam"]["id"])
leumit_teams = {s: set() for s in SEASONS}
for r in rows: leumit_teams[r["season"]].add(r["home_team_id"]); leumit_teams[r["season"]].add(r["away_team_id"])
movers = []
for i in range(1, 5):  # entry seasons 2022/23..2025/26 (complete seasons only)
    s, prev = COMPLETE[i], COMPLETE[i - 1]
    entrants = leumit_teams[s] - leumit_teams[prev]
    mu = st.mean([r["hg"] + r["ag"] for r in rows if r["season"] == s]) / 2
    for tid in sorted(entrants):
        kind = "down_from_haal" if tid in haal_teams[prev] else "up_from_tier3"
        ms = [(r["hg"], r["ag"]) if r["home_team_id"] == tid else (r["ag"], r["hg"])
              for r in rows if r["season"] == s and tid in (r["home_team_id"], r["away_team_id"])]
        gf = st.mean([m[0] for m in ms]); ga = st.mean([m[1] for m in ms])
        movers.append(dict(season=s, team_id=tid, kind=kind, n=len(ms),
                           gf=round(gf, 3), ga=round(ga, 3), mu=round(mu, 3),
                           gf_delta=round(gf - mu, 3), ga_delta=round(ga - mu, 3)))
def agg(kind):
    ms = [m for m in movers if m["kind"] == kind]
    return dict(n_team_seasons=len(ms), gf_delta=round(st.mean([m["gf_delta"] for m in ms]), 3),
                ga_delta=round(st.mean([m["ga_delta"] for m in ms]), 3)) if ms else None
mover_summary = {"down_from_haal": agg("down_from_haal"), "up_from_tier3": agg("up_from_tier3"),
                 "all": dict(n_team_seasons=len(movers),
                             gf_delta=round(st.mean([m["gf_delta"] for m in movers]), 3),
                             ga_delta=round(st.mean([m["ga_delta"] for m in movers]), 3)) if movers else None}

out = dict(by_season=by_season, phase_complete_seasons=phase, split_half_reliability=rel,
           movers=movers, mover_summary=mover_summary)
json.dump(out, open(os.path.join(HERE, "eda_summary.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
