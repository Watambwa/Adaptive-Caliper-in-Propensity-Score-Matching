# Visualization Guide for 54-Scenario Factorial Design

## Overview

This guide describes the professional, publication-ready visualizations generated for the complete factorial design simulation study.

---

## Figure Set 1: Individual Scenario Tracking Plots (Fig 1-6)

**Purpose:** Track performance of all 7 methods across all 54 scenarios for each key metric.

### **Figure 1: Mean Absolute Bias**
- **File:** `fig1_scenario_tracking_mean_abs_bias.png`
- **Shows:** Bias in treatment effect estimation
- **Reference line:** 0.0 (unbiased estimation)
- **Format:** Single panel, 16×5 inches

### **Figure 2: Root Mean Squared Error (RMSE)**
- **File:** `fig2_scenario_tracking_rmse.png`
- **Shows:** Overall estimation accuracy
- **Reference line:** None
- **Interpretation:** Lower is better

### **Figure 3: 95% CI Coverage Rate**
- **File:** `fig3_scenario_tracking_coverage_rate.png`
- **Shows:** Proportion of times 95% CI contains true effect
- **Reference line:** 0.95 (target coverage)
- **Interpretation:** Values close to 0.95 indicate proper uncertainty quantification

### **Figure 4: Sample Retention Rate**
- **File:** `fig4_scenario_tracking_mean_retention.png`
- **Shows:** Proportion of treated units successfully matched
- **Reference line:** None
- **Interpretation:** Higher retention preserves statistical power

### **Figure 5: Maximum Absolute SMD (Balance)**
- **File:** `fig5_scenario_tracking_mean_max_smd.png`
- **Shows:** Worst covariate balance after matching
- **Reference line:** 0.1 (acceptable balance threshold)
- **Interpretation:** Values ≤0.1 indicate good balance

### **Figure 6: Confidence Interval Width**
- **File:** `fig6_scenario_tracking_mean_ci_width.png`
- **Shows:** Average width of 95% confidence intervals
- **Reference line:** None
- **Interpretation:** Narrower intervals indicate greater precision

### Design Features:
- **All 7 methods** displayed with distinct colors
- **Background shading** separates sample sizes (n=500, 1000, 2000)
- **Vertical dashed lines** at scenarios 18.5 and 36.5 mark sample size transitions
- **Markers every 6 scenarios** for clarity without clutter
- **Sample size labels** in colored boxes
- **Legend** positioned below plot for easy reference
- **Grid lines** for reading values
- **Values to 2 decimal places** in all annotations

---

## Figure Set 2: Factorial Design Heatmaps (2×4 Grid)

**Purpose:** Show performance across all factor combinations in a compact, professional format.

### Layout:
- **Grid:** 2 rows × 4 columns (7 methods + 1 empty slot)
- **Size:** 18×10 inches for optimal readability
- **Each subplot:** One method's performance across factorial design

### Generated Heatmaps:

1. **RMSE Heatmap** (`fig1_heatmap_rmse.png`)
2. **Mean Absolute Bias Heatmap** (`fig2_heatmap_mean_abs_bias.png`)
3. **Coverage Rate Heatmap** (`fig3_heatmap_coverage_rate.png`)
4. **Sample Retention Heatmap** (`fig4_heatmap_mean_retention.png`)
5. **Maximum |SMD| Heatmap** (`fig5_heatmap_mean_max_smd.png`)

### Heatmap Structure:
- **Rows:** Factorial combinations of (Overlap Level, Confounding Strength)
  - `(high, weak)` - Best case: good overlap, weak confounding
  - `(high, strong)` - Good overlap, strong confounding
  - `(low, weak)` - Poor overlap, weak confounding
  - `(low, strong)` - Worst case: poor overlap, strong confounding
  - `(medium, weak)` - Intermediate scenarios
  - `(medium, strong)` - Intermediate scenarios

- **Columns:** Factorial combinations of (Sample Size, Treatment Prevalence)
  - `(500, 0.3)` through `(2000, 0.7)` - 9 combinations total

