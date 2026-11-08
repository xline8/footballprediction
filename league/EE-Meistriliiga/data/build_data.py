"""Build the EE-Meistriliiga analysis table and descriptive inventory.

This is a read-only payload audit plus CSV builder.  It deliberately does not
fit a model.  The warehouse is the main footballprediction checkout because
the league payloads are shared across worktrees.
"""
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent / "analysis"
OUT = HERE / "ee_matches.csv"
SEASONS = ["2021", "2022", "2023", "2024", "2025", "2026"]


def events_of(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def score_pair(value):
    parts = str(value).replace(" ", "").split("-")
    if len(parts) != 2:
        raise ValueError(f"bad score: {value!r}")
    return int(parts[0]), int(parts[1])


def stats_nonnull(content):
    periods = ((content or {}).get("stats") or {}).get("Periods")
    if not periods:
        return False, 0
    n = 0
    for block in periods.values():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or []
                if any(v is not None for v in vals):
                    n += 1
    return n > 0, n


def referee(content):
    ref = (((content or {}).get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}
    return ref.get("text") or None


def card_counts(events, home_id, away_id):
    # Yellow is a yellow card; YellowRed and Red are dismissals.  The source
    # feed has no yellow events in 2021-2024, which is preserved as zero.
    yh = ya = rh = ra = 0
    for e in events:
        if e.get("type") != "Card":
            continue
        side = e.get("isHome")
        card = e.get("card")
        if side not in (True, False):
            continue
        if card == "Yellow":
            if side: yh += 1
            else: ya += 1
        elif card in ("Red", "YellowRed"):
            if side: rh += 1
            else: ra += 1
    return yh, ya, rh, ra


def goals_minutes(events):
    return [e.get("time") for e in events if e.get("type") == "Goal" and e.get("time") is not None]


def pearson(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    dx, dy = [x - mx for x in xs], [y - my for y in ys]
    den = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return sum(x * y for x, y in zip(dx, dy)) / den if den else 0.0


def split_half_reliability(rows, field):
    by_team = defaultdict(list)
    for r in rows:
        if field == "goals":
            hf, ha, af, aa = r["home_goals"], r["away_goals"], r["away_goals"], r["home_goals"]
        else:
            hf, ha, af, aa = r[field + "_for"], r[field + "_against"], r[field + "_against"], r[field + "_for"]
        by_team[r["home_team_id"]].append((r["date"], r["match_id"], hf, ha))
        by_team[r["away_team_id"]].append((r["date"], r["match_id"], af, aa))
    eligible = {t: sorted(v) for t, v in by_team.items() if len(v) >= 24}
    vals = {"for": [], "against": []}
    rng = random.Random(248)
    for _ in range(60):
        first, second = {"for": [], "against": []}, {"for": [], "against": []}
        for entries in eligible.values():
            shuffled = entries[:]
            rng.shuffle(shuffled)
            mid = len(shuffled) // 2
            for a, b in ((shuffled[:mid], first), (shuffled[mid:], second)):
                for _, _, gf, ga in a:
                    b["for"].append(gf); b["against"].append(ga)
            # team-level, not pooled-match, correlations
        a_for, b_for, a_against, b_against = [], [], [], []
        for entries in eligible.values():
            shuffled = entries[:]
            rng.shuffle(shuffled); mid = len(shuffled) // 2
            a, b = shuffled[:mid], shuffled[mid:]
            a_for.append(sum(x[2] for x in a) / len(a)); b_for.append(sum(x[2] for x in b) / len(b))
            a_against.append(sum(x[3] for x in a) / len(a)); b_against.append(sum(x[3] for x in b) / len(b))
        vals["for"].append(pearson(a_for, b_for)); vals["against"].append(pearson(a_against, b_against))
    return {
        "teams": len(eligible), "min_matches_per_team": 24, "random_halves": 60,
        "goals_for_r": round(sum(vals["for"]) / len(vals["for"]), 4),
        "goals_for_sd": round((sum((x - sum(vals["for"]) / len(vals["for"])) ** 2 for x in vals["for"]) / len(vals["for"])) ** 0.5, 4),
        "goals_against_r": round(sum(vals["against"]) / len(vals["against"]), 4),
        "goals_against_sd": round((sum((x - sum(vals["against"]) / len(vals["against"])) ** 2 for x in vals["against"]) / len(vals["against"])) ** 0.5, 4),
    }


def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    index = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "248"]
    index.sort(key=lambda r: (r["date"], r["match_id"]))
    rows, inv = [], {s: {"index_rows": 0, "finished": 0, "score_present": 0,
        "stats_nonnull": 0, "period_splits": 0, "events": 0, "card_events": 0,
        "shotmap_nonempty": 0, "referee": 0, "rounds": Counter(), "teams": set()} for s in SEASONS}
    referee_cards = defaultdict(lambda: [0, 0])
    for ir in index:
        season = ir["season"]; d = json.loads((MAIN_REPO / ir["path"]).read_text())
        general, content = d.get("general") or {}, d.get("content") or {}
        status = (d.get("header") or {}).get("status") or {}
        events = events_of(content); stats_ok, stats_n = stats_nonnull(content)
        periods = ((content.get("stats") or {}).get("Periods"))
        hg, ag = score_pair(status.get("scoreStr"))
        assert status.get("finished") and status.get("scoreStr"), f"unplayed/unscored {ir['match_id']}"
        home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
        yh, ya, rh, ra = card_counts(events, home.get("id"), away.get("id"))
        ref = referee(content)
        inv[season]["index_rows"] += 1; inv[season]["finished"] += 1
        inv[season]["score_present"] += 1; inv[season]["stats_nonnull"] += int(stats_ok)
        inv[season]["period_splits"] += int(bool(periods and any(p != "All" for p in periods)))
        inv[season]["events"] += int(bool(events)); inv[season]["card_events"] += sum(e.get("type") == "Card" for e in events)
        inv[season]["shotmap_nonempty"] += int(bool((content.get("shotmap") or {}).get("shots") or []))
        inv[season]["referee"] += int(bool(ref)); inv[season]["rounds"][str(general.get("matchRound") or "")] += 1
        inv[season]["teams"].update([str(home.get("id")), str(away.get("id"))])
        if ref:
            referee_cards[(season, ref)][0] += 1; referee_cards[(season, ref)][1] += yh + ya
        result = "H" if hg > ag else "A" if hg < ag else "D"
        rows.append({"match_id": ir["match_id"], "date": ir["date"], "season": season,
            "round": general.get("matchRound") or "", "league_name": general.get("leagueName") or "",
            "home_team_id": home.get("id"), "home_team": home.get("name") or "",
            "away_team_id": away.get("id"), "away_team": away.get("name") or "",
            "home_goals": hg, "away_goals": ag, "result": result, "referee": ref or "",
            "home_yellow": yh, "away_yellow": ya, "total_yellow": yh + ya,
            "home_red": rh, "away_red": ra, "total_red": rh + ra,
            "goal_minutes": json.dumps(goals_minutes(events), separators=(",", ":")),
            "event_n": len(events), "card_event_n": sum(e.get("type") == "Card" for e in events),
        })
    assert len(rows) == 1056 and all(inv[s]["finished"] == inv[s]["index_rows"] for s in SEASONS)
    fields = list(rows[0])
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    for s in SEASONS:
        inv[s]["teams"] = sorted(inv[s]["teams"]); inv[s]["rounds"] = dict(inv[s]["rounds"])
    team_seasons = {s: sorted({r["home_team_id"] for r in rows if r["season"] == s} | {r["away_team_id"] for r in rows if r["season"] == s}, key=str) for s in SEASONS}
    churn = {}
    for i, s in enumerate(SEASONS):
        prev = set(team_seasons[SEASONS[i - 1]]) if i else set()
        churn[s] = {"entered": sorted(set(team_seasons[s]) - prev, key=str), "left": sorted(prev - set(team_seasons[s]), key=str)}
    team_rows = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            team_rows.append({"season": r["season"], "date": r["date"], "team_id": r[side + "_team_id"],
                "goals_for": r[side + "_goals"], "goals_against": r[other + "_goals"]})
    inventory = {"index_rows": len(index), "finished_rows": len(rows), "season_counts": {s: len([r for r in rows if r["season"] == s]) for s in SEASONS},
        "seasons": {s: dict(v) for s, v in inv.items()}, "team_seasons": team_seasons, "churn": churn,
        "card_definition": "Yellow only for yellow columns; Red and YellowRed for red columns; event-feed provenance.",
        "referee_cards": {s: {ref: {"matches": x[0], "yellow_cards": x[1], "yellow_per_match": round(x[1]/x[0], 4)} for (ss, ref), x in referee_cards.items() if ss == s} for s in SEASONS}}
    (ANALYSIS / "inventory_summary.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    eda = make_eda(rows, team_rows, churn)
    (ANALYSIS / "eda_summary.json").write_text(json.dumps(eda, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"rows": len(rows), "season_counts": inventory["season_counts"], "inventory": inventory, "eda": eda}, indent=2, sort_keys=True))


def make_eda(rows, team_rows, churn):
    levels = {}
    for s in SEASONS:
        rr = [r for r in rows if r["season"] == s]; n = len(rr); goals = [r["home_goals"] + r["away_goals"] for r in rr]
        levels[s] = {"n": n, "goals_per_match": round(sum(goals)/n, 6), "home_goals": round(sum(r["home_goals"] for r in rr)/n, 6),
            "away_goals": round(sum(r["away_goals"] for r in rr)/n, 6), "home_win": round(sum(r["result"] == "H" for r in rr)/n, 6),
            "draw": round(sum(r["result"] == "D" for r in rr)/n, 6), "away_win": round(sum(r["result"] == "A" for r in rr)/n, 6),
            "ou15_over": round(sum(g > 1 for g in goals)/n, 6), "ou25_over": round(sum(g > 2 for g in goals)/n, 6),
            "ou35_over": round(sum(g > 3 for g in goals)/n, 6), "btts": round(sum(r["home_goals"] > 0 and r["away_goals"] > 0 for r in rr)/n, 6),
            "home_advantage": round(sum(r["home_goals"] - r["away_goals"] for r in rr)/n, 6),
            "yellow_per_match": round(sum(r["total_yellow"] for r in rr)/n, 6), "red_per_match": round(sum(r["total_red"] for r in rr)/n, 6)}
    rel = split_half_reliability(rows, "goals")
    rel_by_season = {s: split_half_reliability([r for r in rows if r["season"] == s], "goals") for s in SEASONS}
    entrants = {}
    pooled = []
    season_pool = {}
    for i, s in enumerate(SEASONS[1:], 1):
        entered = churn[s]["entered"]; rr = [r for r in rows if r["season"] == s]; league_gf = sum(r["home_goals"] + r["away_goals"] for r in rr)/(2*len(rr))
        details = []
        for t in entered:
            tr = [x for x in team_rows if x["season"] == s and x["team_id"] == t]; gf = sum(x["goals_for"] for x in tr)/len(tr); ga = sum(x["goals_against"] for x in tr)/len(tr)
            details.append({"team_id": t, "matches": len(tr), "gf_per_match": round(gf, 6), "ga_per_match": round(ga, 6), "dGF": round(gf-league_gf, 6), "dGA": round(ga-league_gf, 6)})
            pooled.extend([(gf-league_gf, ga-league_gf)] * len(tr))
        entrants[s] = {"league_mean_goals_per_team_match": round(league_gf, 6), "clubs": details}
        season_pool[s] = (sum(d["dGF"] * d["matches"] for d in details), sum(d["dGA"] * d["matches"] for d in details), sum(d["matches"] for d in details))
    entrants["pooled"] = {"entrant_team_matches": len(pooled), "dGF": round(sum(x[0] for x in pooled)/len(pooled), 6), "dGA": round(sum(x[1] for x in pooled)/len(pooled), 6)}
    # X2 offsets, expanding and leak-free: for target season S, pool only
    # entrants from seasons strictly before S. 2022 has no prior entrant
    # (X2 inactive); the 2026 virgin-season entrant never enters any offset,
    # so the offset used for the virgin fit comes from 2022-2025 entrants only.
    offsets = {}
    acc_gf = acc_ga = acc_n = 0
    for s in SEASONS:
        offsets[s] = {"dGF": round(acc_gf/acc_n, 6), "dGA": round(acc_ga/acc_n, 6), "entrant_team_matches": acc_n} if acc_n else None
        if s in season_pool:
            acc_gf += season_pool[s][0]; acc_ga += season_pool[s][1]; acc_n += season_pool[s][2]
    entrants["offsets_by_target_season"] = offsets
    referee = {}
    for s in SEASONS:
        rr = [r for r in rows if r["season"] == s]; refs = [r for r in rr if r["referee"]]
        referee[s] = {"matches": len(rr), "referee_present": len(refs), "coverage": round(len(refs)/len(rr), 6), "yellow_per_referee_covered_match": round(sum(r["total_yellow"] for r in refs)/len(refs), 6) if refs else None}
    return {"levels": levels, "trait_reliability": rel, "trait_reliability_by_season": rel_by_season, "entrants": entrants, "referee": referee,
        "card_feed_note": "Yellow event feed is absent in 2021-2024; yellow levels are descriptive only for 2025-2026.",
        "halves": {"available": False, "reason": "content.stats.Periods is null in every payload; FT-only presentation."}}


if __name__ == "__main__":
    main()
