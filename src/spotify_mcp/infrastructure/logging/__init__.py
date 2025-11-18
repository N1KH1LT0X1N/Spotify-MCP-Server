"""
Structured logging infrastructure for Spotify MCP Server.

Provides production-grade logging with JSON formatting, correlation IDs,
and contextual information for debugging and monitoring.
"""

from .logger import (
    get_logger,
    setup_logging,
    LogLevel,
    add_log_context,
    clear_log_context,
    log_context,
    set_correlation_id,
    JSONFormatter,
    HumanReadableFormatter,
)

__all__ = [
    'get_logger',
    'setup_logging',
    'LogLevel',
    'add_log_context',
    'clear_log_context',
    'log_context',
    'set_correlation_id',
    'JSONFormatter',
    'HumanReadableFormatter',
]
