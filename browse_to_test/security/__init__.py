"""
Security module for browse-to-test library.

This module provides security validation and sanitization features to prevent:
- JavaScript URL injection attacks
- Data URL XSS vulnerabilities
- Sensitive data exposure
- Malicious input processing
"""

from .url_validator import (
    URLValidator,
    URLValidationResult,
    URLThreatLevel,
    validate_url,
    is_safe_url,
    sanitize_url_for_testing,
    get_default_validator
)

__all__ = [
    'URLValidator',
    'URLValidationResult', 
    'URLThreatLevel',
    'validate_url',
    'is_safe_url', 
    'sanitize_url_for_testing',
    'get_default_validator'
]