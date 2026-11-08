"""Build the group-stage (regular-phase) AR Liga Profesional match and team tables.

Source: FotMob world warehouse, league_id 112 (Argentina Liga Profesional).
The warehouse window mixes two formats:
  - 2021-2024: one league tournament per calendar year (single round-robin;
    26 teams in 2021, 28 in 2022-2024).
  - 2025-2026: two tournaments per year (Apertura / Clausura), 30 teams in
    two zones, 16 group rounds (240 matches) + a 15-match playoff bracket.
Only the group / round-robin phase is modelled (playoffs excluded by design,
as in NL-Eredivisie). A match is a PLAYOFF match iff its leagueName contains
"Playoff" or its round label is a bracket label (1/8, 1/4, 1/2, final,
*Finals*, *Quarter-finals*, *Semi-finals*); group rounds are plain round
numbers ("1".."27") or "Clausura - Round N" (2026 Clausura). Team identity
is the FotMob team id (accent variants of a name share one id); the
canonical name per id is the spelling in the most recent match.
"""
import csv, json, math, re, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "league"))
from jleague_lib import _num, flat_stats, stats_conflicts, shots_of, events_of, ht_from_events

INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT = HERE.parent
BASE_KEYS = ["total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots", "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box", "corners", "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves", "BallPossesion"]
XG_KEYS = ["expected_goals", "expected_goals_open_play", "expected_goals_set_play", "expected_goals_non_penalty", "expected_goals_on_target"]
HALF_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards", "red_cards", "expected_goals", "fouls"]
BLOCK_ORDER = ["2021", "2022", "2023", "2024", "2025 - Apertura", "2025 - Clausura", "2026 - Apertura", "2026 - Clausura"]
EXPECTED_GROUP = {"2021": 325, "2022": 378, "2023": 378, "2024": 378, "2025 - Apertura": 240, "2025 - Clausura": 240, "2026 - Apertura": 240, "2026 - Clausura": 240}

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

def is_playoff(x):
    g = x.get("general") or {}
    name = g.get("leagueName") or ""
    rnd = str(g.get("matchRound") or "")
    if "Playoff" in name: return True
    low = rnd.lower()
    if low in ("1/8", "1/4", "1/2", "final"): return True
    if any(t in low for t in ("finals", "quarter", "semi", "- final")): return True
    if rnd.isdigit() or re.fullmatch(r"Clausura - Round \d+", rnd) or re.fullmatch(r"Apertura - Round \d+", rnd):
        return False
    raise ValueError(f"unclassified round label: {rnd!r} leagueName={name!r}")

def referee_text(c):
    ib = (c.get("matchFacts") or {}).get("infoBox") or {}
    rd = ib.get("Referee") or {}
    if isinstance(rd, dict):
        t = (rd.get("text") or "").strip()
        return t or None
    return None

def event_yellows(content, home):
    vals = [0, 0]
    for e in events_of(content):
        if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") is not None:
            vals[0 if e["isHome"] else 1] += 1
    return vals

