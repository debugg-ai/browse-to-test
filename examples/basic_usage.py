#!/usr/bin/env python3
"""
Basic Usage Example for Browse-to-Test

This example demonstrates the simplest way to use browse-to-test to convert 
browser automation data into test scripts using the new unified API.

Key features demonstrated:
- Simple convert() function
- Multiple frameworks (Playwright, Selenium)
- Different output languages (Python, TypeScript)
- Basic configuration options

Requirements:
- Set OPENAI_API_KEY environment variable
- Or use: export OPENAI_API_KEY="your-key-here"
"""

import os
import browse_to_test as btt
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_sample_automation_data():
    """Create sample browser automation data for demonstration."""
    return [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            },
            "state": {
                "url": "https://example.com",
                "title": "Example Domain",
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "step_end_time": 1640995203.5,
                "step_number": 1
            }
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "demo@example.com"}}]
            },
            "state": {
                "url": "https://example.com/login",
                "title": "Login - Example Domain",
                "interacted_element": [{
                    "xpath": "//input[@name='email']",
                    "css_selector": "input[name='email']",
                    "highlight_index": 0,
                    "attributes": {
                        "name": "email",
                        "type": "email",
                        "id": "email-field"
                    }
                }]
            },
            "metadata": {
                "step_start_time": 1640995203.5,
                "step_end_time": 1640995205.0,
                "step_number": 2
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://example.com/login",
                "title": "Login - Example Domain",
                "interacted_element": [{
                    "xpath": "//button[@type='submit']",
                    "css_selector": "button[type='submit']",
                    "highlight_index": 0,
                    "attributes": {
                        "type": "submit",
                        "class": "btn btn-primary",
                        "id": "login-button"
                    },
                    "text_content": "Sign In"
                }]
            },
            "metadata": {
                "step_start_time": 1640995205.0,
                "step_end_time": 1640995207.0,
                "step_number": 3
            }
        }
    ]


def example_1_simple_conversion():
    """Example 1: Simplest possible usage."""
    print("=== Example 1: Simple Conversion ===")
    
    automation_data = create_sample_automation_data()
    
    try:
        # One-line conversion using the new convert() function
        script = btt.convert(
            automation_data=automation_data,
            framework="playwright",
            ai_provider="openai"
        )
        
        # Save the script
        output_file = OUTPUT_DIR / "simple_playwright_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Generated Playwright test: {output_file}")
        print(f"  Script length: {len(script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Make sure you have OPENAI_API_KEY set in your environment")


def example_2_multiple_frameworks():
    """Example 2: Generate tests for multiple frameworks."""
    print("\n=== Example 2: Multiple Frameworks ===")
    
    automation_data = create_sample_automation_data()
    frameworks = ["playwright", "selenium"]
    
    for framework in frameworks:
        try:
            script = btt.convert(
                automation_data=automation_data,
                framework=framework,
                ai_provider="openai",
                language="python"
            )
            
            output_file = OUTPUT_DIR / f"{framework}_test.py"
            with open(output_file, 'w') as f:
                f.write(script)
            
            print(f"✓ {framework.capitalize()}: {output_file}")
            
        except Exception as e:
            print(f"✗ {framework.capitalize()}: {e}")


def example_3_different_languages():
    """Example 3: Generate tests in different languages."""
    print("\n=== Example 3: Different Languages ===")
    
    automation_data = create_sample_automation_data()
    languages = [
        ("python", ".py"),
        ("typescript", ".ts")
    ]
    
    for language, extension in languages:
        try:
            script = btt.convert(
                automation_data=automation_data,
                framework="playwright",
                ai_provider="openai",
                language=language,
                include_assertions=True,
                include_error_handling=True
            )
            
            output_file = OUTPUT_DIR / f"playwright_test_{language}{extension}"
            with open(output_file, 'w') as f:
                f.write(script)
            
            print(f"✓ {language.capitalize()}: {output_file}")
            
        except Exception as e:
            print(f"✗ {language.capitalize()}: {e}")


def example_4_with_options():
    """Example 4: Using additional options."""
    print("\n=== Example 4: With Custom Options ===")
    
    automation_data = create_sample_automation_data()
    
    try:
        script = btt.convert(
            automation_data=automation_data,
            framework="playwright",
            ai_provider="openai",
            language="python",
            # Additional options
            include_assertions=True,
            include_error_handling=True,
            include_logging=True,
            add_comments=True,
            test_timeout=60000,  # 60 seconds
            sensitive_data_keys=["email", "password", "token"]
        )
        
        output_file = OUTPUT_DIR / "enhanced_playwright_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Enhanced test: {output_file}")
        print(f"  Features: assertions, error handling, logging, comments")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_5_list_available_options():
    """Example 5: Discover available frameworks and AI providers."""
    print("\n=== Example 5: Available Options ===")
    
    try:
        frameworks = btt.list_frameworks()
        ai_providers = btt.list_ai_providers()
        
        print(f"Available frameworks: {', '.join(frameworks)}")
        print(f"Available AI providers: {', '.join(ai_providers)}")
        
    except Exception as e:
        print(f"✗ Error listing options: {e}")


def main():
    """Run all basic examples."""
    print("Browse-to-Test Basic Usage Examples")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ Warning: OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("Some examples may fail without it.\n")
    
    try:
        # Run examples
        example_1_simple_conversion()
        example_2_multiple_frameworks()
        example_3_different_languages()
        example_4_with_options()
        example_5_list_available_options()
        
        # Show generated files
        print(f"\n📁 Generated files in {OUTPUT_DIR.relative_to(Path.cwd())}:")
        output_files = list(OUTPUT_DIR.glob("*.py")) + list(OUTPUT_DIR.glob("*.ts"))
        for file_path in sorted(output_files):
            size = file_path.stat().st_size
            print(f"   • {file_path.name} ({size:,} bytes)")
        
        print("\n✓ All examples completed successfully!")
        print("\nNext steps:")
        print("- Try the async_usage.py example for better performance")
        print("- Try the incremental_session.py example for live test generation")
        print("- Try the configuration_builder.py example for advanced settings")
        
    except Exception as e:
        print(f"\n✗ Examples failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()