"""EDA computation for IT-SerieB: levels, reliabilities, halves, cards check, movers."""
import csv, json, math, unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path('/home/hatch/workspace/footballprediction')
ROWS = list(csv.DictReader(open(HERE.parent / 'data' / 'itserieb_matches.csv')))
TM = list(csv.DictReader(open(HERE.parent / 'data' / 'itserieb_team_matches.csv')))
DEV_SEASONS = ['2021/2022', '2022/2023', '2023/2024', '2024/2025']
EVAL_SEASONS = ['2022/2023', '2023/2024', '2024/2025']
SEASONS = sorted({r['season'] for r in ROWS})

def num(r, k):
    v = r.get(k)
    try: return float(v) if v not in (None, '') else None
    except ValueError: return None

def tot(r, k):
    a, b = num(r, k + '_home'), num(r, k + '_away')
    return a + b if a is not None and b is not None else None

def mean(xs): return sum(xs) / len(xs) if xs else None

def pearson(xs, ys):
    if len(xs) < 3: return None
    mx, my = mean(xs), mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs)); sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0: return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)

out = {}
levels = {}
for s in SEASONS:
    rs = [r for r in ROWS if r['season'] == s]
    g = [int(r['home_goals']) + int(r['away_goals']) for r in rs]
    lv = {'n': len(rs), 'goals': mean(g), 'home_goals': mean([int(r['home_goals']) for r in rs]),
          'away_goals': mean([int(r['away_goals']) for r in rs]),
          'hw': mean([int(int(r['home_goals']) > int(r['away_goals'])) for r in rs]),
          'draw': mean([int(int(r['home_goals']) == int(r['away_goals'])) for r in rs]),
          'over25': mean([int(x > 2.5) for x in g]),
          'btts': mean([int(int(r['home_goals']) > 0 and int(r['away_goals']) > 0) for r in rs])}
    for key, col in [('sot', 'ShotsOnTarget'), ('corners', 'corners'), ('shots', 'total_shots'),
                     ('yellows_stats', 'yellow_cards'), ('xg', 'expected_goals')]:
        vals = [tot(r, col) for r in rs]; vals = [v for v in vals if v is not None]
        lv[key] = mean(vals) if vals else None; lv[key + '_n'] = len(vals)
    lv['yellows_events'] = mean([int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in rs])
    lv['reds_stats'] = mean([tot(r, 'red_cards') or 0 for r in rs])
    levels[s] = lv
out['levels'] = levels

def over_rates(rs, col, lines):
    if col == 'ev_yellow': vals = [int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in rs]
    else:
        vals = [tot(r, col) for r in rs]; vals = [v for v in vals if v is not None]
    return {str(L): round(mean([int(v > L) for v in vals]), 4) for L in lines}
rates = {}
for label, ss in [('eval_2022_2025', EVAL_SEASONS), ('dev_2021_2025', DEV_SEASONS)]:
    rs = [r for r in ROWS if r['season'] in ss]
    rates[label] = {'sot': over_rates(rs, 'ShotsOnTarget', [6.5, 7.5, 8.5, 9.5]),
        'corners': over_rates(rs, 'corners', [8.5, 9.5, 10.5]),
        'cards_events': over_rates(rs, 'ev_yellow', [3.5, 4.5, 5.5]),
        'cards_stats': over_rates(rs, 'yellow_cards', [3.5, 4.5, 5.5]),
        'shots': over_rates(rs, 'total_shots', [22.5, 23.5, 24.5, 25.5]),
        'goals': {'2.5': round(mean([int(int(r['home_goals']) + int(r['away_goals']) > 2.5) for r in rs]), 4)}}
out['over_rates'] = rates

cc = {}
for s in DEV_SEASONS:
    rs = [r for r in ROWS if r['season'] == s]
    st = sum(tot(r, 'yellow_cards') or 0 for r in rs)
    ev = sum(int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in rs)
    agree = mean([int((tot(r, 'yellow_cards') if tot(r, 'yellow_cards') is not None else -1) == int(r['ev_yellow_home']) + int(r['ev_yellow_away'])) for r in rs])
    agree_yr = mean([int((tot(r, 'yellow_cards') if tot(r, 'yellow_cards') is not None else -1) == int(r['ev_yellow_home']) + int(r['ev_yellow_away']) + int(r['ev_yellowred_home']) + int(r['ev_yellowred_away'])) for r in rs])
    zero = sum(1 for r in rs if (tot(r, 'yellow_cards') or 0) == 0 and int(r['ev_yellow_home']) + int(r['ev_yellow_away']) > 0)
    cc[s] = {'stats_total': st, 'events_yellow_total': ev,
             'stats_vs_events_pct': round(100 * (st - ev) / ev, 2) if ev else None,
             'exact_agree_yellow_only': round(agree, 4), 'exact_agree_yellow_plus_yr': round(agree_yr, 4),
             'stats_zero_but_events_positive': zero}
