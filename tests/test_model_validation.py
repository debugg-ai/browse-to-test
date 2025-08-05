#!/usr/bin/env python3
"""
Test script to verify improved error messaging for unsupported models.
"""

import logging
import os
import browse_to_test as btt

# Configure logging to see error messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Test data
SIMPLE_TEST_DATA = [
    {
        "model_output": {
            "action": [{"go_to_url": {"url": "https://example.com"}}]
        },
        "state": {
            "url": "https://example.com",
            "title": "Example Domain",
            "interacted_element": []
        }
    }
]

def test_unsupported_model():
    """Test with an unsupported model to see error messaging."""
    print("🧪 Testing unsupported model error messaging...")
    
    # Test with an unsupported model
    unsupported_model = "gpt-5-super-turbo"  # This doesn't exist
    
    try:
        config = (
            btt.ConfigBuilder()
            .framework("playwright")
            .ai_provider("openai", model=unsupported_model)
            .language("python")
            .enable_ai_analysis(True)
            .debug(True)
            .build()
        )
        
        print(f"🔧 Config created with model: {config.ai.model}")
        
        # Try to create a converter (this should trigger the error)
        converter = btt.E2eTestConverter(config)
        
        # Try to convert some data
        result = converter.convert(SIMPLE_TEST_DATA)
        
        print(f"⚠️  Conversion completed but AI analysis likely failed silently")
        print(f"Result length: {len(result)} characters")
        
    except Exception as e:
        print(f"❌ Exception caught: {e}")

def test_supported_model():
    """Test with a supported model for comparison."""
    print("\n🧪 Testing supported model for comparison...")
    
    # Test with a supported model
    supported_model = "gpt-4.1-mini"  # From your updated supported models list
    
    try:
        config = (
            btt.ConfigBuilder()
            .framework("playwright")
            .ai_provider("openai", model=supported_model)
            .language("python")
            .enable_ai_analysis(True)
            .debug(True)
            .build()
        )
        
        print(f"🔧 Config created with model: {config.ai.model}")
        
        # Try to create a converter
        converter = btt.E2eTestConverter(config)
        
        # Try to convert some data (without API key, should show clear message)
        result = converter.convert(SIMPLE_TEST_DATA)
        
        print(f"✅ Conversion completed successfully")
        print(f"Result length: {len(result)} characters")
        
    except Exception as e:
        print(f"❌ Exception caught: {e}")

def main():
    """Run the error messaging tests."""
    print("🚀 Testing AI Provider Error Messaging")
    print("=" * 50)
    
    # Test unsupported model
    test_unsupported_model()
    
    # Test supported model  
    test_supported_model()
    
    print(f"\n🏁 Error messaging tests completed!")

if __name__ == "__main__":
    main()