"""
Adaptive Caliper Selection (ACS) Algorithm
===========================================

Implements the multi-objective optimization framework for caliper selection
in propensity score matching.

The ACS algorithm traces the Pareto frontier of the bias-variance trade-off
and selects an optimal caliper based on user-specified criteria:
- Balance-constrained: Largest caliper achieving SMD threshold
- Knee-point: Maximum curvature on the frontier
- Weighted: Minimize weighted combination of imbalance and sample loss

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import numpy as np
import pandas as pd
from scipy.special import logit
from typing import Tuple, Optional, Dict, List, Union
from dataclasses import dataclass

from matching import (
    PropensityScoreMatcher, 
    compute_max_abs_smd, 
    compute_mean_abs_smd,
    compute_balance_statistics
)
from config import CALIPER_GRID, BALANCE_THRESHOLD, LAMBDA_WEIGHTED


@dataclass
class ParetoPoint:
    """Represents a point on the Pareto frontier."""
    caliper: float
    balance: float
    retention: float
    n_matched: int
    is_pareto_optimal: bool = False


@dataclass
class ACSResult:
    """Results from Adaptive Caliper Selection."""
    optimal_caliper: float
    criterion_used: str
    pareto_frontier: List[ParetoPoint]
    all_results: List[ParetoPoint]
    balance_at_optimal: float
    retention_at_optimal: float
    n_matched_at_optimal: int


class AdaptiveCaliperSelector:
    """
    Implements the Adaptive Caliper Selection (ACS) algorithm.
    
    This algorithm traces the Pareto frontier of the bias-variance trade-off
    in propensity score matching and selects an optimal caliper based on
    user-specified criteria.
    """
    
    def __init__(
        self,
        caliper_grid: List[float] = None,
        balance_threshold: float = BALANCE_THRESHOLD,
        lambda_weight: float = LAMBDA_WEIGHTED,
        seed: Optional[int] = None
    ):
        """
        Initialize the ACS algorithm.
        
        Parameters
        ----------
        caliper_grid : list of float, optional
            Grid of caliper values to evaluate (as multiples of SD)
        balance_threshold : float
            SMD threshold for balance criterion (default: 0.1)
        lambda_weight : float
            Weight for balance in weighted criterion (default: 0.5)
        seed : int, optional
            Random seed for reproducibility
        """
        self.caliper_grid = caliper_grid if caliper_grid is not None else CALIPER_GRID
        self.balance_threshold = balance_threshold
        self.lambda_weight = lambda_weight
        self.seed = seed
        
        self.results_ = None
        self.pareto_frontier_ = None
        self.sd_logit_ = None
        
    def fit(
        self,
        df: pd.DataFrame,
        propensity_col: str = 'e_hat',
        treatment_col: str = 'Z',
        covariate_cols: List[str] = None
    ) -> 'AdaptiveCaliperSelector':
        """
        Evaluate all caliper values and identify Pareto frontier.
        
        Parameters
        ----------
        df : pd.DataFrame
            Dataset with propensity scores and covariates
        propensity_col : str
            Name of propensity score column
        treatment_col : str
            Name of treatment column
        covariate_cols : list of str, optional
            Names of covariate columns
            
        Returns
        -------
        self
        """
        if covariate_cols is None:
            covariate_cols = [f'X{i+1}' for i in range(6)]
        
        ps = df[propensity_col].values
        treatment = df[treatment_col].values
        
        ps_clipped = np.clip(ps, 1e-10, 1 - 1e-10)
        logit_ps = logit(ps_clipped)
        self.sd_logit_ = np.std(logit_ps)
        
        n_treated = np.sum(treatment == 1)
        n_control = np.sum(treatment == 0)
        max_matches = min(n_treated, n_control)
        
        results = []
        
        for cal_mult in self.caliper_grid:
            matcher = PropensityScoreMatcher(
                caliper=cal_mult,
                caliper_scale='logit_sd',
                seed=self.seed
            )
            matcher.fit(ps, treatment)
            
            n_matched = matcher.n_matched_
            retention = n_matched / max_matches if max_matches > 0 else 0
            
            if n_matched > 0:
                matched_df = matcher.get_matched_data(df)
                balance = compute_max_abs_smd(matched_df, covariate_cols, treatment_col)
            else:
                balance = np.inf
            
            results.append(ParetoPoint(
                caliper=cal_mult,
                balance=balance,
                retention=retention,
                n_matched=n_matched,
                is_pareto_optimal=False
            ))
        
        self.results_ = results
        self._identify_pareto_frontier()
        
        return self
    
    def _identify_pareto_frontier(self):
        """Identify Pareto-optimal points."""
        sorted_results = sorted(self.results_, key=lambda x: -x.retention)
        
        pareto_frontier = []
        min_balance = np.inf
        
        for point in sorted_results:
            if point.balance < min_balance:
                point.is_pareto_optimal = True
                pareto_frontier.append(point)
                min_balance = point.balance
        
        self.pareto_frontier_ = pareto_frontier
    
    def select_optimal(self, criterion: str = 'balance') -> ACSResult:
        """
        Select optimal caliper based on specified criterion.
        
        Parameters
        ----------
        criterion : str
            Selection criterion: 'balance', 'knee', or 'weighted'
            
        Returns
        -------
        result : ACSResult
            Optimal caliper and associated metrics
        """
        if self.pareto_frontier_ is None:
            raise ValueError("Must call fit() before select_optimal()")
        
        if len(self.pareto_frontier_) == 0:
            raise ValueError("No valid matches found for any caliper")
        
        if criterion == 'balance':
            optimal = self._select_balance_constrained()
        elif criterion == 'knee':
            optimal = self._select_knee_point()
        elif criterion == 'weighted':
            optimal = self._select_weighted()
        else:
            raise ValueError(f"Unknown criterion: {criterion}")
        
        return ACSResult(
            optimal_caliper=optimal.caliper,
            criterion_used=criterion,
            pareto_frontier=self.pareto_frontier_,
            all_results=self.results_,
            balance_at_optimal=optimal.balance,
            retention_at_optimal=optimal.retention,
            n_matched_at_optimal=optimal.n_matched
        )
    
    def _select_balance_constrained(self) -> ParetoPoint:
        """Select largest caliper achieving balance threshold."""
        valid_points = [p for p in self.pareto_frontier_ 
                       if p.balance <= self.balance_threshold]
        
        if len(valid_points) == 0:
            return min(self.pareto_frontier_, key=lambda x: x.balance)
        
        return max(valid_points, key=lambda x: x.retention)
    
    def _select_knee_point(self) -> ParetoPoint:
        """Select caliper at the knee point of the Pareto frontier."""
        if len(self.pareto_frontier_) <= 2:
            return self._select_balance_constrained()
        
        frontier = sorted(self.pareto_frontier_, key=lambda x: x.retention)
        
        retentions = np.array([p.retention for p in frontier])
        balances = np.array([p.balance for p in frontier])
        
        ret_range = retentions.max() - retentions.min()
        bal_range = balances.max() - balances.min()
        
        if ret_range < 1e-10 or bal_range < 1e-10:
            return self._select_balance_constrained()
        
        ret_norm = (retentions - retentions.min()) / ret_range
        bal_norm = (balances - balances.min()) / bal_range
        
        curvatures = []
        for i in range(1, len(frontier) - 1):
            v1 = np.array([ret_norm[i] - ret_norm[i-1], bal_norm[i] - bal_norm[i-1]])
            v2 = np.array([ret_norm[i+1] - ret_norm[i], bal_norm[i+1] - bal_norm[i]])
            
            cross = v1[0] * v2[1] - v1[1] * v2[0]
            mag1 = np.linalg.norm(v1)
            mag2 = np.linalg.norm(v2)
            
            if mag1 < 1e-10 or mag2 < 1e-10:
                curvatures.append(0)
            else:
                curvatures.append(np.abs(cross) / (mag1 * mag2))
        
        if len(curvatures) == 0:
            return self._select_balance_constrained()
        
        max_curv_idx = np.argmax(curvatures) + 1
        return frontier[max_curv_idx]
    
    def _select_weighted(self) -> ParetoPoint:
        """Select caliper minimizing weighted objective."""
        balances = np.array([p.balance for p in self.pareto_frontier_])
        retentions = np.array([p.retention for p in self.pareto_frontier_])
        
        balances = np.where(np.isinf(balances), 10.0, balances)
        
        bal_min, bal_max = balances.min(), balances.max()
        ret_min, ret_max = retentions.min(), retentions.max()
        
        if bal_max - bal_min < 1e-10:
            bal_norm = np.zeros_like(balances)
        else:
            bal_norm = (balances - bal_min) / (bal_max - bal_min)
        
        if ret_max - ret_min < 1e-10:
            ret_norm = np.ones_like(retentions)
        else:
            ret_norm = (retentions - ret_min) / (ret_max - ret_min)
        
        objectives = self.lambda_weight * bal_norm + (1 - self.lambda_weight) * (1 - ret_norm)
        best_idx = np.argmin(objectives)
        
        return self.pareto_frontier_[best_idx]
    
    def get_frontier_dataframe(self) -> pd.DataFrame:
        """Return Pareto frontier as a DataFrame."""
        if self.pareto_frontier_ is None:
            raise ValueError("Must call fit() first")
        
        data = []
        for p in self.pareto_frontier_:
            data.append({
                'caliper': p.caliper,
                'caliper_absolute': p.caliper * self.sd_logit_,
                'max_abs_smd': p.balance,
                'retention': p.retention,
                'n_matched': p.n_matched
            })
        
        return pd.DataFrame(data)
    
    def get_all_results_dataframe(self) -> pd.DataFrame:
        """Return all caliper evaluations as a DataFrame."""
        if self.results_ is None:
            raise ValueError("Must call fit() first")
        
        data = []
        for p in self.results_:
            data.append({
                'caliper': p.caliper,
                'caliper_absolute': p.caliper * self.sd_logit_,
                'max_abs_smd': p.balance,
                'retention': p.retention,
                'n_matched': p.n_matched,
                'is_pareto_optimal': p.is_pareto_optimal
            })
        
        return pd.DataFrame(data)


def run_acs_analysis(
    df: pd.DataFrame,
    propensity_col: str = 'e_hat',
    treatment_col: str = 'Z',
    covariate_cols: List[str] = None,
    caliper_grid: List[float] = None,
    seed: int = None
) -> Dict[str, ACSResult]:
    """
    Run complete ACS analysis with all three criteria.
    
    Returns
    -------
    results : dict
        Dictionary with results for each criterion
    """
    selector = AdaptiveCaliperSelector(
        caliper_grid=caliper_grid,
        seed=seed
    )
    
    selector.fit(df, propensity_col, treatment_col, covariate_cols)
    
    results = {}
    for criterion in ['balance', 'knee', 'weighted']:
        results[criterion] = selector.select_optimal(criterion)
    
    return results


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
    
    covariate_cols = [f'X{i+1}' for i in range(6)]
    
    selector = AdaptiveCaliperSelector(seed=42)
    selector.fit(df, covariate_cols=covariate_cols)
    
    print("Pareto Frontier:")
    print(selector.get_frontier_dataframe().to_string())
    
    print("\n" + "="*60)
    
    for criterion in ['balance', 'knee', 'weighted']:
        result = selector.select_optimal(criterion)
        print(f"\n{criterion.upper()} Criterion:")
        print(f"  Optimal caliper: {result.optimal_caliper:.3f} SD")
        print(f"  Balance (max |SMD|): {result.balance_at_optimal:.4f}")
        print(f"  Retention: {result.retention_at_optimal:.2%}")
        print(f"  N matched: {result.n_matched_at_optimal}")
