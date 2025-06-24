
# granger_test_runner.py

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests
import os

def run_granger_by_developer(df, cause_var, effect_var, dev_col='commenter', max_lag=3, min_months=4, alpha=0.05):
    results = []

    for dev_id, group in df.groupby(dev_col):
        if group.shape[0] < min_months:
            continue
        data = group[[effect_var, cause_var]].dropna()
        if len(data) <= max_lag + 1:
            continue
        try:
            gc_test = grangercausalitytests(data, maxlag=max_lag, verbose=False)
            for lag in range(1, max_lag + 1):
                p_val = gc_test[lag][0]["ssr_ftest"][1]
                results.append({
                    "developer": dev_id,
                    "lag": lag,
                    "p_value": p_val,
                    "significant": p_val < alpha,
                    "cause_var": cause_var,
                    "effect_var": effect_var
                })
        except Exception as e:
            continue

    return pd.DataFrame(results)

def summarize_granger_results(df_result, save_path=None):
    summary = (
        df_result[df_result["significant"]]
        .groupby("lag")
        .agg(significant_devs=("developer", "nunique"))
        .reset_index()
    )
    summary["total_devs"] = df_result.groupby("lag")["developer"].nunique().values
    summary["proportion"] = summary["significant_devs"] / summary["total_devs"]

    # Plot
    plt.figure(figsize=(7, 5))
    plt.bar(summary["lag"], summary["proportion"])
    plt.xlabel("Lag")
    plt.ylabel("Proportion of Developers with Significant Causality")
    plt.title("Granger-Causal Developer Proportion by Lag")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.close()

    return summary
