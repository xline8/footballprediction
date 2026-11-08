import argparse, json
from harness import dev
p=argparse.ArgumentParser(); p.add_argument("command", choices=("dev",)); a=p.parse_args(); dev()
