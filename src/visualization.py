"""
Publication-Quality Visualization Module
=========================================

Creates figures and tables for the Adaptive Caliper Selection manuscript.

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from config import (
    PLT_PARAMS, METHOD_COLORS, METHOD_NAMES, 
    FIGURES_DIR, TABLES_DIR, FIGURE_DPI
)

plt.rcParams.update(PLT_PARAMS)
sns.set_style("whitegrid")


def plot_pareto_frontier(
    selector,
    title: str = "Pareto Frontier: Balance vs. Retention Trade-off",
    highlight_optimal: Dict[str, float] = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (8, 6)
) -> plt.Figure:
    """Plot the Pareto frontier with optimal point highlighting."""
    fig, ax = plt.subplots(figsize=figsize)
    
    all_results = selector.get_all_results_dataframe()
    frontier = selector.get_frontier_dataframe()
    
    non_pareto = all_results[~all_results['is_pareto_optimal']]
    ax.scatter(non_pareto['retention'], non_pareto['max_abs_smd'],
               c='lightgray', s=60, alpha=0.6, label='Non-Pareto points', zorder=1)
    
    ax.plot(frontier['retention'], frontier['max_abs_smd'],
            'b-', linewidth=2, zorder=2)
    ax.scatter(frontier['retention'], frontier['max_abs_smd'],
               c='#377EB8', s=100, edgecolors='black', linewidth=1.5,
               label='Pareto frontier', zorder=3)
    
    if highlight_optimal:
        colors = {'balance': '#FF7F00', 'knee': '#4DAF4A', 'weighted': '#984EA3'}
        markers = {'balance': 's', 'knee': '^', 'weighted': 'D'}
        
        for criterion, caliper in highlight_optimal.items():
            point = frontier[frontier['caliper'] == caliper]
            if len(point) > 0:
                ax.scatter(point['retention'].values[0], 
                          point['max_abs_smd'].values[0],
                          c=colors.get(criterion, 'red'),
                          s=200, marker=markers.get(criterion, 'o'),
                          edgecolors='black', linewidth=2,
                          label=f'ACS-{criterion.capitalize()}', zorder=4)
    
    ax.axhline(y=0.1, color='red', linestyle='--', linewidth=1.5, 
               alpha=0.7, label='Balance threshold (0.1)')
    
    ax.set_xlabel('Sample Retention Rate', fontsize=12, fontweight='bold')
    ax.set_ylabel('Maximum |SMD|', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper right', framealpha=0.95, fontsize=9)
    ax.set_xlim(0, 1.05)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_method_comparison_boxplot(
    results_df: pd.DataFrame,
    metric: str = 'bias',
    title: str = None,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (10, 6)
) -> plt.Figure:
    """Create boxplot comparing methods across scenarios."""
    metric_labels = {
        'bias': 'Bias',
        'mse': 'Mean Squared Error',
        'max_smd': 'Maximum |SMD|',
        'retention': 'Sample Retention Rate',
        'coverage': 'Coverage Probability'
    }
    
    fig, ax = plt.subplots(figsize=figsize)
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    colors = [METHOD_COLORS.get(m, 'gray') for m in method_order]
    plot_data = results_df[results_df['method'].isin(method_order)]
    
    bp = ax.boxplot([plot_data[plot_data['method'] == m][metric].dropna() 
                     for m in method_order],
                    labels=[METHOD_NAMES.get(m, m) for m in method_order],
                    patch_artist=True, widths=0.6)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(2)
    
    if metric == 'bias':
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    elif metric == 'coverage':
        ax.axhline(y=0.95, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    elif metric == 'max_smd':
        ax.axhline(y=0.1, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    
    ax.set_ylabel(metric_labels.get(metric, metric), fontsize=12, fontweight='bold')
    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    
    if title is None:
        title = f'Comparison of {metric_labels.get(metric, metric)} Across Methods'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    
    plt.xticks(rotation=45, ha='right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_ps_distribution(
    df: pd.DataFrame,
    ps_col: str = 'e_hat',
    title: str = "Propensity Score Distribution by Treatment Group",
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (10, 6)
) -> plt.Figure:
    """Plot propensity score distributions for treated and control groups."""
    fig, ax = plt.subplots(figsize=figsize)
    
    treated = df[df['Z'] == 1][ps_col]
    control = df[df['Z'] == 0][ps_col]
    
    ax.hist(control, bins=50, alpha=0.6, color='#377EB8', 
            label=f'Control (n={len(control)})', density=True)
    ax.hist(treated, bins=50, alpha=0.6, color='#E41A1C',
            label=f'Treated (n={len(treated)})', density=True)
    
    common_min = max(treated.min(), control.min())
    common_max = min(treated.max(), control.max())
    ax.axvline(x=common_min, color='green', linestyle='--', linewidth=2)
    ax.axvline(x=common_max, color='green', linestyle='--', linewidth=2,
               label='Common support')
    
    ax.set_xlabel('Propensity Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Density', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper right', framealpha=0.95, fontsize=10)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_love_plot(
    before_balance: pd.DataFrame,
    after_balance: pd.DataFrame,
    title: str = "Covariate Balance: Before vs. After Matching",
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (8, 6)
) -> plt.Figure:
    """Create Love plot showing balance improvement."""
    fig, ax = plt.subplots(figsize=figsize)
    
    covariates = before_balance['covariate'].values
    y_pos = np.arange(len(covariates))
    
    ax.scatter(before_balance['abs_smd'], y_pos, 
               c='#E41A1C', s=100, marker='o', label='Before matching', zorder=3)
    ax.scatter(after_balance['abs_smd'], y_pos,
               c='#377EB8', s=100, marker='s', label='After matching', zorder=3)
    
    for i in range(len(covariates)):
        ax.plot([before_balance['abs_smd'].iloc[i], after_balance['abs_smd'].iloc[i]],
                [y_pos[i], y_pos[i]], 'k-', alpha=0.3, linewidth=1)
    
    ax.axvline(x=0.1, color='red', linestyle='--', linewidth=2, label='Threshold (0.1)')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(covariates)
    ax.set_xlabel('Absolute Standardized Mean Difference', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper right', framealpha=0.95, fontsize=9)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_heatmap_by_scenario(
    summary_df: pd.DataFrame,
    metric: str = 'mean_mse',
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (14, 10)
) -> plt.Figure:
    """Create heatmap showing metric across scenarios and methods."""
    pivot_data = summary_df.pivot_table(
        values=metric,
        index=['n', 'overlap_name', 'confounding_name'],
        columns='method',
        aggfunc='mean'
    )
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    pivot_data = pivot_data[[m for m in method_order if m in pivot_data.columns]]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='RdYlGn_r',
                ax=ax, cbar_kws={'label': metric})
    
    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('Scenario (n, overlap, confounding)', fontsize=12, fontweight='bold')
    ax.set_title(f'{metric} Across Scenarios and Methods',
                 fontsize=14, fontweight='bold', pad=15)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def create_summary_table(
    summary_df: pd.DataFrame,
    save_path: Optional[Path] = None
) -> pd.DataFrame:
    """Create publication-ready summary table."""
    method_summary = summary_df.groupby('method').agg({
        'mean_retention': 'mean',
        'mean_max_smd': 'mean',
        'mean_abs_bias': 'mean',
        'rmse': 'mean',
        'coverage_rate': 'mean',
        'mean_ci_width': 'mean'
    }).round(4)
    
    method_summary.columns = [
        'Retention', 'Max |SMD|', '|Bias|', 'RMSE', 'Coverage', 'CI Width'
    ]
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    method_summary = method_summary.reindex(
        [m for m in method_order if m in method_summary.index]
    )
    
    if save_path:
        method_summary.to_csv(save_path)
    
    return method_summary


def create_scenario_comparison_figure(
    summary_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (18, 14)
) -> plt.Figure:
    """
    Create comprehensive multi-panel figure comparing all methods across all 54 scenarios.
    Uses a 3×2 grid with professional formatting.
    """
    fig, axes = plt.subplots(3, 2, figsize=figsize)
    
    metrics = [
        ('mean_abs_bias', 'Mean Absolute Bias', 0.0),
        ('rmse', 'Root Mean Squared Error', None),
        ('coverage_rate', '95% CI Coverage Rate', 0.95),
        ('mean_retention', 'Sample Retention Rate', None),
        ('mean_max_smd', 'Maximum |SMD|', 0.1),
        ('mean_ci_width', 'Confidence Interval Width', None)
    ]
    
    # Include ALL 7 methods
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    # Get unique scenarios
    n_scenarios = summary_df['scenario_id'].nunique()
    
    for ax, (metric, label, reference_line) in zip(axes.flat, metrics):
        for method in method_order:
            method_data = summary_df[summary_df['method'] == method].sort_values('scenario_id')
            color = METHOD_COLORS.get(method, 'gray')
            
            # Use smaller markers and thinner lines for 54 scenarios
            ax.plot(method_data['scenario_id'], method_data[metric],
                   '-', color=color, label=METHOD_NAMES.get(method, method),
                   linewidth=1.2, alpha=0.75)
            
            # Add markers every 9 scenarios (6 data points) for clarity
            marker_indices = list(range(0, len(method_data), 9))
            ax.plot(method_data['scenario_id'].iloc[marker_indices], 
                   method_data[metric].iloc[marker_indices],
                   'o', color=color, markersize=3, alpha=0.75)
        
        # Add reference lines where appropriate
        if reference_line is not None:
            line_label = 'Target' if metric == 'coverage_rate' else 'Threshold'
            ax.axhline(y=reference_line, color='red', linestyle='--', 
                      linewidth=1.5, alpha=0.6, label=line_label)
        
        # Formatting
        ax.set_xlabel('Scenario ID', fontsize=10, fontweight='bold')
        ax.set_ylabel(label, fontsize=10, fontweight='bold')
        ax.set_title(label, fontsize=11, fontweight='bold', pad=10)
        ax.set_xlim(0, n_scenarios + 1)
        
        # Add vertical lines to separate factor levels (every 18 scenarios = full cycle of prevalence×overlap×confounding)
        for i in range(18, n_scenarios, 18):
            ax.axvline(x=i+0.5, color='gray', linestyle=':', linewidth=0.8, alpha=0.3)
        
        # Grid for readability
        ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Set x-axis ticks to show key scenarios
        ax.set_xticks([1, 10, 20, 30, 40, 50, n_scenarios])
    
    # Create legend with all 7 methods
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=4, 
               bbox_to_anchor=(0.5, 0.99), fontsize=9,
               frameon=True, fancybox=True, shadow=True)
    
    fig.suptitle('Performance Comparison Across All 54 Factorial Design Scenarios\n' + 
                'Scenarios organized by: Sample Size (1-18: n=500 | 19-36: n=1000 | 37-54: n=2000)',
                fontsize=13, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_factorial_heatmaps(
    summary_df: pd.DataFrame,
    metrics: List[str] = None,
    save_dir: Optional[Path] = None,
    figsize: Tuple[float, float] = (18, 10)
) -> Dict[str, plt.Figure]:
    """
    Create heatmaps for each metric across factorial design factors.
    Uses a 2×4 grid layout for professional presentation.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics by scenario and method
    metrics : list of str, optional
        Metrics to plot. Defaults to main metrics.
    save_dir : Path, optional
        Directory to save figures
    figsize : tuple
        Figure size for each heatmap
        
    Returns
    -------
    figures : dict
        Dictionary mapping metric names to figure objects
    """
    if metrics is None:
        metrics = ['mean_abs_bias', 'rmse', 'coverage_rate', 
                   'mean_retention', 'mean_max_smd']
    
    metric_labels = {
        'mean_abs_bias': 'Mean Absolute Bias',
        'rmse': 'RMSE',
        'coverage_rate': 'Coverage Rate',
        'mean_retention': 'Sample Retention',
        'mean_max_smd': 'Max |SMD|'
    }
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    figures = {}
    
    for metric in metrics:
        # Create 2×4 grid (2 rows, 4 columns for 7 methods + 1 empty)
        fig, axes = plt.subplots(2, 4, figsize=figsize, sharex=True, sharey=True)
        axes = axes.flatten()
        
        # Determine color scale limits for consistency
        all_values = []
        for method in method_order:
            method_data = summary_df[summary_df['method'] == method]
            if len(method_data) > 0:
                all_values.extend(method_data[metric].dropna().values)
        
        if len(all_values) > 0:
            vmin, vmax = np.percentile(all_values, [2, 98])
        else:
            vmin, vmax = None, None
        
        for idx, method in enumerate(method_order):
            ax = axes[idx]
            
            # Create pivot table for this method
            pivot_data = summary_df[summary_df['method'] == method].pivot_table(
                values=metric,
                index=['overlap_name', 'confounding_name'],
                columns=['n', 'treatment_prevalence'],
                aggfunc='mean'
            )
            
            # Sort index and columns for consistency
            pivot_data = pivot_data.sort_index()
            pivot_data = pivot_data.reindex(
                columns=sorted(pivot_data.columns, key=lambda x: (x[0], x[1]))
            )
            
            # Create heatmap with better formatting
            cmap = 'RdYlGn' if metric in ['coverage_rate', 'mean_retention'] else 'RdYlGn_r'
            
            sns.heatmap(pivot_data, annot=True, fmt='.2f',  # 2 decimal places
                       cmap=cmap, ax=ax, cbar=True,
                       vmin=vmin, vmax=vmax,
                       annot_kws={'fontsize': 8, 'fontweight': 'bold'},
                       cbar_kws={'label': metric_labels.get(metric, metric),
                                'shrink': 0.8},
                       linewidths=0.5, linecolor='white')
            
            ax.set_title(METHOD_NAMES.get(method, method), 
                        fontsize=11, fontweight='bold', pad=8)
            ax.set_xlabel('(Sample Size, Prevalence)', fontsize=9, fontweight='bold')
            ax.set_ylabel('(Overlap, Confounding)' if idx % 4 == 0 else '', 
                         fontsize=9, fontweight='bold')
            
            # Improve tick labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
            plt.setp(ax.get_yticklabels(), rotation=0, fontsize=8)
        
        # Hide the last subplot (8th position) since we only have 7 methods
        axes[7].set_visible(False)
        
        fig.suptitle(f'{metric_labels.get(metric, metric)} Across All 54 Scenarios\n' + 
                    'Full Factorial Design: 3 Sample Sizes × 3 Prevalences × 3 Overlap Levels × 2 Confounding Strengths',
                    fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        figures[metric] = fig
        
        if save_dir:
            fig.savefig(save_dir / f'fig{list(metrics).index(metric)+1}_heatmap_{metric}.png', 
                       dpi=FIGURE_DPI, bbox_inches='tight')
    
    return figures


def plot_method_ranking_across_scenarios(
    summary_df: pd.DataFrame,
    metric: str = 'rmse',
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (14, 8)
) -> plt.Figure:
    """
    Create visualization showing method rankings across all scenarios.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics
    metric : str
        Metric to rank by (lower is better)
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : plt.Figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    # Left panel: Average rank across scenarios
    ranks = []
    for scenario_id in summary_df['scenario_id'].unique():
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        scenario_data = scenario_data.sort_values(metric)
        scenario_data['rank'] = range(1, len(scenario_data) + 1)
        ranks.append(scenario_data[['method', 'rank']])
    
    ranks_df = pd.concat(ranks)
    avg_ranks = ranks_df.groupby('method')['rank'].mean().sort_values()
    
    colors = [METHOD_COLORS.get(m, 'gray') for m in avg_ranks.index]
    ax1.barh(range(len(avg_ranks)), avg_ranks.values, color=colors, alpha=0.7)
    ax1.set_yticks(range(len(avg_ranks)))
    ax1.set_yticklabels([METHOD_NAMES.get(m, m) for m in avg_ranks.index])
    ax1.set_xlabel('Average Rank (lower is better)', fontsize=11, fontweight='bold')
    ax1.set_title('Average Method Ranking Across All Scenarios', 
                 fontsize=12, fontweight='bold')
    ax1.invert_yaxis()
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Right panel: Win rate (% of scenarios where method is best)
    win_counts = ranks_df[ranks_df['rank'] == 1]['method'].value_counts()
    win_rates = (win_counts / summary_df['scenario_id'].nunique() * 100).reindex(
        method_order, fill_value=0
    )
    
    colors = [METHOD_COLORS.get(m, 'gray') for m in win_rates.index]
    ax2.barh(range(len(win_rates)), win_rates.values, color=colors, alpha=0.7)
    ax2.set_yticks(range(len(win_rates)))
    ax2.set_yticklabels([METHOD_NAMES.get(m, m) for m in win_rates.index])
    ax2.set_xlabel('% Scenarios Where Best', fontsize=11, fontweight='bold')
    ax2.set_title('Method Win Rate', fontsize=12, fontweight='bold')
    ax2.invert_yaxis()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def create_comprehensive_comparison_table(
    summary_df: pd.DataFrame,
    save_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Create comprehensive table comparing all methods across all scenarios.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics
    save_path : Path, optional
        Path to save CSV
        
    Returns
    -------
    comparison_table : pd.DataFrame
        Comprehensive comparison table
    """
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    # Overall summary across all scenarios
    overall = summary_df.groupby('method').agg({
        'mean_retention': ['mean', 'std'],
        'mean_max_smd': ['mean', 'std'],
        'mean_abs_bias': ['mean', 'std'],
        'rmse': ['mean', 'std'],
        'coverage_rate': ['mean', 'std'],
        'mean_ci_width': ['mean', 'std']
    }).round(4)
    
    overall.columns = ['_'.join(col).strip() for col in overall.columns.values]
    overall = overall.reindex([m for m in method_order if m in overall.index])
    
    # Add performance metrics
    # Count scenarios where method achieves balance (max_smd <= 0.1)
    balanced = summary_df[summary_df['mean_max_smd'] <= 0.1].groupby('method').size()
    overall['n_scenarios_balanced'] = balanced
    overall['pct_scenarios_balanced'] = (balanced / summary_df['scenario_id'].nunique() * 100).round(1)
    
    # Count scenarios where coverage is within 93-97%
    good_coverage = summary_df[
        (summary_df['coverage_rate'] >= 0.93) & 
        (summary_df['coverage_rate'] <= 0.97)
    ].groupby('method').size()
    overall['n_scenarios_good_coverage'] = good_coverage
    overall['pct_scenarios_good_coverage'] = (good_coverage / summary_df['scenario_id'].nunique() * 100).round(1)
    
    if save_path:
        overall.to_csv(save_path)
        
        # Also create a formatted version
        formatted_path = save_path.parent / f"{save_path.stem}_formatted.csv"
        formatted = overall.copy()
        for col in formatted.columns:
            if 'mean' in col or 'rmse' in col:
                base = col.replace('_mean', '').replace('_std', '')
                if base + '_std' in formatted.columns:
                    formatted[base] = (
                        formatted[col.replace('_std', '_mean')].astype(str) + 
                        ' ± ' + 
                        formatted[base + '_std'].astype(str)
                    )
        formatted.to_csv(formatted_path)
    
    return overall


def plot_individual_scenario_tracking(
    summary_df: pd.DataFrame,
    metrics: List[str] = None,
    save_dir: Optional[Path] = None,
    figsize: Tuple[float, float] = (16, 5)
) -> Dict[str, plt.Figure]:
    """
    Create individual scenario tracking plots for each metric (Fig 1-6).
    Each plot shows all 7 methods across all 54 scenarios in a compact format.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics
    metrics : list of str, optional
        Metrics to plot
    save_dir : Path, optional
        Directory to save figures
    figsize : tuple
        Figure size
        
    Returns
    -------
    figures : dict
        Dictionary mapping metric names to figure objects
    """
    if metrics is None:
        metrics = [
            ('mean_abs_bias', 'Mean Absolute Bias', 0.0),
            ('rmse', 'Root Mean Squared Error (RMSE)', None),
            ('coverage_rate', '95% Confidence Interval Coverage Rate', 0.95),
            ('mean_retention', 'Sample Retention Rate', None),
            ('mean_max_smd', 'Maximum Absolute SMD (Balance)', 0.1),
            ('mean_ci_width', 'Confidence Interval Width', None)
        ]
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    n_scenarios = summary_df['scenario_id'].nunique()
    figures = {}
    
    for fig_num, (metric, label, reference_line) in enumerate(metrics, 1):
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        # Plot each method
        for method in method_order:
            method_data = summary_df[summary_df['method'] == method].sort_values('scenario_id')
            color = METHOD_COLORS.get(method, 'gray')
            
            ax.plot(method_data['scenario_id'], method_data[metric],
                   '-', color=color, label=METHOD_NAMES.get(method, method),
                   linewidth=2, alpha=0.8)
            
            # Add subtle markers every 6 scenarios
            marker_indices = list(range(0, len(method_data), 6))
            ax.plot(method_data['scenario_id'].iloc[marker_indices], 
                   method_data[metric].iloc[marker_indices],
                   'o', color=color, markersize=4, alpha=0.8)
        
        # Add reference lines
        if reference_line is not None:
            line_style = '--' if metric == 'coverage_rate' else ':'
            line_label = 'Target (0.95)' if metric == 'coverage_rate' else f'Threshold ({reference_line})'
            ax.axhline(y=reference_line, color='red', linestyle=line_style, 
                      linewidth=2, alpha=0.7, label=line_label, zorder=10)
        
        # Add vertical lines to separate sample sizes
        for i in [18.5, 36.5]:
            ax.axvline(x=i, color='gray', linestyle=':', linewidth=1.5, alpha=0.4)
        
        # Add background shading for sample sizes
        ax.axvspan(0.5, 18.5, alpha=0.05, color='blue', zorder=0)
        ax.axvspan(18.5, 36.5, alpha=0.05, color='green', zorder=0)
        ax.axvspan(36.5, n_scenarios+0.5, alpha=0.05, color='orange', zorder=0)
        
        # Add sample size labels
        ax.text(9.5, ax.get_ylim()[1]*0.98, 'n=500', 
               ha='center', va='top', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='blue'))
        ax.text(27.5, ax.get_ylim()[1]*0.98, 'n=1000', 
               ha='center', va='top', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='green'))
        ax.text(45.5, ax.get_ylim()[1]*0.98, 'n=2000', 
               ha='center', va='top', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='orange'))
        
        # Formatting
        ax.set_xlabel('Scenario ID', fontsize=12, fontweight='bold')
        ax.set_ylabel(label, fontsize=12, fontweight='bold')
        ax.set_title(f'Figure {fig_num}: {label} Across All 54 Scenarios\n' + 
                    'Full Factorial Design: 3 Sample Sizes × 3 Prevalences × 3 Overlaps × 2 Confounding Levels',
                    fontsize=13, fontweight='bold', pad=15)
        ax.set_xlim(0.5, n_scenarios + 0.5)
        
        # Set x-axis ticks
        ax.set_xticks([1, 6, 12, 18, 24, 30, 36, 42, 48, 54])
        ax.tick_params(axis='both', which='major', labelsize=10)
        
        # Grid
        ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, which='major')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Legend
        ax.legend(ncol=4, fontsize=9, 
                 frameon=True, fancybox=True, shadow=True,
                 bbox_to_anchor=(0.5, -0.15), loc='upper center')
        
        plt.tight_layout()
        
        figures[metric] = fig
        
        if save_dir:
            fig.savefig(save_dir / f'fig{fig_num}_scenario_tracking_{metric}.png', 
                       dpi=FIGURE_DPI, bbox_inches='tight')
    
    return figures


def plot_all_tradeoff_spaces_grid(
    summary_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (22, 30)
) -> plt.Figure:
    """
    Create a 9×6 grid showing balance-retention trade-off for all 54 scenarios.
    Shows all 7 methods positioned in the trade-off space for each scenario.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary results by scenario and method
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    # Get unique scenarios
    scenarios = sorted(summary_df['scenario_id'].unique())
    
    # Create 9×6 grid (54 subplots)
    fig, axes = plt.subplots(9, 6, figsize=figsize, sharex=True, sharey=True)
    axes = axes.flatten()
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    for idx, scenario_id in enumerate(scenarios):
        ax = axes[idx]
        
        # Get data for this scenario
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        if len(scenario_data) == 0:
            continue
            
        # Get scenario characteristics
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        
        # Plot each method
        for method in method_order:
            method_data = scenario_data[scenario_data['method'] == method]
            if len(method_data) == 0:
                continue
                
            retention = method_data['mean_retention'].values[0]
            max_smd = method_data['mean_max_smd'].values[0]
            color = METHOD_COLORS.get(method, 'gray')
            
            # Plot point with method-specific marker
            if 'ACS' in method:
                marker = 's'  # Square for adaptive
                markersize = 7
                alpha = 0.9
            else:
                marker = 'o'  # Circle for fixed
                markersize = 6
                alpha = 0.7
            
            ax.scatter(retention, max_smd, c=color, marker=marker,
                      s=markersize**2, alpha=alpha, 
                      edgecolors='black', linewidths=0.5, zorder=3)
        
        # Connect points to show trade-off frontier
        method_data_all = scenario_data[scenario_data['method'].isin(method_order)]
        sorted_methods = method_data_all.sort_values('mean_retention')
        ax.plot(sorted_methods['mean_retention'], sorted_methods['mean_max_smd'],
               '-', color='gray', linewidth=0.5, alpha=0.3, zorder=1)
        
        # Balance threshold
        ax.axhline(y=0.1, color='green', linestyle='--', 
                  linewidth=1.5, alpha=0.6, zorder=0)
        ax.axhspan(0, 0.1, alpha=0.1, color='green', zorder=0)
        
        # Formatting
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 0.6)
        
        # Title with scenario info
        title = f"Scenario {scenario_id}\nn={n}, prev={prev:.1f}, {overlap[:3]}, {conf[:4]}"
        ax.set_title(title, fontsize=7, pad=4, fontweight='bold')
        
        # Grid
        ax.grid(True, alpha=0.25, linewidth=0.4, linestyle=':')
        ax.tick_params(labelsize=6)
        
        # Add subtle background color based on sample size
        if n == 500:
            ax.set_facecolor('#f0f8ff')  # Light blue
        elif n == 1000:
            ax.set_facecolor('#f0fff0')  # Light green
        else:  # 2000
            ax.set_facecolor('#fff8f0')  # Light orange
    
    # Set common axis labels
    for i in range(9):
        axes[i*6].set_ylabel('Max |SMD| (Balance)', fontsize=9, fontweight='bold')
    for i in range(48, 54):
        axes[i].set_xlabel('Retention Rate', fontsize=9, fontweight='bold')
    
    # Create custom legend
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=METHOD_COLORS['Fixed-0.1'],
               markersize=6, label='Fixed-0.1', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=METHOD_COLORS['Fixed-0.2'],
               markersize=6, label='Fixed-0.2', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=METHOD_COLORS['Fixed-0.5'],
               markersize=6, label='Fixed-0.5', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=METHOD_COLORS['No Caliper'],
               markersize=6, label='No Caliper', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], marker='s', color='w', markerfacecolor=METHOD_COLORS['ACS-Balance'],
               markersize=7, label='ACS-Balance', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], marker='s', color='w', markerfacecolor=METHOD_COLORS['ACS-Knee'],
               markersize=7, label='ACS-Knee', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], marker='s', color='w', markerfacecolor=METHOD_COLORS['ACS-Weighted'],
               markersize=7, label='ACS-Weighted', markeredgecolor='black', markeredgewidth=0.5),
        Line2D([0], [0], color='green', linestyle='--', linewidth=1.5,
               label='Balance Threshold (0.1)'),
    ]
    
    fig.legend(handles=legend_elements, loc='upper center', ncol=4,
              bbox_to_anchor=(0.5, 0.995), fontsize=9, frameon=True,
              fancybox=True, shadow=True)
    
    # Overall title
    fig.suptitle('Balance-Retention Trade-off Across All 54 Factorial Design Scenarios\n' + 
                'Circles: Fixed calipers | Squares: Adaptive methods | Green shading: Acceptable balance region',
                fontsize=13, fontweight='bold', y=0.998)
    
    plt.tight_layout(rect=[0, 0, 1, 0.992])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def generate_all_scenario_tables(
    summary_df: pd.DataFrame,
    results_df: pd.DataFrame,
    save_dir: Path
) -> Dict[str, pd.DataFrame]:
    """
    Generate comprehensive tables for all 54 scenarios.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics by scenario and method
    results_df : pd.DataFrame
        Raw simulation results
    save_dir : Path
        Directory to save tables
        
    Returns
    -------
    tables : dict
        Dictionary of generated tables
    """
    tables = {}
    
    # TABLE 1: Scenario Definitions (All 54)
    print("  Creating Table 1: Scenario definitions...")
    
    # Get available columns
    available_cols = ['n', 'treatment_prevalence', 'overlap_name', 'confounding_name']
    scenario_def = summary_df.groupby('scenario_id').first()[available_cols].reset_index()
    
    # Create description column
    scenario_def['Description'] = scenario_def.apply(
        lambda row: f"n={row['n']}, prev={row['treatment_prevalence']:.1f}, {row['overlap_name']}, {row['confounding_name']}", 
        axis=1
    )
    
    scenario_def.columns = ['Scenario', 'Sample Size', 'Prevalence', 'Overlap', 'Confounding', 'Description']
    tables['scenario_definitions'] = scenario_def
    scenario_def.to_csv(save_dir / 'table1_scenario_definitions.csv', index=False)
    scenario_def.to_latex(save_dir / 'table1_scenario_definitions.tex', index=False)
    
    # TABLE 2: Pareto Frontier Summary (All 54 scenarios)
    print("  Creating Table 2: Pareto frontier for all scenarios...")
    pareto_data = []
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        
        # Create scenario descriptor
        scenario_desc = f"n={n}, prev={prev:.1f}, {overlap}, {conf}"
        
        # Find methods in acceptable balance region
        balanced_methods = scenario_data[scenario_data['mean_max_smd'] <= 0.1]
        if len(balanced_methods) > 0:
            best_retention = balanced_methods['mean_retention'].max()
            best_method = balanced_methods[
                balanced_methods['mean_retention'] == best_retention
            ]['method'].iloc[0]
            best_balance = balanced_methods[
                balanced_methods['mean_retention'] == best_retention
            ]['mean_max_smd'].iloc[0]
        else:
            best_method = 'None'
            best_retention = 0.0
            best_balance = scenario_data['mean_max_smd'].min()
        
        pareto_data.append({
            'Scenario ID': scenario_id,
            'Scenario': scenario_desc,
            'Best Method': best_method,
            'Retention': f"{best_retention:.3f}",
            'Max |SMD|': f"{best_balance:.3f}",
            'Meets Threshold': 'Yes' if best_balance <= 0.1 else 'No'
        })
    
    pareto_df = pd.DataFrame(pareto_data)
    tables['pareto_frontier'] = pareto_df
    pareto_df.to_csv(save_dir / 'table2_pareto_frontier_all_scenarios.csv', index=False)
    pareto_df.to_latex(save_dir / 'table2_pareto_frontier_all_scenarios.tex', index=False)
    
    # TABLE 3: Performance Metrics by Scenario (All 54 scenarios, all 7 methods)
    print("  Creating Table 3: Performance metrics for all scenarios...")
    
    # Create scenario descriptor column
    perf_df = summary_df.copy()
    perf_df['Scenario'] = perf_df.apply(
        lambda row: f"n={row['n']}, prev={row['treatment_prevalence']:.1f}, {row['overlap_name']}, {row['confounding_name']}", 
        axis=1
    )
    
    # Select columns to include
    output_cols = ['scenario_id', 'Scenario', 'method']
    metric_cols = []
    for col in ['mean_retention', 'mean_max_smd', 'mean_abs_bias', 'rmse', 'coverage_rate', 'mean_ci_width']:
        if col in perf_df.columns:
            metric_cols.append(col)
    
    output_cols.extend(metric_cols)
    perf_df = perf_df[output_cols].copy()
    
    # Create readable column names
    col_mapping = {
        'scenario_id': 'Scenario ID', 'method': 'Method',
        'mean_retention': 'Retention', 'mean_max_smd': 'Max |SMD|', 
        'mean_abs_bias': 'Mean |Bias|', 'rmse': 'RMSE', 
        'coverage_rate': 'Coverage', 'mean_ci_width': 'CI Width'
    }
    perf_df.columns = [col_mapping.get(col, col) for col in perf_df.columns]
    perf_df = perf_df.round(4)
    tables['performance_all_scenarios'] = perf_df
    perf_df.to_csv(save_dir / 'table3_performance_all_scenarios_all_methods.csv', index=False)
    
    # TABLE 4: Method Rankings by Scenario (All 54)
    print("  Creating Table 4: Method rankings for all scenarios...")
    ranking_data = []
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        
        # Create scenario descriptor
        scenario_desc = f"n={n}, prev={prev:.1f}, {overlap}, {conf}"
        
        # Rank methods by RMSE
        scenario_data_sorted = scenario_data.sort_values('rmse')
        ranks = {method: rank+1 for rank, method in enumerate(scenario_data_sorted['method'])}
        
        # Best method (lowest RMSE among threshold-compliant)
        threshold_compliant = scenario_data[scenario_data['mean_max_smd'] <= 0.1]
        if len(threshold_compliant) > 0:
            best = threshold_compliant.sort_values('rmse').iloc[0]
            best_method = best['method']
            best_rmse = best['rmse']
        else:
            best_method = 'None compliant'
            best_rmse = np.nan
        
        ranking_data.append({
            'Scenario ID': scenario_id,
            'Scenario': scenario_desc,
            'Best Method': best_method,
            'Best RMSE': f"{best_rmse:.4f}" if not np.isnan(best_rmse) else 'N/A',
            'Fixed-0.1 Rank': ranks.get('Fixed-0.1', '-'),
            'Fixed-0.2 Rank': ranks.get('Fixed-0.2', '-'),
            'ACS-Balance Rank': ranks.get('ACS-Balance', '-'),
            'ACS-Knee Rank': ranks.get('ACS-Knee', '-')
        })
    
    ranking_df = pd.DataFrame(ranking_data)
    tables['method_rankings'] = ranking_df
    ranking_df.to_csv(save_dir / 'table4_method_rankings_all_scenarios.csv', index=False)
    ranking_df.to_latex(save_dir / 'table4_method_rankings_all_scenarios.tex', index=False)
    
    # TABLE 5: Treatment Effect Comparison (All 54 scenarios, all methods)
    print("  Creating Table 5: Treatment effect estimates for all scenarios...")
    te_data = []
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        # Get scenario characteristics once
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        scenario_desc = f"n={n}, prev={prev:.1f}, {overlap}, {conf}"
        
        for _, row in scenario_data.iterrows():
            # Get bias (prefer mean_bias, fall back to mean_abs_bias)
            bias_val = row.get('mean_bias', row.get('mean_abs_bias', np.nan))
            
            te_data.append({
                'Scenario ID': scenario_id,
                'Scenario': scenario_desc,
                'Method': row['method'],
                'Mean Estimate': f"{row.get('mean_estimate', np.nan):.4f}" if not pd.isna(row.get('mean_estimate')) else 'N/A',
                'Bias': f"{bias_val:.4f}" if not pd.isna(bias_val) else 'N/A',
                'RMSE': f"{row.get('rmse', np.nan):.4f}" if not pd.isna(row.get('rmse')) else 'N/A',
                'Coverage': f"{row.get('coverage_rate', np.nan):.3f}" if not pd.isna(row.get('coverage_rate')) else 'N/A',
                'CI Width': f"{row.get('mean_ci_width', np.nan):.4f}" if not pd.isna(row.get('mean_ci_width')) else 'N/A'
            })
    
    te_df = pd.DataFrame(te_data)
    tables['treatment_effects'] = te_df
    te_df.to_csv(save_dir / 'table5_treatment_effect_comparison_all_scenarios.csv', index=False)
    
    # TABLE 6: Monte Carlo Summary Statistics (All 54 scenarios, all methods)
    print("  Creating Table 6: Monte Carlo summary for all scenarios...")
    mc_data = []
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        # Get scenario characteristics once
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        scenario_desc = f"n={n}, prev={prev:.1f}, {overlap}, {conf}"
        
        for _, row in scenario_data.iterrows():
            mc_data.append({
                'Scenario ID': scenario_id,
                'Scenario': scenario_desc,
                'Method': row['method'],
                'Mean Matched': f"{row.get('mean_n_matched', np.nan):.1f}" if not pd.isna(row.get('mean_n_matched')) else 'N/A',
                'SD Matched': f"{row.get('sd_n_matched', np.nan):.1f}" if not pd.isna(row.get('sd_n_matched')) else 'N/A',
                'Retention': f"{row.get('mean_retention', np.nan):.3f}" if not pd.isna(row.get('mean_retention')) else 'N/A',
                'Max |SMD|': f"{row.get('mean_max_smd', np.nan):.3f}" if not pd.isna(row.get('mean_max_smd')) else 'N/A',
                'Mean Bias': f"{row.get('mean_bias', np.nan):.4f}" if not pd.isna(row.get('mean_bias')) else 'N/A',
                '|Bias|': f"{row.get('mean_abs_bias', np.nan):.4f}" if not pd.isna(row.get('mean_abs_bias')) else 'N/A',
                'RMSE': f"{row.get('rmse', np.nan):.4f}" if not pd.isna(row.get('rmse')) else 'N/A',
                'MSE': f"{row.get('mse', np.nan):.4f}" if not pd.isna(row.get('mse')) else 'N/A',
                'Coverage': f"{row.get('coverage_rate', np.nan):.3f}" if not pd.isna(row.get('coverage_rate')) else 'N/A'
            })
    
    mc_df = pd.DataFrame(mc_data)
    tables['monte_carlo'] = mc_df
    mc_df.to_csv(save_dir / 'table6_monte_carlo_summary_all_scenarios.csv', index=False)
    
    print(f"  ✓ Generated 6 comprehensive tables covering all 54 scenarios")
    return tables


