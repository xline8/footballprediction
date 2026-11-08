import json, glob, os, re
from collections import Counter
ROOT=os.path.expanduser("~/workspace/footballprediction")
rows=[]
for f in sorted(glob.glob(ROOT+"/league/audit_scratch/class_batch*.jsonl")):
    for line in open(f): rows.append(json.loads(line))
pop={r['candidate']:r for r in rows if r['outcome'].startswith('PASS') or (r['outcome']=='FAIL' and r['fail_point']=='sealed')}
MDIR={'G':'goals','S':'sot','C':'corners','K':'cards','T':'total_shots'}

def norm_arm(a):
    s=str(a).strip().lower().replace('-','_')
    if s in ('gz','gatezero','gate_zero'): return 'gate_zero'
    return s
def is_num(x): return isinstance(x,(int,float)) and not isinstance(x,bool)

# ---- gate line from prereg ----
def gate_line(league, market, devkeys_hint=None):
    pdir=f"{ROOT}/league/{league}/prereg"
    files=[]
    if os.path.isdir(pdir):
        for fn in sorted(os.listdir(pdir)):
            if fn.upper().startswith(f"PREREG_{market}_") or f"_{market}" in fn.upper() and fn.endswith('.md'):
                files.append(os.path.join(pdir,fn))
        if not files:
            files=[os.path.join(pdir,fn) for fn in sorted(os.listdir(pdir)) if fn.endswith('.md')]
    txt=""
    for fp in files:
        t=open(fp,errors='ignore').read()
        # prefer file whose name contains the market letter token
        txt+=t+"\n"
    pats=[r'[Pp]rimary line[:\s\*#]*?([0-9]+\.5)\b', r'gate at[:\s\*]*?([0-9]+\.5)\b', r'gated at[:\s\*]*?([0-9]+\.5)\b',
          r'LL@([0-9]+\.5)\b', r'primary_line["\']?\s*[:=]\s*"?([0-9]+\.5)']
    # search GATE LEGS section first
    m=re.search(r'GATE LEGS(.*?)(?:\n## |\Z)', txt, re.S)
    sections=[m.group(1)] if m else []
    sections.append(txt)
    for sec in sections:
        for p in pats:
            mm=re.search(p, sec)
            if mm: return mm.group(1), os.path.basename(files[0]) if files else None
    return None, None

