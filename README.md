# AI QSR Consolidator

Automated ETL system for consolidating AI project tracking data from 30 business units into a single master Excel file.

## Overview

This system extracts 91 fields per project from business unit workbooks, validates and cleans the data, marks duplicates, and appends to a master consolidator file with full audit trail. Includes comprehensive analysis capabilities for generating insights from consolidated data.

**Key Features:**

**ETL Pipeline:**
- Config-driven field extraction (91 fields from P1-P10 sheets)
- 6-gate file validation (catches 90% of errors before extraction)
- Error aggregation (partial success - continue on failures)
- Hash-based deduplication (marks duplicates, preserves all data)
- Complete audit trail (extraction logs, archived workbooks)
- Test/live environment separation

**Analysis Capabilities:**
- Interactive Plotly.js visualizations (11 charts)
- KPI measurement quality scoring (0-10 scale)
- Data normalization (KPI and milestone long-format)
- Comprehensive markdown reports with insights
- Executive dashboards and leadership questions

## Quick Start

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp .env.example .env
```

### Usage

Process a single workbook:

```bash
python main.py --file path/to/workbook.xlsx --business BU_001
```

**Arguments:**
- `--file`: Path to Excel workbook (required)
- `--business`: Business unit ID (required, e.g., BU_001)
- `--skip-dedup`: Skip deduplication (optional, for testing)
- `--log-level`: Logging level (optional, DEBUG/INFO/WARNING/ERROR)

### Example

```bash
# Process ClubOS workbook
python main.py --file ./uploads/clubos_week43.xlsx --business BU_001

# Process with debug logging
python main.py --file ./uploads/ezfacility_week43.xlsx --business BU_002 --log-level DEBUG
```

## Project Structure

```
ai_qsr_consolidation/
├── config/
│   ├── field_mapping.csv         # 91-field extraction configuration (updated from 76)
│   └── businesses.csv             # 30 business unit configurations
├── data/
│   ├── test/                      # Test environment
│   │   ├── AI_QSR_Consolidator.xlsx
│   │   ├── archive/
│   │   ├── logs/
│   │   └── extraction_log.csv
│   ├── live/                      # Live/production environment
│   │   ├── AI_QSR_Consolidator.xlsx  # Master consolidated file (99 columns)
│   │   ├── archive/               # Archived workbooks
│   │   ├── logs/                  # Daily ETL logs
│   │   └── extraction_log.csv     # Audit trail
├── analysis/                      # Analysis artifacts
│   ├── analysis_results/          # Normalized data
│   │   ├── kpi_normalized.csv             # 105 KPI instances (long format)
│   │   └── kpi_measurement_quality_analysis.csv  # Quality scores
│   ├── Nov_2/                     # November 2025 analysis
│   │   ├── html_visualizations/   # Interactive Plotly.js charts
│   │   │   ├── viz_dashboard.html                # 6-panel executive dashboard
│   │   │   ├── viz_leaderboard.html             # Total points & project count
│   │   │   ├── viz_portfolio_composition.html    # L1-L5 heatmap
│   │   │   ├── viz_stage_distribution.html       # Stage maturity
│   │   │   ├── viz_kpi_categories.html          # Top 10 KPI categories
│   │   │   ├── viz_kpi_performance.html         # Delta analysis
│   │   │   ├── viz_milestone_funnel.html        # 12-stage funnel
│   │   │   ├── viz_stage_velocity.html          # Days per stage
│   │   │   ├── viz_kpi_by_business.html         # KPI counts by BU
│   │   │   ├── viz_milestone_completion_by_bu.html  # Completion rates
│   │   │   ├── viz_strategic_value_scatter.html  # Score vs value
│   │   │   ├── business_summary.csv             # Supporting data
│   │   │   ├── consolidated_enhanced.csv        # Supporting data
│   │   │   ├── kpi_normalized.csv               # Supporting data
│   │   │   ├── milestone_normalized.csv         # Supporting data
│   │   │   └── analysis_summary.json            # Metadata
│   │   ├── T1_Oct31.md                    # Comprehensive 35+ page analysis report
│   │   └── KPI_Measurement_Approaches_Analysis.md  # Detailed KPI quality analysis
│   └── PIVOT_ANALYSIS_STRATEGY.md         # Analysis strategy document
├── src/
│   ├── extractors/
│   │   ├── file_validator.py     # 7-gate validation
│   │   └── project_extractor.py  # Config-driven extraction
│   ├── transformers/
│   │   ├── data_cleaner.py       # Data normalization
│   │   ├── data_validator.py     # Business rule validation
│   │   └── deduplicator.py       # Hash-based dedup
│   ├── loaders/
│   │   ├── excel_loader.py       # Master file append
│   │   ├── archive_manager.py    # Workbook archival
│   │   └── log_writer.py         # Extraction logging
│   └── utils/
│       ├── config_loader.py      # Config management
│       ├── error_collector.py    # Error aggregation
│       ├── logger.py              # Structured logging
│       └── helpers.py             # Utility functions
├── tests/                         # Test suite (to be implemented)
├── main.py                        # Main ETL orchestrator
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Configuration

