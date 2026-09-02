"""
src/risk_models.py

Implements Abstract Base Classes (Strategy Pattern) for prepayment and default models,
enabling flexible extensions.
"""

import math
from abc import ABC, abstractmethod
from src.loan_pool import Loan


class PrepaymentModel(ABC):
    """Abstract base class for mortgage prepayment probability models."""

    @abstractmethod
    def calculate_monthly_rate(self, loan: Loan) -> float:
        """Returns the monthly prepayment probability (SMM)."""
        pass


class ConstantPrepaymentRateModel(PrepaymentModel):
    """Models prepayment using a flat annualized Constant Prepayment Rate (CPR)."""

    def __init__(self, cpr_annual: float = 0.10):
        self.cpr_annual = min(max(cpr_annual, 0.0), 0.99)

    def calculate_monthly_rate(self, loan: Loan) -> float:
        return 1.0 - (1.0 - self.cpr_annual) ** (1.0 / 12.0)


class PSAModel(PrepaymentModel):
    """
    Models prepayment utilizing the standard Public Securities Association (PSA) curve.
    """

    def __init__(self, speed: float = 100.0):
        self.speed = max(speed, 0.0)

    def calculate_monthly_rate(self, loan: Loan) -> float:
        age = max(1, loan.age_months)
        base_cpr = 0.06 * (age / 30.0) if age < 30 else 0.06
        cpr_annual = base_cpr * (self.speed / 100.0)
        cpr_annual = min(max(cpr_annual, 0.0), 0.99)
        return 1.0 - (1.0 - cpr_annual) ** (1.0 / 12.0)


class DefaultModel(ABC):
    """Abstract base class for mortgage default probability models."""

    @abstractmethod
    def calculate_monthly_rate(self, loan: Loan) -> float:
        """Returns the monthly probability of default (MDR)."""
        pass


class LogisticDefaultModel(DefaultModel):
    """
    Implements a logistic regression hazard model based on borrower FICO 
    and current loan-to-value (LTV) ratio.
    """

    def __init__(
        self,
        base_pd_annual: float = 0.03,
        fico_weight: float = -0.002,
        ltv_weight: float = 0.01,
    ):
        self.base_pd_annual = min(max(base_pd_annual, 0.0), 0.99)
        self.fico_weight = fico_weight
        self.ltv_weight = ltv_weight

    def calculate_monthly_rate(self, loan: Loan) -> float:
        if self.base_pd_annual <= 1e-9:
            return 0.0

        intercept = -math.log((1.0 / self.base_pd_annual) - 1.0 + 1e-9)
        fico_diff = loan.fico - 680
        ltv_diff_percent = (loan.ltv - 0.8) * 100.0

        z = intercept + (self.fico_weight * fico_diff) + (self.ltv_weight * ltv_diff_percent)
        pd_annual = 1.0 / (1.0 + math.exp(-z))
        
        pd_monthly = 1.0 - (1.0 - pd_annual) ** (1.0 / 12.0)
        return min(max(pd_monthly, 0.0), 1.0)
