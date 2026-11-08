import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from market_runner import main
a = argparse.ArgumentParser(); a.add_argument('mode'); a.add_argument('--arms')
x = a.parse_args(); main('cards', x.mode, x.arms.split(',') if x.arms else None)
