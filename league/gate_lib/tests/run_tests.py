import csv, json, tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[2].parent))
from league.gate_lib import *
root=Path(__file__).parents[3]
with tempfile.TemporaryDirectory() as d:
 p=Path(d); c=p/'x.csv'; c.write_text('season,value\n2026,1\n')
 try: load_sealed_rows(c,'x',p/'r.json')
 except SealedAccessError: pass
 else: raise AssertionError('unguarded read')
 record_dev_pass(p/'r.json','x',True,'results')
 assert load_sealed_rows(c,'x',p/'r.json')
 assert calibration([.6,.6],[0,0])==(60.0,0.0)
 assert parse_prereg(root/'league/J1/prereg/PREREG_T_J1.md').primary_line==24.5
 assert parse_prereg(root/'league/J1/prereg/PREREG_K_J1.md').primary_line==2.5
 assert parse_prereg(root/'league/AE-ProLeague/prereg/PREREG_K_AE.md').primary_line==3.5
 a=CandidateSpec('A','a',{'M_BAR':{'value':24.9}}); b=CandidateSpec('B','b',{'M_BAR':{'value':24.9}})
 assert any(x.severity=='ERROR' for x in check_constants(a,[b]))
 a.constants['M_BAR']['derivation']={'method':'mean','source':'dev','n':2}
 assert not any(x.severity=='ERROR' for x in check_constants(a,[b]))
print('gate_lib tests: PASS')
