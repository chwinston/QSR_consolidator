"""
Archive manager for ETL pipeline.
Archives original submitted workbooks with proper naming.
"""

from pathlib import Path
from datetime import datetime
import shutil
from typing import Optional
from src.utils.logger import ETLLogger
from src.utils.helpers import sanitize_filename


class ArchiveManager:
    """
    Manages archival of original submitted workbooks.

    Naming convention: {business_id}_{submission_date}_{extraction_id}.xlsx
    Example: BU_001_2025-10-26_a1b2c3d4.xlsx
    """

    def __init__(
        self,
        archive_dir: Path,
        logger: ETLLogger = None
    ):
        """
        Initialize archive manager.

        Args:
            archive_dir: Directory for archived files
            logger: ETLLogger instance
        """
        self.archive_dir = Path(archive_dir)
        self.logger = logger or ETLLogger()

        # Ensure archive directory exists
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_workbook(
        self,
        source_path: Path,
        business_id: str,
        extraction_id: str,
        submission_date: Optional[datetime] = None
    ) -> Path:
        """
        Archive a workbook with standardized naming.

        Args:
            source_path: Path to original workbook
            business_id: Business unit identifier
            extraction_id: Unique extraction ID
            submission_date: Submission datetime (default: current datetime)

        Returns:
            Path to archived file

        Raises:
            FileNotFoundError: If source file doesn't exist
            PermissionError: If cannot copy file
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if submission_date is None:
            submission_date = datetime.now()

        # Generate archive filename
        date_str = submission_date.strftime('%Y-%m-%d')
        # Extract first 8 characters of extraction_id for shorter filename
        short_id = extraction_id[:8]
        extension = source_path.suffix

        archive_filename = f"{business_id}_{date_str}_{short_id}{extension}"
        archive_filename = sanitize_filename(archive_filename)

        archive_path = self.archive_dir / archive_filename

        # Copy file to archive
        try:
            shutil.copy2(source_path, archive_path)
            self.logger.log_file_archived(
                original_path=str(source_path),
                archive_path=str(archive_path)
            )
            return archive_path

        except Exception as e:
            self.logger.error(f"Failed to archive workbook: {str(e)}")
            raise

    def get_archived_files(self, business_id: Optional[str] = None) -> list:
        """
        Get list of archived files.

        Args:
            business_id: Filter by business ID (optional)

        Returns:
            List of archived file paths
        """
        if business_id:
            pattern = f"{business_id}_*.xlsx"
        else:
            pattern = "*.xlsx"

        archived_files = sorted(self.archive_dir.glob(pattern))
        return archived_files

    def get_archive_size(self) -> int:
        """
        Get total size of archive directory in bytes.

        Returns:
            Total size in bytes
        """
        total_size = 0
        for file_path in self.archive_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size

    def cleanup_old_archives(self, days_to_keep: int = 90) -> int:
        """
        Delete archives older than specified days.

        Args:
            days_to_keep: Number of days to retain archives

        Returns:
            Number of files deleted
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0

        for file_path in self.archive_dir.rglob('*.xlsx'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old archive: {file_path.name}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {file_path.name}: {str(e)}")

        self.logger.info(f"Cleanup complete: deleted {deleted_count} old archives")
        return deleted_count
