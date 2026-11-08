import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from count_harness import run
def run_dev(): return run("total_shots",("A","B","C"))
