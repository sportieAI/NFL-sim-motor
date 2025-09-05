"""
Causal Inference Example with DoWhy

Test causal effects within the simulation dataset.
"""

import dowhy
from dowhy import CausalModel

def run_causal_inference(df, treatment, outcome):
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=['team_strength', 'weather', 'home_field']
    )
    identified_estimand = model.identify_effect()
    estimate = model.estimate_effect(identified_estimand, method_name="backdoor.propensity_score_matching")
    print(estimate)
    return estimate
