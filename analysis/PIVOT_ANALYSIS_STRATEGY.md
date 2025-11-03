# QSR Consolidator: Pivot Table Analysis Strategy

**Created**: 2025-11-02
**Purpose**: CEO-level strategic analysis framework for AI project portfolio across 30+ business units

---

## Executive Summary

The QSR consolidator contains rich project data, but its **wide format** (99 columns) makes certain pivot analyses challenging. This document outlines:
1. **Analyses you can do immediately** with the current structure
2. **Analyses requiring data transformation** (normalizing KPI and milestone data)
3. **Specific pivot table configurations** for each business question
4. **Data preparation recommendations**

---

## Current Data Structure

**Format**: One row per project
**Columns**: 99 (8 metadata + 91 project fields)

**Key Field Groups**:
- **Metadata** (8): extraction_id, business_id, business_name, sheet_name, submission_date, submission_week, workbook_filename, data_hash
- **Overview** (9): project_name, project_category, strategic_value_level, etc.
- **Resources** (5): contact, product_manager, analyst, tech_lead, executive
- **KPIs** (45): 3 KPIs × 15 fields each (category, name, support_description, measurement_approach, target, actual, delta, notes) × 3 weeks
- **Milestones** (24): 12 milestones × 2 fields each (target date, completed date, days_to_target, notes)
- **Scoring** (5): strategic_value, stage_multiplier, project_score, etc.

---

## Analysis 1: Project Distribution by Category (L1-L5)

### Business Question
*"How many projects are at each strategic value level (L1-L5) across all businesses?"*

### Pivot Table Configuration

**✅ CAN DO IMMEDIATELY** - No data transformation needed

**Pivot Setup**:
- **Rows**: `business_name`
- **Columns**: `project_category` (will show L1-L5)
- **Values**: `project_name` (Count)
- **Filters**: `submission_week` (to analyze specific time periods)

**Secondary Pivot** (Maturity by Category):
- **Rows**: `project_category`
- **Columns**: `stage_multiplier` (or derive current stage from milestone completion)
- **Values**: `project_name` (Count)

**Insights You'll Get**:
- Which BUs focus on basic tools (L1) vs. advanced AI products (L5)
- Portfolio balance across strategic value tiers
- Identification of BUs that may need guidance on higher-value initiatives

**Challenge**: Current stage determination requires looking at milestone completion dates across 12 columns. Recommendation below.

---

## Analysis 2: Point Leaderboard & Distribution by Project Type

### Business Question
*"Which BUs have the highest project scores? How are points distributed by project category?"*

### Pivot Table Configuration

**✅ CAN DO IMMEDIATELY**

**Leaderboard Pivot**:
- **Rows**: `business_name` (sorted descending by sum of scores)
- **Values**: `project_score` (Sum), `project_name` (Count as "# Projects"), `project_score` (Average)
- **Filters**: `submission_week`

**Distribution by Type Pivot**:
- **Rows**: `project_category`
- **Columns**: `stage_multiplier` (proxy for Idea/Dev/Pilot/Live)
- **Values**: `project_score` (Sum)

**Enhanced Leaderboard** (if you add calculated column):
- Add calculated column: `points_per_project = project_score / count_projects`
- Shows efficiency: some BUs may have high total scores due to volume, not quality

**Insights You'll Get**:
- Top performers by total points
- Point concentration: Are points evenly distributed or dominated by a few BUs?
- Whether high scores come from many L1 projects or fewer L5 projects

---

## Analysis 3: Distribution of Project Types per Company

### Business Question
*"Compare the portfolio mix across all BUs - who's doing what?"*

### Pivot Table Configuration

**✅ CAN DO IMMEDIATELY**

**Portfolio Mix Matrix**:
- **Rows**: `business_name`
- **Columns**: `project_category`
- **Values**: `project_name` (Count)
- **Show Values As**: "% of Row Total" (to normalize for BU size)

**Visual Recommendation**: Use a 100% stacked bar chart with BUs on Y-axis

**Strategic Value Matrix**:
- **Rows**: `business_name`
- **Columns**: `strategic_value_level`
- **Values**: `project_name` (Count)

**Insights You'll Get**:
- BUs heavy on L1 (tool adoption) vs. L4/L5 (building AI products)
- Outliers: BUs with unusual portfolio compositions
- Opportunities: BUs that should expand into adjacent categories

---

## Analysis 4: Cross-BU KPI Reporting Comparison

