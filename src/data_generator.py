"""
Data Generation Module for Adaptive Caliper Selection Simulation Study
========================================================================

Generates synthetic observational study data following the simulation design
specified in the manuscript. Implements the data generating process (DGP)
for Monte Carlo evaluation of propensity score matching methods.

Data Generating Process:
------------------------
1. Covariates: X1, X2, X3 ~ N(0,1); X4, X5, X6 ~ Bernoulli(0.5)
2. Propensity Score: logit(e) = α₀ + Σ αₖXₖ
3. Treatment: Z ~ Bernoulli(e)
4. Outcome: Y = β₀ + τZ + Σ βₖXₖ + ε, where ε ~ N(0,1)

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import expit, logit
from typing import Tuple, Dict, Optional, List
import warnings

from config import (
    N_CONTINUOUS_COVARIATES, N_BINARY_COVARIATES, 
    TRUE_TREATMENT_EFFECT, RANDOM_SEED,
    SAMPLE_SIZES, TREATMENT_PREVALENCES,
    OVERLAP_LEVELS, CONFOUNDING_STRENGTHS
)


class DataGenerator:
    """
    Generates synthetic observational study data for propensity score matching simulations.
    
    This class implements the data generating process (DGP) specified in the manuscript,
    allowing systematic variation of:
    - Sample size
    - Treatment prevalence
    - Propensity score overlap
    - Confounding strength
    
    Attributes
    ----------
    seed : int
        Random seed for reproducibility
    rng : numpy.random.Generator
        Random number generator instance
        
    Examples
    --------
    >>> generator = DataGenerator(seed=42)
    >>> df = generator.generate_dataset(
    ...     n=1000,
    ...     treatment_prevalence=0.5,
    ...     overlap_level=0.6,
    ...     confounding_strength=0.5
    ... )
    >>> print(df.shape)
    (1000, 12)
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the data generator.
        
        Parameters
        ----------
        seed : int, optional
            Random seed for reproducibility. If None, uses RANDOM_SEED from config.
        """
        self.seed = seed if seed is not None else RANDOM_SEED
        self.rng = np.random.default_rng(self.seed)
        
    def set_seed(self, seed: int) -> None:
        """
        Reset the random number generator with a new seed.
        
        Parameters
        ----------
        seed : int
            New random seed
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
    def generate_covariates(self, n: int) -> np.ndarray:
        """
        Generate covariate matrix following the specified DGP.
        
        Generates p = 6 covariates:
        - X1, X2, X3 ~ N(0, 1) (continuous)
        - X4, X5, X6 ~ Bernoulli(0.5) (binary)
        
        Parameters
        ----------
        n : int
            Sample size
            
        Returns
        -------
        X : np.ndarray
            Covariate matrix of shape (n, 6)
        """
        # Continuous covariates ~ N(0, 1)
        X_continuous = self.rng.standard_normal((n, N_CONTINUOUS_COVARIATES))
        
        # Binary covariates ~ Bernoulli(0.5)
        X_binary = self.rng.binomial(1, 0.5, (n, N_BINARY_COVARIATES))
        
        # Combine into single matrix
        X = np.hstack([X_continuous, X_binary.astype(float)])
        
        return X
    
    def compute_propensity_scores(
        self, 
        X: np.ndarray, 
        alpha_magnitude: float,
        target_prevalence: float
    ) -> np.ndarray:
        """
        Compute true propensity scores from the specified model.
        
        Model: logit(e_i) = α₀ + α₁X₁ + α₂X₂ + ... + α₆X₆
        
        The intercept α₀ is calibrated to achieve the target treatment prevalence.
        All slope coefficients are set to alpha_magnitude.
        
        Parameters
        ----------
        X : np.ndarray
            Covariate matrix of shape (n, p)
        alpha_magnitude : float
            Magnitude of propensity score coefficients (controls overlap)
            Higher values → less overlap between treatment groups
        target_prevalence : float
            Target treatment prevalence (proportion treated)
            
        Returns
        -------
        e : np.ndarray
            True propensity scores of shape (n,)
        """
        n, p = X.shape
        
        # Set coefficients (all equal magnitude for simplicity)
        alpha = np.full(p, alpha_magnitude)
        
        # Compute linear predictor without intercept
        linear_pred_no_intercept = X @ alpha
        
        # Calibrate intercept to achieve target prevalence
        alpha_0 = self._calibrate_intercept(
            linear_pred_no_intercept, 
            target_prevalence
        )
        
        # Compute propensity scores
        linear_pred = alpha_0 + linear_pred_no_intercept
        e = expit(linear_pred)
        
        return e
    
    def _calibrate_intercept(
        self, 
        linear_pred: np.ndarray, 
        target_prevalence: float,
        tol: float = 1e-6,
        max_iter: int = 100
    ) -> float:
        """
        Calibrate intercept to achieve target treatment prevalence.
        
        Uses binary search to find the intercept α₀ such that
        E[expit(α₀ + Xα)] ≈ target_prevalence.
        
        Parameters
        ----------
        linear_pred : np.ndarray
            Linear predictor without intercept (Xα)
        target_prevalence : float
            Target treatment prevalence
        tol : float
            Convergence tolerance
        max_iter : int
            Maximum iterations for binary search
            
        Returns
        -------
        alpha_0 : float
            Calibrated intercept
        """
        low, high = -10.0, 10.0
        
        for _ in range(max_iter):
            mid = (low + high) / 2
            current_prevalence = np.mean(expit(mid + linear_pred))
            
            if abs(current_prevalence - target_prevalence) < tol:
                return mid
            elif current_prevalence < target_prevalence:
                low = mid
            else:
                high = mid
                
        return mid
    
    def generate_treatment(self, e: np.ndarray) -> np.ndarray:
        """
        Generate treatment assignments based on propensity scores.
        
        Z_i ~ Bernoulli(e_i)
        
        Parameters
        ----------
        e : np.ndarray
            Propensity scores
            
        Returns
        -------
        Z : np.ndarray
            Treatment indicators (0 or 1)
        """
        Z = self.rng.binomial(1, e)
        return Z
    
    def generate_outcomes(
        self,
        X: np.ndarray,
        Z: np.ndarray,
        beta_magnitude: float,
        tau: float = TRUE_TREATMENT_EFFECT
    ) -> np.ndarray:
        """
        Generate outcomes following the specified model.
        
        Model: Y_i = β₀ + τZ_i + β₁X₁ + β₂X₂ + β₃X₃ + ε_i
        
        Note: Only the first 3 covariates (continuous) affect the outcome,
        creating a scenario where some covariates are confounders and
        others are only predictors of treatment.
        
        Parameters
        ----------
        X : np.ndarray
            Covariate matrix
        Z : np.ndarray
            Treatment indicators
        beta_magnitude : float
            Magnitude of outcome model coefficients (confounding strength)
        tau : float
            True treatment effect (ATT)
            
        Returns
        -------
        Y : np.ndarray
            Observed outcomes
        """
        n = X.shape[0]
        
        # Outcome model coefficients (only first 3 covariates affect outcome)
        beta = np.zeros(X.shape[1])
        beta[:N_CONTINUOUS_COVARIATES] = beta_magnitude
        
        # Intercept
        beta_0 = 0.0
        
        # Error term
        epsilon = self.rng.standard_normal(n)
        
        # Generate outcomes: Y = β₀ + τZ + Xβ + ε
        Y = beta_0 + tau * Z + X @ beta + epsilon
        
        return Y
    
    def generate_dataset(
        self,
        n: int,
        treatment_prevalence: float,
        overlap_level: float,
        confounding_strength: float,
        tau: float = TRUE_TREATMENT_EFFECT
    ) -> pd.DataFrame:
        """
        Generate a complete dataset for simulation.
        
        This is the main method for generating simulation data. It combines
        all components of the DGP into a single DataFrame.
        
        Parameters
        ----------
        n : int
            Sample size
        treatment_prevalence : float
            Target proportion of treated units
        overlap_level : float
            Propensity score coefficient magnitude (higher = less overlap)
        confounding_strength : float
            Outcome model coefficient magnitude
        tau : float
            True treatment effect
            
        Returns
        -------
        df : pd.DataFrame
            Dataset with columns:
            - X1, X2, ..., X6: Covariates
            - Z: Treatment indicator
            - e_true: True propensity score
            - logit_e_true: Logit of true propensity score
            - Y: Observed outcome
            - Y0: Potential outcome under control (for evaluation)
            - Y1: Potential outcome under treatment (for evaluation)
        """
        # Generate covariates
        X = self.generate_covariates(n)
        
        # Compute propensity scores
        e = self.compute_propensity_scores(X, overlap_level, treatment_prevalence)
        
        # Generate treatment
        Z = self.generate_treatment(e)
        
        # Generate outcomes
        Y = self.generate_outcomes(X, Z, confounding_strength, tau)
        
        # Create DataFrame
        covariate_names = [f'X{i+1}' for i in range(X.shape[1])]
        df = pd.DataFrame(X, columns=covariate_names)
        df['Z'] = Z
        df['e_true'] = e
        df['logit_e_true'] = logit(np.clip(e, 1e-10, 1-1e-10))
        df['Y'] = Y
        
        # Add potential outcomes for evaluation (not available in practice)
        # These are used only for computing true bias
        Y0 = Y - tau * Z  # Y(0) = Y - τZ
        Y1 = Y0 + tau     # Y(1) = Y(0) + τ
        df['Y0'] = Y0
        df['Y1'] = Y1
        
        return df
    
    def estimate_propensity_scores(
        self, 
        df: pd.DataFrame,
        covariate_cols: List[str] = None
    ) -> np.ndarray:
        """
        Estimate propensity scores using logistic regression.
        
        This simulates the practical scenario where true propensity scores
        are unknown and must be estimated from observed data.
        
        Parameters
        ----------
        df : pd.DataFrame
            Dataset with covariates and treatment
        covariate_cols : list, optional
            List of covariate column names. If None, uses X1-X6.
            
        Returns
        -------
        e_hat : np.ndarray
            Estimated propensity scores
        """
        from sklearn.linear_model import LogisticRegression
        
        if covariate_cols is None:
            covariate_cols = [f'X{i+1}' for i in range(N_CONTINUOUS_COVARIATES + N_BINARY_COVARIATES)]
        
        X = df[covariate_cols].values
        Z = df['Z'].values
        
        # Fit logistic regression (correctly specified model)
        model = LogisticRegression(
            penalty=None,
            solver='lbfgs',
            max_iter=1000,
            random_state=self.seed
        )
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(X, Z)
        
        e_hat = model.predict_proba(X)[:, 1]
        
        return e_hat


