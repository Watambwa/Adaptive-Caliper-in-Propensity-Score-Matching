"""
Adaptive Caliper Selection for Propensity Score Matching
=========================================================

A Multi-Objective Optimization Framework for Adaptive Caliper Selection 
in Propensity Score Matching: Balancing Covariate Equilibrium and Statistical Efficiency

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

from .config import *
from .data_generator import DataGenerator, generate_simulation_scenarios
from .matching import (
    PropensityScoreMatcher,
    compute_smd,
    compute_variance_ratio,
    compute_balance_statistics,
    compute_max_abs_smd,
    compute_mean_abs_smd
)
from .adaptive_caliper import (
    AdaptiveCaliperSelector,
    ACSResult,
    ParetoPoint,
    run_acs_analysis
)
from .treatment_effect import (
    estimate_att_matched,
    evaluate_treatment_effect_estimation
)
from .simulation_runner import (
    run_single_replication,
    run_scenario_simulation,
    run_full_simulation,
    summarize_results
)

__version__ = '1.0.0'
__author__ = 'Perkins Watambwa et al.'
