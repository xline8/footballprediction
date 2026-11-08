import re
from dataclasses import dataclass, field
from pathlib import Path
@dataclass
class PreregSpec:
    primary_line:float=None; ladder:list=field(default_factory=list); calibration_tolerance_pp:float=None
    calibration_raw:str=None; sign_convention_stated:str=None; baselines:list=field(default_factory=list)
    virgin_season:str=None; gate_text:str=None; missing_tokens:list=field(default_factory=list)
def load_config(path):
    out={}; section=None
    try: lines=Path(path).read_text().splitlines()
    except OSError: return out
    for line in lines:
        s=line.split('#',1)[0].strip()
        if not s: continue
        if s.endswith(':') and not s.startswith('-'): section=s[:-1]; continue
        m=re.match(r'([\w-]+)\s*:\s*["\']?([^"\']+?)["\']?\s*$',s)
        if m:
            k,v=m.groups(); v=v.strip()
            try: v=float(v) if re.fullmatch(r'-?\d+(?:\.\d+)?',v) else v
            except ValueError: pass
            out[k]=v; out[f'{section}.{k}']=v if section else v
            if section=='halves_constants': out.setdefault('halves_constants',{})[k]=v
    if 'virgin_primary' not in out:
        for k,v in out.items():
            if k.endswith('.virgin_primary'): out['virgin_primary']=v
    return out
def parse_prereg(path):
    text=Path(path).read_text(encoding='utf-8'); s=PreregSpec()
    primary_patterns=[r'Primary line\s*:?\s*[*`_]*(?:OU)?([0-9]+(?:\.5|\.0|\.\d+)?)',r'primary line[^\n]*?(?:OU)?([0-9]+\.5)']
    for pat in primary_patterns:
        m=re.search(pat,text,re.I)
        if m: s.primary_line=float(m.group(1)); break
    if s.primary_line is None: s.missing_tokens.append('primary_line')
    near=text[max(0,(m.start()-100 if 'm' in locals() and m else 0)): (m.end()+250 if 'm' in locals() and m else 400)]
    lm=re.search(r'(?:Ladder|ladder)[^\n]*?((?:\d+\.5\s*/\s*)+\d+\.5)',near)
    if not lm: lm=re.search(r'((?:\d+\.5\s*/\s*)+\d+\.5)',near)
    if lm: s.ladder=[float(x) for x in re.findall(r'\d+\.5',lm.group(1))]
    cal=re.search(r'((?:≤|<=|less than or equal to)?\s*1\.0\s*pp)',text,re.I)
    if cal: s.calibration_tolerance_pp=1.0; s.calibration_raw=cal.group(1)
    else: s.missing_tokens.append('calibration_tolerance_pp')
    if re.search(r'predicted\s*(?:−|-|minus)\s*actual',text,re.I): s.sign_convention_stated='predicted_minus_actual'
    elif re.search(r'actual\s*(?:−|-|minus)\s*predicted',text,re.I): s.sign_convention_stated='actual_minus_predicted'
    else: s.missing_tokens.append('sign_convention_stated')
    for label in ('league base rate','climatology','naive trailing-10'):
        if re.search(re.escape(label),text,re.I): s.baselines.append(label)
    gm=re.search(r'GATE LEGS.*?(?=\n##|\n#|\Z)',text,re.I|re.S); s.gate_text=gm.group(0) if gm else None
    if s.gate_text is None: s.missing_tokens.append('gate_text')
    cm=re.search(r'virgin_primary\s*:\s*([\w./-]+)',text)
    if cm: s.virgin_season=cm.group(1)
    else:
        cfg=Path(path).parents[1]/'config.yaml'; c=load_config(cfg)
        s.virgin_season=c.get('virgin_primary')
    return s
