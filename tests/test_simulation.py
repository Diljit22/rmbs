"""
tests/test_simulation.py

Pytest suite validating mathematical logic and structural behaviors.
"""

import numpy as np
import pytest
from src.loan_pool import Loan
from src.metrics import calculate_wal, calculate_yield
from src.simulation import calculate_monthly_payment, run_simulation
from src.risk_models import LogisticDefaultModel, PSAModel
from src.structuring import Tranche, allocate_waterfall


def test_calculate_monthly_payment() -> None:
    """Validates monthly mortgage amortization output calculations."""
    loan = Loan(
        principal=100000.0,
        rate=0.06,
        fico=700,
        ltv=0.80,
        age_months=0,
        term_months=360,
    )
    payment = calculate_monthly_payment(loan)
    assert abs(payment - 599.55) < 0.10


def test_calculate_wal() -> None:
    """Checks the Weighted Average Life formula output."""
    cashflows = np.full(48, 100.0)
    wal = calculate_wal(cashflows)
    assert abs(wal - 2.04) < 0.05


def test_calculate_yield() -> None:
    """Validates that IRR bisection handles positive and negative bounds."""
    cashflows = np.full(12, 1000.0)
    
    # Positive yield test
    bond_yield_pos = calculate_yield(cashflows, price=11000.0)
    assert bond_yield_pos > 0.0

    # Negative yield test (price exceeds aggregate cash flows)
    bond_yield_neg = calculate_yield(cashflows, price=13000.0)
    assert bond_yield_neg < 0.0


def test_waterfall_allocation() -> None:
    """Verifies sequential distribution waterfall functionality."""
    tranches = [
        Tranche("Senior", outstanding_principal=1000.0, coupon_rate=0.06),
        Tranche("Mezz", outstanding_principal=500.0, coupon_rate=0.08),
        Tranche("Equity", outstanding_principal=100.0, coupon_rate=0.00),
    ]

    # Month 1 interest payment allocations:
    # Senior interest due: 1000 * 0.06 / 12 = 5.0
    # Mezz interest due: 500 * 0.08 / 12 = 3.3333
    allocate_waterfall(total_interest=10.0, total_principal=90.0, tranches=tranches)

    assert abs(tranches[0].interest_paid - 5.0) < 1e-9
    assert abs(tranches[1].interest_paid - 3.3333) < 1e-4
    assert abs(tranches[0].principal_paid - 91.6667) < 1e-4
    assert tranches[1].principal_paid == 0.0


def test_run_simulation() -> None:
    """Ensures simulation coordinates multi-period outputs correctly."""
    loans = [
        Loan(100000.0, 0.06, 750, 0.80, 0, 360),
        Loan(200000.0, 0.05, 680, 0.75, 12, 360)
    ]
    tranches = [
        Tranche("Senior", outstanding_principal=210000.0, coupon_rate=0.04),
        Tranche("Mezz", outstanding_principal=60000.0, coupon_rate=0.06),
        Tranche("Equity", outstanding_principal=30000.0, coupon_rate=0.00)
    ]
    default_model = LogisticDefaultModel(base_pd_annual=0.0)
    prepayment_model = PSAModel(speed=0.0)

    results = run_simulation(
        loans=loans,
        tranches=tranches,
        default_model=default_model,
        prepayment_model=prepayment_model,
        months=3,
        recovery_rate=0.60
    )

    assert len(results["Senior"]) == 3
    assert len(results["Mezz"]) == 3
    assert len(results["Equity"]) == 3
    for name in results:
        assert all(cf >= 0.0 for cf in results[name])
