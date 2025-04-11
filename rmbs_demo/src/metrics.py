#!/usr/bin/env python3
"""
metrics.py

Bond-level analytics: compute yield (IRR) and Weighted Average Life (WAL).
"""

import numpy as np


def calculate_yield(
    cashflows: np.ndarray, price: float, tolerance=1e-6, max_iter=100
) -> float:
    """
    Computes the monthly IRR that makes the NPV of 'cashflows' equal to 'price'.
    Returns an annualized yield.

    We use a simple bisection search in [0, 100%].
    """
    if price <= 0 or len(cashflows) == 0:
        return 0.0

    def npv(y):
        # y is monthly discount rate
        total = 0.0
        for i, cf in enumerate(cashflows, start=1):
            total += cf / ((1 + y) ** i)
        return total - price

    lower, upper = 0.0, 1.0
    for _ in range(max_iter):
        mid = (lower + upper) / 2
        val = npv(mid)
        if abs(val) < tolerance:
            break
        if val > 0:
            lower = mid
        else:
            upper = mid

    # 'mid' is monthly rate; annualize
    monthly_rate = (lower + upper) / 2
    annualized_rate = (1 + monthly_rate) ** 12 - 1
    return annualized_rate


def calculate_wal(cashflows: np.ndarray) -> float:
    """
    Weighted Average Life (WAL) = sum(t * CF_t) / sum(CF_t), where t is in years.
    """
    total_cf = cashflows.sum()
    if total_cf < 1e-9:
        return 0.0

    weighted_sum = 0.0
    for i, cf in enumerate(cashflows, start=1):
        months = i  # i is month index
        weighted_sum += (months / 12.0) * cf
    return weighted_sum / total_cf