def main():
    selected, excluded = [], 0
    canon = {}  # team_id -> (date, name); latest spelling wins
    with open(INDEX, newline="") as f:
        index_rows = [ir for ir in csv.DictReader(f) if ir.get("league_id") == "112"]
    loaded = []
    for ir in index_rows:
        x = load(ROOT / ir["path"])
        loaded.append((ir, x))
        for t in (x.get("header") or {}).get("teams") or []:
            tid, nm = t.get("id"), t.get("name")
            if tid is not None and nm and (tid not in canon or ir["date"] >= canon[tid][0]):
                canon[tid] = (ir["date"], nm)
    for ir, x in loaded:
        if is_playoff(x): excluded += 1; continue
        selected.append((ir, x))
    rows, team_rows, touches_any = [], [], False
    for ir, x in selected:
        c = x.get("content") or {}; h, a = (x.get("header") or {}).get("teams") or [{}, {}]
        home_id, away_id = h.get("id"), a.get("id")
        home_name = canon.get(home_id, ("", h.get("name")))[1]
        away_name = canon.get(away_id, ("", a.get("name")))[1]
        st = flat_stats(c); conflicts = stats_conflicts(c)
        all_keys = {k for (p, k) in st if p == "All"}; touches_any |= "touches_opp_box" in all_keys
        ft_h, ft_a = score(x); ht = ht_from_events(c)
        evs = events_of(c); shots = [s for s in shots_of(c) if s.get("period") != "PenaltyShootout"]
        sm = {"shots": [0, 0], "sot": [0, 0], "sot_incl_blocked": [0, 0], "xg": [0., 0.], "xgot": [0., 0.], "xgot_n": [0, 0], "xgot_n_on": [0, 0], "xgot_n_off": [0, 0]}
        for s in shots:
            if s.get("teamId") not in (home_id, away_id): continue
            side = 0 if s.get("teamId") == home_id else 1
            sm["shots"][side] += 1
            if s.get("isOnTarget") is True: sm["sot_incl_blocked"][side] += 1
            if s.get("isOnTarget") is True and s.get("isBlocked") is not True: sm["sot"][side] += 1
            if s.get("expectedGoals") is not None: sm["xg"][side] += float(s["expectedGoals"])
            if s.get("expectedGoalsOnTarget") is not None:
                sm["xgot"][side] += float(s["expectedGoalsOnTarget"]); sm["xgot_n"][side] += 1
                sm["xgot_n_on" if s.get("isOnTarget") is True else "xgot_n_off"][side] += 1
        has_all = any(p == "All" for p, k in st); has_half = any(p in ("FirstHalf", "SecondHalf") for p, k in st)
        row = {"match_id": ir["match_id"], "league": "AR-LigaProfesional", "season": ir["season"], "block_idx": BLOCK_ORDER.index(ir["season"]), "season_start": int(ir["season"][:4]), "date": ir["date"], "kickoff_utc": ((x.get("header") or {}).get("status") or {}).get("utcTime", ""), "round": str((x.get("general") or {}).get("matchRound")), "phase": "group", "home_team_id": home_id, "home_team": home_name, "away_team_id": away_id, "away_team": away_name, "coverage_level": (x.get("general") or {}).get("coverageLevel"), "home_goals": ft_h, "away_goals": ft_a, "ht_home_goals": ht[0] if ht else nan(), "ht_away_goals": ht[1] if ht else nan(), "ht_source": "events" if ht is not None else "none", "ev_goals_home": sum(1 for e in evs if e.get("type") == "Goal" and e.get("isHome") is True), "ev_goals_away": sum(1 for e in evs if e.get("type") == "Goal" and e.get("isHome") is False), "score_events_mismatch": False, "referee": referee_text(c), "has_events": bool(evs), "has_lineup": bool(c.get("lineup")), "has_player_stats": bool(c.get("playerStats")), "has_stats_all": has_all, "has_stats_half": has_half, "has_shotmap": bool(shots_of(c)), "n_shootout_shots": len(shots_of(c)) - len(shots)}
        row["score_events_mismatch"] = not math.isnan(ft_h) and (row["ev_goals_home"] != ft_h or row["ev_goals_away"] != ft_a)
        for key in XG_KEYS + BASE_KEYS:
            vals = st.get(("All", key), (nan(), nan()))
            for side, label in enumerate(("home", "away")): row[f"{key}_{label}"] = vals[side]
        for p, pre in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
            for key in HALF_KEYS:
                vals = st.get((p, key), (nan(), nan()))
                row[f"{pre}_{key}_home"], row[f"{pre}_{key}_away"] = vals
        yell = st.get(("All", "yellow_cards")); red = st.get(("All", "red_cards")); ey = event_yellows(c, home_id)
        # AR-specific (measured, see analysis/DATA_UNDERSTANDING.md): the
        # stats-feed yellow_cards key is NOT one consistent quantity in this
        # league -- it undercounts the event feed by ~0.75/match in 2021-2022
        # and by ~0.9-1.7/match in 2026, while the event feed (card ==
        # "Yellow", the program's unified convention) is stable at
        # 4.4-4.9/match in every block. The unified yellow target is
        # therefore EVENT-derived for every match; the raw stats value
        # stays in yellow_cards_* for reference.
        row["cards_source"] = "events" if evs else "none"
        fh_y = [0, 0]
        for e in evs:
            if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("isHome") is not None and e.get("time") is not None and e["time"] <= 45:
                fh_y[0 if e["isHome"] else 1] += 1
        row["fh_yellow_events_home"], row["fh_yellow_events_away"] = fh_y
        for side, label in enumerate(("home", "away")): row[f"yellow_{label}"] = ey[side] if evs else nan()
        for side, label in enumerate(("home", "away")): row[f"red_{label}"] = red[side] if red else nan()
        for k in ("shots", "sot", "sot_incl_blocked", "xg", "xgot", "xgot_n", "xgot_n_on", "xgot_n_off"):
            for side, label in enumerate(("home", "away")): row[f"sm_{k}_{label}"] = sm[k][side]
        if "touches_opp_box" in all_keys: touches_any = True
        rows.append(row)
        for side, tid, name, oid, oname in (("home", home_id, home_name, away_id, away_name), ("away", away_id, away_name, home_id, home_name)):
            tr = {"match_id": ir["match_id"], "season": ir["season"], "block_idx": BLOCK_ORDER.index(ir["season"]), "date": ir["date"], "team_id": tid, "team": name, "opponent_id": oid, "opponent": oname, "home_away": side}
            for k, v in row.items():
                if k.endswith("_home"): tr[k[:-5]] = v if side == "home" else row.get(k[:-5] + "_away")
                elif k.endswith("_away") and k[:-5] not in tr: tr[k[:-5]] = v if side == "away" else row.get(k[:-5] + "_home")
            for k in ("ev_goals", "expected_goals", "total_shots", "ShotsOnTarget", "corners", "yellow", "yellow_cards", "red", "red_cards", "fouls", "big_chance", "touches_opp_box", "BallPossesion"):
                suffix = "_away" if side == "home" else "_home"
                tr[k + "_against"] = row.get(k + suffix, nan())
            team_rows.append(tr)
    rows.sort(key=lambda r: (r["date"], int(r["match_id"]))); team_rows.sort(key=lambda r: (r["date"], int(r["match_id"]), r["home_away"]))
    def write(path, data):
        keys = []
        for r in data:
            for k in r:
                if k not in keys: keys.append(k)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(data)
    write(OUT / "ar_matches.csv", rows); write(OUT / "team_matches.csv", team_rows)
    from collections import Counter
    per_block = dict(Counter(r["season"] for r in rows))
    # Frozen build-time counts are floors, not equalities (the AU/MLS
    # pattern): the daily runner rebuilds this table after fetching newly
    # played matches — each played playoff match raises `excluded` above
    # its frozen 45 and any late group-stage file raises its block above
    # EXPECTED_GROUP, so hard equality would break every daily rebuild
    # from the first played playoff on. The floors still catch an
    # incomplete warehouse: any block below its frozen count fails.
    assert all(per_block.get(block, 0) >= n for block, n in EXPECTED_GROUP.items()), per_block
    assert len(rows) >= 2419 and excluded >= 45 and len({r['match_id'] for r in rows}) == len(rows) and len(team_rows) == 2 * len(rows)
    print(json.dumps({"index_league_112": len(index_rows), "group_stage": len(rows), "excluded_playoffs": excluded, "team_rows": len(team_rows), "per_block": per_block, "touches_opp_box_key_present": touches_any, "stats_conflicts_checked": True}, indent=2))

if __name__ == "__main__": main()
