import json, glob, os, re, sys
ROOT=os.path.expanduser("~/workspace/footballprediction")
rows=[]
for f in sorted(glob.glob(ROOT+"/league/audit_scratch/class_batch*.jsonl")):
    for line in open(f): rows.append(json.loads(line))
pop=[r for r in rows if r['outcome'].startswith('PASS') or (r['outcome']=='FAIL' and r['fail_point']=='sealed')]
MDIR={'G':'goals','S':'sot','C':'corners','K':'cards','T':'total_shots'}

def fmt_line(x):
    # 9.5 -> '9.5'; 25.5 -> '25.5'; 'OU2.5' handled separately
    if x is None: return None
    s=str(x)
    return s

def get_ll(d, line):
    # try keys ll_<line>, ll, logloss dict
    if d is None: return None
    for k in (f"ll_{line}", f"ll_{str(line).replace('.','_')}", "ll"):
        if k in d and isinstance(d[k],(int,float)): return d[k]
    return None

results={}
problems=[]
for r in pop:
    cand=r['candidate']; m=r['market']
    base=f"{ROOT}/league/{r['league']}/engine/{MDIR[m]}"
    dp=base+"/results_dev.json"
    d=json.load(open(dp))
    rec={'candidate':cand,'market':m,'schema':None,'primary_line':None,'seasons':None,'arms':{},'base':{},'naive':{},'clim':{},'pooled_check':None}
    try:
        if isinstance(d,list) or (isinstance(d,dict) and 'rows' in d):
            rws=d if isinstance(d,list) else d['rows']
            kinds=set(x.get('kind') for x in rws)
            if 'climatology' in kinds:
                rec['schema']='goals_rows'
                for x in rws:
                    arm=x['arm']; s=x['season']
                    tgt=rec['arms'] if x['kind']=='model' else rec['clim']
                    # clim stored per arm-name too (same values); store under arm key in clim dict-of-dict
                    if x['kind']=='model':
                        rec['arms'].setdefault(arm,{})[s]=(x.get('ll_1x2'),x.get('rps'),x.get('oull_2_5'),x.get('n'))
                    else:
                        rec['clim'][s]=(x.get('ll_1x2'),x.get('rps'),x.get('oull_2_5'),x.get('n'))
                rec['seasons']=sorted(set(s for a in rec['arms'].values() for s in a if s!='pooled'))
            else:
                rec['schema']='corners_list'
                # primary line unknown yet; collect all ll keys
                for x in rws:
                    arm=x['arm']; s=x['season']; kind=x['kind']
                    lls={k[3:]:v for k,v in x.items() if k.startswith('ll_')}
                    store = rec['arms'] if kind=='model' else (rec['base'] if kind=='league_base_rate' else rec['naive'])
                    key = arm if kind=='model' else '_base'
                    if kind!='model':
                        store.setdefault(s,{})[arm]=lls  # baselines repeated per arm; keep per-arm copy
                    else:
                        rec['arms'].setdefault(arm,{})[s]=lls
                rec['seasons']=sorted(set(s for a in rec['arms'].values() for s in a if s!='pooled'))
        elif isinstance(d,dict) and 'metrics' in d:
            rec['schema']='total_metrics'
            pr=d.get('protocol',{})
            line=fmt_line(pr.get('primary_line'))
            rec['primary_line']=line
            for name,md in d['metrics'].items():
                store = rec['base'] if name=='baseline_league' else (rec['naive'] if name=='baseline_naive' else None)
                for s,sd in md.items():
                    if not isinstance(sd,dict) or 'logloss' not in sd: continue
                    ll=sd['logloss'].get(line) if line else None
                    if store is not None: store[s]=ll
                    else: rec['arms'].setdefault(name,{})[s]=ll
            rec['seasons']=sorted(set(s for a in rec['arms'].values() for s in a if s!='pooled'))
        elif isinstance(d,dict) and 'arms' in d and isinstance(d.get('arms'),dict):
            arms=d['arms']
            # detect cards style: arms[x]['seasons'][s] has model/base/naive subkeys
            sample=next(iter(arms.values()))
            if isinstance(sample,dict) and 'seasons' in sample and isinstance(sample['seasons'],dict):
                ss=next(iter(sample['seasons'].values()))
                if isinstance(ss,dict) and ('model' in ss or 'base' in ss):
                    rec['schema']='cards_arms'
                    pr=d.get('protocol',{})
                    line=fmt_line(pr.get('primary_line'))
                    rec['primary_line']=line
                    for an,ad in arms.items():
                        for s,sd in ad.get('seasons',{}).items():
                            for who,store in (('model',None),('base','B'),('naive','N')):
                                if who in sd and line in sd[who]:
                                    ll=sd[who][line].get('ll')
                                    if store is None: rec['arms'].setdefault(an,{})[s]=ll
                                    elif store=='B': rec['base'][s]=ll
                                    else: rec['naive'][s]=ll
                        if 'pooled' in ad:
                            pd=ad['pooled']
                            # pooled may be {model/base/naive} or flat
                            if isinstance(pd,dict) and 'model' in pd and line in pd.get('model',{}):
                                rec['arms'].setdefault(an,{})['pooled']=pd['model'][line].get('ll')
                    rec['seasons']=sorted(set(s for a in rec['arms'].values() for s in a if s!='pooled'))
                else:
                    rec['schema']='sot_arms'
                    pr=d.get('protocol',{})
                    line=fmt_line(pr.get('primary_line'))
                    rec['primary_line']=line
                    key=f"ll_{line}"
                    for an,ad in arms.items():
                        if 'seasons' in ad:
                            for s,sd in ad['seasons'].items(): rec['arms'].setdefault(an,{})[s]=sd.get(key)
                        if 'pooled' in ad: rec['arms'].setdefault(an,{})['pooled']=ad['pooled'].get(key)
                    bl=d.get('baselines',{})
                    # alternate top-level baselines
                    if not bl:
                        if 'league_base_rate' in d: bl={'league_base_rate':d['league_base_rate']}
                        if 'naive_trailing_10' in d: bl['naive']=d['naive_trailing_10']
                        if 'climatology' in d: bl={'league_base_rate':d['climatology']}
                    for bn,bd in bl.items():
                        store = rec['base'] if 'base' in bn or 'climatology' in bn else rec['naive']
                        if isinstance(bd,dict):
                            if 'seasons' in bd:
                                for s,sd in bd['seasons'].items(): store[s]=sd.get(key)
                            if 'pooled' in bd and isinstance(bd['pooled'],dict): store['pooled']=bd['pooled'].get(key)
                            elif key in bd: store['pooled']=bd.get(key)
                    rec['seasons']=sorted(set(s for a in rec['arms'].values() for s in a if s!='pooled'))
            else:
                rec['schema']='arms_other:'+','.join(sorted(sample.keys())) if isinstance(sample,dict) else 'arms_other'
                problems.append((cand,'arms_other',str(list(arms.keys()))))
        elif isinstance(d,dict) and 'results' in d:
            rec['schema']='results_key'; problems.append((cand,'results_key',str(list(d.keys()))))
        else:
            rec['schema']='UNKNOWN:'+(','.join(sorted(d.keys())) if isinstance(d,dict) else type(d).__name__)
            problems.append((cand,'unknown_schema',rec['schema']))
    except Exception as e:
        rec['schema']='ERROR:'+str(e); problems.append((cand,'exception',str(e)))
    results[cand]=rec

from collections import Counter
print(Counter(v['schema'] for v in results.values()))
print("--- problems ---")
for p in problems: print(p)
json.dump(results, open(ROOT+"/league/improvement_scratch/P1/work/extract_v1.json","w"), indent=1)
# coverage quick look: who lacks last-season arm or baseline values
print("--- last-season completeness (counting markets) ---")
miss=[]
for cand,rec in results.items():
    if rec['market']=='G': continue
    if not rec['seasons']: miss.append((cand,'no seasons',rec['schema'])); continue
    last=rec['seasons'][-1]
    for an,ad in rec['arms'].items():
        if ad.get(last) is None: miss.append((cand,f'arm {an} no last',rec['schema']))
    if rec['base'].get(last) is None: miss.append((cand,'no base last',rec['schema']))
    if rec['naive'].get(last) is None: miss.append((cand,'no naive last',rec['schema']))
for x in miss: print(x)
print("miss count", len(miss))
