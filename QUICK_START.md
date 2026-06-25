# Quick Start Guide - Professional 54-Scenario Analysis

## 🎯 What You're Getting

A complete, professional simulation study with **25 publication-ready figures** comparing **7 methods** across **54 factorial design scenarios**.

---

## ⚡ Run Your Analysis (3 Simple Steps)

### **Step 1: Test the Setup (2-5 minutes)**
```bash
python test_factorial_design.py
```
✓ Verifies everything works  
✓ Tests 5 scenarios with 50 replications  
✓ Generates sample figures  

### **Step 2: Run Full Simulation (30-60 minutes)**
```bash
python run_full_factorial_simulation.py
```
✓ All 54 scenarios  
✓ 1,000 replications per scenario  
✓ Automatically generates all figures and tables  
✓ Saves intermediate results  

### **Step 3: View Your Results**
```bash
open outputs/figures/
open outputs/tables/
```

---

## 📊 What You Get

### **Main Figures (12):**

#### **Fig 1-6: Individual Scenario Tracking**
Six standalone plots, one per metric:
1. `fig1_scenario_tracking_mean_abs_bias.png` - Bias
2. `fig2_scenario_tracking_rmse.png` - Accuracy
3. `fig3_scenario_tracking_coverage_rate.png` - Coverage
4. `fig4_scenario_tracking_mean_retention.png` - Retention
5. `fig5_scenario_tracking_mean_max_smd.png` - Balance
6. `fig6_scenario_tracking_mean_ci_width.png` - Precision

**Features:**
- All 7 methods, all 54 scenarios
- Background shading by sample size
- Reference lines
- 16×5 inches, perfect for manuscripts

#### **Heatmaps (5): 2×4 Grid Layout**
1. `fig1_heatmap_rmse.png`
2. `fig2_heatmap_mean_abs_bias.png`
3. `fig3_heatmap_coverage_rate.png`
4. `fig4_heatmap_mean_retention.png`
5. `fig5_heatmap_mean_max_smd.png`

**Features:**
- 2 rows × 4 columns (7 methods)
- Values to 2 decimal places
- Consistent color scales
- 18×10 inches

#### **Comprehensive Comparison (1)**
`comprehensive_scenario_comparison.png`

**Features:**
- 3×2 grid, 6 metrics
- All 7 methods
- All 54 scenarios
- 18×14 inches

---

### **Supporting Figures (13):**
- 4 Method ranking plots
- 4 Factor effect plots
- 5 Boxplots

---

### **Tables (13):**
- Overall performance comparison
- Performance by sample size
- Performance by overlap level
- Performance by confounding strength
- Performance by treatment prevalence
- Method win rates
- Detailed scenario results
- Plus formatted versions

---

## 🎨 Key Features

### **All Visualizations:**
✓ **All 7 methods** always included  
✓ **All 54 scenarios** represented  
✓ **2 decimal places** for all values  
✓ **Professional formatting** (300 DPI, publication-ready)  
✓ **Colorblind-friendly palette**  
✓ **Clear labels and legends**  

### **Factorial Design:**
- **3** Sample sizes (500, 1000, 2000)
- **3** Treatment prevalences (0.3, 0.5, 0.7)
- **3** Overlap levels (low, medium, high)
- **2** Confounding strengths (weak, strong)
- **= 54 scenarios total**