out={}; problems=[]
for cand, r in pop.items():
    league, market = r['league'], r['market']
    base=f"{ROOT}/league/{league}/engine/{MDIR[market]}"
    dp=base+"/results_dev.json"
    d=json.load(open(dp))
    rec={'candidate':cand,'league':league,'market':market,'outcome':r['outcome'],'fail_legs':r['fail_legs'],
         'schema':None,'gate_line':None,'gate_line_src':None,'seasons':[],'arms':{},'base':{},'naive':{},'clim':{},
         'arm_n':{},'notes':[]}
    gl, glsrc = (None,None) if market=='G' else gate_line(league, market)
    rec['gate_line']=gl; rec['gate_line_src']=glsrc
    key=f"ll_{gl}" if gl else None
    try:
        # ---------- rows-style ----------
        rws=None
        if isinstance(d,list): rws=d
        elif isinstance(d,dict):
            for k in ('rows','tables','results'):
                if isinstance(d.get(k),list) and d[k] and isinstance(d[k][0],dict) and ('kind' in d[k][0] or 'arm' in d[k][0]):
                    rws=d[k]; break
        if rws is not None:
            kinds=set(x.get('kind') for x in rws if isinstance(x,dict))
            if 'climatology' in kinds:
                rec['schema']='goals_rows'
                for x in rws:
                    s=x.get('season') or x.get('block')
                    if x['kind']=='model':
                        rec['arms'].setdefault(norm_arm(x['arm']),{})[s]=(x.get('ll_1x2'),x.get('rps'),x.get('oull_2_5', x.get('ll_ou25')),x.get('n'))
                    elif x['kind']=='climatology':
                        rec['clim'][s]=(x.get('ll_1x2'),x.get('rps'),x.get('oull_2_5', x.get('ll_ou25')),x.get('n'))
            elif any('block' in x for x in rws if isinstance(x,dict)):
                rec['schema']='block_rows'
                for x in rws:
                    s=x.get('block'); kind=x.get('kind')
                    ll=None
                    if 'lines' in x and isinstance(x['lines'],dict): ll=x['lines'].get(gl)
                    if ll is None: ll=x.get('ll')
                    arm = norm_arm(d.get('arm','gate_zero')) if isinstance(d,dict) else 'gate_zero'
                    if kind=='model': rec['arms'].setdefault(arm,{})[s]=ll
                    elif kind=='league_base_rate': rec['base'][s]=ll
                    elif kind in ('naive_trailing_10','naive'): rec['naive'][s]=ll
                    if kind=='model': rec['arm_n'][s]=x.get('n')
            elif any('line' in x for x in rws if isinstance(x,dict)):
                rec['schema']='line_rows'
                for x in rws:
                    if gl is not None and float(x.get('line',-1))!=float(gl): continue
                    s=x.get('season'); kind=x.get('kind')
                    if kind=='model': rec['arms'].setdefault(norm_arm(x['arm']),{})[s]=x.get('ll')
                    elif kind in ('league_base_rate','base_rate','climatology'): rec['base'][s]=x.get('ll')
                    elif kind in ('naive_trailing_10','naive','naive10'): rec['naive'][s]=x.get('ll')
            else:
                rec['schema']='season_rows'
                for x in rws:
                    s=x.get('season'); kind=x.get('kind')
                    ll=x.get(key) if key else None
                    if kind=='model':
                        rec['arms'].setdefault(norm_arm(x['arm']),{})[s]=ll; rec['arm_n'][s]=x.get('n')
                    elif kind=='league_base_rate': rec['base'][s]=ll
                    elif kind in ('naive_trailing_10','naive'): rec['naive'][s]=ll
            rec['seasons']=[s for s in dict.fromkeys(x.get('season') or x.get('block') for x in rws if isinstance(x,dict)) if s and s!='pooled']
        # ---------- metrics list (AUW style) ----------
        elif isinstance(d,dict) and isinstance(d.get('metrics'),list):
            rec['schema']='metrics_list'
            for x in d['metrics']:
                s=x.get('season'); a=x.get('arm'); ll=x.get('primary_ll', x.get('ll'))
                if a in ('baseline_league','league_base_rate','base_rate'): rec['base'][s]=ll
                elif a in ('baseline_naive','naive','naive_trailing_10'): rec['naive'][s]=ll
                else: rec['arms'].setdefault(norm_arm(a),{})[s]=ll
            rec['seasons']=[s for s in dict.fromkeys(x.get('season') for x in d['metrics']) if s and s!='pooled']
        # ---------- total_metrics dict ----------
        elif isinstance(d,dict) and isinstance(d.get('metrics'),dict):
            rec['schema']='total_metrics'
            for name,md in d['metrics'].items():
                if not isinstance(md,dict): continue
                store = rec['base'] if name=='baseline_league' else (rec['naive'] if name=='baseline_naive' else None)
                for s,sd in md.items():
                    if not isinstance(sd,dict): continue
                    ll=None
                    if isinstance(sd.get('logloss'),dict): ll=sd['logloss'].get(gl)
                    elif key and key in sd: ll=sd[key]
                    elif 'll' in sd: ll=sd['ll']
                    if store is not None: store[s]=ll
                    else: rec['arms'].setdefault(norm_arm(name),{})[s]=ll
            rec['seasons']=[s for a in rec['arms'].values() for s in a if s!='pooled']
            rec['seasons']=list(dict.fromkeys(rec['seasons']))
        # ---------- cards blocks_ll ----------
        elif isinstance(d,dict) and any(k.startswith('blocks_ll_at_') for k in d):
            rec['schema']='cards_blocks'
            bk=next(k for k in d if k.startswith('blocks_ll_at_'))
            if gl is None: rec['gate_line']=bk.replace('blocks_ll_at_','').replace('_','.')
            for s,sd in d[bk].items():
                rec['arms'].setdefault('gate_zero',{})[s]=sd.get('model'); rec['base'][s]=sd.get('base'); rec['naive'][s]=sd.get('naive')
            rec['seasons']=list(d[bk].keys())
        # ---------- flat model/base_rate/naive10 (CH-Challenge) ----------
        elif isinstance(d,dict) and 'model' in d and 'base_rate' in d:
            rec['schema']='flat_single'
            rec['arms']['gate_zero']['pooled']=d['model'].get(key)
            rec['base']['pooled']=d['base_rate'].get(key)
            rec['naive']['pooled']=d['naive10'].get(key)
            if gl is None and d.get('primary_line') is not None: rec['gate_line']=str(d['primary_line']); key=f"ll_{rec['gate_line']}"
            rec['notes'].append('pooled_only_flat')
        # ---------- arms dict family ----------
        elif isinstance(d,dict) and isinstance(d.get('arms'),dict):
            arms=d['arms']
            sample=next(iter(arms.values()))
            def season_map(ad):
                # returns {season: metrics-dict} from various nestings
                if not isinstance(ad,dict): return {}
                if isinstance(ad.get('seasons'),dict): return ad['seasons']
                if isinstance(ad.get('per_season'),dict): return ad['per_season']
                # season-keyed directly
                skip={'n','pooled','dev_pass','gate_dev_pass','r','fitted_params','blocks','primary_ll'}
                m={k:v for k,v in ad.items() if k not in skip and isinstance(v,dict)}
                return m
            if isinstance(sample,dict) and season_map(sample) and isinstance(next(iter(season_map(sample).values()),{}),dict) and any(k in next(iter(season_map(sample).values()),{}) for k in ('model','base','naive')):
                rec['schema']='cards_arms'
                for an,ad in arms.items():
                    for s,sd in season_map(ad).items():
                        if not isinstance(sd,dict): continue
                        for who in ('model','base','naive'):
                            if who in sd and isinstance(sd[who],dict):
                                cell=sd[who].get(gl) if gl else None
                                ll=cell.get('ll') if isinstance(cell,dict) else None
                                if who=='model': rec['arms'].setdefault(norm_arm(an),{})[s]=ll
                                elif who=='base': rec['base'][s]=ll
                                else: rec['naive'][s]=ll
                    pd=ad.get('pooled')
                    if isinstance(pd,dict) and isinstance(pd.get('model'),dict) and gl and isinstance(pd['model'].get(gl),dict):
                        rec['arms'][norm_arm(an)]['pooled']=pd['model'][gl].get('ll')
                # pooled baselines from any arm's pooled
                for an,ad in arms.items():
                    pd=ad.get('pooled')
                    if isinstance(pd,dict):
                        for who,store in (('base',rec['base']),('naive',rec['naive'])):
                            if isinstance(pd.get(who),dict) and gl and isinstance(pd[who].get(gl),dict) and 'pooled' not in store:
                                store['pooled']=pd[who][gl].get('ll')
            elif isinstance(sample,dict) and ('ll_' in json.dumps(sample)[:200] or 'primary_ll' in sample or 'll' in sample) and not season_map(sample):
                rec['schema']='flat_arms'
                for an,ad in arms.items():
                    if isinstance(ad,dict): rec['arms'].setdefault(norm_arm(an),{})['pooled']=ad.get(key)
                bl=d.get('baselines',{})
                for bn,bd in bl.items():
                    if not isinstance(bd,dict): continue
                    store = rec['base'] if ('base' in bn or 'climatology' in bn) else rec['naive']
                    store['pooled']=bd.get(key)
                rec['notes'].append('pooled_only_flat')
            else:
                # SOT-style arms {seasons,pooled} OR season-keyed arms OR goals per_season arms
                rec['schema']='arms_seasons'
                for an,ad in arms.items():
                    sm=season_map(ad)
                    for s,sd in sm.items():
                        if not isinstance(sd,dict): continue
                        if market=='G':
                            rec['arms'].setdefault(norm_arm(an),{})[s]=(sd.get('ll_1x2'),sd.get('rps'),sd.get('oull_2_5',sd.get('ll_ou25')),sd.get('n'))
                        else:
                            ll=sd.get(key) if key else None
                            if ll is None: ll=sd.get('ll', sd.get('primary_ll'))
                            rec['arms'].setdefault(norm_arm(an),{})[s]=ll
                    pd=ad.get('pooled')
                    if isinstance(pd,dict):
                        if market=='G': rec['arms'].setdefault(norm_arm(an),{})['pooled']=(pd.get('ll_1x2'),pd.get('rps'),pd.get('oull_2_5',pd.get('ll_ou25')),pd.get('n'))
                        else:
                            ll=pd.get(key) if key else None
                            if ll is None: ll=pd.get('ll', pd.get('primary_ll'))
                            rec['arms'].setdefault(norm_arm(an),{})['pooled']=ll
                    # blocks-style SOT (BO): arms[x]['blocks']
                    if isinstance(ad.get('blocks'),dict):
                        rec['notes'].append('block_folds_no_baseline_per_block')
                        for s,sd in ad['blocks'].items():
                            rec['arms'].setdefault(norm_arm(an),{})[s]=sd.get(key) if key else None
                bl=d.get('baselines',{})
                if not bl:
                    for alt in ('league_base_rate','naive_trailing_10','climatology','naive'):
                        if alt in d and isinstance(d[alt],dict): bl[alt]=d[alt]
                for bn,bd in bl.items():
                    if not isinstance(bd,dict): continue
                    store = rec['base'] if ('base' in bn or 'climatology' in bn) else rec['naive']
                    if market=='G': store=rec['clim']
                    sm=season_map(bd)
                    for s,sd in sm.items():
                        if not isinstance(sd,dict): continue
                        if market=='G': rec['clim'][s]=(sd.get('ll_1x2'),sd.get('rps'),sd.get('oull_2_5',sd.get('ll_ou25')),sd.get('n'))
                        else: store[s]=sd.get(key) if key else sd.get('ll')
                    pd=bd.get('pooled')
                    if isinstance(pd,dict):
                        if market=='G': rec['clim']['pooled']=(pd.get('ll_1x2'),pd.get('rps'),pd.get('oull_2_5',pd.get('ll_ou25')),pd.get('n'))
                        else: store['pooled']=pd.get(key) if key else pd.get('ll')
                    elif key and is_num(bd.get(key)):
                        store['pooled']=bd.get(key)
                # goals top-level climatology/naive (IL style)
                if market=='G' and isinstance(d.get('climatology'),dict):
                    cd=d['climatology']; sm=season_map(cd)
                    for s,sd in sm.items():
                        if isinstance(sd,dict): rec['clim'][s]=(sd.get('ll_1x2'),sd.get('rps'),sd.get('oull_2_5',sd.get('ll_ou25')),sd.get('n'))
                    if isinstance(cd.get('pooled'),dict):
                        pd=cd['pooled']; rec['clim']['pooled']=(pd.get('ll_1x2'),pd.get('rps'),pd.get('oull_2_5',pd.get('ll_ou25')),pd.get('n'))
            rec['seasons']=[s for a in rec['arms'].values() for s in a if s!='pooled']
            rec['seasons']=list(dict.fromkeys(rec['seasons']))
        else:
            rec['schema']='UNKNOWN'; problems.append((cand,'unknown',str(list(d.keys()))[:200] if isinstance(d,dict) else type(d).__name__))
    except Exception as e:
        import traceback; rec['schema']='ERROR:'+str(e); problems.append((cand,'exc',str(e)))
    out[cand]=rec

