# Optimal Caliper Selection Analysis: All 54 Scenarios

## Overview

This analysis identifies the **optimal caliper** for each of the 54 factorial design scenarios. The optimal caliper is defined as the **highest caliper value** that achieves acceptable balance (max |SMD| < 0.1).

---

## Table 7: Optimal Caliper Selection Table

### **File:** `table7_optimal_caliper_all_scenarios.csv` + `.tex`

**Purpose:** Show the best caliper choice for each scenario based on balance-retention trade-off.

### Columns:

1. **Scenario ID** - Numeric identifier (1-54)
2. **Scenario** - Complete descriptor: `"n=500, prev=0.3, high, weak"`
3. **Caliper** - Optimal caliper in SD of logit PS (e.g., "0.20")
4. **Caliper_Absolute** - Absolute caliper value (calculated)
5. **Max_Abs_SMD** - Maximum absolute SMD achieved (should be < 0.1)
6. **Retention** - Retention rate achieved
7. **N_Matched** - Average number of matched pairs
8. **Is_Pareto** - TRUE if achieves balance threshold, FALSE otherwise
9. **Optimal** - TRUE or FALSE with reason

### Selection Criteria:

**For each scenario:**
- Filter all calipers to those achieving **max |SMD| < 0.1**
- Among acceptable calipers, select the one with **highest retention**
- This is guaranteed to be on the Pareto frontier

**If no caliper achieves threshold:**
- Report the caliper with lowest max |SMD|
- Mark as `Is_Pareto: FALSE`
- Mark as `Optimal: FALSE (No acceptable balance)`

### Example Rows:

```csv
Scenario ID,Scenario,Caliper,Caliper_Absolute,Max_Abs_SMD,Retention,N_Matched,Is_Pareto,Optimal
1,n=500, prev=0.3, high, weak,0.25,0.122604,0.0681,0.5919,148.3,TRUE,TRUE
2,n=500, prev=0.3, high, strong,0.20,0.098123,0.0952,0.5789,144.7,TRUE,TRUE
17,n=1000, prev=0.5, medium, weak,0.35,0.175382,0.0987,0.7123,356.2,TRUE,TRUE
```

---

## Visualizations

### **1. Comprehensive Optimal Caliper Visualization**

**File:** `optimal_caliper_comprehensive.png`  
**Size:** 20×12 inches  
**Format:** 2×2 panel layout

#### **Panel 1: Bar Chart (Top, Full Width)**
- **X-axis:** Scenario ID (1-54)
- **Y-axis:** Optimal caliper (SD of logit PS)
- **Colors:** 
  - Green: Achieves balance threshold (max |SMD| < 0.1)
  - Red: Does not achieve threshold
