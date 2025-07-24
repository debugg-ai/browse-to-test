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

from dotenv import load_dotenv


load_dotenv()

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
    
    # Method 1: Simple conversion using the new convert function
    print("\n--- Method 1: Simple Conversion ---")
    try:
        playwright_script = btt.convert(
            automation_data=automation_data,
            framework="playwright",
            language="typescript",
            ai_provider="openai"
        )
        
        # Save the generated script
        output_file = "example_outputs/generated_playwright_test.ts"
        with open(output_file, 'w') as f:
            f.write(playwright_script)
        
        print(f"✓ Generated Playwright script: {output_file}")
        print(f"  Script length: {len(playwright_script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Failed to generate Playwright script: {e}")
    
    # Method 2: Generate Selenium script for comparison
    print("\n--- Method 2: Different Framework ---")
    try:
        selenium_script = btt.convert(
            automation_data=automation_data,
            framework="selenium",
            ai_provider="openai"
        )
        
        # Save the generated script
        output_file = "example_outputs/generated_selenium_test.py"
        with open(output_file, 'w') as f:
            f.write(selenium_script)
        
        print(f"✓ Generated Selenium script: {output_file}")
        print(f"  Script length: {len(selenium_script.splitlines())} lines")
        
    except Exception as e:
        print(f"✗ Failed to generate Selenium script: {e}")


def advanced_example():
    """Demonstrate advanced usage with custom configuration."""
    print("\n=== Advanced Browse-to-Test Example ===\n")
    
    # Create custom configuration using ConfigBuilder
    config = btt.ConfigBuilder() \
        .framework("playwright") \
        .ai_provider("openai", model="gpt-4") \
        .language("python") \
        .include_assertions(True) \
        .include_error_handling(True) \
        .temperature(0.1) \
        .sensitive_data_keys(["username", "password"]) \
        .enable_ai_analysis(True) \
        .debug(True) \
        .build()
    
    print("✓ Configuration built successfully")
    
    # Create converter with custom configuration
    converter = btt.E2eTestConverter(config)
    
    # Get available options
    print("\nAvailable options:")
    try:
        ai_providers = btt.list_ai_providers()
        frameworks = btt.list_frameworks()
        print(f"  AI Providers: {', '.join(ai_providers)}")
        print(f"  Frameworks: {', '.join(frameworks)}")
    except Exception as e:
        print(f"  Unable to list options: {e}")
    
    # Create automation data
    automation_data = create_sample_automation_data()
    
    # Generate test script with full analysis
    print("\n--- Generating Test Script with Custom Configuration ---")
    try:
        generated_script = converter.convert(automation_data)
        
        # Save the script
        output_file = "example_outputs/generated_advanced_test.py"
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
    
    automation_data = create_sample_automation_data()
    frameworks = ["playwright", "selenium"]
    
    print("Generating scripts for multiple frameworks...")
    
    for framework in frameworks:
        try:
            script = btt.convert(
                automation_data=automation_data,
                framework=framework,
                ai_provider="openai"
            )
            
            output_file = f"example_outputs/generated_{framework}_multi.py"
            with open(output_file, 'w') as f:
                f.write(script)
                
            print(f"✓ {framework}: {output_file} ({len(script.splitlines())} lines)")
            
        except Exception as e:
            print(f"✗ {framework}: Failed - {e}")


def load_from_file_example():
    """Demonstrate loading automation data from file."""
    print("\n=== Load from File Example ===\n")
    
    # Save sample data to file
    automation_data = create_sample_automation_data()
    data_file = "example_outputs/sample_automation_data.json"
    
    with open(data_file, 'w') as f:
        json.dump(automation_data, f, indent=2)
    
    print(f"Saved sample data to: {data_file}")
    
    # Load and convert from file (read data manually for now)
    try:
        with open(data_file, 'r') as f:
            loaded_data = json.load(f)
        
        script = btt.convert(
            automation_data=loaded_data,
            framework="playwright",
            include_assertions=True,
            add_comments=True
        )
        
        output_file = "example_outputs/generated_from_file.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Generated script from file: {output_file}")
        
    except Exception as e:
        print(f"✗ Failed to generate from file: {e}")
    
    # Clean up
    if os.path.exists(data_file):
        os.remove(data_file)


def incremental_session_example():
    """Demonstrate incremental session usage."""
    print("\n=== Incremental Session Example ===\n")
    
    try:
        # Create configuration for incremental session
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai") \
            .language("python") \
            .build()
        
        # Start incremental session
        session = btt.IncrementalSession(config)
        
        # Start the session
        result = session.start(target_url="https://example.com")
        print(f"✓ Session started: {result.success}")
        
        # Add steps incrementally
        automation_data = create_sample_automation_data()
        for i, step in enumerate(automation_data[:3]):  # Just first 3 steps
            result = session.add_step(step)
            print(f"✓ Added step {i+1}: {len(result.current_script.splitlines())} lines")
        
        # Finalize the session
        final_result = session.finalize()
        if final_result.success:
            output_file = "example_outputs/generated_incremental_test.py"
            with open(output_file, 'w') as f:
                f.write(final_result.current_script)
            print(f"✓ Finalized incremental test: {output_file}")
        else:
            print(f"✗ Failed to finalize session: {final_result.error}")
            
    except Exception as e:
        print(f"✗ Incremental session failed: {e}")


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
        incremental_session_example()
        
        print("\n" + "=" * 40)
        print("Examples completed! Check the generated files:")
        
        # List generated files
        for file in Path("example_outputs").glob("generated_*.py"):
            size = file.stat().st_size
            print(f"  - {file.name} ({size} bytes)")
        
    except Exception as e:
        print(f"\nExample execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 