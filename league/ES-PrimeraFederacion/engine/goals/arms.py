"""G-ESPF arm adjustments layered over a fitted DC model."""
import math
from collections import defaultdict
import csv
import json
from pathlib import Path


INDEX = Path('/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv')
WAREHOUSE = INDEX.parent.parent
DATA = Path(__file__).resolve().parents[2] / 'data' / 'espf_matches.csv'
_PRIOR_TEAMS = {}

def _prior_team_ids(league_id, season):
    key = (league_id, season)
    if key in _PRIOR_TEAMS:
        return _PRIOR_TEAMS[key]
    ids = set()
    with INDEX.open(newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['season'] != season or r['league_id'] != str(league_id):
                continue
            payload = json.loads((WAREHOUSE / r['path']).read_text(encoding='utf-8'))
            general = payload.get('general') or {}
            for side in ('homeTeam', 'awayTeam'):
                team_id = (general.get(side) or {}).get('id')
                if team_id is not None:
                    ids.add(int(team_id))
    _PRIOR_TEAMS[key] = ids
    return ids


def mover_ids(target_season):
    prior = str(int(target_season.split('/')[0]) - 1) + '/' + str(int(target_season.split('/')[0]))
    target_ids = set()
    with DATA.open(newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['season'] == target_season:
                target_ids.update((int(r['home_team_id']), int(r['away_team_id'])))
    laliga2 = _prior_team_ids(140, prior)
    pf = _prior_team_ids(8968, prior)
    return {team_id: ('laliga2' if team_id in laliga2 else 'below')
            for team_id in target_ids - pf}


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def adjusted_lambdas(model, home, away, arm, movers, multipliers, counts=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm == "shrink":
        counts = counts or {}
        ah *= min(1.0, counts.get(home, 0) / 6.0); da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0); dh *= min(1.0, counts.get(home, 0) / 6.0)
    if arm == "x2":
        mu = model.mu
        if movers.get(home) == 'laliga2': ah += math.log((mu + .081) / mu); dh += math.log((mu - .150) / mu)
        if movers.get(home) == 'below': ah += math.log(max(mu - .054, .10) / mu); dh += math.log((mu + .011) / mu)
        if movers.get(away) == 'laliga2': aa += math.log((mu + .081) / mu); da += math.log((mu - .150) / mu)
        if movers.get(away) == 'below': aa += math.log(max(mu - .054, .10) / mu); da += math.log((mu + .011) / mu)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    return lh, la
