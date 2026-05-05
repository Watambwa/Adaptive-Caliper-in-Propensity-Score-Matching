"""
Propensity Score Matching Module
================================

Implements nearest-neighbor propensity score matching with caliper constraints
and comprehensive balance diagnostics.

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import numpy as np
import pandas as pd
from scipy.special import logit
from typing import Tuple, Optional, Dict, List


class PropensityScoreMatcher:
    """
    Implements nearest-neighbor propensity score matching with caliper constraints.
    
    Supports:
    - 1:1 matching without replacement
    - Matching on logit of propensity score
    - Caliper constraints (SD-scaled or absolute)
    """
    
    def __init__(
        self,
        caliper: Optional[float] = None,
        caliper_scale: str = 'logit_sd',
        random_order: bool = True,
        seed: Optional[int] = None
    ):
        """
        Initialize the matcher.
        
        Parameters
        ----------
        caliper : float, optional
            Caliper width. If caliper_scale='logit_sd', this is a multiplier
            of the standard deviation of the logit propensity score.
        caliper_scale : str
            How to interpret caliper: 'logit_sd' (multiplier of SD) or 'absolute'
        random_order : bool
            Whether to match treated units in random order (recommended)
        seed : int, optional
            Random seed for reproducibility
        """
        self.caliper = caliper
        self.caliper_scale = caliper_scale
        self.random_order = random_order
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
        self.matched_pairs_ = None
        self.matched_treated_ = None
        self.matched_control_ = None
        self.n_matched_ = None
        self.caliper_absolute_ = None
        
    def fit(
        self,
        propensity_scores: np.ndarray,
        treatment: np.ndarray
    ) -> 'PropensityScoreMatcher':
        """
        Perform propensity score matching.
        
        Parameters
        ----------
        propensity_scores : np.ndarray
            Estimated propensity scores
        treatment : np.ndarray
            Treatment indicators (0 or 1)
            
        Returns
        -------
        self
        """
        ps = np.asarray(propensity_scores).flatten()
        z = np.asarray(treatment).flatten()
        
        ps_clipped = np.clip(ps, 1e-10, 1 - 1e-10)
        logit_ps = logit(ps_clipped)
        
        treated_idx = np.where(z == 1)[0]
        control_idx = np.where(z == 0)[0]
        
        n_treated = len(treated_idx)
        n_control = len(control_idx)
        
        if self.caliper is not None:
            if self.caliper_scale == 'logit_sd':
                sd_logit = np.std(logit_ps)
                self.caliper_absolute_ = self.caliper * sd_logit
            else:
                self.caliper_absolute_ = self.caliper
        else:
            self.caliper_absolute_ = np.inf
        
        if self.random_order:
            match_order = self.rng.permutation(n_treated)
        else:
            match_order = np.argsort(-logit_ps[treated_idx])
        
        matched_pairs = []
        control_matched = np.zeros(n_control, dtype=bool)
        
        for i in match_order:
            treated_unit = treated_idx[i]
            treated_logit = logit_ps[treated_unit]
            
            available_mask = ~control_matched
            available_control_idx = np.where(available_mask)[0]
            
            if len(available_control_idx) == 0:
                continue
            
            available_control_units = control_idx[available_control_idx]
            distances = np.abs(logit_ps[available_control_units] - treated_logit)
            
            min_dist_idx = np.argmin(distances)
            min_dist = distances[min_dist_idx]
            
            if min_dist <= self.caliper_absolute_:
                control_unit = available_control_units[min_dist_idx]
                matched_pairs.append((treated_unit, control_unit))
                control_matched[available_control_idx[min_dist_idx]] = True
        
        self.matched_pairs_ = matched_pairs
        if len(matched_pairs) > 0:
            pairs_array = np.array(matched_pairs)
            self.matched_treated_ = pairs_array[:, 0]
            self.matched_control_ = pairs_array[:, 1]
        else:
            self.matched_treated_ = np.array([], dtype=int)
            self.matched_control_ = np.array([], dtype=int)
        self.n_matched_ = len(matched_pairs)
        
        return self
    
    def get_matched_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract matched sample from original dataframe."""
        if self.matched_pairs_ is None:
            raise ValueError("Must call fit() before get_matched_data()")
        
        if self.n_matched_ == 0:
            return pd.DataFrame()
        
        treated_df = df.iloc[self.matched_treated_].copy()
        treated_df['pair_id'] = np.arange(self.n_matched_)
        treated_df['match_type'] = 'treated'
        
        control_df = df.iloc[self.matched_control_].copy()
        control_df['pair_id'] = np.arange(self.n_matched_)
        control_df['match_type'] = 'control'
        
        matched_df = pd.concat([treated_df, control_df], ignore_index=True)
        matched_df = matched_df.sort_values(['pair_id', 'Z'], ascending=[True, False])
        
        return matched_df
    
    def get_match_quality(self, propensity_scores: np.ndarray) -> Dict[str, float]:
        """Compute match quality metrics."""
        if self.n_matched_ == 0:
            return {
                'n_matched': 0,
                'mean_distance': np.nan,
                'max_distance': np.nan,
                'median_distance': np.nan
            }
        
        ps_clipped = np.clip(propensity_scores, 1e-10, 1 - 1e-10)
        logit_ps = logit(ps_clipped)
        
        distances = np.abs(
            logit_ps[self.matched_treated_] - logit_ps[self.matched_control_]
        )
        
        return {
            'n_matched': self.n_matched_,
            'mean_distance': np.mean(distances),
            'max_distance': np.max(distances),
            'median_distance': np.median(distances)
        }


