import argparse
from harness import dev, virgin

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("dev", "virgin"), nargs="?", default="dev")
    args = p.parse_args()
    (dev if args.command == "dev" else virgin)()