### Business Question
*"How are different BUs reporting on the same KPIs? What's the variation in measurement approaches?"*

### ⚠️ REQUIRES DATA TRANSFORMATION

**Challenge**: KPIs are in wide format (kpi1_category, kpi2_category, kpi3_category). You need to "unpivot" to analyze across BUs.

### Recommended Data Transformation

Create a **normalized KPI table**:

```
| business_name | project_name | kpi_number | kpi_category | kpi_name | support_description | measurement_approach | target | actual | delta | notes |
|---------------|--------------|------------|--------------|----------|---------------------|---------------------|---------|--------|-------|-------|
| ClubOS        | Project A    | 1          | Adoption     | KPI      | How it supports...  | How measured...     | 100     | 80     | -20   | ...   |
| ClubOS        | Project A    | 2          | Productivity | KPI      | How it supports...  | How measured...     | 50      | 60     | +10   | ...   |
| ClubOS        | Project A    | 3          | Cost Savings | KPI      | How it supports...  | How measured...     | 1000    | 900    | -100  | ...   |
```

**How to Create** (two options):

**Option A: Power Query (in Excel)**
1. Load consolidator into Power Query
2. Select kpi1_category through kpi1_notes columns
3. "Unpivot Columns" → creates kpi_number column
4. Repeat for kpi2, kpi3
5. Append all three queries

**Option B: Python Script** (I can create this for you)
- Reads consolidator
- Melts KPI columns into long format
- Outputs `KPI_Analysis_Normalized.xlsx`

### Pivot Table Configuration (After Transformation)

**KPI Category Comparison**:
- **Rows**: `kpi_category`, `business_name`
- **Columns**: `kpi_name`
- **Values**: `project_name` (Count)

**Measurement Approach by KPI**:
- **Rows**: `kpi_category`
- **Columns**: `business_name`
- **Values**: `measurement_approach` (as text - shows in details)
- **Use**: Drill into specific categories to see text descriptions

**Insights You'll Get**:
- Which KPIs are most commonly tracked (Adoption, Productivity, Cost Savings, etc.)
- BUs using similar vs. different measurement approaches for same KPI types
- Identification of best practices for measuring specific KPIs
- BUs that may need guidance on KPI definition

**Additional Analysis**: Create a word frequency analysis of `measurement_approach` text field by `kpi_category` to find common patterns.

---

## Analysis 5: Average Number of KPIs per Category

### Business Question
*"Do L1 projects track fewer KPIs than L5 projects? What's the KPI density by category?"*

### ⚠️ REQUIRES CALCULATED COLUMN (simple)

**Add Calculated Column in Excel**:

```excel
=COUNTIF([kpi1_category], "<>") + COUNTIF([kpi2_category], "<>") + COUNTIF([kpi3_category], "<>")
```

**Name**: `kpi_count`

### Pivot Table Configuration

**KPI Density by Category**:
- **Rows**: `project_category`
- **Values**: `kpi_count` (Average), `project_name` (Count)
- **Calculated Field**: Add "Avg KPIs per Project" = SUM(kpi_count) / COUNT(project_name)

**KPI Density by BU**:
- **Rows**: `business_name`
- **Values**: `kpi_count` (Average, Min, Max)

**Insights You'll Get**:
- Whether higher-value projects (L4/L5) have more rigorous KPI tracking
- BUs that consistently track 3 KPIs vs. those using 1-2
- Correlation between KPI tracking rigor and project success (if you add success metrics)

---

## Analysis 6: Project Maturity by Category

### Business Question
*"What stages are projects in for each category (L1-L5)? Are L1 projects moving faster than L5?"*

### ⚠️ REQUIRES CALCULATED COLUMN (medium complexity)

**Challenge**: Current stage is implicit in milestone completion dates (12 milestones across Idea/Develop/Pilot/Live)

**Add Calculated Column**: `current_stage`

**Logic**:
```
IF(live_general_release_available_completed IS NOT NULL, "Live",
   IF(pilot_deployment_to_beta_completed IS NOT NULL, "Pilot",
      IF(develop_coding_started_completed IS NOT NULL, "Develop",
         IF(idea_project_defined_completed IS NOT NULL, "Idea",
            "Not Started"))))
```

**Or use existing field**: `stage_multiplier` (if this already indicates stage)

### Pivot Table Configuration

**Maturity Distribution**:
- **Rows**: `project_category`
- **Columns**: `current_stage`
- **Values**: `project_name` (Count)
- **Show Values As**: "% of Row Total"

