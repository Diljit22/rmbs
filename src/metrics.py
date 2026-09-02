"""
src/metrics.py

Bond-level analytics: computes Yield (IRR) and Weighted Average Life (WAL).
"""

import numpy as np


def calculate_yield(
    cashflows: np.ndarray, price: float, tolerance: float = 1e-7, max_iter: int = 150
) -> float:
    """
    Computes the monthly IRR that equates the NPV of cashflows to the initial price.
    Returns an annualized yield. Supports negative yields.
    """
    if price <= 0.0 or len(cashflows) == 0 or np.sum(cashflows) < 1e-9:
        return 0.0

    cfs = np.asarray(cashflows)
    times = np.arange(1, len(cfs) + 1)

    def get_npv(r_monthly: float) -> float:
        # Guard to prevent division by zero or overflows over 360+ periods
        base = np.maximum(1.0 + r_monthly, 0.01)
        return np.sum(cfs / (base ** times)) - price

    # A monthly rate of -20% is equivalent to -93% annualized return
    lower, upper = -0.20, 5.0

    npv_lower = get_npv(lower)
    npv_upper = get_npv(upper)

    if npv_lower * npv_upper > 0:
        if npv_lower < 0:
            return -1.0
        else:
            return 5.0

    for _ in range(max_iter):
        mid = (lower + upper) / 2.0
        val = get_npv(mid)
        if abs(val) < tolerance:
            break
        if val > 0.0:
            lower = mid
        else:
            upper = mid

    monthly_rate = (lower + upper) / 2.0
    return (1.0 + monthly_rate) ** 12 - 1.0


def calculate_wal(cashflows: np.ndarray) -> float:
    """
    Weighted Average Life (WAL) = sum(t * CF_t) / sum(CF_t) where t is in years.
    Utilizes vectorized operations for performance.
    """
    total_cf = np.sum(cashflows)
    if total_cf < 1e-9:
        return 0.0

    months = np.arange(1, len(cashflows) + 1)
    weighted_sum = np.sum((months / 12.0) * cashflows)
    return float(weighted_sum / total_cf)
