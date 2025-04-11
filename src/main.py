#!/usr/bin/env python3
"""
main.py

Command-line entry for RMBS Structuring & Underwriting Demo.
"""

import argparse
import numpy as np

from src.loan_pool import load_loans_from_csv, generate_loan_pool
from src.structuring import Tranche
from src.simulation import run_simulation
from src.metrics import calculate_yield, calculate_wal
from src.visualization import plot_tranche_cash_flows


def parse_arguments():
    parser = argparse.ArgumentParser(description="RMBS Structuring & Underwriting Demo")
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to CSV file containing loans. If not provided, synthetic loans are generated.",
    )
    parser.add_argument(
        "--months", type=int, default=360, help="Number of months to simulate."
    )
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["base", "stress", "optimistic"],
        default="base",
        help="Scenario for default/prepayment assumptions.",
    )
    parser.add_argument(
        "--show_plot",
        action="store_true",
        help="If set, show a stacked area plot of cash flows.",
    )
    return parser.parse_args()


def get_scenario_params(scenario_name: str):
    """
    Returns default and prepayment assumptions based on scenario.
    """
    if scenario_name == "stress":
        # Higher default rate, lower recovery, higher prepayment
        return {
            "annual_default_base": 0.06,
            "annual_prepayment_base": 0.12,
            "recovery_rate": 0.50,
        }
    elif scenario_name == "optimistic":
        # Very low default rate, moderate prepayment
        return {
            "annual_default_base": 0.01,
            "annual_prepayment_base": 0.08,
            "recovery_rate": 0.70,
        }
    else:
        # base case
        return {
            "annual_default_base": 0.03,
            "annual_prepayment_base": 0.10,
            "recovery_rate": 0.60,
        }


def main():
    args = parse_arguments()
    scenario_params = get_scenario_params(args.scenario)

    # 1) Load or generate loans
    if args.csv:
        loans = load_loans_from_csv(args.csv)
        print(f"Loaded {len(loans)} loans from {args.csv}.")
    else:
        loans = generate_loan_pool(n_loans=100, seed=42)
        print("No CSV provided; generated 100 synthetic loans.")

    # 2) Define a simple 3-tranche structure (Senior, Mezz, Equity)
    total_principal = sum(loan.principal for loan in loans)
    senior_principal = total_principal * 0.70
    mezz_principal = total_principal * 0.20
    equity_principal = total_principal * 0.10

    tranches = [
        Tranche(
            name="Senior", outstanding_principal=senior_principal, coupon_rate=0.04
        ),
        Tranche(name="Mezz", outstanding_principal=mezz_principal, coupon_rate=0.06),
        Tranche(
            name="Equity", outstanding_principal=equity_principal, coupon_rate=0.00
        ),
    ]
    # Keep track of initial principal for later yield calculations
    for t in tranches:
        t.initial_principal = t.outstanding_principal

    # 3) Run simulation
    monthly_results = run_simulation(
        loans=loans,
        tranches=tranches,
        months=args.months,
        recovery_rate=scenario_params["recovery_rate"],
        base_pd_annual=scenario_params["annual_default_base"],
        base_cpr_annual=scenario_params["annual_prepayment_base"],
    )

    # 4) Compute bond-level metrics for each tranche
    print("\n----- Bond Analytics -----")
    for t in tranches:
        cf_array = np.array(monthly_results[t.name])
        price = t.initial_principal  # assume purchase at par for demonstration
        bond_yield = calculate_yield(cf_array, price)
        wal = calculate_wal(cf_array)
        total_cf = cf_array.sum()
        print(
            f"{t.name}:\n"
            f"  Principal: {t.initial_principal:,.2f}\n"
            f"  Total Cash Received: {total_cf:,.2f}\n"
            f"  Yield (IRR): {bond_yield*100:.2f}%\n"
            f"  Weighted Avg Life: {wal:.2f} years\n"
        )

    # 5) Plot if requested
    # if args.show_plot:
    #   plot_tranche_cash_flows(monthly_results)
    plot_tranche_cash_flows(monthly_results)


if __name__ == "__main__":
    main()
