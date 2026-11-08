import json, glob, statistics
from collections import Counter, defaultdict

rows = []
for p in sorted(glob.glob('league/audit_scratch/class_batch*.jsonl')):
    rows += [json.loads(l) for l in open(p)]
print("TOTAL ROWS:", len(rows))
assert len(rows) == 785, len(rows)
leagues = {r['league'] for r in rows}
print("leagues covered:", len(leagues))

print("\n== OUTCOMES ==")
for k, v in Counter(r['outcome'] for r in rows).most_common(): print(f"  {k}: {v}")
print("\n== FAIL POINTS ==")
for k, v in Counter(r['fail_point'] for r in rows).most_common(): print(f"  {k}: {v}")

print("\n== FAIL POINT x MARKET ==")
mkts = ['G', 'S', 'C', 'K', 'T']
fps = ['dev', 'sealed', 'not_buildable', 'not_built', 'none']
print("  market | " + " | ".join(fps) + " | pass_rate_of_built")
for m in mkts:
    sub = [r for r in rows if r['market'] == m]
    c = Counter(r['fail_point'] for r in sub)
    built = [r for r in sub if r['fail_point'] in ('dev', 'sealed', 'none')]
    passed = sum(1 for r in sub if r['outcome'] in ('PASS_CLEAN', 'PASS_PROV'))
    pr = f"{passed}/{len(built)} = {passed/len(built):.0%}" if built else "-"
    print(f"  {m}: " + " | ".join(str(c.get(f, 0)) for f in fps) + f" | {pr}")

print("\n== SIZE BANDS (matches_total) x FAIL POINT ==")
def band(r):
    mt = r['matches_total']
    if mt is None: return 'unstated'
    if mt >= 3000: return '>=3000'
    if mt >= 1500: return '1500-2999'
    return '<1500'
bands = ['>=3000', '1500-2999', '<1500', 'unstated']
for b in bands:
    sub = [r for r in rows if band(r) == b]
    c = Counter(r['fail_point'] for r in sub)
    passed = sum(1 for r in sub if r['outcome'] in ('PASS_CLEAN', 'PASS_PROV'))
    print(f"  {b}: n={len(sub)} dev={c.get('dev',0)} sealed={c.get('sealed',0)} NB={c.get('not_buildable',0)} NBt={c.get('not_built',0)} pass={passed}")

print("\n== STATS SEASONS ==  (candidates by stats_seasons)")
for ss in [0, 1, 2, 3, None]:
    sub = [r for r in rows if r['stats_seasons'] == ss]
    if not sub: continue
    passed = sum(1 for r in sub if r['outcome'] in ('PASS_CLEAN', 'PASS_PROV'))
    print(f"  stats_seasons={ss}: n={len(sub)} pass={passed} ({passed/len(sub):.0%})")

print("\n== FAIL LEGS ==")
legs = Counter()
for r in rows:
    for l in r['fail_legs']: legs[l] += 1
for k, v in legs.most_common(): print(f"  {k}: {v}")

print("\n== MECHANISMS on FAIL rows (multi-tag) ==")
mech = Counter()
for r in rows:
    if r['outcome'] == 'FAIL':
        for m in r['mechanisms']: mech[m] += 1
for k, v in mech.most_common(): print(f"  {k}: {v}")
print("FAIL rows total:", sum(1 for r in rows if r['outcome'] == 'FAIL'))
print("gate_architecture:", mech.get('gate_architecture', 0))
ga = [r for r in rows if 'gate_architecture' in r['mechanisms']]
for r in ga: print("   GA:", r['league'], r['market'])

print("\n== NB MISSING ==")
for k, v in Counter(r['nb_missing'] for r in rows if r['outcome'] == 'NOT_BUILDABLE').most_common(): print(f"  {k}: {v}")
nb_num = sum(1 for r in rows if r['outcome'] == 'NOT_BUILDABLE' and any(ch.isdigit() for ch in (r['nb_detail'] or '')))
nb_tot = sum(1 for r in rows if r['outcome'] == 'NOT_BUILDABLE')
print(f"NB rows with numeric payload evidence: {nb_num}/{nb_tot}")

print("\n== EDA SELF-AUDIT (sealed fails) ==")
sealed = [r for r in rows if r['fail_point'] == 'sealed']
print("sealed fails:", len(sealed), Counter(r['eda_judgement'] for r in sealed))
print("by market:", Counter(r['market'] for r in sealed))

print("\n== SEALED CALIBRATION BREACH/SE ==")
cal = [r for r in sealed if any(l.startswith('CAL') for l in r['fail_legs'])]
bos = [r['breach_over_se'] for r in cal if r['breach_over_se'] is not None]
print(f"cal-leg sealed fails: {len(cal)}; with breach/SE: {len(bos)}")
if bos:
    print(f"  median {statistics.median(bos):.2f} | <=1: {sum(1 for x in bos if x<=1)} | 1-2: {sum(1 for x in bos if 1<x<=2)} | 2-3: {sum(1 for x in bos if 2<x<=3)} | >3: {sum(1 for x in bos if x>3)}")

print("\n== PASS SPLIT ==")
print(Counter(r['outcome'] for r in rows if r['outcome'].startswith('PASS')))
bym = defaultdict(Counter)
for r in rows: bym[r['market']][r['outcome']] += 1
for m in mkts: print(" ", m, dict(bym[m]))
