"""Recompute TZ inventory and EDA JSON from payloads and built CSVs."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = Path.home() / "workspace" / "footballprediction"
INDEX = REPO / "data_enrichment" / "fotmob_world_index.csv"
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]

def corr(a, b):
    return float(np.corrcoef(a, b)[0, 1]) if len(a) > 1 and np.std(a) and np.std(b) else None

def load():
    with (ROOT / "data/tz_matches.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("home_goals", "away_goals", "ht_home_goals", "ht_away_goals", "n_events", "n_goal_events", "n_card_events", "n_red_events", "eligible", "awarded", "has_events", "ht_suspect", "has_stats_all", "has_stats_half", "has_shotmap", "lineup_block", "has_lineup"):
            if r[k] not in ("", None): r[k] = int(r[k])
    return rows

def main():
    rows = load(); by = {s: [r for r in rows if r["season"] == s] for s in SEASONS}
    idx = list(csv.DictReader(INDEX.open(encoding="utf-8", newline="")))
    idx = [r for r in idx if r["league_id"] == "9066"]
    payloads = []
    identity_ex = []; date_ex = []; score_ex = []; event_score_ex = []; parent_ex = []; tournament_ex = []
    event_count = Counter(); card_types = Counter(); aw_inference = []
    for ir in idx:
        p = REPO / ir["path"]; d = json.loads(p.read_text(encoding="utf-8")); payloads.append(str(p))
        g = d.get("general") or {}; h = d.get("header") or {}; st = h.get("status") or {}
        c = d.get("content") or {}; facts = c.get("matchFacts") or {}; ev = ((facts.get("events") or {}).get("events") or [])
        home = g.get("homeTeam") or {}; away = g.get("awayTeam") or {}
        if (home.get("name"), away.get("name")) != (ir["home"], ir["away"]): identity_ex.append(ir["match_id"])
        if ((facts.get("infoBox") or {}).get("Match Date") or {}).get("utcTime", "")[:10] != ir["date"]: date_ex.append(ir["match_id"])
        hs, aws = h.get("teams", [{}, {}])[:2] if len(h.get("teams", [])) >= 2 else ({}, {})
        if (hs.get("score"), aws.get("score")) != tuple(map(int, ir["score"].split("-"))): score_ex.append(ir["match_id"])
        gc = [e for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
        eh = sum(bool(e.get("isHome")) for e in gc); ea = len(gc) - eh
        ixh, ixa = map(int, ir["score"].split("-"))
        if (eh, ea) != (ixh, ixa): event_score_ex.append({"match_id": ir["match_id"], "index": [ixh, ixa], "events": [eh, ea]})
        if g.get("leagueId") != 9066 or g.get("parentLeagueId") != 9066: parent_ex.append(ir["match_id"])
        info = facts.get("infoBox") or {}; t = info.get("Tournament") or {}
        if t.get("id") != 9066 or t.get("parentLeagueId") != 9066: tournament_ex.append(ir["match_id"])
        for e in ev:
            event_count[e.get("type", "")] += 1
            if e.get("type") == "Card": card_types[e.get("card", "")] += 1
        inferred = int(not ev and (ixh, ixa) in ((3, 0), (0, 3)))
        payload_aw = int(st.get("awarded") is True or (st.get("reason") or {}).get("short") == "AW")
        aw_inference.append((ir["match_id"], inferred, payload_aw))
    levels = {}; coverage = {}; team_sets = {}
    for s, rr in by.items():
        e = [r for r in rr if r["eligible"]]
        goals = [r["home_goals"] + r["away_goals"] for r in e]
        hw = sum(r["home_goals"] > r["away_goals"] for r in e); dr = sum(r["home_goals"] == r["away_goals"] for r in e); aw = len(e) - hw - dr
        over = sum(g > 2 for g in goals); btts = sum(r["home_goals"] > 0 and r["away_goals"] > 0 for r in e); zz = sum(g == 0 for g in goals)
        levels[s] = {"n": len(e), "goals": round(sum(goals)/len(e), 6), "home_win": hw/len(e), "draw": dr/len(e), "away_win": aw/len(e), "over25": over/len(e), "btts": btts/len(e), "zerozero": zz/len(e), "home_goals": sum(r["home_goals"] for r in e)/len(e), "away_goals": sum(r["away_goals"] for r in e)/len(e)}
        team_sets[s] = sorted({r["home_team"] for r in rr} | {r["away_team"] for r in rr})
        coverage[s] = {"n": len(rr), "eligible": len(e), "events": sum(r["has_events"] for r in rr), "ht_derivable": sum(r["ht_source"] == "half_event" for r in rr), "stats_all": sum(r["has_stats_all"] for r in rr), "stats_half": sum(r["has_stats_half"] for r in rr), "shotmap_shots": sum(r["has_shotmap"] for r in rr), "lineup_blocks": sum(r["lineup_block"] for r in rr), "lineup_starters": sum(r["has_lineup"] for r in rr), "referee_nonempty": sum(bool(r["referee"]) for r in rr), "player_stats_nonnull": 0, "goals_index": sum(r["home_goals"] + r["away_goals"] for r in rr), "cards": sum(r["n_card_events"] for r in rr)}
    pooled = [r for r in rows if r["eligible"]]
    def level(rr):
        gs = [r["home_goals"] + r["away_goals"] for r in rr]; n = len(rr)
        return {"n": n, "goals": sum(gs)/n, "home_win": sum(r["home_goals"] > r["away_goals"] for r in rr)/n, "draw": sum(r["home_goals"] == r["away_goals"] for r in rr)/n, "away_win": sum(r["home_goals"] < r["away_goals"] for r in rr)/n, "over25": sum(g > 2 for g in gs)/n, "btts": sum(r["home_goals"] > 0 and r["away_goals"] > 0 for r in rr)/n, "zerozero": sum(g == 0 for g in gs)/n, "home_goals": sum(r["home_goals"] for r in rr)/n, "away_goals": sum(r["away_goals"] for r in rr)/n}
    trait = {}; trait_pairs = []
    for s in SEASONS:
        pairs = defaultdict(list)
        for r in sorted(by[s], key=lambda x: (x["date"], x["match_id"])):
            pairs[r["home_team"]].append((r["home_goals"], r["away_goals"])); pairs[r["away_team"]].append((r["away_goals"], r["home_goals"]))
        af=[]; al=[]; df=[]; dl=[]
        for team, vals in pairs.items():
            if len(vals) < 10: continue
            cut = len(vals)//2
            if cut < 5 or len(vals)-cut < 5: continue
            af.append(np.mean([v[0] for v in vals[:cut]])); al.append(np.mean([v[0] for v in vals[cut:]])); df.append(np.mean([v[1] for v in vals[:cut]])); dl.append(np.mean([v[1] for v in vals[cut:]]))
        trait[s] = {"n_team_seasons": len(af), "r_attack": corr(af, al), "r_defence": corr(df, dl)}
        trait_pairs.extend(zip(af, al, df, dl))
    trait_pool = {"n_team_seasons": len(trait_pairs), "r_attack": corr([x[0] for x in trait_pairs], [x[1] for x in trait_pairs]), "r_defence": corr([x[2] for x in trait_pairs], [x[3] for x in trait_pairs])}
    ht = {}; shares = []; noise = []
    for r in pooled:
        if r["ht_source"] == "half_event" and not r["ht_suspect"]:
            h = r["ht_home_goals"] + r["ht_away_goals"]; f = r["home_goals"] + r["away_goals"]
            shares.append(h/f if f else 0.0); noise.append((0.4625*(1-0.4625)/f) if f else 0.0)
    for s in SEASONS:
        x = [r for r in by[s] if r["eligible"] and r["ht_source"] == "half_event" and not r["ht_suspect"]]
        ht[s] = {"ht_matches": len(x), "ht_goals": sum(r["ht_home_goals"] + r["ht_away_goals"] for r in x), "share": sum(r["ht_home_goals"] + r["ht_away_goals"] for r in x)/sum(r["home_goals"]+r["away_goals"] for r in x)}
    team_ht = defaultdict(list)
    for r in sorted(pooled, key=lambda x: (x["date"], x["match_id"])):
        if r["ht_source"] != "half_event" or r["ht_suspect"]: continue
        f = r["home_goals"] + r["away_goals"]
        for team, h, g in ((r["home_team"], r["ht_home_goals"], r["home_goals"]), (r["away_team"], r["ht_away_goals"], r["away_goals"])):
            team_ht[(r["season"], team)].append((h, g))
    hpairs=[]
    for vals in team_ht.values():
        if len(vals) < 10: continue
        cut=len(vals)//2
        if cut<5 or len(vals)-cut<5: continue
        def sh(v): return sum(x[0] for x in v)/sum(x[1] for x in v) if sum(x[1] for x in v) else 0
        hpairs.append((sh(vals[:cut]), sh(vals[cut:])))
    eda = {"levels": {**levels, "pooled": level(pooled)}, "trait_reliability_per_season": trait, "trait_reliability_pooled": trait_pool, "halves": {"by_season": ht, "ht_goals_total": sum(x["ht_goals"] for x in ht.values()), "ht_matches": sum(x["ht_matches"] for x in ht.values()), "frozen_goals_1h_share": sum(r["ht_home_goals"]+r["ht_away_goals"] for r in pooled if r["ht_source"] == "half_event" and not r["ht_suspect"])/sum(r["home_goals"]+r["away_goals"] for r in pooled if r["ht_source"] == "half_event" and not r["ht_suspect"]), "per_match_share_obs_var": float(np.var(shares, ddof=1)), "per_match_share_binomial_floor": float(np.mean(noise)), "per_match_share_excess_var": float(np.var(shares, ddof=1)-np.mean(noise)), "team_season_1h_share_n": len(hpairs), "team_season_1h_share_split_half_r": corr([x[0] for x in hpairs], [x[1] for x in hpairs])}}
    inv = {"totals": {"index_rows": len(idx), "files_on_disk": len(set(payloads)), "unique_match_ids": len({r["match_id"] for r in idx}), "score_parse": len(rows), "eligible": sum(r["eligible"] for r in rows), "awarded": sum(r["awarded"] for r in rows), "total_goals": sum(r["home_goals"]+r["away_goals"] for r in rows), "events": sum(r["has_events"] for r in rows), "goal_events": sum(r["n_goal_events"] for r in rows), "cards": sum(r["n_card_events"] for r in rows), "red_events": sum(r["n_red_events"] for r in rows), "referee_nonempty": sum(bool(r["referee"]) for r in rows), "stats_nonempty": sum(r["has_stats_all"] for r in rows), "stats_half_nonempty": sum(r["has_stats_half"] for r in rows), "shotmap_nonempty": sum(r["has_shotmap"] for r in rows), "player_stats_nonnull": 0, "lineup_blocks": sum(r["lineup_block"] for r in rows), "lineup_starters": sum(r["has_lineup"] for r in rows), "ht_derivable": sum(r["ht_source"] == "half_event" for r in rows)}, "by_season": coverage, "agreements": {"identity": {"agree": len(rows)-len(identity_ex), "exceptions": identity_ex}, "date": {"agree": len(rows)-len(date_ex), "exceptions": date_ex}, "header_score": {"agree": len(rows)-len(score_ex), "exceptions": score_ex}, "goal_events_vs_index_score": {"agree": len(rows)-len(event_score_ex), "exceptions": event_score_ex}, "parent_league_id": {"agree": len(rows)-len(parent_ex), "exceptions": parent_ex}, "tournament_parent_id": {"agree": len(rows)-len(tournament_ex), "exceptions": tournament_ex}, "awarded_payload_vs_inference": {"agree": sum(a==b for _,a,b in aw_inference), "exceptions": [m for m,a,b in aw_inference if a!=b]}}, "event_types": dict(event_count), "card_values": dict(card_types), "team_counts": {"distinct_names": len({r["home_team"] for r in rows}|{r["away_team"]}), "by_season": {s: len(team_sets[s]) for s in SEASONS}}, "turnover": {"new_by_season": {s: sorted(set(team_sets[s]) - set(team_sets[SEASONS[i-1]])) if i else [] for i,s in enumerate(SEASONS)}, "out_by_season": {s: sorted(set(team_sets[SEASONS[i-1]]) - set(team_sets[s])) for i,s in enumerate(SEASONS) if i}}}
    inv["turnover"]["out_by_season"][SEASONS[0]] = []
    (HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=2, sort_keys=True)+"\n")
    (HERE / "eda_numbers.json").write_text(json.dumps(eda, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"inventory": inv["totals"], "agreements": {k:v["agree"] for k,v in inv["agreements"].items()}, "trait": trait_pool, "halves": eda["halves"]}, indent=2))

if __name__ == "__main__": main()
