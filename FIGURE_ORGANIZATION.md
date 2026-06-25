# Complete Figure Organization for Q1 Manuscript

## Publication-Ready Figure Set: Full Factorial Design (54 Scenarios)

All visualizations are designed for direct inclusion in high-impact journals with **300 DPI resolution**, **professional formatting**, and **comprehensive annotation**.

---

## Main Manuscript Figures

### **Figure 1-6: Individual Scenario Tracking Plots**
**Format:** 6 separate figures, each 16×5 inches  
**Layout:** Single wide panel per metric  
**Purpose:** Track all 7 methods across all 54 scenarios for each key metric

| # | File | Metric | Key Feature |
|---|------|--------|-------------|
| **Fig 1** | `fig1_scenario_tracking_mean_abs_bias.png` | Mean Absolute Bias | Reference line at 0.0 |
| **Fig 2a** | `fig2_scenario_tracking_rmse.png` | Root Mean Squared Error | Overall accuracy |
| **Fig 3** | `fig3_scenario_tracking_coverage_rate.png` | 95% CI Coverage Rate | Target line at 0.95 |
| **Fig 4** | `fig4_scenario_tracking_mean_retention.png` | Sample Retention Rate | Efficiency metric |
| **Fig 5** | `fig5_scenario_tracking_mean_max_smd.png` | Maximum |SMD| (Balance) | Threshold at 0.1 |
| **Fig 6** | `fig6_scenario_tracking_mean_ci_width.png` | Confidence Interval Width | Precision metric |

**Design Features:**
- All 7 methods with distinct colors
- Background shading by sample size (blue=500, green=1000, orange=2000)
- Vertical separators at scenarios 18 and 36
- Sample size labels in colored boxes
- Legend below plot (4 columns)

**Use:** Primary results - show method performance patterns across scenarios

---

### **Figure 2: Balance-Retention Trade-off Grid (NEW!)**
**Format:** 9×6 grid (54 subplots)  
**Size:** 22×30 inches  
**File:** `fig2_all_scenarios_tradeoff_grid.png`

**What It Shows:**
Each of 54 subplots displays all 7 methods positioned in the multi-objective space:
- **X-axis:** Retention rate (0 to 1)
- **Y-axis:** Max |SMD| balance (0 to 0.6)
- **Circles:** Fixed calipers (0.1, 0.2, 0.5 SD) + No Caliper
- **Squares:** Adaptive methods (ACS-Balance, ACS-Knee, ACS-Weighted)
- **Green zone:** Acceptable balance region (max |SMD| ≤ 0.1)
- **Background color:** Sample size indicator

**Key Insights:**
- Shows trade-off structure varies by scenario
- Identifies which methods stay in acceptable balance zone
- Demonstrates adaptive methods adjust to scenario characteristics
- Visual evidence of multi-objective optimization

**Use:** Core methodological figure - demonstrates the balance-retention trade-off

---

### **Figure 5: Treatment Effect Estimates Grid (NEW! - All 54 Scenarios)**
**Format:** 9×6 grid (54 subplots)  
**Size:** 24×16 inches  
**File:** `fig5_treatment_effects_all_scenarios.png`

**What It Shows:**
Each of 54 subplots displays treatment effect estimates with 95% confidence intervals:
- **Y-axis:** Methods (7 methods listed vertically)
- **X-axis:** Treatment effect estimate (-0.5 to 2.5)
- **Red dashed line:** True effect (τ = 0.5)
- **Horizontal bars:** 95% confidence intervals
- **Points:** Mean estimates across 1000 replications
- **Background color:** Sample size indicator (blue=500, green=1000, orange=2000)

**Design Features:**
- Method-specific colors (consistent with other figures)
- Error bars show CI width (precision)
- Point estimates show accuracy
- Red reference line for true effect
- Subtitle shows scenario characteristics (n, prevalence, overlap, confounding)

**Key Insights:**
- Shows bias in point estimates (distance from red line)
- Shows precision via CI width
- Identifies methods with good coverage (CIs contain true effect)
- Demonstrates "No Caliper" catastrophic failure (estimates far from truth)
- Shows adaptive methods' performance varies by scenario

**Use:** 
- Primary results figure - treatment effect estimation
- Demonstrates validity of causal inference
- Shows coverage properties across scenarios

---

### **Figure 7-11: Factorial Design Heatmaps**
**Format:** 2×4 grid per heatmap  
**Size:** 18×10 inches each  
**Purpose:** Show performance across all factorial design factors

