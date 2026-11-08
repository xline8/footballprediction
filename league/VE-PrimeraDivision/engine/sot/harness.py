import json, math, os
from model import Engine, load_matches, NB_R, LINES
DATA=os.path.join(os.path.dirname(__file__),'..','..','data','ve_matches.csv'); HERE=os.path.dirname(__file__); BLOCKS=('R1-7','R8-13'); PRIMARY=8.5
def ll(p,y): p=min(max(p,1e-12),1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def actual(m): return int(m['sot_h']+m['sot_a']>PRIMARY)
def metric(rows):
 return {'n':len(rows),'ll':sum(ll(p['probs'][PRIMARY],actual(m)) for m,p in rows)/len(rows),'lines':{str(L):sum(ll(p['probs'][L],int(m['sot_h']+m['sot_a']>L)) for m,p in rows)/len(rows) for L in LINES}}
def run_dev():
 ms=load_matches(DATA,{'2025','2026'}); assert not any(m['season']=='2026' and m['block'] not in BLOCKS for m in ms)
 out={'protocol':{'seed':'2025 Clausura regular','dev_blocks':list(BLOCKS),'virgin_not_loaded':True,'primary_line':PRIMARY},'arms':{},'baselines':{}}
 for arm in ('GZ','RS'):
  e=Engine(ms,arm); rows=[]
  for m in ms:
   if m['block'] in BLOCKS: rows.append((m,e.predict(m)))
   e.update(m)
  out['arms'][arm]={'blocks':{},'pooled':metric(rows)}
  for b in BLOCKS: out['arms'][arm]['blocks'][b]=metric([(m,p) for m,p in rows if m['block']==b])
 gz=[]
 # Re-run once to capture the reference naive predictions and chronological base rates.
 e=Engine(ms,'GZ'); rows=[]
 for m in ms:
  if m['block'] in BLOCKS: rows.append((m,e.predict(m)))
  e.update(m)
 base=[]; naive=[]
 for m,p in rows:
  block_rows=[x for x in ms if x['block']==m['block']]; cutoff=min(x['date'] for x in block_rows); prior=[x for x in ms if x['date']<cutoff]; q=sum(actual(x) for x in prior)/len(prior)
  base.append((m,q)); naive.append((m,p['naive_probs'][PRIMARY]))
 out['baselines']={'league_base_rate':{'ll':sum(ll(q,actual(m)) for m,q in base)/len(base),'n':len(base),'blocks':{b:{'n':sum(m['block']==b for m,q in base),'ll':sum(ll(q,actual(m)) for m,q in base if m['block']==b)/sum(m['block']==b for m,q in base)} for b in BLOCKS}},'naive':{'ll':sum(ll(q,actual(m)) for m,q in naive)/len(naive),'n':len(naive),'blocks':{b:{'n':sum(m['block']==b for m,q in naive),'ll':sum(ll(q,actual(m)) for m,q in naive if m['block']==b)/sum(m['block']==b for m,q in naive)} for b in BLOCKS}}}
 out['dev_pass']={a:out['arms'][a]['pooled']['ll']<out['baselines']['league_base_rate']['ll'] and out['arms'][a]['pooled']['ll']<out['baselines']['naive']['ll'] for a in ('GZ','RS')}
 json.dump(out,open(os.path.join(HERE,'results_dev.json'),'w'),indent=2); print(json.dumps(out,indent=2)); return out
if __name__=='__main__': run_dev()