### **Methods Compared:**
1. Fixed-0.1 SD
2. Fixed-0.2 SD (Austin's recommendation)
3. Fixed-0.5 SD
4. No Caliper
5. ACS-Balance
6. ACS-Knee
7. ACS-Weighted

---

## 📂 Output Structure

```
outputs/
├── figures/           # 25 publication-ready figures
│   ├── fig1_scenario_tracking_mean_abs_bias.png
│   ├── fig2_scenario_tracking_rmse.png
│   ├── fig3_scenario_tracking_coverage_rate.png
│   ├── fig4_scenario_tracking_mean_retention.png
│   ├── fig5_scenario_tracking_mean_max_smd.png
│   ├── fig6_scenario_tracking_mean_ci_width.png
│   ├── fig1_heatmap_rmse.png
│   ├── fig2_heatmap_mean_abs_bias.png
│   ├── ... (and 17 more)
│   
├── tables/            # 13 comprehensive tables
│   ├── comprehensive_comparison.csv
│   ├── table1_overall_comparison.csv
│   ├── table2_by_sample_size.csv
│   ├── ... (and 10 more)
│   
└── results/           # Raw simulation data
    ├── simulation_results_full.csv
    └── simulation_results_intermediate.csv
```

---

## 🔍 Understanding Your Figures

### **Scenario Tracking Plots (Fig 1-6):**
- **X-axis:** Scenario ID (1-54)
  - Scenarios 1-18: n=500
  - Scenarios 19-36: n=1000
  - Scenarios 37-54: n=2000
- **Y-axis:** Performance metric
- **Lines:** One per method (7 colors)
- **Shading:** Background color shows sample size
- **Red lines:** Reference values (if applicable)

### **Heatmaps (2×4 Grid):**
- **Each subplot:** One method
- **Rows:** (Overlap, Confounding) combinations
- **Columns:** (Sample Size, Prevalence) combinations
- **Colors:** 
  - Green = Good performance
  - Yellow = Moderate
  - Red = Poor performance
- **Numbers:** Mean value across replications (2 decimals)

### **Comprehensive Comparison:**
- **6 panels:** One per metric
- **All 7 methods** tracked across all 54 scenarios
- **Vertical lines:** Separate sample sizes
- **Reference lines:** Target values

---

## 💡 Pro Tips

### **Before Full Simulation:**
1. ✓ Run test first
2. ✓ Check test outputs look good
3. ✓ Close unnecessary programs
4. ✓ Ensure stable power source
5. ✓ Allow 30-60 minutes

### **During Simulation:**
- Progress shown for each scenario
- Intermediate results auto-saved
- Can resume if interrupted
- Parallel processing automatically enabled

### **After Simulation:**
- Review `comprehensive_comparison.csv` for overall results
- Check `fig1_heatmap_rmse.png` for pattern overview
- Use scenario tracking plots for detailed analysis
- Win rates table shows which method dominates

---

## 📊 Interpreting Results

### **Good Performance Indicators:**
- **Low RMSE** (< 0.2)
- **Low bias** (close to 0)
- **Coverage near 0.95** (93-97%)
- **High retention** (> 0.8)
- **Low max SMD** (< 0.1)

### **Method Comparison:**
Look for methods that consistently:
- Achieve low RMSE across scenarios
- Maintain good balance (max SMD ≤ 0.1)
- Retain sufficient samples
- Provide proper uncertainty quantification

### **Factorial Design Insights:**
- Which sample sizes work best?
- How does overlap affect performance?
- Is method robust to prevalence?
- Does confounding matter?

---

## 🎓 For Your Manuscript

### **Suggested Main Text Figures:**
1. Fig 2 (RMSE tracking) - Shows accuracy
2. Fig 3 (Coverage tracking) - Shows reliability
3. Fig 1 (RMSE heatmap) - Shows robustness
4. Comprehensive comparison - Shows overall performance

### **Suggested Main Text Tables:**
1. Table 1 (Overall comparison)
2. Table 6 (Win rates)

### **Supplementary Materials:**
- All remaining figures
- All detailed tables
- Full simulation description

---

## ⚠️ Troubleshooting

### **"Command not found: python"**
Use `python3` instead of `python` on macOS

### **Simulation too slow**
- Check `N_JOBS=-1` in `config.py`
- Reduce `N_REPLICATIONS` for testing
- Close other programs

### **Memory errors**
- Reduce parallel jobs: `N_JOBS=4` in `config.py`
- Process fewer scenarios at once
- Check available RAM

### **Unexpected results**
- Run test first: `python test_factorial_design.py`
- Check verification output
- Review intermediate results

---

## 📚 Additional Resources

- **`IMPLEMENTATION_SUMMARY.md`** - Complete technical details
- **`VISUALIZATION_GUIDE.md`** - Figure specifications
- **`FACTORIAL_DESIGN_GUIDE.md`** - Design explanation
- **`README.md`** - Project overview

---

## ✅ Verification Checklist

After running, verify:
- [ ] 25 figures in `outputs/figures/`
- [ ] 13 tables in `outputs/tables/`
- [ ] Raw results in `outputs/results/`
- [ ] All figures show 7 methods
- [ ] All figures show 54 scenarios
- [ ] Values to 2 decimal places
- [ ] No error messages in output
- [ ] Results make statistical sense

---

## 🚀 Ready to Run!

```bash
# Step 1: Quick test (2-5 minutes)
python test_factorial_design.py

# Step 2: Full simulation (30-60 minutes)
python run_full_factorial_simulation.py

# Step 3: Enjoy your results!
open outputs/figures/fig1_scenario_tracking_mean_abs_bias.png
```

**That's it! Professional simulation analysis in 3 commands.** 🎉

---

**Questions?** All functions are fully documented. See docstrings or guides for details.