def compute_smd(treated_values: np.ndarray, control_values: np.ndarray) -> float:
    """
    Compute standardized mean difference.
    
    SMD = (mean_treated - mean_control) / sqrt((var_treated + var_control) / 2)
    """
    mean_t = np.mean(treated_values)
    mean_c = np.mean(control_values)
    
    var_t = np.var(treated_values, ddof=1)
    var_c = np.var(control_values, ddof=1)
    
    pooled_sd = np.sqrt((var_t + var_c) / 2)
    
    if pooled_sd < 1e-10:
        return 0.0
    
    smd = (mean_t - mean_c) / pooled_sd
    return smd


def compute_variance_ratio(treated_values: np.ndarray, control_values: np.ndarray) -> float:
    """Compute variance ratio (treated / control)."""
    var_t = np.var(treated_values, ddof=1)
    var_c = np.var(control_values, ddof=1)
    
    if var_c < 1e-10:
        return np.inf
    
    return var_t / var_c


def compute_balance_statistics(
    df: pd.DataFrame,
    covariate_cols: List[str],
    treatment_col: str = 'Z'
) -> pd.DataFrame:
    """
    Compute balance statistics for all covariates.
    
    Returns DataFrame with SMD, variance ratio, and means for each covariate.
    """
    treated = df[df[treatment_col] == 1]
    control = df[df[treatment_col] == 0]
    
    results = []
    
    for col in covariate_cols:
        t_vals = treated[col].values
        c_vals = control[col].values
        
        smd = compute_smd(t_vals, c_vals)
        vr = compute_variance_ratio(t_vals, c_vals)
        
        results.append({
            'covariate': col,
            'mean_treated': np.mean(t_vals),
            'mean_control': np.mean(c_vals),
            'sd_treated': np.std(t_vals, ddof=1),
            'sd_control': np.std(c_vals, ddof=1),
            'smd': smd,
            'abs_smd': np.abs(smd),
            'variance_ratio': vr
        })
    
    return pd.DataFrame(results)


def compute_max_abs_smd(
    df: pd.DataFrame,
    covariate_cols: List[str],
    treatment_col: str = 'Z'
) -> float:
    """Compute maximum absolute SMD across all covariates."""
    balance = compute_balance_statistics(df, covariate_cols, treatment_col)
    return balance['abs_smd'].max()


def compute_mean_abs_smd(
    df: pd.DataFrame,
    covariate_cols: List[str],
    treatment_col: str = 'Z'
) -> float:
    """Compute mean absolute SMD across all covariates."""
    balance = compute_balance_statistics(df, covariate_cols, treatment_col)
    return balance['abs_smd'].mean()


if __name__ == "__main__":
    from data_generator import DataGenerator
    
    generator = DataGenerator(seed=42)
    df = generator.generate_dataset(
        n=1000,
        treatment_prevalence=0.5,
        overlap_level=0.6,
        confounding_strength=0.5
    )
    
    e_hat = generator.estimate_propensity_scores(df)
    df['e_hat'] = e_hat
    
    calipers = [0.1, 0.2, 0.5, None]
    
    for cal in calipers:
        matcher = PropensityScoreMatcher(caliper=cal, seed=42)
        matcher.fit(df['e_hat'].values, df['Z'].values)
        
        print(f"\nCaliper: {cal}")
        print(f"  Matched pairs: {matcher.n_matched_}")
        
        if matcher.n_matched_ > 0:
            matched_df = matcher.get_matched_data(df)
            covariate_cols = [f'X{i+1}' for i in range(6)]
            
            before_balance = compute_balance_statistics(df, covariate_cols)
            after_balance = compute_balance_statistics(matched_df, covariate_cols)
            
            print(f"  Max |SMD| before: {before_balance['abs_smd'].max():.4f}")
            print(f"  Max |SMD| after: {after_balance['abs_smd'].max():.4f}")