### Field Mapping (`config/field_mapping.csv`)

Defines all 91 fields to extract (updated from original 76):
- `output_column_name`: Column name in master file
- `input_row_number`: Row number in Excel sheet
- `input_column_letter`: Column letter (always C for values)
- `data_type`: text, number, or date
- `is_required`: True/False
- `section`: Overview, Resources, KPIs, Maturity, Scoring

### Business Units (`config/businesses.csv`)

Defines 30 business units:
- `business_id`: Unique identifier (BU_001 - BU_030)
- `business_name`: Display name
- `contact_email`: Contact email(s) for email monitoring
- `is_active`: True/False

## ETL Pipeline

The system follows a 4-step pipeline:

### 1. Validation (6 Gates)
- File existence
- Extension check (.xlsx/.xlsm)
- File size limits
- ZIP integrity
- Password protection
- Sheet structure
Note: Merged cells are now allowed (Gate 7 disabled to support business submissions)

### 2. Extraction
- Read P1-P10 project sheets
- Extract 91 fields per sheet using field_mapping.csv
- Handle formulas, dates, and null values
- Collect errors without stopping process

### 3. Transformation
- Clean and normalize data
- Validate business rules
- Detect duplicates (business_id + project_name + week)
- Filter out invalid/duplicate projects

### 4. Loading
- Append to master Excel file
- Archive original workbook
- Write extraction log entry
- Generate UUID and data hash

## Analysis Capabilities

The system includes comprehensive data analysis capabilities for generating insights from consolidated QSR data.

### Analysis Pipeline

**Normalization** → **Visualization** → **Quality Assessment** → **Reporting**

### Available Analysis Tools

#### 1. Data Normalization Scripts
Transform wide-format consolidator data into analysis-ready long format:

- **KPI Normalization**: Converts 3 KPIs × 15 fields (45 columns) to long format
  - Output: `analysis_results/kpi_normalized.csv` (105 rows for 35 projects)
  - Fields: business_name, project_name, kpi_category, measurement_approach, target, actual, delta

- **Milestone Normalization**: Converts 12 milestones × 2 fields (24 columns) to long format
  - Output: `analysis_results/milestone_normalized.csv` (420 rows for 35 projects)
  - Fields: business_name, project_name, milestone_name, target_date, completed_date

#### 2. Interactive Visualizations (Plotly.js)

**Technology**: Plotly.js - JavaScript-based interactive charting library

**11 Pre-Built Visualizations** (see `analysis/Nov_2/html_visualizations/`):

1. **viz_dashboard.html** - 6-panel executive summary dashboard
2. **viz_leaderboard.html** - Total points & project count with average score overlay
3. **viz_portfolio_composition.html** - Heatmap of L1-L5 project distribution by BU
4. **viz_stage_distribution.html** - Stacked bar chart of stage maturity (Idea/Develop/Pilot/Live)
5. **viz_kpi_categories.html** - Top 10 tracked KPI categories
6. **viz_kpi_performance.html** - Delta analysis by category (exceeding/missing targets)
7. **viz_milestone_funnel.html** - 12-stage completion funnel
8. **viz_stage_velocity.html** - Average days per stage by business unit
9. **viz_kpi_by_business.html** - KPI count comparison across BUs
10. **viz_milestone_completion_by_bu.html** - Milestone completion rates
11. **viz_strategic_value_scatter.html** - Project score vs strategic value

**Features**:
- Interactive hover tooltips
- Zoom and pan controls
- Legend filtering
- Consistent color scheme for business unit identification
- Web-ready HTML format (no server required)

#### 3. KPI Quality Scoring System

Automated quality assessment for KPI measurement approaches using regex-based detection:

**Scoring Algorithm** (0-10 points):
- Specific metrics present: +3 points
- Timeframes included: +2 points
- Baselines documented: +2 points
- Targets specified: +1 point
- Detailed description (>15 words): +2 points

**Quality Categories**:
- Excellent: 8-10/10 (✓)
- Good: 6-7/10
- Fair: 4-5/10
- Poor: 2-3/10
- Very Poor: 0-1/10 (⚠️)
- Empty: Not provided

**Output**: `analysis_results/kpi_measurement_quality_analysis.csv`

#### 4. Comprehensive Reports

**T1_Oct31.md** - 35+ page analysis report with:
- Executive summary with snapshot metrics
- 6 strategic insights and 5 critical concerns
- 12 detailed analysis sections
- 7 prioritized recommendations
- 12 leadership questions
- Links to all interactive visualizations

**KPI_Measurement_Approaches_Analysis.md** - Detailed KPI quality analysis with:
- Section 1: Executive Summary (overall quality metrics, findings, BU comparison)
- Section 2: Performance Summary by Category (targets, actuals, deltas for 12 KPI categories)
- Section 3: Detailed Breakdown (full measurement approaches with quality indicators)

