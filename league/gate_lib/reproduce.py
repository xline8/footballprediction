"""Schema-shape based readers for the historical result artefacts."""
import csv, json, math, re
from .metrics import log_loss, calibration, pooled_ll
def _read(x):
    if isinstance(x,(str,bytes)):
        with open(x,encoding='utf-8') as f:return json.load(f)
    return x
def _line_key(d,line):
    token=str(line).replace('.','_')
    for k in (f'll_{token}',f'll_{line}',f'logloss_{line}',str(line), 'll'):
        if k in d:
            value=d[k]
            return value.get('ll') if isinstance(value,dict) and 'll' in value else value
    logloss = d.get('logloss') if isinstance(d, dict) else None
    if isinstance(logloss, dict):
        for k in (str(line), token, f'{line}'):
            if k in logloss: return logloss[k]
    if 'oull_2_5' in d and (line is None or float(line) == 2.5):
        return d['oull_2_5']
    return None
def normalise_dev(data,line):
    """Return {arm: {seasons:{season: {ll,n}}, pooled:{ll,n}}}."""
    d=_read(data); out={}
    def add(arm,season,ll,n,kind='model'):
        if ll is None or isinstance(ll,(dict,list,tuple)):return
        a=out.setdefault(str(arm),{'seasons':{},'kind':kind})
        if season is not None:a['seasons'][str(season)]={'ll':float(ll),'n':int(n or 0)}
        else:a['pooled']={'ll':float(ll),'n':int(n or 0)}
    rows=d.get('rows') if isinstance(d,dict) else d
    if isinstance(rows,list):
        for r in rows:
            kind=r.get('kind','model'); arm=r.get('arm',r.get('name','unknown'))
            add(str(arm) if kind == 'model' else f'{arm}/{kind}',r.get('season'),_line_key(r,line),r.get('n'),kind)
    if isinstance(d,dict) and isinstance(d.get('arms'),dict):
        for arm,a in d['arms'].items():
            for season,r in (a.get('seasons') or {}).items():
                variants = r.items() if isinstance(r,dict) and any(k in r for k in ('model','base','naive')) else [('model',r)]
                for kind, rr in variants:
                    if not isinstance(rr,dict): continue
                    key = str(arm) if kind == 'model' else f'{arm}/{kind}'
                    n = rr.get('n', r.get('n', a.get('n'))) if isinstance(r,dict) else a.get('n')
                    if not n and isinstance(rr,dict):
                        mv = rr.get(str(line), rr.get(str(line).replace('.','_')))
                        if isinstance(mv,dict): n = mv.get('n', n)
                    add(key,season,_line_key(rr,line),n,kind)
            p=a.get('pooled') or {}
            if p:
                variants = p.items() if any(k in p for k in ('model','base','naive')) else [('model',p)]
                for kind, pp in variants:
                    if isinstance(pp,dict): add(str(arm) if kind == 'model' else f'{arm}/{kind}',None,_line_key(pp,line),pp.get('n',a.get('n')),kind)
            elif not a.get('seasons'):
                # Flat pooled-only schema (e.g. LV-Virsliga: a single dev
                # window, ll_<line> stored directly on the arm dict).
                add(str(arm),None,_line_key(a,line),a.get('n'))
        for arm,a in (d.get('baselines') or {}).items():
            if not isinstance(a,dict): continue
            for season,r in (a.get('seasons') or {}).items():
                add(str(arm),season,_line_key(r,line),r.get('n',a.get('n')))
            p=a.get('pooled') or {}
            if p: add(str(arm),None,_line_key(p,line),p.get('n',a.get('n')))
            elif not a.get('seasons'): add(str(arm),None,_line_key(a,line),a.get('n'))
    if isinstance(d,dict) and isinstance(d.get('metrics'),dict):
        for arm,a in d['metrics'].items():
            if not isinstance(a,dict): continue
            for season,r in a.items():
                if season == 'pooled' or not isinstance(r,dict): continue
                wrapper = r
                rr = r.get('model', r)
                add(arm,season,_line_key(rr.get('logloss',rr),line),rr.get('n', wrapper.get('n', a.get('n'))))
            p=a.get('pooled',{})
            add(arm,None,_line_key(p.get('logloss',p),line),p.get('n'))
    # standardise aggregate for each season collection
    for a in out.values():
        if 'pooled' not in a and a['seasons']:
            vals=list(a['seasons'].values()); n=sum(x['n'] for x in vals)
            a['pooled']={'ll':sum(x['ll']*x['n'] for x in vals)/n if n else None,'n':n}
    return out or None

