"""Run the five AUW dev harnesses only; virgin seasons are intentionally unread."""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for market, runner in (("goals", "run_g_au.py"), ("sot", "run_s_au.py"), ("corners", "run_c_au.py"), ("cards", "run_k_au.py"), ("total_shots", "run_t_au.py")):
    subprocess.run([sys.executable, runner], cwd=HERE / market, check=True)
