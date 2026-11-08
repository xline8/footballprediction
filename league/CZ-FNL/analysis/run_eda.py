"""Reproducible FNL EDA; all statistics are derived from the builder CSV."""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'data'
DEV_SEASONS = {'2021/2022','2022/2023','2023/2024','2024/2025'}
SEASONS = ['2021/2022','2022/2023','2023/2024','2024/2025','2025/2026','2026/2027']
MAIN_REPO = Path('/home/hatch/workspace/footballprediction')


def num(v):
    return None if v in (None, '', 'None') else float(v)


def mean(values):
    return round(statistics.mean(values), 6) if values else None


def corr(x, y):
    if len(x) < 2: return None
    ax, ay = statistics.mean(x), statistics.mean(y)
    den = math.sqrt(sum((a-ax)**2 for a in x) * sum((b-ay)**2 for b in y))
    return round(sum((a-ax)*(b-ay) for a,b in zip(x,y))/den, 6) if den else None


def team_trait(rows, getter):
    units = defaultdict(list)
    for r in rows:
        for side in ('home', 'away'):
            units[(r['season'], r[f'{side}_team_id'])].append((r['date'], getter(r, side)))
    x, y = [], []
    for vals in units.values():
        vals = [v for _, v in sorted(vals) if v is not None]
        if len(vals) >= 10:
            x.append(statistics.mean(vals[0::2])); y.append(statistics.mean(vals[1::2]))
    return {'r': corr(x, y), 'n_units': len(x)}


def parse_score(s):
    a, b = s.replace('–', '-').split('-')[:2]
    return int(a.strip()), int(b.strip())


def load_cz_matches():
    out = []
    index = [r for r in csv.DictReader((MAIN_REPO/'data_enrichment/fotmob_world_index.csv').open()) if r['league_id'] == '122']
    for ix in index:
        d = json.loads((MAIN_REPO / ix['path']).read_text())
        g, st = d.get('general') or {}, (d.get('header') or {}).get('status') or {}
        if not st.get('finished') or 'Placement' in (g.get('leagueName') or ''): continue
        h, a = g['homeTeam'], g['awayTeam']; hg, ag = parse_score(st['scoreStr'])
        out.append({'season': ix['season'], 'date': ix['date'], 'home_id': str(h['id']), 'away_id': str(a['id']), 'hg': hg, 'ag': ag})
    return out


def movers(fnl):
    cz = load_cz_matches()
    cz_by_season = defaultdict(set)
    for r in cz: cz_by_season[r['season']] |= {r['home_id'], r['away_id']}
    fnl_by_season = defaultdict(set)
    for r in fnl: fnl_by_season[r['season']] |= {str(r['home_team_id']), str(r['away_team_id'])}
    transitions, cumulative = [], {}
    prior = []
    for i, target in enumerate(SEASONS[1:5], start=1):
        prev = SEASONS[i-1]
        candidates = sorted(fnl_by_season[target] & cz_by_season[prev])
        # The FNL newcomer from the top tier is the unique overlap; B teams and
        # third-tier promotions do not occur in the CZ-Liga index.
        if len(candidates) != 1: raise AssertionError(f'mover candidates {prev}->{target}: {candidates}')
        club = candidates[0]
        target_rows = [r for r in fnl if r['season'] == target and club in {str(r['home_team_id']), str(r['away_team_id'])}]
        league_rows = [r for r in fnl if r['season'] == target]
        gf = sum(r['home_goals'] if str(r['home_team_id']) == club else r['away_goals'] for r in target_rows)/len(target_rows)
        ga = sum(r['away_goals'] if str(r['home_team_id']) == club else r['home_goals'] for r in target_rows)/len(target_rows)
        league_gf = sum(int(r['home_goals']) + int(r['away_goals']) for r in league_rows)/(2*len(league_rows))
        dgf, dga = gf-league_gf, ga-league_gf
        names = [r['home_team'] if str(r['home_team_id']) == club else r['away_team'] for r in target_rows]
        # Use the club's most recent FNL season as the descriptive prior when present.
        prev_fnl = [r for r in fnl if r['season'] == prev and club in {str(r['home_team_id']), str(r['away_team_id'])}]
        pgf = sum(r['home_goals'] if str(r['home_team_id']) == club else r['away_goals'] for r in prev_fnl)/len(prev_fnl) if prev_fnl else None
        pga = sum(r['away_goals'] if str(r['home_team_id']) == club else r['home_goals'] for r in prev_fnl)/len(prev_fnl) if prev_fnl else None
        transitions.append({'boundary': f'{prev}->{target}', 'club': sorted(names)[-1], 'n': len(target_rows),
                            'gf_per_match': round(gf, 6), 'ga_per_match': round(ga, 6),
                            'league_gf_per_match': round(league_gf, 6), 'dGF': round(dgf, 6), 'dGA': round(dga, 6),
                            'fnl_prev_gf': None if pgf is None else round(pgf, 6), 'fnl_prev_ga': None if pga is None else round(pga, 6)})
        # The offset consumed for target season S is frozen before S begins:
        # this boundary's own outcome is not available to its entrant prior.
        cumulative[target] = None if not prior else {'dGF': round(statistics.mean(x for x,_ in prior), 6), 'dGA': round(statistics.mean(y for _,y in prior), 6)}
        prior.append((dgf, dga))
    cumulative['2022/2023'] = None
    return {'transitions': transitions, 'cumulative_offsets_before_target_season': {s: cumulative.get(s) for s in SEASONS[1:5]},
            'note': 'Computed from fnl_matches.csv and the CZ-Liga (league 122) index, excluding placement matches. One top-tier entrant per boundary; B-team and third-tier entrants start at the league mean.'}


