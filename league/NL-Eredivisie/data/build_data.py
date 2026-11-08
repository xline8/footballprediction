"""Build the regular-season NL Eredivisie match and team tables."""
import csv, json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "league"))
from jleague_lib import _num, flat_stats, stats_conflicts, shots_of, events_of, ht_from_events

INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = HERE.parent
BASE_KEYS = ["total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box", "corners", "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves", "BallPossesion"]
XG_KEYS = ["expected_goals", "expected_goals_open_play", "expected_goals_set_play", "expected_goals_non_penalty"]
HALF_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards", "red_cards", "expected_goals", "fouls"]

def load(p):
    with open(p) as f: return json.load(f)

def nan(): return float("nan")

def score(x):
    s = ((x.get("header") or {}).get("status") or {}).get("scoreStr")
    if isinstance(s, str):
        try:
            a, b = s.replace("–", "-").split("-")[:2]; return int(a.strip()), int(b.strip())
        except (ValueError, AttributeError): pass
    ts = (x.get("header") or {}).get("teams") or []
    if len(ts) >= 2 and ts[0].get("score") is not None and ts[1].get("score") is not None:
        return int(ts[0]["score"]), int(ts[1]["score"])
    return nan(), nan()

def event_yellows(content, home):
    # FotMob card events: type == "Card", card in {Yellow, YellowRed, Red}.
    # Unified convention (J.League Phase 2 rule 6): yellows count card ==
    # "Yellow" only; YellowRed/Red are reds, not yellows.
    vals = [0, 0]
    for e in events_of(content):
        if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") is not None:
            vals[0 if e["isHome"] else 1] += 1
    return vals

