"""Inventory + EDA for KR-KLeague2 (FotMob id 9116).

Population: REGULAR-season matches only for levels/reliability/lines
(play-off rows are a frozen exclusion; inventory reports them separately).
Outputs inventory_summary.json + eda_summary.json beside this file.
Parent corpus for the X2 mover check: league/KR-KLeague1/data/kr_matches.csv
in the MAIN checkout (gitignored runtime data, read-only here).
"""
import csv, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent; DATA = HERE.parent / 'data'
MAIN_REPO = Path('/home/hatch/workspace/footballprediction')

def rows(p):
    with open(p, newline='') as f: return list(csv.DictReader(f))
M_ALL = rows(DATA / 'kr2_matches.csv')
M = [r for r in M_ALL if r['phase'] == 'regular']
T = [r for r in rows(DATA / 'kr2_team_matches.csv') if r['phase'] == 'regular']

def f(r, k):
    try: return float(r.get(k, ''))
    except (TypeError, ValueError): return np.nan
def mean(a):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    return float(np.mean(a)) if len(a) else None
def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); z = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[z], b[z])[0, 1]) if z.sum() > 2 and np.std(a[z]) and np.std(b[z]) else None
def split_r(items, fn, seed=90210, min_matches=24):
    rng = np.random.default_rng(seed); xs = []
    for _ in range(60):
        x = []; y = []
        for z in items.values():
            a = np.asarray([fn(q) for q in z], float); a = a[np.isfinite(a)]
            if len(a) < min_matches: continue
            ix = rng.permutation(len(a)); n = len(a) // 2
            x.append(np.mean(a[ix[:n]])); y.append(np.mean(a[ix[n:]]))
        q = corr(x, y)
        if q is not None: xs.append(q)
    return {'r': float(np.mean(xs)) if xs else None, 'n_splits': len(xs)}
def split_r_ratio(items, num, den, seed=90210, min_n=8):
    rng = np.random.default_rng(seed); xs = []
    for _ in range(60):
        x = []; y = []
        for z in items.values():
            a = [(f(q, num), f(q, den)) for q in z]
            a = [(u, v) for u, v in a if np.isfinite(u) and np.isfinite(v) and v > 0]
            if len(a) < 2 * min_n: continue
            ix = rng.permutation(len(a)); n = len(a) // 2
            x.append(sum(a[i][0] for i in ix[:n]) / sum(a[i][1] for i in ix[:n]))
            y.append(sum(a[i][0] for i in ix[n:]) / sum(a[i][1] for i in ix[n:]))
        q = corr(x, y)
        if q is not None: xs.append(q)
    return {'r': float(np.mean(xs)) if xs else None, 'n_splits': len(xs), 'method': 'ratio_of_sums'}

def levels(rs):
    def v(k): return np.array([f(r, k) for r in rs])
    g = v('home_goals') + v('away_goals'); sh = v('total_shots_home') + v('total_shots_away')
    so = v('ShotsOnTarget_home') + v('ShotsOnTarget_away'); co = v('corners_home') + v('corners_away')
    ye = v('yellow_home') + v('yellow_away')
    def disp(a): return float(np.nanvar(a, ddof=1) / np.nanmean(a)) if len(a) > 1 else None
    return {'n': len(rs), 'goals': mean(g), 'home_goals': mean(v('home_goals')), 'away_goals': mean(v('away_goals')),
            'hw_pct': 100 * float(np.mean(v('home_goals') > v('away_goals'))),
            'draw_pct': 100 * float(np.mean(v('home_goals') == v('away_goals'))),
            'btts_pct': 100 * float(np.mean((v('home_goals') > 0) & (v('away_goals') > 0))),
            'over25_pct': 100 * float(np.mean(g > 2.5)), 'shots': mean(sh), 'sot': mean(so), 'corners': mean(co),
            'yellows': mean(ye), 'reds': mean(v('red_home') + v('red_away')),
            'dispersion': {'goals': disp(g), 'sot': disp(so), 'corners': disp(co), 'yellows': disp(ye), 'shots': disp(sh)}}

def card_agreement(rs):
    both = []
    for r in rs:
        st = f(r, 'yellow_cards_home') + f(r, 'yellow_cards_away')
        ev = f(r, 'ev_yellow_home') + f(r, 'ev_yellow_away')
        if np.isfinite(st) and int(f(r, 'has_events')) == 1: both.append((st, ev))
    return {'n_both_present': len(both), 'n_stats_present_events_absent': sum(1 for r in rs if np.isfinite(f(r, 'yellow_cards_home')) and int(f(r, 'has_events')) == 0),
            'equal_n': sum(a == b for a, b in both), 'n_disagree': sum(a != b for a, b in both),
            'stats_larger_n': sum(a > b for a, b in both), 'events_larger_n': sum(b > a for a, b in both),
            'mean_stats': mean([a for a, b in both]), 'mean_events': mean([b for a, b in both])}

