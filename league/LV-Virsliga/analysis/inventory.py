"""Step-1 inventory for LV-Virsliga (FotMob 226): full 1,017-payload scan.

Reads every payload in the world warehouse for league_id 226 and reports
per-season coverage from payload CONTENTS (never the index flags).
Writes league/LV-Virsliga/analysis/inventory_summary.json.

NOTE (virgin hygiene): this script computes aggregate per-season counts
only (coverage, totals, levels) including 2026. No per-match model
output and no gate quantity is computed here; the virgin is not burned.
"""
import csv
import json
import os
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
IDX = os.path.join(ROOT, "data_enrichment", "fotmob_world_index.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_summary.json")


def stat_map(period):
    """Flatten one stats Period dict -> {key: (home, away)} (non-null only)."""
    out = {}
    if not isinstance(period, dict):
        return out
    for group in period.get("stats", []) or []:
        if not isinstance(group, dict):
            continue
        for item in group.get("stats", []) or []:
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            vals = item.get("stats")
            if key and isinstance(vals, list) and len(vals) == 2 and vals[0] is not None and vals[1] is not None:
                out[key] = (vals[0], vals[1])
    return out


def main():
    rows = [r for r in csv.DictReader(open(IDX)) if r["league_id"] == "226"]
    assert len(rows) == 1017, len(rows)
    per_season = {}
    all_keys = Counter()
    team_names = defaultdict(set)  # team id -> names
    general_keys = Counter()
    for r in rows:
        season = r["season"]
        s = per_season.setdefault(season, {
            "n": 0, "dates": [], "team_ids": set(), "rounds": Counter(),
            "has_stats_all": 0, "has_stats_1h": 0, "has_stats_2h": 0,
            "has_shotmap": 0, "has_events": 0, "has_lineup": 0,
            "referee": 0, "referee_names": Counter(),
            "stat_key_cov": Counter(), "event_types": Counter(),
            "yellow_events": 0, "goal_events": 0, "score_goals": 0,
            "score_reconciled": 0, "has_playoff": 0,
            "goals_h": [], "goals_a": [],
            "period_goals_h1": 0, "period_goals_h2": 0,
        })
        s["n"] += 1
        s["dates"].append(r["date"])
        d = json.load(open(os.path.join(ROOT, r["path"])))
        g = d.get("general", {}) or {}
        general_keys.update(g.keys())
        home_id = g.get("homeTeam", {}).get("id")
        away_id = g.get("awayTeam", {}).get("id")
        home_name = g.get("homeTeam", {}).get("name")
        away_name = g.get("awayTeam", {}).get("name")
        if home_id:
            s["team_ids"].add(home_id)
            team_names[home_id].add(home_name)
        if away_id:
            s["team_ids"].add(away_id)
            team_names[away_id].add(away_name)
        if g.get("matchRound") is not None:
            s["rounds"][str(g.get("matchRound"))] += 1
        if g.get("leagueRoundName") is not None:
            s.setdefault("round_names", Counter())[str(g.get("leagueRoundName"))] += 1
        c = d.get("content", {}) or {}
        if c.get("hasPlayoff"):
            s["has_playoff"] += 1
        # scores from the INDEX score column ("H-A"); goal events reconcile vs it
        sc = (r.get("score") or "").split("-")
        hg = ag = None
        if len(sc) == 2 and sc[0].strip().isdigit() and sc[1].strip().isdigit():
            hg, ag = int(sc[0]), int(sc[1])
        if isinstance(hg, int) and isinstance(ag, int):
            s["score_goals"] += hg + ag
            s["goals_h"].append(hg)
            s["goals_a"].append(ag)
        # stats
        stats = c.get("stats") or {}
        periods = stats.get("Periods", {}) if isinstance(stats, dict) else {}
        m_all = stat_map(periods.get("All"))
        m_1h = stat_map(periods.get("FirstHalf"))
        m_2h = stat_map(periods.get("SecondHalf"))
        if m_all:
            s["has_stats_all"] += 1
        if m_1h:
            s["has_stats_1h"] += 1
        if m_2h:
            s["has_stats_2h"] += 1
        for k in m_all:
            s["stat_key_cov"][k] += 1
            all_keys[k] += 1
        # period-split goal reconciliation (event times) + halves goals
        mf = c.get("matchFacts") or {}
        evs = (mf.get("events") or {}).get("events") or []
        if evs:
            s["has_events"] += 1
        n_goal_ev = 0
        for e in evs:
            t = e.get("type")
            s["event_types"][t] += 1
            if t == "Goal":
                n_goal_ev += 1
                tm = e.get("time", 0) or 0
                if tm <= 45:
                    s["period_goals_h1"] += 1
                else:
                    s["period_goals_h2"] += 1
            if t in ("Card",):
                card = (e.get("card") or e.get("cardType") or "")
                if "ellow" in str(card):
                    s["yellow_events"] += 1
            if t == "YellowCard" or (isinstance(e, dict) and str(e.get("type")) == "Card" and "Yellow" in str(e.get("card"))):
                pass
        s["goal_events"] += n_goal_ev
        if isinstance(hg, int) and isinstance(ag, int) and n_goal_ev == hg + ag:
            s["score_reconciled"] += 1
        # shotmap
        sm = c.get("shotmap") or {}
        shots = sm.get("shots") or []
        if shots:
            s["has_shotmap"] += 1
        # lineup
        if c.get("lineup"):
            s["has_lineup"] += 1
        # referee: search a few known spots
        ref = None
        ib = mf.get("infoBox") or {}
        if isinstance(ib, dict):
            ref = (ib.get("Referee") or {}).get("text") if isinstance(ib.get("Referee"), dict) else ib.get("Referee")
        if not ref:
            ref = g.get("referee") or (d.get("header") or {}).get("referee") if isinstance(d.get("header"), dict) else None
        if ref:
            s["referee"] += 1
            s["referee_names"][str(ref)] += 1

    out = {"league": "LV-Virsliga", "fotmob_id": 226, "n_index": len(rows),
           "seasons": {}, "all_stat_keys": dict(all_keys),
           "general_keys": dict(general_keys),
           "team_names": {str(k): sorted(v) for k, v in team_names.items()}}
    for season in sorted(per_season):
        s = per_season[season]
        n = s["n"]
        gh = s["goals_h"]
        out["seasons"][season] = {
            "n": n,
            "dates": [min(s["dates"]), max(s["dates"])],
            "teams": len(s["team_ids"]),
            "rounds": dict(sorted(s["rounds"].items(), key=lambda kv: (len(kv[0]), kv[0]))),
            "round_names": dict(s.get("round_names", {})),
            "has_stats_all": s["has_stats_all"],
            "has_stats_1h": s["has_stats_1h"],
            "has_stats_2h": s["has_stats_2h"],
            "has_shotmap": s["has_shotmap"],
            "has_events": s["has_events"],
            "has_lineup": s["has_lineup"],
            "referee": s["referee"],
            "referee_names": dict(s["referee_names"]),
            "stat_key_cov": dict(s["stat_key_cov"]),
            "event_types": dict(s["event_types"]),
            "yellow_events": s["yellow_events"],
            "goal_events": s["goal_events"],
            "score_goals": s["score_goals"],
            "score_reconciled": s["score_reconciled"],
            "has_playoff": s["has_playoff"],
            "goals_per_match": round((sum(gh) + sum(s["goals_a"])) / n, 4) if gh else None,
            "home_goals_per_match": round(sum(gh) / n, 4) if gh else None,
            "away_goals_per_match": round(sum(s["goals_a"]) / n, 4) if gh else None,
            "period_goals_h1": s["period_goals_h1"],
            "period_goals_h2": s["period_goals_h2"],
        }
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
