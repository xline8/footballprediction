import argparse
from harness import run_dev

def main():
    p=argparse.ArgumentParser(); p.add_argument("--dev",action="store_true",required=True)
    a=p.parse_args(); run_dev()
if __name__ == "__main__": main()
