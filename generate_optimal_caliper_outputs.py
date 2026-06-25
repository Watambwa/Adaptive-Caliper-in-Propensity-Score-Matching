"""
Generate Optimal Caliper Tables and Visualizations
===================================================

This script generates the new optimal caliper analysis outputs using existing
simulation results. It creates:

1. Table 8: Optimal caliper by method for all 54 scenarios
2. Improved trade-off grid (fig2_improved_tradeoff_grid.png)
3. Method-specific optimal caliper visualizations
4. Comprehensive optimal caliper dashboard

Run this script after the main simulation to generate additional outputs.

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from config import FIGURES_DIR, TABLES_DIR
from visualization import (
    generate_optimal_caliper_by_method_table,
    plot_optimal_caliper_by_method,
    plot_improved_tradeoff_grid,
    plot_optimal_caliper_summary_dashboard
)


def main():
    """Generate optimal caliper analysis outputs."""
    
    print("=" * 80)
    print("OPTIMAL CALIPER ANALYSIS - ADDITIONAL OUTPUTS")
    print("=" * 80)
    
    # Load existing simulation summary
    summary_path = TABLES_DIR / 'simulation_summary.csv'
    
    if not summary_path.exists():
        print(f"\n❌ Error: Simulation summary not found at {summary_path}")
        print("Please run the full simulation first using run_full_factorial_simulation.py")
        return
    
    print(f"\nLoading simulation summary from {summary_path}...")
    summary_df = pd.read_csv(summary_path)
    print(f"  ✓ Loaded {len(summary_df)} rows ({len(summary_df['scenario_id'].unique())} scenarios)")
    
    # 1. Generate Table 8: Optimal caliper by method
    print("\n" + "=" * 80)
    print("1. GENERATING TABLE 8: OPTIMAL CALIPER BY METHOD")
    print("=" * 80)
    
    optimal_by_method_df = generate_optimal_caliper_by_method_table(
        summary_df, 
        TABLES_DIR,
        balance_threshold=0.1
    )
    
    # Display summary
    print("\n  Summary of Table 8:")
    print("  " + "-" * 60)
    
    # Count methods meeting threshold per scenario
    meets_threshold = optimal_by_method_df[optimal_by_method_df['Meets_Threshold'] == 'Yes']
    method_success = meets_threshold.groupby('Method').size()
    print("\n  Methods achieving balance threshold (max|SMD| < 0.1):")
    for method in ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper', 
                   'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']:
        count = method_success.get(method, 0)
        pct = count / 54 * 100
        print(f"    {method:20s}: {count:2d} / 54 scenarios ({pct:5.1f}%)")
    
    # 2. Generate improved trade-off grid
    print("\n" + "=" * 80)
    print("2. GENERATING IMPROVED TRADE-OFF GRID")
    print("=" * 80)
    
    improved_fig = plot_improved_tradeoff_grid(
        summary_df,
        save_path=FIGURES_DIR / 'fig2_improved_tradeoff_grid.png'
    )
    plt.close(improved_fig)
    print("  ✓ Saved: fig2_improved_tradeoff_grid.png")
    
    # 3. Generate method-specific visualizations
    print("\n" + "=" * 80)
    print("3. GENERATING METHOD-SPECIFIC OPTIMAL CALIPER VISUALIZATIONS")
    print("=" * 80)
    
    method_figs = plot_optimal_caliper_by_method(
        summary_df,
        save_dir=FIGURES_DIR,
        balance_threshold=0.1
    )
    
    for method, fig in method_figs.items():
        plt.close(fig)
    
    # 4. Generate comprehensive dashboard
    print("\n" + "=" * 80)
    print("4. GENERATING OPTIMAL CALIPER SUMMARY DASHBOARD")
    print("=" * 80)
    
    dashboard_fig = plot_optimal_caliper_summary_dashboard(
        summary_df,
        save_path=FIGURES_DIR / 'optimal_caliper_dashboard.png'
    )
    plt.close(dashboard_fig)
    print("  ✓ Saved: optimal_caliper_dashboard.png")
    
    # Summary
    print("\n" + "=" * 80)
    print("OUTPUTS GENERATED SUCCESSFULLY")
    print("=" * 80)
    
    print("\nNew Tables:")
    print(f"  - {TABLES_DIR / 'table8_optimal_caliper_by_method_all_scenarios.csv'}")
    print(f"  - {TABLES_DIR / 'table8_optimal_caliper_summary.csv'}")
    
    print("\nNew Figures:")
    print(f"  - {FIGURES_DIR / 'fig2_improved_tradeoff_grid.png'}")
    print(f"  - {FIGURES_DIR / 'optimal_caliper_acs_balance.png'}")
    print(f"  - {FIGURES_DIR / 'optimal_caliper_acs_knee.png'}")
    print(f"  - {FIGURES_DIR / 'optimal_caliper_acs_weighted.png'}")
    print(f"  - {FIGURES_DIR / 'optimal_caliper_dashboard.png'}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