def generate_simulation_scenarios() -> List[Dict]:
    """
    Generate all simulation scenarios based on full factorial design.
    
    Creates 54 scenarios from the combination of:
    - 3 sample sizes × 3 treatment prevalences × 3 overlap levels × 2 confounding strengths
    
    Returns
    -------
    scenarios : list of dict
        List of scenario configurations
    """
    scenarios = []
    scenario_id = 0
    
    for n in SAMPLE_SIZES:
        for prev in TREATMENT_PREVALENCES:
            for overlap_name, overlap_val in OVERLAP_LEVELS.items():
                for conf_name, conf_val in CONFOUNDING_STRENGTHS.items():
                    scenario_id += 1
                    scenarios.append({
                        'scenario_id': scenario_id,
                        'n': n,
                        'treatment_prevalence': prev,
                        'overlap_name': overlap_name,
                        'overlap_level': overlap_val,
                        'confounding_name': conf_name,
                        'confounding_strength': conf_val
                    })
    
    return scenarios


def compute_overlap_statistics(df: pd.DataFrame, ps_col: str = 'e_hat') -> Dict[str, float]:
    """
    Compute propensity score overlap statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset with propensity scores and treatment
    ps_col : str
        Name of propensity score column
        
    Returns
    -------
    stats : dict
        Dictionary of overlap statistics
    """
    ps_treated = df.loc[df['Z'] == 1, ps_col].values
    ps_control = df.loc[df['Z'] == 0, ps_col].values
    
    # Common support region
    common_min = max(ps_treated.min(), ps_control.min())
    common_max = min(ps_treated.max(), ps_control.max())
    
    # Proportion in common support
    prop_treated_in_cs = np.mean((ps_treated >= common_min) & (ps_treated <= common_max))
    prop_control_in_cs = np.mean((ps_control >= common_min) & (ps_control <= common_max))
    
    # C-statistic (AUC)
    from sklearn.metrics import roc_auc_score
    c_stat = roc_auc_score(df['Z'], df[ps_col])
    
    return {
        'common_support_min': common_min,
        'common_support_max': common_max,
        'prop_treated_in_cs': prop_treated_in_cs,
        'prop_control_in_cs': prop_control_in_cs,
        'c_statistic': c_stat,
        'ps_mean_treated': ps_treated.mean(),
        'ps_mean_control': ps_control.mean(),
        'ps_sd_treated': ps_treated.std(),
        'ps_sd_control': ps_control.std()
    }


if __name__ == "__main__":
    # Test data generation
    print("Testing Data Generator")
    print("=" * 60)
    
    generator = DataGenerator(seed=42)
    
    # Generate a test dataset
    df = generator.generate_dataset(
        n=1000,
        treatment_prevalence=0.5,
        overlap_level=0.6,
        confounding_strength=0.5
    )
    
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumn names: {df.columns.tolist()}")
    print(f"\nTreatment distribution:")
    print(df['Z'].value_counts())
    print(f"\nPropensity score summary:")
    print(df['e_true'].describe())
    print(f"\nOutcome summary by treatment:")
    print(df.groupby('Z')['Y'].describe())
    
    # Estimate propensity scores
    e_hat = generator.estimate_propensity_scores(df)
    df['e_hat'] = e_hat
    
    print(f"\nCorrelation between true and estimated PS: {np.corrcoef(df['e_true'], df['e_hat'])[0, 1]:.4f}")
    
    # Compute overlap statistics
    overlap_stats = compute_overlap_statistics(df)
    print(f"\nOverlap Statistics:")
    for key, val in overlap_stats.items():
        print(f"  {key}: {val:.4f}")
