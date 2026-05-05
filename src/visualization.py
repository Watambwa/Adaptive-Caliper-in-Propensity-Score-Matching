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
    figsize: Tuple[float, float] = (14, 10)
) -> plt.Figure:
    """Create multi-panel figure comparing methods across scenarios."""
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    metrics = [('mean_abs_bias', '|Bias|'), ('rmse', 'RMSE'),
               ('coverage_rate', 'Coverage'), ('mean_retention', 'Retention')]
    
    method_order = ['Fixed-0.2', 'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    for ax, (metric, label) in zip(axes.flat, metrics):
        for method in method_order:
            method_data = summary_df[summary_df['method'] == method]
            color = METHOD_COLORS.get(method, 'gray')
            ax.plot(method_data['scenario_id'], method_data[metric],
                   'o-', color=color, label=METHOD_NAMES.get(method, method),
                   markersize=4, linewidth=1.5, alpha=0.8)
        
        ax.set_xlabel('Scenario', fontsize=10)
        ax.set_ylabel(label, fontsize=10, fontweight='bold')
        ax.set_title(label, fontsize=11, fontweight='bold')
        
        if metric == 'coverage_rate':
            ax.axhline(y=0.95, color='red', linestyle='--', alpha=0.7)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=4, 
               bbox_to_anchor=(0.5, 1.02), fontsize=10)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if save_path:
        fig.savefig(save_path, dpi=FIGURE_DPI, bbox_inches='tight')
    
    return fig
