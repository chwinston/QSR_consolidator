"""
Pytest configuration and shared fixtures for ETL tests.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import ETLLogger


@pytest.fixture
def config_dir():
    """Fixture for config directory."""
    return Path(__file__).parent.parent / "config"


@pytest.fixture
def config_loader(config_dir):
    """Fixture for ConfigLoader with loaded configuration."""
    loader = ConfigLoader(config_dir)
    loader.load_all()
    return loader


@pytest.fixture
def test_logger(tmp_path):
    """Fixture for test logger with temp directory."""
    return ETLLogger(log_dir=str(tmp_path), log_level="DEBUG")


@pytest.fixture
def sample_project_data():
    """Fixture for sample project data dictionary."""
    from datetime import datetime
    return {
        'extraction_id': 'test-12345',
        'business_id': 'BU_001',
        'business_name': 'ClubOS',
        'sheet_name': 'P1',
        'submission_date': datetime(2025, 10, 26),
        'submission_week': '2025-43',
        'workbook_filename': 'test_workbook.xlsx',
        'data_hash': 'abc123',
        'project_name': 'Test Project',
        'project_uuid': 'uuid-1234',
        'project_description': 'Test description',
        'strategic_value': 3,
        'stage_multiplier': 0.6,
        'project_score': 1.8
    }
