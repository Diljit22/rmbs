#!/usr/bin/env python3
"""
visualization.py

Function to plot monthly cash flows by tranche.
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_tranche_cash_flows(monthly_results: dict):
    """
    Creates a stacked area plot of monthly cash flows for each tranche.
    monthly_results: {tranche_name: [cf1, cf2, ...], ...}
    """
    tranche_names = list(monthly_results.keys())
    arrays = [np.array(monthly_results[name]) for name in tranche_names]
    max_len = max(arr.shape[0] for arr in arrays)
    data_matrix = np.zeros((max_len, len(tranche_names)))

    for i, arr in enumerate(arrays):
        data_matrix[: arr.shape[0], i] = arr

    months = np.arange(max_len)
    plt.figure(figsize=(10, 6))
    plt.stackplot(months, data_matrix.T, labels=tranche_names)
    plt.xlabel("Month")
    plt.ylabel("Cash Flow")
    plt.title("Monthly Tranche Cash Flows")
    plt.legend()
    plt.tight_layout()
    plt.show()
