"""
src/sensitivity.py

Runs multidimensional stress scenario grids (Default Rate vs Prepayment Speed)
to evaluate structural sensitivity of RMBS tranche yields.
"""

from typing import List
import numpy as np

from src.loan_pool import Loan
from src.metrics import calculate_yield, calculate_wal
from src.risk_models import LogisticDefaultModel, PSAModel
from src.simulation import run_simulation
from src.structuring import Tranche


def run_sensitivity_grid(
    loans: List[Loan],
    tranches: List[Tranche],
    default_scenarios: List[float],
    psa_scenarios: List[float],
    recovery_rate: float = 0.60,
) -> None:
    """
    Simulates every combination of default rates and PSA speeds, printing
    a scenario pricing matrix.
    """
    print("=" * 70)
    print("           RMBS TRANCHE SENSITIVITY MATRIX (YIELD / WAL)          ")
    print("=" * 70)

    for tranche_name in [t.name for t in tranches]:
        print(f"\nTranche: {tranche_name}")
        print("-" * 65)
        headers = " | ".join(f"{psa:4.0f}% PSA" for psa in psa_scenarios)
        print(f"CDR \\ PSA  | {headers}")
        print("-" * 65)

        for cdr in default_scenarios:
            row_items = []
            for psa in psa_scenarios:
                default_model = LogisticDefaultModel(base_pd_annual=cdr)
                prepayment_model = PSAModel(speed=psa)

                results = run_simulation(
                    loans=loans,
                    tranches=tranches,
                    default_model=default_model,
                    prepayment_model=prepayment_model,
                    recovery_rate=recovery_rate,
                )

                cf_array = np.array(results[tranche_name])
                target_tranche = next(t for t in tranches if t.name == tranche_name)
                irr = calculate_yield(cf_array, target_tranche.initial_principal)
                wal = calculate_wal(cf_array)

                row_items.append(f"{irr*100:5.1f}%/{wal:3.1f}y")

            row_string = " | ".join(row_items)
            print(f"CDR {cdr*100:4.1f}% | {row_string}")
        print("-" * 65)
