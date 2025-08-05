#!/usr/bin/env python3
"""
Test script to verify enhanced logging functionality.

This script configures detailed logging and runs a quick test
to demonstrate the timing and performance tracking features.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Enable debug logging for specific modules
logging.getLogger('browse_to_test.ai').setLevel(logging.INFO)
logging.getLogger('browse_to_test.core.orchestration').setLevel(logging.INFO)
logging.getLogger('browse_to_test.core.processing').setLevel(logging.INFO)

print("🚀 Testing Enhanced Logging System")
print("=" * 50)

# Simple test data
SIMPLE_TEST_DATA = [
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
            "step_number": 1
        }
    },
    {
        "model_output": {
            "action": [{"click_element": {"index": 0}}]
        },
        "state": {
            "url": "https://example.com",
            "title": "Example Domain",
            "interacted_element": [{
                "xpath": "//button[@id='test-button']",
                "css_selector": "#test-button",
                "text_content": "Click Me"
            }]
        },
        "metadata": {
            "step_number": 2
        }
    }
]

async def test_basic_conversion():
    """Test basic conversion with logging."""
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Starting basic conversion test...")
    
    try:
        import browse_to_test as btt
        
        # Test without AI (fast)
        config = btt.ConfigBuilder().framework("playwright").enable_ai_analysis(False).build()
        converter = btt.E2eTestConverter(config)
        
        script = converter.convert(SIMPLE_TEST_DATA)
        print(f"✅ Basic conversion completed - Generated {len(script)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Basic conversion failed: {e}")
        return False

async def test_async_session():
    """Test async session with minimal data."""
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Starting async session test...")
    
    try:
        import browse_to_test as btt
        
        # Use a minimal config without AI to focus on session tracking
        config = btt.ConfigBuilder().framework("playwright").enable_ai_analysis(False).build()
        session = btt.AsyncIncrementalSession(config)
        
        # Start session
        result = await asyncio.wait_for(session.start("https://example.com"), timeout=10.0)
        if not result.success:
            print(f"❌ Session start failed: {result.validation_issues}")
            return False
        
        print("✅ Session started successfully")
        
        # Add steps without waiting
        for i, step_data in enumerate(SIMPLE_TEST_DATA):
            result = await asyncio.wait_for(
                session.add_step_async(step_data, wait_for_completion=False),
                timeout=10.0
            )
            if result.success:
                print(f"✅ Step {i+1} queued successfully")
            else:
                print(f"❌ Step {i+1} queue failed: {result.validation_issues}")
        
        # Wait for completion
        final_result = await asyncio.wait_for(session.wait_for_all_tasks(timeout=30), timeout=35)
        
        if final_result.success:
            print(f"✅ All tasks completed - Generated {len(final_result.current_script)} characters")
            return True
        else:
            print(f"❌ Task completion failed: {final_result.validation_issues}")
            return False
            
    except asyncio.TimeoutError:
        print("❌ Async session test timed out")
        return False
    except Exception as e:
        print(f"❌ Async session test failed: {e}")
        return False

async def main():
    """Run all logging tests."""
    print(f"Starting enhanced logging tests at {datetime.now().strftime('%H:%M:%S')}")
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Basic conversion
    if await test_basic_conversion():
        success_count += 1
    
    # Test 2: Async session
    if await test_async_session():
        success_count += 1
    
    print(f"\n{'='*50}")
    print(f"🏁 Tests completed: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Enhanced logging is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)