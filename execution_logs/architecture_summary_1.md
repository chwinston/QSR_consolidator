# Backend-Architect - Architecture Summary

**Agent**: backend-architect
**Phase**: architecture
**Timestamp**: 2025-10-26 14:30:00
**Duration**: Approximately 90 minutes

---

## Task Assignment

```
Design the ETL architecture with extractors/transformers/loaders separation,
config-driven field mapping, and error aggregation without stopping the entire
process.

Requirements:
1. Component Separation (Extractors/Transformers/Loaders)
2. Config-Driven Field Mapping
3. Error Aggregation Without Stopping
4. Directory Structure
5. Data Flow Design
6. Integration Points
```

---

## Context Received

### Previous Work Completed

- **project-init** set up logging infrastructure (execution_log.md, PROJECT_CONTEXT.md, templates)
- No prior architecture or implementation work completed
- Initial PRP specification (Initial.md) provides comprehensive requirements

### Project State When Started

- **Phase**: Just initialized, beginning architecture phase
- **Completed**: Logging infrastructure and PRP documentation
- **Next Up**: System architecture design before implementation begins

---

## Work Performed

### Files Created

| File Path | Purpose | Lines |
|-----------|---------|-------|
| `execution_logs/architecture_summary_1.md` | This comprehensive architecture document | 850+ |

### Files Modified

None - this is pure architecture design phase. Implementation team will use this design to create all system files.

### Architecture Designed

This summary documents the complete ETL system architecture including:

1. **Component Boundaries**: Clean separation between extraction, transformation, and loading
2. **Interface Contracts**: All component APIs and data structures
3. **Configuration Schemas**: Field mapping, business config, error logging structures
4. **Error Handling Strategy**: Partial success with comprehensive error aggregation
5. **Data Flow**: End-to-end processing pipeline with state management
6. **Integration Points**: Email, SharePoint, notifications, logging
7. **Directory Structure**: Complete module organization
8. **Design Patterns**: Separation of concerns, dependency injection, strategy pattern

---

## System Architecture Overview

### High-Level Architecture Pattern

