"""
Helper utilities for ETL pipeline.
"""

import hashlib
import uuid
from datetime import datetime, date
from typing import Any, Optional, Union
import re


def generate_extraction_id() -> str:
    """
    Generate unique extraction ID (UUID).

    Returns:
        UUID string (e.g., "a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    """
    return str(uuid.uuid4())


def compute_data_hash(business_id: str, project_name: str, week: str) -> str:
    """
    Compute hash for duplicate detection.

    Uses MD5 hash of business_id + project_name + week.
    Note: xxhash would be 10x faster but requires additional dependency.

    Args:
        business_id: Business unit identifier
        project_name: Project name
        week: Submission week in format YYYY-WW

    Returns:
        32-character hexadecimal hash string
    """
    hash_input = f"{business_id}|{project_name}|{week}"
    return hashlib.md5(hash_input.encode('utf-8')).hexdigest()


def get_submission_week(submission_date: Optional[datetime] = None) -> str:
    """
    Get submission week in YYYY-WW format.

    Args:
        submission_date: Submission datetime (default: current datetime)

    Returns:
        Week string (e.g., "2025-43")
    """
    if submission_date is None:
        submission_date = datetime.now()

    # Get ISO week number
    iso_calendar = submission_date.isocalendar()
    year = iso_calendar[0]
    week = iso_calendar[1]

    return f"{year}-{week:02d}"


def parse_date(value: Any) -> Optional[date]:
    """
    Parse date from various formats.

    Handles:
    - Excel serial numbers (days since 1899-12-30)
    - ISO format strings (YYYY-MM-DD)
    - datetime objects
    - None/empty values

    Args:
        value: Date value in various formats

    Returns:
        date object or None if parsing fails
    """
    if value is None or value == '':
        return None

    # Already a date object
    if isinstance(value, date):
        return value

    # datetime object
    if isinstance(value, datetime):
        return value.date()

    # Excel serial number (float or int)
    if isinstance(value, (int, float)):
        try:
            # Excel epoch: 1899-12-30 (note: not 1900-01-01 due to Lotus 1-2-3 bug)
            excel_epoch = datetime(1899, 12, 30)
            return (excel_epoch + pd.Timedelta(days=value)).date()
        except:
            return None

    # String format
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        # Try ISO format (YYYY-MM-DD)
        try:
            return datetime.fromisoformat(value).date()
        except:
            pass

        # Try common formats
        formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%d-%m-%Y'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except:
                continue

    return None


def parse_number(value: Any) -> Optional[float]:
    """
    Parse number from various formats.

    Handles:
    - Integers and floats
    - Numeric strings (with commas removed)
    - None/empty values
    - Excel formulas that evaluate to numbers

    Args:
        value: Numeric value in various formats

    Returns:
        float or None if parsing fails
    """
    if value is None or value == '':
        return None

    # Already a number
    if isinstance(value, (int, float)):
        return float(value)

    # String format
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        # Remove commas and currency symbols
        value = value.replace(',', '').replace('$', '').replace('€', '').replace('£', '')

        try:
            return float(value)
        except ValueError:
            return None

    return None


def clean_text(value: Any) -> Optional[str]:
    """
    Clean text value.

    - Strips whitespace
    - Converts empty strings to None
    - Handles None values

    Args:
        value: Text value

    Returns:
        Cleaned string or None
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    # Convert other types to string
    return str(value)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for Windows/Unix filesystems
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')

    # Limit length to 200 characters
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:190] + (f'.{ext}' if ext else '')

    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_project_sheet_names(max_projects: int = 10) -> list:
    """
    Get expected project sheet names (P1, P2, ..., P10).

    Args:
        max_projects: Maximum number of project sheets (default: 10)

    Returns:
        List of sheet names
    """
    return [f"P{i}" for i in range(1, max_projects + 1)]


def is_project_sheet(sheet_name: str) -> bool:
    """
    Check if sheet name matches project sheet pattern (P1-P10).

    Args:
        sheet_name: Sheet name to check

    Returns:
        True if sheet is a project sheet, False otherwise
    """
    pattern = r'^P([1-9]|10)$'
    return bool(re.match(pattern, sheet_name))


# Note: pandas import for date parsing
try:
    import pandas as pd
except ImportError:
    pd = None
    # Fallback for Excel date parsing without pandas
    def parse_date_fallback(value: Any) -> Optional[date]:
        """Fallback date parser without pandas."""
        if isinstance(value, (int, float)):
            from datetime import timedelta
            excel_epoch = datetime(1899, 12, 30)
            return (excel_epoch + timedelta(days=value)).date()
        return None