def main():
    matches = list(csv.DictReader((DATA/'fnl_matches.csv').open()))
    inc = [r for r in matches if r['included'] == '1']; dev = [r for r in inc if r['season'] in DEV_SEASONS]
    for r in inc:
        for k in ('home_goals','away_goals','ht_home_goals','ht_away_goals','ev_yellow_home','ev_yellow_away','ev_yellowred_home','ev_yellowred_away','ev_red_home','ev_red_away'):
            r[k] = float(r[k])
    levels = {}
    for s in SEASONS:
        rs = [r for r in inc if r['season'] == s]
        levels[s] = {'n': len(rs), 'goals': mean([r['home_goals']+r['away_goals'] for r in rs]),
                     'event_yellows': mean([r['ev_yellow_home']+r['ev_yellow_away'] for r in rs]),
                     'yellowreds': mean([r['ev_yellowred_home']+r['ev_yellowred_away'] for r in rs]),
                     'reds': mean([r['ev_red_home']+r['ev_red_away'] for r in rs]),
                     'sot': None, 'corners': None, 'total_shots': None, 'possession': None}
    getters = {
      'goals_for': lambda r,s: r[f'{s}_goals'], 'goals_against': lambda r,s: r[f'{"away" if s=="home" else "home"}_goals']}
    reliabilities = {k: team_trait(dev, fn) for k,fn in getters.items()}
    total_goals = sum(r['home_goals']+r['away_goals'] for r in dev)
    first_goals = sum(r['ht_home_goals']+r['ht_away_goals'] for r in dev)
    shares = [(r['ht_home_goals']+r['ht_away_goals'])/(r['home_goals']+r['away_goals']) for r in dev if r['home_goals']+r['away_goals']]
    p = first_goals/total_goals
    noise = sum(p*(1-p)/(r['home_goals']+r['away_goals']) for r in dev if r['home_goals']+r['away_goals'])/len(shares)
    # Team-season split halves use aggregated first-half / full-time goals in each half.
    unit_shares = defaultdict(lambda: [[], []])
    for r in dev:
        for side in ('home','away'):
            total = r[f'{side}_goals']; first = r[f'ht_{side}_goals']
            unit_shares[(r['season'], r[f'{side}_team_id'])][0].append((r['date'], first, total))
    ux, uy = [], []
    for vals, _ in unit_shares.values():
        vals.sort()
        halves=[]
        for part in (vals[0::2], vals[1::2]):
            den=sum(v[2] for v in part); halves.append(sum(v[1] for v in part)/den if den else None)
        if None not in halves: ux.append(halves[0]); uy.append(halves[1])
    out = {'counts': {'all_matches': len(matches), 'included': len(inc), 'included_by_season': {s: sum(r['season']==s for r in inc) for s in SEASONS},
                      'distinct_team_ids': len({r['home_team_id'] for r in inc}|{r['away_team_id'] for r in inc}),
                      'name_variant_ids': sum(len({r['home_team'] for r in inc if r['home_team_id']==tid}|{r['away_team'] for r in inc if r['away_team_id']==tid}) > 1 for tid in {r['home_team_id'] for r in inc}|{r['away_team_id'] for r in inc})},
           'levels': levels, 'reliabilities': reliabilities,
           'halves': {'goals_1h_share': round(p, 6), 'goals_total': total_goals, 'goals_1h_total': first_goals,
                      'yellows_1h_share': None, 'yellows_total': None, 'yellows_1h_total': None},
           'halves_variance': {'goals': {'pooled_1h_share': round(p,6), 'per_match_share_var': round(statistics.pvariance(shares),6),
                                         'binomial_noise_var': round(noise,6), 'true_var': round(statistics.pvariance(shares)-noise,6),
                                         'team_split_half_r': corr(ux,uy), 'n_matches': len(dev)},
                              'yellows': None, 'note': 'Dev-era plain-Yellow target is absent; yellow half shares are not computable.'},
           'referee_coverage': {'nonempty_text_by_season': {s: sum(bool(r['referee']) for r in inc if r['season']==s) for s in SEASONS},
                                'dev_named': sum(bool(r['referee']) for r in dev), 'reliability': None,
                                'note': 'NOT ESTIMABLE: no named referees in the dev era.'},
           'movers_x2': movers(inc),
           'primary_lines': {'goals': {'primary': 'OU2.5', 'over_rate': round(sum(r['home_goals']+r['away_goals'] > 2.5 for r in dev)/len(dev),6)},
                             'sot': None, 'corners': None, 'total_shots': None, 'cards': None}}
    (HERE/'eda_numbers.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__': main()
