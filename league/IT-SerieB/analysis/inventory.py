"""Inventory and coverage report for IT-SerieB."""
import csv, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader(open(HERE.parent/'data/itserieb_matches.csv')))
def num(r,k):
    try: return float(r.get(k,''))
    except (TypeError,ValueError): return None
def pct(n,d): return round(100*n/d,1) if d else None
def total(r,k):
    a,b=num(r,k+'_home'),num(r,k+'_away')
    return a+b if a is not None and b is not None else None
seasons=sorted({r['season'] for r in ROWS})
out={'n':len(ROWS),'seasons':seasons,'per_season':{}}
for s in seasons:
    rs=[r for r in ROWS if r['season']==s]; n=len(rs)
    out['per_season'][s]={'n':n,'finished':n,'phase_counts':dict(Counter(r['phase'] for r in rs)),
      'teams':len({x for r in rs for x in (r['home_team_id'],r['away_team_id'])}),
      'coverage':{'stats_all':pct(sum(r['has_stats_all']=='1' for r in rs),n),'stats_half':pct(sum(r['has_stats_half']=='1' for r in rs),n),
       'shotmap':pct(sum(r['has_shotmap']=='1' for r in rs),n),'expected_goals':pct(sum(total(r,'expected_goals') is not None for r in rs),n),
       'touches_opp_box':pct(sum(num(r,'touches_opp_box_home') is not None and num(r,'touches_opp_box_away') is not None for r in rs),n),
       'referee':pct(sum(bool(r['referee'].strip()) for r in rs),n),'events':pct(sum(r['has_events']=='1' for r in rs),n)}}
json.dump(out,open(HERE/'inventory_summary.json','w'),indent=1)
print(json.dumps(out,indent=1))
