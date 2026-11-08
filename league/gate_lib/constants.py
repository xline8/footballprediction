from dataclasses import dataclass
from statistics import mean
@dataclass
class Finding: league:str; name:str; severity:str; message:str
@dataclass
class CandidateSpec: league:str; candidate:str; constants:dict
def derive_level_prior(values): return mean(values)
def derive_half_share(first_half,full_time): return sum(first_half)/sum(full_time)
def check_constants(spec,other_specs):
    out=[]
    for name,item in spec.constants.items():
        val=item.get('value') if isinstance(item,dict) else item
        deriv=item.get('derivation') if isinstance(item,dict) else None
        if deriv is None: out.append(Finding(spec.league,name,'WARNING','constant has no derivation record'))
        for other in other_specs:
            oi=other.constants.get(name)
            oval=oi.get('value') if isinstance(oi,dict) else oi
            if oval==val and other.league!=spec.league and deriv is None:
                out.append(Finding(spec.league,name,'ERROR',f'exactly equals {other.league} without derivation'))
    return out
