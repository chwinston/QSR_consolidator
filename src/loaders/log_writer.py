"""
Log writer for ETL pipeline.
Writes extraction audit trail to CSV log file.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import csv
from src.utils.logger import ETLLogger


class LogWriter:
    """
    Writes extraction logs to CSV file for audit trail.

    Log format:
    - extraction_id
    - timestamp
    - business_id
    - business_name
    - workbook_filename
    - project_count
    - error_count
    - success_rate
    - status (SUCCESS, PARTIAL, FAILED)
    """

    def __init__(
        self,
        log_file_path: Path,
        logger: ETLLogger = None
    ):
        """
        Initialize log writer.

        Args:
            log_file_path: Path to extraction log CSV file
            logger: ETLLogger instance
        """
        self.log_file_path = Path(log_file_path)
        self.logger = logger or ETLLogger()

        # Ensure parent directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create log file with headers if it doesn't exist
        if not self.log_file_path.exists():
            self._create_log_file()

    def _create_log_file(self) -> None:
        """Create log file with headers."""
        headers = [
            'extraction_id',
            'timestamp',
            'business_id',
            'business_name',
            'workbook_filename',
            'project_count',
            'error_count',
            'success_rate',
            'status',
            'notes'
        ]

        with open(self.log_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

        self.logger.info(f"Created extraction log file: {self.log_file_path}")

    def write_log_entry(
        self,
        extraction_id: str,
        business_id: str,
        business_name: str,
        workbook_filename: str,
        project_count: int,
        error_count: int,
        success_rate: float,
        notes: str = ""
    ) -> None:
        """
        Write a log entry for an extraction run.

        Args:
            extraction_id: Unique extraction ID
            business_id: Business unit identifier
            business_name: Business unit name
            workbook_filename: Name of processed workbook
            project_count: Number of projects extracted
            error_count: Number of errors encountered
            success_rate: Success rate (0.0-1.0)
            notes: Additional notes (optional)
        """
        # Determine status
        if error_count == 0:
            status = "SUCCESS"
        elif project_count > 0:
            status = "PARTIAL"
        else:
            status = "FAILED"

        entry = {
            'extraction_id': extraction_id,
            'timestamp': datetime.now().isoformat(),
            'business_id': business_id,
            'business_name': business_name,
            'workbook_filename': workbook_filename,
            'project_count': project_count,
            'error_count': error_count,
            'success_rate': f"{success_rate:.2%}",
            'status': status,
            'notes': notes
        }

        try:
            with open(self.log_file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=entry.keys())
                writer.writerow(entry)

            self.logger.debug(f"Wrote log entry: {extraction_id} - {status}")

        except Exception as e:
            self.logger.error(f"Failed to write log entry: {str(e)}")

    def get_recent_logs(self, count: int = 10) -> list:
        """
        Get recent log entries.

        Args:
            count: Number of recent entries to return

        Returns:
            List of log entry dictionaries
        """
        if not self.log_file_path.exists():
            return []

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                logs = list(reader)
                return logs[-count:] if len(logs) > count else logs

        except Exception as e:
            self.logger.error(f"Failed to read log entries: {str(e)}")
            return []

    def get_logs_for_business(self, business_id: str) -> list:
        """
        Get all log entries for a specific business.

        Args:
            business_id: Business unit identifier

        Returns:
            List of log entry dictionaries
        """
        if not self.log_file_path.exists():
            return []

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row for row in reader if row['business_id'] == business_id]

        except Exception as e:
            self.logger.error(f"Failed to read log entries: {str(e)}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get extraction statistics.

        Returns:
            Dictionary with statistics (total runs, success rate, etc.)
        """
        if not self.log_file_path.exists():
            return {}

        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                logs = list(reader)

            if not logs:
                return {}

            total_runs = len(logs)
            successful = sum(1 for log in logs if log['status'] == 'SUCCESS')
            partial = sum(1 for log in logs if log['status'] == 'PARTIAL')
            failed = sum(1 for log in logs if log['status'] == 'FAILED')

            total_projects = sum(int(log['project_count']) for log in logs)
            total_errors = sum(int(log['error_count']) for log in logs)

            return {
                'total_runs': total_runs,
                'successful_runs': successful,
                'partial_runs': partial,
                'failed_runs': failed,
                'success_rate': successful / total_runs if total_runs > 0 else 0,
                'total_projects_extracted': total_projects,
                'total_errors': total_errors
            }

        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {str(e)}")
            return {}
