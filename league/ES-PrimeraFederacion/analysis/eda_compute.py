"""Compute scores/events-only descriptive EDA for ES Primera Federacion."""
import csv, json, math, statistics as st, unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent / 'data' / 'espf_matches.csv')))
SEASONS = ['2021/2022','2022/2023','2023/2024','2024/2025','2025/2026','2026/2027']
DEV = SEASONS[:4]; EVAL = SEASONS[1:4]; VIRGIN = ['2025/2026']
assert len(ROWS) == 4081

def pearson(xs, ys):
    if len(xs) < 2: return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / den if den else None

def half_reliability(seasons, mode):
    pairs = []
    for season in seasons:
        rs = [r for r in ROWS if r['season'] == season]
        by_team = defaultdict(list)
        for r in sorted(rs, key=lambda x: (x['date'], x['match_id'])):
            for side, opp in (('home','away'), ('away','home')):
                if mode == 'chronological':
                    by_team[r[f'{side}_team_id']].append((int(r[f'{side}_goals']), int(r[f'{opp}_goals'])))
                elif r['round'].isdigit():
                    # Regular rounds only: play-offs are a different phase
                    # (cross-group ties, 6-14 matches/season for few teams)
                    # and must not land in either half of a league split.
                    n = int(r['round'])
                    by_team[r[f'{side}_team_id']].append((n, int(r[f'{side}_goals']), int(r[f'{opp}_goals'])))
        for vals in by_team.values():
            if mode == 'chronological':
                cut = len(vals) // 2; a, b = vals[:cut], vals[cut:]
            else:
                a = [v for v in vals if v[0] <= 19]; b = [v for v in vals if v[0] >= 20]
                a = [(v[1], v[2]) for v in a]; b = [(v[1], v[2]) for v in b]
            if a and b: pairs.append((st.mean(v[0] for v in a), st.mean(v[0] for v in b), st.mean(v[1] for v in a), st.mean(v[1] for v in b)))
    return {'gf_r': round(pearson([p[0] for p in pairs], [p[1] for p in pairs]), 3), 'ga_r': round(pearson([p[2] for p in pairs], [p[3] for p in pairs]), 3), 'n_team_seasons': len(pairs)}

def half_share(rs):
    # Restrict to matches whose Goal events are complete: the 16 awarded
    # 2021/2022 matches carry goals in the score with no events, so their
    # goals must not enter the denominator (they would drag the share down
    # by counting goals that could never be first-half goals).
    rs = [r for r in rs if int(r['goal_events_complete'])]
    shares, totals = [], []
    for r in rs:
        total = int(r['home_goals']) + int(r['away_goals'])
        if total:
            shares.append((int(r['ht_home_goals']) + int(r['ht_away_goals'])) / total); totals.append(total)
    p = sum(int(r['ht_home_goals']) + int(r['ht_away_goals']) for r in rs if int(r['home_goals']) + int(r['away_goals'])) / sum(totals) if shares else None
    obs = st.variance(shares) if len(shares) > 1 else 0
    noise = st.mean([p*(1-p)/n for n in totals]) if shares else None
    return {'n': len(shares), 'share': round(p, 4) if p is not None else None, 'observed_sd': round(math.sqrt(obs), 4) if p is not None else None, 'binomial_noise_sd': round(math.sqrt(noise), 4) if noise is not None else None, 'true_sd': round(math.sqrt(max(0, obs-noise)), 4) if noise is not None else None, 'ht_goals': sum(int(r['ht_home_goals']) + int(r['ht_away_goals']) for r in rs), 'goals': sum(int(r['home_goals']) + int(r['away_goals']) for r in rs)}

def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(c)).strip().lower()
idx = list(csv.DictReader(open('/home/hatch/workspace/footballprediction/data_enrichment/fotmob_world_index.csv')))
def index_names(league, season):
    return {norm(x) for r in idx if r['league_id'] == league and r['season'] == season for x in (r['home'], r['away'])}

team_season = {s: {r['home_team_id'] for r in ROWS if r['season'] == s} | {r['away_team_id'] for r in ROWS if r['season'] == s} for s in SEASONS}
id_name = {}
for r in ROWS:
    id_name.setdefault(r['home_team_id'], r['home_team']); id_name.setdefault(r['away_team_id'], r['away_team'])

out = {'seasons': SEASONS, 'n': len(ROWS), 'per_season': {}}
for s in SEASONS:
    rs = [r for r in ROWS if r['season'] == s]; goals = [int(r['home_goals']) + int(r['away_goals']) for r in rs]
    out['per_season'][s] = {'n': len(rs), 'goals_per_match': round(st.mean(goals), 4), 'home_goals_per_match': round(st.mean([int(r['home_goals']) for r in rs]), 4), 'away_goals_per_match': round(st.mean([int(r['away_goals']) for r in rs]), 4), 'H_rate': round(sum(int(r['home_goals']) > int(r['away_goals']) for r in rs)/len(rs), 4), 'D_rate': round(sum(int(r['home_goals']) == int(r['away_goals']) for r in rs)/len(rs), 4), 'A_rate': round(sum(int(r['home_goals']) < int(r['away_goals']) for r in rs)/len(rs), 4), 'OU2.5_over_rate': round(sum(g > 2.5 for g in goals)/len(rs), 4), 'phase_counts': {p: sum(r['phase'] == p for r in rs) for p in ('regular','playoff')}, 'awarded_count': sum(int(r['awarded']) for r in rs), 'extra_time_count': sum(int(r['extra_time']) for r in rs), 'coverage': {'stats': round(100*sum(int(r['has_stats_all']) for r in rs)/len(rs), 1), 'half': round(100*sum(int(r['has_stats_half']) for r in rs)/len(rs), 1), 'shotmap': round(100*sum(int(r['has_shotmap']) for r in rs)/len(rs), 1), 'events': round(100*sum(int(r['has_events']) for r in rs)/len(rs), 1), 'referee': round(100*sum(bool(r['referee']) for r in rs)/len(rs), 1), 'matches_with_any_card_event': round(100*sum(int(r['ev_card_total']) > 0 for r in rs)/len(rs), 1), 'goal_events_complete': round(100*sum(int(r['goal_events_complete']) for r in rs)/len(rs), 1)}}

