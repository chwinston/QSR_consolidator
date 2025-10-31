"""
AI QSR Consolidator - Main ETL Script

Extracts project data from business unit workbooks and consolidates into master Excel file.
"""

import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import ETLLogger
from src.utils.error_collector import ErrorCollector
from src.utils.helpers import generate_extraction_id, get_submission_week

from src.extractors.file_validator import FileValidator
from src.extractors.project_extractor import ProjectExtractor

from src.transformers.data_cleaner import DataCleaner
from src.transformers.data_validator import DataValidator
from src.transformers.deduplicator import Deduplicator

from src.loaders.excel_loader import ExcelLoader
from src.loaders.archive_manager import ArchiveManager
from src.loaders.log_writer import LogWriter


class AIQSRConsolidator:
    """
    Main ETL orchestrator for AI QSR data consolidation.

    Pipeline:
    1. Validation: Validate workbook (7 validation gates)
    2. Extraction: Extract 76 fields from P1-P10 sheets
    3. Transformation: Clean, validate, deduplicate
    4. Loading: Append to master file, archive, log
    """

    def __init__(
        self,
        config_dir: Path = None,
        master_file: Path = None,
        archive_dir: Path = None,
        log_level: str = "INFO"
    ):
        """
        Initialize ETL consolidator.

        Args:
            config_dir: Configuration directory (default: ./config)
            master_file: Master consolidator file (default: ./data/AI_QSR_Consolidator.xlsx)
            archive_dir: Archive directory (default: ./data/archive)
            log_level: Logging level
        """
        # Set default paths
        base_dir = Path(__file__).parent
        self.config_dir = config_dir or base_dir / "config"
        self.master_file = master_file or base_dir / "data" / "AI_QSR_Consolidator.xlsx"
        self.archive_dir = archive_dir or base_dir / "data" / "archive"
        self.log_dir = base_dir / "data" / "logs"
        self.extraction_log = base_dir / "data" / "extraction_log.csv"

        # Initialize logger
        self.logger = ETLLogger(log_level=log_level, log_dir=str(self.log_dir))

        # Load configuration
        self.logger.info("Loading configuration...")
        self.config = ConfigLoader(self.config_dir)
        try:
            if not self.config.load_all():
                raise ValueError("Configuration validation failed")
            self.logger.info(
                f"Configuration loaded: {len(self.config.field_mappings)} fields, "
                f"{len(self.config.businesses)} businesses"
            )
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise

        # Initialize components
        self.validator = FileValidator()
        self.extractor = ProjectExtractor(self.config, self.logger)
        self.cleaner = DataCleaner()
        self.data_validator = DataValidator()
        self.deduplicator = Deduplicator(self.master_file, self.logger)
        self.loader = ExcelLoader(self.master_file, self.logger)
        self.archiver = ArchiveManager(self.archive_dir, self.logger)
        self.log_writer = LogWriter(self.extraction_log, self.logger)

    def process_workbook(
        self,
        file_path: Path,
        business_id: str,
        skip_deduplication: bool = False
    ) -> dict:
        """
        Process a single workbook through the ETL pipeline.

        Args:
            file_path: Path to Excel workbook
            business_id: Business unit identifier
            skip_deduplication: Skip duplicate detection (for testing)

        Returns:
            Result dictionary with extraction_id, project_count, error_count, status
        """
        extraction_id = generate_extraction_id()
        submission_date = datetime.now()
        submission_week = get_submission_week(submission_date)

        self.logger.info(f"="*80)
        self.logger.info(f"Starting ETL process")
        self.logger.info(f"Extraction ID: {extraction_id}")
        self.logger.info(f"Business: {business_id}")
        self.logger.info(f"File: {file_path}")
        self.logger.info(f"="*80)

        result = {
            'extraction_id': extraction_id,
            'business_id': business_id,
            'file_path': str(file_path),
            'project_count': 0,
            'error_count': 0,
            'status': 'FAILED',
            'errors': []
        }

        # Step 1: Validation
        self.logger.info("Step 1/4: Validating workbook...")
        is_valid, error_message = self.validator.validate(file_path)

        if not is_valid:
            self.logger.error(f"Validation failed: {error_message}")
            result['errors'].append(f"Validation failed: {error_message}")
            result['status'] = 'FAILED'
            return result

        self.logger.info("Validation passed")
        project_sheets = self.validator.get_project_sheets(file_path)
        self.logger.info(f"Found {len(project_sheets)} project sheets: {project_sheets}")

        # Step 2: Extraction
        self.logger.info("Step 2/4: Extracting project data...")
        projects, error_collector = self.extractor.extract_workbook(
            file_path=file_path,
            business_id=business_id,
            sheet_names=project_sheets,
            submission_date=submission_date
        )

        result['error_count'] = error_collector.error_count()
        result['errors'] = [str(e) for e in error_collector.get_all_errors()]

        if not projects:
            self.logger.error("No projects extracted")
            result['status'] = 'FAILED'
            return result

        self.logger.info(f"Extracted {len(projects)} projects")

        # Step 3: Transformation
        self.logger.info("Step 3/4: Cleaning and validating data...")

        # Clean data
        projects = self.cleaner.clean_projects(projects)
        self.logger.info("Data cleaning complete")

        # Validate data
        valid_projects, invalid_projects = self.data_validator.validate_projects(projects)
        if invalid_projects:
            self.logger.warning(f"{len(invalid_projects)} projects failed validation")
            for idx, validation_result in invalid_projects:
                for error in validation_result.errors:
                    self.logger.warning(f"  Project {idx}: {error}")
                    result['errors'].append(f"Validation error: {error}")

        self.logger.info(f"Validated {len(valid_projects)} projects")

        # Deduplicate
        if not skip_deduplication:
            self.logger.info("Loading existing hashes for deduplication...")
            self.deduplicator.load_existing_hashes()

            new_projects, duplicate_projects = self.deduplicator.detect_duplicates(valid_projects)

            if duplicate_projects:
                self.logger.warning(f"Skipped {len(duplicate_projects)} duplicate projects")
                duplicate_summary = self.deduplicator.get_duplicate_summary(duplicate_projects)
                self.logger.info(f"Duplicate summary: {duplicate_summary}")

            valid_projects = new_projects
            self.logger.info(f"{len(valid_projects)} new projects after deduplication")

        # Step 4: Loading
        self.logger.info("Step 4/4: Loading data...")

        if valid_projects:
            # Load to Excel
            loaded_count = self.loader.load_projects(valid_projects)
            result['project_count'] = loaded_count
            self.logger.info(f"Loaded {loaded_count} projects to master file")

            # Archive workbook
            archive_path = self.archiver.archive_workbook(
                source_path=file_path,
                business_id=business_id,
                extraction_id=extraction_id,
                submission_date=submission_date
            )
            self.logger.info(f"Archived workbook to: {archive_path}")

        # Write log entry
        business = self.config.get_business_by_id(business_id)
        business_name = business.business_name if business else business_id

        self.log_writer.write_log_entry(
            extraction_id=extraction_id,
            business_id=business_id,
            business_name=business_name,
            workbook_filename=file_path.name,
            project_count=result['project_count'],
            error_count=result['error_count'],
            success_rate=error_collector.success_rate(),
            notes=f"Processed {len(project_sheets)} sheets"
        )

        # Determine final status
        if result['error_count'] == 0:
            result['status'] = 'SUCCESS'
        elif result['project_count'] > 0:
            result['status'] = 'PARTIAL'
        else:
            result['status'] = 'FAILED'

        self.logger.info(f"="*80)
        self.logger.info(f"ETL complete: {result['status']}")
        self.logger.info(f"Projects loaded: {result['project_count']}")
        self.logger.info(f"Errors: {result['error_count']}")
        self.logger.info(f"="*80)

        return result


