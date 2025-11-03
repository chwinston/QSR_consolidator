"""
Configuration loader for ETL pipeline.
Loads field mappings and business unit configurations from CSV files.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FieldMapping:
    """Represents a single field mapping from input Excel to output consolidator."""

    output_column_name: str
    input_row_number: int
    input_column_letter: str
    data_type: str
    is_required: bool
    section: str

    def get_cell_address(self) -> str:
        """Get Excel cell address (e.g., 'C3')."""
        return f"{self.input_column_letter}{self.input_row_number}"


@dataclass
class BusinessUnit:
    """Represents a business unit configuration."""

    business_id: str
    business_name: str
    contact_email: str
    is_active: bool

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'BusinessUnit':
        """Create BusinessUnit from CSV row dictionary."""
        return cls(
            business_id=row['business_id'],
            business_name=row['business_name'],
            contact_email=row['contact_email'],
            is_active=row['is_active'].lower() in ('true', '1', 'yes')
        )


class ConfigLoader:
    """
    Loads and manages ETL configuration from CSV files.

    Configuration files:
    - field_mapping.csv: Defines 76 fields to extract from Excel sheets
    - businesses.csv: Defines 30 business units and their contact info
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            config_dir: Path to config directory (default: ./config)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_dir = Path(config_dir)

        self.field_mappings: List[FieldMapping] = []
        self.businesses: Dict[str, BusinessUnit] = {}
        self.email_to_business: Dict[str, str] = {}

    def load_field_mappings(self, file_path: Optional[Path] = None) -> List[FieldMapping]:
        """
        Load field mappings from CSV file.

        Args:
            file_path: Path to field_mapping.csv (default: config/field_mapping.csv)

        Returns:
            List of FieldMapping objects

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If CSV format is invalid
        """
        if file_path is None:
            file_path = self.config_dir / "field_mapping.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Field mapping file not found: {file_path}")

        self.field_mappings = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Handle generated fields (row_number may be empty or '0')
                    row_num_str = row['input_row_number'].strip()
                    input_row_number = int(row_num_str) if row_num_str else 0

                    mapping = FieldMapping(
                        output_column_name=row['output_column_name'],
                        input_row_number=input_row_number,
                        input_column_letter=row['input_column_letter'],
                        data_type=row['data_type'],
                        is_required=row['is_required'].lower() in ('true', '1', 'yes'),
                        section=row['section']
                    )
                    self.field_mappings.append(mapping)
                except (KeyError, ValueError) as e:
                    raise ValueError(f"Invalid field mapping row: {row}") from e

        return self.field_mappings

    def load_businesses(self, file_path: Optional[Path] = None) -> Dict[str, BusinessUnit]:
        """
        Load business unit configurations from CSV file.

        Args:
            file_path: Path to businesses.csv (default: config/businesses.csv)

        Returns:
            Dictionary mapping business_id to BusinessUnit

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If CSV format is invalid
        """
        if file_path is None:
            file_path = self.config_dir / "businesses.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Businesses file not found: {file_path}")

        self.businesses = {}
        self.email_to_business = {}

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    business = BusinessUnit.from_csv_row(row)
                    self.businesses[business.business_id] = business

                    # Create email lookup (support comma-separated emails)
                    emails = [e.strip() for e in business.contact_email.split(',')]
                    for email in emails:
                        self.email_to_business[email.lower()] = business.business_id

                except (KeyError, ValueError) as e:
                    raise ValueError(f"Invalid business row: {row}") from e

        return self.businesses

    def get_field_mapping_by_name(self, field_name: str) -> Optional[FieldMapping]:
        """Get field mapping by output column name."""
        for mapping in self.field_mappings:
            if mapping.output_column_name == field_name:
                return mapping
        return None

    def get_required_fields(self) -> List[FieldMapping]:
        """Get all required field mappings."""
        return [m for m in self.field_mappings if m.is_required]

    def get_fields_by_section(self, section: str) -> List[FieldMapping]:
        """Get all field mappings for a specific section."""
        return [m for m in self.field_mappings if m.section == section]

    def get_business_by_id(self, business_id: str) -> Optional[BusinessUnit]:
        """Get business unit by ID."""
        return self.businesses.get(business_id)

    def get_business_by_email(self, email: str) -> Optional[BusinessUnit]:
        """
        Get business unit by contact email.

        Args:
            email: Contact email address

        Returns:
            BusinessUnit if found, None otherwise
        """
        business_id = self.email_to_business.get(email.lower())
        if business_id:
            return self.businesses.get(business_id)
        return None

    def get_active_businesses(self) -> List[BusinessUnit]:
        """Get all active business units."""
        return [b for b in self.businesses.values() if b.is_active]

    def validate_config(self) -> bool:
        """
        Validate loaded configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Check field mappings exist
        if not self.field_mappings:
            return False

        # Check expected field count (91 fields: 76 original + 12 milestone notes + 3 KPI notes)
        if len(self.field_mappings) != 91:
            return False

        # Check at least one required field
        required_fields = self.get_required_fields()
        if not required_fields:
            return False

        # Check businesses exist
        if not self.businesses:
            return False

        # Check expected business count (30 businesses)
        if len(self.businesses) != 30:
            return False

        return True

    def load_all(self) -> bool:
        """
        Load all configuration files.

        Returns:
            True if all configs loaded successfully, False otherwise
        """
        try:
            self.load_field_mappings()
            self.load_businesses()
            return self.validate_config()
        except (FileNotFoundError, ValueError):
            return False

    def __repr__(self) -> str:
        """String representation of ConfigLoader."""
        return (
            f"ConfigLoader(field_mappings={len(self.field_mappings)}, "
            f"businesses={len(self.businesses)})"
        )