def main():
    seasons = sorted({r['season'] for r in M})
    inv = {}; lev = {}
    for s in seasons:
        rs = [r for r in M if r['season'] == s]; po = [r for r in M_ALL if r['season'] == s and r['phase'] == 'playoff']
        inv[s] = {'n_regular': len(rs), 'n_playoff_excluded': len(po),
                  'date_range': [min(r['date'] for r in rs), max(r['date'] for r in rs)],
                  'teams': len({r['home_team_id'] for r in rs} | {r['away_team_id'] for r in rs}),
                  'has_stats_all_pct': 100 * mean([f(r, 'has_stats_all') for r in rs]),
                  'has_stats_half_pct': 100 * mean([f(r, 'has_stats_half') for r in rs]),
                  'has_events_pct': 100 * mean([f(r, 'has_events') for r in rs]),
                  'referee_pct': 100 * sum(bool(r['referee']) for r in rs) / len(rs),
                  'xg_pct': 100 * sum(np.isfinite(f(r, 'expected_goals_home')) for r in rs) / len(rs),
                  'touches_pct': 100 * sum(np.isfinite(f(r, 'touches_opp_box_home')) for r in rs) / len(rs),
                  'big_chance_pct': 100 * sum(np.isfinite(f(r, 'big_chance_home')) for r in rs) / len(rs),
                  'possession_pct': 100 * sum(np.isfinite(f(r, 'BallPossesion_home')) for r in rs) / len(rs),
                  'yellow_stats_pct': 100 * sum(np.isfinite(f(r, 'yellow_cards_home')) for r in rs) / len(rs),
                  'missing_stats_match_ids': [r['match_id'] for r in rs if not np.isfinite(f(r, 'total_shots_home'))]}
        lev[s] = levels(rs)
    names_by_id = {}
    for r in M_ALL:
        names_by_id.setdefault(r['home_team_id'], set()).add(r['home_team'])
        names_by_id.setdefault(r['away_team_id'], set()).add(r['away_team'])
    name_variants = {k: sorted(v) for k, v in names_by_id.items() if len(v) > 1}
    # reliabilities on the stats era (2022+) for stats traits; goals/cards all eras
    groups = {}
    for r in T: groups.setdefault(r['team_id'], []).append(r)
    rel = {}
    for name, k in {'goals': 'goals', 'shots': 'total_shots', 'SOT': 'ShotsOnTarget', 'corners': 'corners',
                    'yellows_stats': 'yellow_cards', 'big_chance': 'big_chance', 'possession': 'BallPossesion',
                    'box_touches': 'touches_opp_box'}.items():
        fk = 'goals_for' if k == 'goals' else f'{k}_for'; ak = 'goals_against' if k == 'goals' else f'{k}_against'
        rel[name + '_for'] = split_r(groups, lambda r, k=fk: f(r, k))
        rel[name + '_against'] = split_r(groups, lambda r, k=ak: f(r, k))
    # unified-yellow reliability from match rows per team
    tm = {}
    for r in M:
        for side, opp in (('home', 'away'), ('away', 'home')):
            tm.setdefault(r[f'{side}_team_id'], []).append({'yellow': f(r, 'yellow_home') if side == 'home' else f(r, 'yellow_away'),
                'sot': f(r, f'ShotsOnTarget_{side}'), 'shots': f(r, f'total_shots_{side}'), 'season': r['season']})
    rel['yellows_unified_for'] = split_r(tm, lambda r: r['yellow'])
    rel['ratio_on_target_rate'] = split_r_ratio([r for r in T], 'ShotsOnTarget_for', 'total_shots_for') if False else None
    # on-target ratio reliability: rebuild items keyed by team from team_matches
    tgroups = {}
    for r in T: tgroups.setdefault(r['team_id'], []).append(r)
    rel['ratio_on_target_rate'] = split_r_ratio(tgroups, 'ShotsOnTarget_for', 'total_shots_for')
    # halves: splits era 2023-2025 for stats markets; goals via events (all eras) + splits cross-check
    halves = {}
    mk = {'goals_events': ('ht_home_goals', 'ht_away_goals', 'home_goals', 'away_goals'),
          'SOT': ('fh_ShotsOnTarget_home', 'fh_ShotsOnTarget_away', 'ShotsOnTarget_home', 'ShotsOnTarget_away'),
          'corners': ('fh_corners_home', 'fh_corners_away', 'corners_home', 'corners_away'),
          'total_shots': ('fh_total_shots_home', 'fh_total_shots_away', 'total_shots_home', 'total_shots_away'),
          'yellows_stats': ('fh_yellow_cards_home', 'fh_yellow_cards_away', 'yellow_cards_home', 'yellow_cards_away')}
    for name, (a, b, c, d) in mk.items():
        z = [r for r in M if r['season'] in ('2023', '2024', '2025') and np.isfinite(f(r, a)) and np.isfinite(f(r, c)) and f(r, c) + f(r, d) > 0]
        if name != 'goals_events': z = [r for r in z if f(r, 'has_stats_half') == 1]
        if not z: halves[name] = {'n': 0}; continue
        p = sum(f(r, a) + f(r, b) for r in z) / sum(f(r, c) + f(r, d) for r in z)
        s = np.array([(f(r, a) + f(r, b)) / (f(r, c) + f(r, d)) for r in z]); ns = np.array([f(r, c) + f(r, d) for r in z])
        halves[name] = {'n': len(z), 'share_1h': float(p), 'observed_var': float(np.var(s, ddof=1)),
                        'noise_floor': float(np.mean(p * (1 - p) / ns)), 'true_var': float(np.var(s, ddof=1) - np.mean(p * (1 - p) / ns)),
                        'seasons': sorted({r['season'] for r in z})}
    # cards halves via event times (unified target era check): count card events <=45
    # (builder stores only yellow totals per feed; event-time split needs raw JSON -> done in builder fields fh from stats; skip)
    # referee split-half on unified yellows, referees with >=20 matches
    refs = {}
    for r in M:
        if r['referee']: refs.setdefault(r['referee'], []).append(f(r, 'yellow_home') + f(r, 'yellow_away'))
    refs20 = {k: v for k, v in refs.items() if len(v) >= 20}
    ref_rel = split_r({k: [{'v': x} for x in v] for k, v in refs20.items()}, lambda r: r['v'], min_matches=20) if len(refs20) >= 3 else {'r': None}
    ref_rel['n_refs_ge20'] = len(refs20); ref_rel['n_refs_total'] = len(refs)
    ref_rel['named_matches'] = int(sum(len(v) for v in refs.values())); ref_rel['total_matches'] = len(M)
    # movers: entering teams per season, classified vs K1 corpus (prior season) and K3 (no corpus)
    k1 = rows(MAIN_REPO / 'league' / 'KR-KLeague1' / 'data' / 'kr_matches.csv')
    k1_by_season = {}
    for r in k1: k1_by_season.setdefault(r['season'], set()).add(r['home_team_id']); k1_by_season[r['season']].add(r['away_team_id'])
    by_season = {s: {r['home_team_id'] for r in M if r['season'] == s} | {r['away_team_id'] for r in M if r['season'] == s} for s in seasons}
    movers = {}
    for i, s in enumerate(seasons):
        if i == 0: continue
        prev = str(int(s) - 1); new = by_season[s] - by_season[seasons[i - 1]]
        movers[s] = {'entering': sorted(new),
                     'from_k1_prior_season': sorted(t for t in new if t in k1_by_season.get(prev, set())),
                     'from_k3_or_new_no_corpus': sorted(t for t in new if t not in k1_by_season.get(prev, set())),
                     'names': {t: sorted(names_by_id.get(t, [])) for t in sorted(new)}}
    # primary lines: goals dev 2021-2024; stats markets dev 2022-2024 (target era)
    devg = [r for r in M if r['season'] in ('2021', '2022', '2023', '2024')]
    devs = [r for r in M if r['season'] in ('2022', '2023', '2024')]
    def over(rs, k1_, k2_, line): return float(np.mean([f(r, k1_) + f(r, k2_) > line for r in rs if np.isfinite(f(r, k1_))]))
    lines = {'goals_over25_dev2021_2024': float(np.mean([f(r, 'home_goals') + f(r, 'away_goals') > 2.5 for r in devg])),
             'sot': {str(L): over(devs, 'ShotsOnTarget_home', 'ShotsOnTarget_away', L) for L in (7.5, 8.5, 9.5, 10.5)},
             'corners': {str(L): over(devs, 'corners_home', 'corners_away', L) for L in (8.5, 9.5, 10.5, 11.5)},
             'cards_unified': {str(L): over(devg, 'yellow_home', 'yellow_away', L) for L in (2.5, 3.5, 4.5)},
             'cards_unified_stats_era': {str(L): over(devs, 'yellow_home', 'yellow_away', L) for L in (2.5, 3.5, 4.5)},
             'shots': {str(L): over(devs, 'total_shots_home', 'total_shots_away', L) for L in (23.5, 24.5, 25.5, 26.5)}}
    agreement = {s: card_agreement([r for r in M if r['season'] == s]) for s in seasons}
    out = {'inventory': inv, 'team_name_variants': name_variants, 'levels': lev, 'levels_pooled': levels(M),
           'reliability': rel, 'halves_splits_era_2023_2025': halves, 'referee': ref_rel, 'movers_vs_k1': movers,
           'cards_agreement_by_season': agreement, 'dev_primary_lines': lines,
           'playoff_rows_by_season': {s: sum(1 for r in M_ALL if r['season'] == s and r['phase'] == 'playoff') for s in seasons}}
    (HERE / 'inventory_summary.json').write_text(json.dumps(inv, indent=2, default=str) + '\n')
    (HERE / 'eda_summary.json').write_text(json.dumps(out, indent=2, default=str) + '\n')
    print(json.dumps(out, indent=2, default=str))

if __name__ == '__main__': main()
