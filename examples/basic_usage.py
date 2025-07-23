#!/usr/bin/env python3
"""
Basic usage example for browse-to-test library.

This example demonstrates how to convert browser automation data
into test scripts using the library.
"""

import json
import os
from pathlib import Path

# Import the main library
import browse_to_test as btt


def create_sample_automation_data():
    """Create sample browser automation data for demonstration."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://example.com"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "step_end_time": 1640995203.5,
                "elapsed_time": 3.5
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "index": 0,
                            "text": "<secret>username</secret>"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@name='username']",
                        "css_selector": "input[name='username']",
                        "highlight_index": 0,
                        "attributes": {
                            "name": "username",
                            "type": "text",
                            "id": "username-field"
                        }
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "index": 0,
                            "text": "<secret>password</secret>"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@name='password']",
                        "css_selector": "input[name='password']",
                        "highlight_index": 0,
                        "attributes": {
                            "name": "password",
                            "type": "password",
                            "id": "password-field"
                        }
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "click_element": {
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//button[@type='submit']",
                        "css_selector": "button[type='submit']",
                        "highlight_index": 0,
                        "attributes": {
                            "type": "submit",
                            "class": "btn btn-primary",
                            "id": "login-button"
                        },
                        "text_content": "Login"
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "text": "Successfully completed login process",
                            "success": True
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        }
    ]


def basic_example():
    """Demonstrate basic usage of the library."""
    print("=== Basic Browse-to-Test Example ===\n")
    
    # Create sample automation data
    automation_data = create_sample_automation_data()
    print(f"Created sample automation data with {len(automation_data)} steps")
    
    # Method 1: Simple conversion using convenience function
    print("\n--- Method 1: Simple Conversion ---")
    try:
        playwright_script = btt.convert_to_test_script(
            automation_data=automation_data,
            output_framework="playwright",
            ai_provider="openai"
        )
        
        # Save the generated script
        output_file = "generated_playwright_test.py"
        with open(output_file, 'w') as f:
            f.write(playwright_script)
        
        print(f"✓ Generated Playwright script: {output_file}")
        print(f"  Script length: {len(playwright_script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Failed to generate Playwright script: {e}")
    
    # Method 2: Generate Selenium script for comparison
    print("\n--- Method 2: Different Framework ---")
    try:
        selenium_script = btt.convert_to_test_script(
            automation_data=automation_data,
            output_framework="selenium",
            ai_provider="openai"
        )
        
        # Save the generated script
        output_file = "generated_selenium_test.py"
        with open(output_file, 'w') as f:
            f.write(selenium_script)
        
        print(f"✓ Generated Selenium script: {output_file}")
        print(f"  Script length: {len(selenium_script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Failed to generate Selenium script: {e}")


def advanced_example():
    """Demonstrate advanced usage with custom configuration."""
    print("\n=== Advanced Browse-to-Test Example ===\n")
    
    # Create custom configuration
    config = btt.Config(
        ai=btt.AIConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.1,
        ),
        output=btt.OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_waits=True,
            include_error_handling=True,
            include_logging=True,
            sensitive_data_keys=["username", "password"],
            add_comments=True,
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=True,
            optimize_selectors=True,
            validate_actions=True,
        ),
        debug=True,
        verbose=True,
    )
    
    # Validate configuration
    validation_errors = config.validate()
    if validation_errors:
        print("Configuration validation errors:")
        for error in validation_errors:
            print(f"  - {error}")
        return
    
    print("✓ Configuration validated successfully")
    
    # Create orchestrator
    orchestrator = btt.TestScriptOrchestrator(config)
    
    # Validate the orchestrator setup
    setup_errors = orchestrator.validate_configuration()
    if setup_errors:
        print("Setup validation errors:")
        for error in setup_errors:
            print(f"  - {error}")
        return
    
    print("✓ Orchestrator setup validated")
    
    # Get available options
    options = orchestrator.get_available_options()
    print(f"\nAvailable options:")
    print(f"  AI Providers: {', '.join(options['ai_providers'])}")
    print(f"  Output Plugins: {', '.join(options['output_plugins'])}")
    print(f"  Frameworks: {', '.join(options['supported_frameworks'])}")
    
    # Create automation data
    automation_data = create_sample_automation_data()
    
    # Preview the conversion
    print("\n--- Conversion Preview ---")
    preview = orchestrator.preview_conversion(automation_data)
    print(f"Total steps: {preview['total_steps']}")
    print(f"Total actions: {preview['total_actions']}")
    print(f"Action types: {preview['action_types']}")
    print(f"Sensitive data keys: {preview['sensitive_data_keys']}")
    
    if preview['validation_issues']:
        print("Validation issues:")
        for issue in preview['validation_issues']:
            print(f"  - {issue}")
    
    # Generate test script with full analysis
    print("\n--- Generating Test Script with AI Analysis ---")
    try:
        generated_script = orchestrator.generate_test_script(automation_data)
        
        # Save the script
        output_file = "generated_advanced_test.py"
        with open(output_file, 'w') as f:
            f.write(generated_script)
        
        print(f"✓ Generated advanced test script: {output_file}")
        print(f"  Script length: {len(generated_script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Failed to generate script: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()


def multi_framework_example():
    """Demonstrate generating scripts for multiple frameworks."""
    print("\n=== Multi-Framework Example ===\n")
    
    # Create configuration optimized for multiple frameworks
    config = btt.Config(
        ai=btt.AIConfig(
            provider="openai",
            model="gpt-3.5-turbo",  # Faster model for bulk generation
        ),
        output=btt.OutputConfig(
            include_assertions=True,
            include_error_handling=True,
            add_comments=True,
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=False,  # Disable for faster generation
        )
    )
    
    orchestrator = btt.TestScriptOrchestrator(config)
    automation_data = create_sample_automation_data()
    
    # Generate scripts for multiple frameworks
    frameworks = ["playwright", "selenium"]
    
    print("Generating scripts for multiple frameworks...")
    results = orchestrator.generate_with_multiple_frameworks(
        automation_data, 
        frameworks
    )
    
    for framework, script in results.items():
        if script.startswith("# Error"):
            print(f"✗ {framework}: {script}")
        else:
            output_file = f"generated_{framework}_multi.py"
            with open(output_file, 'w') as f:
                f.write(script)
            print(f"✓ {framework}: {output_file} ({len(script.splitlines())} lines)")


def load_from_file_example():
    """Demonstrate loading automation data from file."""
    print("\n=== Load from File Example ===\n")
    
    # Save sample data to file
    automation_data = create_sample_automation_data()
    data_file = "sample_automation_data.json"
    
    with open(data_file, 'w') as f:
        json.dump(automation_data, f, indent=2)
    
    print(f"Saved sample data to: {data_file}")
    
    # Load and convert from file
    try:
        script = btt.convert_to_test_script(
            automation_data=data_file,  # Pass file path instead of data
            output_framework="playwright",
            config={
                "output": {
                    "include_logging": True,
                    "add_comments": True,
                }
            }
        )
        
        output_file = "generated_from_file.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Generated script from file: {output_file}")
        
    except Exception as e:
        print(f"✗ Failed to generate from file: {e}")
    
    # Clean up
    if os.path.exists(data_file):
        os.remove(data_file)


def main():
    """Run all examples."""
    print("Browse-to-Test Library Examples")
    print("=" * 40)
    
    # Set up environment (you would normally set these in your environment)
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not set. AI features will be limited.")
        print("Set the environment variable to enable full AI analysis.\n")
    
    try:
        # Run examples
        basic_example()
        advanced_example()
        multi_framework_example()
        load_from_file_example()
        
        print("\n" + "=" * 40)
        print("Examples completed! Check the generated files:")
        
        # List generated files
        for file in Path(".").glob("generated_*.py"):
            size = file.stat().st_size
            print(f"  - {file.name} ({size} bytes)")
        
    except Exception as e:
        print(f"\nExample execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 