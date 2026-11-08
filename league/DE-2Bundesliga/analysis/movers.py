"""Mover (entrant) analysis for DE-2Bundesliga -> movers.json.

Entrants = team ids present in season S but absent in S-1 (from the built
CSV). Direction: 'down' = relegated from the Bundesliga (FotMob id 54),
'up' = promoted from 3. Liga (id 208), classified by name-matching the
entrant against the neighbour leagues' previous-season membership in
fotmob_world_index.csv (verified: every entrant resolves to exactly one
neighbour; Arminia Bielefeld enters twice, down in 2022/2023 and up in
2025/2026, keyed by (season, name)).
"""
import csv, json, statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path("/home/hatch/workspace/footballprediction")
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "de2_matches.csv")))
IDX = list(csv.DictReader(open(MAIN / "data_enrichment" / "fotmob_world_index.csv")))
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]

def names(lid, season):
    s = set()
    for r in IDX:
        if r["league_id"] == lid and r["season"] == season:
            s.update([r["home"], r["away"]])
    return s

idname = {}
for r in ROWS:
    idname[r["home_team_id"]] = r["home_team"]; idname[r["away_team_id"]] = r["away_team"]
# CSV display name -> index name variants are the same strings for these clubs
prev_ids, out = None, {}
for s in SEASONS:
    ids = set()
    for r in ROWS:
        if r["season"] == s: ids.update([r["home_team_id"], r["away_team_id"]])
    if prev_ids is not None:
        entrants = ids - prev_ids
        bl, tl = names("54", SEASONS[SEASONS.index(s)-1]), names("208", SEASONS[SEASONS.index(s)-1])
        rec = {}
        for tid in sorted(entrants):
            nm = idname[tid]
            d = "down" if nm in bl else ("up" if nm in tl else "unknown")
            rec[nm] = d
        out[s] = rec
        out.setdefault("ids", {})[s] = {tid: ("down" if idname[tid] in bl else ("up" if idname[tid] in tl else "unknown")) for tid in sorted(entrants)}
    prev_ids = ids

def deltas(season_list):
    res = {}
    for d in ("up", "down"):
        gf, ga, lg = [], [], []
        for s in season_list:
            cur = {idname[k]: v for k, v in [(tid, None) for tid in []]}
            entr_ids = {tid for tid, nm in [(t, idname[t]) for t in
                          [r_ for r_ in set([x["home_team_id"] for x in ROWS if x["season"] == s] +
                                             [x["away_team_id"] for x in ROWS if x["season"] == s])]]
                        if out.get(s, {}).get(nm) == d}
            for r in ROWS:
                if r["season"] != s: continue
                lg += [int(r["home_goals"]), int(r["away_goals"])]
                for side, opp in (("home", "away"), ("away", "home")):
                    if r[f"{side}_team_id"] in entr_ids:
                        gf.append(int(r[f"{side}_goals"])); ga.append(int(r[f"{opp}_goals"]))
        res[d] = {"n_team_matches": len(gf), "gf": round(st.mean(gf), 3), "ga": round(st.mean(ga), 3),
                  "league_gf": round(st.mean(lg), 3), "gf_delta": round(st.mean(gf)-st.mean(lg), 3),
                  "ga_delta": round(st.mean(ga)-st.mean(lg), 3)}
    return res

out["deltas_by_season"] = {s: deltas([s]) for s in SEASONS[1:]}
out["deltas_dev_pooled"] = deltas(["2022/2023", "2023/2024", "2024/2025"])
Path(HERE / "movers.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
