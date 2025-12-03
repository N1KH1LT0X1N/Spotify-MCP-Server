"""
Enhanced error handling for Spotify API operations.

Provides user-friendly error messages and recovery suggestions.
"""

import time
from typing import Optional, Callable, Any, Dict
from functools import wraps
import logging


logger = logging.getLogger(__name__)


class SpotifyAPIError(Exception):
    """Base exception for Spotify API errors."""
    pass


class RateLimitError(SpotifyAPIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, retry_after: int = 30):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limited by Spotify API. Please retry after {retry_after} seconds. "
            f"Tip: Avoid making multiple rapid requests to the same endpoint."
        )


class NoActiveDeviceError(SpotifyAPIError):
    """Raised when no active playback device is found."""
    
    def __init__(self):
        super().__init__(
            "No active Spotify device found. To use playback features:\n"
            "1. Open Spotify on any device (phone, desktop, web player, etc.)\n"
            "2. Make sure the device is logged into the same account\n"
            "3. The device will appear as 'active' for playback control\n"
            "Tip: Web player at https://open.spotify.com works great for development!"
        )


class PremiumRequiredError(SpotifyAPIError):
    """Raised when operation requires Premium."""
    
    def __init__(self):
        super().__init__(
            "This operation requires Spotify Premium. Playback control is only available "
            "to Premium subscribers. Free accounts can use search, library, and read operations."
        )


class AuthenticationError(SpotifyAPIError):
    """Raised when authentication fails."""
    
    def __init__(self):
        super().__init__(
            "Authentication failed. Your token may have expired.\n"
            "To fix this:\n"
            "1. Run: python -m spotify_mcp.auth\n"
            "2. Complete the authorization flow\n"
            "3. Restart the MCP server\n"
            "Tokens typically last 1 hour and are auto-refreshed by the server."
        )


class InvalidParameterError(SpotifyAPIError):
    """Raised when invalid parameters are provided."""
    
    def __init__(self, details: str = ""):
        msg = "Invalid parameter provided to Spotify API."
        if details:
            msg += f" {details}"
        super().__init__(msg)


class ResourceNotFoundError(SpotifyAPIError):
    """Raised when resource is not found."""
    
    def __init__(self, resource_type: str = "resource", resource_id: str = ""):
        msg = f"The {resource_type} was not found"
        if resource_id:
            msg += f": {resource_id}"
        msg += ". Please verify the ID is correct and the resource is available in your region."
        super().__init__(msg)


class RegionalRestrictionError(SpotifyAPIError):
    """Raised when content is not available in user's region."""
    
    def __init__(self):
        super().__init__(
            "This content is not available in your region. "
            "Some tracks, albums, and shows are region-restricted by licensing agreements. "
            "Try searching for similar content or check availability in a different region."
        )


class QuotaExceededError(SpotifyAPIError):
    """Raised when API quota is exceeded."""
    
    def __init__(self):
        super().__init__(
            "API quota exceeded. Your application has exceeded its request limit. "
            "Quotas are typically reset daily. Try again tomorrow or optimize your usage patterns."
        )


def extract_error_info(error: Exception) -> Dict[str, Any]:
    """
    Extract relevant error information from Spotify exceptions.
    
    Args:
        error: The exception to analyze
        
    Returns:
        Dictionary with error details
    """
    error_str = str(error)
    error_info = {
        "type": error.__class__.__name__,
        "message": error_str,
        "retry_possible": False,
        "retry_after": None
    }
    
    # Check for rate limiting
    if "429" in error_str or "rate" in error_str.lower():
        error_info["type"] = "RateLimitError"
        error_info["retry_possible"] = True
        error_info["retry_after"] = 30  # Default retry after
        if "Retry-After" in error_str:
            try:
                error_info["retry_after"] = int(error_str.split("Retry-After")[1].split()[0])
            except (ValueError, IndexError):
                pass
    
    # Check for authentication issues
    elif "401" in error_str or "unauthorized" in error_str.lower():
        error_info["type"] = "AuthenticationError"
        error_info["suggestion"] = "Run 'python -m spotify_mcp.auth' to re-authenticate"
    
    # Check for no active device
    elif "NO_ACTIVE_DEVICE" in error_str or "no active device" in error_str.lower():
        error_info["type"] = "NoActiveDeviceError"
        error_info["suggestion"] = "Open Spotify on any device to enable playback control"
    
    # Check for premium required
    elif "PREMIUM_REQUIRED" in error_str or "premium" in error_str.lower():
        error_info["type"] = "PremiumRequiredError"
        error_info["suggestion"] = "This feature requires Spotify Premium"
    
    # Check for not found
    elif "404" in error_str or "not found" in error_str.lower():
        error_info["type"] = "NotFoundError"
        error_info["suggestion"] = "Verify the ID is correct and the resource exists"
    
    # Check for regional restrictions
    elif "restricted" in error_str.lower() or "unavailable" in error_str.lower():
        error_info["type"] = "RegionalRestrictionError"
        error_info["suggestion"] = "This content may not be available in your region"
    
    return error_info


def with_retry(max_attempts: int = 3, backoff_factor: float = 2.0, 
               initial_delay: float = 1.0) -> Callable:
    """
    Decorator to add automatic retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for delay between retries
        initial_delay: Initial delay in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Rate limited on attempt {attempt + 1}/{max_attempts}. "
                            f"Waiting {e.retry_after} seconds before retry..."
                        )
                        time.sleep(e.retry_after)
                    else:
                        raise
                except (TimeoutError, ConnectionError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Connection error on attempt {attempt + 1}/{max_attempts}. "
                            f"Retrying in {delay} seconds..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise
                except SpotifyAPIError:
                    # Don't retry for non-transient Spotify API errors
                    raise
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1 and attempt < 1:
                        # Only retry once for unexpected errors
                        logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")
                        time.sleep(delay)
                    else:
                        raise
            
            if last_error:
                raise last_error
                
        return wrapper
    return decorator


def with_error_handling(func: Callable) -> Callable:
    """
    Decorator to add comprehensive error handling to tool functions.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = extract_error_info(e)
            
            # Log the error with context
            logger.error(
                f"Error in {func.__name__}: {error_info['type']} - {error_info['message']}"
            )
            
            # Re-raise with enhanced information
            raise SpotifyAPIError(
                f"{error_info['type']}: {error_info['message']}"
            ) from e
    
    return wrapper


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Format an error for MCP response.
    
    Args:
        error: The exception that occurred
        
    Returns:
        Formatted error response dictionary
    """
    error_info = extract_error_info(error)
    
    response = {
        "error": True,
        "error_type": error_info["type"],
        "message": error_info["message"],
    }
    
    if error_info.get("suggestion"):
        response["suggestion"] = error_info["suggestion"]
    
    if error_info.get("retry_possible"):
        response["retry_possible"] = True
        response["retry_after_seconds"] = error_info.get("retry_after", 30)
    
    return response