def normalise_goals_dev(data):
    """Normalise the goals 1X2/RPS/OU artefact.

    Goals engines have used both a top-level row list and ``{rows: [...]}``.
    A row's ``kind`` is part of its identity: climatology and naive rows are
    baselines, not alternate model arms.  The returned shape is deliberately
    small and lossless enough for Gate Zero to replay the pooled rows.
    """
    d = _read(data)
    rows = d.get('rows') if isinstance(d, dict) else d
    if not isinstance(rows, list):
        return None
    out = {}
    for r in rows:
        if not isinstance(r, dict) or r.get('arm') is None:
            continue
        kind = str(r.get('kind', 'model'))
        key = (str(r['arm']), kind)
        item = out.setdefault(key, {'arm': str(r['arm']), 'kind': kind,
                                    'seasons': {}, 'pooled': None})
        value = {m: r.get(m) for m in ('ll_1x2', 'rps', 'oull_2_5')}
        if not any(v is not None for v in value.values()):
            continue
        value['n'] = int(r.get('n') or 0)
        season = str(r.get('season')) if r.get('season') is not None else None
        if season == 'pooled':
            item['pooled'] = value
        elif season is not None:
            item['seasons'][season] = value
    for item in out.values():
        if item['pooled'] is None and item['seasons']:
            item['pooled'] = {m: pooled_ll([
                {'ll': v[m], 'n': v['n']} for v in item['seasons'].values()
                if v.get(m) is not None]) for m in ('ll_1x2', 'rps', 'oull_2_5')}
            item['pooled']['n'] = sum(v['n'] for v in item['seasons'].values())
    return out or None
def normalise_virgin(data,line):
    d=_read(data); out={}
    def take(name,a):
        if not isinstance(a,dict):return
        ll=_line_key(a,line)
        cal_key='calibration_diff' if 'calibration_diff' in a else ('calibration' if 'calibration' in a else 'calibration_pp')
        cal=a.get(cal_key)
        se=a.get('calibration_se',a.get('calibration_se_pp'))
        if isinstance(cal,dict):
            se=cal.get('se',cal.get('calibration_se',se)); cal=cal.get('diff',cal.get('value',cal.get('pp')))
        if isinstance(se,dict): se=se.get('se',se.get('value'))
        if isinstance(cal,(list,tuple)): cal=cal[0] if cal else None
        if isinstance(se,(list,tuple)): se=se[0] if se else None
        if cal is not None and cal_key != 'calibration_pp' and abs(float(cal))<1: cal=float(cal)*100
        if se is not None and 'calibration_se_pp' not in a and abs(float(se))<1: se=float(se)*100
        # Goals store two calibration fields in a nested object.  Preserve
        # both so the runner can select the home-win or OU leg explicitly.
        calibration_fields = {}
        c = a.get('calibration')
        if isinstance(c, dict):
            for k, v in c.items():
                if k.endswith('_diff') or k.endswith('_se'):
                    calibration_fields[k] = float(v) * 100 if abs(float(v)) < 1 else float(v)
            if cal is None and c.get('over25_diff') is not None:
                cal = c['over25_diff'] * 100 if abs(float(c['over25_diff'])) < 1 else c['over25_diff']
                se = c.get('over25_se')
                if se is not None and abs(float(se)) < 1: se = float(se) * 100
        out[name]={'ll':ll,'calibration_diff_pp':cal,'calibration_se_pp':se,
                   'calibration_fields':calibration_fields,'n':a.get('n')}
    if isinstance(d,dict):
        for k,v in (d.get('arms') or {}).items():
            # Some count-market artefacts nest the actual metrics under
            # arms.<arm>.metrics.<kind> while goals keep them at arm level.
            if isinstance(v, dict) and isinstance(v.get('metrics'), dict):
                for mk, mv in v['metrics'].items(): take(f'{k}/{mk}', mv)
                if isinstance(v['metrics'].get('model'), dict): take(k, v['metrics']['model'])
                if any(x in v for x in ('calibration','calibration_diff')): take(k, v)
            else:
                take(k,v)
        for k,v in (d.get('baselines') or {}).items():take(k,v)
        for k,v in (d.get('metrics') or {}).items():take(k,v)
        g=d.get('gate_zero')
        if isinstance(g,dict): take(d.get('shipped_arm','gate_zero'),g)
        # Top-level arm entries (e.g. TR goals results_virgin.json is
        # {gate_zero: {...}, shrink: {...}, x3: {...}} with no 'arms' key).
        reserved={'protocol','arms','baselines','metrics','shipped_arm','export_arm','read_arms','gate_zero'}
        for k,v in d.items():
            if k in reserved or not isinstance(v,dict) or k in out: continue
            if _line_key(v,line) is not None or 'oull_2_5' in v or isinstance(v.get('metrics'),dict):
                take(k,v)
        for k,v in (d.get('arms') or {}).items():
            c=v.get('calibration') if isinstance(v,dict) else None
            target=out.get(f'{k}/model')
            if isinstance(c,dict) and target is not None:
                diff=c.get('diff_2_5',c.get('diff')); se=c.get('se_2_5',c.get('se'))
                if diff is not None: target['calibration_diff_pp']=float(diff)*100 if abs(float(diff))<1 else float(diff)
                if se is not None: target['calibration_se_pp']=float(se)*100 if abs(float(se))<1 else float(se)
    return out or None
