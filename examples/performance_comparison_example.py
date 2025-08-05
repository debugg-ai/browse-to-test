#!/usr/bin/env python3
"""
Performance Comparison Example - Fast vs Thorough Mode

This example demonstrates the performance difference between:
1. Fast mode (no final analysis) - default for performance
2. Thorough mode (with final analysis) - optional for quality grading
"""

import asyncio
import time
import os
import logging
from pathlib import Path
import browse_to_test as btt

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

load_dotenv()

# Sample automation data
SAMPLE_STEPS = [
    {
        "model_output": {
            "action": [{"go_to_url": {"url": "https://example.com"}}]
        },
        "state": {
            "url": "https://example.com",
            "title": "Example Domain"
        }
    },
    {
        "model_output": {
            "action": [{"click_element": {"index": 0}}]
        },
        "state": {
            "url": "https://example.com",
            "title": "Example Domain"
        }
    },
    {
        "model_output": {
            "action": [{"done": {}}]
        },
        "state": {
            "url": "https://example.com",
            "title": "Example Domain"
        }
    }
]

async def run_fast_mode():
    """Run with fast mode (default - no final analysis)."""
    print("🏃‍♂️ Running FAST MODE (default - no final analysis)...")
    
    # Default config has enable_final_script_analysis=False
    config = (
        btt.ConfigBuilder()
        .framework("playwright")
        .ai_provider("openai", model="gpt-4.1-mini")
        .language("python")
        .enable_ai_analysis(True)
        .debug(False)  # Reduce noise
        .build()
    )
    
    # Verify the setting
    print(f"   Final analysis enabled: {config.processing.enable_final_script_analysis}")
    
    start_time = time.time()
    
    session = btt.AsyncIncrementalSession(config)
    await session.start(target_url="https://example.com")
    
    # Add all steps
    for i, step_data in enumerate(SAMPLE_STEPS):
        await session.add_step_async(step_data, wait_for_completion=False)
    
    # Wait for completion
    result = await session.wait_for_all_tasks()
    await session.finalize_async()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   ✅ Fast mode completed in {duration:.2f}s")
    print(f"   📄 Generated script: {len(result.current_script)} characters")
    
    return duration, len(result.current_script)

async def run_thorough_mode():
    """Run with thorough mode (optional final analysis for grading)."""
    print("🎯 Running THOROUGH MODE (with final analysis for grading)...")
    
    # Enable final script analysis for detailed grading
    config = (
        btt.ConfigBuilder()
        .framework("playwright")
        .ai_provider("openai", model="gpt-4.1-mini")
        .language("python")
        .enable_ai_analysis(True)
        .enable_final_script_analysis(True)  # Enable the expensive analysis
        .debug(False)  # Reduce noise
        .build()
    )
    
    # Verify the setting
    print(f"   Final analysis enabled: {config.processing.enable_final_script_analysis}")
    
    start_time = time.time()
    
    session = btt.AsyncIncrementalSession(config)
    await session.start(target_url="https://example.com")
    
    # Add all steps
    for i, step_data in enumerate(SAMPLE_STEPS):
        await session.add_step_async(step_data, wait_for_completion=False)
    
    # Wait for completion
    result = await session.wait_for_all_tasks()
    await session.finalize_async()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   ✅ Thorough mode completed in {duration:.2f}s")
    print(f"   📄 Generated script: {len(result.current_script)} characters")
    
    return duration, len(result.current_script)

async def main():
    """Compare performance between fast and thorough modes."""
    print("🚀 Browse-to-Test Performance Comparison")
    print("=" * 60)
    print("Comparing fast mode (default) vs thorough mode (optional)")
    print()
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found - running without AI analysis")
        print("   (You'll still see the performance difference in script generation)")
        print()
    else:
        print("✅ OpenAI API key found - full AI analysis available")
        print()
    
    try:
        # Run fast mode
        fast_duration, fast_chars = await run_fast_mode()
        print()
        
        # Run thorough mode only if API key is available
        if api_key:
            thorough_duration, thorough_chars = await run_thorough_mode()
            print()
            
            # Compare results
            print("📊 PERFORMANCE COMPARISON:")
            print(f"   Fast mode:     {fast_duration:.2f}s ({fast_chars} chars)")
            print(f"   Thorough mode: {thorough_duration:.2f}s ({thorough_chars} chars)")
            
            if thorough_duration > fast_duration:
                speedup = thorough_duration / fast_duration
                print(f"   🏃‍♂️ Fast mode is {speedup:.1f}x faster!")
            
            print("\n💡 RECOMMENDATION:")
            print("   • Use fast mode (default) for regular development")
            print("   • Use thorough mode only when you need detailed script analysis/grading")
        else:
            print("💡 RECOMMENDATION:")
            print("   • Set OPENAI_API_KEY to see the full performance comparison")
            print("   • Even without AI, you can see fast script generation in action")
    
    except Exception as e:
        print(f"❌ Error during comparison: {e}")

if __name__ == "__main__":
    asyncio.run(main())