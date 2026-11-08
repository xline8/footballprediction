"""Gate arithmetic. Calibration is predicted minus actual."""
import math
def log_loss(p,y):
    p=min(1-1e-12,max(1e-12,float(p)))
    return -(float(y)*math.log(p)+(1-float(y))*math.log1p(-p))
def calibration(p_list,y_list):
    d=[float(p)-float(y) for p,y in zip(p_list,y_list)]; n=len(d)
    if not n: return (None,None)
    mean=sum(d)/n
    se=(math.sqrt(sum((x-mean)**2 for x in d)/(n-1))/math.sqrt(n)) if n>1 else None
    return mean*100, None if se is None else se*100
def pooled_ll(season_rows):
    vals=[(r.get('ll',r.get('value')),r.get('n')) for r in season_rows]
    vals=[(float(v),int(n)) for v,n in vals if v is not None and n]
    return None if not vals else sum(v*n for v,n in vals)/sum(n for _,n in vals)
def calibration_band(diff_pp,se_pp,tol_pp=1.0):
    if diff_pp is None: return 'FAIL'
    if abs(diff_pp)<=tol_pp: return 'PASS'
    if se_pp is not None and abs(diff_pp)<=tol_pp+se_pp: return 'PROVISIONAL'
    return 'FAIL'
def sign_check(per_season_ll_arm,per_season_ll_ref):
    pairs=[(a,b) for a,b in zip(per_season_ll_arm,per_season_ll_ref) if a is not None and b is not None]
    wins=sum(a<=b for a,b in pairs); n=len(pairs)
    return wins,n,wins >= math.ceil(n/2) if n else False
