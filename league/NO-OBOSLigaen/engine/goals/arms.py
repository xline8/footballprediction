"""NO-OBOS goals arm adjustments."""
import math

def transition_offset(obos, elites, cutoff_season):
    ob={}; es={}
    for g in obos: ob.setdefault(g['season'],[]).append(g)
    for g in elites: es.setdefault(g['season'],[]).append(g)
    ta=td=tn=0.0
    for s,games in ob.items():
        if int(s)>=int(cutoff_season): continue
        prior={t for g in es.get(str(int(s)-1),[]) for t in (g['hi'],g['ai'])}
        entrants=prior & {t for g in games for t in (g['hi'],g['ai'])}
        mu=sum(g['yh']+g['ya'] for g in games)/(2*len(games))
        for t in entrants:
            gs=[g for g in games if t in (g['hi'],g['ai'])]
            ta += sum(g['yh'] if g['hi']==t else g['ya'] for g in gs)-len(gs)*mu
            td += sum(g['ya'] if g['hi']==t else g['yh'] for g in gs)-len(gs)*mu
            tn += len(gs)
    entrants=({t for g in ob.get(str(cutoff_season),[]) for t in (g['hi'],g['ai'])} & {t for g in es.get(str(int(cutoff_season)-1),[]) for t in (g['hi'],g['ai'])})
    return (ta/tn if tn else 0.0,td/tn if tn else 0.0,tn,entrants)

def adjusted_lambdas(model,home,away,arm,counts,offset):
    lh,la=model.lambdas(home,away)
    if arm in ('shr','x2'):
        if counts.get(home,0)<8: lh=.5*lh+.5*model.mu
        if counts.get(away,0)<8: la=.5*la+.5*model.mu
    if arm=='x2' and model.mu>0:
        da,dd,_,entrants=offset; ma=min(2,max(.5,(model.mu+da)/model.mu)); md=min(2,max(.5,(model.mu+dd)/model.mu))
        if home in entrants: lh*=ma; la*=md
        if away in entrants: la*=ma; lh*=md
    return lh,la
