# AI QSR Consolidator

Automated ETL system for consolidating AI project tracking data from 30 business units into a single master Excel file.

## Overview

This system extracts 76 fields per project from business unit workbooks, validates and cleans the data, deduplicates submissions, and appends to a master consolidator file with full audit trail.

**Key Features:**
- Config-driven field extraction (76 fields from P1-P10 sheets)
- 7-gate file validation (catches 90% of errors before extraction)
- Error aggregation (partial success - continue on failures)
- Hash-based deduplication (prevents duplicate week submissions)
- Complete audit trail (extraction logs, archived workbooks)
- Week-over-week history (never overwrites existing data)

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
│   ├── field_mapping.csv         # 76-field extraction configuration
│   └── businesses.csv             # 30 business unit configurations
├── data/
│   ├── AI_QSR_Consolidator.xlsx  # Master consolidated file
│   ├── archive/                   # Archived workbooks
│   ├── logs/                      # Daily ETL logs
│   └── extraction_log.csv         # Audit trail
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

Defines all 76 fields to extract:
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

### 1. Validation (7 Gates)
- File existence
- Extension check (.xlsx/.xlsm)
- File size limits
- ZIP integrity
- Password protection
- Sheet structure
- Merged cells detection

### 2. Extraction
- Read P1-P10 project sheets
- Extract 76 fields per sheet using field_mapping.csv
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
- **Behavior:** Same project can be tracked week-over-week, but duplicate submissions within same week are rejected
- **Implementation:** MD5 hash (can upgrade to xxhash for 10x performance)

## Output Format

### Master Consolidator File

Each row contains:
- **Metadata:** extraction_id, business_id, business_name, sheet_name, submission_date, submission_week, workbook_filename, data_hash
- **Project Data:** 76 fields from field_mapping.csv

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

✅ Extract all 76 fields from sample workbook
✅ Generate correct output format matching consolidator template
✅ Identify business unit from config
✅ Append to existing master file without data loss
✅ Detect and skip duplicate submissions
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