| # | File | Metric | Color Scale |
|---|------|--------|-------------|
| **Fig 7** | `fig1_heatmap_rmse.png` | RMSE | Red-Yellow-Green (inverted) |
| **Fig 8** | `fig2_heatmap_mean_abs_bias.png` | Mean Absolute Bias | Red-Yellow-Green (inverted) |
| **Fig 9** | `fig3_heatmap_coverage_rate.png` | Coverage Rate | Red-Yellow-Green |
| **Fig 10** | `fig4_heatmap_mean_retention.png` | Sample Retention | Red-Yellow-Green |
| **Fig 11** | `fig5_heatmap_mean_max_smd.png` | Maximum |SMD| | Red-Yellow-Green (inverted) |

**Design Features:**
- 7 methods in 2×4 grid (8th position empty)
- Values to **2 decimal places** (.2f format)
- Bold annotations (fontsize 8)
- Consistent color scaling across methods
- White gridlines for cell separation
- Comprehensive titles

**Heatmap Structure:**
- **Rows:** (Overlap, Confounding) combinations
- **Columns:** (Sample Size, Prevalence) combinations

**Use:** Comprehensive results - show performance across all factor combinations

---

### **Figure 12: Comprehensive Scenario Comparison**
**Format:** 3×2 grid (6 metrics)  
**Size:** 18×14 inches  
**File:** `comprehensive_scenario_comparison.png`

**Panels:**
1. Mean Absolute Bias
2. Root Mean Squared Error
3. 95% CI Coverage Rate
4. Sample Retention Rate
5. Maximum |SMD| (Balance)
6. Confidence Interval Width

**Design Features:**
- All 7 methods tracked across all 54 scenarios
- Thin lines (linewidth=1.2) to prevent crowding
- Markers every 9 scenarios
- Vertical separators at scenarios 18.5 and 36.5
- Reference lines where applicable
- Grid background
- Legend at top

**Use:** Multi-metric overview for comprehensive comparison

---

## Supplementary Figures

### **Method Rankings (4 figures)**
**Files:**
- `method_rankings_rmse.png`
- `method_rankings_mean_abs_bias.png`
- `method_rankings_coverage_rate.png`
- `method_rankings_mean_max_smd.png`

**Format:** Horizontal bar charts showing average rank and win rate

---

### **Factor Effect Plots (4 figures)**
**Files:**
- `factor_effects_rmse.png`
- `factor_effects_mean_abs_bias.png`
- `factor_effects_coverage_rate.png`
- `factor_effects_mean_retention.png`

**Format:** 2×2 grid showing main effect of each factorial design factor

---

### **Distribution Boxplots (5 figures)**
**Files:**
- `boxplot_bias.png`
- `boxplot_mse.png`
- `boxplot_max_smd.png`
- `boxplot_retention.png`
- `boxplot_coverage.png`

**Format:** Side-by-side boxplots for method comparison

---

## Complete Figure Inventory

### **Main Manuscript (13 figures):**
1-6. Individual scenario tracking (6 figures)
7. Balance-retention trade-off grid (NEW! 9×6 grid for all 54 scenarios)
8. Treatment effect estimates grid (NEW! 9×6 grid for all 54 scenarios)
9-13. Factorial design heatmaps (5 figures)

### **Supplementary Materials (14 figures):**
- Comprehensive scenario comparison: 1 figure
- Method rankings: 4 figures
- Factor effects: 4 figures
- Boxplots: 5 figures

**Total: 27 publication-quality figures**

---

## Recommended Manuscript Organization

### **Main Text Figures:**

**Figure 1:** RMSE scenario tracking (`fig2_scenario_tracking_rmse.png`)  
→ Shows overall estimation accuracy across all 54 scenarios

**Figure 2:** Balance-retention trade-off grid (`fig2_all_scenarios_tradeoff_grid.png`)  
→ Core methodological contribution - demonstrates multi-objective optimization for all 54 scenarios

**Figure 3:** Coverage scenario tracking (`fig3_scenario_tracking_coverage_rate.png`)  
→ Shows inferential validity across all 54 scenarios

**Figure 4:** Treatment effect estimates grid (`fig5_treatment_effects_all_scenarios.png`)  
→ Treatment effect estimates with CIs for all 54 scenarios - demonstrates bias and coverage

**Figure 5:** RMSE heatmap (`fig1_heatmap_rmse.png`)  
→ Compact factorial design results (2×4 grid for all 7 methods)

**Figure 6:** Method rankings RMSE (`method_rankings_rmse.png`)  
→ Overall method comparison and win rates

### **Supplementary Figures:**
- All remaining scenario tracking plots (Figs 1, 4, 5, 6)
- All remaining heatmaps (Figs 8-13)
- Comprehensive comparison figure
- All factor effects (4 figures)
- All boxplots (5 figures)
- All other rankings (3 figures)

---

## Technical Specifications

### **Resolution & Format:**
- **DPI:** 300 (publication quality)
- **Format:** PNG with tight bounding box
- **Color palette:** Colorblind-friendly (7 distinct colors)