out['reliability'] = {'chronological_halves': half_reliability(DEV, 'chronological'), 'rounds_1_19_vs_20_38_regular': half_reliability(DEV, 'rounds')}
out['half_shares_goals_events'] = {'dev_pooled': half_share([r for r in ROWS if r['season'] in DEV]), 'per_season': {s: half_share([r for r in ROWS if r['season'] == s]) for s in SEASONS}}

movers = {}; mover_classes = {}
for i, s in enumerate(SEASONS[1:], 1):
    prev = SEASONS[i-1]; entries = team_season[s] - team_season[prev]
    ll_names = index_names('140', prev)
    from_ll = sorted(id_name[t] for t in entries if norm(id_name[t]) in ll_names)
    below = sorted(id_name[t] for t in entries if norm(id_name[t]) not in ll_names)
    assert len(from_ll) == 4 and len(below) == 10, (s, from_ll, below)
    movers[s] = {'from_LaLiga2': from_ll, 'from_below': below}; mover_classes[s] = {t: 'from_LaLiga2' if norm(id_name[t]) in ll_names else 'from_below' for t in entries}
out['movers'] = movers

def mover_perf(seasons, baseline_seasons=None):
    groups = defaultdict(lambda: [[], []]); all_rows = [r for r in ROWS if r['season'] in seasons]
    for r in all_rows:
        for side, opp in (('home','away'), ('away','home')):
            cls = mover_classes.get(r['season'], {}).get(r[f'{side}_team_id'])
            if cls: groups[cls][0].append(int(r[f'{side}_goals'])); groups[cls][1].append(int(r[f'{opp}_goals']))
    baseline_rows = [r for r in ROWS if r['season'] in (baseline_seasons or seasons)]
    mu = sum(int(r['home_goals']) + int(r['away_goals']) for r in baseline_rows) / (2*len(baseline_rows))
    result = {'mu': round(mu, 4), 'n_matches': len(baseline_rows)}
    for cls in ('from_LaLiga2','from_below'):
        gf, ga = groups[cls]; gfm, gam = st.mean(gf), st.mean(ga)
        result[cls] = {'team_matches': len(gf), 'gf_per_match': round(gfm, 4), 'ga_per_match': round(gam, 4), 'gd_per_match': round(gfm-gam, 4), 'delta_gf_vs_mu': round(gfm-mu, 4), 'delta_ga_vs_mu': round(gam-mu, 4)}
    return result
out['mover_perf_dev'] = mover_perf(EVAL, DEV)
# Descriptive only, NOT a frozen input: entry seasons through the last
# complete season. The partial 2026/2027 season is excluded.
out['mover_perf_pooled_incl_virgin'] = mover_perf(['2022/2023', '2023/2024', '2024/2025', '2025/2026'])

out['churn'] = {'distinct_teams_per_season': {s: len(team_season[s]) for s in SEASONS}, 'entries': {s: {'count': len(team_season[s]-team_season[SEASONS[i-1]]), 'teams': sorted(id_name[t] for t in team_season[s]-team_season[SEASONS[i-1]])} for i, s in enumerate(SEASONS[1:], 1)}, 'distinct_teams_overall': len(set().union(*team_season.values()))}
def card_evidence(s):
    rs = [r for r in ROWS if r['season'] == s]
    return {'matches_with_any_card_event': sum(int(r['ev_card_total']) > 0 for r in rs), 'total_card_events': sum(int(r['ev_card_total']) for r in rs), 'card_events_per_match': round(sum(int(r['ev_card_total']) for r in rs)/len(rs), 4)}
out['cards_evidence'] = {s: card_evidence(s) for s in SEASONS}
def ou(s):
    rs = [r for r in ROWS if r['season'] in s]; return round(sum(int(r['home_goals'])+int(r['away_goals']) > 2.5 for r in rs)/len(rs), 4)
out['over_rates'] = {'EVAL': ou(EVAL), 'VIRGIN': ou(VIRGIN)}
dev_rows = [r for r in ROWS if r['season'] in DEV]
out['home_advantage_dev'] = {'home_win_rate_pct': round(100*sum(int(r['home_goals']) > int(r['away_goals']) for r in dev_rows)/len(dev_rows), 2), 'home_goals_per_match': round(st.mean([int(r['home_goals']) for r in dev_rows]), 4), 'away_goals_per_match': round(st.mean([int(r['away_goals']) for r in dev_rows]), 4), 'home_goals_share': round(sum(int(r['home_goals']) for r in dev_rows)/sum(int(r['home_goals'])+int(r['away_goals']) for r in dev_rows), 4)}
out['groups'] = {s: {str(g): len({r['home_team_id'] for r in ROWS if r['season'] == s and r['group_home'] == g} | {r['away_team_id'] for r in ROWS if r['season'] == s and r['group_away'] == g}) for g in ('1','2')} for s in SEASONS}
json.dump(out, open(HERE / 'eda_numbers.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