### Analysis Artifacts

**File Types Generated**:
- **CSV**: Normalized data, quality scores, business summaries
- **HTML**: Interactive Plotly.js visualizations (11 charts)
- **Markdown**: Comprehensive analysis reports (2 documents)
- **JSON**: Metadata and analysis configuration

**Location**: All analysis artifacts organized in `analysis/` directory:
- `analysis_results/` - Normalized data and quality scores
- `Nov_2/html_visualizations/` - Interactive charts and supporting data
- `Nov_2/` - Markdown reports

### Running Analysis

```bash
# Normalize data
python deep_analysis.py

# Generate visualizations (requires plotly)
pip install plotly kaleido
python create_visualizations.py

# Assess KPI quality
python generate_kpi_analysis.py

# Create reports
python create_measurement_report.py
```

### Key Insights from Recent Analysis (Nov 2025)

- **Performance**: Only 7.6% of KPIs exceed targets (8 of 105)
- **Quality**: Average KPI measurement quality: 4.55/10
- **Bottleneck**: Pilot stage takes 36.5 days (7x longer than other stages)
- **Leadership**: ClubWise leads with 600 points across 6 projects
- **Concern**: EZ_Facility trails with 45% milestone completion rate

## Error Handling

The system uses **error aggregation** pattern:
- Continue processing on sheet-level failures
- Partial success accepted (50% threshold configurable)
- All errors logged with full traceback
- Return status: SUCCESS, PARTIAL, or FAILED

**Example:** If 8 of 10 project sheets extract successfully, the system accepts the 8 projects and logs errors for the 2 failed sheets.

## Deduplication

Hash-based duplicate detection:
- **Hash key:** `business_id + project_name + submission_week`
- **Behavior:** Duplicates are **marked but not skipped** - all submissions load to consolidator with `is_duplicate` flag
- **Implementation:** MD5 hash (can upgrade to xxhash for 10x performance)
- **Rationale:** Preserves all submitted data for audit trail while flagging potential duplicates for review

## Output Format

### Master Consolidator File

Each row contains:
- **Metadata:** extraction_id, business_id, business_name, sheet_name, submission_date, submission_week, workbook_filename, data_hash, is_duplicate
- **Project Data:** 91 fields from field_mapping.csv
- **Total Columns:** 99 (8 metadata + 91 project fields)

### Extraction Log

CSV audit trail with:
- extraction_id
- timestamp
- business_id/business_name
- workbook_filename
- project_count
- error_count
- success_rate
- status (SUCCESS/PARTIAL/FAILED)

### Archive

Workbooks archived with naming: `{business_id}_{date}_{extraction_id}.xlsx`

Example: `BU_001_2025-10-26_a1b2c3d4.xlsx`

## Validation Checklist

### ETL System
✅ Extract all 91 fields from sample workbook
✅ Generate correct output format (99 columns: 8 metadata + 91 project fields)
✅ Identify business unit from config
✅ Append to existing master file without data loss
✅ Detect and mark duplicate submissions (is_duplicate flag)
✅ Handle all error scenarios with proper logging
✅ Archive original files with correct naming
✅ Log all activities with timestamps
✅ Process multiple projects (P1-P10) in single workbook
✅ Handle missing/null values gracefully
✅ Generate extraction_id and data_hash correctly
✅ Parse dates in various formats
✅ Skip non-project sheets (Scorecard, Lookups, etc.)
✅ Validate Excel file format
✅ Create all required directories on first run
✅ Support test/live environment separation

### Analysis System
✅ Normalize 91-field wide data to long format (KPI and milestone)
✅ Generate 11 interactive Plotly.js visualizations
✅ Assess KPI measurement quality with scoring algorithm
✅ Create comprehensive markdown reports with insights
✅ Organize all artifacts in analysis/ directory structure

## Troubleshooting

### "File is locked" error
- Master Excel file is open in Excel
- **Solution:** Close the file and retry

### "Validation failed: merged cells"
- Excel sheet contains merged cells
- **Solution:** Unmerge all cells in project sheets (P1-P10)

### "Required field missing: project_name"
- Project sheet missing required field
- **Solution:** Check field_mapping.csv row numbers match Excel template

### "Workbook contains no sheets"
- Corrupted Excel file
- **Solution:** Try opening file in Excel first, then save

## Future Enhancements (Phase 2)

- [ ] Email monitoring (IMAP integration)
- [ ] SharePoint integration
- [ ] Database backend (PostgreSQL)
- [ ] Web dashboard
- [ ] Automated scheduling
- [ ] Email notifications
- [ ] Data quality reports

## Development

### Running Tests (Not Yet Implemented)

```bash
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## License

Internal use only - Constellation Software Inc.

## Contact

For questions or issues, contact the AI Transformation team.
