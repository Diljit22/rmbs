import pytest
from src.structuring import Tranche, allocate_waterfall


def test_allocate_waterfall():
    # 2 tranches
    senior = Tranche(name="Senior", outstanding_principal=1000, coupon_rate=0.05)
    mezz = Tranche(name="Mezz", outstanding_principal=500, coupon_rate=0.07)
    tranches = [senior, mezz]

    # Suppose there's 60 of interest and 500 of principal to allocate
    allocate_waterfall(60, 500, tranches)

    # Check interest
    # Senior interest due = 1000 * (0.05/12) = ~4.17
    # So they get 4.17 from the 60
    assert abs(senior.interest_paid - 4.1666) < 1e-1
    # Remainder for mezz interest
    # Mezz interest due = 500 * (0.07/12) = ~2.92
    # So they get that from the remainder, leaving about 60 - (4.17+2.92)= ~52.91 not used
    # Actually we should check if there's any cap. It's more than enough so mezz gets full 2.92
    assert mezz.interest_paid > 2.0

    # Check principal
    # Senior principal first. Senior had 1000.
    # We have 500 total principal. So senior gets min(1000, 500) = 500
    # Mezz gets 0
    assert senior.principal_paid == 500
    assert mezz.principal_paid == 0
