#!/usr/bin/env python3
"""
Browse-to-Test Live Library Verification Sample

This script demonstrates and verifies the functionality of the live browse-to-test
library by testing various features and use cases.

Usage:
    python main.py [--ai-provider openai|anthropic] [--verbose]

Requirements:
    pip install browse-to-test[all]
    
Environment Variables:
    OPENAI_API_KEY - Required for OpenAI provider
    ANTHROPIC_API_KEY - Required for Anthropic provider
"""

import sys
import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


try:
    import browse_to_test as btt
except ImportError:
    print("❌ Error: browse-to-test library not found!")
    print("📦 Please install: pip install browse-to-test[all]")
    sys.exit(1)

def print_section(title: str, char: str = "="):
    """Print a styled section header."""
    print(f"\n{char * 60}")
    print(f" {title}")
    print(f"{char * 60}")

def print_result(test_name: str, success: bool, details: str = "", output_file: str = None):
    """Print test result with formatting."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   📝 {details}")
    if output_file:
        print(f"   📄 Output: {output_file}")

def load_sample_data() -> Dict[str, List[Dict]]:
    """Load different types of sample automation data."""
    return {
        "simple_navigation": [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://example.com"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate to example.com", "elapsed_time": 1.2}
            }
        ],
        
        "login_flow": [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://app.example.com/login"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate to login page", "elapsed_time": 1.5}
            },
            {
                "model_output": {
                    "action": [{"input_text": {"text": "user@example.com", "index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "xpath": "//input[@data-testid='email-input']",
                        "css_selector": "input[data-testid='email-input']",
                        "attributes": {"data-testid": "email-input", "type": "email", "name": "email"}
                    }]
                },
                "metadata": {"description": "Enter email", "elapsed_time": 0.8}
            },
            {
                "model_output": {
                    "action": [{"input_text": {"text": "secure_password123", "index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "xpath": "//input[@data-testid='password-input']",
                        "css_selector": "input[data-testid='password-input']",
                        "attributes": {"data-testid": "password-input", "type": "password", "name": "password"}
                    }]
                },
                "metadata": {"description": "Enter password", "elapsed_time": 0.6}
            },
            {
                "model_output": {
                    "action": [{"click_element": {"index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "xpath": "//button[@data-testid='login-submit']",
                        "css_selector": "button[data-testid='login-submit']",
                        "attributes": {"data-testid": "login-submit", "type": "submit", "class": "btn btn-primary"}
                    }]
                },
                "metadata": {"description": "Click login button", "elapsed_time": 0.4}
            },
            {
                "model_output": {
                    "action": [
                        {"wait": {"seconds": 2}},
                        {"done": {"success": True, "text": "Login successful"}}
                    ]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Wait and complete", "elapsed_time": 2.1}
            }
        ],
        
        "shopping_cart": [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://shop.example.com"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate to shop", "elapsed_time": 1.8}
            },
            {
                "model_output": {
                    "action": [{"input_text": {"text": "laptop", "index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "xpath": "//input[@placeholder='Search products...']",
                        "css_selector": "input.search-input",
                        "attributes": {"placeholder": "Search products...", "type": "text", "class": "search-input"}
                    }]
                },
                "metadata": {"description": "Search for laptop", "elapsed_time": 0.5}
            },
            {
                "model_output": {
                    "action": [{"click_element": {"index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "xpath": "//button[contains(@class, 'search-btn')]",
                        "css_selector": "button.search-btn",
                        "attributes": {"class": "search-btn", "type": "button"}
                    }]
                },
                "metadata": {"description": "Click search button", "elapsed_time": 0.3}
            },
            {
                "model_output": {
                    "action": [{"click_element": {"index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "xpath": "//div[@data-product-id='laptop-123']//button[contains(text(), 'Add to Cart')]",
                        "css_selector": "[data-product-id='laptop-123'] .add-to-cart",
                        "attributes": {"class": "add-to-cart btn", "data-product-id": "laptop-123"}
                    }]
                },
                "metadata": {"description": "Add laptop to cart", "elapsed_time": 0.7}
            }
        ]
    }

def test_simple_conversion(ai_provider: str, verbose: bool = False) -> bool:
    """Test basic conversion functionality."""
    print_section("1. Basic Conversion Tests", "-")
    
    sample_data = load_sample_data()
    frameworks = ["playwright", "selenium"]
    languages = ["python"]  # Focus on Python for now
    
    all_tests_passed = True
    
    for framework in frameworks:
        for language in languages:
            try:
                script = btt.convert(
                    sample_data["simple_navigation"],
                    framework=framework,
                    ai_provider=ai_provider,
                    language=language,
                    include_assertions=True,
                    include_error_handling=True
                )
                
                output_file = f"output/simple_{framework}_{language}_test.py"
                os.makedirs("output", exist_ok=True)
                
                with open(output_file, 'w') as f:
                    f.write(script)
                
                success = len(script) > 100  # Basic validation
                test_name = f"Simple {framework.capitalize()} {language.capitalize()} conversion"
                print_result(test_name, success, f"Generated {len(script)} characters", output_file)
                
                if verbose and success:
                    print(f"   📄 Preview:\n{script[:200]}...")
                
                all_tests_passed = all_tests_passed and success
                
            except Exception as e:
                print_result(f"Simple {framework} {language} conversion", False, f"Error: {str(e)}")
                all_tests_passed = False
    
    return all_tests_passed

def test_config_builder(ai_provider: str, verbose: bool = False) -> bool:
    """Test ConfigBuilder functionality."""
    print_section("2. ConfigBuilder Tests", "-")
    
    sample_data = load_sample_data()["login_flow"]
    
    try:
        # Test fluent configuration
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider(ai_provider) \
            .language("python") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .include_logging(True) \
            .timeout(15000) \
            .debug(verbose) \
            .build()
        
        converter = btt.E2eTestConverter(config)
        script = converter.convert(sample_data)
        
        output_file = "output/config_builder_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        success = len(script) > 200
        print_result("ConfigBuilder fluent interface", success, f"Generated {len(script)} characters", output_file)
        
        if verbose and success:
            print(f"   📄 Preview:\n{script[:300]}...")
        
        return success
        
    except Exception as e:
        print_result("ConfigBuilder fluent interface", False, f"Error: {str(e)}")
        return False

def test_incremental_session(ai_provider: str, verbose: bool = False) -> bool:
    """Test incremental session functionality."""
    print_section("3. Incremental Session Tests", "-")
    
    sample_data = load_sample_data()["shopping_cart"]
    
    try:
        # Build session config
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider(ai_provider) \
            .language("python") \
            .build()
        
        # Create incremental session
        session = btt.IncrementalSession(config)
        
        # Start session
        result = session.start("https://shop.example.com")
        if not result.success:
            print_result("Incremental session start", False, "Failed to start session")
            return False
        
        print_result("Incremental session start", True, "Session started successfully")
        
        # Add steps incrementally
        step_results = []
        for i, step in enumerate(sample_data):
            result = session.add_step(step)
            step_results.append(result.success)
            
            if verbose:
                print(f"   📦 Step {i+1}: {'✅' if result.success else '❌'} ({result.lines_added} lines added)")
        
        # Finalize session
        final_result = session.finalize()
        
        output_file = "output/incremental_session_test.py"
        with open(output_file, 'w') as f:
            f.write(final_result.current_script)
        
        all_steps_success = all(step_results)
        final_success = final_result.success and len(final_result.current_script) > 300
        
        print_result("Incremental steps", all_steps_success, f"Added {len(sample_data)} steps")
        print_result("Session finalization", final_success, f"Generated {len(final_result.current_script)} characters", output_file)
        
        return all_steps_success and final_success
        
    except Exception as e:
        print_result("Incremental session", False, f"Error: {str(e)}")
        return False

def test_utility_functions(verbose: bool = False) -> bool:
    """Test utility functions."""
    print_section("4. Utility Function Tests", "-")
    
    try:
        # Test framework listing
        frameworks = btt.list_frameworks()
        frameworks_test = len(frameworks) > 0 and "playwright" in frameworks
        print_result("List frameworks", frameworks_test, f"Found: {frameworks}")
        
        # Test AI provider listing
        providers = btt.list_ai_providers()
        providers_test = len(providers) > 0 and "openai" in providers
        print_result("List AI providers", providers_test, f"Found: {providers}")
        
        return frameworks_test and providers_test
        
    except Exception as e:
        print_result("Utility functions", False, f"Error: {str(e)}")
        return False

def test_error_handling(ai_provider: str, verbose: bool = False) -> bool:
    """Test error handling capabilities."""
    print_section("5. Error Handling Tests", "-")
    
    tests_passed = []
    
    # Test invalid framework
    try:
        script = btt.convert(
            load_sample_data()["simple_navigation"],
            framework="invalid_framework",
            ai_provider=ai_provider
        )
        tests_passed.append(False)  # Should have failed
        print_result("Invalid framework handling", False, "Should have raised an error")
    except Exception:
        tests_passed.append(True)  # Expected to fail
        print_result("Invalid framework handling", True, "Correctly raised an error")
    
    # Test invalid data
    try:
        script = btt.convert(
            [{"invalid": "data"}],
            framework="playwright",
            ai_provider=ai_provider
        )
        tests_passed.append(False)  # Should have failed
        print_result("Invalid data handling", False, "Should have raised an error")
    except Exception:
        tests_passed.append(True)  # Expected to fail
        print_result("Invalid data handling", True, "Correctly raised an error")
    
    # Test empty data
    try:
        script = btt.convert(
            [],
            framework="playwright",
            ai_provider=ai_provider
        )
        # Empty data might be handled gracefully, so check result
        success = len(script) > 50  # Should generate at least basic script structure
        tests_passed.append(success)
        print_result("Empty data handling", success, "Generated basic script structure" if success else "Failed to handle empty data")
    except Exception as e:
        tests_passed.append(False)
        print_result("Empty data handling", False, f"Unexpected error: {str(e)}")
    
    return all(tests_passed)

def test_advanced_features(ai_provider: str, verbose: bool = False) -> bool:
    """Test advanced features like sensitive data handling."""
    print_section("6. Advanced Features Tests", "-")
    
    sample_data = load_sample_data()["login_flow"]
    
    try:
        # Test with sensitive data configuration
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider(ai_provider) \
            .language("python") \
            .sensitive_data_keys(["password", "email"]) \
            .include_assertions(True) \
            .include_error_handling(True) \
            .build()
        
        converter = btt.E2eTestConverter(config)
        script = converter.convert(sample_data)
        
        output_file = "output/advanced_features_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        # Check if sensitive data appears to be handled
        has_sensitive_handling = "password" not in script or "***" in script or "REDACTED" in script
        script_quality = len(script) > 400  # Should be substantial
        
        success = has_sensitive_handling and script_quality
        details = f"Generated {len(script)} characters"
        if has_sensitive_handling:
            details += ", sensitive data handled"
        
        print_result("Advanced features", success, details, output_file)
        
        return success
        
    except Exception as e:
        print_result("Advanced features", False, f"Error: {str(e)}")
        return False

def generate_test_report(results: Dict[str, bool], ai_provider: str) -> str:
    """Generate a test report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    report = f"""
Browse-to-Test Live Library Verification Report
===============================================

Timestamp: {timestamp}
AI Provider: {ai_provider}
Total Tests: {total_tests}
Passed: {passed_tests}
Failed: {total_tests - passed_tests}
Success Rate: {(passed_tests/total_tests)*100:.1f}%

Test Results:
"""
    
    for test_name, passed in results.items():
        status = "PASS ✅" if passed else "FAIL ❌"
        report += f"  - {test_name}: {status}\n"
    
    report += f"""
Generated Files:
  - output/simple_playwright_python_test.py
  - output/simple_selenium_python_test.py  
  - output/config_builder_test.py
  - output/incremental_session_test.py
  - output/advanced_features_test.py
  - output/test_report.txt

Overall Status: {'✅ ALL TESTS PASSED' if passed_tests == total_tests else '❌ SOME TESTS FAILED'}

Notes:
- This verification tests the live browse-to-test library functionality
- All generated test files are saved in the output/ directory
- For production use, ensure proper API keys are configured
- Generated tests should be reviewed before production deployment
"""
    
    return report

