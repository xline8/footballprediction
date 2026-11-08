import json, glob, os, re
from collections import Counter
ROOT=os.path.expanduser("~/workspace/footballprediction")
rows=[]
for f in sorted(glob.glob(ROOT+"/league/audit_scratch/class_batch*.jsonl")):
    for line in open(f): rows.append(json.loads(line))
pop={(r['league'],r['candidate']):r for r in rows if r['outcome'].startswith('PASS') or (r['outcome']=='FAIL' and r['fail_point']=='sealed')}
MDIR={'G':'goals','S':'sot','C':'corners','K':'cards','T':'total_shots'}
def ou_of(dd):
    if not isinstance(dd,dict): return None
    for k in ('oull_2_5','ll_ou25','ll_ou2_5','ou25_ll','ll_ou_2_5'):
        if is_num(dd.get(k)): return dd[k]
    return None
def norm_arm(a):
    s=str(a).strip().lower().replace('-','_')
    if s in ('gz','gatezero','gate_zero'): return 'gate_zero'
    return s
def is_num(x): return isinstance(x,(int,float)) and not isinstance(x,bool)

def ll_keys_of(d):
    if isinstance(d,dict): return [k[3:] for k in d if k.startswith('ll_') and is_num(d[k])]
    return []

def resolve_gate_line(league, market, cand, dev):
    """returns (line_str, source)"""
    cands=[]
    # protocol / root primary_line in dev JSON
    if isinstance(dev,dict):
        pr=dev.get('protocol')
        if isinstance(pr,dict) and is_num(pr.get('primary_line')): cands.append((str(pr['primary_line']),'dev_protocol'))
        if is_num(dev.get('primary_line')): cands.append((str(dev['primary_line']),'dev_root'))
    # prereg file for this candidate
    pdir=f"{ROOT}/league/{league}/prereg"
    pfiles=[]
    if os.path.isdir(pdir):
        suf=cand.split('-',1)[1] if '-' in cand else ''
        for fn in sorted(os.listdir(pdir)):
            if fn.endswith('.md') and (fn.upper().startswith(f"PREREG_{market}_")): pfiles.append(os.path.join(pdir,fn))
    pats=[r'[Pp]rimary line[:\s\*#]*?([0-9]+\.5)\b', r'[Pp]rimary line is[:\s\*]*?([0-9]+\.5)\b',
          r'[Ll]ine is[:\s\*]*?([0-9]+\.5)\b', r'[Pp]rimary line OU[:\s]*([0-9]+\.5)\b', r'[Pp]rimary line[^\d\n]{0,12}([0-9]+\.5)\b', r'gate at[:\s\*]*?([0-9]+\.5)\b', r'gated at[:\s\*]*?([0-9]+\.5)\b',
          r'LL@([0-9]+\.5)\b', r'primary_line["\']?\s*[:=]\s*"?([0-9]+\.5)']
    for fp in pfiles:
        t=open(fp,errors='ignore').read()
        m=re.search(r'GATE LEGS(.*?)(?:\n## |\Z)', t, re.S)
        for sec in ([m.group(1)] if m else [])+[t]:
            for p in pats:
                mm=re.search(p, sec)
                if mm: cands.append((mm.group(1),'prereg:'+os.path.basename(fp))); break
            else: continue
            break
        if cands and cands[-1][1].startswith('prereg'): break
    # verdict
    vdir=f"{ROOT}/league/{league}/reports"
    if os.path.isdir(vdir):
        for fn in sorted(os.listdir(vdir)):
            if fn.endswith('_VERDICT.md') and fn.startswith(f"{market}_"):
                t=open(os.path.join(vdir,fn),errors='ignore').read()
                mm=re.findall(r'LL@([0-9]+\.5)\b', t)
                if mm: cands.append((Counter(mm).most_common(1)[0][0],'verdict:'+fn))
                break
    # validate against pooled ll keys present in dev JSON
    keys=set()
    import re as _re
    def collect(x, in_tuning=False):
        if isinstance(x,dict):
            for k,v in x.items():
                if k=='tuning': continue
                if _re.match(r'^ll_\d+\.5$', k) and is_num(v): keys.add(k[3:])
                if k=='logloss' and isinstance(v,dict):
                    for lk in v: 
                        if _re.match(r'^\d+\.5$', str(lk)): keys.add(str(lk))
                collect(v, in_tuning)
        elif isinstance(x,list):
            for v in x: collect(v, in_tuning)
    collect(dev)
    for val,src in cands:
        if val in keys: return val,src
    if len(keys)==1: return next(iter(keys)),'unique_json_key'
    if cands: return cands[0][0], cands[0][1]+' (unvalidated)'
    return None,None

