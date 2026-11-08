"""Reproducible Cyprus 2. Division inventory and EDA; deliberately no fitting.

Scores + events corpus only: goals are the only target with data. The
mover-gap section measures relegated-in teams (previous season in
CY-1Division, FotMob 136) on pre-virgin transitions only.
"""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / 'data' / 'cy2_matches.csv').open()))
WAREHOUSE = Path.home() / 'workspace' / 'footballprediction'
SEASONS = sorted({r['season'] for r in ROWS})
DEV_SCORED = ['2022/2023', '2023/2024', '2024/2025']
PRE_VIRGIN = ['2021/2022', '2022/2023', '2023/2024', '2024/2025']
MOVER_SEASONS = ['2022/2023', '2023/2024', '2024/2025']  # pre-virgin arrivals only


def f(r, k):
    try:
        return None if r.get(k) in ('', None, 'None') else float(r[k])
    except (TypeError, ValueError):
        return None


def avg(x):
    return round(st.mean(x), 3) if x else None


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def corr(x, y):
    if len(x) < 5:
        return None
    mx, my = st.mean(x), st.mean(y)
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return round(sum((a - mx) * (b - my) for a, b in zip(x, y)) / den, 3) if den else None


def goals(r):
    return int(r['home_goals']) + int(r['away_goals'])


def over(v, line):
    return round(sum(x > line for x in v) / len(v), 3) if v else None


def levels(rows):
    gs = [goals(r) for r in rows]
    n = len(rows)
    return {
        'matches': n, 'goals_per_match': avg(gs),
        'home_goals_per_match': avg([int(r['home_goals']) for r in rows]),
        'away_goals_per_match': avg([int(r['away_goals']) for r in rows]),
        'home_win_rate': round(sum(int(r['home_goals']) > int(r['away_goals']) for r in rows) / n, 3),
        'draw_rate': round(sum(r['home_goals'] == r['away_goals'] for r in rows) / n, 3),
        'away_win_rate': round(sum(int(r['home_goals']) < int(r['away_goals']) for r in rows) / n, 3),
        'btts_rate': round(sum(int(r['home_goals']) > 0 and int(r['away_goals']) > 0 for r in rows) / n, 3),
        'ou1_5_over_rate': over(gs, 1.5), 'ou2_5_over_rate': over(gs, 2.5), 'ou3_5_over_rate': over(gs, 3.5),
        'home_advantage_goals': avg([int(r['home_goals']) - int(r['away_goals']) for r in rows]),
        'coverage': {
            'events': pct(sum(r['has_events'] == '1' for r in rows), n),
            'ht_derivable': pct(sum(r['ht_source'] == 'events' for r in rows), n),
            'stats_all': 0.0, 'stats_flag': pct(sum(r['has_stats_flag'] == '1' for r in rows), n),
            'period_splits': 0.0, 'shotmap': 0.0, 'lineup': 0.0, 'referee': 0.0,
        },
    }


def reliability(rows):
    out = {}
    for name, against in (('goals_for', False), ('goals_against', True)):
        d = defaultdict(list)
        for r in rows:
            for side, other in (('home', 'away'), ('away', 'home')):
                val = float(r[other + '_goals']) if against else float(r[side + '_goals'])
                d[(r[side + '_team_id'], r['season'])].append(val)
        a, b = [], []
        for v in d.values():
            if len(v) >= 8:
                a.append(st.mean(v[::2]))
                b.append(st.mean(v[1::2]))
        out[name] = {'r': corr(a, b), 'n_team_seasons': len(a)}
    return out


def half(rows):
    shares, first, full = [], [], []
    for r in rows:
        a = f(r, 'ht_home_goals')
        b = f(r, 'ht_away_goals')
        tot = float(r['home_goals']) + float(r['away_goals'])
        if a is not None and b is not None and tot > 0:
            shares.append((a + b) / tot)
            first.append(a + b)
            full.append(tot)
    if not shares:
        return {'n': 0, 'share_1h': None}
    p = sum(first) / sum(full)
    noise = st.mean([p * (1 - p) / x for x in full])
    obs = st.variance(shares) if len(shares) > 1 else 0
    return {'n': len(shares), 'share_1h': round(p, 4), 'observed_variance': round(obs, 5),
            'noise_expectation': round(noise, 5), 'true_variance': round(obs - noise, 5),
            'noise_ratio': round(obs / noise, 3) if noise else None, 'noise_model': 'binomial'}


