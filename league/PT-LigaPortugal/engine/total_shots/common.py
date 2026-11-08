import csv, math
from collections import defaultdict, deque
from datetime import date

SEASONS = ('2021/2022','2022/2023','2023/2024','2024/2025','2025/2026')
TARGETS = SEASONS[1:]

def f(x): return None if x in ('', None) else float(x)
def load(path, fields, seasons=SEASONS):
    out=[]
    with open(path, newline='', encoding='utf8') as fh:
        for x in csv.DictReader(fh):
            if x['season'] not in seasons: continue
            z={'match_id':x['match_id'],'season':x['season'],'date':date.fromisoformat(x['date']),
               'home_id':x['home_id'],'away_id':x['away_id'],'referee':x.get('referee','')}
            z.update({k:f(x.get(v,'')) for k,v in fields.items()})
            out.append(z)
    return sorted(out,key=lambda x:(x['date'],x['match_id']))

def w(cutoff,d,hl): return .5**((cutoff-d).days/hl)
weight = w
def clamp(x,a,b): return max(a,min(b,x))
def moment(vals):
    m=sum(vals)/len(vals); v=sum((x-m)**2 for x in vals)/len(vals)
    return clamp(m/(v/m-1),1.02,200) if m and v>m else 200.0
def nb_over(mu,r,line):
    if mu<=0: return 0.0
    k=int(math.floor(line)); shape=r
    q=mu/(shape+mu); p=(shape/(shape+mu))**shape; c=p
    for i in range(1,k+1): p*=((i-1+shape)/i)*q; c+=p
    return clamp(1-c,0,1)
def logloss(p,y):
    p=clamp(p,1e-12,1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))

def season_state(rows, season, hl, total_key, hkey=None, akey=None):
    idx=SEASONS.index(season); tr=[x for x in rows if SEASONS.index(x['season'])<idx]
    cutoff=min(x['date'] for x in rows if x['season']==season)
    ww=[w(cutoff,x['date'],hl) for x in tr]
    totals=[x[total_key] for x in tr]
    mu=sum(q*y for q,y in zip(ww,totals))/sum(ww); r=moment(totals)
    if hkey: bh=sum(q*x[hkey] for q,x in zip(ww,tr))/sum(ww); ba=sum(q*x[akey] for q,x in zip(ww,tr))/sum(ww)
    else: bh=ba=None
    return tr,cutoff,ww,mu,r,bh,ba

def naive(rows, target, total_h, total_a, base_mu):
    hist=defaultdict(lambda:deque(maxlen=10)); out={}; i=0
    rows=sorted(rows,key=lambda x:(x['date'],x['match_id']))
    while i<len(rows):
        j=i+1
        while j<len(rows) and rows[j]['date']==rows[i]['date']: j+=1
        for x in rows[i:j]:
            def means(t):
                q=hist[t]
                if len(q)<6: return base_mu/2,base_mu/2
                return sum(v[0] for v in q)/len(q),sum(v[1] for v in q)/len(q)
            hf,ha=means(x['home_id']); af,aa=means(x['away_id'])
            out[x['match_id']]=(hf+aa)/2+(af+ha)/2
        for x in rows[i:j]:
            hist[x['home_id']].append((x[total_h],x[total_a])); hist[x['away_id']].append((x[total_a],x[total_h]))
        i=j
    return out

def naive_bruteforce(rows, sample, total_h, total_a, base_mu):
    prior=[x for x in rows if (x['date'],x['match_id']) < (sample['date'],sample['match_id'])]
    # Explicitly omit every match on the sample date, matching the grouped updater.
    prior=[x for x in prior if x['date'] < sample['date']]
    hist=defaultdict(list)
    for x in prior:
        hist[x['home_id']].append((x[total_h],x[total_a]));hist[x['away_id']].append((x[total_a],x[total_h]))
    def m(t):
        q=hist[t][-10:]
        return (base_mu/2,base_mu/2) if len(q)<6 else (sum(v[0] for v in q)/len(q),sum(v[1] for v in q)/len(q))
    hf,ha=m(sample['home_id']);af,aa=m(sample['away_id']);return (hf+aa)/2+(af+ha)/2

def metrics(preds,line):
    n=len(preds); return {'n':n,'ll':sum(logloss(p,y) for p,y in preds)/n,'mean_p_over':sum(p for p,y in preds)/n,'actual_over':sum(y for p,y in preds)/n}
