import pytest
import numpy as np
from src.loan_pool import Loan
from src.risk_models import logistic_default_probability, simple_prepayment_probability


def test_default_probability_bounds():
    loan = Loan(
        principal=100000, rate=0.04, fico=700, ltv=0.8, age_months=10, term_months=360
    )
    pd_monthly = logistic_default_probability(loan)
    assert 0.0 <= pd_monthly <= 1.0


def test_prepayment_probability_bounds():
    loan = Loan(
        principal=100000, rate=0.04, fico=700, ltv=0.8, age_months=10, term_months=360
    )
    cpr_monthly = simple_prepayment_probability(loan, base_cpr_annual=0.12)
    assert 0.0 <= cpr_monthly <= 1.0
