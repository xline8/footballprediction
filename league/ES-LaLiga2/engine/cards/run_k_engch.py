import argparse
from harness import dev, virgin_metrics, predict
p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("dev"); q=s.add_parser("virgin"); q.add_argument("--arms",nargs="+",required=True,choices=("gate_zero","x8")); a=p.parse_args()
if a.cmd=="dev": dev()
else:
    dev=__import__("json").loads((__import__("pathlib").Path(__file__).resolve().parent/"results_dev.json").read_text())
    if not dev["arms"]["gate_zero"]["dev_gate_pass"]:
        (__import__("pathlib").Path(__file__).resolve().parent/"results_virgin.json").write_text(__import__("json").dumps({"virgin_read":False,"reason":"gate zero failed dev gate"},indent=2)+"\n")
        raise SystemExit(0)
    virgin_metrics(tuple(a.arms))
    result=__import__("json").loads((__import__("pathlib").Path(__file__).resolve().parent/"results_virgin.json").read_text())
    dev=__import__("json").loads((__import__("pathlib").Path(__file__).resolve().parent/"results_dev.json").read_text())
    eligible=[]; best_base=min([result["arms"][x]["metrics"]["base"]["4.5"]["ll"] for x in result["arms"]]+[result["arms"][x]["metrics"]["naive"]["4.5"]["ll"] for x in result["arms"]])
    for arm in a.arms:
        v=result["arms"][arm]; sign=True
        if v["metrics"]["model"]["4.5"]["ll"]<=best_base and abs(v["calibration"]["diff_4_5"])<=.01+v["calibration"]["se_4_5"] and sign: eligible.append(arm)
    if eligible:
        chosen=min(eligible,key=lambda x:(result["arms"][x]["metrics"]["model"]["4.5"]["ll"],0 if x=="gate_zero" else 1)); result["shipped_arm"]=chosen; predict(chosen)
    else:
        result["shipped_arm"]=None
    (__import__("pathlib").Path(__file__).resolve().parent/"results_virgin.json").write_text(__import__("json").dumps(result,indent=2)+"\n")