**Timeline Analysis**:
- **Rows**: `project_category`
- **Values**:
  - Days from Idea → Develop: `develop_coding_started_completed - idea_project_defined_completed`
  - Days from Develop → Pilot: `pilot_deployment_to_beta_completed - develop_coding_started_completed`
  - Days from Pilot → Live: `live_general_release_available_completed - pilot_deployment_to_beta_completed`

**Insights You'll Get**:
- Stage distribution: Are most projects stuck in Idea? Or progressing to Live?
- Velocity by category: Do L1 projects move faster (expected) than L5?
- Bottleneck identification: Which stage has longest duration?

---

## Analysis 7: "Days to Target" Performance

### Business Question
*"Which milestones are consistently behind schedule? Which BUs hit targets?"*

### ⚠️ REQUIRES DATA TRANSFORMATION

**Challenge**: 12 milestone "days_to_target" fields in separate columns

### Recommended Data Transformation

Create **normalized milestone table**:

```
| business_name | project_name | milestone_name | stage | target_date | completed_date | days_to_target | notes |
|---------------|--------------|----------------|-------|-------------|----------------|----------------|-------|
| ClubOS        | Project A    | Project Defined| Idea  | 2025-01-15  | 2025-01-10     | OK             | ...   |
| ClubOS        | Project A    | Bus Case       | Idea  | 2025-02-01  | NULL           | 5 Days Late    | ...   |
```

**Transformation Method**: Same as KPI normalization (Power Query or Python)

### Pivot Table Configuration

**On-Time Performance by Stage**:
- **Rows**: `stage` (Idea, Develop, Pilot, Live)
- **Columns**: `days_to_target` (bucketed: "OK", "1-5 Days Late", "6-10 Days Late", ">10 Days Late")
- **Values**: `milestone_name` (Count)

**BU Performance Scorecard**:
- **Rows**: `business_name`
- **Values**:
  - `milestone_name` (Count as "Total Milestones")
  - `days_to_target = "OK"` (Count as "On-Time")
  - Calculated: On-Time % = On-Time / Total
- **Sort**: By On-Time % descending

**Insights You'll Get**:
- Which stages have the most delays (common pattern: Pilot → Live transition)
- BUs that consistently deliver on-time vs. those struggling
- Milestone risk: Which specific milestones are hardest to hit on time?

---

## Analysis 8: Resource Allocation Patterns

### Business Question
*"How are roles distributed? Which BUs have dedicated analysts vs. shared resources?"*

### Pivot Table Configuration

**✅ CAN DO IMMEDIATELY**

**Role Coverage by BU**:
- **Rows**: `business_name`
- **Values**:
  - `contact` (Count)
  - `product_manager` (Count of non-blank)
  - `analyst` (Count of non-blank)
  - `tech_lead` (Count of non-blank)
  - `executive` (Count of non-blank)
- **Calculated Field**: "Role Density" = Average # of roles filled per project

**Resource Sharing Analysis**:
- Create calculated column: `is_shared_resource` (if same name appears >3 times across projects)
- **Rows**: `business_name`
- **Values**: `is_shared_resource` (% of projects)

**Insights You'll Get**:
- BUs with dedicated resources vs. stretched teams
- Correlation between resource coverage and project success
- Executives championing multiple projects (good signal)

---

## Analysis 9: Time Series & Trend Analysis

### Business Question
*"How is the portfolio evolving week-over-week? Are projects progressing or stalling?"*

### Pivot Table Configuration

**✅ CAN DO IMMEDIATELY**

**Portfolio Growth**:
- **Rows**: `submission_week` (grouped by month/quarter)
- **Columns**: `project_category`
- **Values**: `project_name` (Count)
- **Chart**: Line chart showing trend

**Score Progression**:
- **Rows**: `project_name`, `business_name`
- **Columns**: `submission_week`
- **Values**: `project_score`
- **Filter**: Top 20 projects by average score

**Stage Progression Tracking**:
- **Rows**: `project_name`
- **Columns**: `submission_week`
- **Values**: `stage_multiplier` (Last value - to see if it increased)

**Insights You'll Get**:
- Portfolio momentum: Growing or shrinking?
- Project velocity: Which projects are advancing stages vs. stuck?
- Score trends: Are BUs improving their reporting or scoring declining?

---

## Analysis 10: KPI Performance Analysis

### Business Question
*"Which KPIs show positive deltas? Are targets being met?"*

### ⚠️ PARTIALLY POSSIBLE (better with transformation)