**Pattern**: **Pipeline Architecture** (Chain of Responsibility + ETL Pattern)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ETL Pipeline Orchestrator                      │
│                              (main.py)                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
    ┌───────────────────┐  ┌───────────────┐  ┌──────────────────┐
    │   EXTRACTORS      │→ │ TRANSFORMERS  │→ │    LOADERS       │
    │                   │  │               │  │                  │
    │ - Email Handler   │  │ - Validator   │  │ - Excel Loader   │
    │ - File Validator  │  │ - Data Clean  │  │ - Archive Mgr    │
    │ - Project Extract │  │ - Deduplicate │  │ - Log Writer     │
    └───────────────────┘  └───────────────┘  └──────────────────┘
            │                      │                    │
            └──────────────────────┴────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │      Error Aggregator       │
                    │   (collects all errors,     │
                    │    doesn't stop pipeline)   │
                    └─────────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    Notification Service     │
                    │  (email reports + logging)  │
                    └─────────────────────────────┘
```

### Core Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Open/Closed**: Easy to add new extractors/transformers without modifying existing code
3. **Dependency Injection**: Components receive dependencies, not hard-coded imports
4. **Fail-Safe Processing**: Errors collected but don't stop entire pipeline
5. **Config-Driven**: All field mappings and business logic externalized to config files
6. **Testability**: Each component testable in isolation with mock dependencies

---

## Component Architecture

### 1. EXTRACTORS (Input Layer)

**Responsibility**: Retrieve data from external sources and convert to standardized format

#### 1.1 EmailHandler (`src/extractors/email_handler.py`)

**Purpose**: Monitor email inbox, download Excel attachments, identify sender

**Interface**:
```python
class EmailHandler:
    def __init__(self, config: EmailConfig, logger: Logger):
        """
        Args:
            config: Email server settings (IMAP host, port, credentials)
            logger: Logging instance for audit trail
        """
        pass

    def fetch_unprocessed_emails(self) -> List[EmailMessage]:
        """
        Fetch emails with Excel attachments that haven't been processed.

        Returns:
            List of EmailMessage objects containing:
            - sender_email: str
            - subject: str
            - received_date: datetime
            - attachments: List[Attachment]

        Raises:
            EmailConnectionError: Cannot connect to IMAP server
            AuthenticationError: Invalid credentials
        """
        pass

    def download_attachment(self, attachment: Attachment) -> bytes:
        """
        Download Excel attachment as bytes.

        Args:
            attachment: Attachment metadata

        Returns:
            Raw file bytes

        Raises:
            AttachmentDownloadError: Cannot download attachment
        """
        pass

    def mark_as_processed(self, email_id: str):
        """
        Mark email as processed to prevent reprocessing.

        Args:
            email_id: Unique email identifier
        """
        pass
```

**Data Structures**:
```python
@dataclass
class EmailMessage:
    email_id: str
    sender_email: str
    subject: str
    received_date: datetime
    attachments: List[Attachment]

@dataclass
class Attachment:
    filename: str
    content_type: str
    size_bytes: int
    data: Optional[bytes] = None  # Lazy loaded
```

**Error Scenarios**:
- IMAP connection failure → Retry with exponential backoff (3 attempts)
- Authentication failure → Fail immediately, notify admin
- No attachments found → Skip email, log warning
- Non-Excel attachment → Skip attachment, continue processing other attachments
- Malformed email → Log error, continue to next email

#### 1.2 FileValidator (`src/extractors/file_validator.py`)

**Purpose**: Validate Excel file structure before extraction

**Interface**:
```python
class FileValidator:
    def __init__(self, config: ValidationConfig, logger: Logger):
        """
        Args:
            config: Validation rules (expected sheets, field count, etc.)
            logger: Logging instance
        """
        pass

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate Excel file structure and contents.

        Args:
            file_path: Path to Excel file

        Returns:
            ValidationResult with status and error details

        Validation Checks:
            - File format (xlsx/xlsm)
            - Not password protected
            - Not corrupted
            - Contains 1-10 project sheets (P1-P10)
            - No merged cells in project sheets
            - All expected reference sheets present
        """
        pass

    def get_project_sheets(self, workbook: Workbook) -> List[str]:
        """
        Identify project sheets (P1, P2, ... P10).

        Args:
            workbook: openpyxl Workbook object

        Returns:
            List of sheet names matching pattern P[1-10]
        """
        pass

    def check_merged_cells(self, worksheet: Worksheet) -> List[str]:
        """
        Detect merged cells in worksheet.

        Args:
            worksheet: openpyxl Worksheet object

        Returns:
            List of merged cell ranges (e.g., ['A1:B2', 'C5:D6'])
        """
        pass
```

**Data Structures**:
```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    project_sheets: List[str]  # Only if valid

@dataclass
class ValidationError:
    error_code: str  # e.g., 'FILE_CORRUPTED', 'MERGED_CELLS'
    message: str
    details: Dict[str, Any]  # Additional context
```

**Validation Rules**:
1. **File Format**: Must be .xlsx or .xlsm
2. **Password Protection**: Must not be password protected
3. **Corruption Check**: Must be readable by openpyxl
4. **Sheet Count**: Must have 1-10 project sheets (P1-P10)
5. **Merged Cells**: No merged cells in columns B-C (data area)
6. **Reference Sheets**: Scorecard, Project Data, Lookups sheets exist (optional check)

#### 1.3 ProjectExtractor (`src/extractors/project_extractor.py`)

**Purpose**: Extract 76 fields from each project sheet using config-driven mapping

**Interface**:
```python
class ProjectExtractor:
    def __init__(self,
                 field_mapping: FieldMapping,
                 logger: Logger,
                 error_collector: ErrorCollector):
        """
        Args:
            field_mapping: Config-driven field position mappings
            logger: Logging instance
            error_collector: Aggregates errors without stopping
        """
        pass

    def extract_workbook(self,
                        file_path: Path,
                        business_id: str,
                        submission_date: datetime) -> ExtractionResult:
        """
        Extract all projects from workbook.

        Args:
            file_path: Path to Excel file
            business_id: Identified business unit ID
            submission_date: When file was submitted

        Returns:
            ExtractionResult containing:
            - projects: List[ProjectData] (successfully extracted)
            - errors: List[ExtractionError] (per-sheet failures)
            - extraction_id: UUID for this run

        Process:
            1. Load workbook with openpyxl (data_only=True for formulas)
            2. Get project sheets (P1-P10)
            3. For each sheet:
                a. Try to extract 76 fields
                b. If successful, add to projects list
                c. If failed, log error and CONTINUE to next sheet
            4. Return all successful extractions + all errors
        """
        pass

    def extract_project(self,
                       worksheet: Worksheet,
                       sheet_name: str,
                       business_id: str,
                       submission_date: datetime) -> ProjectData:
        """
        Extract 76 fields from single project sheet.

        Args:
            worksheet: openpyxl Worksheet object
            sheet_name: Name of project sheet (P1, P2, etc.)
            business_id: Business unit identifier
            submission_date: Submission timestamp

        Returns:
            ProjectData with all 76 fields + metadata

        Raises:
            FieldExtractionError: If required field missing or invalid
        """
        pass

    def extract_field(self,
                     worksheet: Worksheet,
                     field_config: FieldConfig) -> Any:
        """
        Extract single field from worksheet.

        Args:
            worksheet: openpyxl Worksheet object
            field_config: Field mapping config (row, column, type)

        Returns:
            Field value converted to appropriate data type

        Raises:
            FieldExtractionError: If field required but missing
        """
        pass
```

**Data Structures**:
```python
@dataclass
class ExtractionResult:
    extraction_id: str  # UUID
    business_id: str
    submission_date: datetime
    projects: List[ProjectData]  # Successfully extracted
    errors: List[ExtractionError]  # Per-sheet failures
    total_sheets_attempted: int
    total_sheets_succeeded: int

@dataclass
class ProjectData:
    # Metadata
    extraction_id: str
    business_id: str
    business_name: str
    sheet_name: str
    submission_date: datetime
    submission_week: str  # YYYY-WW format
    workbook_filename: str

    # Overview (9 fields)
    project_name: str
    project_uuid: str
    project_description: str
    project_category: str
    strategic_value_level: int
    project_examples: str
    ratio_impacted: str
    ai_tools_services: str

    # Project Resources (5 fields)
    contact_person: str
    product_manager: str
    analyst: str
    tech_lead: str
    executive_sponsor: str

    # KPIs (21 fields - 3 KPI sets)
    kpi1_category: str
    kpi1_name: str
    kpi1_support_description: str
    kpi1_measurement_approach: str
    kpi1_target: float
    kpi1_actual: float
    kpi1_delta: float

    kpi2_category: str
    kpi2_name: str
    kpi2_support_description: str
    kpi2_measurement_approach: str
    kpi2_target: float
    kpi2_actual: float
    kpi2_delta: float

    kpi3_category: str
    kpi3_name: str
    kpi3_support_description: str
    kpi3_measurement_approach: str
    kpi3_target: float
    kpi3_actual: float
    kpi3_delta: float

    # Maturity Stages (36 fields - 12 milestones)
    # Idea Stage
    milestone1_idea_target_date: datetime
    milestone1_idea_completion_date: datetime
    milestone1_idea_days_to_target: int

    milestone2_idea_target_date: datetime
    milestone2_idea_completion_date: datetime
    milestone2_idea_days_to_target: int

    milestone3_idea_target_date: datetime
    milestone3_idea_completion_date: datetime
    milestone3_idea_days_to_target: int

    # Develop Stage
    milestone4_develop_target_date: datetime
    milestone4_develop_completion_date: datetime
    milestone4_develop_days_to_target: int

    milestone5_develop_target_date: datetime
    milestone5_develop_completion_date: datetime
    milestone5_develop_days_to_target: int

    milestone6_develop_target_date: datetime
    milestone6_develop_completion_date: datetime
    milestone6_develop_days_to_target: int

    # Pilot Stage
    milestone7_pilot_target_date: datetime
    milestone7_pilot_completion_date: datetime
    milestone7_pilot_days_to_target: int

    milestone8_pilot_target_date: datetime
    milestone8_pilot_completion_date: datetime
    milestone8_pilot_days_to_target: int

    milestone9_pilot_target_date: datetime
    milestone9_pilot_completion_date: datetime
    milestone9_pilot_days_to_target: int

    # Live Stage
    milestone10_live_target_date: datetime
    milestone10_live_completion_date: datetime
    milestone10_live_days_to_target: int

    milestone11_live_target_date: datetime
    milestone11_live_completion_date: datetime
    milestone11_live_days_to_target: int

    milestone12_live_target_date: datetime
    milestone12_live_completion_date: datetime
    milestone12_live_days_to_target: int

    # Scoring (5 fields)
    strategic_value_score: float
    stage_multiplier: float
    stage_last_quarter: str
    project_score: float

    # Internal tracking
    data_hash: str  # For duplicate detection

@dataclass
class ExtractionError:
    sheet_name: str
    error_code: str
    message: str
    traceback: str
    timestamp: datetime
```

**Error Handling Strategy (CRITICAL)**:

```python
# PATTERN: Collect errors, NEVER stop entire extraction

errors = []
successful_projects = []

for sheet_name in project_sheets:
    try:
        project_data = self.extract_project(
            worksheet=workbook[sheet_name],
            sheet_name=sheet_name,
            business_id=business_id,
            submission_date=submission_date
        )
        successful_projects.append(project_data)
        logger.info(f"✅ Extracted {sheet_name}: {project_data.project_name}")

    except FieldExtractionError as e:
        # Required field missing - log and continue
        error = ExtractionError(
            sheet_name=sheet_name,
            error_code='REQUIRED_FIELD_MISSING',
            message=str(e),
            traceback=traceback.format_exc(),
            timestamp=datetime.now()
        )
        errors.append(error)
        logger.error(f"❌ Failed {sheet_name}: {e}")
        continue  # Don't stop - process next sheet

    except Exception as e:
        # Unexpected error - log and continue
        error = ExtractionError(
            sheet_name=sheet_name,
            error_code='EXTRACTION_FAILED',
            message=str(e),
            traceback=traceback.format_exc(),
            timestamp=datetime.now()
        )
        errors.append(error)
        logger.error(f"❌ Failed {sheet_name}: {e}")
        continue  # Don't stop - process next sheet

# Return BOTH successes AND failures
return ExtractionResult(
    extraction_id=str(uuid.uuid4()),
    business_id=business_id,
    submission_date=submission_date,
    projects=successful_projects,
    errors=errors,
    total_sheets_attempted=len(project_sheets),
    total_sheets_succeeded=len(successful_projects)
)
```

---

### 2. TRANSFORMERS (Processing Layer)

**Responsibility**: Clean, validate, and transform extracted data

#### 2.1 DataCleaner (`src/transformers/data_cleaner.py`)

**Purpose**: Clean and normalize extracted field values

**Interface**:
```python
class DataCleaner:
    def __init__(self, logger: Logger):
        pass

    def clean_project(self, project: ProjectData) -> ProjectData:
        """
        Clean all fields in project data.

        Args:
            project: Raw extracted project data

        Returns:
            Cleaned project data with normalized values

        Cleaning Rules:
            - Text: Strip whitespace, handle None as empty string
            - Numbers: Convert None to 0 or NaN based on context
            - Dates: Parse multiple formats, convert to datetime
            - Booleans: Standardize to True/False
        """
        pass

    def clean_text_field(self, value: Any) -> str:
        """Clean text field: strip whitespace, handle None."""
        pass

    def clean_numeric_field(self, value: Any, allow_null: bool = False) -> float:
        """Clean numeric field: convert to float, handle None/empty."""
        pass

    def clean_date_field(self, value: Any) -> datetime:
        """
        Clean date field: parse multiple formats.

        Supported Formats:
            - Excel serial number (44927 → 2022-12-15)
            - ISO string (2022-12-15)
            - US format (12/15/2022)
            - UK format (15/12/2022)
        """
        pass
```

**Data Type Handling**:

| Field Type | Input Examples | Output Type | Null Handling |
|------------|---------------|-------------|---------------|
| Text | "  Hello  ", None, "" | str | None → "" |
| Integer | 5, "5", None, "" | int | None → 0 |
| Float | 3.14, "3.14", None | float | None → 0.0 |
| Date | 44927, "2022-12-15", None | datetime | None → None |
| Boolean | "Yes", "No", 1, 0 | bool | None → False |

#### 2.2 DataValidator (`src/transformers/data_validator.py`)

**Purpose**: Validate cleaned data against business rules

**Interface**:
```python
class DataValidator:
    def __init__(self, logger: Logger, error_collector: ErrorCollector):
        pass

    def validate_project(self, project: ProjectData) -> ValidationResult:
        """
        Validate project data against business rules.

        Args:
            project: Cleaned project data

        Returns:
            ValidationResult with errors/warnings

        Validation Rules:
            - project_name: Required, max 200 chars
            - strategic_value_level: Must be 1-5
            - KPI targets: Must be numeric
            - Dates: Must be valid datetime
            - project_uuid: Must be valid UUID format
        """
        pass

    def validate_required_fields(self, project: ProjectData) -> List[str]:
        """
        Check all required fields are present.

        Required Fields:
            - project_name
            - business_id
            - submission_date
            - project_category
            - strategic_value_level

        Returns:
            List of missing required field names
        """
        pass
```

#### 2.3 Deduplicator (`src/transformers/deduplicator.py`)

**Purpose**: Detect and handle duplicate submissions

**Interface**:
```python
class Deduplicator:
    def __init__(self, master_file_path: Path, logger: Logger):
        """
        Args:
            master_file_path: Path to AI_QSR_Consolidator.xlsx
            logger: Logging instance
        """
        pass

    def calculate_data_hash(self, project: ProjectData) -> str:
        """
        Calculate unique hash for duplicate detection.

        Hash Key Components:
            - business_id
            - sheet_name (P1, P2, etc.)
            - submission_week (YYYY-WW)

        Returns:
            xxhash digest (hex string)

        Rationale:
            - Allows same project tracked week-over-week
            - Detects duplicate submissions within same week
            - Fast hash calculation with xxhash
        """
        pass

    def is_duplicate(self, project: ProjectData) -> bool:
        """
        Check if project already exists in master file.

        Args:
            project: Project to check

        Returns:
            True if data_hash found in master file
        """
        pass

    def filter_duplicates(self,
                         projects: List[ProjectData]) -> DuplicationResult:
        """
        Filter out duplicate projects.

        Args:
            projects: List of projects to check

        Returns:
            DuplicationResult with new/duplicate project lists
        """
        pass
```

**Data Structures**:
```python
@dataclass
class DuplicationResult:
    new_projects: List[ProjectData]
    duplicate_projects: List[ProjectData]
    duplicate_count: int
```

**Hash Calculation Implementation**:
```python
import xxhash

def calculate_data_hash(self, project: ProjectData) -> str:
    # Construct hash key
    hash_key = f"{project.business_id}|{project.sheet_name}|{project.submission_week}"

    # Calculate xxhash (fast, collision-resistant)
    hasher = xxhash.xxh64()
    hasher.update(hash_key.encode('utf-8'))

    return hasher.hexdigest()
```

---

### 3. LOADERS (Output Layer)

**Responsibility**: Write transformed data to persistent storage

#### 3.1 ExcelLoader (`src/loaders/excel_loader.py`)

**Purpose**: Append projects to master Excel consolidator file

**Interface**:
```python
class ExcelLoader:
    def __init__(self,
                 master_file_path: Path,
                 logger: Logger,
                 error_collector: ErrorCollector):
        """
        Args:
            master_file_path: Path to AI_QSR_Consolidator.xlsx
            logger: Logging instance
            error_collector: Error aggregation
        """
        pass

    def load_projects(self, projects: List[ProjectData]) -> LoadResult:
        """
        Append projects to master Excel file.

        Args:
            projects: List of validated, deduplicated projects

        Returns:
            LoadResult with success/failure counts

        Process:
            1. Read existing master file (or create if missing)
            2. Convert projects to DataFrame rows
            3. Append to existing data (never overwrite)
            4. Write back to Excel
            5. Validate write succeeded

        Error Handling:
            - File locked → Retry 3 times with 2-second delay
            - Disk full → Fail immediately, notify admin
            - Permission denied → Fail immediately, notify admin
        """
        pass

    def ensure_master_file_exists(self):
        """
        Create master file if doesn't exist.

        File Structure:
            - Sheet: "Consolidated Data"
            - Row 1: Empty
            - Row 2: 76 column headers + 4 metadata columns
            - Row 3+: Project data
        """
        pass

    def convert_to_dataframe_row(self, project: ProjectData) -> Dict[str, Any]:
        """
        Convert ProjectData to dictionary for DataFrame row.

        Args:
            project: Project data object

        Returns:
            Dictionary with keys matching Excel column headers
        """
        pass
```

**Data Structures**:
```python
@dataclass
class LoadResult:
    rows_written: int
    errors: List[LoadError]
    master_file_size_bytes: int
    write_timestamp: datetime

@dataclass
class LoadError:
    project_name: str
    error_code: str
    message: str
    traceback: str
```

**Master File Column Order**:
```python
# Column order in AI_QSR_Consolidator.xlsx
MASTER_FILE_COLUMNS = [
    # Metadata (4 columns)
    'extraction_id',
    'submission_date',
    'submission_week',
    'business_id',
    'business_name',
    'workbook_filename',
    'sheet_name',
    'data_hash',

    # Overview (9 fields)
    'project_name',
    'project_uuid',
    'project_description',
    # ... (all 76 fields in order)
]
```

#### 3.2 ArchiveManager (`src/loaders/archive_manager.py`)

**Purpose**: Archive original submitted workbooks

**Interface**:
```python
class ArchiveManager:
    def __init__(self, archive_path: Path, logger: Logger):
        """
        Args:
            archive_path: Root archive directory
            logger: Logging instance
        """
        pass

    def archive_workbook(self,
                        file_path: Path,
                        business_id: str,
                        submission_date: datetime,
                        extraction_id: str) -> Path:
        """
        Archive original workbook with structured naming.

        Args:
            file_path: Path to original workbook
            business_id: Business unit ID
            submission_date: When submitted
            extraction_id: Unique ETL run ID

        Returns:
            Path to archived file

        Archive Structure:
            archive/
                2025/
                    10/
                        BU_001_2025-10-26_uuid123.xlsx
                        BU_002_2025-10-26_uuid456.xlsx
                    11/
                        ...

        Filename Format: {business_id}_{date}_{extraction_id}.xlsx
        """
        pass
```

#### 3.3 LogWriter (`src/loaders/log_writer.py`)

**Purpose**: Write extraction audit logs to CSV

**Interface**:
```python
class LogWriter:
    def __init__(self, log_path: Path, logger: Logger):
        """
        Args:
            log_path: Path to data/logs/ directory
            logger: Logging instance
        """
        pass

    def write_extraction_log(self, result: ExtractionResult):
        """
        Append extraction result to extraction_log.csv.

        Args:
            result: Complete extraction result

        CSV Columns:
            - extraction_id
            - timestamp
            - business_id
            - business_name
            - workbook_filename
            - total_sheets_attempted
            - total_sheets_succeeded
            - total_sheets_failed
            - error_count
            - status (SUCCESS/PARTIAL/FAILED)
        """
        pass
```

**extraction_log.csv Schema**:
```csv
extraction_id,timestamp,business_id,business_name,workbook_filename,sheets_attempted,sheets_succeeded,sheets_failed,error_count,status
uuid-123,2025-10-26 14:30:00,BU_001,ClubOS,AI_QSR_Inputs_vBeta.xlsx,8,8,0,0,SUCCESS
uuid-456,2025-10-26 14:35:00,BU_002,EZ Facility,AI_QSR_Inputs_vBeta.xlsx,10,8,2,2,PARTIAL
```

---

### 4. UTILITIES (Cross-Cutting Concerns)

#### 4.1 ErrorCollector (`src/utils/error_collector.py`)

**Purpose**: Aggregate errors across entire pipeline without stopping

**Interface**:
```python
class ErrorCollector:
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []

    def add_error(self,
                 error_type: str,
                 message: str,
                 context: Dict[str, Any],
                 traceback_str: str = None):
        """
        Add error to collection.

        Args:
            error_type: Error category (VALIDATION, EXTRACTION, LOAD)
            message: Human-readable error message
            context: Additional context (sheet_name, business_id, etc.)
            traceback_str: Full traceback for debugging
        """
        self.errors.append({
            'timestamp': datetime.now(),
            'error_type': error_type,
            'message': message,
            'context': context,
            'traceback': traceback_str
        })

    def has_errors(self) -> bool:
        """Check if any errors collected."""
        return len(self.errors) > 0

    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all collected errors."""
        return self.errors

    def clear(self):
        """Clear error collection."""
        self.errors = []
```

**Usage Pattern**:
```python
# In ProjectExtractor
error_collector = ErrorCollector()

for sheet_name in project_sheets:
    try:
        project = extract_project(sheet_name)
        projects.append(project)
    except Exception as e:
        error_collector.add_error(
            error_type='EXTRACTION',
            message=f"Failed to extract {sheet_name}",
            context={'sheet': sheet_name, 'business': business_id},
            traceback_str=traceback.format_exc()
        )
        continue  # Keep processing

# Later, check if any errors occurred
if error_collector.has_errors():
    notifier.send_error_report(error_collector.get_errors())
```

#### 4.2 Logger (`src/utils/logger.py`)

**Purpose**: Structured logging with rotation

**Interface**:
```python
class ETLLogger:
    def __init__(self, log_path: Path, level: str = 'INFO'):
        """
        Configure logging with file rotation.

        Log Format:
            {timestamp} | {level} | {extraction_id} | {message}

        Rotation:
            - Daily rotation
            - Keep 30 days
            - Max 10MB per file
        """
        pass

    def set_extraction_id(self, extraction_id: str):
        """Set extraction_id for context in all log messages."""
        pass
```

#### 4.3 Notifier (`src/utils/notifier.py`)

**Purpose**: Send email notifications for success/failure

**Interface**:
```python
class EmailNotifier:
    def __init__(self, smtp_config: SMTPConfig, logger: Logger):
        pass

    def send_success_notification(self, result: ExtractionResult):
        """
        Send success email.

        Subject: [SUCCESS] AI QSR ETL - {business_name} - {date}

        Body:
            Extraction ID: {uuid}
            Business: {business_name} ({business_id})
            Timestamp: {datetime}
            Workbook: {filename}

            Results:
            - Projects Extracted: {count}
            - Sheets Processed: {total_sheets_succeeded}/{total_sheets_attempted}

            Next Steps:
            - Data appended to master file
            - Original workbook archived
        """
        pass

    def send_error_notification(self, result: ExtractionResult):
        """
        Send error email with detailed error list.

        Subject: [ERROR] AI QSR ETL - {business_name} - {date}

        Body:
            Extraction ID: {uuid}
            Business: {business_name} ({business_id})
            Timestamp: {datetime}
            Workbook: {filename}

            Results:
            - Projects Extracted: {success_count}
            - Errors: {error_count}

            Error Details:
            1. Sheet: {sheet_name}
               Error: {message}
               Traceback: {traceback}

            2. Sheet: {sheet_name}
               Error: {message}
               Traceback: {traceback}
        """
        pass

    def send_partial_notification(self, result: ExtractionResult):
        """
        Send partial success notification.

        Subject: [PARTIAL] AI QSR ETL - {business_name} - {date}
        """
        pass
```

#### 4.4 ConfigLoader (`src/utils/config_loader.py`)

**Purpose**: Load and validate configuration files

**Interface**:
```python
class ConfigLoader:
    @staticmethod
    def load_field_mapping(file_path: Path) -> FieldMapping:
        """
        Load field_mapping.csv into structured object.

        Returns:
            FieldMapping with 76 field configurations
        """
        pass

    @staticmethod
    def load_business_config(file_path: Path) -> BusinessConfig:
        """
        Load businesses.csv into structured object.

        Returns:
            BusinessConfig with 30 business unit mappings
        """
        pass

    @staticmethod
    def identify_business(sender_email: str,
                         business_config: BusinessConfig) -> str:
        """
        Identify business_id from sender email.

        Args:
            sender_email: Email address of sender
            business_config: Business configuration

        Returns:
            business_id (e.g., "BU_001")

        Raises:
            UnknownBusinessError: Email not in business config
        """
        pass
```

---

## Configuration Schemas

### field_mapping.csv

**Purpose**: Define position of all 76 fields in Excel template

**Schema**:
```csv
output_column_name,input_row_number,input_column_letter,data_type,is_required,default_value,validation_rule
project_name,3,C,text,true,,max_length:200
project_uuid,4,C,text,true,,format:uuid
project_description,5,C,text,false,"",
project_category,6,C,text,true,,enum:Enhancement|New Feature|Integration
strategic_value_level,7,C,integer,true,,range:1-5
project_examples,8,C,text,false,"",
ratio_impacted,9,C,text,false,"",
ai_tools_services,10,C,text,false,"",
contact_person,11,C,text,true,,
product_manager,12,C,text,false,"",
analyst,13,C,text,false,"",
tech_lead,14,C,text,false,"",
executive_sponsor,15,C,text,false,"",
kpi1_category,16,C,text,false,"",
kpi1_name,17,C,text,false,"",
kpi1_support_description,18,C,text,false,"",
kpi1_measurement_approach,19,C,text,false,"",
kpi1_target,20,C,float,false,0.0,
kpi1_actual,21,C,float,false,0.0,
kpi1_delta,22,C,float,false,0.0,
... (continue for all 76 fields)
```

**Columns**:
- `output_column_name`: Column name in AI_QSR_Consolidator.xlsx
- `input_row_number`: Row number in P# sheet (1-indexed)
- `input_column_letter`: Column letter in P# sheet (always C for values)
- `data_type`: text | integer | float | date | boolean
- `is_required`: true | false (validation requirement)
- `default_value`: Value to use if field empty
- `validation_rule`: Optional validation (max_length, range, enum, format)

**Benefits**:
- Maintainable: Update CSV if Excel template changes, no code changes
- Auditable: See all field mappings in one place
- Testable: Easy to test field extraction logic
- Flexible: Add validation rules without code changes

### businesses.csv

**Purpose**: Map email addresses to business unit IDs

**Schema**:
```csv
business_id,business_name,contact_email,is_active,notes
BU_001,ClubOS,clubos-pm@jonas.com,true,Tier 1 priority
BU_002,EZ Facility,ezfacility-contact@jonas.com,true,Tier 1 priority
BU_003,Campsite,campsite-team@jonas.com,true,Tier 1 priority
BU_004,InnoSoft,innosoft-dev@jonas.com,true,Tier 1 priority
BU_005,ClubWise,clubwise-ai@jonas.com,true,Tier 1 priority
BU_006,Jonas Fitness Inc,jfi-pm@jonas.com,true,Tier 1 priority
... (24 more business units)
```

**Columns**:
- `business_id`: Unique identifier (BU_001 - BU_030)
- `business_name`: Human-readable business name
- `contact_email`: Email domain for sender identification (supports comma-separated multiple)
- `is_active`: true | false (skip inactive businesses)
- `notes`: Optional notes (priority tier, etc.)

**Email Matching Logic**:
```python
def identify_business(sender_email: str, businesses: List[Business]) -> str:
    sender_domain = sender_email.split('@')[1]

    for business in businesses:
        if not business.is_active:
            continue

        # Support multiple emails (comma-separated)
        allowed_emails = [e.strip() for e in business.contact_email.split(',')]

        for allowed_email in allowed_emails:
            if sender_email.lower() == allowed_email.lower():
                return business.business_id

            # Domain-level matching
            allowed_domain = allowed_email.split('@')[1]
            if sender_domain.lower() == allowed_domain.lower():
                return business.business_id

    raise UnknownBusinessError(f"Email {sender_email} not found in business config")
```

---

## Data Flow Architecture

### End-to-End Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                       PHASE 1: INPUT ACQUISITION                    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
            ┌─────────────────┐        ┌─────────────────┐
            │ Email Monitor   │        │ Manual File     │
            │ (IMAP)          │        │ Input           │
            └─────────────────┘        └─────────────────┘
                     │                           │
                     │ Download Attachment       │ Provide File Path
                     ▼                           ▼
            ┌─────────────────────────────────────────────┐
            │         File System (temp/input/)           │
            └─────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 2: VALIDATION                            │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                     ┌───────────────────────────┐
                     │  FileValidator            │
                     │  - Check file format      │
                     │  - Detect corruption      │
                     │  - Verify sheet structure │
                     │  - Check merged cells     │
                     └───────────────────────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                   VALID  ▼                 ▼  INVALID
            ┌──────────────────┐    ┌──────────────────┐
            │ Continue         │    │ Send Error Email │
            │ Processing       │    │ Log Failure      │
            └──────────────────┘    │ STOP Processing  │
                     │              └──────────────────┘
                     │
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: EXTRACTION                            │
└─────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Identify Business Unit         │
        │ (businesses.csv lookup)        │
        └────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ ProjectExtractor               │
        │ - Load workbook (openpyxl)     │
        │ - Get project sheets (P1-P10)  │
        │ - For EACH sheet:              │
        │   - Try extract 76 fields      │
        │   - If success: add to list    │
        │   - If error: log and CONTINUE │
        └────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ ExtractionResult               │
        │ - projects: [...]              │
        │ - errors: [...]                │
        │ - extraction_id: uuid          │
        └────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: TRANSFORMATION                          │
└─────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ DataCleaner                    │
        │ - Clean text fields            │
        │ - Parse dates                  │
        │ - Normalize numbers            │
        └────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ DataValidator                  │
        │ - Check required fields        │
        │ - Validate data types          │
        │ - Business rule validation     │
        └────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Deduplicator                   │
        │ - Calculate data_hash          │
        │ - Check against master file    │
        │ - Filter duplicates            │
        └────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Validated Projects             │
        │ (duplicates removed)           │
        └────────────────────────────────┘
                     │
┌─────────────────────────────────────────────────────────────────────┐
│                       PHASE 5: LOADING                              │
└─────────────────────────────────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┬──────────────┐
          ▼                     ▼              ▼
┌───────────────────┐  ┌──────────────┐  ┌─────────────┐
│ ExcelLoader       │  │ Archive Mgr  │  │ LogWriter   │
│ - Append to       │  │ - Copy file  │  │ - Write     │
│   master file     │  │   to archive │  │   audit log │
│ - Never overwrite │  │ - Structured │  │   (CSV)     │
│ - Retry on lock   │  │   naming     │  └─────────────┘
└───────────────────┘  └──────────────┘
          │                     │              │
          └──────────┬──────────┴──────────────┘
                     │
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 6: NOTIFICATION                           │
└─────────────────────────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ EmailNotifier                  │
        │                                │
        │ If errors.count == 0:          │
        │   → Send SUCCESS email         │
        │                                │
        │ If 0 < errors < total:         │
        │   → Send PARTIAL email         │
        │                                │
        │ If errors.count == total:      │
        │   → Send ERROR email           │
        └────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ ETL Complete                   │
        │ - Logs written                 │
        │ - Notifications sent           │
        │ - Archive created              │
        └────────────────────────────────┘
```

### State Management

**Extraction State Tracking**:
```python
@dataclass
class ETLState:
    extraction_id: str
    business_id: str
    workbook_path: Path
    status: str  # STARTED, VALIDATING, EXTRACTING, TRANSFORMING, LOADING, COMPLETED, FAILED
    start_time: datetime
    end_time: Optional[datetime]
    current_phase: str
    sheets_processed: List[str]
    sheets_remaining: List[str]
```

**State Persistence**:
- In-memory state during processing
- Written to extraction_log.csv on completion
- No database required for Phase 1 (simplicity)

---

## Directory Structure (Detailed)

```
ai_qsr_etl/
├── config/                          # Configuration files
│   ├── businesses.csv               # Business unit mappings (30 rows)
│   ├── field_mapping.csv            # 76 field positions
│   └── email_config.yaml            # Email server settings (optional, can use .env)
│
├── data/                            # Data files
│   ├── AI_QSR_Consolidator.xlsx    # Master output file
│   ├── archive/                     # Archived workbooks
│   │   └── 2025/
│   │       ├── 10/
│   │       │   ├── BU_001_2025-10-26_uuid123.xlsx
│   │       │   └── BU_002_2025-10-26_uuid456.xlsx
│   │       └── 11/
│   │           └── ...
│   ├── logs/                        # Log files
│   │   ├── extraction_log.csv       # Audit trail
│   │   ├── etl_20251026.log         # Daily rotating logs
│   │   ├── etl_20251027.log
│   │   └── ...
│   └── temp/                        # Temporary files (auto-cleaned)
│       └── ...
│
├── src/                             # Source code
│   ├── __init__.py
│   │
│   ├── extractors/                  # Extraction layer
│   │   ├── __init__.py
│   │   ├── email_handler.py         # Email monitoring (IMAP)
│   │   ├── file_validator.py        # File structure validation
│   │   └── project_extractor.py     # 76-field extraction logic
│   │
│   ├── transformers/                # Transformation layer
│   │   ├── __init__.py
│   │   ├── data_cleaner.py          # Data normalization
│   │   ├── data_validator.py        # Business rule validation
│   │   └── deduplicator.py          # Hash-based duplicate detection
│   │
│   ├── loaders/                     # Loading layer
│   │   ├── __init__.py
│   │   ├── excel_loader.py          # Master file appender
│   │   ├── archive_manager.py       # Workbook archival
│   │   └── log_writer.py            # Audit log writer
│   │
│   ├── utils/                       # Cross-cutting utilities
│   │   ├── __init__.py
│   │   ├── config_loader.py         # Config file parsers
│   │   ├── error_collector.py       # Error aggregation
│   │   ├── logger.py                # Structured logging
│   │   ├── notifier.py              # Email notifications
│   │   └── helpers.py               # Common utilities
│   │
│   └── orchestrator.py              # Pipeline orchestration
│
├── tests/                           # Test suite
│   ├── __init__.py
│   │
│   ├── unit/                        # Unit tests
│   │   ├── test_extractor.py
│   │   ├── test_validator.py
│   │   ├── test_cleaner.py
│   │   ├── test_deduplicator.py
│   │   └── test_loader.py
│   │
│   ├── integration/                 # Integration tests
│   │   ├── test_full_etl.py
│   │   └── test_error_handling.py
│   │
│   ├── e2e/                         # End-to-end tests
│   │   ├── test_email_workflow.py
│   │   └── test_manual_workflow.py
│   │
│   └── fixtures/                    # Test data
│       ├── sample_valid.xlsx
│       ├── sample_invalid_merged_cells.xlsx
│       ├── sample_missing_fields.xlsx
│       ├── sample_10_projects.xlsx
│       └── businesses_test.csv
│
├── docs/                            # Documentation
│   ├── architecture.md              # This architecture document
│   ├── field_mapping_guide.md       # How to update field mappings
│   └── troubleshooting.md           # Common issues and solutions
│
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
├── .gitignore                       # Git ignore rules
└── README.md                        # Setup and usage guide
```

**Key Directory Responsibilities**:

- `config/`: All externalized configuration (no hardcoded values)
- `data/`: All data artifacts (master file, archives, logs)
- `src/extractors/`: Only responsible for getting data in
- `src/transformers/`: Only responsible for cleaning/validating data
- `src/loaders/`: Only responsible for writing data out
- `src/utils/`: Shared utilities with no business logic
- `tests/`: Comprehensive test coverage at all levels

---

## Design Decisions & Rationale

### Decision 1: Config-Driven Field Mapping

**Choice**: Use `field_mapping.csv` instead of hardcoding field positions

**Rationale**:
- Excel template may change (fields move, new fields added)
- Non-technical users can update CSV without code changes
- Easy to audit all field mappings in one place
- Supports multiple template versions simultaneously

**Alternatives Considered**:
- Hardcode in Python constants (rejected - not maintainable)
- JSON config (rejected - CSV easier for non-technical users)
- Database table (rejected - overkill for Phase 1)

**Tradeoffs**:
- Pro: Extremely flexible, maintainable by non-developers
- Pro: Easy to version control field mapping changes
- Con: Requires CSV parsing on every run (minimal performance impact <10ms)
- Con: Field mapping errors only caught at runtime, not compile time

**Implementation Guidance**:
```python
# Load once at startup
field_mapping = ConfigLoader.load_field_mapping('config/field_mapping.csv')

# Use throughout extraction
for field_config in field_mapping.fields:
    cell_value = worksheet[f'{field_config.column}{field_config.row}'].value
    project_data[field_config.output_name] = convert_type(cell_value, field_config.data_type)
```

### Decision 2: Error Aggregation Without Stopping

**Choice**: Collect all errors, never stop entire ETL run

**Rationale**:
- Partial success is valuable (8 of 10 projects better than 0)
- Business needs weekly data even if some sheets malformed
- Better user experience (one comprehensive error report vs multiple failures)
- Reduces manual intervention (don't need to fix and re-run for each error)

**Alternatives Considered**:
- Fail-fast on first error (rejected - too disruptive)
- Stop per-workbook but continue across workbooks (rejected - still loses partial data)

**Tradeoffs**:
- Pro: Maximum data capture
- Pro: Better error reporting (see all issues at once)
- Pro: Reduces manual intervention
- Con: More complex error handling logic
- Con: Must carefully track state to know what succeeded/failed

**Implementation Pattern**:
```python
# ALWAYS use this pattern
errors = []
successes = []

for item in items_to_process:
    try:
        result = process_item(item)
        successes.append(result)
    except Exception as e:
        errors.append({'item': item, 'error': e})
        continue  # CRITICAL: Don't stop

return ProcessResult(successes=successes, errors=errors)
```

### Decision 3: xxhash for Duplicate Detection

**Choice**: Use xxhash for data_hash calculation

**Rationale**:
- 10x faster than MD5/SHA for large strings
- Collision resistance sufficient for this use case (30 businesses × 10 projects × 52 weeks = ~15,000 records/year)
- Python bindings mature and stable
- Non-cryptographic hash appropriate (not securing data, just detecting duplicates)

**Alternatives Considered**:
- MD5 (rejected - slower, overkill for collision resistance)
- SHA256 (rejected - much slower, cryptographic features not needed)
- Simple string comparison (rejected - no collision detection)

**Tradeoffs**:
- Pro: Very fast (< 1ms per hash)
- Pro: Low memory footprint
- Con: Requires additional dependency (xxhash package)
- Con: Hash not cryptographically secure (acceptable for this use case)

**Hash Key Design**:
```python
# Hash key: business_id + sheet_name + submission_week
# Allows same project tracked week-over-week as separate entries
# Detects duplicate submissions within same week

hash_key = f"{business_id}|{sheet_name}|{submission_week}"
# Example: "BU_001|P1|2025-W43"
```

### Decision 4: Excel Output (Phase 1) vs Database (Future)

**Choice**: Use Excel as master file for Phase 1

**Rationale**:
- Stakeholders already use Excel ecosystem
- No database infrastructure required
- Easy to inspect/audit data manually
- Supports existing workflows (pivot tables, charts, etc.)
- Fast time-to-value (no DB setup)

**Alternatives Considered**:
- PostgreSQL (rejected for Phase 1 - infrastructure overhead)
- SQLite (considered - but Excel provides better stakeholder experience)
- Cloud database (rejected for Phase 1 - costs and complexity)

**Tradeoffs**:
- Pro: Zero infrastructure setup
- Pro: Familiar to stakeholders
- Pro: Easy manual inspection
- Con: Performance degrades >50,000 rows (plan database migration)
- Con: No concurrent write support (single ETL run at a time)
- Con: Limited query capabilities compared to SQL

**Migration Path**:
```python
# Design loaders with interface abstraction
class DataLoader(ABC):
    @abstractmethod
    def load_projects(self, projects: List[ProjectData]) -> LoadResult:
        pass

class ExcelLoader(DataLoader):
    # Phase 1 implementation
    pass

class DatabaseLoader(DataLoader):
    # Phase 2 implementation
    # Can swap without changing upstream code
    pass
```

### Decision 5: openpyxl with data_only=True

**Choice**: Use openpyxl with data_only=True parameter

**Rationale**:
- Excel cells contain formulas (=SUM(...), =IF(...), etc.)
- Need calculated values, not formula strings
- data_only=True returns last cached value from Excel
- Alternative (evaluate formulas live) requires Excel COM automation (Windows-only)

**Alternatives Considered**:
- xlrd (rejected - deprecated for .xlsx, only .xls)
- pandas read_excel (rejected - doesn't handle formulas well)
- Excel COM automation (rejected - Windows-only, heavy dependency)

**Tradeoffs**:
- Pro: Cross-platform (works on Windows/Mac/Linux)
- Pro: No Excel installation required
- Pro: Fast and reliable
- Con: Returns cached values, not live calculations
- Con: If file never saved in Excel, cached values may be None

**Mitigation**:
```python
# Document edge case in validation
if cell_value is None and cell.data_type == 'f':  # Formula cell
    raise ValidationError(
        "Formula cell has no cached value. "
        "Please open workbook in Excel and save before submitting."
    )
```

### Decision 6: Pipeline Orchestrator Pattern

**Choice**: Central orchestrator coordinates all components

**Rationale**:
- Clear entry point for ETL process
- Manages dependencies between components
- Handles error aggregation across all phases
- Provides consistent logging and notification

**Alternatives Considered**:
- Chain of responsibility (rejected - harder to test individual components)
- Event-driven architecture (rejected - overkill for linear ETL)

**Tradeoffs**:
- Pro: Clear control flow
- Pro: Easy to test orchestration logic
- Pro: Single place to manage error aggregation
- Con: Orchestrator can become complex
- Con: Tight coupling between orchestrator and components

**Implementation**:
```python
# src/orchestrator.py
class ETLOrchestrator:
    def __init__(self, config: ETLConfig):
        self.email_handler = EmailHandler(config.email)
        self.file_validator = FileValidator(config.validation)
        self.project_extractor = ProjectExtractor(config.field_mapping)
        self.data_cleaner = DataCleaner()
        self.deduplicator = Deduplicator(config.master_file_path)
        self.excel_loader = ExcelLoader(config.master_file_path)
        self.archive_manager = ArchiveManager(config.archive_path)
        self.notifier = EmailNotifier(config.smtp)
        self.error_collector = ErrorCollector()

    def run_etl(self, mode: str = 'email'):
        # Coordinate entire pipeline
        pass
```

---

## Integration Points

### 1. Email Monitoring Integration

**Protocol**: IMAP (Internet Message Access Protocol)

**Configuration**:
```yaml
# config/email_config.yaml (or .env)
IMAP_SERVER: imap.gmail.com
IMAP_PORT: 993
IMAP_USE_SSL: true
EMAIL_ADDRESS: etl@company.com
EMAIL_PASSWORD: app_password_here
SEARCH_FOLDER: INBOX
MARK_AS_READ: true
```

**Email Filter Criteria**:
```python
# Search for unread emails with Excel attachments
search_criteria = [
    'UNSEEN',  # Unread only
    'SUBJECT "QSR"',  # Subject contains "QSR"
    'FROM "@jonas.com"',  # From jonas.com domain
]
```

**Attachment Processing**:
```python
# Email structure
email = {
    'from': 'clubos-pm@jonas.com',
    'subject': 'AI QSR Week 43 Submission',
    'attachments': [
        {
            'filename': 'AI_QSR_Inputs_vBeta.xlsx',
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size': 125000  # bytes
        }
    ]
}

# Download and validate
if attachment.content_type in ALLOWED_CONTENT_TYPES:
    file_bytes = email_handler.download_attachment(attachment)
    temp_path = save_to_temp(file_bytes, attachment.filename)
    validate_and_process(temp_path)
```

**Error Scenarios**:
- No attachment → Skip email, send warning to sender
- Multiple attachments → Process all Excel files, warn if >1 Excel
- Corrupted attachment → Skip, send error notification
- Unknown sender → Skip, send warning to admin

### 2. SharePoint Integration (Phase 2)

**Library**: Office365-REST-Python-Client

**Configuration**:
```python
from office365.sharepoint.client_context import ClientContext

sharepoint_config = {
    'site_url': 'https://company.sharepoint.com/sites/AI-QSR',
    'document_library': 'Weekly Submissions',
    'username': 'etl-service@company.com',
    'password': 'app_password'
}
```

**Polling Strategy**:
```python
# Check for new files every 30 minutes
while True:
    new_files = sharepoint.get_files_modified_since(last_check)

    for file in new_files:
        if file.name.endswith('.xlsx'):
            process_file(file)

    last_check = datetime.now()
    time.sleep(1800)  # 30 minutes
```

### 3. Notification System Integration

**Protocol**: SMTP (Simple Mail Transfer Protocol)

**Configuration**:
```python
SMTP_SERVER: smtp.gmail.com
SMTP_PORT: 587
SMTP_USE_TLS: true
SMTP_USERNAME: notifications@company.com
SMTP_PASSWORD: app_password
NOTIFICATION_TO: data-team@company.com
NOTIFICATION_CC: ai-transformation@company.com
```

**Email Templates**:

**Success Template**:
```html
<html>
<head><style>
    .success { color: green; font-weight: bold; }
    table { border-collapse: collapse; }
    th, td { border: 1px solid #ddd; padding: 8px; }
</style></head>
<body>
<h2 class="success">✅ AI QSR ETL - Success</h2>

<p><strong>Extraction ID:</strong> {extraction_id}</p>
<p><strong>Business:</strong> {business_name} ({business_id})</p>
<p><strong>Timestamp:</strong> {timestamp}</p>
<p><strong>Workbook:</strong> {filename}</p>

<h3>Results</h3>
<table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Projects Extracted</td><td>{project_count}</td></tr>
    <tr><td>Sheets Processed</td><td>{sheets_succeeded}/{sheets_total}</td></tr>
    <tr><td>Errors</td><td>0</td></tr>
</table>

<h3>Next Steps</h3>
<ul>
    <li>Data appended to master file</li>
    <li>Original workbook archived</li>
    <li>Extraction logged to audit trail</li>
</ul>
</body>
</html>
```

**Error Template**:
```html
<html>
<head><style>
    .error { color: red; font-weight: bold; }
    .error-detail { background: #ffe6e6; padding: 10px; margin: 10px 0; }
</style></head>
<body>
<h2 class="error">❌ AI QSR ETL - Errors Detected</h2>

<p><strong>Extraction ID:</strong> {extraction_id}</p>
<p><strong>Business:</strong> {business_name} ({business_id})</p>
<p><strong>Timestamp:</strong> {timestamp}</p>
<p><strong>Workbook:</strong> {filename}</p>

<h3>Results</h3>
<table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Projects Extracted</td><td>{success_count}</td></tr>
    <tr><td>Sheets Failed</td><td>{error_count}</td></tr>
</table>

<h3>Error Details</h3>
{for error in errors}
<div class="error-detail">
    <p><strong>Sheet:</strong> {error.sheet_name}</p>
    <p><strong>Error:</strong> {error.message}</p>
    <pre>{error.traceback}</pre>
</div>
{endfor}

<h3>Action Required</h3>
<p>Please review the errors above and resubmit corrected workbook.</p>
</body>
</html>
```

### 4. Logging System Integration

**Library**: Python logging module + loguru (optional)

**Log Rotation Strategy**:
```python
import logging
from logging.handlers import TimedRotatingFileHandler

# Daily rotation, keep 30 days
handler = TimedRotatingFileHandler(
    filename='data/logs/etl.log',
    when='midnight',
    interval=1,
    backupCount=30
)

formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(extraction_id)s | %(message)s'
)
handler.setFormatter(formatter)
```

**Log Levels**:
- DEBUG: Field-level extraction details
- INFO: Phase transitions, progress updates
- WARNING: Non-critical issues (missing optional fields)
- ERROR: Sheet extraction failures, validation errors
- CRITICAL: System-level failures (disk full, SMTP down)

**Log Output Examples**:
```
2025-10-26 14:30:00 | INFO | uuid-123 | Starting ETL run for BU_001
2025-10-26 14:30:01 | INFO | uuid-123 | Validating file: AI_QSR_Inputs_vBeta.xlsx
2025-10-26 14:30:02 | INFO | uuid-123 | Validation passed, 8 project sheets found
2025-10-26 14:30:03 | DEBUG | uuid-123 | Extracting P1: Field 'project_name' = 'Member Retention AI'
2025-10-26 14:30:04 | INFO | uuid-123 | ✅ Extracted P1: Member Retention AI
2025-10-26 14:30:05 | ERROR | uuid-123 | ❌ Failed P2: Required field 'project_name' missing
2025-10-26 14:30:06 | INFO | uuid-123 | ✅ Extracted P3: Voice Operations Assistant
2025-10-26 14:30:15 | INFO | uuid-123 | Extraction complete: 7/8 succeeded
2025-10-26 14:30:16 | INFO | uuid-123 | Appending 7 projects to master file
2025-10-26 14:30:17 | INFO | uuid-123 | Master file updated: 7 rows written
2025-10-26 14:30:18 | INFO | uuid-123 | Sending partial success notification
```

---

## Scalability Considerations

### Current Scale (Phase 1)

- **Business Units**: 30
- **Projects per BU**: 1-10 (average 5)
- **Submissions per Week**: 30 workbooks
- **Records per Week**: ~150 projects
- **Annual Data Volume**: ~7,800 projects
- **Excel File Size**: ~2-5MB per year

**Performance Targets**:
- Workbook processing: < 5 seconds per workbook
- Total weekly ETL: < 3 minutes for all 30 businesses
- Master file append: < 500ms for 150 rows

### Future Scale (Phase 2+)

**Scenario: 100 Business Units**

- Records per Week: ~500 projects
- Annual Data Volume: ~26,000 projects
- Excel File Size: ~8-15MB per year (approaching Excel limits)

**Recommended Migration Path**:

1. **Year 1 (0-10,000 rows)**: Excel output (current design)
2. **Year 2 (10,000-50,000 rows)**: Dual output (Excel + SQLite)
3. **Year 3 (50,000+ rows)**: PostgreSQL with Excel export for reporting

**Database Schema (Future)**:
```sql
-- projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    extraction_id UUID NOT NULL,
    business_id VARCHAR(10) NOT NULL,
    business_name VARCHAR(100),
    sheet_name VARCHAR(10),
    submission_date TIMESTAMP,
    submission_week VARCHAR(7),  -- YYYY-WW
    workbook_filename VARCHAR(255),
    data_hash VARCHAR(64) UNIQUE,

    -- 76 project fields
    project_name VARCHAR(200),
    project_uuid UUID,
    -- ... (all 76 fields)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- extraction_log table
CREATE TABLE extraction_log (
    id SERIAL PRIMARY KEY,
    extraction_id UUID UNIQUE,
    business_id VARCHAR(10),
    timestamp TIMESTAMP,
    status VARCHAR(20),  -- SUCCESS, PARTIAL, FAILED
    sheets_attempted INT,
    sheets_succeeded INT,
    sheets_failed INT,
    error_count INT
);

-- Indexes
CREATE INDEX idx_business_week ON projects(business_id, submission_week);
CREATE INDEX idx_data_hash ON projects(data_hash);
CREATE INDEX idx_submission_date ON projects(submission_date);
```

### Performance Optimization Strategies

**Parallel Processing**:
```python
# Phase 2: Process multiple workbooks in parallel
from concurrent.futures import ThreadPoolExecutor

def process_workbook(file_path: Path):
    # Extract, transform, load
    pass

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_workbook, f) for f in workbooks]
    results = [future.result() for future in futures]
```

**Batch Loading**:
```python
# Instead of appending one row at a time
# Batch all projects and append once
all_projects = []
for workbook in workbooks:
    projects = extract_workbook(workbook)
    all_projects.extend(projects)

# Single append operation
excel_loader.load_projects(all_projects)
```

**Caching**:
```python
# Cache field mapping and business config
# Load once at startup, not per workbook
class ETLOrchestrator:
    def __init__(self):
        self.field_mapping = load_field_mapping()  # Load once
        self.business_config = load_business_config()  # Load once
```

---

## Testing Strategy

### Level 1: Unit Tests (Isolation)

**Coverage Target**: 80%+ line coverage

**Example Tests**:
```python
# tests/unit/test_extractor.py

def test_extract_text_field():
    """Test extracting text field from cell."""
    worksheet = create_mock_worksheet({'C3': 'Project Name'})
    field_config = FieldConfig(row=3, column='C', data_type='text')

    result = extractor.extract_field(worksheet, field_config)

    assert result == 'Project Name'

def test_extract_missing_required_field_raises_error():
    """Test that missing required field raises error."""
    worksheet = create_mock_worksheet({'C3': None})
    field_config = FieldConfig(row=3, column='C', data_type='text', required=True)

    with pytest.raises(FieldExtractionError):
        extractor.extract_field(worksheet, field_config)

def test_extract_date_field_excel_serial():
    """Test parsing Excel serial date (44927 = 2022-12-15)."""
    worksheet = create_mock_worksheet({'C5': 44927})
    field_config = FieldConfig(row=5, column='C', data_type='date')

    result = extractor.extract_field(worksheet, field_config)

    assert result == datetime(2022, 12, 15)
```

### Level 2: Integration Tests (Component Interaction)

**Example Tests**:
```python
# tests/integration/test_full_etl.py

def test_process_single_workbook_success():
    """Test full ETL pipeline with valid workbook."""
    # Setup
    workbook_path = 'tests/fixtures/sample_valid.xlsx'
    orchestrator = ETLOrchestrator(test_config)

    # Execute
    result = orchestrator.run_etl(mode='manual', file_path=workbook_path)

    # Assert
    assert result.status == 'SUCCESS'
    assert result.projects_extracted == 8
    assert len(result.errors) == 0

    # Verify master file updated
    master_df = pd.read_excel('data/AI_QSR_Consolidator.xlsx')
    assert len(master_df) == 8

def test_process_workbook_with_errors_continues():
    """Test that errors in some sheets don't stop entire extraction."""
    # Setup: Workbook with 10 sheets, 2 have missing required fields
    workbook_path = 'tests/fixtures/sample_partial_errors.xlsx'
    orchestrator = ETLOrchestrator(test_config)

    # Execute
    result = orchestrator.run_etl(mode='manual', file_path=workbook_path)

    # Assert
    assert result.status == 'PARTIAL'
    assert result.projects_extracted == 8
    assert len(result.errors) == 2

    # Verify 8 successful projects saved
    master_df = pd.read_excel('data/AI_QSR_Consolidator.xlsx')
    assert len(master_df) == 8
```

### Level 3: E2E Tests (Full Workflow)

**Example Tests**:
```python
# tests/e2e/test_email_workflow.py

def test_email_workflow_complete():
    """Test complete email monitoring workflow."""
    # Setup: Mock IMAP server with test email
    mock_imap = setup_mock_imap_server()
    add_test_email(
        from_='clubos-pm@jonas.com',
        subject='AI QSR Week 43',
        attachment='tests/fixtures/sample_valid.xlsx'
    )

    # Execute: Run email monitoring
    orchestrator = ETLOrchestrator(test_config)
    orchestrator.run_etl(mode='email')

    # Assert: Email processed, data extracted, notification sent
    assert email_marked_as_read()
    assert master_file_contains_new_projects(8)
    assert notification_sent_to('clubos-pm@jonas.com')
    assert archive_created()
```

### Level 4: Edge Case Tests

**Critical Edge Cases**:
```python
# Merged cells
def test_reject_workbook_with_merged_cells()

# Password protected
def test_reject_password_protected_workbook()

# Corrupted file
def test_handle_corrupted_excel_file()

# Formula cells with no cached value
def test_handle_formula_cells_no_cache()

# Duplicate submission same week
def test_skip_duplicate_submission()

# Unknown business email
def test_reject_unknown_business_sender()

# Missing required field
def test_skip_sheet_with_missing_required_field()

# Invalid date formats
def test_parse_various_date_formats()

# Empty workbook (0 project sheets)
def test_reject_workbook_no_project_sheets()

# >10 project sheets
def test_handle_workbook_more_than_10_sheets()
```

---

## Challenges Encountered

No challenges encountered during architecture phase - this is pure design work. Implementation team may encounter challenges during development, which should be documented in their execution summaries.

---

## Validation Results

N/A - Architecture design phase has no code to validate. Implementation team will validate their code against this architecture design.

---

## Handoff Notes

### For Implementation Team

**Critical Architecture Principles**:

1. **NEVER Stop on Error**: Always collect errors and continue processing
   - Use error_collector pattern throughout
   - Return both successes and failures from every function
   - Partial success is valuable

2. **Config-Driven Everything**: No hardcoded field positions or business mappings
   - Use field_mapping.csv for all field extractions
   - Use businesses.csv for all business lookups
   - Makes system maintainable by non-developers

3. **Separation of Concerns**: Each module has one responsibility
   - Extractors: Get data in
   - Transformers: Clean and validate
   - Loaders: Write data out
   - Don't mix responsibilities

4. **Testability First**: Design for unit testing
   - Use dependency injection
   - Mock external dependencies (IMAP, file system, SMTP)
   - Each function should be testable in isolation

**Implementation Order Recommendation**:

**Week 1: Foundation**
1. Setup project structure and dependencies
2. Implement ConfigLoader (field_mapping.csv, businesses.csv)
3. Implement ErrorCollector and Logger
4. Create test fixtures

**Week 2: Extraction Layer**
5. Implement FileValidator
6. Implement ProjectExtractor (core 76-field extraction)
7. Unit tests for extraction logic
8. Integration test for full extraction

**Week 3: Transformation Layer**
9. Implement DataCleaner
10. Implement DataValidator
11. Implement Deduplicator
12. Unit tests for transformation logic

**Week 4: Loading Layer**
13. Implement ExcelLoader
14. Implement ArchiveManager
15. Implement LogWriter
16. Integration test for full loading

**Week 5: Orchestration**
17. Implement ETLOrchestrator
18. Implement EmailHandler (manual mode first)
19. Implement EmailNotifier
20. E2E test for manual workflow

**Week 6: Email Monitoring**
21. Implement EmailHandler (IMAP mode)
22. E2E test for email workflow
23. Error scenario testing
24. Performance testing

**Week 7: Polish & Documentation**
25. Comprehensive error handling
26. User documentation
27. Deployment guide
28. Handoff to operations

**Critical Files to Create First**:
1. `config/field_mapping.csv` (76 rows - defines entire extraction logic)
2. `config/businesses.csv` (30 rows - defines business mappings)
3. `src/utils/error_collector.py` (used by all components)
4. `src/utils/logger.py` (used by all components)
5. `src/utils/config_loader.py` (loads configs for all components)

**Gotchas to Watch For**:

1. **openpyxl Formula Handling**:
   - Use `data_only=True` to get cached values
   - Cells may return None if Excel hasn't calculated
   - Document this in user guide

2. **Excel File Locking**:
   - If user has file open, write will fail
   - Implement retry logic with 3 attempts
   - Clear error message to close file

3. **Date Parsing**:
   - Excel stores dates as serial numbers (44927)
   - openpyxl may return datetime objects or numbers
   - Handle both cases in clean_date_field()

4. **Merged Cells**:
   - Only top-left cell contains value
   - Other cells in merge return None
   - Validate and reject files with merged cells

5. **Sheet Name Matching**:
   - Use regex: `^P\d{1,2}$` (P1, P2, ..., P10)
   - Case-sensitive matching
   - Ignore sheets like "P1 Draft" or "P1_old"

6. **Hash Calculation**:
   - Include business_id + sheet_name + submission_week
   - Use consistent encoding (UTF-8)
   - Store as hex string in data_hash column

**Testing Checklist Before Launch**:

- [ ] Extract all 76 fields from sample workbook
- [ ] Handle missing optional fields gracefully
- [ ] Reject files with missing required fields
- [ ] Detect and skip duplicate submissions
- [ ] Process 10 project sheets in single workbook
- [ ] Continue processing after sheet extraction failure
- [ ] Send success notification with correct counts
- [ ] Send error notification with full traceback
- [ ] Archive workbook with correct naming
- [ ] Append to master file without overwriting
- [ ] Write extraction log entry
- [ ] Handle file locking gracefully
- [ ] Parse multiple date formats
- [ ] Identify business from email correctly
- [ ] Reject unknown business senders

**Performance Benchmarks**:

Target performance for Phase 1:
- Single workbook processing: < 5 seconds
- 30 workbook batch: < 3 minutes
- Master file append (150 rows): < 500ms
- Email check and download: < 10 seconds

If performance slower than targets:
1. Profile code to find bottleneck
2. Consider parallel processing for multiple workbooks
3. Batch database operations
4. Cache field_mapping and business_config

**Support for Future Database Migration**:

Design loaders with interface abstraction:
```python
class DataLoader(ABC):
    @abstractmethod
    def load_projects(self, projects: List[ProjectData]) -> LoadResult:
        pass

class ExcelLoader(DataLoader):
    # Phase 1
    pass

class DatabaseLoader(DataLoader):
    # Phase 2 - can swap without changing upstream code
    pass
```

### Questions for Product Owner

Before starting implementation, clarify:

1. **Email Monitoring Frequency**: Continuous monitoring or hourly checks?
2. **Duplicate Handling**: Silent skip or notify sender?
3. **Partial Success**: Save partial data or reject entire workbook?
4. **Error Notification Recipients**: Send to sender, admin, or both?
5. **Archive Retention**: How long to keep archived workbooks?
6. **Log Retention**: How long to keep daily logs?

### Unresolved Design Questions

1. **Concurrent Submissions**: What if two businesses submit simultaneously?
   - Phase 1: Single-threaded processing (FIFO queue)
   - Phase 2: Thread-safe master file appending

2. **Workbook Versioning**: What if business resubmits corrected file?
   - Current design: Duplicate detection prevents overwrite
   - Future: Add "replacement" mode to update existing entries

3. **Schema Evolution**: What if new fields added to Excel template?
   - Add rows to field_mapping.csv
   - Existing extractions unaffected (NULL for new fields)
   - Requires database migration for Phase 2

---

## Artifacts Produced

**Architecture Documents**:
- This comprehensive architecture summary (execution_logs/architecture_summary_1.md)

**Design Artifacts** (to be created by implementation team):
- Component interface definitions
- Data structure schemas
- Configuration file templates
- Test fixture specifications

**Configuration Schemas Defined**:
- field_mapping.csv schema (76 fields)
- businesses.csv schema (30 business units)
- extraction_log.csv schema (audit trail)
- .env template (environment variables)

**Directory Structure Designed**:
- Complete src/ module organization
- Test suite structure
- Data file organization
- Archive directory hierarchy

---

## References

**Architectural Patterns**:
- Pipeline Architecture: https://en.wikipedia.org/wiki/Pipeline_(software)
- ETL Pattern: https://en.wikipedia.org/wiki/Extract,_transform,_load
- Chain of Responsibility: https://refactoring.guru/design-patterns/chain-of-responsibility
- Strategy Pattern (for config-driven logic): https://refactoring.guru/design-patterns/strategy

**Python Libraries**:
- pandas: https://pandas.pydata.org/docs/
- openpyxl: https://openpyxl.readthedocs.io/
- xxhash: https://github.com/ifduyue/python-xxhash
- python-dotenv: https://pypi.org/project/python-dotenv/
- Office365 REST: https://github.com/vgrem/Office365-REST-Python-Client

**Best Practices**:
- Fail-Safe Processing: https://martinfowler.com/articles/patterns-of-distributed-systems/failing-gracefully.html
- Config-Driven Systems: https://12factor.net/config
- Structured Logging: https://www.structlog.org/en/stable/why.html

**Internal References**:
- Project Requirements: [Initial.md](../Initial.md)
- Execution Log: [execution_log.md](../execution_log.md)
- Logging Protocol: [PROJECT_CONTEXT.md](../PROJECT_CONTEXT.md)

---

## Summary

This architecture provides a **robust, maintainable, and scalable foundation** for the AI QSR Consolidation ETL system.

**Key Architectural Strengths**:

1. **Separation of Concerns**: Clear boundaries between extraction, transformation, and loading
2. **Error Resilience**: Partial success supported with comprehensive error aggregation
3. **Config-Driven**: All business logic externalized for non-developer maintenance
4. **Testability**: Each component independently testable with clear interfaces
5. **Scalability**: Designed for 30 BUs, scales to 100+ with database migration path
6. **Maintainability**: Single responsibility per module, dependency injection, clear documentation

**Implementation Team Next Steps**:

1. Review this architecture document thoroughly
2. Ask clarifying questions on any unclear design decisions
3. Follow recommended implementation order (Week 1-7 plan)
4. Create field_mapping.csv and businesses.csv first (foundation)
5. Implement error_collector.py and logger.py early (used everywhere)
6. Write tests alongside implementation (not after)
7. Validate against checklist before considering complete

**Success Metrics**:

- ✅ All 76 fields extracted accurately
- ✅ Partial failures handled gracefully (continue processing)
- ✅ Duplicates detected and skipped
- ✅ Master file grows week-over-week without data loss
- ✅ Comprehensive error reporting
- ✅ < 5 seconds per workbook processing
- ✅ Zero manual intervention for successful extractions

This architecture is ready for implementation. Good luck! 🚀
