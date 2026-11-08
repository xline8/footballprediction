"""The three preregistered goals arms."""
import math
from collections import defaultdict

def match_counts(games):
    c=defaultdict(int)
    for g in games: c[g["hi"]]+=1; c[g["ai"]]+=1
    return c

def adjusted_lambdas(model, home, away, arm, offsets=None, counts=None):
    ah,da,aa,dh=model.a[home],model.d[away],model.a[away],model.d[home]
    if arm=="shrink":
        ch=(counts or {}).get(home,0)/6; ca=(counts or {}).get(away,0)/6
        ah*=min(1,ch); dh*=min(1,ch); aa*=min(1,ca); da*=min(1,ca)
    if arm=="x2":
        oh,od=(offsets or {}).get(home,(0,0)); ah+=oh; dh+=od
        oh,od=(offsets or {}).get(away,(0,0)); aa+=oh; da+=od
    return math.exp(ah+da+model.h), math.exp(aa+dh)
