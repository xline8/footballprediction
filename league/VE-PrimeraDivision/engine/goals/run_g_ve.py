import argparse
from harness import run_dev, run_virgin
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('step',choices=('dev','virgin')); a=p.parse_args(); d=run_dev()
    if a.step=='virgin': run_virgin(d)
