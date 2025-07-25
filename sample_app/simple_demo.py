#!/usr/bin/env python3
"""
Simple Browse-to-Test Demo

A minimal demo script to quickly test the basic functionality of the 
live browse-to-test library.

Usage:
    python simple_demo.py
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

try:
    import browse_to_test as btt
    print("✅ browse-to-test library imported successfully!")
except ImportError:
    print("❌ Error: browse-to-test library not found!")
    print("📦 Please install: pip install browse-to-test[all]")
    sys.exit(1)

def main():
    print("🚀 Browse-to-Test Simple Demo\n")
    
    # Simple sample data
    sample_data = [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            },
            "state": {"interacted_element": []},
            "metadata": {"description": "Navigate to example.com"}
        },
        {
            "model_output": {
                "action": [{"input_text": {"text": "test@example.com", "index": 0}}]
            },
            "state": {
                "interacted_element": [{
                    "css_selector": "input[type='email']",
                    "attributes": {"type": "email", "name": "email"}
                }]
            },
            "metadata": {"description": "Enter email"}
        }
    ]
    
    print("📋 Sample automation data loaded")
    print(f"   Steps: {len(sample_data)}")
    print(f"   Actions: {sum(len(step['model_output']['action']) for step in sample_data)}")
    
    # Test 1: Simple conversion
    print("\n1️⃣ Testing simple conversion...")
    try:
        script = btt.convert(
            sample_data, 
            framework="playwright",
            ai_provider="openai",
            include_assertions=True
        )
        
        print(f"✅ Success! Generated {len(script)} characters")
        
        # Save the script
        with open("simple_demo_output.py", "w") as f:
            f.write(script)
        
        print("📄 Script saved to: simple_demo_output.py")
        
        # Show preview
        print("\n📖 Script preview:")
        print("-" * 40)
        print(script[:400] + "..." if len(script) > 400 else script)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    # Test 2: List available options
    print("\n2️⃣ Testing utility functions...")
    try:
        frameworks = btt.list_frameworks()
        providers = btt.list_ai_providers()
        
        print(f"✅ Available frameworks: {frameworks}")
        print(f"✅ Available AI providers: {providers}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: ConfigBuilder
    print("\n3️⃣ Testing ConfigBuilder...")
    try:
        config = btt.ConfigBuilder() \
            .framework("selenium") \
            .ai_provider("openai") \
            .language("python") \
            .include_error_handling(True) \
            .build()
        
        converter = btt.E2eTestConverter(config)
        script = converter.convert(sample_data)
        
        print(f"✅ ConfigBuilder success! Generated {len(script)} characters")
        
        # Save the script
        with open("config_demo_output.py", "w") as f:
            f.write(script)
        
        print("📄 Config script saved to: config_demo_output.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Simple demo completed!")
    print("\nGenerated files:")
    print("  - simple_demo_output.py")
    print("  - config_demo_output.py")
    
    # Check API key
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    print(f"\n🔑 API Key Status: {'✅ Set' if api_key_set else '❌ Not set'}")
    if not api_key_set:
        print("   Set OPENAI_API_KEY environment variable for full functionality")

if __name__ == "__main__":
    main() 