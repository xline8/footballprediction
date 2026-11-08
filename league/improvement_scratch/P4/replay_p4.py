#!/usr/bin/env python3
"""P4 Gate Zero replay v2: level-only recalibration from the last dev season.
Persisted artefacts only. Tiers:
  dev source: PM = per-match file/JSON inputs; AGG = per-season aggregate in results_dev.json
              (mean P(over) and actual rate for the last dev season -- the offset
               mean_p - actual is identical to the per-match computation).
  sealed source: PM = per-match predictions; AGG = aggregate in results_virgin.json
              (after_pp = before_pp - offset; SE carried over, exact for a pure
               shift absent clamping, since sd(p_i - y_i) is shift-invariant).
"""
import json, glob, os, re, csv, math, statistics
ROOT = '/home/hatch/workspace/footballprediction/league'
MKTDIR = {'S':'sot','C':'corners','K':'cards','T':'total_shots','G':'goals'}
MKTPREFIX = {'S':'s','C':'c','K':'k','T':'t','G':'g'}

def norm_arm(a):
    if a is None: return None
    s = str(a).strip().lower().replace(' ','_').replace('-','_')
    if s in ('gz','gate_zero','gatezero','gate_0'): return 'GZ'
    if s in ('a','arm_a','v1'): return 'A'
    if s in ('b','arm_b'): return 'B'
    if s in ('c','arm_c'): return 'C'
    return s.upper()

