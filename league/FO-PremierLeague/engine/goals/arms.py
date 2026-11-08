"""The two preregistered G-FO arms."""
def adjusted_lambdas(model, hi, ai, arm):
    if arm == "gate_zero": return model.lambdas(hi, ai)
    if arm != "shrink": raise ValueError(arm)
    import math
    return (math.exp(.85*model.a[hi] + .85*model.d[ai] + model.h),
            math.exp(.85*model.a[ai] + .85*model.d[hi]))
