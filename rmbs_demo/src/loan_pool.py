#!/usr/bin/env python3
"""
loan_pool.py

Contains the Loan dataclass and functions for loading or generating loan pools.
"""

import csv
import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class Loan:
    """
    Represents a single mortgage loan.

    Attributes:
        principal (float): Current outstanding principal.
        rate (float): Annual interest rate (decimal).
        fico (int): Borrower's FICO score.
        ltv (float): Loan-to-value ratio (0 - 1).
        age_months (int): Months since origination.
        term_months (int): Total term in months (e.g. 360).
    """

    principal: float
    rate: float
    fico: int
    ltv: float
    age_months: int
    term_months: int

    def is_active(self) -> bool:
        return (self.principal > 1e-8) and (self.age_months < self.term_months)


def load_loans_from_csv(csv_path: str) -> List[Loan]:
    """
    Loads loans from a CSV file with headers:
    principal,rate,fico,ltv,age_months,term_months
    """
    loans = []
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            loan = Loan(
                principal=float(row["principal"]),
                rate=float(row["rate"]),
                fico=int(row["fico"]),
                ltv=float(row["ltv"]),
                age_months=int(row["age_months"]),
                term_months=int(row["term_months"]),
            )
            loans.append(loan)
    return loans


def generate_loan_pool(n_loans: int = 100, seed: int = 42) -> List[Loan]:
    """
    Generates synthetic loans for demonstration.
    """
    np.random.seed(seed)
    loans = []
    for _ in range(n_loans):
        principal = float(np.random.randint(100_000, 500_000))
        rate = float(np.random.choice([0.04, 0.045, 0.05, 0.055, 0.06]))
        fico = int(np.random.randint(600, 800))
        ltv = float(np.random.uniform(0.7, 0.95))
        age_months = int(np.random.randint(0, 60))  # some seasoning
        term_months = 360  # 30-year
        loans.append(Loan(principal, rate, fico, ltv, age_months, term_months))
    return loans
