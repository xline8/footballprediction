"""Prediction-time arm logic for G-COA."""
import math

def adjusted_lambdas(model, home, away, arm, home_mover_up=False, away_mover_up=False):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm == "x2":
        if home_mover_up: ah, dh = math.log(0.81), dh
        if away_mover_up: aa, da = math.log(0.81), da
        if home_mover_up: dh = math.log(1.18)
        if away_mover_up: da = math.log(1.18)
    elif arm != "gate_zero":
        raise ValueError(f"unknown arm: {arm}")
    return math.exp(ah + da + model.h), math.exp(aa + dh)
