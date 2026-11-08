"""Frozen Gate Zero yellow-card count model."""
import math
from collections import defaultdict,deque
HL=270.; K_PRIOR=8.; K_REF=8.; FB_MU_H=2.15; FB_MU_A=1.95
class D:
    def __init__(s): s.x=s.w=0.; s.last=None
    def at(s,d):
        if s.last is not None and d>s.last: f=.5**((d-s.last)/HL); s.x*=f; s.w*=f
        s.last=d; return s.x,s.w
    def add(s,d,x): s.at(d); s.x+=x; s.w+=1
class T:
    def __init__(s): s.ah,s.dh,s.aa,s.da=D(),D(),D(),D()
class State:
    def __init__(s): s.t=defaultdict(T); s.h,s.a=D(),D()
    def means(s,d):
        h,wh=s.h.at(d); a,wa=s.a.at(d); return h/wh if wh and h>0 else FB_MU_H,a/wa if wa and a>0 else FB_MU_A
    def shr(s,x,d,mu): z,w=x.at(d); return (z+K_PRIOR*mu)/(w+K_PRIOR)
    def pred(s,h,a,d):
        mh,ma=s.means(d); th,ta=s.t[h],s.t[a]; return mh*s.shr(th.ah,d,mh)/mh*s.shr(ta.da,d,mh)/mh,ma*s.shr(ta.aa,d,ma)/ma*s.shr(th.dh,d,ma)/ma
    def update(s,h,a,d,yh,ya):
        th,ta=s.t[h],s.t[a]; th.ah.add(d,yh); th.dh.add(d,ya); ta.aa.add(d,ya); ta.da.add(d,yh); s.h.add(d,yh); s.a.add(d,ya)
    def snapshot(s,d):
        mh,ma=s.means(d); return {'league_mean_home':mh,'league_mean_away':ma,'teams':{str(k):{'att_home':s.shr(v.ah,d,mh),'def_home':s.shr(v.dh,d,ma),'att_away':s.shr(v.aa,d,ma),'def_away':s.shr(v.da,d,mh)} for k,v in s.t.items()}}
def nb_over(mu,r,line):
    k=int(math.floor(line)); q=mu/(r+mu); term=(r/(r+mu))**r; c=term
    for i in range(1,k+1): term*=(i-1+r)/i*q; c+=term
    return min(max(1-c,0),1)
def estimate_r(rows,key):
    num=sum(x[key]**2 for x in rows); den=sum((x['y']-x[key])**2-x[key] for x in rows); return 500. if den<=0 else min(max(num/den,2.),500.)
class Online:
    def __init__(s): s.state=State(); s.n=defaultdict(lambda:deque(maxlen=10))
    def prediction(s,r):
        eh,ea=s.state.pred(r['home_id'],r['away_id'],r['day']); mh,ma=s.state.means(r['day']); h,a=s.n[r['home_id']],s.n[r['away_id']]
        if h and a:
            hf,ha=sum(x[0] for x in h)/len(h),sum(x[1] for x in h)/len(h); af,aa=sum(x[0] for x in a)/len(a),sum(x[1] for x in a)/len(a); nh,na=(hf+aa)/2,(af+ha)/2
        else: nh,na=mh,ma
        return {'model':eh+ea,'base':mh+ma,'naive':nh+na,'eh':eh,'ea':ea}
    def update(s,r): s.state.update(r['home_id'],r['away_id'],r['day'],r['yh'],r['ya']); s.n[r['home_id']].append((r['yh'],r['ya'])); s.n[r['away_id']].append((r['ya'],r['yh']))
