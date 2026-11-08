"""Fail-closed access to sealed rows."""
import csv, json, hashlib
from datetime import datetime, timezone

class SealedAccessError(RuntimeError): pass

class DevPassRegistry:
    def __init__(self, path):
        self.path = path
        try:
            with open(path, encoding='utf-8') as f: self.tokens = json.load(f)
            if not isinstance(self.tokens, dict): raise ValueError('registry is not an object')
        except Exception as e: raise SealedAccessError('unreadable dev-pass registry') from e
    def has_pass(self, candidate_id):
        return self.tokens.get(candidate_id, {}).get('dev_pass') is True

def record_dev_pass(registry_path, candidate_id, dev_pass, evidence):
    try:
        try:
            with open(registry_path, encoding='utf-8') as f: data=json.load(f)
        except FileNotFoundError: data={}
        if not isinstance(data, dict): raise ValueError('registry is not an object')
        ev = evidence if isinstance(evidence, str) else json.dumps(evidence, sort_keys=True)
        item={'dev_pass': dev_pass is True, 'recorded_at': datetime.now(timezone.utc).isoformat()}
        if isinstance(evidence, str) and __import__('os').path.exists(evidence): item['source_path']=evidence
        else: item['dev_results_sha256']=hashlib.sha256(ev.encode()).hexdigest()
        data[candidate_id]=item
        with open(registry_path,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,sort_keys=True)
    except Exception as e: raise SealedAccessError('could not record dev pass') from e

def load_sealed_rows(csv_path, candidate_id, registry_path, virgin_season=None):
    reg=DevPassRegistry(registry_path)
    if candidate_id not in reg.tokens: raise SealedAccessError('candidate has no dev-pass token')
    if reg.tokens[candidate_id].get('dev_pass') is not True: raise SealedAccessError('dev pass is not exactly True')
    try:
        with open(csv_path, newline='', encoding='utf-8') as f: rows=list(csv.DictReader(f))
    except Exception as e: raise SealedAccessError('sealed CSV unreadable') from e
    if virgin_season is not None: assert_no_sealed_rows(rows, {virgin_season})
    return rows

def assert_no_sealed_rows(rows, sealed_seasons):
    sealed={str(x) for x in sealed_seasons}
    for row in rows:
        season=next((row.get(k) for k in ('season','Season','season_id') if row.get(k) is not None), None)
        if season is not None and str(season) in sealed: raise SealedAccessError('sealed row found in dev loader')
    return True
