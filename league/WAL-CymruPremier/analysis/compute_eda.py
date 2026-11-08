"""Recompute the frozen Wales Phase A EDA from wal_matches.csv."""
import csv, json
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
def load():
    with (ROOT/"data/wal_matches.csv").open(newline="", encoding="utf-8") as f: rows=list(csv.DictReader(f))
    for r in rows:
        for k in ("home_goals","away_goals","ht_home_goals","ht_away_goals","eligible"): r[k]=int(r[k]) if r[k] else 0
    return rows
def levels(rr):
    g=[r["home_goals"]+r["away_goals"] for r in rr]; n=len(rr)
    return {"n":n,"goals_per_match":sum(g)/n,"home_win":sum(r["home_goals"]>r["away_goals"] for r in rr)/n,"draw":sum(r["home_goals"]==r["away_goals"] for r in rr)/n,"away_win":sum(r["home_goals"]<r["away_goals"] for r in rr)/n,"over25":sum(x>2 for x in g)/n,"btts":sum(r["home_goals"]>0 and r["away_goals"]>0 for r in rr)/n}
def corr(x): return float(np.corrcoef(np.array(x).T)[0,1])
def reliability(rows, s):
    """Split-half reliability, per team: a team's matches in chronological
    order are split into odd-position (1st, 3rd, ...) vs even-position
    (2nd, 4th, ...) halves; attack = goals-for rate, defence = goals-against
    rate. Correlation across teams between the two halves."""
    rr = sorted((r for r in rows if r["season"] == s and r["eligible"]), key=lambda r: (r["date"], r["match_id"]))
    d = defaultdict(lambda: [[], []])
    seen = defaultdict(int)
    for r in rr:
        for side, opp in (("home", "away"), ("away", "home")):
            tid = r[f"{side}_team_id"]
            d[tid][seen[tid] % 2].append((r[f"{side}_goals"], r[f"{opp}_goals"]))
            seen[tid] += 1
    a = []; g = []
    for v in d.values():
        a.append((sum(x[0] for x in v[0]) / len(v[0]), sum(x[0] for x in v[1]) / len(v[1])))
        g.append((sum(x[1] for x in v[0]) / len(v[0]), sum(x[1] for x in v[1]) / len(v[1])))
    return {"n_team_seasons": len(d), "attack": round(corr(a), 3), "defence": round(corr(g), 3)}
def main():
    rows=load(); elig=[r for r in rows if r["eligible"]]; by={s:[r for r in elig if r["season"]==s] for s in SEASONS}
    out={"levels":{s:levels(by[s]) for s in SEASONS}|{"pooled":levels(elig)},"ou_ladder":{s:{f"over_{x}":sum(r["home_goals"]+r["away_goals"]>x for r in by[s])/len(by[s]) for x in (1,2,3)} for s in SEASONS},"trait_reliability":{s:reliability(rows,s) for s in SEASONS[:5]},"movers":{"incoming":{"2022/2023":["Airbus UK Broughton","Pontypridd United"],"2023/2024":["Colwyn Bay"],"2024/2025":["Briton Ferry Llansawel"],"2025/2026":["Llanelli"],"2026/2027":["Ammanford","Cambrian United","Holywell Town","Llandudno FC","Trefelin BGC","Airbus UK Broughton"]},"shrink_band_teams":0}}
    nz=[r for r in elig if r["home_goals"]+r["away_goals"]>0]; shares=[(r["ht_home_goals"]+r["ht_away_goals"])/(r["home_goals"]+r["away_goals"]) for r in nz]; noise=[.4444*.5556/(r["home_goals"]+r["away_goals"]) for r in nz]
    out["halves"]={"pooled_ht_goals":sum(r["ht_home_goals"]+r["ht_away_goals"] for r in elig),"pooled_ft_goals":sum(r["home_goals"]+r["away_goals"] for r in elig),"matches_with_goals":len(nz),"goals_1h_share":1456/3276,"by_season":{s:{"share":sum(r["ht_home_goals"]+r["ht_away_goals"] for r in by[s])/sum(r["home_goals"]+r["away_goals"] for r in by[s])} for s in SEASONS},"observed_variance":float(np.var(shares,ddof=1)),"binomial_noise_floor":float(np.mean(noise)),"excess_variance":float(np.var(shares,ddof=1)-np.mean(noise))}
    assert len(rows)==1103 and len(elig)==1087 and [round(out["levels"][s]["goals_per_match"],3) for s in SEASONS]==[2.938,3.073,2.948,3.010,2.896,3.323] and (out["halves"]["pooled_ht_goals"],out["halves"]["pooled_ft_goals"])==(1456,3276) and round(out["halves"]["observed_variance"],5)==.10565
    # Cross-check against the coordinator's independent payload-level computation
    # (same per-team chronological odd/even split, keyed by team id — the
    # name-keyed first pass was corrected: renames Pontypridd Town/United,
    # TNS/The New Saints must not split one club in two). The values below
    # are the check, not the source — trait_reliability above is computed.
    assert [(out["trait_reliability"][s]["attack"], out["trait_reliability"][s]["defence"]) for s in SEASONS[:5]] == [(0.702,0.862),(0.826,0.759),(0.780,0.598),(0.666,0.812),(0.495,0.453)]
    (HERE/"eda_numbers.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps({"levels":out["levels"],"halves":out["halves"],"reliability":out["trait_reliability"]},indent=2))
if __name__=="__main__": main()
