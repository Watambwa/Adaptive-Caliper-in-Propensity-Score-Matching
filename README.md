# Adaptive Caliper Selection for Propensity Score Matching

## A Multi-Objective Optimization Framework

**Authors:** Perkins Watambwa, Glory Chidumwa, Fortunate Machingura, et al.  
**Institution:** Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe

---

## Abstract

Propensity score matching (PSM) is a cornerstone method for causal inference in observational studies, yet the selection of caliper width remains a consequential but often arbitrary decision. We propose a multi-objective optimization framework that formalizes the bias-variance tradeoff inherent in caliper selection by simultaneously minimizing covariate imbalance and maximizing effective sample size retention.

## Project Structure

```
Adaptive-Caliper-in-Propensity-Score-Matching/
├── src/
│   ├── config.py              # Configuration and parameters
│   ├── data_generator.py      # Synthetic data generation
│   ├── matching.py            # Propensity score matching
│   ├── adaptive_caliper.py    # ACS algorithm implementation
│   ├── treatment_effect.py    # ATT estimation
│   ├── simulation_runner.py   # Monte Carlo simulation
│   └── visualization.py       # Figures
├── notebooks/
│   └── 01_simulation_study.ipynb  # Main analysis notebook
├── outputs/
│   ├── figures/               # Generated figures
│   ├── tables/                # Generated tables
│   └── results/               # Simulation results
├── requirements.txt           # Python dependencies
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Single Scenario Example

```python
from src.data_generator import DataGenerator
from src.adaptive_caliper import AdaptiveCaliperSelector

# Generate data
generator = DataGenerator(seed=42)
df = generator.generate_dataset(n=1000, treatment_prevalence=0.5,
                                 overlap_level=0.6, confounding_strength=1.0)
df['e_hat'] = generator.estimate_propensity_scores(df)

# Run ACS
selector = AdaptiveCaliperSelector(seed=42)
selector.fit(df, covariate_cols=[f'X{i+1}' for i in range(6)])

# Get optimal caliper
result = selector.select_optimal('balance')
print(f"Optimal caliper: {result.optimal_caliper:.3f} SD")
```

### Run Full Factorial Simulation

```bash
# Run all 54 scenarios (takes 30-60 minutes with parallel processing)
python run_full_factorial_simulation.py
```

Or use the Jupyter notebook:
```bash
jupyter notebook notebooks/full_factorial_analysis.ipynb
```

## Methods Compared

| Method | Description |
|--------|-------------|
| Fixed-0.1 | Caliper = 0.1 × SD(logit PS) |
| Fixed-0.2 | Austin's recommendation |
| Fixed-0.5 | Looser caliper |
| No Caliper | Nearest-neighbor without restriction |
| ACS-Balance | Largest caliper achieving SMD ≤ 0.1 |
| ACS-Knee | Maximum curvature on Pareto frontier |
| ACS-Weighted | Minimize λ·Balance + (1-λ)·(1-Retention) |

## Simulation Design

**Full Factorial Design:**

| Factor | Levels |
|--------|--------|
| Sample size (n) | 500, 1000, 2000 |
| Treatment prevalence | 0.3, 0.5, 0.7 |
| Overlap (coefficient magnitude) | Low (α = 0.3), Medium (α = 0.6), High (α = 1.0) |
| Confounding strength | Weak (β = 0.3), Strong (β = 1.0) |

**Total scenarios:** 3 × 3 × 3 × 2 = **54 scenarios**  
**Replications:** 1000 per scenario  
**Total simulations:** 54,000

## Citation

```bibtex
To be added upon publication
}
```

## License

MIT License
