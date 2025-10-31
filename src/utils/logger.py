"""
Logger utility for ETL pipeline.
Provides structured logging with daily rotation and multiple output targets.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = "ai_qsr_etl",
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    console_output: bool = True
) -> logging.Logger:
    """
    Set up logger with file and console handlers.

    Args:
        name: Logger name
        log_dir: Directory for log files (default: ./data/logs)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.handlers.clear()  # Remove existing handlers

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with daily rotation
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "data" / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"etl_{datetime.now().strftime('%Y%m%d')}.log"

    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


class ETLLogger:
    """
    Wrapper class for structured ETL logging.

    Provides convenience methods for common logging patterns.
    """

    def __init__(
        self,
        logger_name: str = "ai_qsr_etl",
        log_dir: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize ETL logger.

        Args:
            logger_name: Name of the logger
            log_dir: Directory for log files
            log_level: Logging level
        """
        self.logger = setup_logger(logger_name, log_dir, log_level)

    def log_extraction_start(
        self,
        extraction_id: str,
        business_id: str,
        file_path: str
    ) -> None:
        """Log start of extraction process."""
        self.logger.info(
            f"Starting extraction | ID: {extraction_id} | "
            f"Business: {business_id} | File: {file_path}"
        )

    def log_extraction_complete(
        self,
        extraction_id: str,
        project_count: int,
        error_count: int
    ) -> None:
        """Log completion of extraction process."""
        status = "SUCCESS" if error_count == 0 else "PARTIAL" if project_count > 0 else "FAILED"
        self.logger.info(
            f"Extraction complete | ID: {extraction_id} | "
            f"Status: {status} | Projects: {project_count} | Errors: {error_count}"
        )

    def log_field_extraction(
        self,
        sheet_name: str,
        field_name: str,
        value: any,
        success: bool = True
    ) -> None:
        """Log field extraction (DEBUG level)."""
        if success:
            self.logger.debug(
                f"Field extracted | Sheet: {sheet_name} | "
                f"Field: {field_name} | Value: {value}"
            )
        else:
            self.logger.warning(
                f"Field extraction failed | Sheet: {sheet_name} | Field: {field_name}"
            )

    def log_validation_error(
        self,
        validation_type: str,
        error_message: str,
        context: dict
    ) -> None:
        """Log validation error."""
        self.logger.error(
            f"Validation failed | Type: {validation_type} | "
            f"Error: {error_message} | Context: {context}"
        )

    def log_duplicate_detected(
        self,
        business_id: str,
        project_name: str,
        week: str
    ) -> None:
        """Log duplicate submission detection."""
        self.logger.warning(
            f"Duplicate detected | Business: {business_id} | "
            f"Project: {project_name} | Week: {week}"
        )

    def log_file_archived(
        self,
        original_path: str,
        archive_path: str
    ) -> None:
        """Log file archival."""
        self.logger.info(
            f"File archived | Original: {original_path} | Archive: {archive_path}"
        )

    def log_error(
        self,
        component: str,
        error_type: str,
        error_message: str,
        **kwargs
    ) -> None:
        """Log generic error with context."""
        context_str = " | ".join(f"{k}: {v}" for k, v in kwargs.items())
        self.logger.error(
            f"Error in {component} | Type: {error_type} | "
            f"Message: {error_message} | {context_str}"
        )

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
