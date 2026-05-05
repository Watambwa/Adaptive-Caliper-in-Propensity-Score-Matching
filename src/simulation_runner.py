"""
Monte Carlo Simulation Runner
==============================

Orchestrates the Monte Carlo simulation study for evaluating
Adaptive Caliper Selection methods against fixed-caliper approaches.

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from tqdm import tqdm
import warnings
from joblib import Parallel, delayed
import time

from config import (
    N_REPLICATIONS, TRUE_TREATMENT_EFFECT, FIXED_CALIPERS,
    CALIPER_GRID, N_JOBS, RESULTS_DIR, generate_all_scenarios
)
from data_generator import DataGenerator
from matching import PropensityScoreMatcher, compute_max_abs_smd, compute_mean_abs_smd
from adaptive_caliper import AdaptiveCaliperSelector
from treatment_effect import evaluate_treatment_effect_estimation


@dataclass
class ReplicationResult:
    """Results from a single simulation replication."""
    method: str
    caliper: float
    n_matched: int
    retention: float
    max_smd: float
    mean_smd: float
    att: float
    se: float
    bias: float
    mse: float
    coverage: float
    ci_width: float


def run_single_replication(
    scenario: Dict,
    rep_seed: int,
    methods: List[str] = None
) -> List[Dict]:
    """
    Run a single Monte Carlo replication.
    
    Parameters
    ----------
    scenario : dict
        Scenario configuration
    rep_seed : int
        Random seed for this replication
    methods : list, optional
        Methods to evaluate
        
    Returns
    -------
    results : list of dict
        Results for each method
    """
    if methods is None:
        methods = ['Fixed-0.1', 'Fixed-0.2', 'Fixed-0.5', 'No Caliper',
                   'ACS-Balance', 'ACS-Knee', 'ACS-Weighted']
    
    generator = DataGenerator(seed=rep_seed)
    
    df = generator.generate_dataset(
        n=scenario['n'],
        treatment_prevalence=scenario['treatment_prevalence'],
        overlap_level=scenario['overlap_level'],
        confounding_strength=scenario['confounding_strength']
    )
    
    e_hat = generator.estimate_propensity_scores(df)
    df['e_hat'] = e_hat
    
    covariate_cols = [f'X{i+1}' for i in range(6)]
    n_treated = df['Z'].sum()
    n_control = len(df) - n_treated
    max_possible_matches = min(n_treated, n_control)
    
    results = []
    
    acs_selector = AdaptiveCaliperSelector(
        caliper_grid=CALIPER_GRID,
        seed=rep_seed
    )
    acs_selector.fit(df, covariate_cols=covariate_cols)
    
    for method in methods:
        try:
            if method.startswith('Fixed-'):
                caliper_val = FIXED_CALIPERS[method]
                matcher = PropensityScoreMatcher(caliper=caliper_val, seed=rep_seed)
            elif method == 'No Caliper':
                matcher = PropensityScoreMatcher(caliper=None, seed=rep_seed)
                caliper_val = np.inf
            elif method.startswith('ACS-'):
                criterion = method.split('-')[1].lower()
                acs_result = acs_selector.select_optimal(criterion)
                caliper_val = acs_result.optimal_caliper
                matcher = PropensityScoreMatcher(caliper=caliper_val, seed=rep_seed)
            else:
                continue
            
            matcher.fit(df['e_hat'].values, df['Z'].values)
            
            if matcher.n_matched_ == 0:
                results.append({
                    'method': method,
                    'caliper': caliper_val,
                    'n_matched': 0,
                    'retention': 0.0,
                    'max_smd': np.nan,
                    'mean_smd': np.nan,
                    'att': np.nan,
                    'se': np.nan,
                    'bias': np.nan,
                    'mse': np.nan,
                    'coverage': np.nan,
                    'ci_width': np.nan
                })
                continue
            
            matched_df = matcher.get_matched_data(df)
            
            max_smd = compute_max_abs_smd(matched_df, covariate_cols)
            mean_smd = compute_mean_abs_smd(matched_df, covariate_cols)
            retention = matcher.n_matched_ / max_possible_matches
            
            te_results = evaluate_treatment_effect_estimation(
                matched_df, TRUE_TREATMENT_EFFECT
            )
            
            results.append({
                'method': method,
                'caliper': caliper_val,
                'n_matched': matcher.n_matched_,
                'retention': retention,
                'max_smd': max_smd,
                'mean_smd': mean_smd,
                'att': te_results['att'],
                'se': te_results['se'],
                'bias': te_results['bias'],
                'mse': te_results['mse'],
                'coverage': te_results['coverage'],
                'ci_width': te_results['ci_width']
            })
            
        except Exception as e:
            results.append({
                'method': method,
                'caliper': np.nan,
                'n_matched': 0,
                'retention': 0.0,
                'max_smd': np.nan,
                'mean_smd': np.nan,
                'att': np.nan,
                'se': np.nan,
                'bias': np.nan,
                'mse': np.nan,
                'coverage': np.nan,
                'ci_width': np.nan,
                'error': str(e)
            })
    
    return results


def run_scenario_simulation(
    scenario: Dict,
    n_replications: int = N_REPLICATIONS,
    n_jobs: int = N_JOBS,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Run Monte Carlo simulation for a single scenario.
    
    Parameters
    ----------
    scenario : dict
        Scenario configuration
    n_replications : int
        Number of replications
    n_jobs : int
        Number of parallel jobs
    verbose : bool
        Whether to show progress bar
        
    Returns
    -------
    results_df : pd.DataFrame
        Results for all replications and methods
    """
    base_seed = scenario['scenario_id'] * 10000
    
    if verbose:
        print(f"\nRunning scenario {scenario['scenario_id']}: {scenario.get('description', '')}")
    
    if n_jobs == 1:
        all_results = []
        iterator = tqdm(range(n_replications), disable=not verbose)
        for rep in iterator:
            rep_results = run_single_replication(scenario, base_seed + rep)
            for r in rep_results:
                r['replication'] = rep
            all_results.extend(rep_results)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rep_results_list = Parallel(n_jobs=n_jobs, verbose=0)(
                delayed(run_single_replication)(scenario, base_seed + rep)
                for rep in range(n_replications)
            )
        
        all_results = []
        for rep, rep_results in enumerate(rep_results_list):
            for r in rep_results:
                r['replication'] = rep
            all_results.extend(rep_results)
    
    results_df = pd.DataFrame(all_results)
    
    for key, value in scenario.items():
        results_df[key] = value
    
    return results_df


