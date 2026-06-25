"""
Run Full Factorial Design Simulation Study
==========================================

This script runs the complete Monte Carlo simulation across all 54 scenarios
from the full factorial design:
- 3 sample sizes (500, 1000, 2000)
- 3 treatment prevalences (0.3, 0.5, 0.7)
- 3 overlap levels (low, medium, high)
- 2 confounding strengths (weak, strong)

Total: 3 × 3 × 3 × 2 = 54 scenarios

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from config import (
    N_REPLICATIONS, RESULTS_DIR, FIGURES_DIR, TABLES_DIR,
    generate_all_scenarios
)
from simulation_runner import run_full_simulation, summarize_results
from visualization import (
    plot_factorial_heatmaps,
    plot_method_ranking_across_scenarios,
    create_comprehensive_comparison_table,
    plot_scenario_factor_effects,
    create_scenario_comparison_figure,
    plot_method_comparison_boxplot
)


def main():
    """Run full factorial simulation and generate all outputs."""
    
    print("=" * 80)
    print("FULL FACTORIAL SIMULATION STUDY")
    print("=" * 80)
    print("\nSimulation Design:")
    print("  - Sample sizes: 500, 1000, 2000")
    print("  - Treatment prevalences: 0.3, 0.5, 0.7")
    print("  - Overlap levels: low, medium, high")
    print("  - Confounding strengths: weak, strong")
    print(f"  - Total scenarios: 54")
    print(f"  - Replications per scenario: {N_REPLICATIONS}")
    print(f"  - Total simulations: {54 * N_REPLICATIONS:,}")
    print("\n" + "=" * 80)
    
    # Generate all scenarios
    scenarios = generate_all_scenarios()
    print(f"\nGenerated {len(scenarios)} scenarios")
    
    # Print scenario summary
    print("\nScenario Summary:")
    print("-" * 80)
    for i, scenario in enumerate(scenarios[:5]):  # Show first 5
        print(f"  Scenario {scenario['scenario_id']}: {scenario['description']}")
    print(f"  ... ({len(scenarios) - 5} more scenarios)")
    print("-" * 80)
    
    # Ask for confirmation
    response = input("\nProceed with full simulation? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Simulation cancelled.")
        return
    
    # Run simulation
    print("\n" + "=" * 80)
    print("RUNNING SIMULATION...")
    print("=" * 80)
    start_time = time.time()
    
    results_df = run_full_simulation(
        scenarios=scenarios,
        n_replications=N_REPLICATIONS,
        n_jobs=-1,  # Use all available cores
        save_intermediate=True,
        verbose=True
    )
    
    elapsed_time = time.time() - start_time
    print(f"\n{'=' * 80}")
    print(f"SIMULATION COMPLETED in {elapsed_time/60:.1f} minutes")
    print(f"{'=' * 80}")
    
    # Summarize results
    print("\nGenerating summary statistics...")
    summary_df = summarize_results(results_df)
    summary_df.to_csv(TABLES_DIR / 'simulation_summary.csv', index=False)
    print(f"  ✓ Summary saved to {TABLES_DIR / 'simulation_summary.csv'}")
    
    # Generate comprehensive comparison table
    print("\nGenerating comprehensive comparison table...")
    comparison_table = create_comprehensive_comparison_table(
        summary_df,
        save_path=TABLES_DIR / 'comprehensive_comparison.csv'
    )
    print(f"  ✓ Table saved to {TABLES_DIR / 'comprehensive_comparison.csv'}")
    print("\nOverall Performance Across All Scenarios:")
    print(comparison_table.to_string())
    
    # Generate visualizations
    print("\n" + "=" * 80)
    print("GENERATING VISUALIZATIONS...")
    print("=" * 80)
    
    # 1. Factorial design heatmaps
    print("\n1. Creating factorial design heatmaps...")
    heatmap_figs = plot_factorial_heatmaps(
        summary_df,
        save_dir=FIGURES_DIR
    )
    print(f"  ✓ Generated {len(heatmap_figs)} heatmaps")
    
    # 2. Method rankings
    print("\n2. Creating method ranking visualizations...")
    for metric in ['rmse', 'mean_abs_bias', 'coverage_rate', 'mean_max_smd']:
        fig = plot_method_ranking_across_scenarios(
            summary_df,
            metric=metric,
            save_path=FIGURES_DIR / f'method_rankings_{metric}.png'
        )
        plt.close(fig)
    print("  ✓ Method rankings saved")
    
    # 3. Factor effects
    print("\n3. Creating factorial design factor effect plots...")
    for metric in ['rmse', 'mean_abs_bias', 'coverage_rate', 'mean_retention']:
        fig = plot_scenario_factor_effects(
            summary_df,
            metric=metric,
            save_path=FIGURES_DIR / f'factor_effects_{metric}.png'
        )
        plt.close(fig)
    print("  ✓ Factor effect plots saved")
    
    # 4. Scenario comparison figure
    print("\n4. Creating scenario comparison figure...")
    fig = create_scenario_comparison_figure(
        summary_df,
        save_path=FIGURES_DIR / 'scenario_comparison.png'
    )
    plt.close(fig)
    print("  ✓ Scenario comparison saved")
    
    # 5. Boxplots for main metrics
    print("\n5. Creating method comparison boxplots...")
    for metric in ['bias', 'mse', 'max_smd', 'retention', 'coverage']:
        fig = plot_method_comparison_boxplot(
            results_df,
            metric=metric,
            save_path=FIGURES_DIR / f'boxplot_{metric}.png'
        )
        plt.close(fig)
    print("  ✓ Boxplots saved")
    
    # Generate detailed scenario-by-scenario results
    print("\n6. Creating scenario-specific detailed results...")
    scenario_results = []
    for scenario_id in summary_df['scenario_id'].unique():
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        scenario_results.append(scenario_data)
    
    detailed_df = pd.concat(scenario_results)
    detailed_df.to_csv(TABLES_DIR / 'scenario_detailed_results.csv', index=False)
    print(f"  ✓ Detailed results saved to {TABLES_DIR / 'scenario_detailed_results.csv'}")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    print("\nAverage Performance Across All 54 Scenarios:")
    print("-" * 80)
    summary_by_method = summary_df.groupby('method').agg({
        'mean_retention': 'mean',
        'mean_max_smd': 'mean',
        'mean_abs_bias': 'mean',
        'rmse': 'mean',
        'coverage_rate': 'mean'
    }).round(4)
    print(summary_by_method.to_string())
    
    # Count best-performing method for each scenario
    print("\n\nMethod Performance Summary:")
    print("-" * 80)
    
    best_rmse = summary_df.loc[summary_df.groupby('scenario_id')['rmse'].idxmin()]
    best_counts = best_rmse['method'].value_counts()
    print("\nScenarios where each method achieved lowest RMSE:")
    for method, count in best_counts.items():
        pct = count / 54 * 100
        print(f"  {method:20s}: {count:2d} / 54 ({pct:5.1f}%)")
    
    best_balance = summary_df.loc[summary_df.groupby('scenario_id')['mean_max_smd'].idxmin()]
    best_balance_counts = best_balance['method'].value_counts()
    print("\nScenarios where each method achieved best balance (lowest max |SMD|):")
    for method, count in best_balance_counts.items():
        pct = count / 54 * 100
        print(f"  {method:20s}: {count:2d} / 54 ({pct:5.1f}%)")
    
    # Count scenarios where methods achieved good balance
    good_balance = summary_df[summary_df['mean_max_smd'] <= 0.1]
    balance_counts = good_balance.groupby('method').size()
    print("\nScenarios where each method achieved good balance (max |SMD| ≤ 0.1):")
    for method in summary_df['method'].unique():
        count = balance_counts.get(method, 0)
        pct = count / 54 * 100
        print(f"  {method:20s}: {count:2d} / 54 ({pct:5.1f}%)")
    
    print("\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print(f"\nAll results saved to:")
    print(f"  - Raw results: {RESULTS_DIR}")
    print(f"  - Tables: {TABLES_DIR}")
    print(f"  - Figures: {FIGURES_DIR}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
