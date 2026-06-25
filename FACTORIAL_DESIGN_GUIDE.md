# Full Factorial Design Simulation Guide

## Overview

This guide explains the full factorial design for evaluating Adaptive Caliper Selection (ACS) methods across 54 scenarios.

## Factorial Design Factors

### Factor 1: Sample Size (n)
- **Levels:** 500, 1000, 2000
- **Rationale:** Examines performance across small, medium, and large samples, reflecting real-world study sizes in observational research.

### Factor 2: Treatment Prevalence
- **Levels:** 0.3, 0.5, 0.7
- **Rationale:** Tests methods under asymmetric designs (30% treated, 70% control; 70% treated, 30% control) and balanced designs (50/50).

### Factor 3: Overlap Level
- **Levels:** 
  - **High overlap** (α = 0.3): Propensity score distributions overlap substantially
  - **Medium overlap** (α = 0.6): Moderate separation between treatment groups
  - **Low overlap** (α = 1.0): Substantial separation, limited common support
- **Rationale:** Represents varying degrees of covariate imbalance and confounding severity.

### Factor 4: Confounding Strength
- **Levels:**
  - **Weak** (β = 0.3): Covariates have weak effects on outcome
  - **Strong** (β = 1.0): Covariates have strong effects on outcome
- **Rationale:** Tests sensitivity to confounding magnitude in treatment effect estimation.

## Total Design

**Total Scenarios:** 3 × 3 × 3 × 2 = **54 scenarios**

Each scenario is replicated **1,000 times** to ensure stable Monte Carlo estimates.

**Total simulations:** 54 × 1,000 = **54,000 simulation runs**

## Scenario Enumeration

Scenarios are numbered 1-54 following this pattern:

```
For each sample size:
  For each treatment prevalence:
    For each overlap level:
      For each confounding strength:
        Create scenario
```

### Example Scenarios

| ID | n | Prevalence | Overlap | Confounding | Description |
|----|---|------------|---------|-------------|-------------|
| 1 | 500 | 0.3 | high | weak | Small sample, minority treated, good overlap, weak conf |
| 27 | 1000 | 0.3 | high | weak | Medium sample, minority treated, good overlap, weak conf |
| 54 | 2000 | 0.7 | low | strong | Large sample, majority treated, poor overlap, strong conf |

## Methods Compared

Seven methods are evaluated in each scenario:

### Fixed-Caliper Methods
1. **Fixed-0.1**: Caliper = 0.1 × SD(logit PS)
2. **Fixed-0.2**: Caliper = 0.2 × SD(logit PS) [Austin's recommendation]
3. **Fixed-0.5**: Caliper = 0.5 × SD(logit PS)
4. **No Caliper**: Nearest-neighbor matching without caliper restriction

### Adaptive Caliper Selection (ACS) Methods
5. **ACS-Balance**: Selects largest caliper achieving max |SMD| ≤ 0.1
6. **ACS-Knee**: Selects caliper at maximum curvature of Pareto frontier
7. **ACS-Weighted**: Minimizes λ·Balance + (1-λ)·(1-Retention) with λ=0.5

## Performance Metrics

Each method is evaluated on:

### Balance Metrics
- **Max |SMD|**: Maximum absolute standardized mean difference across covariates
- **Mean |SMD|**: Average absolute standardized mean difference

### Efficiency Metrics
- **Retention**: Proportion of treated units successfully matched
- **N matched**: Number of matched pairs

### Treatment Effect Metrics
- **Bias**: Difference between estimated and true ATT (0.5)
- **RMSE**: Root mean squared error
- **MSE**: Mean squared error
- **Coverage**: 95% CI coverage rate
- **CI Width**: Average confidence interval width

## Running the Simulation

### Option 1: Command Line (Recommended for full run)

```bash
python run_full_factorial_simulation.py
```

Expected runtime: 30-60 minutes with parallel processing on modern multi-core systems.

### Option 2: Jupyter Notebook (Interactive analysis)

```bash
jupyter notebook notebooks/full_factorial_analysis.ipynb
```

The notebook allows:
- Running a subset of scenarios for testing
- Interactive visualization of results
- Step-by-step analysis of performance

### Option 3: Test Run (Verify setup)

```bash
python test_factorial_design.py
```

Runs 5 representative scenarios with 50 replications each (~2-5 minutes).

## Output Files

### Results Directory (`outputs/results/`)
- `simulation_results_full.csv`: Raw results for all replications
- `simulation_results_intermediate.csv`: Intermediate results (saved during run)

### Tables Directory (`outputs/tables/`)
- `simulation_summary.csv`: Summary statistics by scenario and method
- `comprehensive_comparison.csv`: Overall performance across all scenarios
- `table1_overall_comparison.csv`: Main results table
- `table2_by_sample_size.csv`: Performance by sample size
- `table3_by_overlap.csv`: Performance by overlap level
- `table4_by_confounding.csv`: Performance by confounding strength
- `table5_by_prevalence.csv`: Performance by treatment prevalence
- `table6_win_rates.csv`: Percentage of scenarios where each method performs best

### Figures Directory (`outputs/figures/`)

#### Factorial Design Heatmaps
- `factorial_heatmap_rmse.png`: RMSE across all factor combinations
- `factorial_heatmap_mean_abs_bias.png`: Bias across all factor combinations
- `factorial_heatmap_coverage_rate.png`: Coverage across all factor combinations
- `factorial_heatmap_mean_retention.png`: Retention across all factor combinations
- `factorial_heatmap_mean_max_smd.png`: Balance across all factor combinations

#### Method Comparisons
- `method_rankings_rmse.png`: Method rankings by RMSE
- `method_rankings_mean_abs_bias.png`: Method rankings by bias
- `method_rankings_coverage_rate.png`: Method rankings by coverage
- `method_rankings_mean_max_smd.png`: Method rankings by balance

#### Factor Effects
- `factor_effects_rmse.png`: Main effects of design factors on RMSE
- `factor_effects_mean_abs_bias.png`: Main effects on bias
- `factor_effects_coverage_rate.png`: Main effects on coverage
- `factor_effects_mean_retention.png`: Main effects on retention

#### Distribution Comparisons
- `boxplot_bias.png`: Bias distributions by method
- `boxplot_mse.png`: MSE distributions by method
- `boxplot_max_smd.png`: Balance distributions by method
- `boxplot_retention.png`: Retention distributions by method
- `boxplot_coverage.png`: Coverage distributions by method

#### Scenario Tracking
- `scenario_comparison.png`: Multi-panel plot tracking performance across all scenarios

## Interpreting Results

### Key Questions Addressed

1. **Which method performs best overall?**
   - See `comprehensive_comparison.csv` and method ranking plots

2. **How does performance vary by sample size?**
   - See `table2_by_sample_size.csv` and factor effect plots

3. **Which scenarios favor which methods?**
   - See factorial heatmaps showing performance across factor combinations

4. **Is ACS robust across diverse scenarios?**
   - Compare ACS methods' win rates and consistency metrics

5. **What are the trade-offs between balance and efficiency?**
   - Examine retention vs. max |SMD| across methods

### Expected Findings

Based on the ACS framework, we expect:

- **ACS-Balance** to excel when balance is critical (e.g., high confounding)
- **ACS-Knee** to provide balanced performance across scenarios
- **ACS-Weighted** to adapt to different priorities
- **Fixed-0.2** to perform reasonably but suboptimally in extreme scenarios
- **Fixed-0.1** to achieve excellent balance but poor retention
- **Fixed-0.5** to achieve high retention but poor balance
- **No Caliper** to struggle with balance across most scenarios

## Computational Resources

### Memory Requirements
- Raw results: ~100-200 MB
- Peak memory during simulation: ~2-4 GB

### Disk Space
- Total output files: ~300-500 MB

### Parallelization
- Uses `joblib` for parallel processing
- Set `N_JOBS = -1` in `config.py` to use all cores
- Scales well up to 16+ cores

## Reproducibility

All simulations use explicit random seeds:
- Each scenario has a base seed: `scenario_id * 10000`
- Each replication within a scenario: `base_seed + replication_number`

This ensures:
- Complete reproducibility of results
- Ability to re-run individual scenarios
- Fair comparison across methods (same data for all methods)

## Troubleshooting

### Simulation runs slowly
- Check `N_JOBS` setting in `config.py`
- Reduce `N_REPLICATIONS` for testing
- Run subset of scenarios first

### Memory errors
- Reduce number of parallel jobs
- Process scenarios sequentially
- Use `save_intermediate=True` to avoid losing progress

### Unexpected results
- Run `test_factorial_design.py` to verify setup
- Check for warnings in simulation output
- Examine intermediate results files

## References

- Austin, P. C. (2011). Optimal caliper widths for propensity-score matching when estimating differences in means and differences in proportions in observational studies. *Pharmaceutical Statistics*, 10(2), 150-161.

- Rosenbaum, P. R., & Rubin, D. B. (1985). Constructing a control group using multivariate matched sampling methods that incorporate the propensity score. *The American Statistician*, 39(1), 33-38.

- Stuart, E. A. (2010). Matching methods for causal inference: A review and a look forward. *Statistical Science*, 25(1), 1-21.