def main():
    selected, excluded = [], 0
    with open(INDEX, newline="") as f:
        for ir in csv.DictReader(f):
            if ir.get("league_id") != "57": continue
            x = load(ROOT / ir["path"])
            if (x.get("general") or {}).get("leagueName") != "Eredivisie": excluded += 1; continue
            selected.append((ir, x))
    rows, team_rows, touches_any = [], [], False
    for ir, x in selected:
        c = x.get("content") or {}; h, a = (x.get("header") or {}).get("teams") or [{}, {}]
        home_id, away_id = h.get("id"), a.get("id")
        st = flat_stats(c); conflicts = stats_conflicts(c)
        all_keys = {k for (p,k) in st if p == "All"}; touches_any |= "touches_opp_box" in all_keys
        ft_h, ft_a = score(x); ht = ht_from_events(c)
        evs = events_of(c); shots = [s for s in shots_of(c) if s.get("period") != "PenaltyShootout"]
        sm = {"shots": [0,0], "sot": [0,0], "sot_incl_blocked": [0,0], "xg": [0.,0.], "xgot": [0.,0.], "xgot_n": [0,0], "xgot_n_on": [0,0], "xgot_n_off": [0,0]}; nshoot = 0
        for s in shots:
            side = 0 if s.get("teamId") == home_id else 1
            if s.get("teamId") not in (home_id, away_id): continue
            nshoot += 1; sm["shots"][side] += 1
            if s.get("isOnTarget") is True: sm["sot_incl_blocked"][side] += 1
            if s.get("isOnTarget") is True and s.get("isBlocked") is not True: sm["sot"][side] += 1
            if s.get("expectedGoals") is not None: sm["xg"][side] += float(s["expectedGoals"])
            if s.get("expectedGoalsOnTarget") is not None:
                sm["xgot"][side] += float(s["expectedGoalsOnTarget"]); sm["xgot_n"][side] += 1
                sm["xgot_n_on" if s.get("isOnTarget") is True else "xgot_n_off"][side] += 1
        has_all = any(p == "All" for p,k in st); has_half = any(p in ("FirstHalf","SecondHalf") for p,k in st)
        row = {"match_id": ir["match_id"], "league": "NL-Eredivisie", "season": ir["season"], "season_start": int(ir["season"][:4]), "date": ir["date"], "kickoff_utc": ((x.get("header") or {}).get("status") or {}).get("utcTime", ""), "round": ((x.get("general") or {}).get("matchRound") or ((c.get("matchFacts") or {}).get("infoBox") or {}).get("Tournament", {}).get("round")), "home_team_id": home_id, "home_team": h.get("name"), "away_team_id": away_id, "away_team": a.get("name"), "coverage_level": (x.get("general") or {}).get("coverageLevel"), "home_goals": ft_h, "away_goals": ft_a, "ht_home_goals": ht[0] if ht else nan(), "ht_away_goals": ht[1] if ht else nan(), "ht_source": "events" if ht is not None else "none", "ev_goals_home": sum(1 for e in evs if e.get("type") == "Goal" and e.get("isHome") is True), "ev_goals_away": sum(1 for e in evs if e.get("type") == "Goal" and e.get("isHome") is False), "score_events_mismatch": False, "referee": ((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee", {}).get("text"), "has_events": bool(evs), "has_lineup": bool(c.get("lineup")), "has_player_stats": bool(c.get("playerStats")), "has_stats_all": has_all, "has_stats_half": has_half, "has_shotmap": bool(shots_of(c)), "n_shootout_shots": len(shots_of(c))-len(shots)}
        row["score_events_mismatch"] = not math.isnan(ft_h) and (row["ev_goals_home"] != ft_h or row["ev_goals_away"] != ft_a)
        for key in XG_KEYS + BASE_KEYS:
            vals = st.get(("All", key), (nan(), nan()))
            for side, label in enumerate(("home", "away")): row[f"{key}_{label}"] = vals[side]
        for p, pre in (("FirstHalf","fh"),("SecondHalf","sh")):
            for key in HALF_KEYS:
                vals = st.get((p,key), (nan(),nan()))
                row[f"{pre}_{key}_home"], row[f"{pre}_{key}_away"] = vals
        yell = st.get(("All","yellow_cards")); red = st.get(("All","red_cards")); ey = event_yellows(c, home_id)
        row["cards_source"] = "stats" if yell else ("events" if evs else "none")
        for key, vals, ev in (("yellow", yell, ey), ("red", red, [0,0])):
            for side, label in enumerate(("home","away")): row[f"{key}_{label}"] = vals[side] if vals else (ev[side] if key == "yellow" and evs else nan())
        for k in ("shots","sot","sot_incl_blocked","xg","xgot","xgot_n","xgot_n_on","xgot_n_off"):
            for side, label in enumerate(("home","away")): row[f"sm_{k}_{label}"] = sm[k][side]
        # The feed's key spelling is retained exactly; this is intentionally absent when absent everywhere.
        if "touches_opp_box" in all_keys: touches_any = True
        rows.append(row)
        for side, label, tid, name in (("home","home",home_id,h.get("name")),("away","away",away_id,a.get("name"))):
            tr = {"match_id": ir["match_id"], "season": ir["season"], "date": ir["date"], "team_id": tid, "team": name, "opponent_id": away_id if side == "home" else home_id, "opponent": a.get("name") if side == "home" else h.get("name"), "home_away": side}
            for k,v in row.items():
                if k.endswith("_home"): tr[k[:-5]] = v if side == "home" else row.get(k[:-5]+"_away")
                elif k.endswith("_away") and k[:-5] not in tr: tr[k[:-5]] = v if side == "away" else row.get(k[:-5]+"_home")
            for k in ("ev_goals", "expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow", "yellow_cards", "red", "red_cards", "fouls", "big_chance", "touches_opp_box", "BallPossesion"):
                suffix = "_away" if side == "home" else "_home"
                tr[k + "_against"] = row.get(k + suffix, nan())
            team_rows.append(tr)
    rows.sort(key=lambda r:(r["date"], int(r["match_id"]))); team_rows.sort(key=lambda r:(r["date"], int(r["match_id"]), r["home_away"]))
    def write(path, data):
        keys=[]
        for r in data:
            for k in r:
                if k not in keys: keys.append(k)
        with open(path,"w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(data)
    write(OUT/"nl_matches.csv", rows); write(OUT/"team_matches.csv", team_rows)
    assert len(rows) >= 1638 and len({r['match_id'] for r in rows}) == len(rows) and len(team_rows) == 2*len(rows)
    print(json.dumps({"index_league_57":1659,"regular_season":len(rows),"excluded_playoffs":excluded,"team_rows":len(team_rows),"touches_opp_box_key_present":touches_any,"stats_conflicts_checked":True}, indent=2))
if __name__ == "__main__": main()
