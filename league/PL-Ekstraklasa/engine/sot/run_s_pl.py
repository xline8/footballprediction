#!/usr/bin/env python3
import argparse
from harness import run_dev

def main():
    p=argparse.ArgumentParser(); p.add_argument("command",choices=["dev"]); args=p.parse_args()
    run_dev()
if __name__=="__main__": main()