out={}; problems=[]
for (lg_key, cand), r in pop.items():
    league, market = r['league'], r['market']
    base=f"{ROOT}/league/{league}/engine/{MDIR[market]}"
    d=json.load(open(base+"/results_dev.json"))
    rec={'candidate':cand,'league':league,'market':market,'outcome':r['outcome'],'fail_legs':r['fail_legs'],
         'schema':None,'gate_line':None,'gate_line_src':None,'seasons':[],'arms':{},'base':{},'naive':{},'clim':{},
         'notes':[]}
    gl,glsrc=(None,None) if market=='G' else resolve_gate_line(league,market,cand,d)
    rec['gate_line']=gl; rec['gate_line_src']=glsrc
    key=f"ll_{gl}" if gl else None
    def pick_ll(sd):
        if not isinstance(sd,dict): return None
        if key and is_num(sd.get(key)): return sd[key]
        if key:
            for k,v in sd.items():
                if k.endswith(key) and is_num(v): return v
        if is_num(sd.get('ll')): return sd['ll']
        if is_num(sd.get('primary_ll')): return sd['primary_ll']
        return None
    try:
        rws=None
        if isinstance(d,list): rws=d
        elif isinstance(d,dict):
            for k in ('rows','tables','results','metrics'):
                if isinstance(d.get(k),list) and d[k] and isinstance(d[k][0],dict) and ('kind' in d[k][0] or 'arm' in d[k][0]):
                    rws=d[k]; break
        if rws is not None:
            kinds=set(x.get('kind') for x in rws if isinstance(x,dict))
            has_arm_season=all(('season' in x or 'block' in x) for x in rws if isinstance(x,dict))
            if 'climatology' in kinds:
                rec['schema']='goals_rows'
                for x in rws:
                    s=x.get('season') or x.get('block')
                    if x['kind']=='model': rec['arms'].setdefault(norm_arm(x['arm']),{})[s]=(x.get('ll_1x2'),x.get('rps'),ou_of(x),x.get('n'))
                    elif x['kind']=='climatology': rec['clim'][s]=(x.get('ll_1x2'),x.get('rps'),ou_of(x),x.get('n'))
            elif any('block' in x for x in rws if isinstance(x,dict)):
                rec['schema']='block_rows'
                darm = norm_arm(d.get('arm','gate_zero')) if isinstance(d,dict) else 'gate_zero'
                for x in rws:
                    s=x.get('block'); kind=x.get('kind')
                    ll=None
                    if isinstance(x.get('lines'),dict): ll=x['lines'].get(gl)
                    if ll is None: ll=pick_ll(x)
                    if kind=='model': rec['arms'].setdefault(darm,{})[s]=ll
                    elif kind=='league_base_rate': rec['base'][s]=ll
                    elif kind in ('naive_trailing_10','naive'): rec['naive'][s]=ll
            elif not has_arm_season:
                rec['schema']='rows_no_arm'; problems.append((cand,'rows_no_arm',str(rws[0])[:200]))
            elif any('line' in x for x in rws if isinstance(x,dict)):
                rec['schema']='line_rows'
                for x in rws:
                    if gl is not None and float(x.get('line',-1))!=float(gl): continue
                    s=x.get('season'); kind=x.get('kind')
                    if kind=='model': rec['arms'].setdefault(norm_arm(x['arm']),{})[s]=x.get('ll')
                    elif kind in ('league_base_rate','base_rate','base','climatology'): rec['base'][s]=x.get('ll')
                    elif kind in ('naive_trailing_10','naive','naive10'): rec['naive'][s]=x.get('ll')
            else:
                rec['schema']='season_rows'
                for x in rws:
                    s=x.get('season'); kind=x.get('kind')
                    ll=pick_ll(x)
                    a=norm_arm(x['arm']) if x.get('arm') else 'gate_zero'
                    if kind=='model': rec['arms'].setdefault(a,{})[s]=ll
                    elif kind in ('league_base_rate','base_rate','base'): rec['base'][s]=ll
                    elif kind in ('naive_trailing_10','naive','naive10'): rec['naive'][s]=ll
                    elif kind is None and x.get('arm') in ('baseline_league','baseline'): rec['base'][s]=ll
                    elif kind is None and x.get('arm') in ('baseline_naive',): rec['naive'][s]=ll
                    elif kind is None: rec['arms'].setdefault(a,{})[s]=ll
            rec['seasons']=[s for s in dict.fromkeys((x.get('season') or x.get('block')) for x in rws if isinstance(x,dict)) if s and s!='pooled']
            if not rec['seasons'] and rec['schema'] in ('season_rows','block_rows','line_rows'):
                rec['notes'].append('pooled_only_flat')
        elif isinstance(d,dict) and isinstance(d.get('metrics'),dict):
            rec['schema']='total_metrics'
            pr=d.get('protocol',{}) if isinstance(d.get('protocol'),dict) else {}
            gate_pool=pr.get('gate_pool') if isinstance(pr.get('gate_pool'),list) else None
            for name,md in d['metrics'].items():
                if not isinstance(md,dict): continue
                store = rec['base'] if name=='baseline_league' else (rec['naive'] if name=='baseline_naive' else None)
                for s,sd in md.items():
                    if s=='gate_pool': s='pooled'
                    if not isinstance(sd,dict): continue
                    ll=None
                    if isinstance(sd.get('logloss'),dict): ll=sd['logloss'].get(gl)
                    if ll is None: ll=pick_ll(sd)
                    if store is not None: store[s]=ll
                    else: rec['arms'].setdefault(norm_arm(name),{})[s]=ll
            if gate_pool: rec['seasons']=list(gate_pool)
            else:
                rec['seasons']=[s for a in rec['arms'].values() for s in a if s not in ('pooled',)]
                rec['seasons']=list(dict.fromkeys(rec['seasons']))
                tun=pr.get('tuning_season')
                if tun and tun in rec['seasons'] and len(rec['seasons'])>1:
                    # tuning season is scored only if in gate_pool; without gate_pool keep but flag
                    rec['notes'].append(f'tuning_season_present:{tun}')
        elif isinstance(d,dict) and any(k.startswith('blocks_ll_at_') for k in d):
            rec['schema']='cards_blocks'
            bk=next(k for k in d if k.startswith('blocks_ll_at_'))
            if gl is None: rec['gate_line']=bk.replace('blocks_ll_at_','').replace('_','.'); gl=rec['gate_line']
            for s,sd in d[bk].items():
                rec['arms'].setdefault('gate_zero',{})[s]=sd.get('model'); rec['base'][s]=sd.get('base'); rec['naive'][s]=sd.get('naive')
            dg=d.get('dev_gate',{})
            if is_num(dg.get('model_ll')):
                rec['arms']['gate_zero']['pooled']=dg['model_ll']; rec['base']['pooled']=dg.get('base_ll'); rec['naive']['pooled']=dg.get('naive_ll')
            rec['seasons']=list(d[bk].keys())
        elif isinstance(d,dict) and 'model' in d and 'base_rate' in d and isinstance(d.get('model'),dict):
            rec['schema']='flat_single'
            rec['arms'].setdefault('gate_zero',{})['pooled']=pick_ll(d['model'])
            rec['base']['pooled']=pick_ll(d['base_rate'])
            rec['naive']['pooled']=pick_ll(d['naive10'])
            rec['notes'].append('pooled_only_flat')
        elif isinstance(d,dict) and isinstance(d.get('arms'),dict):
            arms=d['arms']
            def season_map(ad):
                if not isinstance(ad,dict): return {}
                if isinstance(ad.get('seasons'),dict): return ad['seasons']
                if isinstance(ad.get('per_season'),dict): return ad['per_season']
                skip={'n','pooled','dev_pass','gate_dev_pass','r','fitted_params','primary_ll','blocks','blocks_ll_rps_ou'}
                return {k:v for k,v in ad.items() if k not in skip and isinstance(v,dict)}
            sample=next(iter(arms.values()))
            sm0=season_map(sample)
            first_cell=next(iter(sm0.values()),{}) if sm0 else {}
            if isinstance(first_cell,dict) and any(k in first_cell for k in ('model','base','naive')):
                rec['schema']='cards_arms'
                for an,ad in arms.items():
                    for s,sd in season_map(ad).items():
                        if not isinstance(sd,dict): continue
                        for who in ('model','base','naive'):
                            cell=sd.get(who)
                            if isinstance(cell,dict):
                                c2=cell.get(gl) if gl else None
                                ll=c2.get('ll') if isinstance(c2,dict) else pick_ll(cell)
                                if who=='model' and isinstance(c2,dict) and is_num(c2.get('n')): rec.setdefault('season_n',{})[s]=c2['n']
                                if who=='model': rec['arms'].setdefault(norm_arm(an),{})[s]=ll
                                elif who=='base': rec['base'][s]=ll
                                else: rec['naive'][s]=ll
                    pd=ad.get('pooled')
                    if isinstance(pd,dict) and isinstance(pd.get('model'),dict):
                        c2=pd['model'].get(gl) if gl else None
                        if isinstance(c2,dict): rec['arms'][norm_arm(an)]['pooled']=c2.get('ll')
                for an,ad in arms.items():
                    pd=ad.get('pooled')
                    if isinstance(pd,dict):
                        for who,store in (('base',rec['base']),('naive',rec['naive'])):
                            c2=pd.get(who,{}).get(gl) if gl and isinstance(pd.get(who),dict) else None
                            if isinstance(c2,dict) and 'pooled' not in store: store['pooled']=c2.get('ll')
            elif sm0 or (market=='G' and any(isinstance(ad,dict) and 'blocks_ll_rps_ou' in ad for ad in arms.values())):
                rec['schema']='arms_seasons'
                for an,ad in arms.items():
                    if market=='G' and isinstance(ad.get('blocks_ll_rps_ou'),dict):
                        for s,tri in ad['blocks_ll_rps_ou'].items():
                            if isinstance(tri,(list,tuple)) and len(tri)>=3:
                                rec['arms'].setdefault(norm_arm(an),{})[s]=(tri[0],tri[1],tri[2],None)
                    for s,sd in season_map(ad).items():
                        if not isinstance(sd,dict): continue
                        if market=='G': rec['arms'].setdefault(norm_arm(an),{})[s]=(sd.get('ll_1x2'),sd.get('rps'),sd.get('oull_2_5') or sd.get('ll_ou25') or sd.get('ll_ou2_5') or sd.get('ou25_ll'),sd.get('n'))
                        else: rec['arms'].setdefault(norm_arm(an),{})[s]=pick_ll(sd)
                    pd=ad.get('pooled')
                    if isinstance(pd,dict):
                        if market=='G': rec['arms'].setdefault(norm_arm(an),{})['pooled']=(pd.get('ll_1x2'),pd.get('rps'),pd.get('oull_2_5') or pd.get('ll_ou25') or pd.get('ll_ou2_5') or pd.get('ou25_ll'),pd.get('n'))
                        else: rec['arms'].setdefault(norm_arm(an),{})['pooled']=pick_ll(pd)
                    elif market!='G' and pick_ll(ad) is not None:
                        rec['arms'].setdefault(norm_arm(an),{})['pooled']=pick_ll(ad)
                    if isinstance(ad.get('blocks'),dict):
                        rec['notes'].append('block_folds')
                        for s,sd in ad['blocks'].items(): rec['arms'].setdefault(norm_arm(an),{})[s]=pick_ll(sd)
                bl={}
                if isinstance(d.get('baselines'),dict): bl=d['baselines']
                else:
                    for alt in ('league_base_rate','naive_trailing_10','climatology','naive'):
                        if isinstance(d.get(alt),dict): bl[alt]=d[alt]
                for bn,bd in bl.items():
                    if not isinstance(bd,dict): continue
                    store = rec['clim'] if (market=='G' and 'climatology' in bn) else (rec['base'] if ('base' in bn or 'climatology' in bn) else rec['naive'])
                    for s,sd in season_map(bd).items():
                        if not isinstance(sd,dict): continue
                        if market=='G': rec['clim'][s]=(sd.get('ll_1x2'),sd.get('rps'),sd.get('oull_2_5') or sd.get('ll_ou25') or sd.get('ll_ou2_5') or sd.get('ou25_ll'),sd.get('n'))
                        else: store[s]=pick_ll(sd)
                    pd=bd.get('pooled')
                    if isinstance(pd,dict):
                        if market=='G': rec['clim']['pooled']=(pd.get('ll_1x2'),pd.get('rps'),pd.get('oull_2_5') or pd.get('ll_ou25') or pd.get('ll_ou2_5') or pd.get('ou25_ll'),pd.get('n'))
                        else: store['pooled']=pick_ll(pd)
                    elif pick_ll(bd) is not None:
                        store['pooled']=pick_ll(bd)
                if market=='G' and isinstance(d.get('climatology'),dict) and isinstance(d['climatology'].get('blocks_ll_rps_ou'),dict):
                    for s,tri in d['climatology']['blocks_ll_rps_ou'].items():
                        if isinstance(tri,(list,tuple)) and len(tri)>=3:
                            rec['clim'][s]=(tri[0],tri[1],tri[2],None)
                if market=='G' and isinstance(d.get('climatology'),dict):
                    cd=d['climatology']
                    for s,sd in season_map(cd).items():
                        if isinstance(sd,dict): rec['clim'][s]=(sd.get('ll_1x2'),sd.get('rps'),sd.get('oull_2_5') or sd.get('ll_ou25') or sd.get('ll_ou2_5') or sd.get('ou25_ll'),sd.get('n'))
                    if isinstance(cd.get('pooled'),dict):
                        pd=cd['pooled']; rec['clim']['pooled']=(pd.get('ll_1x2'),pd.get('rps'),pd.get('oull_2_5') or pd.get('ll_ou25') or pd.get('ll_ou2_5') or pd.get('ou25_ll'),pd.get('n'))
            else:
                rec['schema']='flat_arms'
                for an,ad in arms.items():
                    if isinstance(ad,dict):
                        rec['arms'].setdefault(norm_arm(an),{})['pooled']=pick_ll(ad['pooled']) if isinstance(ad.get('pooled'),dict) else pick_ll(ad)
                bl=d.get('baselines',{}) if isinstance(d.get('baselines'),dict) else {}
                for bn,bd in bl.items():
                    if not isinstance(bd,dict): continue
                    store = rec['base'] if ('base' in bn or 'climatology' in bn) else rec['naive']
                    store['pooled']=pick_ll(bd['pooled']) if isinstance(bd.get('pooled'),dict) else pick_ll(bd)
                rec['notes'].append('pooled_only_flat')
            if rec['schema'] in ('cards_arms','arms_seasons'):
                rec['seasons']=[s for a in rec['arms'].values() for s in a if s!='pooled']
                rec['seasons']=list(dict.fromkeys(rec['seasons']))
        else:
            rec['schema']='UNKNOWN'; problems.append((cand,'unknown',str(list(d.keys()))[:200] if isinstance(d,dict) else type(d).__name__))
    except Exception as e:
        rec['schema']='ERROR:'+str(e); problems.append((cand,'exc',str(e)))
    out[league+'|'+cand]=rec
