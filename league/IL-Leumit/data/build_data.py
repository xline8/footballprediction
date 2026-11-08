#!/usr/bin/env python3
"""Build league/IL-Leumit/data/il_leumit_matches.csv from the FotMob world warehouse.

One row per played match, league_id=128 only. Team identity is keyed by
FotMob team ID (general.homeTeam.id / awayTeam.id); names are recorded
as the canonical (most frequent) name per ID plus any variant names.
Phase: rounds 1-30 = regular, 31-37 = split (frozen Step-1 fact).
Goals-only league: no stats/shotmap exist (0% coverage), so the CSV
carries fixture + score fields only. Nothing is fabricated.
Warehouse root resolution: this worktree's data_enrichment/ if the
per-match JSONs are present there, else the main checkout
~/workspace/footballprediction (warehouse is gitignored data).
"""
import csv, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MAIN = os.path.expanduser("~/workspace/footballprediction")

def warehouse_root():
    for base in (REPO, MAIN):
        idx = os.path.join(base, "data_enrichment", "fotmob_world_index.csv")
        if os.path.exists(idx):
            with open(idx) as f:
                for r in csv.DictReader(f):
                    if r["league_id"] == "128":
                        if os.path.exists(os.path.join(base, r["path"])):
                            return base
                        break
    sys.exit("warehouse JSONs not found under worktree or main checkout")

def main():
    base = warehouse_root()
    idx_path = os.path.join(base, "data_enrichment", "fotmob_world_index.csv")
    rows = [r for r in csv.DictReader(open(idx_path)) if r["league_id"] == "128"]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    name_votes = defaultdict(Counter)
    parsed = []
    for r in rows:
        d = json.load(open(os.path.join(base, r["path"])))
        g, h = d["general"], d["header"]
        hid, aid = g["homeTeam"]["id"], g["awayTeam"]["id"]
        name_votes[hid][g["homeTeam"]["name"]] += 1
        name_votes[aid][g["awayTeam"]["name"]] += 1
        hs, as_ = h["teams"][0]["score"], h["teams"][1]["score"]
        rnd = int(g["matchRound"])
        parsed.append(dict(match_id=r["match_id"], season=r["season"], date=r["date"],
                           round=rnd, phase=("regular" if rnd <= 30 else "split"),
                           home_team_id=hid, away_team_id=aid,
                           home_goals=hs, away_goals=as_))
    canon = {tid: c.most_common(1)[0][0] for tid, c in name_votes.items()}
    variants = {tid: sorted(n for n in c if n != canon[tid]) for tid, c in name_votes.items()}
    out = os.path.join(HERE, "il_leumit_matches.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["match_id", "season", "date", "round", "phase",
            "home_team_id", "home_team", "away_team_id", "away_team", "home_goals", "away_goals"])
        w.writeheader()
        for p in parsed:
            p["home_team"] = canon[p["home_team_id"]]
            p["away_team"] = canon[p["away_team_id"]]
            w.writerow(p)
    print(f"wrote {out}: {len(parsed)} rows, {len(canon)} distinct team IDs")
    for tid, vs in sorted(variants.items()):
        if vs:
            print(f"NAME VARIANT team_id={tid} canonical={canon[tid]!r} variants={vs}")

if __name__ == "__main__":
    main()