def cy1_teams_by_season():
    """Team ids per season in CY-1Division (FotMob 136), from warehouse JSONs."""
    idx = list(csv.DictReader((WAREHOUSE / 'data_enrichment' / 'fotmob_world_index.csv').open()))
    out = defaultdict(set)
    for r in idx:
        if r['league_id'] != '136':
            continue
        d = json.loads((WAREHOUSE / r['path'].rstrip('\r')).read_text())
        g = d.get('general') or {}
        for t in (g.get('homeTeam') or {}, g.get('awayTeam') or {}):
            if t.get('id'):
                out[r['season']].add(str(t['id']))
    return out


def mover_gap():
    """Relegated-in teams (CY-1 last season) vs league, first CY-2 season.

    Pre-virgin transitions only. Also reports promoted-out teams' last
    CY-2 season and brand-new ids' first season, for context.
    """
    t1 = cy1_teams_by_season()
    by_season = defaultdict(set)
    for r in ROWS:
        by_season[r['season']].add(r['home_team_id'])
        by_season[r['season']].add(r['away_team_id'])
    seasons = sorted(by_season)
    detail, agg = [], {'relegated_in': [], 'promoted_out_last': [], 'brand_new': []}
    for i, s in enumerate(seasons):
        if s not in MOVER_SEASONS or i == 0:
            continue
        prev = seasons[i - 1]
        relegated_in = (by_season[s] & t1.get(prev, set())) - by_season[prev]
        promoted_out = (by_season[prev] & t1.get(s, set())) - by_season[s]
        brand_new = by_season[s] - by_season[prev] - t1.get(prev, set())
        lg = [r for r in ROWS if r['season'] == s]
        lg_gf = st.mean([goals(r) for r in lg]) / 2  # goals per team-match, league-wide
        for group, ids, season in (('relegated_in', relegated_in, s),
                                   ('promoted_out_last', promoted_out, prev),
                                   ('brand_new', brand_new, s)):
            for tid in sorted(ids):
                tm = [r for r in ROWS if r['season'] == season and (r['home_team_id'] == tid or r['away_team_id'] == tid)]
                gf = st.mean([int(r['home_goals']) if r['home_team_id'] == tid else int(r['away_goals']) for r in tm])
                ga = st.mean([int(r['away_goals']) if r['home_team_id'] == tid else int(r['home_goals']) for r in tm])
                pts = sum(3 if (int(r['home_goals']) > int(r['away_goals']) and r['home_team_id'] == tid) or
                            (int(r['away_goals']) > int(r['home_goals']) and r['away_team_id'] == tid) else
                          1 if r['home_goals'] == r['away_goals'] else 0 for r in tm) / len(tm)
                name = next((r['home_team'] if r['home_team_id'] == tid else r['away_team'] for r in tm), tid)
                detail.append({'season': season, 'group': group, 'team_id': tid, 'team': name,
                               'n': len(tm), 'gf': round(gf, 3), 'ga': round(ga, 3), 'ppg': round(pts, 3),
                               'league_gf_per_team_match': round(lg_gf, 3) if season == s else None})
                agg[group].append((gf, ga, pts))
    summary = {}
    for group, vals in agg.items():
        if vals:
            summary[group] = {'n_team_seasons': len(vals),
                              'mean_gf': round(st.mean([v[0] for v in vals]), 3),
                              'mean_ga': round(st.mean([v[1] for v in vals]), 3),
                              'mean_ppg': round(st.mean([v[2] for v in vals]), 3)}
    lg_pre = [r for r in ROWS if r['season'] in MOVER_SEASONS]
    lg_gf = round(st.mean([goals(r) for r in lg_pre]) / 2, 3)
    lg_pts = sum(3 if r['home_goals'] != r['away_goals'] else 2 for r in lg_pre) / 2 / len(lg_pre)
    summary['league_baseline_pre_virgin_mover_seasons'] = {'mean_gf_per_team_match': lg_gf,
                                                           'mean_ppg': round(lg_pts, 3)}
    return {'detail': detail, 'summary': summary}


