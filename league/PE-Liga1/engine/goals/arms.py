"""Prediction-time arm logic for G-PE."""
import math

def adjusted_lambdas(model, home, away, arm, home_mover_up=False, away_mover_up=False):
    ah, da = model.a[home], model.d[away]; aa, dh = model.a[away], model.d[home]
    if arm == "x2":
        if home_mover_up: ah, dh = -0.0645, dh
        if away_mover_up: aa, da = -0.0645, da
        if home_mover_up: dh = 0.1024
        if away_mover_up: da = 0.1024
    elif arm != "gate_zero":
        raise ValueError(f"unknown arm: {arm}")
    return math.exp(ah + da + model.h), math.exp(aa + dh)