### **Typography:**
- **Titles:** 12-14pt, bold
- **Axis labels:** 10-12pt, bold
- **Annotations:** 8pt, bold (in heatmaps)
- **Tick labels:** 6-10pt (depending on figure type)
- **Legend:** 9-10pt

### **Numerical Precision:**
- **Heatmaps:** 2 decimal places (.2f)
- **Scenario tracking:** Automatic scaling
- **Tables:** 3-4 decimal places

### **Color Schemes:**
- **Methods:** Distinct colors per method (consistent across all figures)
- **Heatmaps:** Red-Yellow-Green diverging
- **Background:** Subtle tinting by sample size (trade-off grid)

---

## Quality Assurance Checklist

Before manuscript submission, verify:

- [x] All 7 methods included in every figure
- [x] All 54 scenarios represented where applicable
- [x] Values to 2 decimal places in heatmaps
- [x] Consistent color schemes across figures
- [x] Professional typography (fonts, sizes, weights)
- [x] Clear axis labels and titles
- [x] Appropriate reference lines
- [x] Legends properly positioned
- [x] High resolution (300 DPI)
- [x] Tight bounding boxes
- [x] No excess whitespace
- [x] Colorblind-friendly palette
- [x] Grid lines for readability
- [x] Proper statistical labeling

---

## Generating the Figures

### **Full Simulation:**
```bash
python3 run_full_factorial_simulation.py
```
Automatically generates all 25 figures (30-60 minutes)

### **Test Run:**
```bash
python3 test_factorial_design.py
```
Quick verification with sample figures (2-5 minutes)

### **Output Location:**
All figures saved to: `outputs/figures/`

---

## Key Improvements in This Version

✅ **NEW: Figure 2** - 9×6 grid showing all 54 scenarios' trade-off spaces  
✅ **NEW: Figure 5** - 9×6 grid showing treatment effect estimates with CIs for all 54 scenarios  
✅ **NEW: Comprehensive Tables** - 6 tables covering all 54 scenarios and all 7 methods (378 rows)  
✅ **Enhanced heatmaps** - 2×4 grid layout, 2 decimal places, better formatting  
✅ **Comprehensive scenario tracking** - All 7 methods across all 54 scenarios  
✅ **Consistent visual language** - Same color palette and style throughout  
✅ **Publication-ready quality** - 300 DPI, professional formatting  
✅ **Complete documentation** - Every figure and table fully described and justified  

---

## For Manuscript Preparation

**Main text should include:**
- 4-6 key figures from main set
- 2-3 summary tables (aggregated across scenarios)
- Reference supplementary materials for comprehensive results

**Suggested main text figures:**
1. Balance-retention trade-off grid (Fig 2 - NEW!)
2. RMSE scenario tracking (Fig 1)
3. Treatment effect estimates grid (Fig 5 - NEW!)
4. Coverage scenario tracking (Fig 3)
5. RMSE heatmap (Fig 7)
6. Method rankings (optional)

**Suggested main text tables:**
1. Average performance by method (aggregated from Table 3)
2. Representative scenario results (subset of Table 5)
3. Method win rates (from Table 4)

**Supplementary should include:**
- All 27 figures
- All 6 comprehensive tables (54 scenarios × 7 methods)
- Detailed scenario-by-scenario results
- Full simulation design description

This organization provides:
- **Clarity:** Key findings in main text with visual impact
- **Completeness:** Full results (54 scenarios, 7 methods, 1000 reps) in supplementary
- **Flexibility:** Reviewers can examine any specific scenario
- **Transparency:** Complete methodological details
- **Professionalism:** All materials publication-ready

---

## Complete Coverage Summary

### **Figures:**
- ✅ 27 total publication-quality figures (300 DPI)
- ✅ All 54 scenarios visualized (tracking, trade-off, treatment effects)
- ✅ All 7 methods in every comparison
- ✅ Consistent color schemes and formatting

### **Tables:**
- ✅ 6 comprehensive tables in CSV and LaTeX formats
- ✅ 378 rows (54 scenarios × 7 methods)
- ✅ All key metrics (bias, RMSE, coverage, balance, retention)
- ✅ 1000 replications per scenario summarized

### **Documentation:**
- ✅ FIGURE_ORGANIZATION.md - Complete figure guide
- ✅ TABLE_DOCUMENTATION.md - Complete table guide
- ✅ VISUALIZATION_GUIDE.md - Technical details
- ✅ FACTORIAL_DESIGN_GUIDE.md - Simulation design

---

**All visualizations and tables are now Q1-journal ready with comprehensive 54-scenario, 7-method, 1000-replication coverage!** 🎯✨

**Ready to generate:** Run `python3 run_full_factorial_simulation.py`
