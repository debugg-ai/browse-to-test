#!/usr/bin/env python3
"""
Test the async usage example with detailed logging enabled.
"""

import asyncio
import logging
import os
import time
from pathlib import Path

# Configure detailed logging BEFORE importing browse_to_test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S.%f'
)

# Enable detailed logging for all browse_to_test modules
logging.getLogger('browse_to_test').setLevel(logging.INFO)

import browse_to_test as btt
from dotenv import load_dotenv

load_dotenv()

# Test data from the example
REAL_AUTOMATION_STEPS = [
    {
        "model_output": {
            "thinking": 'Starting by navigating to the target homepage to begin verification process.',
            "action": [{"go_to_url": {"url": "https://debugg.ai"}}]
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": 'Successfully navigated to homepage and found Sandbox header text visible.'
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": []
        },
        "metadata": {
            "step_start_time": 1753997156.1953292,
            "step_end_time": 1753997203.220958,
            "step_number": 1,
        },
    },
    {
        "model_output": {
            "thinking": "Now I need to locate and click on the main navigation or header element.",
            "action": [{"click_element": {"index": 0}}]
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Clicked on header element to explore the page structure."
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": [{
                "xpath": "//header//h1",
                "css_selector": "header h1",
                "text_content": "Debugg AI",
                "attributes": {
                    "class": "text-2xl font-bold text-gray-900"
                }
            }]
        },
        "metadata": {
            "step_start_time": 1753997350.8411188,
            "step_end_time": 1753997369.5740314,
            "step_number": 2,
        },
    }
]

async def test_with_ai_enabled():
    """Test with AI analysis enabled to see API calls."""
    print("🔍 Testing with AI analysis enabled...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found. Testing without AI.")
        config = btt.ConfigBuilder().framework("playwright").enable_ai_analysis(False).build()
    else:
        print(f"✅ OpenAI API key found. Enabling AI analysis.")
        config = btt.ConfigBuilder().framework("playwright").enable_ai_analysis(True).ai_provider("openai").build()
    
    session = btt.AsyncIncrementalSession(config)
    
    start_time = time.time()
    
    try:
        # Start session
        print(f"\n⏰ {time.strftime('%H:%M:%S')} - Starting session...")
        result = await asyncio.wait_for(session.start("https://debugg.ai"), timeout=30.0)
        
        if not result.success:
            print(f"❌ Session start failed: {result.validation_issues}")
            return False
        
        print(f"✅ Session started")
        
        # Add steps with AI analysis
        task_ids = []
        for i, step_data in enumerate(REAL_AUTOMATION_STEPS):
            print(f"\n⏰ {time.strftime('%H:%M:%S')} - Adding step {i + 1}...")
            
            result = await asyncio.wait_for(
                session.add_step_async(step_data, wait_for_completion=False),
                timeout=30.0
            )
            
            if result.success and "task_id" in result.metadata:
                task_ids.append(result.metadata["task_id"])
                print(f"✅ Step {i + 1} queued - Task ID: {result.metadata['task_id']}")
            else:
                print(f"❌ Step {i + 1} failed: {result.validation_issues}")
        
        print(f"\n⏰ {time.strftime('%H:%M:%S')} - Waiting for all tasks to complete...")
        
        # Wait for completion
        final_result = await asyncio.wait_for(session.wait_for_all_tasks(timeout=120), timeout=130)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        if final_result.success:
            print(f"✅ All tasks completed in {total_duration:.2f}s")
            print(f"📄 Generated script: {len(final_result.current_script)} characters")
            return True
        else:
            print(f"❌ Tasks failed: {final_result.validation_issues}")
            return False
            
    except asyncio.TimeoutError:
        end_time = time.time()
        total_duration = end_time - start_time
        print(f"⏰ Test timed out after {total_duration:.2f}s")
        return False
    except Exception as e:
        end_time = time.time()
        total_duration = end_time - start_time
        print(f"❌ Test failed after {total_duration:.2f}s: {e}")
        return False
    finally:
        try:
            await asyncio.wait_for(session.finalize_async(), timeout=30.0)
        except:
            pass

async def main():
    """Run the test with detailed logging."""
    print("🚀 Testing Async Usage with Enhanced Logging")
    print("=" * 60)
    
    overall_start = time.time()
    success = await test_with_ai_enabled()
    overall_end = time.time()
    overall_duration = overall_end - overall_start
    
    print(f"\n{'='*60}")
    print(f"🏁 Test completed in {overall_duration:.2f}s - {'✅ Success' if success else '❌ Failed'}")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())