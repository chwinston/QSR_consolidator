# AI QSR Consolidator - Weekly ETL Automation

## FEATURE:

Build a robust Python-based ETL automation system that consolidates AI project tracking data from 30 business units into a single master Excel file, triggered by weekly email submissions or SharePoint uploads.

### Core Functionality:

**Input Processing:**

- Monitor email inbox (or SharePoint folder) for weekly workbook submissions from 30 business units
- Each business submits one Excel workbook per week (format: `AI_QSR_Inputs_vBeta.xlsx`)
- Each workbook contains 1-10 active project sheets (named P1, P2, P3... P10)
- Additional reference sheets exist but should be ignored (Scorecard, Project Data, Lookups, KPI Library, Maturity Ratings)

**Data Extraction:**

- Extract **76 fields per project** from each P1-P10 sheet
- Data layout: Field labels in Column B, values in Column C
- Fields include:
  - **Overview (9 fields):** Project name, UUID, description, category, strategic value level, examples, ratio impacted, AI tools/services
  - **Project Resources (5 fields):** Contact, Product Manager, Analyst, Tech Lead, Executive
  - **KPIs (21 fields):** 3 KPI sets, each with category, name, support description, measurement approach, target, actual, delta
  - **Maturity Stages (36 fields):** 12 milestones across Idea/Develop/Pilot/Live stages, each with target date, completion date, days to target
  - **Scoring (5 fields):** Strategic value, stage multiplier, stage last quarter, project score

**Output Generation:**

- Consolidate all projects into single master Excel file: `AI_QSR_Consolidator.xlsx`
- Each row = one project from one business unit
- Add metadata columns: Submission Date, Submission Week (YYYY-WW), Business Unit Name, Workbook Filename
- Maintain **week-over-week history** - append new data, never overwrite
- Generate unique extraction_id (UUID) per ETL run
- Calculate data_hash for duplicate detection (business_id + project_name + week)

**Business Unit Identification:**

- Identify submitting business from sender email address
- Maintain `businesses.csv` config file with: business_id, business_name, contact_email, is_active
- 30 business units total

**Error Handling & Validation:**

- **File-level validation:**
  - Verify Excel format (xlsx/xlsm)
  - Check for corruption or password protection
  - Validate sheet structure (P1-P10 format)
  - Confirm sheet count (1-10 range)
- **Data-level validation:**
  - Verify 76 fields present per sheet
  - Type checking (dates, numbers, text)
  - Required field validation
  - Handle empty/null values gracefully
- **Duplicate detection:**
  - Check for duplicate submissions (same business + week)
  - Skip duplicates based on data_hash comparison
- **Error notifications:**
  - Send detailed email alerts on extraction failures
  - Include: extraction_id, business_id, error messages, full traceback
  - Separate notifications for success (with project count)
  - Log all errors to `extraction_log.csv` with timestamps

**Archival:**

- Archive original submitted workbooks with naming: `{business_id}_{submission_date}_{extraction_id}.xlsx`
- Maintain archive/ directory structure

### Technical Requirements:

- **Language:** Python 3.10+
- **Core Libraries:** pandas, openpyxl, python-dotenv
- **Email Handling:** imaplib or O365 for email monitoring
- **Scheduling:** Can be triggered manually initially, then scheduled (cron/Task Scheduler)

### Expected Usage Pattern:

```bash
# Manual trigger for single workbook
python main.py --file path/to/workbook.xlsx --business "BU_001"

# Email monitoring mode
python main.py --mode email --monitor

# Process specific business
python main.py --business "BU_001" --source sharepoint
```

### Success Criteria:

1. Successfully extract all 76 fields from each P1-P10 sheet
2. Correctly identify business unit from email sender
3. Append data to master consolidator without duplicates
4. Generate comprehensive error reports with actionable details
5. Archive original workbooks with proper naming
6. Maintain extraction logs with full audit trail
7. Handle missing/malformed data gracefully without stopping entire process
8. Support both email and SharePoint triggers
9. Process all 30 business units reliably

## EXAMPLES:

Sample files are provided in the project root:

- **`AI_QSR_Inputs_vBeta.xlsx`** - Template input workbook showing sheet structure (P1-P10)
  - Each P# sheet represents one project
  - Field labels in Column B (rows 1-48)
  - Field values in Column C
  - Reference sheets to ignore: Scorecard, Project Data, Lookups, KPI Library, Maturity Ratings
- **`AI_QSR_Consolidator__beta_.xlsx`** - Expected output format
  - Single sheet with 76 columns
  - Row 2 contains headers matching output field names
  - Each subsequent row = one extracted project

**Key Patterns to Follow:**

1. **Field Extraction Pattern:**

   - Use openpyxl to read specific cell locations (Column B for labels, Column C for values)
   - Map extracted values to output column headers exactly as shown in consolidator
   - Handle formulas in cells (some cells contain `=` expressions)

2. **Sheet Detection:**

   - Iterate through sheet names
   - Only process sheets matching pattern: `P1`, `P2`, `P3`, etc. (P + digit)
   - Skip all other sheets (Scorecard, Lookups, etc.)

3. **Error Recovery:**

   - If one project sheet fails, continue processing other sheets
   - Collect all errors and report at end
   - Partial success is acceptable (e.g., 8 of 10 projects extracted)

4. **Data Type Handling:**
   - Dates: Parse flexibly (Excel serial numbers, ISO strings, etc.)
   - Numbers: Handle empty cells, text in numeric fields
   - Text: Strip whitespace, handle None/NaN
   - Booleans: Standardize to True/False

## DOCUMENTATION:

- **Pandas:** https://pandas.pydata.org/docs/
- **Openpyxl:** https://openpyxl.readthedocs.io/
- **Python IMAP:** https://docs.python.org/3/library/imaplib.html
- **Python dotenv:** https://pypi.org/project/python-dotenv/

## OTHER CONSIDERATIONS:

### Critical Implementation Details:

1. **Field Mapping Configuration:**

   - Create `field_mapping.csv` with columns: `output_column_name`, `input_row_number`, `input_column_letter`, `data_type`, `is_required`
   - This makes the system maintainable if field locations change
   - Example row: `"Project", 3, "C", "text", True`

2. **Business Unit Config:**

   - Create `businesses.csv` with columns: `business_id`, `business_name`, `contact_email`, `is_active`
   - Use this for email sender → business_id lookup
   - Support multiple emails per business (comma-separated)

3. **Email Gotchas:**

   - Handle attachment encoding issues (base64, MIME types)
   - Check for inline vs attached files
   - Some businesses may send zipped files
   - Email subject line format: Parse for week identifier if present

4. **Excel Gotchas:**

   - Some cells contain formulas that need evaluation
   - Merged cells should be detected and rejected
   - Hidden rows/columns should be ignored
   - Data validation lists may cause read errors - handle gracefully

5. **Performance Considerations:**

   - Each workbook takes ~2-5 seconds to process
   - 30 businesses × 10 projects = 300 rows per week maximum
   - Keep master file size under 10MB for Excel compatibility
   - Consider database migration when master file exceeds 50,000 rows

6. **Duplicate Detection Strategy:**

   - Hash key: `business_id + sheet_name + submission_week`
   - This allows same project to be tracked week-over-week as separate entries
   - Edge case: Business resubmits same week → detect and skip with notification

7. **Missing Data Handling:**

   - Required fields (project name, business unit): FAIL extraction if missing
   - Optional fields (KPI actuals, maturity dates): Set to None/NaN
   - Log all missing required fields in error report

8. **Testing Strategy:**

   - Create `tests/` directory with sample workbooks
   - Include edge cases: empty sheets, wrong format, missing fields, corrupted data
   - Unit tests for each major function (extraction, validation, loading)
   - Integration test: Full ETL run with 3 sample businesses

9. **Logging Requirements:**

   - Log to both file (`logs/etl_YYYYMMDD.log`) and console
   - Include: timestamp, extraction_id, business_id, action, status
   - Rotate logs daily, keep 30 days
   - Log levels: DEBUG for field extraction, INFO for progress, ERROR for failures