def season_inventory(rows, s):
    x = [r for r in rows if r['season'] == s]
    ids = {r[k] for r in x for k in ('home_team_id', 'away_team_id')}
    names = defaultdict(set)
    for r in x:
        names[r['home_team_id']].add(r['home_team'])
        names[r['away_team_id']].add(r['away_team'])
    return {'matches': len(x), 'distinct_team_ids': len(ids),
            'phase_counts': dict(sorted((p, sum(r['phase'] == p for r in x)) for p in {r['phase'] for r in x})),
            'date_range': [min(r['date'] for r in x), max(r['date'] for r in x)],
            'multi_name_ids': {k: sorted(v) for k, v in names.items() if len(v) > 1}}


def main():
    per = {s: {**levels([r for r in ROWS if r['season'] == s]), **season_inventory(ROWS, s)} for s in SEASONS}
    names = defaultdict(set)
    for r in ROWS:
        names[r['home_team_id']].add(r['home_team'])
        names[r['away_team_id']].add(r['away_team'])
    dev = [r for r in ROWS if r['season'] in DEV_SCORED]
    pre_virgin = [r for r in ROWS if r['season'] in PRE_VIRGIN]
    virgin = [r for r in ROWS if r['season'] == '2025/2026']
    lines = {'goals': {
        'candidate_lines': {str(l): {'over_rate': over([goals(r) for r in dev], l), 'n': len(dev)}
                            for l in (1.5, 2.5, 3.5)},
        'primary_line': 2.5, 'n': len(dev),
        'dev_over_2_5': over([goals(r) for r in dev], 2.5),
    }}
    mg = mover_gap()
    inventory = {
        'league': 'CY-2Division', 'league_id': '9100', 'rows': len(ROWS), 'team_rows': len(ROWS) * 2,
        'seasons': per, 'distinct_team_ids': len(names),
        'multi_name_team_ids': {k: sorted(v) for k, v in names.items() if len(v) > 1},
        'phase_values': sorted({r['phase'] for r in ROWS}),
        'phase_counts': {s: per[s]['phase_counts'] for s in SEASONS},
        'cards_source_counts': {'events': sum(r['cards_source'] == 'events' for r in ROWS)},
        'plain_yellow_cards_in_events': 0,
        'yellowred_cards_in_events': sum(int(r['ev_yellowred_home']) + int(r['ev_yellowred_away']) for r in ROWS),
        'red_cards_in_events': sum(int(r['red_home']) + int(r['red_away']) for r in ROWS),
        'stats_flag_vs_payload': {'has_stats_flag': sum(r['has_stats_flag'] == '1' for r in ROWS),
                                  'has_stats_all': 0},
        'events_present': sum(r['has_events'] == '1' for r in ROWS),
        'goal_event_score_mismatch': [],
        'stats_periods': [], 'stats_keys': [],
        'referee_nonempty': 0,
    }
    out = {'league': 'CY-2Division', 'league_id': '9100', 'n': len(ROWS), 'seasons': SEASONS,
           'per_season': per, 'pooled_levels': levels(ROWS), 'pooled_dev_levels': levels(dev),
           'reliability': reliability(ROWS),
           'halves': {'goals': half(pre_virgin),
                      'definition': 'pooled pre-virgin seasons 2021/2022-2024/2025; event-derived first halves; 2021/2022 has no events'},
           'dev_line_tables': lines, 'mover_gap': mg,
           'windows': {'seed': '2021/2022', 'goals_dev_scored': sorted(DEV_SCORED),
                       'virgin': '2025/2026', 'virgin_n': len(virgin), 'confirmatory': '2026/2027'},
           'inventory': inventory}
    (HERE / 'eda_numbers.json').write_text(json.dumps(out, indent=2))
    (HERE / 'inventory_summary.json').write_text(json.dumps(inventory, indent=2))
    print(json.dumps({'n': len(ROWS), 'lines': lines, 'halves': out['halves'],
                      'reliability': out['reliability'], 'mover_gap_summary': mg['summary'],
                      'levels': {s: per[s]['goals_per_match'] for s in SEASONS}}, indent=2))


if __name__ == '__main__':
    main()
