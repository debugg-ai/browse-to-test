"""
URL validation and sanitization for security protection.

This module provides comprehensive URL validation to prevent:
- JavaScript URL injection attacks
- Data URL XSS attacks  
- File protocol vulnerabilities
- Malicious redirect chains
"""

import re
import urllib.parse
from typing import Optional, List, Set
from dataclasses import dataclass
from enum import Enum


class URLThreatLevel(Enum):
    """URL threat classification levels."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"


@dataclass
class URLValidationResult:
    """Result of URL validation."""
    is_valid: bool
    threat_level: URLThreatLevel
    sanitized_url: Optional[str] = None
    warnings: List[str] = None
    blocked_reason: Optional[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class URLValidator:
    """Comprehensive URL validator for security protection."""
    
    # Dangerous URL schemes that should be blocked
    BLOCKED_SCHEMES = {
        'javascript', 'data', 'file', 'vbscript', 'jar', 'javascript:',
        'data:', 'file:', 'vbscript:', 'jar:'
    }
    
    # Suspicious patterns in URLs
    SUSPICIOUS_PATTERNS = [
        r'javascript\s*:',
        r'data\s*:',
        r'<script',
        r'eval\s*\(',
        r'alert\s*\(',
        r'document\.cookie',
        r'document\.domain',
        r'window\.location',
        r'fetch\s*\(',
        r'XMLHttpRequest',
        r'iframe',
        r'embed',
        r'object',
        r'base64',
        r'atob\s*\(',
        r'btoa\s*\(',
        r'unescape\s*\(',
        r'decodeURI',
        r'fromCharCode'
    ]
    
    # Safe URL schemes
    SAFE_SCHEMES = {'http', 'https'}
    
    # Safe domains (can be configured)
    TRUSTED_DOMAINS: Set[str] = set()
    
    def __init__(self, trusted_domains: Optional[Set[str]] = None):
        """Initialize URL validator with optional trusted domains."""
        if trusted_domains:
            self.TRUSTED_DOMAINS = trusted_domains.copy()
    
    def validate_url(self, url: str) -> URLValidationResult:
        """
        Comprehensive URL validation and sanitization.
        
        Args:
            url: URL to validate
            
        Returns:
            URLValidationResult with validation status and sanitized URL
        """
        if not url or not isinstance(url, str):
            return URLValidationResult(
                is_valid=False,
                threat_level=URLThreatLevel.BLOCKED,
                blocked_reason="Empty or invalid URL"
            )
        
        # Remove whitespace and normalize
        url = url.strip()
        
        # Check for blocked schemes
        scheme_check = self._check_blocked_schemes(url)
        if not scheme_check.is_valid:
            return scheme_check
        
        # Check for suspicious patterns
        pattern_check = self._check_suspicious_patterns(url)
        if pattern_check.threat_level == URLThreatLevel.BLOCKED:
            return pattern_check
        
        # Parse and validate URL structure
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            return URLValidationResult(
                is_valid=False,
                threat_level=URLThreatLevel.BLOCKED,
                blocked_reason=f"URL parsing failed: {e}"
            )
        
        # Validate scheme
        if parsed.scheme.lower() not in self.SAFE_SCHEMES:
            return URLValidationResult(
                is_valid=False,
                threat_level=URLThreatLevel.BLOCKED,
                blocked_reason=f"Unsafe scheme: {parsed.scheme}"
            )
        
        # Additional security checks
        security_check = self._additional_security_checks(parsed, url)
        if not security_check.is_valid:
            return security_check
        
        # Create sanitized URL
        sanitized_url = self._sanitize_url(parsed)
        
        # Determine final threat level
        final_threat = max(pattern_check.threat_level, URLThreatLevel.SAFE, key=lambda x: x.value)
        
        return URLValidationResult(
            is_valid=True,
            threat_level=final_threat,
            sanitized_url=sanitized_url,
            warnings=pattern_check.warnings
        )
    
    def _check_blocked_schemes(self, url: str) -> URLValidationResult:
        """Check for blocked URL schemes."""
        url_lower = url.lower().strip()
        
        for blocked_scheme in self.BLOCKED_SCHEMES:
            if url_lower.startswith(blocked_scheme) or blocked_scheme in url_lower:
                return URLValidationResult(
                    is_valid=False,
                    threat_level=URLThreatLevel.BLOCKED,
                    blocked_reason=f"Blocked scheme detected: {blocked_scheme}"
                )
        
        return URLValidationResult(is_valid=True, threat_level=URLThreatLevel.SAFE)
    
    def _check_suspicious_patterns(self, url: str) -> URLValidationResult:
        """Check for suspicious patterns in URL."""
        warnings = []
        threat_level = URLThreatLevel.SAFE
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                warning = f"Suspicious pattern detected: {pattern}"
                warnings.append(warning)
                
                # Some patterns are more dangerous than others
                if pattern in [r'javascript\s*:', r'data\s*:', r'<script']:
                    threat_level = URLThreatLevel.BLOCKED
                    return URLValidationResult(
                        is_valid=False,
                        threat_level=threat_level,
                        blocked_reason=f"Dangerous pattern detected: {pattern}",
                        warnings=warnings
                    )
                else:
                    threat_level = max(threat_level, URLThreatLevel.SUSPICIOUS, key=lambda x: x.value)
        
        return URLValidationResult(
            is_valid=True,
            threat_level=threat_level,
            warnings=warnings
        )
    
    def _additional_security_checks(self, parsed: urllib.parse.ParseResult, original_url: str) -> URLValidationResult:
        """Additional security validation checks."""
        warnings = []
        
        # Check for suspicious query parameters
        if parsed.query:
            query_params = urllib.parse.parse_qs(parsed.query)
            for param, values in query_params.items():
                for value in values:
                    if any(re.search(pattern, value, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS):
                        warnings.append(f"Suspicious query parameter: {param}={value}")
        
        # Check for suspicious fragments
        if parsed.fragment:
            if any(re.search(pattern, parsed.fragment, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS):
                warnings.append(f"Suspicious URL fragment: {parsed.fragment}")
        
        # Check URL length (extremely long URLs can be suspicious)
        if len(original_url) > 2048:
            warnings.append("Unusually long URL detected")
        
        # Check for URL encoding obfuscation
        if '%' in original_url:
            try:
                decoded = urllib.parse.unquote(original_url)
                if decoded != original_url:
                    # Check if decoded version contains suspicious patterns
                    for pattern in self.SUSPICIOUS_PATTERNS:
                        if re.search(pattern, decoded, re.IGNORECASE):
                            return URLValidationResult(
                                is_valid=False,
                                threat_level=URLThreatLevel.BLOCKED,
                                blocked_reason="URL encoding detected with suspicious content"
                            )
            except Exception:
                warnings.append("URL decoding failed")
        
        return URLValidationResult(
            is_valid=True,
            threat_level=URLThreatLevel.SAFE,
            warnings=warnings
        )
    
    def _sanitize_url(self, parsed: urllib.parse.ParseResult) -> str:
        """Create a sanitized version of the URL."""
        # Reconstruct URL with only safe components
        sanitized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment for safety
        ))
        return sanitized
    
    def is_safe_url(self, url: str) -> bool:
        """Quick check if URL is safe for use."""
        result = self.validate_url(url)
        return result.is_valid and result.threat_level in [URLThreatLevel.SAFE, URLThreatLevel.SUSPICIOUS]
    
    def sanitize_for_testing(self, url: str) -> Optional[str]:
        """Sanitize URL specifically for test generation."""
        result = self.validate_url(url)
        
        if not result.is_valid:
            # For testing, we might want to provide a safe placeholder
            return "https://example.com"  # Safe placeholder
        
        if result.threat_level == URLThreatLevel.BLOCKED:
            return "https://example.com"  # Safe placeholder
        
        return result.sanitized_url or url


# Global validator instance
_default_validator = None


def get_default_validator() -> URLValidator:
    """Get the default URL validator instance."""
    global _default_validator
    if _default_validator is None:
        _default_validator = URLValidator()
    return _default_validator


def validate_url(url: str) -> URLValidationResult:
    """Validate URL using the default validator."""
    return get_default_validator().validate_url(url)


def is_safe_url(url: str) -> bool:
    """Check if URL is safe using the default validator."""
    return get_default_validator().is_safe_url(url)


def sanitize_url_for_testing(url: str) -> str:
    """Sanitize URL for safe test generation."""
    return get_default_validator().sanitize_for_testing(url) or "https://example.com"