print(Counter(v['schema'] for v in out.values()))
for p in problems: print(p)
json.dump(out, open(ROOT+"/league/improvement_scratch/P1/work/extract_v3.json","w"), indent=1, default=str)
print("--- completeness counting (excl flat) ---")
bad=[]
for cand,rec in out.items():
    if rec['market']=='G':
        if not rec['seasons'] or not rec['clim']: bad.append((cand,'goals incomplete',rec['schema']))
        else:
            last=rec['seasons'][-1]
            if rec['clim'].get(last) is None: bad.append((cand,'goals clim missing last',rec['schema']))
        continue
    if 'pooled_only_flat' in rec['notes']: continue
    if not rec['seasons']: bad.append((cand,'no seasons',rec['schema'])); continue
    last=rec['seasons'][-1]
    for an,ad in rec['arms'].items():
        if ad.get(last) is None: bad.append((cand,f'arm {an} missing last',rec['schema']))
        if ad.get('pooled') is None: bad.append((cand,f'arm {an} missing pooled',rec['schema']))
    for nm,store in (('base',rec['base']),('naive',rec['naive'])):
        if store.get(last) is None: bad.append((cand,f'{nm} missing last',rec['schema']))
        if store.get('pooled') is None: bad.append((cand,f'{nm} missing pooled',rec['schema']))
for b in bad: print(b)
print("bad:", len(bad))
print("--- flat candidates ---")
for cand,rec in out.items():
    if 'pooled_only_flat' in rec['notes']: print(cand, rec['schema'], rec['gate_line'], rec['gate_line_src'])
print("--- gate line sources ---")
print(Counter((v['market'], (v['gate_line_src'] or 'NONE').split(':')[0]) for v in out.values() if v['market']!='G'))
print("--- gate line None ---")
for cand,rec in out.items():
    if rec['market']!='G' and not rec['gate_line']: print(cand)
