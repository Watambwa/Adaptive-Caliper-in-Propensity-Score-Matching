"""
Test Full Factorial Design Setup
=================================

Quick test script to verify the factorial design simulation works correctly.
Runs a small subset of scenarios with fewer replications.

Author: Perkins Watambwa et al.
"""

import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from config import generate_all_scenarios, FIGURES_DIR, TABLES_DIR
from simulation_runner import run_scenario_simulation, summarize_results
from visualization import (
    plot_method_comparison_boxplot,
    plot_method_ranking_across_scenarios,
    create_comprehensive_comparison_table
)

print("=" * 80)
print("TESTING FACTORIAL DESIGN SETUP")
print("=" * 80)

# Generate all scenarios
all_scenarios = generate_all_scenarios()
print(f"\n✓ Generated {len(all_scenarios)} scenarios")

# Test with a representative subset
test_scenarios = [
    all_scenarios[0],   # Scenario 1: n=500, prev=0.3, high overlap, weak conf
    all_scenarios[8],   # Scenario 9: n=500, prev=0.5, medium overlap, weak conf
    all_scenarios[26],  # Scenario 27: n=1000, prev=0.3, high overlap, weak conf
    all_scenarios[40],  # Scenario 41: n=2000, prev=0.3, low overlap, weak conf
    all_scenarios[53],  # Scenario 54: n=2000, prev=0.7, low overlap, strong conf
]

print(f"\nRunning test with {len(test_scenarios)} representative scenarios:")
for scenario in test_scenarios:
    print(f"  - Scenario {scenario['scenario_id']}: {scenario['description']}")

print(f"\nUsing 50 replications per scenario (instead of 1000)")
print("=" * 80)

# Run simulations
all_results = []
for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n[{i}/{len(test_scenarios)}] Running scenario {scenario['scenario_id']}...")
    
    results = run_scenario_simulation(
        scenario=scenario,
        n_replications=50,
        n_jobs=-1,
        verbose=False
    )
    all_results.append(results)
    
    # Quick summary
    method_summary = results.groupby('method')['rmse'].mean()
    best_method = method_summary.idxmin()
    print(f"  ✓ Completed. Best method (lowest RMSE): {best_method} ({method_summary[best_method]:.4f})")

# Combine results
results_df = pd.concat(all_results, ignore_index=True)
print(f"\n{'=' * 80}")
print(f"✓ All test scenarios completed!")
print(f"  Total results: {len(results_df)} rows")
print(f"  Methods: {results_df['method'].nunique()}")
print(f"  Scenarios: {results_df['scenario_id'].nunique()}")

# Generate summary
print(f"\n{'=' * 80}")
print("GENERATING SUMMARY...")
print("=" * 80)

summary_df = summarize_results(results_df)
print(f"✓ Summary generated: {len(summary_df)} rows")

# Overall comparison table
comparison_table = create_comprehensive_comparison_table(summary_df)
print("\n" + "=" * 80)
print("OVERALL PERFORMANCE (Test Scenarios)")
print("=" * 80)
print(comparison_table[['mean_retention_mean', 'mean_max_smd_mean', 
                        'mean_abs_bias_mean', 'rmse_mean', 'coverage_rate_mean']])

# Method rankings
print("\n" + "=" * 80)
print("METHOD RANKINGS BY RMSE")
print("=" * 80)

# Calculate ranks
ranks = []
for scenario_id in summary_df['scenario_id'].unique():
    scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
    scenario_data = scenario_data.sort_values('rmse')
    scenario_data['rank'] = range(1, len(scenario_data) + 1)
    ranks.append(scenario_data[['method', 'rank']])

ranks_df = pd.concat(ranks)
avg_ranks = ranks_df.groupby('method')['rank'].mean().sort_values()

print("\nAverage rank across test scenarios (lower is better):")
for method, rank in avg_ranks.items():
    print(f"  {method:20s}: {rank:.2f}")

# Create test visualizations
print("\n" + "=" * 80)
print("GENERATING TEST VISUALIZATIONS...")
print("=" * 80)

# Boxplot
try:
    fig = plot_method_comparison_boxplot(
        results_df,
        metric='bias',
        title='Bias Across Test Scenarios',
        figsize=(12, 6)
    )
    test_fig_path = FIGURES_DIR / 'test_boxplot_bias.png'
    fig.savefig(test_fig_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Boxplot saved to {test_fig_path}")
except Exception as e:
    print(f"  ⚠ Boxplot generation failed: {e}")

# Rankings
try:
    fig = plot_method_ranking_across_scenarios(
        summary_df,
        metric='rmse',
        figsize=(12, 6)
    )
    test_fig_path = FIGURES_DIR / 'test_method_rankings.png'
    fig.savefig(test_fig_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Ranking plot saved to {test_fig_path}")
except Exception as e:
    print(f"  ⚠ Ranking plot generation failed: {e}")

# Save test results
test_results_path = TABLES_DIR / 'test_simulation_results.csv'
results_df.to_csv(test_results_path, index=False)
print(f"  ✓ Test results saved to {test_results_path}")

test_summary_path = TABLES_DIR / 'test_simulation_summary.csv'
summary_df.to_csv(test_summary_path, index=False)
print(f"  ✓ Test summary saved to {test_summary_path}")

# Final verification
print("\n" + "=" * 80)
print("VERIFICATION CHECKS")
print("=" * 80)

checks = []

# Check 1: All methods evaluated
expected_methods = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
actual_methods = results_df['method'].unique()
methods_ok = all(m in actual_methods for m in expected_methods)
checks.append(('All methods evaluated', methods_ok))

# Check 2: All scenarios completed
scenarios_ok = results_df['scenario_id'].nunique() == len(test_scenarios)
checks.append(('All scenarios completed', scenarios_ok))

# Check 3: No excessive missing values
missing_pct = results_df['att'].isna().sum() / len(results_df) * 100
missing_ok = missing_pct < 10
checks.append((f'Missing values < 10% ({missing_pct:.1f}%)', missing_ok))

# Check 4: Reasonable performance metrics
rmse_ok = summary_df['rmse'].mean() < 1.0
checks.append((f'Reasonable RMSE ({summary_df["rmse"].mean():.4f} < 1.0)', rmse_ok))

# Check 5: Coverage rates reasonable
coverage_ok = (summary_df['coverage_rate'].mean() > 0.80) and (summary_df['coverage_rate'].mean() < 1.0)
checks.append((f'Coverage rates reasonable ({summary_df["coverage_rate"].mean():.3f})', coverage_ok))

print("")
for check_name, check_passed in checks:
    status = "✓ PASS" if check_passed else "✗ FAIL"
    print(f"  {status}: {check_name}")

all_passed = all(check[1] for check in checks)

print("\n" + "=" * 80)
if all_passed:
    print("✓ ALL CHECKS PASSED - Setup is working correctly!")
    print("\nYou can now run the full simulation with:")
    print("  python run_full_factorial_simulation.py")
    print("\nOr use the Jupyter notebook:")
    print("  jupyter notebook notebooks/full_factorial_analysis.ipynb")
else:
    print("⚠ SOME CHECKS FAILED - Please review the results above")
print("=" * 80)
