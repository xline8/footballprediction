import argparse, json
from pathlib import Path
from harness import dev, gate_passes, virgin, write_predictions, BLOCKS

p = argparse.ArgumentParser()
s = p.add_subparsers(dest="cmd", required=True)
s.add_parser("dev")
s.add_parser("virgin")
a = p.parse_args()
here = Path(__file__).resolve().parent
if a.cmd == "dev":
    dev()
else:
    dev_result = json.loads((here / "results_dev.json").read_text())
    gates = gate_passes(dev_result)
    print("dev gate:", gates)
    if not gates["gate_zero"]:
        out = {"verdict": "FAIL", "shipped_arm": None, "legs": {"dev_gate": gates, "virgin_read": False}}
        (here / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    else:
        arms = tuple(x for x in ("gate_zero", "x7") if gates[x])
        result, target = virgin(arms, dev_result)
        base = min(result["league_base_rate"]["ll_9.5"], result["naive_trailing_10"]["ll_9.5"])
        legs = {"dev_gate": gates, "arms": {}}
        for arm in arms:
            r = result[arm]
            i = r["ll_9.5"] <= result["gate_zero"]["ll_9.5"] and r["ll_9.5"] <= base
            ii = abs(r["calibration_diff"]) <= .01 + r["calibration_se"]
            sign = arm == "gate_zero" or sum(next(x for x in dev_result if x["arm"] == "x7" and x["block"] == b and x["kind"] == "model")["ll_9.5"] <= next(x for x in dev_result if x["arm"] == "gate_zero" and x["block"] == b and x["kind"] == "model")["ll_9.5"] for b in BLOCKS) >= 2
            legs["arms"][arm] = {"dev": gates[arm], "i": i, "ii": ii, "iii": sign, "calibration_status": "PASS" if abs(r["calibration_diff"]) <= .01 else ("PROVISIONAL" if ii else "FAIL")}
        eligible = [x for x, l in legs["arms"].items() if all(l[k] for k in ("dev", "i", "ii", "iii"))]
        ship = min(eligible, key=lambda x: (result[x]["ll_9.5"], x != "gate_zero")) if eligible else None
        out = {**result, "verdict": "PASS" if ship else "FAIL", "shipped_arm": ship, "legs": legs}
        (here / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
        if ship:
            write_predictions(ship, target, result[ship]["params"])
