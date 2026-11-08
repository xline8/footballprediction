import json, glob, os, re
from collections import Counter
ROOT=os.path.expanduser("~/workspace/footballprediction")
W=ROOT+"/league/improvement_scratch/P1/work"
ext=json.load(open(W+"/extract_v3.json"))
rows=[]
for f in sorted(glob.glob(ROOT+"/league/audit_scratch/class_batch*.jsonl")):
    for line in open(f): rows.append(json.loads(line))
cls={(r['league'],r['candidate']):r for r in rows}
MDIR={'G':'goals','S':'sot','C':'corners','K':'cards','T':'total_shots'}
def norm_arm(a):
    if a is None: return None
    s=str(a).strip().lower().replace('-','_').replace(' ','_')
    if s in ('gz','gatezero','gate_zero'): return 'gate_zero'
    return s
REF={'S':'gate_zero','C':'gate_zero','K':'gate_zero','G':'gate_zero','T':'a'}
ALIASES={'gate_zero':['gate zero','gate_zero','gz'],'rs':['rs'],'x7':['x7'],'x5':['x5'],'x4':['x4'],'x6':['x6'],'x8':['x8'],
         'x3':['x3'],'x2':['x2'],'a':['arm a','a'],'b':['arm b','b'],'c':['arm c','c'],'shrink':['shrink'],'plain':['plain'],'entrant':['entrant']}

def virgin_info(league, market, cand, dev_arms):
    base=f"{ROOT}/league/{league}/engine/{MDIR[market]}"
    info={'shipped':None,'shipped_src':None,'scored':[]}
    vp=base+"/results_virgin.json"
    if os.path.exists(vp):
        try: v=json.load(open(vp))
        except Exception: v=None
        if isinstance(v,dict):
            for k in ('shipped_arm','export_arm','ship_arm'):
                if v.get(k): info['shipped']=norm_arm(v[k]); info['shipped_src']='virgin_json:'+k; break
            sc=[]
            if isinstance(v.get('arm'),str): sc=[norm_arm(v['arm'])]
            if not sc and isinstance(v.get('read_arms'),list): sc=[norm_arm(a) for a in v['read_arms']]
            pr=v.get('protocol',{})
            if not sc and isinstance(pr,dict) and isinstance(pr.get('scored_arms'),list): sc=[norm_arm(a) for a in pr['scored_arms']]
            if not sc and isinstance(v.get('passing_arms'),list): sc=[norm_arm(a) for a in v['passing_arms']]
            if not sc and isinstance(v.get('results'),dict):
                sc=[norm_arm(k.split('|')[0]) for k in v['results'].keys() if k.endswith('|model')]
            if not sc and isinstance(v.get('metrics'),list):
                sc=list({norm_arm(x.get('arm')) for x in v['metrics'] if isinstance(x,dict) and x.get('kind')=='model'})
            if not sc and isinstance(v.get('arms'),dict): sc=[norm_arm(a) for a in v['arms'].keys()]
            if not sc and isinstance(v.get('metrics'),dict): sc=[norm_arm(a) for a in v['metrics'].keys() if not a.startswith('baseline')]
            if not sc:
                known={'gate_zero','gz','rs','x7','x5','x4','x6','x8','x3','x2','a','b','c','shrink','plain','entrant'}
                sc=[norm_arm(k) for k in v.keys() if k.lower() in known]
            if not sc and isinstance(v.get('model'),dict): sc=['gate_zero']
            if not sc and isinstance(v.get('metrics_at_5_5'),dict): sc=['gate_zero']
            info['scored']=[a for a in sc if a]
        elif isinstance(v,list):
            info['scored']=list({norm_arm(x.get('arm')) for x in v if isinstance(x,dict) and x.get('kind')=='model'})
    if not info['shipped']:
        texts=[]
        vdir=f"{ROOT}/league/{league}/reports"
        if os.path.isdir(vdir):
            for fn in sorted(os.listdir(vdir)):
                if fn.endswith('_VERDICT.md') and fn.startswith(f"{market}_"):
                    texts.append(open(os.path.join(vdir,fn),errors='ignore').read()); break
        texts.append(cls[(league,cand)].get('notes',''))
        for t in texts:
            tl=t.lower()
            hits=[]
            for arm in dev_arms:
                for al in ALIASES.get(arm,[arm]):
                    if re.search(r'\b'+re.escape(al)+r'\s+ships\b', tl) or re.search(r'ships:\s*\**'+re.escape(al)+r'\b', tl) or re.search(r'\*\*'+re.escape(al)+r'\s+ships', tl):
                        hits.append(arm); break
            if len(set(hits))==1:
                info['shipped']=hits[0]; info['shipped_src']='text_alias'; break
            elif len(set(hits))>1:
                info['shipped_src']='text_ambiguous:'+','.join(sorted(set(hits))); break
    return info

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
    last=seasons[-1] if seasons else ('pooled' if flat else None)
    eff_last = last
    if flat: eff_last='pooled'
    if market=='G':
        clim=rec['clim']; cp=pooled_of(clim)
        for an,ad in arms.items():
            ap=pooled_of(ad)
            if ap and cp and all(x is not None for x in ap[:3]) and all(x is not None for x in cp[:3]):
                dev_pass[an]=(ap[0]<cp[0] and ap[1]<cp[1] and ap[2]<cp[2])
            al=ad.get(eff_last) if eff_last else None
            cl=clim.get(eff_last) if eff_last else None
            if al and cl and all(x is not None for x in al[:3]) and all(x is not None for x in cl[:3]):
                fwd[an]=(al[0]<cl[0] and al[1]<cl[1] and al[2]<cl[2])
                margins[an]=[round(cl[i]-al[i],6) for i in range(3)]
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
    results[key]={'candidate':cand,'league':league,'market':market,'group':group,'outcome':r['outcome'],
                  'schema':rec['schema'],'gate_line':rec['gate_line'],'gate_line_src':rec['gate_line_src'],
                  'seasons':seasons,'last_season':eff_last,'flat':flat,'dev_pass':dev_pass,'fwd':fwd,'margins':margins,
                  'shipped':vi['shipped'],'shipped_src':vi['shipped_src'],'scored':vi['scored'],
                  'notes':rec['notes'],'arms':list(arms.keys()),
                  'arm_last_ll':({an: arms[an].get(eff_last) for an in arms} if market!='G' else {an: arms[an].get(eff_last) for an in arms}),
                  'base_last': (rec['base'].get(eff_last) if market!='G' else rec['clim'].get(eff_last)),
                  'naive_last': (rec['naive'].get(eff_last) if market!='G' else None)}
