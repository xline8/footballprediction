import csv,json,math,os
from datetime import date
from model import Online,estimate_r,nb_over
DATA=os.path.join(os.path.dirname(__file__),'..','..','data','ve_matches.csv'); HERE=os.path.dirname(__file__); BLOCKS=('R1-7','R8-13'); PRIMARY=6.5
def load():
 out=[]
 for r in csv.DictReader(open(DATA,newline='',encoding='utf-8')):
  if r['phase']!='regular' or (r['season']=='2025' and r['stage']!='Clausura') or (r['season']=='2026' and r['stage']!='Apertura'): continue
  if r['season'] not in ('2025','2026'): continue
  yh=r['stats_yellow_home']; ya=r['stats_yellow_away']; y=None if yh=='' or ya=='' else int(float(yh))+int(float(ya)); rnd=int(float(r['round']))
  out.append({'match_id':r['match_id'],'season':r['season'],'block':'seed' if r['season']=='2025' else ('R1-7' if rnd<=7 else 'R8-13'),'day':date.fromisoformat(r['date']).toordinal(),'home_id':r['home_team_id'],'away_id':r['away_team_id'],'yh':None if y is None else int(float(yh)),'ya':None if y is None else int(float(ya)),'y':y})
 return sorted(out,key=lambda x:(x['day'],x['match_id']))
def ll(p,y): p=min(max(p,1e-12),1-1e-12); return -(y*math.log(p)+(1-y)*math.log(1-p))
def run_dev():
 rows=load(); assert not any(r['season']=='2026' and r['block'] not in BLOCKS for r in rows); e=Online(); warm=[]; scored=[]
 for r in rows:
  p=e.prediction(r,'gate_zero')
  if r['block'] in BLOCKS and r['y'] is not None: scored.append((r,p))
  elif r['block']=='seed' and r['y'] is not None: warm.append({'y':r['y'],'model':p['model'],'base':p['base'],'naive':p['naive']})
  if r['y'] is not None: e.update(r)
 rm={k:estimate_r(warm,k) for k in ('model','base','naive')}; out={'protocol':{'seed':'2025 Clausura regular','dev_blocks':list(BLOCKS),'virgin_not_loaded':True,'primary_line':PRIMARY},'arm':'gate_zero','r':rm,'blocks':{}}
 for b in BLOCKS:
  z=[(r,p) for r,p in scored if r['block']==b]; out['blocks'][b]={k:{'n':len(z),'ll':sum(ll(nb_over(p[k],rm[k],PRIMARY),int(r['y']>PRIMARY)) for r,p in z)/len(z)} for k in ('model','base','naive')}
 for b in BLOCKS:
  target=[r for r in rows if r['block']==b and r['y'] is not None]; cutoff=min(r['day'] for r in target); prior=[r for r in rows if r['day']<cutoff and r['y'] is not None]; q=sum(r['y'] for r in prior)/len(prior); out['blocks'][b]['base']['ll']=sum(ll(nb_over(q,rm['base'],PRIMARY),int(r['y']>PRIMARY)) for r in target)/len(target)
 out['pooled']={k:{'n':len(scored),'ll':sum(ll(nb_over(p[k],rm[k],PRIMARY),int(r['y']>PRIMARY)) for r,p in scored)/len(scored)} for k in ('model','base','naive')}; out['pooled']['base']['ll']=sum(out['blocks'][b]['base']['ll']*out['blocks'][b]['base']['n'] for b in BLOCKS)/len(scored); out['dev_pass']=out['pooled']['model']['ll']<out['pooled']['base']['ll'] and out['pooled']['model']['ll']<out['pooled']['naive']['ll']; json.dump(out,open(os.path.join(HERE,'results_dev.json'),'w'),indent=2); print(json.dumps(out,indent=2)); return out
if __name__=='__main__': run_dev()
