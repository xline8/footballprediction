"""Phase 1 inventory: scan every J.League warehouse JSON once and record
what it actually contains, per league-season. Output: inventory_summary.json
plus a compact stdout digest. Read-only against the warehouse.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jleague_lib import (LEAGUES, STAT_KEYS, events_of, flat_stats, goal_events,
                         ht_from_events, ht_from_shotmap, iter_files, load,
                         shots_of, stats_conflicts)

OUT = Path(__file__).parent / "inventory_summary.json"
INDEX = Path(__file__).parents[2] / "data_enrichment" / "fotmob_jleague_index.csv"


def new_cell():
    return {
        "n": 0, "finished": 0, "dates": [],
        "coverage_level": Counter(),
        "shot_matches": 0, "shots_total": 0,
        "shot_field_nonnull": Counter(), "shot_rows": 0,
        "shot_event_types": Counter(), "shot_periods": Counter(),
        "periods_present": Counter(),
        "stat_key_all": Counter(), "stat_key_half": Counter(),
        "stat_conflicts": 0,
        "lineup_full": 0, "formation": 0, "player_stats": 0,
        "events_matches": 0, "goal_events": 0, "card_events": 0,
        "card_kinds": Counter(),
        "ht_events": 0, "ht_shotmap": 0, "ht_agree": 0, "ht_both": 0,
        "ft_events_agree": 0, "ft_events_seen": 0,
        "header_redcards": 0, "xg_group": 0,
        "teams": set(), "league_id_seen": Counter(),
    }


cells = {}
id_locations = defaultdict(list)
team_names = defaultdict(set)   # team_id -> names
name_ids = defaultdict(set)     # name -> team_ids

for lg, season, path in iter_files():
    cell = cells.setdefault((lg, season), new_cell())
    cell["n"] += 1
    d = load(path)
    gen, hdr, content = d.get("general") or {}, d.get("header") or {}, d.get("content") or {}
    mid = str(gen.get("matchId") or path.stem)
    id_locations[mid].append(f"{lg}/{season}")
    cell["league_id_seen"][gen.get("leagueId")] += 1
    if (hdr.get("status") or {}).get("finished"):
        cell["finished"] += 1
    if gen.get("matchTimeUTCDate"):
        cell["dates"].append(gen["matchTimeUTCDate"][:10])
    cell["coverage_level"][gen.get("coverageLevel")] += 1
    for side in ("homeTeam", "awayTeam"):
        t = gen.get(side) or {}
        if t.get("id") is not None:
            cell["teams"].add(t["id"])
            team_names[t["id"]].add(t.get("name"))
            name_ids[t.get("name")].add(t["id"])

    shots = shots_of(content)
    if shots:
        cell["shot_matches"] += 1
        cell["shots_total"] += len(shots)
        for s in shots:
            cell["shot_rows"] += 1
            for f in ("expectedGoals", "expectedGoalsOnTarget", "x", "y",
                      "situation", "shotType", "period", "isOnTarget",
                      "isBlocked", "playerId"):
                if s.get(f) is not None:
                    cell["shot_field_nonnull"][f] += 1
            cell["shot_event_types"][s.get("eventType")] += 1
            cell["shot_periods"][s.get("period")] += 1

    fs = flat_stats(content)
    periods = ((content.get("stats") or {}).get("Periods") or {})
    for p in periods:
        cell["periods_present"][p] += 1
    for k in STAT_KEYS:
        if ("All", k) in fs:
            cell["stat_key_all"][k] += 1
        if ("FirstHalf", k) in fs or ("SecondHalf", k) in fs:
            cell["stat_key_half"][k] += 1
    cell["stat_conflicts"] += stats_conflicts(content)
    all_groups = [g.get("title") for g in (periods.get("All") or {}).get("stats", [])]
    if "Expected goals (xG)" in all_groups:
        cell["xg_group"] += 1

    lu = content.get("lineup") or {}
    def starters(side):
        return ((lu.get(side) or {}).get("starters") or [])
    if len(starters("homeTeam")) == 11 and len(starters("awayTeam")) == 11:
        cell["lineup_full"] += 1
    if (lu.get("homeTeam") or {}).get("formation"):
        cell["formation"] += 1
    if content.get("playerStats"):
        cell["player_stats"] += 1

    evs = events_of(content)
    if evs:
        cell["events_matches"] += 1
    cell["goal_events"] += len(goal_events(content))
    for e in evs:
        if e.get("type") == "Card":
            cell["card_events"] += 1
            cell["card_kinds"][str(e.get("card"))] += 1
    home_id = (gen.get("homeTeam") or {}).get("id")
    hte, hts = ht_from_events(content), ht_from_shotmap(content, home_id)
    if hte is not None:
        cell["ht_events"] += 1
    if hts is not None:
        cell["ht_shotmap"] += 1
    if hte is not None and hts is not None:
        cell["ht_both"] += 1
        if hte == hts:
            cell["ht_agree"] += 1
    # FT cross-check: goal events counted vs header scoreStr
    score = (hdr.get("status") or {}).get("scoreStr") or ""
    if evs and " - " in score:
        try:
            hh, aa = (int(x) for x in score.split(" - "))
            ge = goal_events(content)
            eh = sum(1 for e in ge if e.get("isHome"))
            ea = sum(1 for e in ge if e.get("isHome") is False)
            cell["ft_events_seen"] += 1
            if (eh, ea) == (hh, aa):
                cell["ft_events_agree"] += 1
        except ValueError:
            pass
    st = hdr.get("status") or {}
    if (st.get("numberOfHomeRedCards") or 0) + (st.get("numberOfAwayRedCards") or 0):
        cell["header_redcards"] += 1

summary = {"cells": {}, "globals": {}}
for (lg, season), c in sorted(cells.items()):
    n = c["n"]
    summary["cells"][f"{lg}|{season}"] = {
        "n": n, "finished": c["finished"],
        "date_min": min(c["dates"]) if c["dates"] else None,
        "date_max": max(c["dates"]) if c["dates"] else None,
        "coverage_level": dict(c["coverage_level"]),
        "league_id_seen": {str(k): v for k, v in c["league_id_seen"].items()},
        "n_teams": len(c["teams"]),
        "shot_matches": c["shot_matches"], "shots_total": c["shots_total"],
        "shot_field_nonnull": dict(c["shot_field_nonnull"]), "shot_rows": c["shot_rows"],
        "shot_event_types": dict(c["shot_event_types"]),
        "shot_periods": dict(c["shot_periods"]),
        "periods_present": dict(c["periods_present"]),
        "stat_key_all": dict(c["stat_key_all"]), "stat_key_half": dict(c["stat_key_half"]),
        "stat_conflicts": c["stat_conflicts"],
        "lineup_full": c["lineup_full"], "formation": c["formation"],
        "player_stats": c["player_stats"],
        "events_matches": c["events_matches"], "goal_events": c["goal_events"],
        "card_events": c["card_events"], "card_kinds": dict(c["card_kinds"]),
        "ht_events": c["ht_events"], "ht_shotmap": c["ht_shotmap"],
        "ht_both": c["ht_both"], "ht_agree": c["ht_agree"],
        "ft_events_seen": c["ft_events_seen"], "ft_events_agree": c["ft_events_agree"],
        "header_redcards": c["header_redcards"], "xg_group": c["xg_group"],
    }

dup_ids = {k: v for k, v in id_locations.items() if len(v) > 1}
summary["globals"] = {
    "total_files": sum(c["n"] for c in cells.values()),
    "unique_match_ids": len(id_locations),
    "duplicate_ids": dup_ids,
    "team_ids_with_multiple_names": {str(k): sorted(v) for k, v in team_names.items() if len(v) > 1},
    "names_with_multiple_ids": {k: sorted(v) for k, v in name_ids.items() if len(v) > 1},
    "n_team_ids": len(team_names),
}

# reconcile vs the pull index CSV
import csv
idx_ids = set()
with open(INDEX) as fh:
    for row in csv.DictReader(fh):
        idx_ids.add(str(row["match_id"]))
disk_ids = set(id_locations)
summary["globals"]["index_rows"] = len(idx_ids)
summary["globals"]["in_index_not_on_disk"] = sorted(idx_ids - disk_ids)
summary["globals"]["on_disk_not_in_index"] = sorted(disk_ids - idx_ids)

OUT.write_text(json.dumps(summary, indent=1, ensure_ascii=False))
g = summary["globals"]
print(f"files={g['total_files']} unique_ids={g['unique_match_ids']} dup={len(dup_ids)} "
      f"index_rows={g['index_rows']} idx_not_disk={len(g['in_index_not_on_disk'])} "
      f"disk_not_idx={len(g['on_disk_not_in_index'])} teams={g['n_team_ids']}")
print(f"team ids w/ >1 name: {len(g['team_ids_with_multiple_names'])}; names w/ >1 id: {len(g['names_with_multiple_ids'])}")
for k, c in summary["cells"].items():
    print(f"{k:14s} n={c['n']:4d} fin={c['finished']:4d} {c['date_min']}..{c['date_max']} "
          f"teams={c['n_teams']:2d} shots={c['shot_matches']:4d} lineup={c['lineup_full']:4d} "
          f"pstats={c['player_stats']:4d} ev={c['events_matches']:4d} ht_ev={c['ht_events']:4d} "
          f"ht_sm={c['ht_shotmap']:4d} agree={c['ht_agree']}/{c['ht_both']} ft_agree={c['ft_events_agree']}/{c['ft_events_seen']} "
          f"conf={c['stat_conflicts']} cov={c['coverage_level']}")
