"""
Data ingestion and preprocessing pipeline for NFL simulation.
"""

import pandas as pd


def load_data(filepath):
    df = pd.read_csv(filepath)
    # Basic validation: drop missing, filter columns
    df = df.dropna()
    df = df[["play_description", "yards", "team"]]
    return df


def preprocess(df):
    # Example: Standardize text, normalize values
    df["play_description"] = df["play_description"].str.lower()
    df["yards"] = df["yards"].clip(lower=0)
    return df


# Example usage:
# df = load_data("data/plays.csv")
# df = preprocess(df)