10. **Notification Email Template:**

    ```
    Subject: [SUCCESS/ERROR] AI QSR ETL - {business_name} - {date}

    Extraction ID: {uuid}
    Business: {business_name} ({business_id})
    Timestamp: {datetime}
    Workbook: {filename}

    Results:
    - Projects Extracted: {count}
    - Errors: {error_count}

    [If errors:]
    Error Details:
    1. Sheet: {sheet_name}
       Error: {message}
       Traceback: {traceback}
    ```

11. **Directory Structure:**

    ```
    ai_qsr_etl/
    ├── config/
    │   ├── businesses.csv
    │   ├── field_mapping.csv
    │   └── email_config.yaml
    ├── data/
    │   ├── AI_QSR_Consolidator.xlsx
    │   ├── archive/
    │   └── logs/
    ├── src/
    │   ├── extractors/
    │   │   ├── __init__.py
    │   │   ├── email_handler.py
    │   │   ├── file_validator.py
    │   │   └── project_extractor.py
    │   ├── transformers/
    │   │   ├── __init__.py
    │   │   ├── data_cleaner.py
    │   │   └── deduplicator.py
    │   ├── loaders/
    │   │   ├── __init__.py
    │   │   └── excel_loader.py
    │   └── utils/
    │       ├── __init__.py
    │       ├── logger.py
    │       ├── notifier.py
    │       └── helpers.py
    ├── tests/
    │   ├── test_extractor.py
    │   ├── test_validator.py
    │   └── fixtures/
    ├── main.py
    ├── requirements.txt
    ├── .env.example
    └── README.md
    ```

12. **Phase 1 vs Phase 2:**

    - **Phase 1 (MVP):** Excel output, manual file input, basic error reporting
    - **Phase 2 (Production):** Email monitoring, database output, scheduled runs, advanced analytics

13. **Common AI Assistant Mistakes to Avoid:**

    - Don't hardcode field positions - use field_mapping.csv
    - Don't stop entire ETL run on one sheet failure - collect errors and continue
    - Don't overwrite historical data - always append
    - Don't skip duplicate detection - critical for data integrity
    - Don't ignore data types - enforce validation
    - Don't use openpyxl for reading tabular data - use pandas with openpyxl engine for better performance
    - Don't forget to close workbook file handles - can cause locked files

14. **Environment Variables (.env):**

    ```
    # Email Configuration
    IMAP_SERVER=imap.gmail.com
    IMAP_PORT=993
    EMAIL_ADDRESS=etl@company.com
    EMAIL_PASSWORD=app_password_here

    # Paths
    MASTER_FILE_PATH=./data/AI_QSR_Consolidator.xlsx
    ARCHIVE_PATH=./data/archive
    LOG_PATH=./data/logs

    # Notifications
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    NOTIFICATION_EMAIL=data-team@company.com

    # Settings
    MAX_PROJECTS_PER_WORKBOOK=10
    EXPECTED_FIELD_COUNT=76
    ```

## VALIDATION CHECKLIST:

Before considering the ETL complete, verify:

- [ ] Extract all 76 fields from sample workbook
- [ ] Generate correct output format matching consolidator template
- [ ] Identify business unit from email correctly
- [ ] Append to existing master file without data loss
- [ ] Detect and skip duplicate submissions
- [ ] Handle all error scenarios with proper notifications
- [ ] Archive original files with correct naming
- [ ] Log all activities with timestamps
- [ ] Process multiple projects (P1-P10) in single workbook
- [ ] Handle missing/null values gracefully
- [ ] Generate extraction_id and data_hash correctly
- [ ] Parse dates in various formats
- [ ] Skip non-project sheets (Scorecard, Lookups, etc.)
- [ ] Validate email attachment is Excel file
- [ ] Create all required directories on first run

## FUTURE ENHANCEMENTS (Not in Scope for Initial PRP):

- Database backend (PostgreSQL/SQL Server) instead of Excel
- Web dashboard for viewing consolidated data
- Automated data quality reports
- Anomaly detection (e.g., projects not updating for 3+ weeks)
- Integration with project management tools (Jira, Monday.com)
- Real-time SharePoint synchronization
- Multi-user concurrent processing
- Advanced analytics and trend visualization