**Current State Pivot** (Limited):
- Can analyze kpi1_target vs kpi1_actual individually
- Cannot aggregate across all 3 KPIs easily

**After Normalization**:

**KPI Achievement Rate**:
- **Rows**: `kpi_category`
- **Values**:
  - `delta` (Average)
  - `delta > 0` (Count as "Exceeding Target")
  - `delta < 0` (Count as "Missing Target")
- **Calculated**: % Achieving Target

**Target Setting Realism**:
- **Rows**: `business_name`
- **Columns**: `kpi_category`
- **Values**: `delta / target` (Average - shows % miss/beat)

**Insights You'll Get**:
- Which KPI categories are hardest to achieve (might indicate ambitious targets or execution challenges)
- BUs that consistently beat targets (good execution) vs. miss (need support or unrealistic targets)
- KPI types that may need target recalibration

---

## Recommended Data Preparation Workflow

### Option 1: All-in-Excel (Best for non-technical users)

**Steps**:
1. **Add Calculated Columns** (in consolidator sheet):
   - `kpi_count`: Count non-blank KPIs
   - `current_stage`: Derive from milestone completions
   - `days_in_current_stage`: Date math

2. **Create Unpivot Sheets** using Power Query:
   - `KPI_Normalized`: Unpivot 3 KPIs into long format
   - `Milestones_Normalized`: Unpivot 12 milestones into long format

3. **Create Pivot Tables** from each data source as outlined above

**Pros**: No coding, stays in Excel ecosystem
**Cons**: Manual refresh needed, performance issues with large datasets (>10k rows)

---

### Option 2: Python Pre-Processing (Best for automation)

**I can create a script** that:
1. Reads `AI_QSR_Consolidator.xlsx`
2. Adds calculated columns (kpi_count, current_stage, etc.)
3. Creates normalized tables (KPI_Normalized, Milestones_Normalized)
4. Outputs multi-sheet workbook: `QSR_Analysis_Ready.xlsx`

**Output Sheets**:
- `Consolidator_Enhanced` (original + calculated columns)
- `KPI_Analysis` (normalized KPI data)
- `Milestone_Analysis` (normalized milestone data)
- `Summary_Stats` (pre-calculated aggregations)

**Pros**: Automated, fast, repeatable, handles large datasets
**Cons**: Requires Python environment, initial setup

**Would you like me to build this?**

---

### Option 3: Hybrid Approach (Recommended)

1. **Week 1**: Use Option 1 for immediate analyses (Distribution, Leaderboard, Portfolio Mix)
2. **Week 2**: Request Option 2 script for KPI and Milestone deep-dives
3. **Ongoing**: Schedule Python script to run weekly after data extraction

---

## Quick Win Analyses (Start Here)

If you want **immediate insights today**, start with these 3 pivot tables (no transformation needed):

### 1. Executive Dashboard Pivot

**Purpose**: One-page CEO view

**Pivot Setup**:
- **Rows**: `business_name`
- **Values**:
  - `project_name` (Count as "# Projects")
  - `project_score` (Sum as "Total Points")
  - `project_score` (Average as "Avg Score")
  - `strategic_value` (Average as "Avg Strategic Value")
- **Sorting**: By Total Points descending
- **Conditional Formatting**: Color scale on Total Points

**Add Slicer**: `project_category` (to filter by L1-L5)

**Instant Insights**:
- Top 5 BUs by points
- Portfolio size by BU
- Score quality (high count + low avg = many low-value projects)

---

### 2. Portfolio Composition Matrix

**Purpose**: Compare strategic focus across BUs

**Pivot Setup**:
- **Rows**: `business_name`
- **Columns**: `project_category`
- **Values**: `project_name` (Count)
- **Show Values As**: "% of Row Total"
- **Conditional Formatting**: Color scale (green = high %, red = low %)

**Instant Insights**:
- BUs over-indexed on L1 (basic tools) vs. L5 (AI products)
- Portfolio diversity: Some BUs spread across all categories, others concentrated

---

### 3. Strategic Value Distribution

**Purpose**: Understand value tier allocation

**Pivot Setup**:
- **Rows**: `project_category`
- **Columns**: `strategic_value_level`
- **Values**: `project_name` (Count)
- **Chart Type**: 100% Stacked Bar

**Instant Insights**:
- Whether L5 projects have high strategic value (expected)
- Misalignments: L1 projects with high strategic value (possible mis-categorization)

---

## Advanced Insights (Require Transformation)

