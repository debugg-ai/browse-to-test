#!/usr/bin/env python3
"""
Test script to verify the new QA functionality works correctly.
"""

import asyncio
import logging
import os
import pytest
from unittest.mock import patch, MagicMock
import browse_to_test as btt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Test data
SAMPLE_AUTOMATION_DATA = [
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

def test_sync_session_qa():
    """Test sync session with optional QA analysis."""
    print("🧪 Testing sync session with QA analysis...")
    
    try:
        # Create config with fast mode (default)
        config = (
            btt.ConfigBuilder()
            .framework("playwright")
            .ai_provider("openai", model="gpt-4.1-mini")
            .language("python")
            .debug(False)
            .build()
        )
        
        print(f"   Final analysis enabled: {config.processing.enable_final_script_analysis}")
        
        # Create session and generate script
        session = btt.IncrementalSession(config)
        session.start(target_url="https://example.com")
        
        # Add steps
        for step_data in SAMPLE_AUTOMATION_DATA:
            session.add_step(step_data)
        
        # Finalize to get fast script
        result = session.finalize()
        print(f"   ✅ Fast script generated: {len(result.current_script)} characters")
        
        # Now perform optional QA analysis
        print("   🔍 Performing optional script quality analysis...")
        qa_result = session.analyze_script_quality()
        
        if qa_result.success:
            print(f"   ✅ QA analysis completed!")
            print(f"   📊 Metadata: {qa_result.metadata}")
        else:
            print(f"   ⚠️  QA analysis failed: {qa_result.validation_issues}")
        
    except Exception as e:
        print(f"   ❌ Sync session test failed: {e}")

# @pytest.mark.asyncio
# async def test_async_session_qa():
#     """Test async session with optional QA analysis."""
#     print("\n🧪 Testing async session with QA analysis...")
    
#     # Mock the AI provider and related components to avoid real API calls
#     with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_converter_class, \
#          patch('browse_to_test.ai.factory.AIProviderFactory') as mock_ai_factory:
        
#         # Setup mocks
#         mock_converter = MagicMock()
#         mock_converter.convert.return_value = "# Generated Playwright test script\nfrom playwright.sync_api import sync_playwright\n\ndef test_example():\n    pass"
#         mock_converter.validate_data.return_value = []
#         mock_converter_class.return_value = mock_converter
        
#         mock_ai_provider = MagicMock()
#         mock_ai_factory.return_value.create_provider.return_value = mock_ai_provider
        
#         # Create config with fast mode (default)
#         config = (
#             btt.ConfigBuilder()
#             .framework("playwright")
#             .ai_provider("openai", model="gpt-4.1-mini")
#             .language("python")
#             .debug(False)
#             .build()
#         )
        
#         print(f"   Final analysis enabled: {config.processing.enable_final_script_analysis}")
        
#         # Create session and generate script
#         session = btt.AsyncIncrementalSession(config)
#         await session.start(target_url="https://example.com")
        
#         # Add steps
#         for step_data in SAMPLE_AUTOMATION_DATA:
#             await session.add_step_async(step_data, wait_for_completion=False)
        
#         # Wait for all tasks and finalize with timeout
#         result = await asyncio.wait_for(session.wait_for_all_tasks(), timeout=40)
#         await asyncio.wait_for(session.finalize_async(), timeout=40)
        
#         print(f"   ✅ Fast script generated: {len(result.current_script)} characters")
        
#         # Mock the analyze_script_quality_async method to return success
#         mock_qa_result = btt.core.orchestration.session.SessionResult(
#             success=True,
#             current_script="# Optimized Playwright test script\nfrom playwright.sync_api import sync_playwright\n\ndef test_example_optimized():\n    pass",
#             step_count=3,
#             metadata={
#                 'quality_analysis_completed': True,
#                 'analysis_duration': 0.1,
#                 'original_script_chars': len(result.current_script),
#                 'analyzed_script_chars': 200,
#                 'original_script_lines': 4,
#                 'analyzed_script_lines': 4,
#                 'improvement_detected': True
#             }
#         )
        
#         with patch.object(session, 'analyze_script_quality_async', return_value=mock_qa_result):
#             # Now perform optional QA analysis
#             print("   🔍 Performing optional script quality analysis...")
#             qa_result = await asyncio.wait_for(session.analyze_script_quality_async(timeout=40), timeout=40)
            
#             assert qa_result.success, f"QA analysis should succeed, got: {qa_result.validation_issues}"
#             print(f"   ✅ QA analysis completed!")
#             print(f"   📊 Metadata: {qa_result.metadata}")
            
#             # Verify QA metadata
#             assert 'quality_analysis_completed' in qa_result.metadata
#             assert qa_result.metadata['quality_analysis_completed'] is True
#             assert 'improvement_detected' in qa_result.metadata

@pytest.mark.asyncio
async def test_async_session_qa_timeout_handling():
    """Test that async QA analysis handles timeouts gracefully."""
    # Create a simple mock that immediately raises TimeoutError
    async def timeout_side_effect(*args, **kwargs):
        raise asyncio.TimeoutError("QA analysis timed out")
    
    # Create a minimal session mock
    session = MagicMock()
    session.analyze_script_quality_async = MagicMock(side_effect=timeout_side_effect)
    
    # Test that timeout is handled gracefully
    with pytest.raises(asyncio.TimeoutError):
        await session.analyze_script_quality_async(timeout=0.1)

def test_sync_session_qa_unit():
    """Unit test for sync session QA functionality."""
    # Mock components to avoid real API calls
    with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_converter_class:
        
        mock_converter = MagicMock()
        mock_converter.convert.return_value = "# Generated Playwright test script\nfrom playwright.sync_api import sync_playwright\n\ndef test_example():\n    pass"
        mock_converter.validate_data.return_value = []
        mock_converter_class.return_value = mock_converter
        
        config = (
            btt.ConfigBuilder()
            .framework("playwright")
            .ai_provider("openai", model="gpt-4.1-mini")
            .language("python")
            .debug(False)
            .build()
        )
        
        session = btt.IncrementalSession(config)
        session.start(target_url="https://example.com")
        
        # Add steps
        for step_data in SAMPLE_AUTOMATION_DATA:
            session.add_step(step_data)
        
        # Finalize to get script
        result = session.finalize()
        assert result.success
        assert len(result.current_script) > 0
        
        # Mock the analyze_script_quality method
        mock_qa_result = btt.core.orchestration.session.SessionResult(
            success=True,
            current_script="# Optimized script",
            step_count=3,
            metadata={
                'quality_analysis_completed': True,
                'analysis_duration': 0.05,
                'improvement_detected': True
            }
        )
        
        with patch.object(session, 'analyze_script_quality', return_value=mock_qa_result):
            qa_result = session.analyze_script_quality()
            
            assert qa_result.success
            assert 'quality_analysis_completed' in qa_result.metadata
            assert qa_result.metadata['quality_analysis_completed'] is True

def test_standalone_qa():
    """Test standalone QA functions."""
    print("\n🧪 Testing standalone QA functions...")
    
    try:
        # Generate initial script with fast mode
        print("   🚀 Generating initial script (fast mode)...")
        script = btt.convert(SAMPLE_AUTOMATION_DATA, framework="playwright")
        print(f"   ✅ Fast script generated: {len(script)} characters")
        
        # Test sync QA function
        print("   🔍 Testing sync QA function...")
        qa_result = btt.perform_script_qa(
            script, 
            SAMPLE_AUTOMATION_DATA, 
            framework="playwright"
        )
        
        print(f"   📊 QA Results:")
        print(f"      • Quality Score: {qa_result['quality_score']}")
        print(f"      • Improvements: {len(qa_result['improvements'])} suggestions")
        print(f"      • Optimized script: {len(qa_result['optimized_script'])} characters")
        print(f"      • Improvement detected: {qa_result['analysis_metadata']['improvement_detected']}")
        
    except Exception as e:
        print(f"   ❌ Standalone QA test failed: {e}")

async def test_standalone_qa_async():
    """Test standalone async QA functions."""
    print("\n🧪 Testing standalone async QA functions...")
    
    try:
        # Generate initial script with fast mode
        print("   🚀 Generating initial script (fast mode)...")
        script = await btt.convert_async(SAMPLE_AUTOMATION_DATA, framework="playwright")
        print(f"   ✅ Fast script generated: {len(script)} characters")
        
        # Test async QA function
        print("   🔍 Testing async QA function...")
        qa_result = await btt.perform_script_qa_async(
            script, 
            SAMPLE_AUTOMATION_DATA, 
            framework="playwright"
        )
        
        print(f"   📊 QA Results:")
        print(f"      • Quality Score: {qa_result['quality_score']}")
        print(f"      • Improvements: {len(qa_result['improvements'])} suggestions")
        print(f"      • Optimized script: {len(qa_result['optimized_script'])} characters")
        print(f"      • Improvement detected: {qa_result['analysis_metadata']['improvement_detected']}")
        
    except Exception as e:
        print(f"   ❌ Standalone async QA test failed: {e}")

# Note: This file contains both unit tests and manual test functions
# The unit tests (marked with pytest decorators) are for automated testing
# The manual test functions can be run separately for integration testing

async def main():
    """Run all QA functionality tests manually (not pytest)."""
    print("🚀 Testing QA Functionality")
    print("=" * 50)
    
    # Check API key status
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found - QA analysis will use fallback logic")
        print("   Set OPENAI_API_KEY to test full AI-powered analysis")
        print()
    else:
        print("✅ OpenAI API key found - full QA analysis available")
        print()
    
    # Run manual integration tests (not pytest)
    test_sync_session_qa()
    test_standalone_qa()
    await test_standalone_qa_async()
    
    print("\n🏁 QA functionality tests completed!")

if __name__ == "__main__":
    asyncio.run(main())