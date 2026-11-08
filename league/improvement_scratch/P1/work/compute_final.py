import json, glob, os, re
from collections import Counter
ROOT=os.path.expanduser("~/workspace/footballprediction")
W=ROOT+"/league/improvement_scratch/P1/work"
exec(open(W+"/compute.py").read().split("results={}")[0])  # reuse helpers + ext/cls loading (norm_arm, virgin_info defs etc.)

# NOTE: compute.py top part defines ext, cls, virgin_info, norm_arm, REF, ALIASES
UNMEASURABLE={
 ('BO-PrimeraDivision','S-BO'):"dev is 4 round-blocks (r11-15..r26-30) inside the single 2025 season; per-block baseline LLs not persisted (baselines pooled only in results_dev.json) and no per-match dev predictions file exists in the engine dir",
 ('CO-PrimeraA','S-COA'):"per-season baseline LLs not persisted (baselines pooled only in results_dev.json); no per-match dev predictions file",
 ('PE-Liga1','S-PE'):"per-season baseline LLs not persisted (baselines pooled only in results_dev.json); no per-match dev predictions file",
 ('PY-DivisionProfesional','S-PY'):"per-block baseline LLs not persisted (baselines pooled only in results_dev.json; verdict prints pooled baselines only); no per-match dev predictions file",
}
results={}
for key,rec in ext.items():
    league,cand=key.split('|')
    r=cls[(league,cand)]; market=rec['market']
    group='pass' if r['outcome'].startswith('PASS') else ('sealed_cal_fail' if any(l.startswith('CAL') for l in r['fail_legs']) else 'sealed_other_fail')
    flat='pooled_only_flat' in rec['notes']
    seasons=[s for s in rec['seasons'] if s!='pooled']
    def pooled_of(store):
        if store.get('pooled') is not None: return store['pooled']
        vals=[store[s] for s in seasons if store.get(s) is not None]
        if len(seasons)==1 and len(vals)==1: return vals[0]
        return None
    arms=rec['arms']; dev_pass={}; fwd={}; margins={}
    eff_last='pooled' if flat else (seasons[-1] if seasons else None)
    if market=='G':
        clim=rec['clim']; cp=pooled_of(clim)
        for an,ad in arms.items():
            ap=pooled_of(ad)
            if ap and cp and all(x is not None for x in ap[:3]) and all(x is not None for x in cp[:3]):
                dev_pass[an]=(ap[0]<cp[0] and ap[1]<cp[1] and ap[2]<cp[2])
            al=ad.get(eff_last) if eff_last else None
            cl=clim.get(eff_last) if eff_last else None
            if al and cl and all(x is not None for x in al[:3]) and all(x is not None for x in cl[:3]):
                fwd[an]=(al[0]<cl[0] and al[1]<cl[1] and al[2]<cl[2]); margins[an]=[round(cl[i]-al[i],6) for i in range(3)]
    else:
        bp=pooled_of(rec['base']); np_=pooled_of(rec['naive'])
        bl=rec['base'].get(eff_last) if eff_last else None; nl=rec['naive'].get(eff_last) if eff_last else None
        for an,ad in arms.items():
            ap=pooled_of(ad)
            if ap is not None and bp is not None and np_ is not None: dev_pass[an]=(ap<bp and ap<np_)
            al=ad.get(eff_last) if eff_last else None
            if al is not None and bl is not None and nl is not None:
                fwd[an]=(al<bl and al<nl); margins[an]=[round(bl-al,6),round(nl-al,6)]
    vi=virgin_info(league, market, cand, list(arms.keys()))
    OVERRIDE_SHIPPED={('EG-PremierLeague','C-EG'):'gate_zero', ('KZ-PremierLeague','G-KZ'):'gate_zero'}
    if (league,cand) in OVERRIDE_SHIPPED:
        vi['shipped']=OVERRIDE_SHIPPED[(league,cand)]; vi['shipped_src']='manual_verdict_read'
    # evaluated arms for fails
    scored=[a for a in vi['scored'] if a in arms]
    eval_arms=[a for a in scored if dev_pass.get(a)]
    eval_src='scored∩dev_pass'
    if not eval_arms:
        if scored: eval_arms=scored; eval_src='scored_only'
        else: eval_arms=[a for a in arms if dev_pass.get(a)]; eval_src='dev_pass_fallback'
    # measurability
    meas=True; reason=''
    if (league,cand) in UNMEASURABLE: meas=False; reason=UNMEASURABLE[(league,cand)]
    elif group=='pass':
        if not vi['shipped']: meas=False; reason='shipped arm not identifiable'
        elif vi['shipped'] not in fwd: meas=False; reason=f"shipped arm {vi['shipped']} forward LLs not persisted"
    else:
        if not eval_arms: meas=False; reason='no evaluated arms'
        elif any(a not in fwd for a in eval_arms): meas=False; reason='forward LLs missing for evaluated arm(s): '+','.join(a for a in eval_arms if a not in fwd)
    results[key]={'candidate':cand,'league':league,'market':market,'group':group,'outcome':r['outcome'],
        'schema':rec['schema'],'gate_line':rec['gate_line'],'gate_line_src':rec['gate_line_src'],'seasons':seasons,
        'last_season':eff_last,'flat_single_window':flat,'n_dev_seasons':len(seasons),'dev_pass':dev_pass,'fwd':fwd,'margins':margins,
        'shipped':vi['shipped'],'shipped_src':vi['shipped_src'],'scored':vi['scored'],'eval_arms':eval_arms,'eval_src':eval_src,
        'measurable':meas,'unmeas_reason':reason,
        'arm_last_ll':({an: arms[an].get(eff_last) for an in arms}),
        'base_last':(rec['base'].get(eff_last) if market!='G' else rec['clim'].get(eff_last)),
        'naive_last':(rec['naive'].get(eff_last) if market!='G' else None),
        'fail_legs':r['fail_legs']}
