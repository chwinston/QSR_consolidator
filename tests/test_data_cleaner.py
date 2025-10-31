"""
Tests for DataCleaner.
"""

import pytest
from src.transformers.data_cleaner import DataCleaner


def test_clean_value_text():
    """Test cleaning text values."""
    cleaner = DataCleaner()

    assert cleaner._clean_value("  test  ", "field") == "test"
    assert cleaner._clean_value("", "field") is None
    assert cleaner._clean_value(None, "field") is None


def test_clean_value_numbers():
    """Test cleaning numeric values."""
    cleaner = DataCleaner()

    assert cleaner._clean_value(123, "field") == 123
    assert cleaner._clean_value(45.67, "field") == 45.67


def test_standardize_none_values():
    """Test standardizing null values."""
    cleaner = DataCleaner()
    project = {
        'field1': 'N/A',
        'field2': '',
        'field3': 'valid_value',
        'field4': 'null'
    }

    result = cleaner.standardize_none_values(project)

    assert result['field1'] is None
    assert result['field2'] is None
    assert result['field3'] == 'valid_value'
    assert result['field4'] is None


def test_remove_extra_whitespace():
    """Test removing extra whitespace."""
    cleaner = DataCleaner()
    project = {
        'field1': '  multiple   spaces  ',
        'field2': 'newline\nhere',
        'field3': 123
    }

    result = cleaner.remove_extra_whitespace(project)

    assert result['field1'] == 'multiple spaces'
    assert result['field2'] == 'newline here'
    assert result['field3'] == 123