Once you have normalized KPI and Milestone data:

### 1. KPI Measurement Playbook

**Analysis**: Text mining of `measurement_approach` by `kpi_category`

**Method**:
1. Export `kpi_category` + `measurement_approach` to CSV
2. Group by `kpi_category`
3. Use word frequency analysis to find common patterns
4. Create "best practice" document for each KPI type

**Output**: Playbook showing how top-performing BUs measure each KPI type

---

### 2. Milestone Risk Heatmap

**Analysis**: Which milestones are consistently late across all BUs?

**Pivot**:
- **Rows**: `milestone_name` (12 milestones)
- **Columns**: `days_to_target_bucket` ("OK", "1-5 Late", "6-10 Late", ">10 Late")
- **Values**: Count
- **Conditional Formatting**: Red = high concentration of delays

**Output**: Identify "high-risk" milestones that need process improvement

---

### 3. Stage Velocity Benchmarking

**Analysis**: How long does each stage take by BU and category?

**Calculated Columns**:
- `idea_duration`: Date diff between first and last Idea milestone
- `develop_duration`: Date diff between first and last Develop milestone
- `pilot_duration`: Date diff between first and last Pilot milestone
- `live_duration`: Date diff between first and last Live milestone

**Pivot**:
- **Rows**: `business_name`, `project_category`
- **Values**: Average duration for each stage
- **Compare**: Against portfolio average (add calculated field)

**Output**: Identify fast-movers and laggards for each stage/category combination

---

## Data Quality Checks to Run First

Before analysis, validate data quality with these checks:

### 1. Completeness Check

**Pivot**:
- **Rows**: Field names (all 91 fields)
- **Values**: `COUNT(field)` and `COUNT_BLANKS(field)`
- **Purpose**: Identify fields with low completion rates

**Red Flags**:
- Required fields (project_name, business_name) with blanks
- KPI fields with <50% completion
- Milestone dates with unusual patterns

---

### 2. Consistency Check

**Validations**:
- `project_category` values match expected (L1-L5 only?)
- `strategic_value_level` values are consistent
- `stage_multiplier` values align with milestone completion
- Date fields are in valid date format

**Method**: Create a "Data Quality" pivot showing distinct values per field

---

### 3. Duplicate Check

**Pivot**:
- **Rows**: `business_name`, `project_name`, `submission_week`
- **Values**: `data_hash` (Count)
- **Filter**: Count > 1

**Purpose**: Ensure deduplication is working (flag true duplicates vs. legitimate weekly re-submissions)

---

## Summary: Your Action Plan

### Phase 1: Immediate (This Week)
- [ ] Create "Executive Dashboard Pivot" (5 min)
- [ ] Create "Portfolio Composition Matrix" (5 min)
- [ ] Create "Strategic Value Distribution" (5 min)
- [ ] Run data quality checks
- [ ] Schedule meeting to review initial insights

### Phase 2: Enhanced Analysis (Next Week)
- [ ] Decide on transformation approach (Excel Power Query vs. Python)
- [ ] Create normalized KPI table
- [ ] Create normalized Milestone table
- [ ] Build "KPI Comparison" pivots
- [ ] Build "Milestone Risk" pivots

### Phase 3: Advanced Insights (Week 3-4)
- [ ] Text mining of KPI measurement approaches
- [ ] Stage velocity benchmarking
- [ ] Trend analysis (week-over-week)
- [ ] Create executive summary deck from insights

---

## Questions to Consider

Before building all pivots, align on:

1. **Primary Audience**: Who will use these analyses? (You only, or shared with BU leaders?)
2. **Update Frequency**: Weekly refresh, monthly reporting, or ad-hoc?
3. **Data Volume**: How many weeks of history do you have? (affects performance)
4. **Action Orientation**: What decisions will these analyses drive?

**Example Decision Framework**:
- **Low Points** → Offer support, share best practices
- **Stuck in Idea Stage** → Investigate resource constraints
- **Missing KPI Targets** → Review target-setting process or execution support

---

## Next Steps

**Recommendation**:
1. Run the 3 "Quick Win" pivots today
2. Share results - tell me what insights surprise you or raise questions
3. I'll refine recommendations and (if you want) build the Python transformation script

**If you'd like the transformation script now**, I can create:
- `prepare_pivot_data.py`: Reads consolidator → outputs analysis-ready workbook
- `PIVOT_CONFIGS.md`: Step-by-step instructions for each pivot table setup

Let me know what you'd like to tackle first!
