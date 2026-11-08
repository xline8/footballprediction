import argparse
import json
from pathlib import Path

from harness import run_dev


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dev")
    args = parser.parse_args()
    if args.cmd == "dev":
        result = run_dev()
        gate = result["dev_gate"]
        g = gate["gate_zero"]
        m = g["pooled_model"]; c = g["pooled_climatology"]
        b = result["ou25_base_rate_baseline"]
        if not g["passes"]:
            reason = ("Gate Zero failed the mechanical dev gate: pooled 1X2 LL "
                      f"{m['ll_1x2']:.12f} vs climatology {c['ll_1x2']:.12f}, "
                      f"RPS {m['rps']:.12f} vs climatology {c['rps']:.12f}, and "
                      f"OU2.5 LL {m['oull_2_5']:.12f} vs frozen base-rate LL "
                      f"{b['oull_2_5']:.12f}; the virgin was not read per the frozen rule.")
        else:
            reason = ("Gate Zero passed the mechanical dev gate; the virgin read is pending "
                      "in the separate virgin phase and was not performed by this run.")
        (Path(__file__).resolve().parent / "results_virgin.json").write_text(json.dumps({
            "virgin_read": False, "virgin_season": "2025", "reason": reason,
            "dev_gate": {a: gate[a]["passes"] for a in ("gate_zero", "shrink")}}, indent=2) + "\n")
        for arm, verdict in gate.items():
            print(arm, "PASS" if verdict["passes"] else "FAIL")


if __name__ == "__main__":
    main()