def run_full_simulation(
    scenarios: List[Dict] = None,
    n_replications: int = N_REPLICATIONS,
    n_jobs: int = N_JOBS,
    save_intermediate: bool = True,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Run full Monte Carlo simulation across all scenarios.
    
    Parameters
    ----------
    scenarios : list of dict, optional
        List of scenarios. If None, uses all scenarios from config.
    n_replications : int
        Number of replications per scenario
    n_jobs : int
        Number of parallel jobs
    save_intermediate : bool
        Whether to save intermediate results
    verbose : bool
        Whether to show progress
        
    Returns
    -------
    all_results : pd.DataFrame
        Combined results for all scenarios
    """
    if scenarios is None:
        scenarios = generate_all_scenarios()
    
    all_results = []
    
    start_time = time.time()
    
    for i, scenario in enumerate(scenarios):
        if verbose:
            print(f"\n{'='*60}")
            print(f"Scenario {i+1}/{len(scenarios)}")
        
        scenario_results = run_scenario_simulation(
            scenario, n_replications, n_jobs, verbose
        )
        all_results.append(scenario_results)
        
        if save_intermediate:
            intermediate_df = pd.concat(all_results, ignore_index=True)
            intermediate_df.to_csv(
                RESULTS_DIR / 'simulation_results_intermediate.csv',
                index=False
            )
    
    final_results = pd.concat(all_results, ignore_index=True)
    
    elapsed_time = time.time() - start_time
    if verbose:
        print(f"\n{'='*60}")
        print(f"Simulation completed in {elapsed_time/60:.1f} minutes")
        print(f"Total replications: {len(final_results)}")
    
    final_results.to_csv(RESULTS_DIR / 'simulation_results_full.csv', index=False)
    
    return final_results


def summarize_results(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize simulation results by scenario and method.
    
    Parameters
    ----------
    results_df : pd.DataFrame
        Raw simulation results
        
    Returns
    -------
    summary_df : pd.DataFrame
        Summary statistics
    """
    groupby_cols = ['scenario_id', 'n', 'treatment_prevalence', 
                    'overlap_name', 'confounding_name', 'method']
    
    summary = results_df.groupby(groupby_cols).agg({
        'caliper': 'mean',
        'n_matched': 'mean',
        'retention': 'mean',
        'max_smd': ['mean', 'std'],
        'mean_smd': 'mean',
        'att': ['mean', 'std'],
        'bias': ['mean', lambda x: np.mean(np.abs(x))],
        'mse': 'mean',
        'coverage': 'mean',
        'ci_width': 'mean'
    }).reset_index()
    
    summary.columns = [
        'scenario_id', 'n', 'treatment_prevalence', 'overlap_name', 
        'confounding_name', 'method', 'mean_caliper', 'mean_n_matched',
        'mean_retention', 'mean_max_smd', 'sd_max_smd', 'mean_mean_smd',
        'mean_att', 'sd_att', 'mean_bias', 'mean_abs_bias', 'mean_mse',
        'coverage_rate', 'mean_ci_width'
    ]
    
    summary['rmse'] = np.sqrt(summary['mean_mse'])
    
    return summary


if __name__ == "__main__":
    print("Testing Simulation Runner")
    print("=" * 60)
    
    test_scenario = {
        'scenario_id': 1,
        'n': 500,
        'treatment_prevalence': 0.5,
        'overlap_name': 'medium',
        'overlap_level': 0.6,
        'confounding_name': 'strong',
        'confounding_strength': 1.0,
        'description': 'Test scenario'
    }
    
    results = run_scenario_simulation(
        test_scenario,
        n_replications=10,
        n_jobs=1,
        verbose=True
    )
    
    print("\nResults shape:", results.shape)
    print("\nSummary by method:")
    summary = results.groupby('method').agg({
        'n_matched': 'mean',
        'retention': 'mean',
        'max_smd': 'mean',
        'bias': 'mean',
        'mse': 'mean',
        'coverage': 'mean'
    }).round(4)
    print(summary)
