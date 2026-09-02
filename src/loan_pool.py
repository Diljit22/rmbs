"""
src/loan_pool.py

Contains the Loan dataclass and functions for loading or generating loan pools.
"""

import copy
import csv
from dataclasses import dataclass
from typing import List
import numpy as np


@dataclass
class Loan:
    """
    Represents a single residential mortgage loan.
    """

    principal: float
    rate: float
    fico: int
    ltv: float
    age_months: int
    term_months: int

    def __post_init__(self) -> None:
        if self.principal < 0.0:
            raise ValueError(f"Principal cannot be negative. Got: {self.principal}")
        if not (300 <= self.fico <= 850):
            raise ValueError(f"FICO must be between 300 and 850. Got: {self.fico}")
        if not (0.0 <= self.ltv <= 2.0):
            raise ValueError(f"LTV must be between 0.0 and 2.0. Got: {self.ltv}")
        if self.age_months < 0:
            raise ValueError(f"Age cannot be negative. Got: {self.age_months}")
        if self.term_months <= 0:
            raise ValueError(f"Term must be greater than zero. Got: {self.term_months}")

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
        for row_idx, row in enumerate(reader, start=1):
            try:
                loan = Loan(
                    principal=float(row["principal"]),
                    rate=float(row["rate"]),
                    fico=int(row["fico"]),
                    ltv=float(row["ltv"]),
                    age_months=int(row["age_months"]),
                    term_months=int(row["term_months"]),
                )
                loans.append(loan)
            except (ValueError, KeyError) as e:
                raise ValueError(
                    f"Error parsing row {row_idx} in CSV: {row}. Details: {e}"
                )
    return loans


def generate_loan_pool(n_loans: int = 100, seed: int = 42) -> List[Loan]:
    """
    Generates synthetic loans for demonstration using a thread-safe random generator.
    """
    rng = np.random.default_rng(seed)
    loans = []
    for _ in range(n_loans):
        principal = float(rng.integers(100_000, 500_000))
        rate = float(rng.choice([0.04, 0.045, 0.05, 0.055, 0.06]))
        fico = int(rng.integers(600, 850))
        ltv = float(rng.uniform(0.5, 0.95))
        age_months = int(rng.integers(0, 60))
        term_months = 360
        loans.append(Loan(principal, rate, fico, ltv, age_months, term_months))
    return loans
