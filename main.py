"""
main.py

Command-line entry for the RMBS Structuring, Underwriting & Sensitivity Demo.
"""

import argparse
import numpy as np

from src.loan_pool import load_loans_from_csv, generate_loan_pool
from src.structuring import Tranche
from src.risk_models import LogisticDefaultModel, PSAModel, ConstantPrepaymentRateModel
from src.simulation import run_simulation
from src.metrics import calculate_yield, calculate_wal
from src.visualization import plot_tranche_cash_flows
from src.sensitivity import run_sensitivity_grid


def parse_arguments():
    parser = argparse.ArgumentParser(description="RMBS Structuring & Underwriting Demo")
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to CSV file containing loans.",
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
        "--sensitivity",
        action="store_true",
        help="If set, run a multi-dimensional stress testing grid instead of a single scenario.",
    )
    parser.add_argument(
        "--show_plot",
        action="store_true",
        help="If set, show a stacked area plot of cash flows.",
    )
    return parser.parse_args()


def get_scenario_models(scenario_name: str):
    """
    Returns default and prepayment models corresponding to the selected scenario.
    """
    if scenario_name == "stress":
        return {
            "default_model": LogisticDefaultModel(base_pd_annual=0.06),
            "prepayment_model": PSAModel(speed=150.0),
            "recovery_rate": 0.50,
        }
    elif scenario_name == "optimistic":
        return {
            "default_model": LogisticDefaultModel(base_pd_annual=0.01),
            "prepayment_model": PSAModel(speed=75.0),
            "recovery_rate": 0.70,
        }
    else:  # base case
        return {
            "default_model": LogisticDefaultModel(base_pd_annual=0.03),
            "prepayment_model": PSAModel(speed=100.0),
            "recovery_rate": 0.60,
        }


def main():
    args = parse_arguments()

    # 1) Ingest loan pool
    if args.csv:
        loans = load_loans_from_csv(args.csv)
        print(f"Loaded {len(loans)} loans from {args.csv}.")
    else:
        loans = generate_loan_pool(n_loans=100, seed=42)
        print("No CSV provided; generated 100 synthetic loans.")

    # 2) Standard capital structure (70% Senior, 20% Mezz, 10% Equity)
    total_principal = sum(loan.principal for loan in loans)
    senior_principal = total_principal * 0.70
    mezz_principal = total_principal * 0.20
    equity_principal = total_principal * 0.10

    tranches = [
        Tranche(
            name="Senior",
            outstanding_principal=senior_principal,
            initial_principal=senior_principal,
            coupon_rate=0.04,
        ),
        Tranche(
            name="Mezz",
            outstanding_principal=mezz_principal,
            initial_principal=mezz_principal,
            coupon_rate=0.06,
        ),
        Tranche(
            name="Equity",
            outstanding_principal=equity_principal,
            initial_principal=equity_principal,
            coupon_rate=0.00,
        ),
    ]

    # 3) Check running path
    if args.sensitivity:
        default_scenarios = [0.01, 0.03, 0.06, 0.10]
        psa_scenarios = [50.0, 100.0, 150.0, 200.0]
        run_sensitivity_grid(
            loans=loans,
            tranches=tranches,
            default_scenarios=default_scenarios,
            psa_scenarios=psa_scenarios,
        )
    else:
        config = get_scenario_models(args.scenario)
        monthly_results = run_simulation(
            loans=loans,
            tranches=tranches,
            default_model=config["default_model"],
            prepayment_model=config["prepayment_model"],
            months=args.months,
            recovery_rate=config["recovery_rate"],
        )

        print("\n----- Bond Analytics -----")
        for t in tranches:
            cf_array = np.array(monthly_results[t.name])
            bond_yield = calculate_yield(cf_array, t.initial_principal)
            wal = calculate_wal(cf_array)
            total_cf = cf_array.sum()
            print(
                f"{t.name}:\n"
                f"  Principal: {t.initial_principal:,.2f}\n"
                f"  Total Cash Received: {total_cf:,.2f}\n"
                f"  Yield (IRR): {bond_yield*100:.2f}%\n"
                f"  Weighted Avg Life: {wal:.2f} years\n"
            )

        if args.show_plot:
            plot_tranche_cash_flows(monthly_results)


if __name__ == "__main__":
    main()
