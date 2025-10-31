"""
Tests for ConfigLoader.
"""

import pytest
from pathlib import Path
from src.utils.config_loader import ConfigLoader


def test_config_loader_initialization(config_dir):
    """Test ConfigLoader initialization."""
    loader = ConfigLoader(config_dir)
    assert loader.config_dir == config_dir


def test_load_field_mappings(config_loader):
    """Test loading field mappings."""
    assert len(config_loader.field_mappings) == 76
    assert all(mapping.output_column_name for mapping in config_loader.field_mappings)


def test_load_businesses(config_loader):
    """Test loading business units."""
    assert len(config_loader.businesses) == 30
    assert 'BU_001' in config_loader.businesses
    assert config_loader.businesses['BU_001'].business_name == 'ClubOS'


def test_get_required_fields(config_loader):
    """Test getting required fields."""
    required = config_loader.get_required_fields()
    assert len(required) > 0
    assert all(field.is_required for field in required)


def test_get_business_by_email(config_loader):
    """Test getting business by email."""
    business = config_loader.get_business_by_email('clubos@example.com')
    assert business is not None
    assert business.business_id == 'BU_001'


def test_validate_config(config_loader):
    """Test config validation."""
    assert config_loader.validate_config() is True
