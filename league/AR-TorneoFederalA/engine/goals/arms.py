"""G-FEDA Gate Zero and X2 newcomer adjustment."""
import math

GF_GAP, GA_GAP = 0.05535, 0.00444

def newcomer_ids(target, prior):
    current={x for r in target for x in (r["hi"],r["ai"])}
    previous={x for r in prior for x in (r["hi"],r["ai"])}
    return current - previous

def adjusted_lambdas(model, home, away, arm, newcomers):
    ah,da=model.a[home],model.d[away]; aa,dh=model.a[away],model.d[home]
    offsets={}
    if arm == "x2":
        for team in (home, away):
            if team in newcomers:
                att=math.log(max(model.mu+GF_GAP,0.10)/model.mu)
                deff=math.log(max(model.mu+GA_GAP,0.10)/model.mu)
                offsets[team]={"attack":att,"defence":deff}
                if team == home: ah += att; dh += deff
                else: aa += att; da += deff
    return (math.exp(ah+da+model.h), math.exp(aa+dh)), offsets
