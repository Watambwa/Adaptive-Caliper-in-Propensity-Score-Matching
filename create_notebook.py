import json

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Adaptive Caliper Selection: Complete Simulation Study\n",
                "**Authors:** Perkins Watambwa et al. | CeSHHAR Zimbabwe\n",
                "\n",
                "---"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Setup\n",
                "import sys\n",
                "import os\n",
                "sys.path.insert(0, os.path.abspath('../src'))\n",
                "\n",
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from pathlib import Path\n",
                "import warnings\n",
                "warnings.filterwarnings('ignore')\n",
                "\n",
                "from config import *\n",
                "from data_generator import DataGenerator\n",
                "from matching import PropensityScoreMatcher, compute_balance_statistics, compute_max_abs_smd\n",
                "from adaptive_caliper import AdaptiveCaliperSelector\n",
                "from treatment_effect import evaluate_treatment_effect_estimation\n",
                "from simulation_runner import run_scenario_simulation, summarize_results\n",
                "from visualization import plot_pareto_frontier, plot_ps_distribution, plot_love_plot, plot_method_comparison_boxplot\n",
                "\n",
                "plt.rcParams.update(PLT_PARAMS)\n",
                "print('Setup complete!')\n",
                "print(f'Output directory: {OUTPUT_DIR}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 1. Generate Synthetic Data"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "generator = DataGenerator(seed=42)\n",
                "df = generator.generate_dataset(n=1000, treatment_prevalence=0.5, overlap_level=0.6, confounding_strength=1.0)\n",
                "df['e_hat'] = generator.estimate_propensity_scores(df)\n",
                "\n",
                "print(f'Sample size: {len(df)}')\n",
                "print(f\"Treated: {df['Z'].sum()} | Control: {(1-df['Z']).sum()}\")\n",
                "print(f\"PS correlation: {np.corrcoef(df['e_true'], df['e_hat'])[0,1]:.4f}\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# PS Distribution Plot\n",
                "fig, ax = plt.subplots(figsize=(10, 5))\n",
                "ax.hist(df[df['Z']==0]['e_hat'], bins=40, alpha=0.6, color='blue', label='Control', density=True)\n",
                "ax.hist(df[df['Z']==1]['e_hat'], bins=40, alpha=0.6, color='red', label='Treated', density=True)\n",
                "ax.set_xlabel('Propensity Score')\n",
                "ax.set_ylabel('Density')\n",
                "ax.set_title('Propensity Score Distribution')\n",
                "ax.legend()\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Adaptive Caliper Selection"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "covariate_cols = [f'X{i+1}' for i in range(6)]\n",
                "selector = AdaptiveCaliperSelector(seed=42)\n",
                "selector.fit(df, covariate_cols=covariate_cols)\n",
                "\n",
                "print('PARETO FRONTIER:')\n",
                "print(selector.get_frontier_dataframe().to_string(index=False))"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Select optimal calipers\n",
                "optimal = {}\n",
                "for crit in ['balance', 'knee', 'weighted']:\n",
                "    r = selector.select_optimal(crit)\n",
                "    optimal[crit] = r.optimal_caliper\n",
                "    print(f'{crit.upper()}: caliper={r.optimal_caliper:.3f} SD, SMD={r.balance_at_optimal:.4f}, retention={r.retention_at_optimal:.1%}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Balance Diagnostics"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "matcher = PropensityScoreMatcher(caliper=optimal['balance'], seed=42)\n",
                "matcher.fit(df['e_hat'].values, df['Z'].values)\n",
                "matched_df = matcher.get_matched_data(df)\n",
                "\n",
                "before = compute_balance_statistics(df, covariate_cols)\n",
                "after = compute_balance_statistics(matched_df, covariate_cols)\n",
                "\n",
                "print(f\"Max |SMD| Before: {before['abs_smd'].max():.4f}\")\n",
                "print(f\"Max |SMD| After: {after['abs_smd'].max():.4f}\")\n",
                "print(f'Matched pairs: {matcher.n_matched_}')"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Love Plot\n",
                "fig, ax = plt.subplots(figsize=(8, 5))\n",
                "y = np.arange(len(covariate_cols))\n",
                "ax.scatter(before['abs_smd'], y, c='red', s=100, label='Before')\n",
                "ax.scatter(after['abs_smd'], y, c='blue', s=100, label='After')\n",
                "for i in range(len(y)):\n",
                "    ax.plot([before['abs_smd'].iloc[i], after['abs_smd'].iloc[i]], [y[i], y[i]], 'k-', alpha=0.3)\n",
                "ax.axvline(0.1, color='red', ls='--', label='Threshold')\n",
                "ax.set_yticks(y)\n",
                "ax.set_yticklabels(covariate_cols)\n",
                "ax.set_xlabel('Absolute SMD')\n",
                "ax.set_title('Love Plot')\n",
                "ax.legend()\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Treatment Effect"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "te = evaluate_treatment_effect_estimation(matched_df, TRUE_TREATMENT_EFFECT)\n",
                "print(f'True ATT: {TRUE_TREATMENT_EFFECT}')\n",
                "print(f\"Estimated: {te['att']:.4f}\")\n",
                "print(f\"Bias: {te['bias']:.4f}\")\n",
                "print(f\"95% CI: [{te['ci_lower']:.4f}, {te['ci_upper']:.4f}]\")\n",
                "print(f\"Coverage: {te['coverage']}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 5. Monte Carlo Simulation"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "scenario = {'scenario_id': 1, 'n': 1000, 'treatment_prevalence': 0.5, 'overlap_name': 'medium', 'overlap_level': 0.6, 'confounding_name': 'strong', 'confounding_strength': 1.0}\n",
                "N_REPS = 50  # Change to 1000 for full study\n",
                "print(f'Running {N_REPS} replications...')\n",
                "results = run_scenario_simulation(scenario, n_replications=N_REPS, n_jobs=1, verbose=True)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Summary\n",
                "summary = results.groupby('method').agg({'n_matched': 'mean', 'retention': 'mean', 'max_smd': 'mean', 'bias': ['mean', lambda x: np.mean(np.abs(x))], 'mse': 'mean', 'coverage': 'mean'}).round(4)\n",
                "summary.columns = ['N', 'Ret', 'SMD', 'Bias', '|Bias|', 'MSE', 'Cov']\n",
                "print(summary)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Bias Boxplot\n",
                "method_order = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper', 'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']\n",
                "fig, ax = plt.subplots(figsize=(12, 5))\n",
                "bp = ax.boxplot([results[results['method']==m]['bias'].dropna() for m in method_order], labels=method_order, patch_artist=True)\n",
                "ax.axhline(0, color='red', ls='--')\n",
                "ax.set_ylabel('Bias')\n",
                "ax.set_title('Bias by Method')\n",
                "plt.xticks(rotation=45, ha='right')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["print('SIMULATION COMPLETE!')"]
        }
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('notebooks/run_simulation.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)
print('Notebook created successfully!')