rs = [r for r in ROWS if r['season'] == '2025/2026']
cc['2025/2026_descriptive'] = {'stats_total': sum(tot(r, 'yellow_cards') or 0 for r in rs),
    'events_yellow_total': sum(int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in rs),
    'exact_agree_yellow_only': round(mean([int((tot(r, 'yellow_cards') if tot(r, 'yellow_cards') is not None else -1) == int(r['ev_yellow_home']) + int(r['ev_yellow_away'])) for r in rs]), 4)}
out['cards_check_dev'] = cc

def reliability(tm_rows, for_key, min_matches=10):
    by_team = defaultdict(list)
    for r in tm_rows: by_team[r['team_id']].append(r)
    xs, ys = [], []
    for tid, ms in by_team.items():
        ms = sorted(ms, key=lambda r: (r['date'], r['match_id']))
        halves = [[], []]
        for i, m in enumerate(ms): halves[i % 2].append(m)
        vals, ok = [], True
        for h in halves:
            tot_v, n = 0.0, 0
            for m in h:
                v = num(m, for_key)
                if v is None: ok = False; break
                tot_v += v; n += 1
            if not ok or n < 5: ok = False; break
            vals.append(tot_v / n)
        if ok and len(ms) >= min_matches: xs.append(vals[0]); ys.append(vals[1])
    r = pearson(xs, ys)
    return {'r': round(r, 3) if r is not None else None, 'n_teams': len(xs)}
rel = {}
for trait, key in [('goals_for', 'goals_for'), ('goals_against', 'goals_against'),
                   ('sot_for', 'ShotsOnTarget_for'), ('sot_against', 'ShotsOnTarget_against'),
                   ('corners_for', 'corners_for'), ('corners_against', 'corners_against'),
                   ('shots_for', 'total_shots_for'), ('shots_against', 'total_shots_against'),
                   ('yellows_events_for', 'yellow_events_for'), ('yellows_stats_for', 'yellow_cards_for'),
                   ('possession', 'BallPossesion_for'), ('big_chance_for', 'big_chance_for'),
                   ('box_touches_for', 'touches_opp_box_for'), ('box_touches_against', 'touches_opp_box_against')]:
    rel[trait] = reliability(TM, key)
out['reliability'] = rel
rel_gs = {}
for s in SEASONS:
    sub = [r for r in TM if r['season'] == s]
    rel_gs[s] = {'gf': reliability(sub, 'goals_for', 10), 'ga': reliability(sub, 'goals_against', 10)}
out['reliability_goals_by_season'] = rel_gs

complete = [s for s in SEASONS if mean([int(r['has_stats_half']) for r in ROWS if r['season'] == s]) >= 0.99]
def half_share(rs, fh_key, ft_key):
    shares, tot_fh, tot_ft = [], 0.0, 0.0
    for r in rs:
        fh, ft = tot(r, fh_key), tot(r, ft_key)
        if fh is None or ft is None or ft == 0: continue
        shares.append(fh / ft); tot_fh += fh; tot_ft += ft
    if not shares: return None
    m = tot_fh / tot_ft
    obs_sd = math.sqrt(mean([(x - mean(shares)) ** 2 for x in shares]))
    mean_ft = tot_ft / len(shares)
    exp_sd = math.sqrt(m * (1 - m) / mean_ft) if mean_ft else 0
    return {'share_ratio_of_sums': round(m, 4), 'n': len(shares), 'obs_sd': round(obs_sd, 4),
            'exp_sd_approx': round(exp_sd, 4), 'true_sd': round(math.sqrt(max(obs_sd ** 2 - exp_sd ** 2, 0.0)), 4)}
hs = {'seasons_used': complete}
rs_c = [r for r in ROWS if r['season'] in complete]
hs['sot'] = half_share(rs_c, 'fh_ShotsOnTarget', 'ShotsOnTarget')
hs['corners'] = half_share(rs_c, 'fh_corners', 'corners')
hs['shots'] = half_share(rs_c, 'fh_total_shots', 'total_shots')
gfh = sum(int(r['ht_home_goals']) + int(r['ht_away_goals']) for r in rs_c)
gft = sum(int(r['home_goals']) + int(r['away_goals']) for r in rs_c)
hs['goals_events'] = {'share_ratio_of_sums': round(gfh / gft, 4), 'n': len(rs_c)}
yfh = sum(int(r['ev_yellow_1h_home']) + int(r['ev_yellow_1h_away']) for r in rs_c)
yft = sum(int(r['ev_yellow_home']) + int(r['ev_yellow_away']) for r in rs_c)
hs['yellows_events'] = {'share_ratio_of_sums': round(yfh / yft, 4), 'n': len(rs_c)}
out['half_shares'] = hs

ref_matches = defaultdict(list)
for r in sorted([x for x in ROWS if x['season'] in DEV_SEASONS], key=lambda x: (x['date'], x['match_id'])):
    if r['referee'].strip():
        ref_matches[r['referee']].append(int(r['ev_yellow_home']) + int(r['ev_yellow_away']))
