"""
Configuration Settings for Adaptive Caliper Selection Simulation Study
========================================================================

A Multi-Objective Optimization Framework for Adaptive Caliper Selection 
in Propensity Score Matching: Balancing Covariate Equilibrium and Statistical Efficiency

Author: Perkins Watambwa et al.
Centre for Sexual Health and HIV/AIDS Research (CeSHHAR), Zimbabwe
"""

import os
from pathlib import Path

# ============================================================================
# DIRECTORY SETTINGS
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
OUTPUT_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"
RESULTS_DIR = OUTPUT_DIR / "results"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, FIGURES_DIR, TABLES_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================
RANDOM_SEED = 42
N_REPLICATIONS = 1000  # Number of Monte Carlo replications per scenario

# Sample sizes to evaluate (following Austin, 2011b methodology)
SAMPLE_SIZES = [500, 1000, 2000]

# Treatment prevalence levels (asymmetric and symmetric designs)
TREATMENT_PREVALENCES = [0.3, 0.5, 0.7]

# Overlap levels (propensity score coefficient magnitudes)
# Higher values = less overlap (more separation between treatment groups)
OVERLAP_LEVELS = {
    'high': 0.3,      # High overlap (small coefficients, similar PS distributions)
    'medium': 0.6,    # Medium overlap
    'low': 1.0        # Low overlap (large coefficients, separated PS distributions)
}

# Confounding strength levels (outcome model coefficient magnitudes)
CONFOUNDING_STRENGTHS = {
    'weak': 0.3,      # Weak confounding
    'strong': 1.0     # Strong confounding
}

# True treatment effect (ATT)
TRUE_TREATMENT_EFFECT = 0.5

# Number of covariates
N_CONTINUOUS_COVARIATES = 3
N_BINARY_COVARIATES = 3
N_TOTAL_COVARIATES = N_CONTINUOUS_COVARIATES + N_BINARY_COVARIATES

# ============================================================================
# CALIPER SETTINGS
# ============================================================================
# Caliper grid for adaptive selection (multiples of SD of logit propensity score)
# Fine grid for precise Pareto frontier characterization
CALIPER_GRID = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 
                0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0]

# Fixed caliper values for comparison (benchmark methods)
FIXED_CALIPERS = {
    'Fixed-0.1': 0.1,
    'Fixed-0.2': 0.2,  # Austin's (2011b) recommendation
    'Fixed-0.5': 0.5
}

# Balance threshold for ACS-Balance criterion (SMD threshold)
BALANCE_THRESHOLD = 0.1

# Lambda for weighted criterion (balance vs. retention tradeoff)
LAMBDA_WEIGHTED = 0.5

# ============================================================================
# MATCHING SETTINGS
# ============================================================================
MATCHING_RATIO = 1  # 1:1 matching
WITH_REPLACEMENT = False

# ============================================================================
# EVALUATION THRESHOLDS
# ============================================================================
SMD_THRESHOLD = 0.1  # Threshold for acceptable balance (Normand et al., 2001)
VARIANCE_RATIO_LOWER = 0.5
VARIANCE_RATIO_UPPER = 2.0

# ============================================================================
# VISUALIZATION SETTINGS (Publication Quality)
# ============================================================================
FIGURE_DPI = 300
FIGURE_FORMAT = 'png'

# Color palette for methods (colorblind-friendly)
METHOD_COLORS = {
    'Fixed-0.1': '#E41A1C',      # Red
    'Fixed-0.2': '#377EB8',      # Blue
    'Fixed-0.5': '#4DAF4A',      # Green
    'No Caliper': '#984EA3',     # Purple
    'ACS-Balance': '#FF7F00',    # Orange
    'ACS-Knee': '#FFFF33',       # Yellow
    'ACS-Weighted': '#A65628'    # Brown
}

# Method display names for figures
METHOD_NAMES = {
    'Fixed-0.1': 'Fixed (0.1 SD)',
    'Fixed-0.2': 'Fixed (0.2 SD)',
    'Fixed-0.5': 'Fixed (0.5 SD)',
    'No Caliper': 'No Caliper',
    'ACS-Balance': 'ACS-Balance',
    'ACS-Knee': 'ACS-Knee',
    'ACS-Weighted': 'ACS-Weighted'
}

# Publication-quality matplotlib settings
PLT_PARAMS = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'axes.linewidth': 1.0,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'xtick.major.width': 1.0,
    'ytick.major.width': 1.0,
    'legend.fontsize': 9,
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'figure.titlesize': 13,
    'figure.dpi': 300,
    'figure.figsize': (8, 6),
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'lines.linewidth': 1.5,
    'lines.markersize': 6,
    'grid.alpha': 0.3,
    'grid.linestyle': '--'
}

# ============================================================================
# PARALLEL PROCESSING
# ============================================================================
N_JOBS = -1  # Use all available cores
VERBOSE = 1

# ============================================================================
# SCENARIO GENERATION
# ============================================================================
def generate_all_scenarios():
    """
    Generate all simulation scenarios based on full factorial design.
    
    Returns
    -------
    scenarios : list of dict
        List of scenario configurations (54 total scenarios)
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
                        'confounding_strength': conf_val,
                        'description': f"n={n}, prev={prev}, overlap={overlap_name}, conf={conf_name}"
                    })
    
    return scenarios


if __name__ == "__main__":
    print("Adaptive Caliper Selection Configuration")
    print("=" * 50)
    print(f"Base directory: {BASE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"\nSimulation Parameters:")
    print(f"  Replications: {N_REPLICATIONS}")
    print(f"  Sample sizes: {SAMPLE_SIZES}")
    print(f"  Treatment prevalences: {TREATMENT_PREVALENCES}")
    print(f"  Overlap levels: {list(OVERLAP_LEVELS.keys())}")
    print(f"  Confounding strengths: {list(CONFOUNDING_STRENGTHS.keys())}")
    print(f"\nTotal scenarios: {len(generate_all_scenarios())}")
