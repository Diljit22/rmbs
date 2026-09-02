"""
src/simulation.py

Runs multi-month loan-level cash flow calculations using modular risk models.
"""

import copy
from typing import Dict, List
import numpy as np
from src.loan_pool import Loan
from src.risk_models import DefaultModel, PrepaymentModel
from src.structuring import Tranche, allocate_waterfall


def calculate_monthly_payment(loan: Loan) -> float:
    monthly_rate = loan.rate / 12.0
    months_left = loan.term_months - loan.age_months
    if months_left <= 0 or monthly_rate <= 0:
        return 0.0

    denom = 1.0 - (1.0 + monthly_rate) ** (-months_left)
    if denom < 1e-12:
        return 0.0
    return monthly_rate * loan.principal / denom


def simulate_loan_month(
    loan: Loan,
    recovery_rate: float,
    default_model: DefaultModel,
    prepayment_model: PrepaymentModel,
    rng: np.random.Generator,
) -> Dict[str, float]:
    """
    Simulates one monthly period for a single loan, evaluating default and prepayment hazards.
    """
    if not loan.is_active():
        return {"interest": 0.0, "principal": 0.0}

    scheduled_payment = calculate_monthly_payment(loan)
    interest_portion = loan.principal * (loan.rate / 12.0)
    principal_portion = max(0.0, scheduled_payment - interest_portion)

    # 1. Default Check
    pd_monthly = default_model.calculate_monthly_rate(loan)
    if rng.random() < pd_monthly:
        recovered = loan.principal * recovery_rate
        loan.principal = 0.0
        loan.age_months += 1
        return {"interest": 0.0, "principal": recovered}

    # 2. Amortization Check
    paid_interest = interest_portion
    paid_principal = min(loan.principal, principal_portion)

    # 3. Prepayment Check
    ppay_monthly = prepayment_model.calculate_monthly_rate(loan)
    if rng.random() < ppay_monthly:
        remaining_balance = loan.principal - paid_principal
        paid_principal += remaining_balance

    loan.principal = max(0.0, loan.principal - paid_principal)
    loan.age_months += 1

    return {"interest": paid_interest, "principal": paid_principal}


def run_simulation(
    loans: List[Loan],
    tranches: List[Tranche],
    default_model: DefaultModel,
    prepayment_model: PrepaymentModel,
    months: int = 360,
    recovery_rate: float = 0.60,
    seed: int = 42,
) -> Dict[str, List[float]]:
    """
    Coordinates multi-month simulation of the RMBS portfolio.
    """
    sim_loans = copy.deepcopy(loans)
    rng = np.random.default_rng(seed)

    for t in tranches:
        t.outstanding_principal = t.initial_principal
        t.interest_paid = 0.0
        t.principal_paid = 0.0
        t.cf_history = []

    monthly_results = {t.name: [] for t in tranches}

    for _ in range(months):
        loans_active = any(ln.is_active() for ln in sim_loans)
        tranches_active = any(t.outstanding_principal > 1e-8 for t in tranches)

        if not loans_active and not tranches_active:
            break

        total_interest = 0.0
        total_principal = 0.0

        for ln in sim_loans:
            perf = simulate_loan_month(
                ln, recovery_rate, default_model, prepayment_model, rng
            )
            total_interest += perf["interest"]
            total_principal += perf["principal"]

        allocate_waterfall(total_interest, total_principal, tranches)

        for t in tranches:
            cf = t.interest_paid + t.principal_paid
            monthly_results[t.name].append(cf)
            t.cf_history.append(cf)

            t.interest_paid = 0.0
            t.principal_paid = 0.0

    return monthly_results