def _find(row,patterns):
    for k in row:
        if any(re.fullmatch(p,k,re.I) for p in patterns): return row[k]
    return None
def virgin_csv_metrics(csv_path,line,arm=None,actual_column=None,actual_by_match=None):
    """Recompute the selected CSV arm; absent columns produce a non-raising result.

    Column names in the wild use both ``p_over_8_5`` and ``p_over_8.5`` spellings;
    matching normalises '.' and '_' before comparing. When the CSV carries no
    actual column, ``actual_by_match`` (match_id -> actual total) may supply the
    outcomes from the league's data file (e.g. J1 cards, whose virgin CSV has
    no actual column; the target definition comes from the prereg).
    """
    try:
        with open(csv_path,newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    except OSError:return {'available':False,'reason':'CSV absent'}
    if arm and rows and 'arm' in rows[0]:
        sel=[r for r in rows if r.get('arm')==arm]
        if sel: rows=sel
    token=str(line).replace('.','_')
    def _norm(k): return k.lower().replace('.','_')
    pcols=[k for k in rows[0] if re.search(r'(?:p_over|ft_p_over).*'+re.escape(token)+r'$',_norm(k))] if rows else []
    ac=actual_column
    if not ac and rows:
        for k in ('actual_total','actual_total_sot','actual_target','actual_corners_total','total'):
            if k in rows[0]: ac=k;break
        if not ac and 'home_goals' in rows[0] and 'away_goals' in rows[0]: ac='__goals__'
        if not ac and actual_by_match and 'match_id' in rows[0]: ac='__lookup__'
    if not pcols or not ac:return {'available':False,'reason':'probability or actual column absent','n':len(rows)}
    ps=[]; ys=[]
    for r in rows:
        try:
            p=float(r[pcols[0]])
            if ac=='__goals__': y=float(r['home_goals'])+float(r['away_goals'])
            elif ac=='__lookup__': y=float(actual_by_match[str(r['match_id'])])
            else: y=float(r[ac])
            ps.append(p);ys.append(float(y>float(line)))
        except (TypeError,ValueError,KeyError):pass
    if not ps:return {'available':False,'reason':'no numeric rows'}
    diff,se=calibration(ps,ys)
    return {'available':True,'n':len(ps),'ll':sum(log_loss(p,y) for p,y in zip(ps,ys))/len(ps),'calibration_diff_pp':diff,'calibration_se_pp':se}
