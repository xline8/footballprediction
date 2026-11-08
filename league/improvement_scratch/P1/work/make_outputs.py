import json, csv, os
from collections import Counter
ROOT=os.path.expanduser("~/workspace/footballprediction")
W=ROOT+"/league/improvement_scratch/P1/work"
OUT=ROOT+"/league/improvement_scratch/P1"
res=json.load(open(W+"/compute_final.json"))
REF={'S':'gate_zero','C':'gate_zero','K':'gate_zero','G':'gate_zero','T':'a'}
rows=[]
for key,v in res.items():
    if v['group']=='pass':
        flp = v['fwd'].get(v['shipped']) if v['measurable'] else None
        basis=f"shipped arm {v['shipped']}"
    else:
        flp = (any(v['fwd'][a] for a in v['eval_arms'])) if v['measurable'] else None
        basis="eval arms "+",".join(v['eval_arms'])
    ref_flp=v['fwd'].get(REF[v['market']])
    def fmt_ll(x):
        if x is None: return ''
        if isinstance(x,(list,tuple)): return ';'.join('' if i is None else f"{i:.6f}" for i in x[:3])
        return f"{x:.6f}"
    srcmap={'arms_seasons':'results_dev.json arms{seasons,pooled}+baselines','season_rows':'results_dev.json row list (arm/kind/season)',
      'total_metrics':'results_dev.json metrics{arm:{season:logloss}}+protocol.gate_pool','cards_arms':'results_dev.json arms{seasons:{model/base/naive}}',
      'goals_rows':'results_dev.json rows (arm/kind/season, ll_1x2/rps/ou)','flat_arms':'results_dev.json pooled only (single dev window)',
      'flat_single':'results_dev.json flat {model,base_rate,naive10} (single dev season)','line_rows':'results_dev.json line rows (arm/kind/season/line/ll)',
      'cards_blocks':'results_dev.json blocks_ll_at_<line> per tournament block','block_rows':'results_dev.json per-block rows (arm at top level)'}
    rows.append({'league':v['league'],'market':v['market'],'candidate':v['candidate'],'group':v['group'],
      'measurable':'y' if v['measurable'] else 'n',
      'forward_leg_pass':('y' if flp else 'n') if v['measurable'] else '',
      'forward_leg_pass_ref_arm':('y' if ref_flp else 'n') if ref_flp is not None else '',
      'basis':basis,'shipped_arm':v['shipped'] or '','eval_arms':",".join(v['eval_arms']),
      'last_dev_season':v['last_season'] or '','n_dev_seasons':v['n_dev_seasons'],'single_window_flat':'y' if v['flat_single_window'] else 'n',
      'gate_line':v['gate_line'] or '','gate_line_src':v['gate_line_src'] or '',
      'arm_ll_last':fmt_ll(v['arm_last_ll'].get(v['shipped']) if v['group']=='pass' and v['shipped'] else (v['arm_last_ll'].get(v['eval_arms'][0]) if v['eval_arms'] else None)),
      'base_ll_last':fmt_ll(v['base_last']),'naive_ll_last':fmt_ll(v['naive_last']),
      'source':srcmap.get(v['schema'],v['schema'])+' | engine/'+v['market'].lower()+' path in league tree',
      'schema':v['schema'],'notes':(v['unmeas_reason'] if not v['measurable'] else '')})
rows.sort(key=lambda r:(r['group'],r['league'],r['market']))
with open(OUT+"/per_candidate.csv","w",newline="") as f:
    wtr=csv.DictWriter(f, fieldnames=list(rows[0].keys())); wtr.writeheader(); wtr.writerows(rows)
print("wrote", OUT+"/per_candidate.csv", len(rows), "rows")
# summaries
def summ(group):
    g=[v for v in res.values() if v['group']==group]; m=[v for v in g if v['measurable']]
    return g,m
cal,cal_m=summ('sealed_cal_fail'); pas,pas_m=summ('pass'); oth,oth_m=summ('sealed_other_fail')
A=[v for v in cal_m if not any(v['fwd'][a] for a in v['eval_arms'])]
B=[v for v in pas_m if v['fwd'].get(v['shipped'])==False]
print(f"A headline {len(A)}/{len(cal_m)}")
print(f"B headline {len(B)}/{len(pas_m)}")
print("A by market:", Counter(v['market'] for v in A), "of cal_m:", Counter(v['market'] for v in cal_m))
print("B by market:", Counter(v['market'] for v in B), "of pas_m:", Counter(v['market'] for v in pas_m))
print("other-group stopped (info):", sum(1 for v in oth_m if not any(v['fwd'][a] for a in v['eval_arms'])), "/", len(oth_m))
print("single-season (n=1) in cal_m:", sum(1 for v in cal_m if v['n_dev_seasons']==1), "in pas_m:", sum(1 for v in pas_m if v['n_dev_seasons']==1))
print("flat single-window in cal_m:", [v['candidate'] for v in cal_m if v['flat_single_window']], "in pas_m:", [v['candidate'] for v in pas_m if v['flat_single_window']])
