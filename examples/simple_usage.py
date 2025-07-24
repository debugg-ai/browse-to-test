#!/usr/bin/env python3
"""
Simple usage examples for the new browse-to-test API.

This example demonstrates the streamlined, user-friendly API
that makes it easy to get started with test generation.
"""

import browse_to_test as btt

# Sample automation data - what you'd get from browser automation
sample_data = [
    {
        "model_output": {
            "action": [
                {"go_to_url": {"url": "https://example.com"}}
            ]
        },
        "state": {"interacted_element": []}
    },
    {
        "model_output": {
            "action": [
                {"input_text": {"index": 0, "text": "test@example.com"}}
            ]
        },
        "state": {
            "interacted_element": [{
                "xpath": "//input[@type='email']",
                "css_selector": "input[type='email']",
                "attributes": {"type": "email", "name": "email"}
            }]
        }
    },
    {
        "model_output": {
            "action": [
                {"click": {"index": 0}}
            ]
        },
        "state": {
            "interacted_element": [{
                "xpath": "//button[@type='submit']", 
                "css_selector": "button[type='submit']",
                "attributes": {"type": "submit", "class": "btn-primary"}
            }]
        }
    }
]

def main():
    print("🚀 Browse-to-Test Simple Examples\n")
    
    # ========================================
    # 1. SIMPLEST POSSIBLE USAGE
    # ========================================
    print("1️⃣ Simplest usage - one line conversion:")
    print("=" * 50)
    
    # Convert to Playwright with just one line
    script = btt.convert(sample_data, framework="playwright")
    print("Generated Playwright script:")
    print(script[:200] + "..." if len(script) > 200 else script)
    print()
    
    # ========================================
    # 2. WITH BASIC OPTIONS
    # ========================================
    print("2️⃣ With basic options:")
    print("=" * 30)
    
    # Add some common options
    script = btt.convert(
        sample_data,
        framework="selenium",
        language="python",
        include_assertions=True,
        include_error_handling=True
    )
    print(f"Generated Selenium script ({len(script)} characters)")
    print()
    
    # ========================================
    # 3. USING CONFIG BUILDER (ADVANCED)
    # ========================================
    print("3️⃣ Using ConfigBuilder for advanced configuration:")
    print("=" * 50)
    
    # Build custom configuration
    config = btt.ConfigBuilder() \
        .framework("playwright") \
        .language("python") \
        .include_assertions(True) \
        .include_error_handling(True) \
        .timeout(15000) \
        .debug(False) \
        .build()
    
    # Create converter with custom config
    converter = btt.E2eTestConverter(config)
    script = converter.convert(sample_data)
    print(f"Generated script with custom config ({len(script)} characters)")
    print()
    
    # ========================================
    # 4. INCREMENTAL SESSION
    # ========================================
    print("4️⃣ Incremental session for live test generation:")
    print("=" * 50)
    
    # Start an incremental session
    session_config = btt.ConfigBuilder().framework("playwright").build()
    session = btt.IncrementalSession(session_config)
    
    # Start the session
    result = session.start("https://example.com")
    print(f"Session started: {result.success}")
    
    # Add steps one by one
    for i, step in enumerate(sample_data):
        result = session.add_step(step)
        print(f"Added step {i+1}: {result.success} ({result.lines_added} lines added)")
    
    # Finalize and get the complete script
    final_result = session.finalize()
    print(f"Session finalized: {final_result.success}")
    print(f"Total steps: {final_result.step_count}")
    print(f"Final script length: {len(final_result.current_script)} characters")
    print()
    
    # ========================================
    # 5. UTILITY FUNCTIONS
    # ========================================
    print("5️⃣ Utility functions:")
    print("=" * 25)
    
    # List available frameworks and AI providers
    frameworks = btt.list_frameworks()
    providers = btt.list_ai_providers()
    
    print(f"Available frameworks: {frameworks}")
    print(f"Available AI providers: {providers}")
    print()
    
    # ========================================
    # 6. ERROR HANDLING
    # ========================================
    print("6️⃣ Error handling example:")
    print("=" * 30)
    
    try:
        # Try with invalid data
        invalid_data = [{"invalid": "data"}]
        script = btt.convert(invalid_data, framework="playwright")
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")
    print()
    
    print("✅ All examples completed successfully!")


if __name__ == "__main__":
    main() 