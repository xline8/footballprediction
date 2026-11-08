from harness import dev, virgin, gate_passes

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("dev"); s.add_parser("virgin"); a=p.parse_args()
    if a.cmd == "dev": dev()
    else:
        d=dev(); arms=tuple(x for x,v in gate_passes(d).items() if v)
        if arms: virgin(arms,d)