async def main():
    """Main verification function."""
    parser = argparse.ArgumentParser(description="Browse-to-Test Live Library Verification")
    parser.add_argument("--ai-provider", choices=["openai", "anthropic"], default="openai",
                        help="AI provider to use (default: openai)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print_section("🚀 Browse-to-Test Live Library Verification")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 AI Provider: {args.ai_provider}")
    print(f"📝 Verbose Mode: {'Enabled' if args.verbose else 'Disabled'}")
    
    # Check API key
    api_key_env = f"{args.ai_provider.upper()}_API_KEY"
    if not os.getenv(api_key_env):
        print(f"\n⚠️  Warning: {api_key_env} environment variable not set!")
        print(f"   Some tests may fail without proper API key configuration.")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run tests
    test_results = {}
    
    test_results["Basic Conversion"] = test_simple_conversion(args.ai_provider, args.verbose)
    test_results["ConfigBuilder"] = test_config_builder(args.ai_provider, args.verbose)
    test_results["Incremental Session"] = test_incremental_session(args.ai_provider, args.verbose)
    test_results["Utility Functions"] = test_utility_functions(args.verbose)
    test_results["Error Handling"] = test_error_handling(args.ai_provider, args.verbose)
    test_results["Advanced Features"] = test_advanced_features(args.ai_provider, args.verbose)
    
    # Generate and save report
    report = generate_test_report(test_results, args.ai_provider)
    
    with open("output/test_report.txt", "w") as f:
        f.write(report)
    
    print_section("📊 Final Results")
    print(report)
    
    # Return appropriate exit code
    all_passed = all(test_results.values())
    if all_passed:
        print("\n🎉 All verification tests passed! The live library is working correctly.")
        return 0
    else:
        print("\n❌ Some verification tests failed. Check the detailed results above.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 