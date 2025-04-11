import pytest
from src.loan_pool import Loan
from src.simulation import simulate_loan_month


def test_simulate_loan_month():
    loan = Loan(
        principal=100000, rate=0.04, fico=700, ltv=0.8, age_months=0, term_months=360
    )
    # Force zero default & prepayment to check scheduled amounts
    perf = simulate_loan_month(
        loan, recovery_rate=0.0, base_pd_annual=0.0, base_cpr_annual=0.0
    )
    # Check that we paid some interest and some principal
    assert perf["interest"] > 0
    assert perf["principal"] > 0
    # principal should decrease
    assert loan.principal < 100000