json.dump(results, open(W+"/compute_v1.json","w"), indent=1, default=str)
print("groups:", Counter(v['group'] for v in results.values()), "total", len(results))
print("--- no arm dev-passes (recomputed) ---")
for c,v in results.items():
    if not any(v['dev_pass'].values()): print(c, v['group'], v['dev_pass'], v['schema'], v['gate_line'])
print("--- reference arm fails pooled ---")
for c,v in results.items():
    if v['dev_pass'].get(REF[v['market']]) is False: print(c, v['group'], v['dev_pass'], 'fwd', v['fwd'], 'scored', v['scored'], 'shipped', v['shipped'])
print("--- passes shipped problems ---")
for c,v in results.items():
    if v['group']=='pass' and (not v['shipped'] or v['shipped'] not in v['arms']): print(c, v['shipped'], v['shipped_src'], v['arms'])
print("shipped src:", Counter(v['shipped_src'] for v in results.values() if v['group']=='pass'))
print("--- fails scored empty ---")
for c,v in results.items():
    if v['group']!='pass' and not v['scored']: print(c, v['group'], v['schema'])
print("--- fwd missing for dev_pass arms ---")
for c,v in results.items():
    for an,dp_ in v['dev_pass'].items():
        if dp_ and an not in v['fwd']: print(c, an, v['group'], v['schema'], 'flat', v['flat'], 'last', v['last_season'])
