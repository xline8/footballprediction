"""Shared extraction helpers for the J.League FotMob warehouse experiment.

Reads the raw matchDetails JSONs under data_enrichment/fotmob_jleague/ and
exposes flat, documented accessors. No modelling code lives here.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STORE = REPO / "data_enrichment" / "fotmob_jleague"
LEAGUES = ["J1", "J2", "J3"]
LEAGUE_IDS = {"J1": 223, "J2": 8974, "J3": 9136}

STAT_KEYS = [
    "BallPossesion", "expected_goals", "expected_goals_open_play",
    "expected_goals_set_play", "expected_goals_non_penalty",
    "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
    "shots_inside_box", "shots_outside_box", "big_chance",
    "touches_opp_box", "corners", "yellow_cards", "red_cards", "fouls",
    "Offsides", "keeper_saves",
]


def iter_files():
    """Yield (league, season_label, path) for every stored JSON."""
    for lg in LEAGUES:
        base = STORE / lg
        if not base.exists():
            continue
        for sdir in sorted(p for p in base.iterdir() if p.is_dir()):
            for f in sorted(sdir.glob("*.json")):
                yield lg, sdir.name, f


def load(path):
    with open(path) as fh:
        return json.load(fh)


def _num(v):
    """FotMob stat values arrive as int, float, '1.49', '188 (64%)' or None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        head = v.split(" ")[0].replace("%", "")
        try:
            return float(head)
        except ValueError:
            return None
    return None


def flat_stats(content):
    """{(period, key): (home, away)} from content.stats.Periods.

    Section-header rows carry None values and are dropped. The same key can
    appear in several groups (e.g. expected_goals in 'Top stats' and in the
    'Expected goals (xG)' group); duplicates are expected to be identical --
    the caller can verify via stats_conflicts().
    """
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for s in group.get("stats", []) or []:
                vals = s.get("stats") or [None, None]
                h, a = _num(vals[0]), _num(vals[1]) if len(vals) > 1 else None
                if h is None and a is None:
                    continue
                out[(period, s.get("key"))] = (h, a)
    return out


def stats_conflicts(content):
    """Count (period, key) pairs whose repeated group entries disagree."""
    seen, bad = {}, 0
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for s in group.get("stats", []) or []:
                vals = s.get("stats") or [None, None]
                h = _num(vals[0])
                a = _num(vals[1]) if len(vals) > 1 else None
                if h is None and a is None:
                    continue
                k = (period, s.get("key"))
                if k in seen and seen[k] != (h, a):
                    bad += 1
                seen[k] = (h, a)
    return bad


def shots_of(content):
    return ((content or {}).get("shotmap") or {}).get("shots") or []


def events_of(content):
    ev = ((content or {}).get("matchFacts") or {}).get("events") or {}
    return ev.get("events") or []


def goal_events(content):
    return [e for e in events_of(content) if e.get("type") == "Goal"]


def ht_from_events(content):
    """HT goals (h, a) from matchFacts goal events, or None if any goal
    event lacks time/isHome. First half = time <= 45 (FotMob files 45+2'
    under time 45 with overloadTime set; verified in the EDA phase against
    shotmap period counts)."""
    goals = goal_events(content)
    if not goals:
        return (0, 0) if events_of(content) else None
    h = a = 0
    for e in goals:
        if e.get("time") is None or e.get("isHome") is None:
            return None
        if e["time"] <= 45:
            if e["isHome"]:
                h += 1
            else:
                a += 1
    return h, a


def ht_from_shotmap(content, home_team_id):
    """HT goals (h, a) from shotmap Goal shots with period == FirstHalf."""
    shots = shots_of(content)
    if not shots:
        return None
    # Shotmap teamId is the SHOOTING team; an own goal is credited to the
    # opponent, so OG shots flip sides (verified against the event feed,
    # whose isHome is the CREDITED team and matches scoreStr 100%).
    h = a = 0
    for s in shots:
        if s.get("eventType") != "Goal" or s.get("period") != "FirstHalf":
            continue
        credited_home = (s.get("teamId") == home_team_id) != bool(s.get("isOwnGoal"))
        if credited_home:
            h += 1
        else:
            a += 1
    return h, a


def ft_from_events(content):
    """FT goals (h, a) counted from goal events (cross-check vs header)."""
    goals = goal_events(content)
    if not goals and not events_of(content):
        return None
    h = sum(1 for e in goals if e.get("isHome"))
    a = sum(1 for e in goals if e.get("isHome") is False)
    return h, a
