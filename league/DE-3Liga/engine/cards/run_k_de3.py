from harness import dev, virgin_metrics, predict
import argparse, json
from pathlib import Path

p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("dev"); s.add_parser("virgin"); a=p.parse_args()
if a.cmd=="dev": dev()
else:
    d=dev(); arms=tuple(x for x,v in d["arms"].items() if v.get("dev_gate_pass"))
    if arms:
        virgin_metrics(arms)
        result=json.loads((Path(__file__).resolve().parent/"results_virgin.json").read_text())
        # Match the frozen virgin gate, including the variant season sign check.
        best_base=min(result["arms"][x]["metrics"]["base"]["4.5"]["ll"] for x in result["arms"])
        gzll=result["arms"].get("gate_zero", result["arms"][arms[0]])["metrics"]["model"]["4.5"]["ll"]
        eligible=[]
        for x,v in result["arms"].items():
            sign=x=="gate_zero" or sum(d["arms"][x]["seasons"][s]["model"]["4.5"]["ll"]<=d["arms"]["gate_zero"]["seasons"][s]["model"]["4.5"]["ll"] for s in ("2022/2023","2023/2024","2024/2025"))>=2
            if v["metrics"]["model"]["4.5"]["ll"]<=gzll and v["metrics"]["model"]["4.5"]["ll"]<=best_base and abs(v["calibration"]["diff_4_5"])<=.01+v["calibration"]["se_4_5"] and sign: eligible.append(x)
        result["shipped_arm"]=min(eligible,key=lambda x:(result["arms"][x]["metrics"]["model"]["4.5"]["ll"],0 if x=="gate_zero" else 1)) if eligible else None
        if result["shipped_arm"]: predict(result["shipped_arm"])
        (Path(__file__).resolve().parent/"results_virgin.json").write_text(json.dumps(result,indent=2)+"\n")
