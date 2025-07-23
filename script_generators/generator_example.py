#!/usr/bin/env python3
"""
Example usage of PlaywrightTestGenerator

This script demonstrates how to use the PlaywrightTestGenerator class
to create Playwright test scripts with assertions and validations.
"""

import json
from playwright_test_generator import PlaywrightTestGenerator


def create_sample_history():
    """Creates a sample agent history for demonstration."""
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
                        "highlight_index": 0
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
                        "highlight_index": 0
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


def main():
    """Main function demonstrating PlaywrightTestGenerator usage."""
    
    # Sample agent history
    history = create_sample_history()
    
    # Sensitive data configuration
    sensitive_keys = ["username", "password"]
    
    # Test-specific configuration
    test_config = {
        "test_timeout": 15000,  # 15 seconds
        "screenshot_on_failure": True,
        "validate_page_loads": True,
        "check_console_errors": True,
        "strict_assertions": False  # Set to True for strict mode
    }
    
    # Create the test generator
    test_generator = PlaywrightTestGenerator(
        history_list=history,
        sensitive_data_keys=sensitive_keys,
        test_config=test_config
    )
    
    # Generate the test script
    test_script_content = test_generator.generate_script_content()
    
    # Save the generated test script
    output_file = "generated_test_script.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_script_content)
    
    print(f"✓ Test script generated successfully: {output_file}")
    print("\nFeatures included in the generated test script:")
    print("- Element visibility assertions")
    print("- Page load validations")
    print("- Console error checking")
    print("- URL validation")
    print("- Input value verification")
    print("- Screenshot capture on failures")
    print("- Scroll position validation")
    print("- Download verification")
    print("- Final test result reporting")
    
    print(f"\nTo run the generated test script:")
    print(f"python {output_file}")
    
    print(f"\nTest configuration used:")
    for key, value in test_config.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main() 