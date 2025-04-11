#!/usr/bin/env python3
"""
simulation.py

Performs the monthly simulation of all loans and the RMBS structure.
"""

import numpy as np
from typing import List, Dict
from src.loan_pool import Loan
from src.structuring import Tranche, allocate_waterfall
from src.risk_models import logistic_default_probability, simple_prepayment_probability


def calculate_monthly_payment(loan: Loan) -> float:
    """
    Standard mortgage amortization formula for fully amortizing loans:
    M = r * P / (1 - (1+r)^-n)
    where:
      - r is monthly interest rate
      - P is current principal
      - n is number of payments remaining
    """
    monthly_rate = loan.rate / 12.0
    months_left = loan.term_months - loan.age_months
    if months_left <= 0 or monthly_rate <= 0:
        # Edge cases: if no interest rate or no months left, no scheduled payment.
        return 0.0

    # M = (monthly_rate * principal) / (1 - (1 + monthly_rate)^(-months_left))
    denom = 1 - (1 + monthly_rate) ** (-months_left)
    if denom < 1e-12:
        return 0.0
    return monthly_rate * loan.principal / denom


def simulate_loan_month(
    loan: Loan, recovery_rate: float, base_pd_annual: float, base_cpr_annual: float
) -> Dict[str, float]:
    """
    Simulates one monthly period for a single loan:
      1) Compute scheduled payment (interest + principal).
      2) Check for default -> recover some fraction.
      3) If no default, check for prepayment (partial or full).
      4) Update loan's principal & age.
    Returns a dict of interest and principal paid this month (from this loan).
    """
    if not loan.is_active():
        return {"interest": 0.0, "principal": 0.0}

    # Scheduled Payment for a standard amortizing mortgage
    scheduled_payment = calculate_monthly_payment(loan)
    interest_portion = loan.principal * (loan.rate / 12.0)
    principal_portion = scheduled_payment - interest_portion
    if principal_portion < 0:
        # Safety check if interest_portion > scheduled_payment
        principal_portion = 0.0

    # Default Probability
    pd_monthly = logistic_default_probability(loan, base_pd_annual)

    # If default occurs
    if np.random.rand() < pd_monthly:
        # We recover only a fraction of the outstanding principal
        recovered = loan.principal * recovery_rate
        # Loan is now done
        loan.principal = 0.0
        loan.age_months += 1
        return {"interest": interest_portion, "principal": recovered}

    # If no default, apply scheduled payment first
    paid_interest = interest_portion
    paid_principal = principal_portion

    # Prepayment Probability
    ppay_monthly = simple_prepayment_probability(loan, base_cpr_annual)
    if np.random.rand() < ppay_monthly:
        # Full prepayment of whatever principal is left
        paid_principal += loan.principal - principal_portion

    # Apply the total principal to the loan
    loan.principal -= paid_principal
    if loan.principal < 1e-8:
        loan.principal = 0.0

    # Increment age
    loan.age_months += 1

    return {"interest": paid_interest, "principal": paid_principal}


def run_simulation(
    loans: List[Loan],
    tranches: List[Tranche],
    months: int = 360,
    recovery_rate: float = 0.60,
    base_pd_annual: float = 0.03,
    base_cpr_annual: float = 0.10,
) -> Dict[str, List[float]]:
    """
    Runs the multi-month simulation.
    Returns a dict of monthly CF arrays: { "Senior": [...], "Mezz": [...], "Equity": [...] }.
    """
    monthly_results = {t.name: [] for t in tranches}

    for m in range(months):
        # 1) If everything is paid off, we can end early
        if all((not ln.is_active()) for ln in loans) and all(
            t.outstanding_principal < 1e-8 for t in tranches
        ):
            break

        # 2) Simulate each loan for one month
        total_interest = 0.0
        total_principal = 0.0
        for ln in loans:
            perf = simulate_loan_month(
                ln, recovery_rate, base_pd_annual, base_cpr_annual
            )
            total_interest += perf["interest"]
            total_principal += perf["principal"]

        # 3) Allocate to tranches
        allocate_waterfall(total_interest, total_principal, tranches)

        # 4) Record monthly CF for each tranche
        for t in tranches:
            cf = t.interest_paid + t.principal_paid
            monthly_results[t.name].append(cf)
            t.cf_history.append(cf)

            # reset for next month
            t.interest_paid = 0.0
            t.principal_paid = 0.0

    return monthly_results
