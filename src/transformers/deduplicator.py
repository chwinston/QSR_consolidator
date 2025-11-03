"""
Deduplicator for ETL pipeline.
Detects and handles duplicate project submissions using hash-based approach.
"""

from typing import Dict, Any, List, Set, Tuple
from src.utils.logger import ETLLogger
from pathlib import Path
import csv


class Deduplicator:
    """
    Detects duplicate submissions using data hash.

    Hash key: business_id + project_name + submission_week
    - Allows same project tracked week-over-week as separate entries
    - Prevents duplicate submissions within same week
    """

    def __init__(
        self,
        master_file_path: Path,
        logger: ETLLogger = None
    ):
        """
        Initialize deduplicator.

        Args:
            master_file_path: Path to master consolidator Excel file
            logger: ETLLogger instance
        """
        self.master_file_path = master_file_path
        self.logger = logger or ETLLogger()
        self.existing_hashes: Set[str] = set()

    def load_existing_hashes(self) -> int:
        """
        Load existing data hashes from master file.

        Returns:
            Number of hashes loaded
        """
        import pandas as pd

        if not self.master_file_path.exists():
            self.logger.info("Master file does not exist yet. No hashes to load.")
            return 0

        try:
            # Read master file
            df = pd.read_excel(self.master_file_path, engine='openpyxl')

            # Extract data_hash column
            if 'data_hash' in df.columns:
                self.existing_hashes = set(df['data_hash'].dropna().tolist())
                self.logger.info(f"Loaded {len(self.existing_hashes)} existing hashes from master file")
                return len(self.existing_hashes)
            else:
                self.logger.warning("Master file does not have 'data_hash' column")
                return 0

        except Exception as e:
            self.logger.error(f"Failed to load existing hashes: {str(e)}")
            return 0

    def detect_duplicates(
        self,
        projects: List[Dict[str, Any]],
        mark_only: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect duplicate projects.

        Args:
            projects: List of project dictionaries with 'data_hash' field
            mark_only: If True, mark duplicates but return all projects. If False, filter duplicates.

        Returns:
            Tuple of (new_projects, duplicate_projects)
            - new_projects: Projects that are not duplicates (or all projects if mark_only=True)
            - duplicate_projects: Projects that are duplicates (for logging only if mark_only=True)
        """
        new_projects = []
        duplicate_projects = []

        for project in projects:
            data_hash = project.get('data_hash')

            if not data_hash:
                # No hash - cannot deduplicate, treat as new
                self.logger.warning(
                    f"Project missing data_hash: {project.get('project_name', 'Unknown')}"
                )
                project['is_duplicate'] = False
                new_projects.append(project)
                continue

            if data_hash in self.existing_hashes:
                # Duplicate detected
                self.logger.log_duplicate_detected(
                    business_id=project.get('business_id', 'Unknown'),
                    project_name=project.get('project_name', 'Unknown'),
                    week=project.get('submission_week', 'Unknown')
                )
                project['is_duplicate'] = True
                duplicate_projects.append(project)

                if mark_only:
                    # Mark as duplicate but still include in results
                    new_projects.append(project)
            else:
                # New project
                project['is_duplicate'] = False
                new_projects.append(project)
                # Add to existing hashes to detect duplicates within same batch
                self.existing_hashes.add(data_hash)

        if mark_only:
            self.logger.info(
                f"Deduplication complete: {len(new_projects)} total projects, {len(duplicate_projects)} marked as duplicates (but still included)"
            )
        else:
            self.logger.info(
                f"Deduplication complete: {len(new_projects)} new, {len(duplicate_projects)} duplicates filtered"
            )

        return (new_projects, duplicate_projects)

    def get_duplicate_summary(
        self,
        duplicate_projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate summary of duplicate projects.

        Args:
            duplicate_projects: List of duplicate project dictionaries

        Returns:
            Summary dictionary with counts by business and project
        """
        summary = {
            'total_duplicates': len(duplicate_projects),
            'by_business': {},
            'by_project': {}
        }

        for project in duplicate_projects:
            business_id = project.get('business_id', 'Unknown')
            project_name = project.get('project_name', 'Unknown')

            # Count by business
            summary['by_business'][business_id] = summary['by_business'].get(business_id, 0) + 1

            # Count by project
            key = f"{business_id}:{project_name}"
            summary['by_project'][key] = summary['by_project'].get(key, 0) + 1

        return summary

    def clear_cache(self) -> None:
        """Clear in-memory hash cache."""
        self.existing_hashes.clear()
