#!/usr/bin/env python3
"""
risk_models.py

Implements default and prepayment probability functions.
"""

import math
from src.loan_pool import Loan


def logistic_default_probability(
    loan: Loan,
    base_pd_annual: float = 0.03,
    fico_weight: float = -0.002,
    ltv_weight: float = 0.01,
) -> float:
    """
    Approximate logistic default model using base PD, FICO, and LTV.

    If base_pd_annual is zero or negative, the function returns 0
    to avoid division by zero.
    """
    if base_pd_annual <= 0.0:
        return 0.0
    if base_pd_annual >= 1.0:
        return 1.0

    # Convert base PD to logistic intercept
    # intercept = -log(1/base_pd - 1)
    intercept = -math.log((1 / base_pd_annual) - 1 + 1e-9)

    fico_diff = loan.fico - 680  # reference FICO
    ltv_diff_percent = (loan.ltv - 0.8) * 100.0  # difference in percentage points

    z = intercept + (fico_weight * fico_diff) + (ltv_weight * ltv_diff_percent)
    pd_annual = 1.0 / (1.0 + math.exp(-z))

    # Convert annual PD to monthly PD
    pd_monthly = 1 - (1 - pd_annual) ** (1 / 12)
    return max(min(pd_monthly, 1.0), 0.0)


def simple_prepayment_probability(loan: Loan, base_cpr_annual: float = 0.10) -> float:
    """
    Simple monthly prepayment probability from an annual CPR.
    """
    monthly_cpr = 1 - (1 - base_cpr_annual) ** (1 / 12)
    return max(min(monthly_cpr, 1.0), 0.0)
