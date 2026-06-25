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