json.dump(results, open(W+"/compute_final.json","w"), indent=1, default=str)

def frac(num,den): return f"{num}/{den} = {100*num/den:.2f}%" if den else "n/a"
cal=[v for v in results.values() if v['group']=='sealed_cal_fail']
pas=[v for v in results.values() if v['group']=='pass']
oth=[v for v in results.values() if v['group']=='sealed_other_fail']
cal_m=[v for v in cal if v['measurable']]; pas_m=[v for v in pas if v['measurable']]
print(f"COVERAGE cal: {len(cal_m)}/{len(cal)}  pass: {len(pas_m)}/{len(pas)}  other: {sum(1 for v in oth if v['measurable'])}/{len(oth)}")
print("unmeasurable:")
for v in results.values():
    if not v['measurable']: print(" ", v['league'], v['candidate'], v['group'], "-", v['unmeas_reason'])
# Measure A headline: all eval arms fail fwd
A_stop=[v for v in cal_m if all(v['fwd'][a]==False for a in v['eval_arms'])]
A_ref=[v for v in cal_m if v['fwd'].get(REF[v['market']])==False]
A_any=[v for v in cal_m if any(v['fwd'][a]==False for a in v['eval_arms'])]
print(f"\nMEASURE A (headline, all evaluated arms fail forward): {frac(len(A_stop),len(cal_m))}")
print(f"MEASURE A (ref-arm sensitivity): {frac(len(A_ref),len(cal_m))}")
print(f"MEASURE A (any-arm upper bound): {frac(len(A_any),len(cal_m))}")
B_kill=[v for v in pas_m if v['fwd'].get(v['shipped'])==False]
B_all=[v for v in pas_m if v['dev_pass'] and all(v['fwd'].get(a)==False for a in v['dev_pass'])]
print(f"\nMEASURE B (headline, shipped arm fails forward): {frac(len(B_kill),len(pas_m))}")
print(f"MEASURE B (all dev-pass arms fail sensitivity): {frac(len(B_all),len(pas_m))}")
print("\nA stopped candidates:", [v['candidate']+'@'+v['league'] for v in A_stop])
print("\nB killed candidates:", [(v['candidate']+'@'+v['league'], v['shipped']) for v in B_kill])
print("\nscored arms not dev_passing (fails):")
for v in results.values():
    if v['group']!='pass':
        extra=[a for a in v['scored'] if a in v['arms'] and not v['dev_pass'].get(a)]
        if extra: print(" ", v['league'], v['candidate'], "scored-not-devpass:", extra, "eval:", v['eval_arms'], v['eval_src'])
print("\nsingle-season dev candidates (fwd==pooled by construction):", sum(1 for v in results.values() if v['n_dev_seasons']==1), " flat single-window:", sum(1 for v in results.values() if v['flat_single_window']))
print("by market A:", Counter((v['market'], v in A_stop) for v in cal_m))
print("by market B:", Counter((v['market'], v in B_kill) for v in pas_m))
