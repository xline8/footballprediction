"""G-KR2 arm adjustments layered over a fitted DC model.

X2 mover offsets are keyed by FotMob team ID and computed from the
KR-KLeague1 corpus exactly as frozen in PREREG_G_KR2: for target
season S, a team qualifies iff (a) it played in K League 1 in season
S-1 (ID match) and (b) it has zero K League 2 matches before season
S. att_rel = (GF + 10*mu) / ((n + 10)*mu) with GF/n from the team's
S-1 K1 season and mu = the K1 league goals per team-match in S-1;
def_rel likewise with goals against. Offsets add log(att_rel) to the
team's attack log-rating and log(def_rel) to its defence log-rating
(the defence rating enters opponents' lambdas, so def_rel > 1 makes
opponents score more, as registered).
"""
import csv, math
from collections import defaultdict
from pathlib import Path

K1_CSV = Path('/home/hatch/workspace/footballprediction/league/KR-KLeague1/data/kr_matches.csv')


def match_counts(rows):
    c = defaultdict(int)
    for r in rows:
        c[r['hi']] += 1; c[r['ai']] += 1
    return c


def mover_offsets(target_season, k2_rows_before):
    """{team_id: (att_rel, def_rel)} for the X2 arm of target_season."""
    prev = str(int(target_season) - 1)
    k1 = [r for r in csv.DictReader(K1_CSV.open())
          if r['season'] == prev]
    if not k1:
        return {}
    mu = sum(int(r['home_goals']) + int(r['away_goals']) for r in k1) / (2 * len(k1))
    k2_seen = {r['hi'] for r in k2_rows_before} | {r['ai'] for r in k2_rows_before}
    stats = defaultdict(lambda: [0, 0, 0])  # team_id -> [gf, ga, n]
    for r in k1:
        h, a = int(r['home_team_id']), int(r['away_team_id'])
        stats[h][0] += int(r['home_goals']); stats[h][1] += int(r['away_goals']); stats[h][2] += 1
        stats[a][0] += int(r['away_goals']); stats[a][1] += int(r['home_goals']); stats[a][2] += 1
    out = {}
    for tid, (gf, ga, n) in stats.items():
        if tid in k2_seen:
            continue
        out[tid] = ((gf + 10 * mu) / ((n + 10) * mu),
                    (ga + 10 * mu) / ((n + 10) * mu))
    return out


def adjusted_lambdas(model, home, away, arm, counts=None, movers=None):
    counts = counts or {}
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == 'shrink':
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    if arm == 'x2' and movers:
        if home in movers:
            ah += math.log(movers[home][0]); dh += math.log(movers[home][1])
        if away in movers:
            aa += math.log(movers[away][0]); da += math.log(movers[away][1])
    return (math.exp(ah + da + model.h), math.exp(aa + dh))
