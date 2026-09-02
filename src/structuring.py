"""
src/structuring.py

Defines RMBS tranches and cash-flow allocation.
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
    initial_principal: float = 0.0

    def __post_init__(self) -> None:
        if self.initial_principal == 0.0:
            self.initial_principal = self.outstanding_principal


def allocate_waterfall(
    total_interest: float, total_principal: float, tranches: List[Tranche]
) -> None:
    """
    Allocates total pool cash flows (interest + principal) to tranches
    using a standard structured finance sequential-pay waterfall.
    """
    available_funds = total_interest + total_principal

    # 1) Pay Interest sequentially to Debt Tranches (excluding Equity)
    for t in tranches:
        if t.name == "Equity":
            continue
        if t.outstanding_principal > 1e-8:
            interest_due = t.outstanding_principal * (t.coupon_rate / 12.0)
            pay_interest = min(interest_due, available_funds)
            t.interest_paid = pay_interest
            available_funds -= pay_interest

    # 2) Pay Principal sequentially to Debt Tranches
    for t in tranches:
        if t.name == "Equity":
            continue
        if t.outstanding_principal > 1e-8:
            principal_due = t.outstanding_principal
            pay_principal = min(principal_due, available_funds)
            t.principal_paid = pay_principal
            t.outstanding_principal -= pay_principal
            available_funds -= pay_principal

    # 3) Residual Cash Flows flow directly to the Equity/Residual Tranche
    equity_tranche = next((t for t in tranches if t.name == "Equity"), None)
    if equity_tranche:
        if equity_tranche.outstanding_principal > 1e-8:
            pay_equity_principal = min(
                equity_tranche.outstanding_principal, available_funds
            )
            equity_tranche.principal_paid = pay_equity_principal
            equity_tranche.outstanding_principal -= pay_equity_principal
            available_funds -= pay_equity_principal

        if available_funds > 1e-8:
            equity_tranche.interest_paid += available_funds
            available_funds = 0.0
