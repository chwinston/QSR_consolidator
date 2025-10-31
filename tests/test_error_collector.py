"""
Tests for ErrorCollector.
"""

import pytest
from src.utils.error_collector import ErrorCollector


def test_error_collector_initialization():
    """Test ErrorCollector initialization."""
    collector = ErrorCollector(partial_success_threshold=0.5)
    assert collector.partial_success_threshold == 0.5
    assert collector.error_count() == 0


def test_add_error():
    """Test adding errors."""
    collector = ErrorCollector()
    collector.add_error(
        component="TestComponent",
        error_type="TestError",
        message="Test error message"
    )
    assert collector.error_count() == 1
    assert collector.has_errors() is True


def test_success_tracking():
    """Test success/failure tracking."""
    collector = ErrorCollector()
    collector.record_success()
    collector.record_success()
    collector.record_failure()

    assert collector.success_count == 2
    assert collector.total_count == 3
    assert collector.success_rate() == pytest.approx(0.667, rel=0.01)


def test_meets_threshold():
    """Test threshold checking."""
    collector = ErrorCollector(partial_success_threshold=0.5)
    collector.record_success()
    collector.record_success()
    collector.record_failure()

    assert collector.meets_threshold() is True

    collector.record_failure()
    collector.record_failure()
    assert collector.meets_threshold() is False


def test_get_summary():
    """Test getting error summary."""
    collector = ErrorCollector()
    collector.record_success()
    collector.record_success()
    collector.record_failure()

    collector.add_error(
        component="Extractor",
        error_type="ExtractionError",
        message="Test error"
    )

    summary = collector.get_summary()
    assert summary['total_operations'] == 3
    assert summary['successful_operations'] == 2
    assert summary['error_count'] == 1
