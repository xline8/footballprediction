import csv,json,math,os
from model import Engine,load_matches
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','..','..')); DATA=os.path.join(ROOT,'league','NO-OBOSLigaen','data','no_obos_matches.csv'); OUT=os.path.dirname(__file__)
DEV=('2021','2022','2023','2024','2025'); SCORED=('2022','2023','2024','2025'); PRIMARY=9.5
def ll(p,y): return -(y*math.log(max(p,1e-12))+(1-y)*math.log(max(1-p,1e-12)))
def actual(m): return int(m['sot_h']+m['sot_a']>PRIMARY)
def metrics(rows,fn):
    a={'pooled_dev_ll_9.5':sum(ll(fn(m,p),actual(m)) for m,p in rows)/len(rows),'n_scored':len(rows),'per_season':{}}
    for s in SCORED:
        z=[x for x in rows if x[0]['season']==s]; a['per_season'][s]={'ll_9.5':sum(ll(fn(m,p),actual(m)) for m,p in z)/len(z),'n':len(z)}
    a['mean_predicted_over_rate']=sum(fn(m,p) for m,p in rows)/len(rows); a['actual_over_rate']=sum(actual(m) for m,p in rows)/len(rows); return a
def run_dev():
    assert '2026' not in DEV; ms=load_matches(DATA,set(DEV)); out={'protocol':'S-NO-OBOS DEV; 2026 excluded','primary_line':PRIMARY,'arms':{},'baselines':{}}; allrows={}
    for arm in ('GZ','RS'):
        eng=Engine(ms,arm); rows=[]
        for m in ms:
            if m['season'] in SCORED: rows.append((m,eng.predict(m)))
            eng.update(m)
        allrows[arm]=rows; out['arms'][arm]=metrics(rows,lambda m,p:p['probs'][PRIMARY])
    rates={s:sum(actual(x) for x in ms if int(x['season'])<int(s))/sum(int(x['season'])<int(s) for x in ms) for s in SCORED}
    def base(m,p): return rates[m['season']]
    out['baselines']['base_rate']=metrics(allrows['GZ'],base); out['baselines']['naive_trailing_10']=metrics(allrows['GZ'],lambda m,p:p['naive_probs'][PRIMARY]); write(out,allrows,ms); return out
def write(out,allrows,all_ms):
    with open(os.path.join(OUT,'results_dev.json'),'w') as f: json.dump(out,f,indent=2)
    fields=['kind','arm_or_baseline','season','match_id','p_over_9_5','actual_over_9_5','exp_sot_total']
    with open(os.path.join(OUT,'results_dev.csv'),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for arm,rows in allrows.items():
            for m,p in rows: w.writerow({'kind':'arm','arm_or_baseline':arm,'season':m['season'],'match_id':m['match_id'],'p_over_9_5':p['probs'][PRIMARY],'actual_over_9_5':actual(m),'exp_sot_total':p['exp_h']+p['exp_a']})
        rates={s:sum(actual(x) for x in all_ms if int(x['season'])<int(s))/sum(int(x['season'])<int(s) for x in all_ms) for s in SCORED}
        for name,fn in [('base_rate',lambda m,p:rates[m['season']]),('naive_trailing_10',lambda m,p:p['naive_probs'][PRIMARY])]:
            for m,p in allrows['GZ']: w.writerow({'kind':'baseline','arm_or_baseline':name,'season':m['season'],'match_id':m['match_id'],'p_over_9_5':fn(m,p),'actual_over_9_5':actual(m),'exp_sot_total':p['exp_h']+p['exp_a']})
