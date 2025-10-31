"""
Data cleaner for ETL pipeline.
Normalizes and cleans extracted project data.
"""

from typing import Dict, Any, List
from datetime import datetime


class DataCleaner:
    """
    Cleans and normalizes project data after extraction.

    Responsibilities:
    - Standardize None/NaN/empty values to None
    - Trim whitespace from text fields
    - Format dates consistently
    - Remove invalid characters
    - Normalize numeric formats
    """

    def __init__(self):
        """Initialize data cleaner."""
        pass

    def clean_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single project dictionary.

        Args:
            project_data: Raw project data dictionary

        Returns:
            Cleaned project data dictionary
        """
        cleaned = {}

        for key, value in project_data.items():
            cleaned[key] = self._clean_value(value, key)

        return cleaned

    def clean_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean multiple project dictionaries.

        Args:
            projects: List of project data dictionaries

        Returns:
            List of cleaned project data dictionaries
        """
        return [self.clean_project(project) for project in projects]

    def _clean_value(self, value: Any, field_name: str) -> Any:
        """
        Clean a single value based on its type.

        Args:
            value: Value to clean
            field_name: Name of the field (for context)

        Returns:
            Cleaned value
        """
        # Handle None, empty strings, NaN
        if value is None or value == '' or (isinstance(value, float) and value != value):
            return None

        # String cleaning
        if isinstance(value, str):
            value = value.strip()
            return value if value else None

        # Numeric cleaning (already cleaned by helpers.parse_number)
        if isinstance(value, (int, float)):
            return value

        # Date cleaning (already cleaned by helpers.parse_date)
        if isinstance(value, datetime):
            return value

        # Return as-is for other types
        return value

    def standardize_none_values(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize all empty/null values to None.

        Converts: '', NaN, 'N/A', 'null', etc. to None

        Args:
            project_data: Project data dictionary

        Returns:
            Standardized project data dictionary
        """
        null_equivalents = ['', 'N/A', 'n/a', 'NA', 'null', 'NULL', 'None', 'NONE', '-']

        standardized = {}
        for key, value in project_data.items():
            if value in null_equivalents:
                standardized[key] = None
            elif isinstance(value, str) and value.strip() in null_equivalents:
                standardized[key] = None
            else:
                standardized[key] = value

        return standardized

    def remove_extra_whitespace(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove extra whitespace from all text fields.

        - Trim leading/trailing whitespace
        - Replace multiple spaces with single space
        - Remove newlines and tabs

        Args:
            project_data: Project data dictionary

        Returns:
            Cleaned project data dictionary
        """
        import re

        cleaned = {}
        for key, value in project_data.items():
            if isinstance(value, str):
                # Remove newlines and tabs
                value = value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                # Replace multiple spaces with single space
                value = re.sub(r'\s+', ' ', value)
                # Trim
                value = value.strip()
                cleaned[key] = value if value else None
            else:
                cleaned[key] = value

        return cleaned