def main():
    """Command-line interface for ETL consolidator."""
    parser = argparse.ArgumentParser(
        description="AI QSR Consolidator - Extract project data from business unit workbooks"
    )

    parser.add_argument(
        '--file',
        type=str,
        required=True,
        help='Path to Excel workbook'
    )

    parser.add_argument(
        '--business',
        type=str,
        required=True,
        help='Business unit ID (e.g., BU_001)'
    )

    parser.add_argument(
        '--skip-dedup',
        action='store_true',
        help='Skip deduplication (for testing)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )

    args = parser.parse_args()

    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Initialize and run ETL
    try:
        consolidator = AIQSRConsolidator(log_level=args.log_level)
        result = consolidator.process_workbook(
            file_path=file_path,
            business_id=args.business,
            skip_deduplication=args.skip_dedup
        )

        # Print summary
        print("\n" + "="*80)
        print(f"ETL Result: {result['status']}")
        print(f"Extraction ID: {result['extraction_id']}")
        print(f"Projects Loaded: {result['project_count']}")
        print(f"Errors: {result['error_count']}")
        print("="*80)

        if result['errors']:
            print("\nErrors encountered:")
            for error in result['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(result['errors']) > 5:
                print(f"  ... and {len(result['errors']) - 5} more errors")

        # Exit code based on status
        if result['status'] == 'SUCCESS':
            sys.exit(0)
        elif result['status'] == 'PARTIAL':
            sys.exit(2)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