### Color Scheme:
- **Red-Yellow-Green (inverted)** for metrics where lower is better (RMSE, Bias, SMD)
- **Red-Yellow-Green** for metrics where higher is better (Coverage, Retention)
- **Consistent scale** across all methods for each metric (using 2nd-98th percentiles)
- **White gridlines** separate cells for clarity

### Formatting Features:
- **2 decimal places** (.2f format) for all values
- **Bold annotations** (fontsize 8) for readability
- **Colorbar** with metric label on each subplot
- **Consistent axis labels** across all subplots
- **Professional titles** with method names
- **Comprehensive suptitle** explaining factorial design

---

## Figure Set 3: Comprehensive Scenario Comparison

**File:** `comprehensive_scenario_comparison.png`

### Purpose:
Multi-panel figure tracking 6 key metrics across all 54 scenarios with all 7 methods.

### Layout:
- **Grid:** 3 rows × 2 columns
- **Size:** 18×14 inches
- **6 metrics:** Bias, RMSE, Coverage, Retention, Balance, CI Width

### Design Features:
- **Thinner lines** (linewidth=1.2) to prevent overcrowding with 7 methods
- **Periodic markers** every 9 scenarios for visual anchors
- **Vertical separator lines** at scenarios 18.5 and 36.5
- **Reference lines** for Coverage (0.95), Bias (0.0), and Balance (0.1)
- **Sample size organization** clearly indicated in subtitle
- **Grid background** for precise value reading
- **Legend** at top with all 7 methods
- **Informative titles** for each panel

### Interpretation Guide:
- **Scenarios 1-18:** n=500 (small sample)
- **Scenarios 19-36:** n=1000 (medium sample)  
- **Scenarios 37-54:** n=2000 (large sample)

Within each sample size:
- **Scenarios cycle through:** 3 prevalences × 3 overlaps × 2 confounding levels

---

## Additional Visualizations

### Method Rankings
**Files:** `method_rankings_[metric].png`
- **Left panel:** Average rank across scenarios (lower = better)
- **Right panel:** Win rate (% scenarios where method is best)
- **Horizontal bar charts** for easy comparison
- **Color-coded** by method
- **Generated for:** RMSE, Bias, Coverage, Balance

### Factor Effect Plots
**Files:** `factor_effects_[metric].png`
- **2×2 grid:** One panel per factor
- **Line plots** showing main effect of each factor
- **All 4 ACS and Fixed-0.2 methods** shown
- **Identifies:** Which factors most influence performance
- **Generated for:** RMSE, Bias, Coverage, Retention

### Boxplots
**Files:** `boxplot_[metric].png`
- **Distribution comparisons** across all scenarios
- **Color-coded boxes** by method
- **Reference lines** where appropriate
- **Shows variability** and outliers
- **Generated for:** Bias, MSE, Balance, Retention, Coverage

---

## Technical Specifications

### Color Palette (Colorblind-Friendly):
- **Fixed-0.1:** `#E41A1C` (Red)
- **Fixed-0.2:** `#377EB8` (Blue)
- **Fixed-0.5:** `#4DAF4A` (Green)
- **No Caliper:** `#984EA3` (Purple)
- **ACS-Balance:** `#FF7F00` (Orange)
- **ACS-Knee:** `#FFFF33` (Yellow)
- **ACS-Weighted:** `#A65628` (Brown)

### Resolution:
- **DPI:** 300 (publication quality)
- **Format:** PNG with tight bounding box
- **File sizes:** Optimized for manuscripts and presentations

### Typography:
- **Font family:** Sans-serif (Arial/Helvetica/DejaVu Sans)
- **Titles:** 12-14pt, bold
- **Axis labels:** 10-12pt, bold
- **Tick labels:** 8-10pt
- **Annotations:** 8pt, bold
- **Legend:** 9-10pt