def season_key(s):
    m = re.match(r'^(\d{4})(?:[/-](\d{2,4}))?$', str(s).strip())
    if not m: return None
    y2 = m.group(2)
    if y2 and len(y2)==2: y2 = str(int(m.group(1))//100)+y2
    return (int(m.group(1)), int(y2) if y2 else 0)

def clamp(p): return min(0.999, max(0.001, p))

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except Exception: return None

def find_primary_line(engdir, league, market):
    # 1) prereg text
    pdir = os.path.join(ROOT, league, 'prereg')
    if os.path.isdir(pdir):
        for fn in sorted(os.listdir(pdir)):
            if fn.startswith(f'PREREG_{market}_') and fn.endswith('.md'):
                txt = open(os.path.join(pdir,fn), errors='ignore').read()
                m = re.search(r'[Pp]rimary line[^0-9]{0,30}?(\d{1,2}\.\d)', txt)
                if m: return float(m.group(1))
                m = re.search(r'[Pp]rimary[^\n]{0,60}?(\d{1,2}\.5)\b', txt)
                if m: return float(m.group(1))
    # 2) protocol primary_line in jsons
    for fn in ('results_virgin.json','results_dev.json','fitted_params_virgin.json'):
        d = load_json(os.path.join(engdir, fn))
        if d is None: continue
        stack=[d]
        while stack:
            o=stack.pop()
            if isinstance(o,dict):
                if isinstance(o.get('primary_line'),(int,float)): return float(o['primary_line'])
                stack.extend(o.values())
            elif isinstance(o,list): stack.extend(o)
    # 3) virgin json: line whose mean-actual matches calibration_diff, else unique ll_ key
    d = load_json(os.path.join(engdir,'results_virgin.json'))
    if isinstance(d, dict):
        cands=[]
        stack=[d]
        while stack:
            o=stack.pop()
            if isinstance(o,dict):
                lines=[k for k in o if re.match(r'^ll_\d+\.5$', k)]
                for lk in lines:
                    ln=float(lk[3:])
                    mp=o.get(f'mean_p_{ln:g}'); ac=o.get(f'actual_over_{ln:g}'); cd=o.get('calibration_diff')
                    if mp is not None and ac is not None and cd is not None and abs(abs(mp-ac)-abs(cd))<0.002:
                        return ln
                    cands.append(ln)
                stack.extend(o.values())
            elif isinstance(o,list): stack.extend(o)
        uniq=sorted(set(cands))
        if len(uniq)==1: return uniq[0]
    return None

def find_shipped_arm(engdir):
    for fn in ('results_virgin.json','fitted_params_virgin.json','fitted_params.json'):
        d = load_json(os.path.join(engdir, fn))
        if d is None: continue
        stack=[d]
        while stack:
            o=stack.pop()
            if isinstance(o,dict):
                for k,v in o.items():
                    if k in ('shipped_arm','ship_arm','selected_arm','chosen_arm','winner_arm') and isinstance(v,str):
                        return norm_arm(v)
                stack.extend(o.values())
            elif isinstance(o,list): stack.extend(o)
    return None

def read_csv(path):
    try:
        with open(path, newline='') as f: return list(csv.DictReader(f))
    except Exception: return None

def col(row, names):
    for n in names:
        if n in row and row[n] not in ('', None): return n
    return None

def line_variants(line):
    s=f"{line:g}"; return [s, s.replace('.','_'), s.replace('.','')]

def prob_col(row, line):
    names=['p_over_primary']
    for v in line_variants(line): names += [f'ft_p_over_{v}', f'p_over_{v}']
    names += ['p_over']
    return col(row, names)

def actual_over(row, line):
    c=col(row,['actual_over_primary'])
    if c:
        try: return float(row[c])
        except: pass
    c=col(row,['actual_total','actual_target','total','actual_total_sot','target'])
    if not c:
        cands=[k for k in row if k.startswith('actual') and k.endswith('_total')]
        c=cands[0] if cands else None
    if c:
        try: return 1.0 if float(row[c])>line else 0.0
        except: pass
    return None

def arm_of(row):
    c=col(row,['arm','arm_or_baseline'])
    if not c: return None
    v=row[c]
    if ':' in v: v=v.split(':',1)[1]
    return norm_arm(v)

def extract_pm(rows, line, arm_want=None, amap=None):
    if not rows: return None
    per={}
    for r in rows:
        a=arm_of(r)
        if arm_want and a and a!=arm_want: continue
        pc=prob_col(r,line)
        if pc is None: continue
        try: p=float(r[pc])
        except: continue
        y=actual_over(r,line)
        if y is None and amap and str(r.get('match_id','')) in amap:
            y=1.0 if amap[str(r['match_id'])]>line else 0.0
        if y is None: continue
        s=r.get('season') or '__noseason__'
        per.setdefault(str(s),[]).append((p,y))
    return per or None

def extract_pm_goals(rows, arm_want=None):
    if not rows: return None
    per={}
    for r in rows:
        a=arm_of(r)
        if arm_want and a and a!=arm_want: continue
        phc=col(r,['p_home','ph','p_home_win','pH']); poc=col(r,['p_over_2_5','p_over_2.5','p_over_25','p_over'])
        hgc=col(r,['actual_home_goals','home_goals','hg']); agc=col(r,['actual_away_goals','away_goals','ag'])
        if not(phc and poc and hgc and agc): continue
        try: ph=float(r[phc]); po=float(r[poc]); hg=float(r[hgc]); ag=float(r[agc])
        except: continue
        s=r.get('season') or '__noseason__'
        per.setdefault(str(s),[]).append((ph,1.0 if hg>ag else 0.0,po,1.0 if hg+ag>2.5 else 0.0))
    return per or None


def extract_pm_goals_wide(rows, arm_want=None):
    if not rows: return None
    hdr=list(rows[0].keys())
    prefixes=sorted({h[:-3] for h in hdr if h.endswith('_ph')})
    if not prefixes: return None
    per={}
    for r in rows:
        hg_c=col(r,['actual_home_goals','home_goals','hg']); ag_c=col(r,['actual_away_goals','away_goals','ag'])
        if not(hg_c and ag_c): continue
        try: hg=float(r[hg_c]); ag=float(r[ag_c])
        except: continue
        for pre in prefixes:
            if arm_want and norm_arm(pre)!=arm_want: continue
            oc=f'{pre}_over25'
            if oc not in r: continue
            try: ph=float(r[f'{pre}_ph']); po=float(r[oc])
            except: continue
            s=r.get('season') or '__noseason__'
            per.setdefault(str(s),[]).append((ph,1.0 if hg>ag else 0.0,po,1.0 if hg+ag>2.5 else 0.0))
    return per or None


_season_map_cache={}
def season_map(league):
    if league in _season_map_cache: return _season_map_cache[league]
    mp={}
    ddir=os.path.join(ROOT,league,'data')
    if os.path.isdir(ddir):
        for fn in sorted(os.listdir(ddir)):
            if fn.endswith('_matches.csv') and 'team' not in fn:
                rows=read_csv(os.path.join(ddir,fn)) or []
                for r in rows:
                    if r.get('match_id') and r.get('season'): mp[str(r['match_id'])]=str(r['season'])
                if mp: break
    _season_map_cache[league]=mp
    return mp

def enrich_seasons(rows, league):
    if not rows: return rows
    if any(r.get('season') for r in rows): return rows
    mp=season_map(league)
    if not mp: return rows
    for r in rows:
        if not r.get('season') and str(r.get('match_id','')) in mp:
            r['season']=mp[str(r['match_id'])]
    return rows


def file_arm(fn):
    low=os.path.basename(fn).lower()
    if 'gatezero' in low.replace('_','') or 'gate_zero' in low: return 'GZ'
    if 'entrant' in low: return 'ENTRANT'
    if 'shrink' in low: return 'SHRINK'
    m=re.search(r'_(x\d)(?:_|\.)', low)
    if m: return m.group(1).upper()
    if low.endswith('_gz.csv') or '_gz_' in low: return 'GZ'
    if low.endswith('_rs.csv') or '_rs_' in low: return 'RS'
    m=re.search(r'_([abc])\.csv$', low)
    if m: return m.group(1).upper()
    return None

_actual_map_cache={}
def actual_map(league, market):
    key=(league,market)
    if key in _actual_map_cache: return _actual_map_cache[key]
    mp={}
    ddir=os.path.join(ROOT,league,'data')
    if os.path.isdir(ddir):
        for fn in sorted(os.listdir(ddir)):
            if fn.endswith('_matches.csv') and 'team' not in fn:
                rows=read_csv(os.path.join(ddir,fn)) or []
                for r in rows:
                    mid=str(r.get('match_id',''))
                    if not mid: continue
                    try:
                        if market=='S': v=float(r['ShotsOnTarget_home'])+float(r['ShotsOnTarget_away'])
                        elif market=='C': v=float(r['corners_home'])+float(r['corners_away'])
                        elif market=='T': v=float(r['total_shots_home'])+float(r['total_shots_away'])
                        elif market=='K': v=float(r['yellow_home'])+float(r['yellow_away'])
                        else: continue
                    except Exception: continue
                    mp[mid]=v
                if mp: break
    _actual_map_cache[key]=mp
    return mp

def rows_from_calibration_inputs(d):
    if isinstance(d,dict) and isinstance(d.get('calibration_inputs'),list):
        return [{k:(str(v) if v is not None else '') for k,v in row.items()} if isinstance(row,dict) else None for row in d['calibration_inputs']]
    return None

# ---------- aggregate collectors ----------
def mean_actual_from_node(node, line, line_ctx=None):
    if not isinstance(node,dict): return None
    for v in line_variants(line):
        for mk in (f'mean_p_{v}', f'mean_pred_{v}'):
            ak=f'actual_over_{v}'
            if mk in node and ak in node:
                try: return float(node[mk]), float(node[ak])
                except: return None
    if line_ctx is not None and abs(line_ctx-line)>1e-9: return None
    if 'mean_pred_over_pp' in node and 'actual_over_rate_pp' in node:
        try: return float(node['mean_pred_over_pp'])/100.0, float(node['actual_over_rate_pp'])/100.0
        except: return None
    for mk,ak in [('mean_p_primary','actual_over_primary'),('mean_p_over','actual_over'),('mean_p','actual_rate'),
                  ('mean_p','actual_over'),('mean_pred','actual_rate'),('mean_p','actual_over_rate'),
                  ('mean_predicted_over_rate','actual_over_rate')]:
        if mk in node and ak in node:
            try:
                m=float(node[mk]); a=float(node[ak])
                if m>1.5: m/=100.0
                if a>1.5: a/=100.0
                return m,a
            except: return None
    return None

def se_from_node(node, line):
    if not isinstance(node,dict): return None
    for v in line_variants(line):
        for sk in (f'calibration_se_{v}',):
            if sk in node:
                try: return float(node[sk])
                except: pass
    for sk,scale in [('calibration_se_pp',0.01),('se_pp',0.01),('calibration_se',1.0),('se',1.0)]:
        if sk in node:
            try: return float(node[sk])*scale
            except: pass
    return None

ARM_TOKENS={'gz','gate_zero','gatezero','rs','a','b','c','shrink','plain','entrant'}
def walk_records(d, line, with_se=False):
    recs=[]
    def walk(node, arm_ctx, season_ctx, kind_ctx, line_ctx=None):
        if isinstance(node,dict):
            arm,season,kind=arm_ctx,season_ctx,kind_ctx
            if isinstance(node.get('arm'),str): arm=norm_arm(node['arm'])
            if isinstance(node.get('season'),(str,int)): season=str(node['season'])
            if isinstance(node.get('kind'),str): kind=node['kind']
            if isinstance(node.get('line'),(int,float)): line_ctx=float(node['line'])
            if kind is None or kind=='model':
                ma=mean_actual_from_node(node,line,line_ctx)
                if ma:
                    recs.append((arm,season,ma[0],ma[1], se_from_node(node,line) if with_se else None, kind))
            for k,v in node.items():
                ks=str(k).strip(); na,ns,nk,nl=arm,season,kind,line_ctx
                if ks.lower().replace(' ','_') in ARM_TOKENS or re.match(r'^x\d+$',ks.lower()) or norm_arm(ks) in ('GZ','RS','A','B','C','SHRINK','PLAIN','ENTRANT'):
                    na=norm_arm(ks)
                if season_key(ks) and not re.match(r'^\d+\.\d+$',ks): ns=ks
                if re.match(r'^\d+\.5$',ks): nl=float(ks)
                kl=ks.lower().replace(' ','_')
                if kl=='model': nk='model'
                elif kl in ('base','league_base_rate','naive','naive_trailing_10','climatology','baseline_league','baseline_naive','baselines','league_base','base_rate'): nk='baseline'
                walk(v,na,ns,nk,nl)
        elif isinstance(node,list):
            for it in node: walk(it,arm_ctx,season_ctx,kind_ctx,line_ctx)
    walk(d,None,None,None)
    out={}
    for r in recs: out[(r[0],r[1],round(r[2],10),round(r[3],10),r[5])]=r
    return list(out.values())

def pick_dev_agg(recs, arm_want):
    if not recs: return None
    cand=[r for r in recs if r[1] and season_key(r[1]) and (len(r)<6 or r[5] in (None,'model'))]
    if arm_want: cand2=[r for r in cand if r[0]==arm_want]
    else: cand2=[]
    if cand2: cand=cand2
    elif arm_want:
        cand=[r for r in cand if r[0] in (None,'MODEL')]
        if not cand: return None
    if not cand: return None
    last=sorted({r[1] for r in cand}, key=lambda s: season_key(s))[-1]
    rows=[r for r in cand if r[1]==last]
    return rows[0][2]-rows[0][3], last


def collect_se(d, line):
    """arm -> SE (fraction) from calibration/se keys anywhere in virgin json"""
    out={}
    lvs=line_variants(line)
    def walk(node, arm_ctx):
        if isinstance(node,dict):
            arm=arm_ctx
            if isinstance(node.get('arm'),str): arm=norm_arm(node['arm'])
            for k,v in node.items():
                ks=str(k); na=arm
                if ks.lower().replace(' ','_') in ARM_TOKENS or re.match(r'^x\d+$',ks.lower()) or norm_arm(ks) in ('GZ','RS','A','B','C','SHRINK','PLAIN','ENTRANT'):
                    na=norm_arm(ks)
                if isinstance(v,(int,float)):
                    for lv in lvs:
                        if ks in (f'se_{lv}', f'calibration_se_{lv}'):
                            out.setdefault(na, float(v))
                    if ks=='calibration_se': out.setdefault(na, float(v))
                    if ks in ('se_pp','calibration_se_pp'): out.setdefault(na, float(v)/100.0)
                walk(v,na)
        elif isinstance(node,list):
            for it in node: walk(it,arm_ctx)
    walk(d,None)
    return out

def pick_sealed_agg(recs, arm_want):
    if not recs: return None
    cand=[r for r in recs if r[0] not in ('LEAGUE_BASE_RATE','NAIVE','BASE','BASELINE_LEAGUE','BASELINE_NAIVE','NAIVE_TRAILING_10','CLIMATOLOGY') and (len(r)<6 or r[5] in (None,'model'))]
    if arm_want:
        c2=[r for r in cand if r[0]==arm_want]
        if c2: cand=c2
        else:
            c3=[r for r in cand if r[0] in (None,'MODEL')]
            if c3: cand=c3
            else: return None
    if not cand: return None
    r=cand[0]
    return r[2], r[3], r[4]  # mean, actual, se

# goals aggregates
def goals_dev_agg(d, arm_want):
    """per-season (hw_cal_pp, ou_cal_pp) pred-actual, DK-style"""
    if not isinstance(d,dict): return None
    arms=d.get('arms') or {}
    cands={}
    for ak,av in arms.items():
        if not isinstance(av,dict): continue
        seasons=av.get('seasons') or {}
        for s,sv in seasons.items():
            if isinstance(sv,dict) and 'home_win_calibration_pp' in sv and 'ou25_calibration_pp' in sv and season_key(str(s)):
                cands.setdefault(norm_arm(ak),{})[str(s)]=(float(sv['home_win_calibration_pp'])/100.0, float(sv['ou25_calibration_pp'])/100.0)
    if arm_want and arm_want in cands: seasons=cands[arm_want]
    elif len(cands)==1: seasons=list(cands.values())[0]
    elif 'GZ' in cands: seasons=cands['GZ']
    else: return None
    last=sorted(seasons, key=lambda s: season_key(s))[-1]
    hw,ou=seasons[last]
    return (hw,ou), last

def goals_sealed_agg(d, arm_want):
    """virgin json <arm>.calibration{home_win_diff,home_win_se,over25_diff,over25_se} pred-actual"""
    if not isinstance(d,dict): return None
    out={}
    for ak,av in d.items():
        if isinstance(av,dict) and isinstance(av.get('calibration'),dict):
            c=av['calibration']
            if 'home_win_diff' in c and 'over25_diff' in c:
                out[norm_arm(ak)]=(float(c['home_win_diff'])*100, float(c.get('home_win_se',0))*100,
                                   float(c['over25_diff'])*100, float(c.get('over25_se',0))*100)
    if not out: return None
    if arm_want and arm_want in out: return out[arm_want]
    if 'GZ' in out: return out['GZ']
    if len(out)==1: return list(out.values())[0]
    return None

def score(pairs, offset):
    n=len(pairs); mean_p=sum(p for p,_ in pairs)/n; act=sum(y for _,y in pairs)/n
    before=(mean_p-act)*100
    se_b=(statistics.stdev([p-y for p,y in pairs])/math.sqrt(n)*100) if n>1 else float('nan')
    adj=[(clamp(p-offset),y) for p,y in pairs]
    after=(sum(p for p,_ in adj)/n-act)*100
    se_a=(statistics.stdev([p-y for p,y in adj])/math.sqrt(n)*100) if n>1 else float('nan')
    return dict(n=n,before=before,se_before=se_b,after=after,se_after=se_a)

def leg_status(pp, se):
    if se is None or (isinstance(se,float) and math.isnan(se)):
        return 'clean' if abs(pp)<=1.0 else 'unknown'
    if abs(pp)<=1.0: return 'clean'
    if abs(pp)<=1.0+se: return 'provisional'
    return 'fail'

def main():
    rows=[]
    for f in sorted(glob.glob(ROOT+'/audit_scratch/class_batch*.jsonl')):
        for line in open(f): rows.append(json.loads(line))
    targets=[r for r in rows if r['outcome'].startswith('PASS') or r['fail_point']=='sealed']
    out=[]
    for r in targets:
        L,m,cand=r['league'],r['market'],r['candidate']
        engdir=os.path.join(ROOT,L,'engine',MKTDIR[m])
        group='PASS' if r['outcome'].startswith('PASS') else ('SEALED_CAL_FAIL' if any('CAL' in x for x in r['fail_legs']) else 'SEALED_OTHER_FAIL')
        rec=dict(league=L,market=m,candidate=cand,group=group,outcome=r['outcome'],measurable='',arm='',
                 primary_line='',dev_last_season='',dev_source='',sealed_source='',offset='',
                 sealed_before_pp='',sealed_after_pp='',se_after_pp='',rescued='',broken='',notes='')
        out.append(rec)
        if not os.path.isdir(engdir): rec['measurable']='no'; rec['notes']='no engine dir'; continue
        line=find_primary_line(engdir,L,m)
        if m=='G': line=2.5
        if line is None: rec['measurable']='no'; rec['notes']='primary line not found in prereg/json'; continue
        rec['primary_line']=line
        shipped=find_shipped_arm(engdir)
        # file inventories
        sealed_csvs=[]; dev_csvs=[]
        for fn in sorted(os.listdir(engdir)):
            if not fn.endswith('.csv'): continue
            p=os.path.join(engdir,fn)
            if 'virgin' in fn.lower(): sealed_csvs.append(p)
            if 'dev' in fn.lower(): dev_csvs.append(p)
        pdir=os.path.join(ROOT,L,'predictions')
        if os.path.isdir(pdir):
            for fn in sorted(os.listdir(pdir)):
                if fn.endswith('_virgin_predictions.csv') and fn.startswith(MKTPREFIX[m]+'_'):
                    sealed_csvs.append(os.path.join(pdir,fn))
        dev_json=load_json(os.path.join(engdir,'results_dev.json'))
        vir_json=load_json(os.path.join(engdir,'results_virgin.json'))
        dev_agg_recs = walk_records(dev_json, line) if (dev_json is not None and m!='G') else []
        sealed_agg_recs = walk_records(vir_json, line, with_se=True) if (vir_json is not None and m!='G') else []

        arm_try=[]
        for a in [shipped,'GZ','A','RS','SHRINK','B','C','PLAIN','X8','X7','X3','X2','ENTRANT']:
            if a and a not in arm_try: arm_try.append(a)
        arm_try.append(None)

        attempts=[]
        for arm_want in arm_try:
            # --- sealed ---
            sealed=None  # ('PM', pairs or goalpairs, src) or ('AGG', before_pp, se, src) ; goals AGG separate
            for sf in sealed_csvs:
                farm=file_arm(sf)
                if farm and arm_want and farm!=arm_want: continue
                srows=read_csv(sf)
                if not srows: continue
                if m=='G':
                    per=extract_pm_goals(srows,arm_want)
                    if per:
                        allp=[]; [allp.extend(v) for v in per.values()]
                        if allp: sealed=('PM',allp,os.path.basename(sf),None); break
                else:
                    per=extract_pm(srows,line,arm_want,actual_map(L,m))
                    if per:
                        allp=[]; [allp.extend(v) for v in per.values()]
                        if allp: sealed=('PM',allp,os.path.basename(sf),None); break
            if sealed is None and vir_json is not None:
                ci=rows_from_calibration_inputs(vir_json)
                if ci:
                    if m=='G':
                        per=extract_pm_goals(ci,arm_want)
                        if per:
                            allp=[]; [allp.extend(v) for v in per.values()]
                            if allp: sealed=('PM',allp,'results_virgin.json:calibration_inputs',None)
                    else:
                        per=extract_pm(ci,line,arm_want)
                        if per:
                            allp=[]; [allp.extend(v) for v in per.values()]
                            if allp: sealed=('PM',allp,'results_virgin.json:calibration_inputs',None)
            if sealed is None and m!='G':
                pa=pick_sealed_agg(sealed_agg_recs,arm_want)
                if pa and pa[0] is not None:
                    mean,act,se=pa
                    if se is None and vir_json is not None:
                        semap=collect_se(vir_json,line)
                        se=semap.get(arm_want) or semap.get(None) or (list(semap.values())[0] if len(semap)==1 else None)
                    sealed=('AGG',(mean-act)*100,'results_virgin.json (aggregate)',se)
            if sealed is None and m=='G' and vir_json is not None:
                ga=goals_sealed_agg(vir_json,arm_want)
                if ga: sealed=('GAGG',ga,'results_virgin.json (aggregate)',None)
            if sealed is None: continue
            # --- dev offset ---
            offset=None; dseason=None; dsrc=None
            for df in dev_csvs:
                farm=file_arm(df)
                if farm and arm_want and farm!=arm_want: continue
                drows=enrich_seasons(read_csv(df), L)
                if not drows: continue
                if m=='G':
                    per=extract_pm_goals(drows,arm_want) or extract_pm_goals_wide(drows,arm_want)
                    if per:
                        seasons=[s for s in per if season_key(s)]
                        if seasons:
                            last=sorted(seasons,key=lambda s: season_key(s))[-1]; ps=per[last]
                            offset=(sum(x[0] for x in ps)/len(ps)-sum(x[1] for x in ps)/len(ps),
                                    sum(x[2] for x in ps)/len(ps)-sum(x[3] for x in ps)/len(ps))
                            dseason=last; dsrc=os.path.basename(df)+' (per-match)'; break
                else:
                    per=extract_pm(drows,line,arm_want)
                    if per:
                        seasons=[s for s in per if season_key(s)]
                        if seasons:
                            last=sorted(seasons,key=lambda s: season_key(s))[-1]; ps=per[last]
                            offset=sum(p for p,_ in ps)/len(ps)-sum(y for _,y in ps)/len(ps)
                            dseason=last; dsrc=os.path.basename(df)+' (per-match)'; break
            if offset is None and dev_json is not None:
                ci=rows_from_calibration_inputs(dev_json)
                if ci:
                    if m=='G':
                        per=extract_pm_goals(ci,arm_want)
                        if per:
                            seasons=[s for s in per if season_key(s)]
                            if seasons:
                                last=sorted(seasons,key=lambda s: season_key(s))[-1]; ps=per[last]
                                offset=(sum(x[0] for x in ps)/len(ps)-sum(x[1] for x in ps)/len(ps),
                                        sum(x[2] for x in ps)/len(ps)-sum(x[3] for x in ps)/len(ps))
                                dseason=last; dsrc='results_dev.json:calibration_inputs (per-match)'
                    else:
                        per=extract_pm(ci,line,arm_want)
                        if per:
                            seasons=[s for s in per if season_key(s)]
                            if seasons:
                                last=sorted(seasons,key=lambda s: season_key(s))[-1]; ps=per[last]
                                offset=sum(p for p,_ in ps)/len(ps)-sum(y for _,y in ps)/len(ps)
                                dseason=last; dsrc='results_dev.json:calibration_inputs (per-match)'
            if offset is None and m!='G':
                pa=pick_dev_agg(dev_agg_recs,arm_want)
                if pa: offset,dseason=pa; dsrc='results_dev.json (per-season aggregate)'
            if offset is None and m=='G':
                ga=goals_dev_agg(dev_json,arm_want)
                if ga: offset,dseason=ga; dsrc='results_dev.json (per-season aggregate)'
            if offset is None: continue
            attempts.append((arm_want,sealed,offset,dseason,dsrc))
            # early accept: breach match or shipped pass arm
            if m!='G' and r.get('breach_pp') is not None:
                if sealed[0]=='PM': bfr=score(sealed[1],offset)['before']
                else: bfr=sealed[1]
                if abs(abs(bfr)-abs(r['breach_pp']))<=0.30: break
            if group=='PASS' and shipped and arm_want==shipped: break
        if not attempts:
            rec['measurable']='no'; rec['notes']='no dev-offset + sealed pair for any arm'; continue
        # Arm of record: PASS -> shipped arm (attempts are in arm_try order, shipped first).
        # FAIL -> reference arm (GZ for S/C/K/G, A for T) if it was scored on the sealed
        # window; else the first attempt whose before-leg fails; else first attempt.
        if group=='PASS':
            best=attempts[0]
        else:
            ref='A' if m=='T' else 'GZ'
            ref_at=[at for at in attempts if at[0]==ref]
            if ref_at: best=ref_at[0]
            else:
                fail_at=[]
                for at in attempts:
                    if m=='G':
                        fail_at.append(at)  # goals: first non-reference attempt
                        break
                    if at[1][0]=='PM': bfr=score(at[1][1],at[2])
                    else: bfr=None
                    fail_at.append(at); break
                best=fail_at[0] if fail_at else attempts[0]
        arm_want,sealed,offset,dseason,dsrc=best
        rec['measurable']='yes'; rec['arm']=arm_want or ''; rec['dev_last_season']=dseason
        rec['dev_source']=dsrc; rec['sealed_source']=sealed[2]
        tier=f"dev={'PM' if 'per-match' in dsrc else 'AGG'}/sealed={sealed[0]}"
        if m=='G':
            rec['offset']=f"HW {offset[0]*100:+.2f}pp; OU {offset[1]*100:+.2f}pp"
            if sealed[0]=='PM':
                gp=sealed[1]
                hw=score([(x[0],x[1]) for x in gp],offset[0]); ou=score([(x[2],x[3]) for x in gp],offset[1])
                b_hw,b_ou,s_hw,s_ou = hw['before'],ou['before'],hw['se_after'],ou['se_after']
                a_hw,a_ou = hw['after'],ou['after']; seb_hw,seb_ou=hw['se_before'],ou['se_before']; n=hw['n']
            else:
                b_hw,s_hw,b_ou,s_ou = sealed[1]; seb_hw,seb_ou=s_hw,s_ou
                a_hw=b_hw-offset[0]*100; a_ou=b_ou-offset[1]*100; n=r.get('virgin_n')
            rec['sealed_before_pp']=f"HW {b_hw:+.2f}; OU {b_ou:+.2f}"
            rec['sealed_after_pp']=f"HW {a_hw:+.2f}; OU {a_ou:+.2f}"
            rec['se_after_pp']=f"HW {s_hw:.2f}; OU {s_ou:.2f}"
            st_b=[leg_status(b_hw,seb_hw),leg_status(b_ou,seb_ou)]; st_a=[leg_status(a_hw,s_hw),leg_status(a_ou,s_ou)]
            rec['notes']=f"tier={tier}; n={n}; before HW={st_b[0]}/OU={st_b[1]}; after HW={st_a[0]}/OU={st_a[1]}"
            if group=='SEALED_CAL_FAIL':
                idx=0 if 'CAL_1X2' in r['fail_legs'] else 1
                rec['rescued']='yes' if (st_a[idx] in ('clean','provisional') and all(s in ('clean','provisional') for s in st_a)) else 'no'
            if group=='PASS': rec['broken']='yes' if any(s=='fail' for s in st_a) else 'no'
        else:
            if sealed[0]=='PM':
                sc=score(sealed[1],offset)
                rec['offset']=f"{offset*100:+.2f}"; rec['sealed_before_pp']=f"{sc['before']:+.2f}"
                rec['sealed_after_pp']=f"{sc['after']:+.2f}"; rec['se_after_pp']=f"{sc['se_after']:.2f}"
                st_b=leg_status(sc['before'],sc['se_before']); st_a=leg_status(sc['after'],sc['se_after'])
                rec['notes']=f"tier={tier}; n={sc['n']}; before leg={st_b}; after leg={st_a}; se_before={sc['se_before']:.2f}"
            else:
                bfr=sealed[1]; se_b=sealed[3]
                if se_b is not None: se_b=se_b*100.0
                if se_b is None and r.get('se_pp') is not None: se_b=float(r['se_pp'])
                after=bfr-offset*100
                rec['offset']=f"{offset*100:+.2f}"; rec['sealed_before_pp']=f"{bfr:+.2f}"
                rec['sealed_after_pp']=f"{after:+.2f}"; rec['se_after_pp']=f"{se_b:.2f}" if se_b is not None else ''
                st_b=leg_status(bfr,se_b); st_a=leg_status(after,se_b)
                rec['notes']=f"tier={tier}; n={r.get('virgin_n')}; before leg={st_b}; after leg={st_a}; se carried over (shift-invariant)"
            if st_a=='unknown':
                rec['measurable']='indeterminate'
            if group=='SEALED_CAL_FAIL': rec['rescued']='yes' if st_a in ('clean','provisional') else ('no' if st_a=='fail' else '')
            if group=='PASS': rec['broken']='yes' if st_a=='fail' else ('no' if st_a in ('clean','provisional') else '')
    # NOTE: sealed AGG handling patched below in main2
    cols=['league','market','candidate','group','measurable','arm','primary_line','dev_last_season','dev_source','sealed_source','offset','sealed_before_pp','sealed_after_pp','se_after_pp','rescued','broken','outcome','notes']
    outpath=os.path.join(ROOT,'improvement_scratch','P4','per_candidate.csv')
    with open(outpath,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for rec in out: w.writerow({k:rec.get(k,'') for k in cols})
    for g in ('SEALED_CAL_FAIL','PASS','SEALED_OTHER_FAIL'):
        sub=[x for x in out if x['group']==g]; meas=[x for x in sub if x['measurable']=='yes']
        print(g,'total',len(sub),'measurable',len(meas))
        if g=='SEALED_CAL_FAIL': print('  rescued',sum(1 for x in meas if x['rescued']=='yes'))
        if g=='PASS': print('  broken',sum(1 for x in meas if x['broken']=='yes'))
    json.dump(out,open('/tmp/p4_out.json','w'),indent=1)

if __name__=='__main__': main()
