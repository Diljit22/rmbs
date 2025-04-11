import pytest
from src.loan_pool import Loan, generate_loan_pool


def test_loan_active():
    loan = Loan(
        principal=100000, rate=0.04, fico=700, ltv=0.8, age_months=0, term_months=360
    )
    assert loan.is_active() is True


def test_generate_loan_pool():
    loans = generate_loan_pool(n_loans=10, seed=123)
    assert len(loans) == 10
    for ln in loans:
        assert ln.principal > 0
