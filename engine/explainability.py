"""
Explainable AI Integration Example

Uses SHAP or LIME to explain model predictions in the simulation.
"""

import shap


def explain_prediction(model, data):
    explainer = shap.Explainer(model)
    shap_values = explainer(data)
    shap.summary_plot(shap_values, data)
