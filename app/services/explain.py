"""Deterministic explanations for the additive five-factor scoring model."""
def exact_shapley(dimensions:dict[str,float],weights:dict[str,float],baseline:float=50)->dict[str,float]:
 return {name:round(weights[name]*(value-baseline),4) for name,value in dimensions.items() if name in weights}