def generate_optimal_caliper_table(
    summary_df: pd.DataFrame,
    save_dir: Path,
    balance_threshold: float = 0.1
) -> pd.DataFrame:
    """
    Generate table showing optimal caliper for each scenario.
    For each scenario, selects the method with highest retention among those achieving balance.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary results with aggregated metrics per method
    save_dir : Path
        Directory to save table
    balance_threshold : float
        Maximum acceptable SMD (default: 0.1)
        
    Returns
    -------
    optimal_df : pd.DataFrame
        Table with optimal selection per scenario
    """
    print("\n  Creating Optimal Caliper Selection Table...")
    
    optimal_data = []
    
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        # Get scenario characteristics
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        scenario_desc = f"n={n}, prev={prev:.1f}, {overlap}, {conf}"
        
        # Filter to methods achieving acceptable balance
        acceptable = scenario_data[scenario_data['mean_max_smd'] < balance_threshold]
        
        if len(acceptable) > 0:
            # Find highest retention among acceptable methods
            best_idx = acceptable['mean_retention'].idxmax()
            best_row = acceptable.loc[best_idx]
            
            method_name = best_row['method']
            
            # Extract caliper value from method name if it's a fixed caliper
            caliper_str = "N/A"
            if 'Fixed-' in method_name:
                caliper_str = method_name.split('-')[1]
            elif method_name.startswith('ACS-'):
                caliper_str = "Adaptive"
            
            optimal_data.append({
                'Scenario ID': scenario_id,
                'Scenario': scenario_desc,
                'Best_Method': method_name,
                'Method_Type': 'Fixed' if 'Fixed' in method_name else 'Adaptive',
                'Caliper': caliper_str,
                'Max_Abs_SMD': f"{best_row['mean_max_smd']:.4f}",
                'Retention': f"{best_row['mean_retention']:.4f}",
                'N_Matched': f"{best_row.get('mean_n_matched', np.nan):.1f}" if not pd.isna(best_row.get('mean_n_matched')) else 'N/A',
                'RMSE': f"{best_row.get('rmse', np.nan):.4f}" if not pd.isna(best_row.get('rmse')) else 'N/A',
                'Is_Pareto': 'TRUE',
                'Optimal': 'TRUE'
            })
        else:
            # No method achieves acceptable balance
            # Report the best balance achieved
            best_idx = scenario_data['mean_max_smd'].idxmin()
            best_row = scenario_data.loc[best_idx]
            
            method_name = best_row['method']
            caliper_str = "N/A"
            if 'Fixed-' in method_name:
                caliper_str = method_name.split('-')[1]
            elif method_name.startswith('ACS-'):
                caliper_str = "Adaptive"
            
            optimal_data.append({
                'Scenario ID': scenario_id,
                'Scenario': scenario_desc,
                'Best_Method': method_name,
                'Method_Type': 'Fixed' if 'Fixed' in method_name else 'Adaptive',
                'Caliper': caliper_str,
                'Max_Abs_SMD': f"{best_row['mean_max_smd']:.4f}",
                'Retention': f"{best_row['mean_retention']:.4f}",
                'N_Matched': f"{best_row.get('mean_n_matched', np.nan):.1f}" if not pd.isna(best_row.get('mean_n_matched')) else 'N/A',
                'RMSE': f"{best_row.get('rmse', np.nan):.4f}" if not pd.isna(best_row.get('rmse')) else 'N/A',
                'Is_Pareto': 'FALSE',
                'Optimal': 'FALSE (No acceptable balance)'
            })
    
    optimal_df = pd.DataFrame(optimal_data)
    
    # Save table
    optimal_df.to_csv(save_dir / 'table7_optimal_caliper_all_scenarios.csv', index=False)
    optimal_df.to_latex(save_dir / 'table7_optimal_caliper_all_scenarios.tex', index=False)
    
    print(f"  ✓ Generated optimal caliper table for all {len(optimal_data)} scenarios")
    return optimal_df


