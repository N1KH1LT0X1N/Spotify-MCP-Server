"""
Core logging functionality for Spotify MCP Server.

Provides structured logging with JSON formatting, correlation IDs,
and contextual information for production monitoring.
"""

import logging
import json
import sys
import uuid
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from contextlib import contextmanager
from pathlib import Path


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Thread-local storage for correlation IDs and context
_thread_local = threading.local()


def _get_correlation_id() -> str:
    """Get or create correlation ID for current thread."""
    if not hasattr(_thread_local, 'correlation_id'):
        _thread_local.correlation_id = str(uuid.uuid4())
    return _thread_local.correlation_id


def _get_context() -> Dict[str, Any]:
    """Get context dictionary for current thread."""
    if not hasattr(_thread_local, 'context'):
        _thread_local.context = {}
    return _thread_local.context


def set_correlation_id(correlation_id: str):
    """
    Set correlation ID for current thread.

    Args:
        correlation_id: Correlation ID to use
    """
    _thread_local.correlation_id = correlation_id


def add_log_context(**kwargs):
    """
    Add context to all log messages in current thread.

    Args:
        **kwargs: Key-value pairs to add to log context
    """
    context = _get_context()
    context.update(kwargs)


def clear_log_context():
    """Clear all log context for current thread."""
    if hasattr(_thread_local, 'context'):
        _thread_local.context = {}


@contextmanager
def log_context(**kwargs):
    """
    Context manager to temporarily add log context.

    Usage:
        with log_context(user_id="123", request_id="abc"):
            logger.info("Processing request")

    Args:
        **kwargs: Key-value pairs to add to log context
    """
    old_context = _get_context().copy()
    try:
        add_log_context(**kwargs)
        yield
    finally:
        _thread_local.context = old_context


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for production environments.

    Outputs structured JSON logs with correlation IDs and context.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': _get_correlation_id(),
        }

        # Add context
        context = _get_context()
        if context:
            log_data['context'] = context

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        # Add source location
        log_data['source'] = {
            'file': record.filename,
            'line': record.lineno,
            'function': record.funcName,
        }

        return json.dumps(log_data)


class HumanReadableFormatter(logging.Formatter):
    """
    Human-readable log formatter for development.

    Outputs colored, easy-to-read logs for local development.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record in human-readable format."""
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']

        # Build message
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        correlation_id = _get_correlation_id()[:8]  # Short version

        # Base message
        parts = [
            f"{color}{record.levelname:<8}{reset}",
            f"{timestamp}",
            f"[{correlation_id}]",
            f"{record.name}",
            f"{record.getMessage()}",
        ]

        # Add context if present
        context = _get_context()
        if context:
            context_str = ' '.join(f"{k}={v}" for k, v in context.items())
            parts.append(f"({context_str})")

        message = ' '.join(parts)

        # Add exception if present
        if record.exc_info:
            message += '\n' + self.formatException(record.exc_info)

        return message


class ContextFilter(logging.Filter):
    """Filter to add context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to record."""
        record.correlation_id = _get_correlation_id()
        record.context = _get_context()
        return True


def setup_logging(
    level: LogLevel = LogLevel.INFO,
    format_type: str = "human",
    log_file: Optional[Path] = None,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Minimum log level
        format_type: "json" for structured JSON logs, "human" for readable logs
        log_file: Optional file path to write logs to
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.value))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Choose formatter
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = HumanReadableFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())  # Always use JSON for files
        file_handler.addFilter(ContextFilter())
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('spotipy').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance

    Usage:
        logger = get_logger(__name__)
        logger.info("Starting application")
    """
    return logging.getLogger(name)