print(Counter(v['schema'] for v in out.values()))
print("--- problems ---")
for p in problems: print(p)
print("--- completeness: counting markets, arms/base/naive at last season + pooled ---")
bad=[]
for cand,rec in out.items():
    if rec['market']=='G':
        if not rec['seasons'] or not rec['clim']: bad.append((cand,'goals incomplete',rec['schema']))
        continue
    if 'pooled_only_flat' in rec['notes']: continue
    last=rec['seasons'][-1] if rec['seasons'] else None
    if last is None: bad.append((cand,'no seasons',rec['schema'])); continue
    for an,ad in rec['arms'].items():
        if ad.get(last) is None: bad.append((cand,f'arm {an} missing last',rec['schema']))
        if ad.get('pooled') is None: bad.append((cand,f'arm {an} missing pooled',rec['schema']))
    if rec['base'].get(last) is None: bad.append((cand,'base missing last',rec['schema']))
    if rec['naive'].get(last) is None: bad.append((cand,'naive missing last',rec['schema']))
    if rec['base'].get('pooled') is None: bad.append((cand,'base missing pooled',rec['schema']))
    if rec['naive'].get('pooled') is None: bad.append((cand,'naive missing pooled',rec['schema']))
for b in bad: print(b)
print("bad count", len(bad))
json.dump(out, open(ROOT+"/league/improvement_scratch/P1/work/extract_v2.json","w"), indent=1, default=str)
