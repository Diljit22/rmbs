#!/usr/bin/env python3
"""
structuring.py

Defines RMBS tranches and a waterfall allocation function.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Tranche:
    name: str
    outstanding_principal: float
    coupon_rate: float
    interest_paid: float = 0.0
    principal_paid: float = 0.0
    cf_history: List[float] = field(default_factory=list)

    # For analytics, store the original principal
    initial_principal: float = 0.0


def allocate_waterfall(
    total_interest: float, total_principal: float, tranches: List[Tranche]
) -> None:
    """
    Allocates interest and principal top-down:
    Senior -> Mezz -> Equity.
    """
    # 1) Allocate interest top-down
    remaining_interest = total_interest
    for t in tranches:
        if t.outstanding_principal > 1e-8:
            monthly_interest_due = t.outstanding_principal * (t.coupon_rate / 12.0)
            pay_interest = min(monthly_interest_due, remaining_interest)
            t.interest_paid = pay_interest
            remaining_interest -= pay_interest
        else:
            t.interest_paid = 0.0

    # 2) Allocate principal top-down
    remaining_principal = total_principal
    for t in tranches:
        if t.outstanding_principal > 1e-8:
            pay_principal = min(t.outstanding_principal, remaining_principal)
            t.principal_paid = pay_principal
            t.outstanding_principal -= pay_principal
            remaining_principal -= pay_principal
        else:
            t.principal_paid = 0.0
