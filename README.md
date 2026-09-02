# RMBS Structuring, Underwriting & Sensitivity Engine

A standard Residential Mortgage-Backed Security (RMBS) structuring and simulation engine. The model simulates monthly loan-level amortization, default, and prepayment cash flows, routing pool collections through a sequential-pay waterfall to evaluate bond performance metrics across multidimensional stress scenarios.

---

## Technical Features

### 1. Strategic Risk Modeling (Strategy Pattern)
Risk models are decoupled from the core simulation loop using Abstract Base Classes (`PrepaymentModel` and `DefaultModel`). This allows you to easily write and plug in custom hazard models without refactoring the simulation engine.
* **PSA Prepayment Model (`PSAModel`):** Implements the standard Public Securities Association curve (prepayments rising linearly over the first 30 months of seasoning before leveling off at a flat CPR).
* **Logistic Hazard Model (`LogisticDefaultModel`):** Estimates monthly default probabilities (MDR) based on borrower FICO scores and dynamic LTV limits.

### 2. Available Funds Sequential Waterfall
Realized pool collections (scheduled interest, principal, recoveries, and prepayments) are consolidated into a single "Available Funds" bucket. Cash is distributed sequentially:
1. Senior Interest
2. Mezzanine Interest
3. Senior Principal (until retired)
4. Mezzanine Principal (until retired)
5. Equity/Residual Principal and Residual Yield (all remaining collections), preventing cash leakage and resolving the excess spread distribution errors common in simple procedural structures.

### 3. Stress-Testing Sensitivity Grid
A dedicated analysis engine runs multidimensional parameter sweeps (Constant Default Rates [CDR] from 1% to 10% vs. PSA Prepayment Speeds from 50% to 200%) to automatically output structured yield (IRR) and Weighted Average Life (WAL) tables for each tranche.

### 4. Vectorized Metrics & Numerical Guarding
* **Vectorized WAL:** Weighted Average Life is calculated using vectorized NumPy operations for speed.
* **Defensive Yield Search:** The bisection search solver contains numerical guards (such as a `-20%` monthly lower bound and clipped denominators) to prevent float underflow and division-by-zero errors when evaluating highly impaired tranches over 360+ periods.
* **Thread-Safety:** Simulations use localized, thread-safe instances of `np.random.default_rng()`.

---

## Installation & Usage

Install the package and its development requirements (pytest, ruff) in editable mode. 
```bash
pip install ".[dev]"
```

### Run a Static Scenario Simulation
Simulate the portfolio under a preset assumption profile (`base`, `stress`, or `optimistic`) and display a stacked cash flow chart:
```bash
python3 main.py --scenario stress --show_plot
```

### Run the Sensitivity Stress Grid
Evaluate the structural sensitivity of your tranches over a parameter matrix of CDR and PSA speeds:
```bash
python3 main.py --sensitivity
```