### Layout Principles:
1. **Consistency:** Same visual language across all figures
2. **Clarity:** Grid lines, reference lines, and clear labels
3. **Completeness:** All 7 methods, all 54 scenarios
4. **Compactness:** Efficient use of space without clutter
5. **Professionalism:** Publication-ready formatting
6. **Precision:** 2 decimal places for all numerical displays

---

## Figure File Naming Convention

### Scenario Tracking:
- `fig1_scenario_tracking_mean_abs_bias.png`
- `fig2_scenario_tracking_rmse.png`
- `fig3_scenario_tracking_coverage_rate.png`
- `fig4_scenario_tracking_mean_retention.png`
- `fig5_scenario_tracking_mean_max_smd.png`
- `fig6_scenario_tracking_mean_ci_width.png`

### Heatmaps:
- `fig1_heatmap_rmse.png`
- `fig2_heatmap_mean_abs_bias.png`
- `fig3_heatmap_coverage_rate.png`
- `fig4_heatmap_mean_retention.png`
- `fig5_heatmap_mean_max_smd.png`

### Comprehensive:
- `comprehensive_scenario_comparison.png`

### Supporting:
- `method_rankings_[metric].png`
- `factor_effects_[metric].png`
- `boxplot_[metric].png`

---

## Usage in Manuscript

### Main Text Figures (6):
1. **Figure 1 (Bias tracking)** - Shows unbiasedness across scenarios
2. **Figure 2 (RMSE tracking)** - Shows overall accuracy
3. **Figure 3 (Coverage tracking)** - Shows proper uncertainty quantification
4. **Figure 4 (Heatmap - RMSE)** - Compact factorial design results
5. **Figure 5 (Method rankings)** - Overall method comparison
6. **Figure 6 (Comprehensive comparison)** - Multi-metric overview

### Supplementary Figures:
- Remaining heatmaps (Bias, Coverage, Retention, Balance)
- Factor effect plots
- Boxplots
- Additional scenario tracking plots

---

## Generating the Figures

### Quick Test (5 scenarios):
```bash
python test_factorial_design.py
```
Generates test versions to verify formatting.

### Full Study (54 scenarios):
```bash
python run_full_factorial_simulation.py
```
Generates all figures automatically.

### From Saved Results:
```python
import pandas as pd
from visualization import *

# Load results
summary_df = pd.read_csv('outputs/tables/simulation_summary.csv')

# Generate specific figures
tracking_figs = plot_individual_scenario_tracking(summary_df, save_dir='outputs/figures')
heatmap_figs = plot_factorial_heatmaps(summary_df, save_dir='outputs/figures')
comp_fig = create_scenario_comparison_figure(summary_df, save_path='outputs/figures/comparison.png')
```

---

## Quality Assurance Checklist

- [x] All 7 methods included in every figure
- [x] All 54 scenarios represented
- [x] Values displayed to 2 decimal places
- [x] Consistent color scheme across figures
- [x] Professional formatting (fonts, spacing, alignment)
- [x] Clear axis labels and titles
- [x] Appropriate reference lines
- [x] Legends properly positioned
- [x] High-resolution output (300 DPI)
- [x] Tight bounding boxes (no excess whitespace)
- [x] Colorblind-friendly palette
- [x] Grid lines for readability
- [x] Proper statistical labeling

---

## Tips for Presentation

### For Talks:
- Use **scenario tracking plots** (Fig 1-6) to tell the story metric-by-metric
- Show **heatmaps** to demonstrate robustness across design space
- Use **rankings** for quick method comparison

### For Papers:
- Include **2-3 main figures** in main text
- Relegate **detailed comparisons** to supplementary materials
- Reference **heatmaps** for comprehensive results

### For Posters:
- Use **comprehensive comparison figure** as centerpiece
- Add **1-2 key heatmaps** for detail
- Include **method ranking bar chart** for quick takeaways

---

This visualization system provides a complete, professional presentation of the 54-scenario factorial design results suitable for high-impact statistical and medical journals.
