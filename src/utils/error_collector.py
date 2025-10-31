"""
Error Collector for ETL Pipeline
Aggregates errors without stopping the entire process.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import traceback


@dataclass
class ETLError:
    """Represents a single error in the ETL pipeline."""

    timestamp: datetime
    component: str
    error_type: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/reporting."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'component': self.component,
            'error_type': self.error_type,
            'message': self.message,
            'context': self.context,
            'traceback': self.traceback
        }

    def __str__(self) -> str:
        """Human-readable error representation."""
        return (
            f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{self.component} - {self.error_type}: {self.message}"
        )


class ErrorCollector:
    """
    Collects errors during ETL pipeline execution without stopping the process.

    Usage:
        collector = ErrorCollector()
        try:
            # ... operation ...
        except Exception as e:
            collector.add_error(
                component="ProjectExtractor",
                error_type="FieldExtractionError",
                message=str(e),
                context={'sheet': 'P1', 'field': 'project_name'}
            )
    """

    def __init__(self, partial_success_threshold: float = 0.5):
        """
        Initialize error collector.

        Args:
            partial_success_threshold: Minimum success rate (0.0-1.0) to accept partial results.
                                      Default 0.5 means 50% success required.
        """
        self.errors: List[ETLError] = []
        self.partial_success_threshold = partial_success_threshold
        self.success_count = 0
        self.total_count = 0

    def add_error(
        self,
        component: str,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Add an error to the collection.

        Args:
            component: Name of component where error occurred (e.g., "ProjectExtractor")
            error_type: Type of error (e.g., "FieldExtractionError")
            message: Human-readable error message
            context: Additional context (sheet name, field name, etc.)
            exception: Original exception if available (for traceback)
        """
        error = ETLError(
            timestamp=datetime.now(),
            component=component,
            error_type=error_type,
            message=message,
            context=context or {},
            traceback=traceback.format_exc() if exception else None
        )
        self.errors.append(error)

    def record_success(self) -> None:
        """Record a successful operation."""
        self.success_count += 1
        self.total_count += 1

    def record_failure(self) -> None:
        """Record a failed operation."""
        self.total_count += 1

    def has_errors(self) -> bool:
        """Check if any errors have been collected."""
        return len(self.errors) > 0

    def error_count(self) -> int:
        """Get total number of errors."""
        return len(self.errors)

    def success_rate(self) -> float:
        """
        Calculate success rate.

        Returns:
            Success rate as float (0.0-1.0), or 1.0 if no operations recorded.
        """
        if self.total_count == 0:
            return 1.0
        return self.success_count / self.total_count

    def meets_threshold(self) -> bool:
        """
        Check if success rate meets the partial success threshold.

        Returns:
            True if success rate >= threshold, False otherwise.
        """
        return self.success_rate() >= self.partial_success_threshold

    def get_errors_by_component(self, component: str) -> List[ETLError]:
        """Get all errors from a specific component."""
        return [e for e in self.errors if e.component == component]

    def get_errors_by_type(self, error_type: str) -> List[ETLError]:
        """Get all errors of a specific type."""
        return [e for e in self.errors if e.error_type == error_type]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors and success metrics.

        Returns:
            Dictionary with error counts, success rate, and threshold status.
        """
        return {
            'total_operations': self.total_count,
            'successful_operations': self.success_count,
            'failed_operations': self.total_count - self.success_count,
            'error_count': self.error_count(),
            'success_rate': self.success_rate(),
            'threshold': self.partial_success_threshold,
            'meets_threshold': self.meets_threshold(),
            'errors_by_component': self._group_errors_by_component(),
            'errors_by_type': self._group_errors_by_type()
        }

    def _group_errors_by_component(self) -> Dict[str, int]:
        """Group error counts by component."""
        counts = {}
        for error in self.errors:
            counts[error.component] = counts.get(error.component, 0) + 1
        return counts

    def _group_errors_by_type(self) -> Dict[str, int]:
        """Group error counts by error type."""
        counts = {}
        for error in self.errors:
            counts[error.error_type] = counts.get(error.error_type, 0) + 1
        return counts

    def get_all_errors(self) -> List[ETLError]:
        """Get all errors in chronological order."""
        return self.errors

    def clear(self) -> None:
        """Clear all errors and reset counters."""
        self.errors = []
        self.success_count = 0
        self.total_count = 0

    def format_for_email(self) -> str:
        """
        Format errors for email notification.

        Returns:
            Human-readable formatted string of all errors.
        """
        if not self.has_errors():
            return "No errors occurred."

        lines = [
            f"Total Errors: {self.error_count()}",
            f"Success Rate: {self.success_rate():.1%}",
            f"Meets Threshold ({self.partial_success_threshold:.0%}): {self.meets_threshold()}",
            "",
            "Error Details:",
            "=" * 80
        ]

        for i, error in enumerate(self.errors, 1):
            lines.append(f"\nError {i}:")
            lines.append(f"  Time: {error.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"  Component: {error.component}")
            lines.append(f"  Type: {error.error_type}")
            lines.append(f"  Message: {error.message}")

            if error.context:
                lines.append(f"  Context: {error.context}")

            if error.traceback:
                lines.append(f"  Traceback:")
                for line in error.traceback.split('\n'):
                    if line.strip():
                        lines.append(f"    {line}")

        return '\n'.join(lines)

    def __repr__(self) -> str:
        """String representation of ErrorCollector."""
        return (
            f"ErrorCollector(errors={self.error_count()}, "
            f"success_rate={self.success_rate():.1%}, "
            f"meets_threshold={self.meets_threshold()})"
        )
