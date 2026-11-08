"""G-FR arm adjustments layered over a fitted DC model."""
import math
from collections import defaultdict
import csv
from pathlib import Path


INDEX = Path('/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv')

def norm(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', s).casefold() if not unicodedata.combining(c))

def mover_ids(target_season, rows):
    prior = str(int(target_season.split('/')[0]) - 1) + '/' + str(int(target_season.split('/')[0]))
    teams = {r['home'] for r in rows if r['season'] == target_season} | {r['away'] for r in rows if r['season'] == target_season}
    ch = set(); pl = set(); l1 = set()
    with INDEX.open(newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['season'] != prior or r['league_id'] not in ('53', '8970', '110'):
                continue
            (l1 if r['league_id'] == '53' else pl if r['league_id'] == '8970' else ch).update((norm(r['home']), norm(r['away'])))
    return {norm(t): ('ligue1' if norm(t) in l1 - ch else 'ligue3') for t in teams if norm(t) in (l1 | pl) - ch}


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
    home_name = norm(model.team_names.get(home, home))
    away_name = norm(model.team_names.get(away, away))
    if arm == "x2":
        mu = model.mu
        if movers.get(home_name) == 'ligue1': ah += math.log((mu + .227) / mu); dh += math.log((mu - .151) / mu)
        if movers.get(home_name) == 'ligue3': ah += math.log(max(mu - .177, .10) / mu); dh += math.log((mu + .161) / mu)
        if movers.get(away_name) == 'ligue1': aa += math.log((mu + .227) / mu); da += math.log((mu - .151) / mu)
        if movers.get(away_name) == 'ligue3': aa += math.log(max(mu - .177, .10) / mu); da += math.log((mu + .161) / mu)
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    return lh, la