xs, ys, nref = [], [], 0
for ref, lst in ref_matches.items():
    if len(lst) >= 10:
        nref += 1
        xs.append(mean([v for i, v in enumerate(lst) if i % 2 == 0])); ys.append(mean([v for i, v in enumerate(lst) if i % 2 == 1]))
r_ = pearson(xs, ys)
out['referee'] = {'n_referees_ge10_dev': nref, 'split_half_r': round(r_, 3) if r_ is not None else None,
                  'coverage_by_season': {s: round(mean([int(bool(r['referee'].strip())) for r in ROWS if r['season'] == s]), 4) for s in SEASONS}}

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s).casefold() if not unicodedata.combining(c)).strip()
idx = list(csv.DictReader(open(MAIN / 'data_enrichment' / 'fotmob_world_index.csv')))
tier_names = {}
for lid in ('55', '147'):
    for r in idx:
        if r['league_id'] == lid: tier_names.setdefault((lid, r['season']), set()).update([norm(r['home']), norm(r['away'])])
by_season_ids = {s: {r['home_team_id'] for r in ROWS if r['season'] == s} | {r['away_team_id'] for r in ROWS if r['season'] == s} for s in SEASONS}
name_by_id_season = {}
for r in ROWS:
    name_by_id_season[(r['season'], r['home_team_id'])] = r['home_team']; name_by_id_season[(r['season'], r['away_team_id'])] = r['away_team']
movers = {}
for i, s in enumerate(SEASONS):
    if i == 0: continue
    prev = SEASONS[i - 1]
    new_ids = by_season_ids[s] - by_season_ids[prev]
    mu = mean([float(r['goals_for']) for r in TM if r['season'] == s])
    groups = defaultdict(list)
    for tid in new_ids:
        nm = norm(name_by_id_season.get((s, tid), ''))
        nm = {'ac reggiana 1919': 'reggiana'}.get(nm, nm)  # Serie C index spells the club 'Reggiana'
        src = 'serie_a' if nm in tier_names.get(('55', prev), set()) else ('serie_c' if nm in tier_names.get(('147', prev), set()) else 'unknown')
        groups[src].append(tid)
    rec = {'churn_new_teams': len(new_ids), 'mu_team_goals': round(mu, 4), 'by_source': {}}
    for src, tids in groups.items():
        ms = [r for r in TM if r['season'] == s and r['team_id'] in tids]
        rec['by_source'][src] = {'n_clubs': len(tids), 'team_matches': len(ms),
            'gf': round(mean([float(r['goals_for']) for r in ms]), 4), 'ga': round(mean([float(r['goals_against']) for r in ms]), 4),
            'dgf': round(mean([float(r['goals_for']) for r in ms]) - mu, 4), 'dga': round(mean([float(r['goals_against']) for r in ms]) - mu, 4),
            'clubs': sorted({name_by_id_season.get((s, t), t) for t in tids})}
    movers[s] = rec
out['movers'] = movers
for pool_label, ss in [('entry_2022_2026', SEASONS[1:5]), ('entry_all', SEASONS[1:])]:
    pooled = {}
    for src in ('serie_a', 'serie_c'):
        gf, ga, mus, n = [], [], [], 0
        for s in ss:
            rec = movers.get(s, {}).get('by_source', {}).get(src)
            if not rec: continue
            gf += [rec['gf']] * rec['team_matches']; ga += [rec['ga']] * rec['team_matches']; mus += [movers[s]['mu_team_goals']] * rec['team_matches']; n += rec['team_matches']
        if n: pooled[src] = {'team_matches': n, 'gf': round(mean(gf), 4), 'ga': round(mean(ga), 4), 'mu': round(mean(mus), 4),
                             'dgf': round(mean(gf) - mean(mus), 4), 'dga': round(mean(ga) - mean(mus), 4)}
    out['movers_pooled_' + pool_label] = pooled

comp = [r for r in ROWS if r['season'] in DEV_SEASONS + ['2025/2026']]
hg = mean([int(r['home_goals']) for r in comp]); ag = mean([int(r['away_goals']) for r in comp])
out['home_adv_pooled_complete'] = {'home_goals': hg, 'away_goals': ag, 'ratio': round(hg / ag, 4), 'n': len(comp)}
for s in SEASONS:
    rs = [r for r in ROWS if r['season'] == s]
    xv = [tot(r, 'expected_goals') for r in rs]
    if sum(v is not None for v in xv) > 50:
        gg = sum(int(r['home_goals']) + int(r['away_goals']) for r, v in zip(rs, xv) if v is not None)
        xx = sum(v for v in xv if v is not None)
        out.setdefault('xg_descriptive', {})[s] = {'goals_over_xg': round(gg / xx, 4), 'n_with_xg': sum(v is not None for v in xv)}
json.dump(out, open(HERE / 'eda_numbers.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
