import argparse
import json
from pathlib import Path

from harness import dev, gate_passes, virgin, write_predictions

parser = argparse.ArgumentParser()
parser.add_argument("command", choices=("dev", "virgin"))
args = parser.parse_args()
here = Path(__file__).resolve().parent

if args.command == "dev":
    dev()
else:
    dev_result = json.loads((here / "results_dev.json").read_text())
    gates = gate_passes(dev_result)
    print("dev gate:", gates)
    if not gates["gate_zero"]:
        out = {"virgin_read": False, "reason": "gate zero failed dev gate"}
        (here / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    else:
        arms = tuple(arm for arm in ("gate_zero", "x7") if gates[arm])
        result, target = virgin(arms, dev_result)
        base = min(result["league_base_rate"]["ll_9.5"], result["naive_trailing_10"]["ll_9.5"])
        legs = {"dev_gate": gates, "arms": {}}
        dev_seasons = ("2022 - Apertura", "2022 - Clausura", "2023 - Apertura", "2023 - Clausura", "2024 - Apertura", "2024 - Clausura")
        for arm in arms:
            r = result[arm]
            leg_i = r["ll_9.5"] <= result["gate_zero"]["ll_9.5"] and r["ll_9.5"] <= base
            clean = abs(r["calibration_diff"]) <= 0.01
            provisional = abs(r["calibration_diff"]) <= 0.01 + r["calibration_se"]
            sign = arm == "gate_zero" or sum(
                next(x for x in dev_result if x["arm"] == "x7" and x["season"] == season and x["kind"] == "model")["ll_9.5"]
                <= next(x for x in dev_result if x["arm"] == "gate_zero" and x["season"] == season and x["kind"] == "model")["ll_9.5"]
                for season in dev_seasons
            ) >= 3
            legs["arms"][arm] = {
                "dev": gates[arm], "i": leg_i, "ii": provisional,
                "ii_status": "clean" if clean else ("provisional" if provisional else "fail"),
                "iii": sign,
            }
        eligible = [arm for arm, leg in legs["arms"].items() if all(leg[key] for key in ("dev", "i", "ii", "iii"))]
        ship = min(eligible, key=lambda arm: (result[arm]["ll_9.5"], arm != "gate_zero")) if eligible else None
        out = {**result, "verdict": "PASS" if ship else "FAIL", "shipped_arm": ship, "legs": legs}
        (here / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
        if ship:
            write_predictions(ship, target, result[ship]["params"])
            (here / "fitted_params_virgin.json").write_text(json.dumps({"arm": ship, "params": result[ship]["params"]}, indent=2) + "\n")
        else:
            (here / "fitted_params_virgin.json").write_text(json.dumps({"virgin_read": True, "shipped_arm": None}, indent=2) + "\n")