- **Reference line:** Blue dashed at 0.2 (Austin's recommendation)
- **Shows:** How optimal caliper varies across scenarios

#### **Panel 2: Balance-Retention Scatter (Bottom Left)**
- **X-axis:** Retention rate
- **Y-axis:** Maximum |SMD|
- **Colors:** Green (acceptable) vs Red (not acceptable)
- **Green zone:** Shaded region below 0.1 threshold
- **Shows:** Where optimal points fall in trade-off space

#### **Panel 3: Boxplots by Sample Size (Bottom Right)**
- **Groups:** n=500, n=1000, n=2000
- **Y-axis:** Optimal caliper values
- **Shows:** Distribution of optimal calipers by sample size
- **Labels:** Show count of acceptable scenarios per group

### **2. Optimal Caliper Heatmap**

**File:** `optimal_caliper_heatmap.png`  
**Size:** 16×10 inches  
**Format:** Heatmap showing factorial design structure

#### **Layout:**
- **Rows:** (Overlap, Confounding) combinations
- **Columns:** (Sample Size, Prevalence) combinations
- **Cell values:** Optimal caliper (to 2 decimal places)
- **Color scale:** Red-Yellow-Green
  - Green = Higher caliper (more lenient, better retention)
  - Red = Lower caliper (stricter, better balance)

#### **Interpretation:**
- **Patterns by sample size:** Does optimal caliper increase with n?
- **Patterns by prevalence:** Effect of treatment prevalence
- **Patterns by overlap:** How does propensity score overlap affect optimal caliper?
- **Patterns by confounding:** Does confounding strength matter?

---

## Key Insights from Optimal Caliper Analysis

### **1. Comparison to Austin's Recommendation**

The blue dashed line at 0.2 SD shows Austin's (2011b) recommendation. The analysis reveals:
- **Scenarios where 0.2 is optimal** (green bar at or near 0.2)
- **Scenarios requiring stricter caliper** (green bar < 0.2)
- **Scenarios allowing more lenient caliper** (green bar > 0.2)

### **2. Sample Size Effects**

Boxplot panel shows whether optimal caliper depends on sample size:
- **Larger n:** May allow larger calipers (better matching)
- **Smaller n:** May require smaller calipers (maintain balance)

### **3. Scenario-Specific Recommendations**

The table provides specific guidance:
- **Use Scenario column** to find scenarios similar to your data
- **Use Caliper column** for the recommended value
- **Check Is_Pareto** to ensure balance is achievable

### **4. Failure Cases**

Red bars/points indicate scenarios where:
- No caliper achieves max |SMD| < 0.1
- Even strictest matching has residual imbalance
- May need alternative methods (e.g., weighting, regression adjustment)

---

## Using the Results

### **For Practitioners:**

**Step 1:** Identify your scenario characteristics:
- Sample size (n)
- Treatment prevalence
- Expected propensity score overlap
- Expected confounding strength

**Step 2:** Find matching scenario in Table 7

**Step 3:** Use the optimal caliper value

**Step 4:** Check if balance threshold is achievable (Is_Pareto = TRUE)

### **For Researchers:**

**Manuscript Use:**
- Include Table 7 in supplementary materials
- Show heatmap in main text to illustrate factorial design patterns
- Use comprehensive visualization to show variability across scenarios

**Key Messages:**
1. "Optimal caliper is scenario-specific"
2. "Austin's 0.2 SD is not universally optimal"
3. "Balance threshold is achievable in X out of 54 scenarios"
4. "Optimal caliper ranges from Y to Z across scenarios"

---

## Statistical Interpretation

### **Pareto Optimality**

A caliper is **Pareto optimal** if:
- No other caliper achieves both better balance AND better retention
- Trade-off between balance and retention is optimal

The highest caliper with acceptable balance is guaranteed to be Pareto optimal because:
- It maximizes retention (higher caliper = more matches)
- While maintaining balance (max |SMD| < 0.1)
- Any higher caliper would violate balance
- Any lower caliper would reduce retention unnecessarily

### **Balance Threshold Rationale**

**max |SMD| < 0.1** is used because:
- Widely accepted in literature (Normand et al., 2001; Austin, 2011)
- Indicates negligible residual confounding
- Ensures sufficient covariate balance for causal inference

### **Retention Considerations**

High retention is important for:
- **Statistical power:** More matched pairs = narrower CIs
- **Efficiency:** Less data waste
- **External validity:** Matched sample closer to original sample

---

## Technical Details

### **Caliper Types:**

1. **Caliper (SD):** Multiple of standard deviation of logit PS
   - Standard unit used in literature
   - Comparable across scenarios
   
2. **Caliper_Absolute:** Actual distance threshold
   - Calculated as: Caliper × SD(logit PS)
   - Scenario-specific value

### **Aggregation:**

For each scenario:
- Mean metrics across 1,000 replications
- For each caliper in grid (0.05 to 2.0 SD)
- Select optimal based on criteria

### **Data Requirements:**

The optimal caliper table requires:
- Raw results with `caliper` column
- Multiple calipers evaluated per scenario
- Balance and retention metrics

---

## Output Summary

### **Generated Files:**

✅ `table7_optimal_caliper_all_scenarios.csv` - Full table (54 rows)  
✅ `table7_optimal_caliper_all_scenarios.tex` - LaTeX version  
✅ `optimal_caliper_comprehensive.png` - Multi-panel visualization  
✅ `optimal_caliper_heatmap.png` - Factorial design heatmap  

### **Coverage:**

- ✅ All 54 scenarios
- ✅ Optimal caliper for each scenario
- ✅ Balance and retention trade-off
- ✅ Pareto optimality assessment
- ✅ Comparison to Austin's recommendation
- ✅ Publication-ready visualizations (300 DPI)

---

## Manuscript Integration

### **Main Text Figure:**

**Figure X:** Optimal Caliper Heatmap
```
"Optimal caliper selection across the 54-scenario factorial design. 
Cell values show the highest caliper (in SD of logit propensity score) 
achieving maximum |SMD| < 0.1. Green indicates higher optimal calipers 
(more lenient matching), red indicates lower optimal calipers (stricter 
matching required for balance)."
```

### **Supplementary Figure:**

**Figure SX:** Comprehensive Optimal Caliper Analysis
```
"Comprehensive analysis of optimal caliper selection. Panel A shows 
optimal caliper for each scenario (green: achieves balance threshold; 
red: threshold not achievable). Panel B shows optimal points in 
balance-retention space. Panel C shows distribution by sample size."
```

### **Supplementary Table:**

**Table SX:** Optimal Caliper Selection
```
"Optimal caliper for each factorial design scenario. Optimal caliper 
is defined as the highest caliper achieving maximum |SMD| < 0.1."
```

---

## Example Analysis Workflow

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load optimal caliper table
optimal_df = pd.read_csv('outputs/tables/table7_optimal_caliper_all_scenarios.csv')

# How many scenarios achieve balance threshold?
n_acceptable = (optimal_df['Is_Pareto'] == 'TRUE').sum()
print(f"{n_acceptable} out of 54 scenarios achieve balance threshold")

# What's the range of optimal calipers?
acceptable = optimal_df[optimal_df['Is_Pareto'] == 'TRUE']
optimal_calipers = pd.to_numeric(acceptable['Caliper'])
print(f"Optimal caliper range: {optimal_calipers.min():.2f} to {optimal_calipers.max():.2f}")

# How does it compare to Austin's 0.2?
within_austin = ((optimal_calipers >= 0.15) & (optimal_calipers <= 0.25)).sum()
print(f"{within_austin} scenarios have optimal caliper near Austin's 0.2")
```

---

## References

- **Austin, P. C. (2011b).** Optimal caliper widths for propensity-score matching when estimating differences in means and differences in proportions in observational studies. *Pharmaceutical Statistics*, 10(2), 150-161.

- **Normand, S. L. T., et al. (2001).** Validating recommendations for coronary angiography following acute myocardial infarction in the elderly: A matched analysis using propensity scores. *Journal of Clinical Epidemiology*, 54(4), 387-398.

---

**All optimal caliper analysis tools are now ready for Q1 journal publication!** 🎯✨
