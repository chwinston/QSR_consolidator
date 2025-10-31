"""
Data validator for ETL pipeline.
Validates project data against business rules.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, date


class ValidationResult:
    """Represents the result of a validation check."""

    def __init__(self, is_valid: bool, errors: List[str] = None):
        """
        Initialize validation result.

        Args:
            is_valid: Whether validation passed
            errors: List of error messages (if validation failed)
        """
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error_message: str) -> None:
        """Add an error message."""
        self.errors.append(error_message)
        self.is_valid = False

    def __bool__(self) -> bool:
        """Allow validation result to be used as boolean."""
        return self.is_valid


class DataValidator:
    """
    Validates project data against business rules.

    Validation checks:
    - Required fields present
    - Data types correct
    - Value ranges valid
    - Business logic constraints
    """

    def __init__(self):
        """Initialize data validator."""
        pass

    def validate_project(self, project_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single project dictionary.

        Args:
            project_data: Project data dictionary

        Returns:
            ValidationResult with is_valid and error messages
        """
        result = ValidationResult(is_valid=True)

        # Required fields validation
        self._validate_required_fields(project_data, result)

        # Data type validation
        self._validate_data_types(project_data, result)

        # Business logic validation
        self._validate_business_logic(project_data, result)

        return result

    def validate_projects(
        self,
        projects: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Tuple[int, ValidationResult]]]:
        """
        Validate multiple projects.

        Args:
            projects: List of project dictionaries

        Returns:
            Tuple of (valid_projects, invalid_projects_with_errors)
            - valid_projects: List of projects that passed validation
            - invalid_projects_with_errors: List of (index, ValidationResult) for failed projects
        """
        valid = []
        invalid = []

        for i, project in enumerate(projects):
            result = self.validate_project(project)
            if result.is_valid:
                valid.append(project)
            else:
                invalid.append((i, result))

        return (valid, invalid)

    def _validate_required_fields(
        self,
        project_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate required fields are present and not empty."""
        required_fields = ['project_name', 'project_uuid', 'business_id']

        for field in required_fields:
            if field not in project_data:
                result.add_error(f"Required field missing: {field}")
            elif project_data[field] is None or project_data[field] == '':
                result.add_error(f"Required field is empty: {field}")

    def _validate_data_types(
        self,
        project_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate data types are correct."""
        # Date fields
        date_fields = [
            'submission_date',
            'milestone1_target_date', 'milestone1_completion_date',
            'milestone2_target_date', 'milestone2_completion_date',
            'milestone3_target_date', 'milestone3_completion_date',
            'milestone4_target_date', 'milestone4_completion_date',
            'milestone5_target_date', 'milestone5_completion_date',
            'milestone6_target_date', 'milestone6_completion_date',
            'milestone7_target_date', 'milestone7_completion_date',
            'milestone8_target_date', 'milestone8_completion_date',
            'milestone9_target_date', 'milestone9_completion_date',
            'milestone10_target_date', 'milestone10_completion_date',
            'milestone11_target_date', 'milestone11_completion_date',
            'milestone12_target_date', 'milestone12_completion_date'
        ]

        for field in date_fields:
            if field in project_data and project_data[field] is not None:
                if not isinstance(project_data[field], (datetime, date)):
                    result.add_error(f"Field '{field}' must be a date, got {type(project_data[field])}")

        # Numeric fields
        numeric_fields = [
            'kpi1_target', 'kpi1_actual', 'kpi1_delta',
            'kpi2_target', 'kpi2_actual', 'kpi2_delta',
            'kpi3_target', 'kpi3_actual', 'kpi3_delta',
            'strategic_value', 'stage_multiplier', 'project_score', 'total_project_score'
        ]

        for field in numeric_fields:
            if field in project_data and project_data[field] is not None:
                if not isinstance(project_data[field], (int, float)):
                    result.add_error(f"Field '{field}' must be numeric, got {type(project_data[field])}")

    def _validate_business_logic(
        self,
        project_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate business logic constraints."""
        # Project name length
        if 'project_name' in project_data and project_data['project_name']:
            if len(project_data['project_name']) > 200:
                result.add_error("Project name exceeds 200 characters")

        # Strategic value (should be positive number, actual template uses 100-200 range)
        if 'strategic_value' in project_data and project_data['strategic_value'] is not None:
            if project_data['strategic_value'] < 0:
                result.add_error(f"Strategic value must be positive, got {project_data['strategic_value']}")

        # Stage multiplier (should be positive number, actual template uses decimal values)
        if 'stage_multiplier' in project_data and project_data['stage_multiplier'] is not None:
            if project_data['stage_multiplier'] < 0:
                result.add_error(f"Stage multiplier must be positive, got {project_data['stage_multiplier']}")

        # Milestone dates logic (completion should be after target if both present)
        for i in range(1, 13):
            target_field = f'milestone{i}_target_date'
            completion_field = f'milestone{i}_completion_date'

            if (target_field in project_data and completion_field in project_data and
                project_data[target_field] is not None and project_data[completion_field] is not None):

                target_date = project_data[target_field]
                completion_date = project_data[completion_field]

                # Both should be dates
                if isinstance(target_date, (datetime, date)) and isinstance(completion_date, (datetime, date)):
                    # Warning if completion is way before target (might indicate data issue)
                    if isinstance(target_date, datetime):
                        target_date = target_date.date()
                    if isinstance(completion_date, datetime):
                        completion_date = completion_date.date()

                    days_diff = (completion_date - target_date).days
                    if days_diff < -365:  # More than 1 year early
                        result.add_error(f"Milestone {i}: completion date is >1 year before target (possible data error)")
