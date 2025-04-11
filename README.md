# RMBS Structuring & Underwriting Demo

## Overview

This project demonstrates a simplified **Residential Mortgage-Backed Security (RMBS)** transaction workflow:

1. **Loan Ingestion**  
   Loads mortgage loans from a CSV file (`sample_loans.csv`) or, if unavailable, generates a synthetic pool.  

2. **Risk Modeling**  
   - **Default:** Uses a logistic-based default probability that factors in FICO scores and loan-to-value ratios.  
   - **Prepayment:** Applies a constant annual CPR converted to monthly probabilities.  

3. **Cash Flow Simulation**  
   - Implements standard mortgage amortization (principal + interest).  
   - Assesses whether a loan defaults (with partial recovery) or prepays.  

4. **Structuring**  
   - Aggregates monthly interest and principal from the pool.  
   - Distributes proceeds to three tranches (Senior, Mezzanine, Equity) via a simple top-down waterfall.  

5. **Bond Analytics**  
   - Computes each tranche’s **Yield (IRR)** and **Weighted Average Life (WAL)**.  

6. **Visualization**  
   - Optionally produces a stacked area plot of monthly tranche cash flows.  

7. **Testing**  
   - Contains unit tests that verify core functionalities, ensuring stability and correctness.  

---

## Requirements

- **Python 3.8+**  
- Refer to `requirements.txt` for required libraries:
  numpy>=1.21.0
  pandas>=1.3.0
  matplotlib>=3.4.0
  pytest>=7.0.0
  black>=23.1.0
  flake8>=5.0.0

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

1. **Loan Data**  
   - If you have a loan dataset, place a CSV file in the project folder or specify its path.  
   - A sample file (`sample_loans.csv`) is provided.  

2. **Run the Demo**  
   From the project directory, use:

   ```bash
   python main.py \
       --csv sample_loans.csv \
       --months 360 \
       --scenario base \
       --show_plot
   ```

   - `--csv` indicates the path to your loan CSV. If omitted, a synthetic set of loans is generated.  
   - `--months` is the number of months to simulate (e.g., 360 for 30 years).  
   - `--scenario` can be `base`, `stress`, or `optimistic`, defining default/prepayment assumptions.  
   - `--show_plot` will display a stacked area chart of monthly cash flows allocated to each tranche.  

3. **Results**  
   - The script prints monthly cash flows for each tranche, as well as **Yield (IRR)** and **WAL**.  
   - If `--show_plot` is used, a graphical output of monthly cash flows is displayed.  

---

## Testing

A suite of **pytest**-based tests is included. Run them with:

```bash
pytest
```

These tests confirm that each component (loan data, default/prepayment models, waterfall allocations, etc.) behaves as intended.

---

## Project Structure

```bash
rmbs_demo/
├── .setup.cfg
├── README.md
├── requirements.txt
├── main.py         # A small script that imports and runs src.main
├── src/
│   ├── __init__.py
│   ├── main.py     # Contains the bulk of the application logic
│   ├── loan_pool.py
│   ├── risk_models.py
│   ├── structuring.py
│   ├── simulation.py
│   ├── metrics.py
│   ├── visualization.py
│   └── data/
│       └── sample_loans.csv
└── tests/
    ├── test_loan_pool.py
    ├── test_risk_models.py
    ├── test_structuring.py
    ├── test_simulation.py
    └── test_metrics.py


```

- **main.py**  
  Command-line entry point. Parses arguments, loads loans, runs the simulation, and summarizes results.  
- **loan_pool.py**  
  Contains `Loan` data class and methods to load or generate loan data.  
- **risk_models.py**  
  Implements default and prepayment probability calculations.  
- **simulation.py**  
  Coordinates monthly activity, including amortization, default/prepayment, and aggregation of payments.  
- **structuring.py**  
  Defines tranche objects and a waterfall function to allocate monthly cash flows.  
- **metrics.py**  
  Provides functions to compute bond-level metrics (Yield/IRR, WAL).  
- **visualization.py**  
  Creates a stacked area chart of monthly tranche cash flows.  
- **tests/**  
  Contains automated tests to verify correctness.