def plot_optimal_caliper_visualization(
    optimal_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (20, 12)
) -> plt.Figure:
    """
    Create comprehensive visualization of optimal method selections across all scenarios.
    
    Parameters
    ----------
    optimal_df : pd.DataFrame
        Optimal method table from generate_optimal_caliper_table()
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    if len(optimal_df) == 0:
        print("  ⚠ No data to plot")
        return None
    
    # Convert string columns to numeric
    optimal_df_plot = optimal_df.copy()
    optimal_df_plot['Max_Abs_SMD'] = pd.to_numeric(optimal_df_plot['Max_Abs_SMD'])
    optimal_df_plot['Retention'] = pd.to_numeric(optimal_df_plot['Retention'])
    
    # Create 2x2 subplot figure
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Extract n, prev, overlap, conf from Scenario string
    optimal_df_plot['n'] = optimal_df_plot['Scenario'].str.extract(r'n=(\d+)').astype(int)
    optimal_df_plot['prev'] = optimal_df_plot['Scenario'].str.extract(r'prev=([\d.]+)').astype(float)
    
    # Panel 1: Best Method by Scenario (Bar chart showing which method is optimal)
    ax1 = fig.add_subplot(gs[0, :])  # Top full width
    
    scenarios = optimal_df_plot['Scenario ID'].values
    methods = optimal_df_plot['Best_Method'].values
    
    # Assign numeric values to methods for plotting
    method_map = {m: i for i, m in enumerate(optimal_df_plot['Best_Method'].unique())}
    method_values = [method_map[m] for m in methods]
    
    colors = ['#2ecc71' if opt == 'TRUE' else '#e74c3c' 
              for opt in optimal_df_plot['Is_Pareto'].values]
    
    bars = ax1.bar(scenarios, [1]*len(scenarios), color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Add method labels on bars
    for i, (scen, method, color) in enumerate(zip(scenarios, methods, colors)):
        ax1.text(scen, 0.5, method.replace('Fixed-', 'F').replace('ACS-', 'A'), 
                ha='center', va='center', fontsize=7, fontweight='bold', rotation=90)
    
    ax1.set_xlabel('Scenario ID', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Best Method', fontsize=12, fontweight='bold')
    ax1.set_title('Optimal Method Selection Across All 54 Scenarios\n' +
                  'Green: Achieves balance threshold (max |SMD| < 0.1) | Red: No acceptable balance',
                  fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlim(0, 55)
    ax1.set_ylim(0, 1.2)
    ax1.set_yticks([])
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Panel 2: Balance vs Retention Scatter
    ax2 = fig.add_subplot(gs[1, 0])
    
    scatter_colors = ['#2ecc71' if opt == 'TRUE' else '#e74c3c' 
                      for opt in optimal_df_plot['Is_Pareto'].values]
    
    ax2.scatter(optimal_df_plot['Retention'], optimal_df_plot['Max_Abs_SMD'],
                c=scatter_colors, s=100, alpha=0.6, edgecolors='black', linewidths=0.5)
    
    ax2.axhline(y=0.1, color='green', linestyle='--', linewidth=2, 
                alpha=0.6, label='Balance threshold (0.1)')
    ax2.axhspan(0, 0.1, alpha=0.1, color='green')
    
    ax2.set_xlabel('Retention Rate', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Maximum |SMD|', fontsize=11, fontweight='bold')
    ax2.set_title('Balance-Retention Trade-off\n(Optimal Points)', 
                  fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=9)
    ax2.set_xlim(0, 1.05)
    ax2.set_ylim(0, max(optimal_df_plot['Max_Abs_SMD']) * 1.1)
    
    # Panel 3: Method Type Distribution
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Count method types among acceptable scenarios
    acceptable = optimal_df_plot[optimal_df_plot['Is_Pareto'] == 'TRUE']
    
    if len(acceptable) > 0:
        method_counts = acceptable['Best_Method'].value_counts()
        
        colors_bar = ['#377EB8' if 'Fixed' in m else '#FF7F00' for m in method_counts.index]
        bars = ax3.barh(range(len(method_counts)), method_counts.values, color=colors_bar, alpha=0.7, edgecolor='black')
        
        ax3.set_yticks(range(len(method_counts)))
        ax3.set_yticklabels(method_counts.index, fontsize=10)
        ax3.set_xlabel('Number of Scenarios', fontsize=11, fontweight='bold')
        ax3.set_title(f'Best Method Frequency\n({len(acceptable)} scenarios achieve balance)', 
                      fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Add count labels
        for i, (method, count) in enumerate(method_counts.items()):
            ax3.text(count + 0.5, i, str(count), va='center', fontsize=10, fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'No scenarios\nachieve balance\nthreshold', 
                ha='center', va='center', fontsize=12, transform=ax3.transAxes)
        ax3.set_xticks([])
        ax3.set_yticks([])
    
    # Overall title
    fig.suptitle('Optimal Method Selection: Analysis Across 54 Factorial Design Scenarios',
                 fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_optimal_caliper_heatmap(
    optimal_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (18, 10)
) -> plt.Figure:
    """
    Create heatmap showing optimal method and retention across factorial design.
    
    Parameters
    ----------
    optimal_df : pd.DataFrame
        Optimal method table
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    if len(optimal_df) == 0:
        return None
    
    # Parse scenario information
    plot_df = optimal_df.copy()
    plot_df['n'] = plot_df['Scenario'].str.extract(r'n=(\d+)').astype(int)
    plot_df['prev'] = plot_df['Scenario'].str.extract(r'prev=([\d.]+)').astype(float)
    plot_df['overlap'] = plot_df['Scenario'].str.extract(r', (\w+),')[0]
    plot_df['conf'] = plot_df['Scenario'].str.extract(r', (\w+)$')[0]
    plot_df['Retention'] = pd.to_numeric(plot_df['Retention'])
    
    # Create pivot table for retention
    pivot_retention = plot_df.pivot_table(
        values='Retention',
        index=['overlap', 'conf'],
        columns=['n', 'prev'],
        aggfunc='mean'
    )
    
    # Create annotation with method names
    pivot_methods = plot_df.pivot_table(
        values='Best_Method',
        index=['overlap', 'conf'],
        columns=['n', 'prev'],
        aggfunc='first'
    )
    
    # Sort index and columns
    pivot_retention = pivot_retention.sort_index()
    pivot_retention = pivot_retention.reindex(
        columns=sorted(pivot_retention.columns, key=lambda x: (x[0], x[1]))
    )
    pivot_methods = pivot_methods.reindex(index=pivot_retention.index, columns=pivot_retention.columns)
    
    # Create annotations combining method and retention
    annot_array = []
    for i in range(len(pivot_retention)):
        row_annot = []
        for j in range(len(pivot_retention.columns)):
            method = pivot_methods.iloc[i, j]
            retention = pivot_retention.iloc[i, j]
            # Abbreviate method name
            method_abbr = method.replace('Fixed-', 'F').replace('ACS-', 'A') if isinstance(method, str) else 'N/A'
            row_annot.append(f'{method_abbr}\n{retention:.3f}')
        annot_array.append(row_annot)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap with retention as color
    sns.heatmap(pivot_retention, annot=annot_array, fmt='',
                cmap='RdYlGn', ax=ax, cbar=True, linewidths=0.5, linecolor='white',
                annot_kws={'fontsize': 9, 'fontweight': 'bold'},
                cbar_kws={'label': 'Retention Rate', 'shrink': 0.8},
                vmin=0, vmax=1)
    
    ax.set_title('Optimal Method Selection Across Factorial Design\n' +
                 'Best method (top) and retention rate (bottom) achieving max |SMD| < 0.1',
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('(Sample Size, Treatment Prevalence)', fontsize=12, fontweight='bold')
    ax.set_ylabel('(Overlap, Confounding)', fontsize=12, fontweight='bold')
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_treatment_effects_all_scenarios(
    summary_df: pd.DataFrame,
    true_effect: float = 0.5,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (24, 16)
) -> plt.Figure:
    """
    Create comprehensive visualization of treatment effect estimates across all 54 scenarios.
    Figure 5: Treatment Effect Estimates Grid (9×6 for all scenarios).
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics by scenario and method
    true_effect : float
        True treatment effect (default: 0.5)
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    # Get unique scenarios
    scenarios = sorted(summary_df['scenario_id'].unique())
    
    # Create 9×6 grid (54 subplots)
    fig, axes = plt.subplots(9, 6, figsize=figsize, sharex=False, sharey=True)
    axes = axes.flatten()
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    for idx, scenario_id in enumerate(scenarios):
        ax = axes[idx]
        
        # Get data for this scenario
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        if len(scenario_data) == 0:
            continue
            
        # Get scenario characteristics
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        
        # Extract estimates and CIs for each method
        y_positions = []
        estimates = []
        ci_lows = []
        ci_highs = []
        colors = []
        
        for i, method in enumerate(method_order):
            method_data = scenario_data[scenario_data['method'] == method]
            if len(method_data) == 0:
                continue
                
            # Get mean estimate and CI
            estimate = method_data.get('mean_estimate', method_data.get('mean_bias', 0) + true_effect).values[0]
            ci_width = method_data.get('mean_ci_width', 0.4).values[0]
            
            # Approximate CI (estimate ± half width)
            ci_low = estimate - ci_width / 2
            ci_high = estimate + ci_width / 2
            
            y_positions.append(i)
            estimates.append(estimate)
            ci_lows.append(ci_low)
            ci_highs.append(ci_high)
            colors.append(METHOD_COLORS.get(method, 'gray'))
        
        # Plot horizontal error bars (CIs)
        for y, est, ci_l, ci_h, color in zip(y_positions, estimates, ci_lows, ci_highs, colors):
            ax.plot([ci_l, ci_h], [y, y], '-', color=color, linewidth=2, alpha=0.6)
            ax.plot(est, y, 'o', color=color, markersize=7, 
                   markeredgecolor='black', markeredgewidth=0.5)
        
        # True effect line
        ax.axvline(x=true_effect, color='red', linestyle='--', 
                  linewidth=1.5, alpha=0.7, zorder=0)
        
        # Formatting
        ax.set_yticks(range(len(method_order)))
        ax.set_yticklabels([METHOD_NAMES.get(m, m) for m in method_order], fontsize=6)
        ax.set_xlim(-0.5, 2.5)
        
        # Title with scenario info
        title = f"S{scenario_id}: n={n}, p={prev:.1f}\n{overlap[:3]}, {conf[:4]}"
        ax.set_title(title, fontsize=7, pad=4, fontweight='bold')
        
        # Grid
        ax.grid(True, alpha=0.25, linewidth=0.4, linestyle=':', axis='x')
        ax.tick_params(labelsize=6)
        
        # Add subtle background color based on sample size
        if n == 500:
            ax.set_facecolor('#f0f8ff')  # Light blue
        elif n == 1000:
            ax.set_facecolor('#f0fff0')  # Light green
        else:  # 2000
            ax.set_facecolor('#fff8f0')  # Light orange
    
    # Set common axis labels
    for i in range(9):
        axes[i*6].set_ylabel('Method', fontsize=9, fontweight='bold')
    for i in range(48, 54):
        axes[i].set_xlabel('Treatment Effect Estimate', fontsize=9, fontweight='bold')
    
    # Overall title
    fig.suptitle('Treatment Effect Estimates with 95% Confidence Intervals Across All 54 Scenarios\n' + 
                f'Red dashed line: True effect (τ = {true_effect}) | Points: Mean estimates | Bars: 95% CIs',
                fontsize=13, fontweight='bold', y=0.998)
    
    plt.tight_layout(rect=[0, 0, 1, 0.992])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def generate_optimal_caliper_by_method_table(
    summary_df: pd.DataFrame,
    save_dir: Path,
    balance_threshold: float = 0.1
) -> pd.DataFrame:
    """
    Generate table showing optimal caliper for each scenario and method.
    For each scenario-method combination, finds the highest caliper achieving max_abs_smd < 0.10.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary results with aggregated metrics per method
    save_dir : Path
        Directory to save table
    balance_threshold : float
        Maximum acceptable SMD (default: 0.1)
        
    Returns
    -------
    optimal_df : pd.DataFrame
        Table with optimal caliper per scenario per method
    """
    print("\n  Creating Optimal Caliper by Method Table (54 scenarios × 7 methods)...")
    
    # Define methods
    methods = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
               'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    optimal_data = []
    
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        # Get scenario characteristics
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        scenario_desc = f"n={n}, prev={prev:.1f}, {overlap}, {conf}"
        
        for method in methods:
            method_data = scenario_data[scenario_data['method'] == method]
            
            if len(method_data) == 0:
                continue
            
            row = method_data.iloc[0]
            max_smd = row['mean_max_smd']
            retention = row['mean_retention']
            n_matched = row.get('mean_n_matched', np.nan)
            rmse = row.get('rmse', np.nan)
            
            # Determine if this method achieves acceptable balance
            meets_threshold = max_smd < balance_threshold
            
            # Get caliper value
            if method == 'No Caliper':
                caliper_val = 'None'
            elif method.startswith('Fixed-'):
                caliper_val = method.split('-')[1]
            else:
                caliper_val = row.get('mean_caliper', 'Adaptive')
                if isinstance(caliper_val, float):
                    caliper_val = f"{caliper_val:.3f}"
            
            optimal_data.append({
                'Scenario_ID': scenario_id,
                'Scenario': scenario_desc,
                'Method': method,
                'Caliper': caliper_val,
                'Max_Abs_SMD': max_smd,
                'Retention': retention,
                'N_Matched': n_matched,
                'RMSE': rmse,
                'Meets_Threshold': 'Yes' if meets_threshold else 'No'
            })
    
    optimal_df = pd.DataFrame(optimal_data)
    
    # Save full table
    optimal_df.to_csv(save_dir / 'table8_optimal_caliper_by_method_all_scenarios.csv', index=False)
    
    # Create a summary table: for each scenario, show only the method with highest retention that meets threshold
    summary_optimal = []
    for scenario_id in sorted(summary_df['scenario_id'].unique()):
        scenario_rows = optimal_df[optimal_df['Scenario_ID'] == scenario_id]
        acceptable = scenario_rows[scenario_rows['Meets_Threshold'] == 'Yes']
        
        if len(acceptable) > 0:
            # Get the one with highest retention
            best_idx = acceptable['Retention'].idxmax()
            best_row = acceptable.loc[best_idx]
            summary_optimal.append({
                'Scenario_ID': scenario_id,
                'Scenario': best_row['Scenario'],
                'Best_Method': best_row['Method'],
                'Caliper': best_row['Caliper'],
                'Max_Abs_SMD': best_row['Max_Abs_SMD'],
                'Retention': best_row['Retention'],
                'N_Matched': best_row['N_Matched'],
                'RMSE': best_row['RMSE']
            })
        else:
            # No method achieves threshold - report best balance
            best_idx = scenario_rows['Max_Abs_SMD'].idxmin()
            best_row = scenario_rows.loc[best_idx]
            summary_optimal.append({
                'Scenario_ID': scenario_id,
                'Scenario': best_row['Scenario'],
                'Best_Method': f"{best_row['Method']} (no threshold met)",
                'Caliper': best_row['Caliper'],
                'Max_Abs_SMD': best_row['Max_Abs_SMD'],
                'Retention': best_row['Retention'],
                'N_Matched': best_row['N_Matched'],
                'RMSE': best_row['RMSE']
            })
    
    summary_df_out = pd.DataFrame(summary_optimal)
    summary_df_out.to_csv(save_dir / 'table8_optimal_caliper_summary.csv', index=False)
    
    print(f"  ✓ Generated optimal caliper tables for all {len(summary_df['scenario_id'].unique())} scenarios")
    return optimal_df


def plot_optimal_caliper_by_method(
    summary_df: pd.DataFrame,
    save_dir: Path,
    balance_threshold: float = 0.1,
    figsize: Tuple[float, float] = (20, 16)
) -> Dict[str, plt.Figure]:
    """
    Create publication-quality visualizations of optimal caliper selection by method.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary results with aggregated metrics per method
    save_dir : Path
        Directory to save figures
    balance_threshold : float
        Maximum acceptable SMD (default: 0.1)
    figsize : tuple
        Figure size
        
    Returns
    -------
    figures : dict
        Dictionary of generated figures
    """
    print("\n  Creating Optimal Caliper Visualizations by Method...")
    
    figures = {}
    methods = ['ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    for method in methods:
        method_data = summary_df[summary_df['method'] == method].copy()
        
        if len(method_data) == 0:
            continue
        
        # Create figure with 2x2 layout
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f'Optimal Caliper Analysis: {method}\n' +
                     f'Across All 54 Factorial Design Scenarios (Balance Threshold: max|SMD| < {balance_threshold})',
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Panel 1: Caliper vs Scenario (sorted by caliper)
        ax1 = axes[0, 0]
        method_data_sorted = method_data.sort_values('mean_caliper')
        scenarios = range(len(method_data_sorted))
        calipers = method_data_sorted['mean_caliper'].values
        meets_threshold = method_data_sorted['mean_max_smd'] < balance_threshold
        
        colors = ['#2ecc71' if mt else '#e74c3c' for mt in meets_threshold]
        bars = ax1.bar(scenarios, calipers, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
        
        ax1.set_xlabel('Scenario (sorted by caliper)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Mean Caliper (SD of logit PS)', fontsize=11, fontweight='bold')
        ax1.set_title('Caliper Values Across Scenarios\n(Green: meets balance | Red: does not meet balance)',
                      fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_xlim(-1, len(scenarios))
        
        # Panel 2: Retention vs Max SMD scatter
        ax2 = axes[0, 1]
        scatter = ax2.scatter(method_data['mean_retention'], method_data['mean_max_smd'],
                             c=method_data['mean_caliper'], cmap='viridis', 
                             s=100, alpha=0.7, edgecolors='black', linewidths=0.5)
        
        ax2.axhline(y=balance_threshold, color='red', linestyle='--', linewidth=2, 
                    alpha=0.7, label=f'Balance threshold ({balance_threshold})')
        ax2.axhspan(0, balance_threshold, alpha=0.1, color='green')
        
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Caliper Value', fontsize=10, fontweight='bold')
        
        ax2.set_xlabel('Retention Rate', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Max |SMD|', fontsize=11, fontweight='bold')
        ax2.set_title('Balance-Retention Trade-off\n(Color: Caliper value)',
                      fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, 1.05)
        
        # Panel 3: Caliper distribution by overlap level
        ax3 = axes[1, 0]
        overlap_order = ['high', 'medium', 'low']
        overlap_data = [method_data[method_data['overlap_name'] == o]['mean_caliper'].values 
                        for o in overlap_order]
        
        bp = ax3.boxplot(overlap_data, labels=overlap_order, patch_artist=True)
        colors_box = ['#3498db', '#f39c12', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors_box):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        
        ax3.set_xlabel('Overlap Level', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Caliper Value', fontsize=11, fontweight='bold')
        ax3.set_title('Caliper Distribution by Overlap Level',
                      fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Panel 4: Caliper distribution by sample size
        ax4 = axes[1, 1]
        n_order = [500, 1000, 2000]
        n_data = [method_data[method_data['n'] == n]['mean_caliper'].values 
                  for n in n_order]
        
        bp2 = ax4.boxplot(n_data, labels=[str(n) for n in n_order], patch_artist=True)
        colors_box2 = ['#f0f8ff', '#f0fff0', '#fff8f0']
        edge_colors = ['#3498db', '#27ae60', '#e67e22']
        for patch, fc, ec in zip(bp2['boxes'], colors_box2, edge_colors):
            patch.set_facecolor(fc)
            patch.set_edgecolor(ec)
            patch.set_linewidth(2)
        
        ax4.set_xlabel('Sample Size', fontsize=11, fontweight='bold')
        ax4.set_ylabel('Caliper Value', fontsize=11, fontweight='bold')
        ax4.set_title('Caliper Distribution by Sample Size',
                      fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save figure
        save_path = save_dir / f'optimal_caliper_{method.lower().replace("-", "_")}.png'
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
        figures[method] = fig
        
        print(f"    ✓ Generated {method} optimal caliper visualization")
    
    return figures


def plot_improved_tradeoff_grid(
    summary_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (28, 36)
) -> plt.Figure:
    """
    Create an improved, clearer 9×6 grid showing balance-retention trade-off for all 54 scenarios.
    Enhanced version with better visibility and optimal caliper highlighting.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary results by scenario and method
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    
    # Get unique scenarios
    scenarios = sorted(summary_df['scenario_id'].unique())
    
    # Create 9×6 grid (54 subplots)
    fig, axes = plt.subplots(9, 6, figsize=figsize)
    axes = axes.flatten()
    
    method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                    'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    # Enhanced markers for better visibility
    method_markers = {
        'Fixed-0.1': 'o',
        'Fixed-0.2': 's',
        'Fixed-0.5': '^',
        'No Caliper': 'X',
        'ACS-Balance': 'D',
        'ACS-Knee': 'P',
        'ACS-Weighted': 'H'
    }
    
    for idx, scenario_id in enumerate(scenarios):
        ax = axes[idx]
        
        # Get data for this scenario
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        
        if len(scenario_data) == 0:
            continue
            
        # Get scenario characteristics
        n = scenario_data['n'].iloc[0]
        prev = scenario_data['treatment_prevalence'].iloc[0]
        overlap = scenario_data['overlap_name'].iloc[0]
        conf = scenario_data['confounding_name'].iloc[0]
        
        # Find optimal method (highest retention with max_smd < 0.1)
        acceptable = scenario_data[scenario_data['mean_max_smd'] < 0.1]
        optimal_method = None
        if len(acceptable) > 0:
            optimal_method = acceptable.loc[acceptable['mean_retention'].idxmax(), 'method']
        
        # Plot each method
        for method in method_order:
            method_data = scenario_data[scenario_data['method'] == method]
            if len(method_data) == 0:
                continue
                
            retention = method_data['mean_retention'].values[0]
            max_smd = method_data['mean_max_smd'].values[0]
            color = METHOD_COLORS.get(method, 'gray')
            marker = method_markers.get(method, 'o')
            
            # Highlight optimal method with larger marker and gold edge
            if method == optimal_method:
                markersize = 12
                edgecolor = 'gold'
                edgewidth = 3
                zorder = 5
            else:
                markersize = 9
                edgecolor = 'black'
                edgewidth = 0.8
                zorder = 3
            
            ax.scatter(retention, max_smd, c=color, marker=marker,
                      s=markersize**2, alpha=0.9, 
                      edgecolors=edgecolor, linewidths=edgewidth, zorder=zorder)
        
        # Balance threshold region
        ax.axhline(y=0.1, color='green', linestyle='--', 
                  linewidth=2, alpha=0.7, zorder=0)
        ax.axhspan(0, 0.1, alpha=0.15, color='green', zorder=0)
        
        # Formatting
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 0.5)
        
        # Title with scenario info - more readable
        title = f"S{scenario_id}: n={n}, p={prev:.1f}\n{overlap}, {conf}"
        ax.set_title(title, fontsize=9, pad=6, fontweight='bold')
        
        # Grid
        ax.grid(True, alpha=0.3, linewidth=0.5, linestyle='-')
        ax.tick_params(labelsize=8)
        
        # Add subtle background color based on sample size
        if n == 500:
            ax.set_facecolor('#e6f2ff')  # Light blue
        elif n == 1000:
            ax.set_facecolor('#e6ffe6')  # Light green
        else:  # 2000
            ax.set_facecolor('#fff2e6')  # Light orange
    
    # Set common axis labels
    for i in range(9):
        axes[i*6].set_ylabel('Max |SMD|', fontsize=10, fontweight='bold')
    for i in range(48, 54):
        axes[i].set_xlabel('Retention', fontsize=10, fontweight='bold')
    
    # Create enhanced legend
    legend_elements = []
    for method in method_order:
        legend_elements.append(
            Line2D([0], [0], marker=method_markers[method], color='w', 
                   markerfacecolor=METHOD_COLORS[method],
                   markersize=10, label=METHOD_NAMES.get(method, method), 
                   markeredgecolor='black', markeredgewidth=0.8)
        )
    
    legend_elements.append(Line2D([0], [0], color='green', linestyle='--', linewidth=2,
                                   label='Balance Threshold (0.1)'))
    legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                                   markersize=12, markeredgecolor='gold', markeredgewidth=3,
                                   label='Optimal Method'))
    
    # Add sample size legend
    legend_elements.append(Patch(facecolor='#e6f2ff', edgecolor='black', label='n=500'))
    legend_elements.append(Patch(facecolor='#e6ffe6', edgecolor='black', label='n=1000'))
    legend_elements.append(Patch(facecolor='#fff2e6', edgecolor='black', label='n=2000'))
    
    fig.legend(handles=legend_elements, loc='upper center', ncol=6,
              bbox_to_anchor=(0.5, 0.995), fontsize=10, frameon=True,
              fancybox=True, shadow=True)
    
    # Overall title
    fig.suptitle('Balance-Retention Trade-off Across All 54 Factorial Design Scenarios\n' + 
                'Gold outline: Optimal method (highest retention with max|SMD| < 0.1) | Green region: Acceptable balance',
                fontsize=15, fontweight='bold', y=0.999)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_optimal_caliper_summary_dashboard(
    summary_df: pd.DataFrame,
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (24, 20)
) -> plt.Figure:
    """
    Create a comprehensive dashboard summarizing optimal caliper selection across all scenarios.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary results with aggregated metrics per method
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    """
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    methods = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
               'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    # Panel 1: Method success rate (top left) - which methods achieve balance threshold
    ax1 = fig.add_subplot(gs[0, 0])
    
    success_counts = {}
    for method in methods:
        method_data = summary_df[summary_df['method'] == method]
        success_counts[method] = (method_data['mean_max_smd'] < 0.1).sum()
    
    colors = [METHOD_COLORS.get(m, 'gray') for m in methods]
    bars = ax1.bar(range(len(methods)), [success_counts[m] for m in methods], 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    
    ax1.set_xticks(range(len(methods)))
    ax1.set_xticklabels([m.replace('Fixed-', 'F').replace('ACS-', 'A') for m in methods], 
                        rotation=45, ha='right', fontsize=10)
    ax1.set_ylabel('Scenarios Meeting Threshold', fontsize=11, fontweight='bold')
    ax1.set_title('Balance Threshold Achievement\n(max|SMD| < 0.1)', fontsize=12, fontweight='bold')
    ax1.axhline(y=54, color='red', linestyle='--', alpha=0.5, label='Total scenarios (54)')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add count labels on bars
    for i, (method, count) in enumerate(success_counts.items()):
        ax1.text(i, count + 1, str(count), ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Panel 2: Best method frequency (top middle)
    ax2 = fig.add_subplot(gs[0, 1])
    
    best_method_counts = {}
    for scenario_id in summary_df['scenario_id'].unique():
        scenario_data = summary_df[summary_df['scenario_id'] == scenario_id]
        acceptable = scenario_data[scenario_data['mean_max_smd'] < 0.1]
        if len(acceptable) > 0:
            best = acceptable.loc[acceptable['mean_retention'].idxmax(), 'method']
            best_method_counts[best] = best_method_counts.get(best, 0) + 1
    
    if best_method_counts:
        sorted_methods = sorted(best_method_counts.keys(), key=lambda x: best_method_counts[x], reverse=True)
        colors2 = [METHOD_COLORS.get(m, 'gray') for m in sorted_methods]
        bars2 = ax2.barh(range(len(sorted_methods)), [best_method_counts[m] for m in sorted_methods],
                        color=colors2, alpha=0.7, edgecolor='black', linewidth=1)
        ax2.set_yticks(range(len(sorted_methods)))
        ax2.set_yticklabels(sorted_methods, fontsize=10)
        ax2.set_xlabel('Number of Scenarios', fontsize=11, fontweight='bold')
        ax2.set_title('Best Method Frequency\n(Highest retention meeting threshold)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        for i, method in enumerate(sorted_methods):
            ax2.text(best_method_counts[method] + 0.5, i, str(best_method_counts[method]), 
                    va='center', fontsize=10, fontweight='bold')
    
    # Panel 3: Retention distribution by method (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    
    retention_data = [summary_df[summary_df['method'] == m]['mean_retention'].values for m in methods]
    bp = ax3.boxplot(retention_data, labels=[m.replace('Fixed-', 'F').replace('ACS-', 'A') for m in methods],
                     patch_artist=True, vert=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax3.set_ylabel('Retention Rate', fontsize=11, fontweight='bold')
    ax3.set_title('Retention Distribution by Method', fontsize=12, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Panel 4: Scatter of all methods (middle row, full width)
    ax4 = fig.add_subplot(gs[1, :])
    
    for method in methods:
        method_data = summary_df[summary_df['method'] == method]
        ax4.scatter(method_data['mean_retention'], method_data['mean_max_smd'],
                   c=METHOD_COLORS.get(method, 'gray'), label=METHOD_NAMES.get(method, method),
                   s=80, alpha=0.6, edgecolors='black', linewidths=0.5)
    
    ax4.axhline(y=0.1, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax4.axhspan(0, 0.1, alpha=0.1, color='green')
    
    ax4.set_xlabel('Retention Rate', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Max |SMD|', fontsize=12, fontweight='bold')
    ax4.set_title('Balance-Retention Trade-off: All Methods Across All 54 Scenarios',
                  fontsize=14, fontweight='bold')
    ax4.legend(loc='upper right', fontsize=10, ncol=2)
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 1.05)
    ax4.set_ylim(0, 0.8)
    
    # Panel 5: RMSE by method (bottom left)
    ax5 = fig.add_subplot(gs[2, 0])
    
    rmse_data = [summary_df[summary_df['method'] == m]['rmse'].dropna().values for m in methods]
    bp2 = ax5.boxplot(rmse_data, labels=[m.replace('Fixed-', 'F').replace('ACS-', 'A') for m in methods],
                      patch_artist=True)
    
    for patch, color in zip(bp2['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax5.set_ylabel('RMSE', fontsize=11, fontweight='bold')
    ax5.set_title('RMSE Distribution by Method', fontsize=12, fontweight='bold')
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # Panel 6: Performance by overlap (bottom middle)
    ax6 = fig.add_subplot(gs[2, 1])
    
    overlap_order = ['high', 'medium', 'low']
    acs_methods = ['ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    x = np.arange(len(overlap_order))
    width = 0.25
    
    for i, method in enumerate(acs_methods):
        method_data = summary_df[summary_df['method'] == method]
        means = [method_data[method_data['overlap_name'] == o]['mean_retention'].mean() 
                 for o in overlap_order]
        ax6.bar(x + i*width, means, width, label=method, 
                color=METHOD_COLORS.get(method, 'gray'), alpha=0.7, edgecolor='black')
    
    ax6.set_xticks(x + width)
    ax6.set_xticklabels(overlap_order, fontsize=10)
    ax6.set_xlabel('Overlap Level', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Mean Retention', fontsize=11, fontweight='bold')
    ax6.set_title('ACS Methods: Retention by Overlap', fontsize=12, fontweight='bold')
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Panel 7: Performance by sample size (bottom right)
    ax7 = fig.add_subplot(gs[2, 2])
    
    n_order = [500, 1000, 2000]
    
    x = np.arange(len(n_order))
    
    for i, method in enumerate(acs_methods):
        method_data = summary_df[summary_df['method'] == method]
        means = [method_data[method_data['n'] == n]['mean_max_smd'].mean() 
                 for n in n_order]
        ax7.bar(x + i*width, means, width, label=method, 
                color=METHOD_COLORS.get(method, 'gray'), alpha=0.7, edgecolor='black')
    
    ax7.axhline(y=0.1, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax7.set_xticks(x + width)
    ax7.set_xticklabels([str(n) for n in n_order], fontsize=10)
    ax7.set_xlabel('Sample Size', fontsize=11, fontweight='bold')
    ax7.set_ylabel('Mean Max |SMD|', fontsize=11, fontweight='bold')
    ax7.set_title('ACS Methods: Balance by Sample Size', fontsize=12, fontweight='bold')
    ax7.legend(fontsize=9)
    ax7.grid(True, alpha=0.3, axis='y')
    
    # Overall title
    fig.suptitle('Optimal Caliper Selection Dashboard: Comprehensive Analysis Across 54 Scenarios',
                 fontsize=18, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig


def plot_scenario_factor_effects(
    summary_df: pd.DataFrame,
    metric: str = 'rmse',
    save_path: Optional[Path] = None,
    figsize: Tuple[float, float] = (14, 10)
) -> plt.Figure:
    """
    Create plots showing main effects of each factorial design factor.
    
    Parameters
    ----------
    summary_df : pd.DataFrame
        Summary statistics
    metric : str
        Metric to analyze
    save_path : Path, optional
        Path to save figure
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : plt.Figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    metric_label = {
        'rmse': 'RMSE',
        'mean_abs_bias': 'Mean Absolute Bias',
        'coverage_rate': 'Coverage Rate',
        'mean_retention': 'Sample Retention',
        'mean_max_smd': 'Max |SMD|'
    }.get(metric, metric)
    
    method_order = ['Fixed-0.2', 'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    factors = [
        ('n', 'Sample Size'),
        ('treatment_prevalence', 'Treatment Prevalence'),
        ('overlap_name', 'Overlap Level'),
        ('confounding_name', 'Confounding Strength')
    ]
    
    for ax, (factor, factor_label) in zip(axes.flat, factors):
        for method in method_order:
            method_data = summary_df[summary_df['method'] == method]
            factor_means = method_data.groupby(factor)[metric].mean()
            
            color = METHOD_COLORS.get(method, 'gray')
            ax.plot(range(len(factor_means)), factor_means.values,
                   'o-', color=color, label=METHOD_NAMES.get(method, method),
                   markersize=8, linewidth=2, alpha=0.8)
        
        ax.set_xticks(range(len(factor_means)))
        ax.set_xticklabels(factor_means.index, rotation=45 if factor != 'n' else 0)
        ax.set_xlabel(factor_label, fontsize=11, fontweight='bold')
        ax.set_ylabel(metric_label, fontsize=11, fontweight='bold')
        ax.set_title(f'{metric_label} by {factor_label}', 
                    fontsize=12, fontweight='bold')
        
        if factor == 'n':
            ax.legend(loc='best', fontsize=8)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
    
    fig.suptitle(f'Main Effects of Factorial Design Factors on {metric_label}',
                fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig
