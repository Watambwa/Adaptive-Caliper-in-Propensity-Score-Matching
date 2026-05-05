"""
Treatment Effect Estimation Module
===================================

Implements ATT estimation and variance calculation for matched samples.
Includes paired difference estimator with cluster-robust standard errors.

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict, Optional


def estimate_att_matched(
    matched_df: pd.DataFrame,
    outcome_col: str = 'Y',
    treatment_col: str = 'Z',
    pair_col: str = 'pair_id'
) -> Dict[str, float]:
    """
    Estimate Average Treatment Effect on the Treated (ATT) from matched sample.
    
    Uses paired difference estimator with cluster-robust standard errors.
    
    Parameters
    ----------
    matched_df : pd.DataFrame
        Matched sample with pair identifiers
    outcome_col : str
        Name of outcome column
    treatment_col : str
        Name of treatment column
    pair_col : str
        Name of pair identifier column
        
    Returns
    -------
    results : dict
        Dictionary containing ATT estimate, SE, CI, and p-value
    """
    if len(matched_df) == 0:
        return {
            'att': np.nan,
            'se': np.nan,
            'ci_lower': np.nan,
            'ci_upper': np.nan,
            'p_value': np.nan,
            'n_pairs': 0
        }
    
    treated = matched_df[matched_df[treatment_col] == 1].set_index(pair_col)
    control = matched_df[matched_df[treatment_col] == 0].set_index(pair_col)
    
    common_pairs = treated.index.intersection(control.index)
    
    if len(common_pairs) == 0:
        return {
            'att': np.nan,
            'se': np.nan,
            'ci_lower': np.nan,
            'ci_upper': np.nan,
            'p_value': np.nan,
            'n_pairs': 0
        }
    
    y_treated = treated.loc[common_pairs, outcome_col].values
    y_control = control.loc[common_pairs, outcome_col].values
    
    differences = y_treated - y_control
    n_pairs = len(differences)
    
    att = np.mean(differences)
    se = np.std(differences, ddof=1) / np.sqrt(n_pairs)
    
    t_crit = stats.t.ppf(0.975, df=n_pairs - 1)
    ci_lower = att - t_crit * se
    ci_upper = att + t_crit * se
    
    t_stat = att / se if se > 0 else np.inf
    p_value = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=n_pairs - 1))
    
    return {
        'att': att,
        'se': se,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'p_value': p_value,
        'n_pairs': n_pairs,
        't_statistic': t_stat
    }


def compute_bias(estimated_att: float, true_att: float) -> float:
    """Compute bias of ATT estimate."""
    return estimated_att - true_att


def compute_mse(estimated_att: float, true_att: float, variance: float) -> float:
    """Compute mean squared error."""
    bias = estimated_att - true_att
    return bias**2 + variance


def compute_coverage(ci_lower: float, ci_upper: float, true_att: float) -> bool:
    """Check if confidence interval covers true value."""
    return ci_lower <= true_att <= ci_upper


def evaluate_treatment_effect_estimation(
    matched_df: pd.DataFrame,
    true_att: float,
    outcome_col: str = 'Y',
    treatment_col: str = 'Z',
    pair_col: str = 'pair_id'
) -> Dict[str, float]:
    """
    Comprehensive evaluation of treatment effect estimation.
    
    Parameters
    ----------
    matched_df : pd.DataFrame
        Matched sample
    true_att : float
        True treatment effect
    outcome_col : str
        Name of outcome column
    treatment_col : str
        Name of treatment column
    pair_col : str
        Name of pair identifier column
        
    Returns
    -------
    metrics : dict
        Dictionary of evaluation metrics
    """
    att_results = estimate_att_matched(
        matched_df, outcome_col, treatment_col, pair_col
    )
    
    if np.isnan(att_results['att']):
        return {
            'att': np.nan,
            'se': np.nan,
            'bias': np.nan,
            'mse': np.nan,
            'coverage': np.nan,
            'ci_width': np.nan,
            'n_pairs': 0
        }
    
    bias = compute_bias(att_results['att'], true_att)
    variance = att_results['se']**2
    mse = bias**2 + variance
    coverage = compute_coverage(
        att_results['ci_lower'], 
        att_results['ci_upper'], 
        true_att
    )
    ci_width = att_results['ci_upper'] - att_results['ci_lower']
    
    return {
        'att': att_results['att'],
        'se': att_results['se'],
        'bias': bias,
        'abs_bias': np.abs(bias),
        'variance': variance,
        'mse': mse,
        'rmse': np.sqrt(mse),
        'coverage': float(coverage),
        'ci_lower': att_results['ci_lower'],
        'ci_upper': att_results['ci_upper'],
        'ci_width': ci_width,
        'p_value': att_results['p_value'],
        'n_pairs': att_results['n_pairs']
    }


if __name__ == "__main__":
    from data_generator import DataGenerator
    from matching import PropensityScoreMatcher
    from config import TRUE_TREATMENT_EFFECT
    
    generator = DataGenerator(seed=42)
    df = generator.generate_dataset(
        n=1000,
        treatment_prevalence=0.5,
        overlap_level=0.6,
        confounding_strength=0.5
    )
    
    e_hat = generator.estimate_propensity_scores(df)
    df['e_hat'] = e_hat
    
    matcher = PropensityScoreMatcher(caliper=0.2, seed=42)
    matcher.fit(df['e_hat'].values, df['Z'].values)
    matched_df = matcher.get_matched_data(df)
    
    results = evaluate_treatment_effect_estimation(
        matched_df, 
        TRUE_TREATMENT_EFFECT
    )
    
    print("Treatment Effect Estimation Results:")
    print(f"  True ATT: {TRUE_TREATMENT_EFFECT}")
    print(f"  Estimated ATT: {results['att']:.4f}")
    print(f"  Bias: {results['bias']:.4f}")
    print(f"  SE: {results['se']:.4f}")
    print(f"  95% CI: [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}]")
    print(f"  Coverage: {results['coverage']}")
    print(f"  MSE: {results['mse']:.6f}")
    print(f"  N pairs: {results['n_pairs']}")
