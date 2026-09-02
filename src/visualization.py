"""
src/visualization.py

Function to plot monthly cash flows by tranche.
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_tranche_cash_flows(monthly_results: dict) -> None:
    """
    Creates a stacked area plot of monthly cash flows for each tranche.
    """
    tranche_names = list(monthly_results.keys())
    arrays = [np.array(monthly_results[name]) for name in tranche_names]
    max_len = max(arr.shape[0] for arr in arrays)
    data_matrix = np.zeros((max_len, len(tranche_names)))

    for i, arr in enumerate(arrays):
        data_matrix[: arr.shape[0], i] = arr

    months = np.arange(max_len)
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.stackplot(
        months, data_matrix.T, labels=tranche_names, alpha=0.85, edgecolor="white"
    )

    ax.set_xlabel("Month", fontsize=11, fontweight="semibold")
    ax.set_ylabel("Cash Flow ($)", fontsize=11, fontweight="semibold")
    ax.set_title("Tranche Monthly Cash Flow Distribution", fontsize=13, pad=15)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="none")

    plt.tight_layout()
    plt.show()
