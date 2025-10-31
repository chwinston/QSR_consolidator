"""
Excel loader for ETL pipeline.
Appends project data to master consolidator Excel file.
"""

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from src.utils.logger import ETLLogger


class ExcelLoader:
    """
    Loads project data into master Excel consolidator file.

    Responsibilities:
    - Create master file if it doesn't exist
    - Append new projects without overwriting history
    - Maintain proper column structure
    - Handle file locking gracefully
    """

    def __init__(
        self,
        master_file_path: Path,
        logger: ETLLogger = None
    ):
        """
        Initialize Excel loader.

        Args:
            master_file_path: Path to master consolidator Excel file
            logger: ETLLogger instance
        """
        self.master_file_path = Path(master_file_path)
        self.logger = logger or ETLLogger()

    def load_projects(
        self,
        projects: List[Dict[str, Any]],
        create_if_missing: bool = True
    ) -> int:
        """
        Append projects to master Excel file.

        Args:
            projects: List of project dictionaries
            create_if_missing: Create master file if it doesn't exist

        Returns:
            Number of projects successfully loaded

        Raises:
            FileNotFoundError: If master file doesn't exist and create_if_missing=False
            PermissionError: If file is locked
        """
        if not projects:
            self.logger.info("No projects to load")
            return 0

        # Convert to DataFrame
        df_new = pd.DataFrame(projects)

        # Ensure parent directory exists
        self.master_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load or create master file
        if self.master_file_path.exists():
            df_existing = self._load_existing_master()
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            if not create_if_missing:
                raise FileNotFoundError(f"Master file not found: {self.master_file_path}")
            self.logger.info("Creating new master file")
            df_combined = df_new

        # Write to Excel
        try:
            df_combined.to_excel(
                self.master_file_path,
                index=False,
                engine='openpyxl'
            )
            self.logger.info(f"Loaded {len(projects)} projects to master file")
            return len(projects)

        except PermissionError as e:
            self.logger.error(f"Cannot write to master file - file may be open in Excel: {str(e)}")
            raise

    def _load_existing_master(self) -> pd.DataFrame:
        """
        Load existing master file.

        Returns:
            DataFrame with existing data
        """
        try:
            df = pd.read_excel(self.master_file_path, engine='openpyxl')
            self.logger.info(f"Loaded {len(df)} existing rows from master file")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load existing master file: {str(e)}")
            raise

    def get_row_count(self) -> int:
        """
        Get total row count in master file.

        Returns:
            Number of rows (excluding header)
        """
        if not self.master_file_path.exists():
            return 0

        try:
            df = pd.read_excel(self.master_file_path, engine='openpyxl')
            return len(df)
        except Exception as e:
            self.logger.error(f"Failed to get row count: {str(e)}")
            return 0

    def create_empty_master(self, columns: List[str]) -> None:
        """
        Create empty master file with specified columns.

        Args:
            columns: List of column names
        """
        df = pd.DataFrame(columns=columns)
        self.master_file_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(
            self.master_file_path,
            index=False,
            engine='openpyxl'
        )
        self.logger.info(f"Created empty master file with {len(columns)} columns")
