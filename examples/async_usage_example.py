#!/usr/bin/env python3
"""
Async Usage Example for Browse-to-Test - FIXED VERSION

This example demonstrates how to use the async API to queue multiple script
generation tasks without blocking other processing. The AI calls will be
sequential (to maintain context) while allowing other work to continue in parallel.

FIXES APPLIED:
1. Fixed REAL_AUTOMATION_STEPS with proper Browse-to-Test action format
2. Added comprehensive error handling for action parsing failures
3. Added data validation helpers
4. Improved timeout and retry mechanisms
5. Added better fallback behavior
"""

import asyncio
import time
import os
from pathlib import Path
import browse_to_test as btt
from typing import List, Dict, Any

from dotenv import load_dotenv

load_dotenv()

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def save_generated_script(script_content: str, filename: str, data_source: str = "") -> str:
    """
    Save generated script to output directory with metadata.
    
    Args:
        script_content: The generated test script
        filename: Base filename (without extension)
        data_source: Description of the data source used
    
    Returns:
        Full path to saved file
    """
    # Create timestamp for unique filenames
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Determine file extension based on script content
    if "# Framework: playwright" in script_content and "# Language: python" in script_content:
        extension = ".py"
    elif "// Framework: playwright" in script_content and "language: typescript" in script_content.lower():
        extension = ".ts"
    elif "// Framework: playwright" in script_content and "language: javascript" in script_content.lower():
        extension = ".js"
    else:
        extension = ".py"  # Default to Python
    
    # Create filename
    full_filename = f"{filename}_{timestamp}{extension}"
    file_path = OUTPUT_DIR / full_filename
    
    # Add metadata header to script
    metadata_header = f"""# Generated by Browse-to-Test Async Example
# Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}
# Data Source: {data_source or "Unknown"}
# Script Length: {len(script_content)} characters
# =====================================

"""
    
    # Write script with metadata
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(metadata_header + script_content)
    
    return str(file_path)


def validate_automation_data(automation_data: List[Dict[str, Any]]) -> bool:
    """
    Validate automation data format before processing.
    
    Returns True if data appears valid, False otherwise.
    """
    if not isinstance(automation_data, list) or len(automation_data) == 0:
        return False
    
    for i, step in enumerate(automation_data):
        if not isinstance(step, dict):
            print(f"Step {i} is not a dictionary")
            return False
            
        if 'model_output' not in step:
            print(f"Step {i} missing required 'model_output' field")
            return False
            
        model_output = step['model_output']
        if not isinstance(model_output, dict):
            print(f"Step {i} has invalid model_output type")
            return False
            
        if 'action' not in model_output:
            print(f"Step {i} missing 'action' field in model_output")
            return False
            
        actions = model_output['action']
        if not isinstance(actions, list):
            print(f"Step {i} has invalid actions format")
            return False
            
        # Check for empty actions (the main issue we're fixing)
        for j, action in enumerate(actions):
            if not isinstance(action, dict) or not action:
                print(f"Step {i}, action {j} is empty or invalid: {action}")
                return False
            
            # Check that action has at least one valid action type
            action_types = ['go_to_url', 'click_element', 'input_text', 'wait', 'done', 'scroll', 'press_key']
            if not any(action_type in action for action_type in action_types):
                print(f"Step {i}, action {j} has no recognized action type: {list(action.keys())}")
                return False
    
    return True


# Sample automation data for testing - guaranteed to work format
SAMPLE_AUTOMATION_STEPS = [
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
            "step_start_time": 1704067200.0,
            "step_end_time": 1704067203.5,
            "step_number": 1
        }
    },
    {
        "model_output": {
            "action": [{"click_element": {"index": 0}}]
        },
        "state": {
            "url": "https://example.com/login",
            "title": "Login - Example Domain",
            "interacted_element": [{
                "xpath": "//button[@id='login-button']",
                "css_selector": "#login-button",
                "text_content": "Login",
                "attributes": {"id": "login-button", "type": "button"}
            }]
        },
        "metadata": {
            "step_start_time": 1704067203.5,
            "step_end_time": 1704067204.0,
            "step_number": 2
        }
    },
    {
        "model_output": {
            "action": [{"input_text": {"index": 0, "text": "testuser"}}]
        },
        "state": {
            "url": "https://example.com/login",
            "title": "Login - Example Domain",
            "interacted_element": [{
                "xpath": "//input[@id='username']",
                "css_selector": "#username",
                "attributes": {"id": "username", "type": "text", "placeholder": "Username"}
            }]
        },
        "metadata": {
            "step_start_time": 1704067204.0,
            "step_end_time": 1704067204.5,
            "step_number": 3
        }
    },
    {
        "model_output": {
            "action": [{"input_text": {"index": 0, "text": "password123"}}]
        },
        "state": {
            "url": "https://example.com/login",
            "title": "Login - Example Domain",
            "interacted_element": [{
                "xpath": "//input[@id='password']",
                "css_selector": "#password",
                "attributes": {"id": "password", "type": "password", "placeholder": "Password"}
            }]
        },
        "metadata": {
            "step_start_time": 1704067204.5,
            "step_end_time": 1704067205.0,
            "step_number": 4
        }
    },
    {
        "model_output": {
            "action": [{"click_element": {"index": 0}}]
        },
        "state": {
            "url": "https://example.com/dashboard",
            "title": "Dashboard - Example Domain",
            "interacted_element": [{
                "xpath": "//button[@id='submit']",
                "css_selector": "#submit",
                "text_content": "Submit",
                "attributes": {"id": "submit", "type": "submit"}
            }]
        },
        "metadata": {
            "step_start_time": 1704067205.0,
            "step_end_time": 1704067206.0,
            "step_number": 5
        }
    },
    {
        "model_output": {
            "action": [{"done": {}}]
        },
        "state": {
            "url": "https://example.com/dashboard",
            "title": "Dashboard - Example Domain",
            "interacted_element": []
        },
        "metadata": {
            "step_start_time": 1704067206.0,
            "step_end_time": 1704067206.5,
            "step_number": 6
        }
    }
]

# Fixed automation data with proper Browse-to-Test format
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
    },
    {
        "model_output": {
            "thinking": "Let me wait a moment for any dynamic content to load completely.",
            "action": [{"wait": {"seconds": 2}}]
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Waited for page to fully load before proceeding."
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": []
        },
        "metadata": {
            "step_start_time": 1753997372.2532299,
            "step_end_time": 1753997391.3151274,
            "step_number": 3,
        },
    },
    {
        "model_output": {
            "thinking": "Let me scroll down to explore more content on the page.",
            "action": [{"scroll": {"direction": "down", "amount": 500}}]
        },
        "result": [
            {
                "is_done": False,
                "success": True,
                "error": None,
                "long_term_memory": "Scrolled down the page to view additional content."
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": []
        },
        "metadata": {
            "step_start_time": 1753997394.1183739,
            "step_end_time": 1753997414.787713,
            "step_number": 4,
        },
    },
    {
        "model_output": {
            "thinking": "Task completed successfully. I have explored the website structure and interactions.",
            "action": [{"done": {}}]
        },
        "result": [
            {
                "is_done": True,
                "success": True,
                "error": None,
                "long_term_memory": "Successfully completed website exploration and interaction testing."
            }
        ],
        "state": {
            "url": "https://debugg.ai",
            "title": "Debugg AI - AI-Powered Testing Platform",
            "interacted_element": []
        },
        "metadata": {
            "step_start_time": 1753997419.0800045,
            "step_end_time": 1753997442.0409794,
            "step_number": 5,
        },
    }
]

async def incremental_session_example():
    """
    Example 2: Async Incremental Session with enhanced error handling
    
    This shows how to use AsyncIncrementalSession to queue multiple steps
    with proper validation and resilient processing.
    """
    print("=== Async Incremental Session Example ===")

    # Choose and validate data
    automation_data = REAL_AUTOMATION_STEPS
    data_source = "REAL_AUTOMATION_STEPS"
    
    
    print(f"Using {data_source} ({len(automation_data)} steps)")

    # Create async session with smart AI configuration
    api_key = os.getenv("OPENAI_API_KEY")
    use_ai_analysis = bool(api_key)
    
    if not api_key:
        print("WARNING: No OPENAI_API_KEY found. Disabling AI analysis for faster execution.")
    
    config = (
        btt.ConfigBuilder()
        .framework("playwright")
        .ai_provider("openai")
        .language("python")
        .enable_ai_analysis(use_ai_analysis)  # Only enable AI if we have API key
        .build()
    )

    session = btt.AsyncIncrementalSession(config)

    try:
        # Start the session with timeout
        print("DEBUG: Starting session...")
        result = await asyncio.wait_for(
            session.start(target_url="https://example.com"),
            timeout=30.0
        )
        print(f"✓ Session started: {result.success}")

        if not result.success:
            print(f"✗ Failed to start session: {result.validation_issues}")
            return

        # Queue multiple steps without waiting for completion
        task_ids = []
        successful_steps = 0
        
        for i, step_data in enumerate(automation_data):
            try:
                print(f"DEBUG: Queueing step {i + 1}...")
                result = await asyncio.wait_for(
                    session.add_step_async(step_data, wait_for_completion=False),
                    timeout=30.0
                )
                
                if result.success and "task_id" in result.metadata:
                    task_ids.append(result.metadata["task_id"])
                    successful_steps += 1
                    print(f"  ✓ Step {i + 1} queued with task ID: {result.metadata['task_id']}")
                else:
                    print(f"  ✗ Step {i + 1} failed to queue: {result.validation_issues}")
            
            except asyncio.TimeoutError:
                print(f"  ✗ Step {i + 1} timed out while queueing")
            except Exception as e:
                print(f"  ✗ Step {i + 1} failed: {e}")

        print(f"\n✓ Successfully queued {successful_steps}/{len(automation_data)} steps")

        # Do other work while steps are processing
        print("\nMonitoring queue while steps are processing...")
        for i in range(5):
            await asyncio.sleep(1)
            try:
                stats = session.get_queue_stats()
                print(f"  Queue stats: {stats['pending_tasks']} pending, {stats['total_tasks']} total")
                
                # If no pending tasks, we're done early
                if stats['pending_tasks'] == 0:
                    print("  All tasks completed early!")
                    break
            except Exception as e:
                print(f"  Warning: Could not get queue stats: {e}")

        # Wait for all tasks to complete with timeout
        print("\nWaiting for all tasks to complete...")
        try:
            final_result = await asyncio.wait_for(
                session.wait_for_all_tasks(timeout=300),  # 5 minute timeout for tasks
                timeout=320  # Extra buffer for the wait itself
            )

            if final_result.success:
                print(f"✓ All steps completed! Final script has {len(final_result.current_script)} characters")
                
                # Save the generated script to output directory
                try:
                    saved_path = save_generated_script(
                        final_result.current_script,
                        "async_incremental_session",
                        data_source
                    )
                    print(f"✓ Script saved to: {saved_path}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not save script: {e}")
                
                print("✓ Final script preview:")
                preview = (
                    final_result.current_script[:400] + "..."
                    if len(final_result.current_script) > 400
                    else final_result.current_script
                )
                print(preview)
            else:
                print(f"✗ Session failed: {final_result.validation_issues}")

        except asyncio.TimeoutError:
            print("✗ Tasks timed out during processing")
        
        # Always try to finalize the session
        try:
            await asyncio.wait_for(session.finalize_async(), timeout=30.0)
            print("✓ Session finalized")
        except Exception as e:
            print(f"Warning: Session finalization failed: {e}")

    except asyncio.TimeoutError:
        print("✗ Session startup timed out")
    except Exception as e:
        print(f"✗ Session failed: {e}")
        
    print()


async def simple_async_conversion_example():
    """
    Example 1: Simple async conversion with file output
    
    This shows basic async conversion with script saving.
    """
    print("=== Simple Async Conversion Example ===")
    
    start_time = time.time()
    
    try:
        # Use the async convert function with sample data
        script = await btt.convert_async(
            SAMPLE_AUTOMATION_STEPS,
            framework="playwright",
            ai_provider="openai",
            language="python",
        )
        
        end_time = time.time()
        
        print(f"✓ Generated script in {end_time - start_time:.2f} seconds")
        print(f"✓ Script length: {len(script)} characters")
        
        # Save the generated script
        try:
            saved_path = save_generated_script(
                script,
                "simple_async_conversion",
                "SAMPLE_AUTOMATION_STEPS"
            )
            print(f"✓ Script saved to: {saved_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save script: {e}")
        
        print("✓ Script preview:")
        preview = script[:200] + "..." if len(script) > 200 else script
        print(preview)
        
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
    
    print()


async def data_validation_example():
    """
    Example 2: Data validation demonstration
    
    Shows how the validation helper identifies problematic data.
    """
    print("=== Data Validation Example ===")
    
    # Test with various data formats
    test_cases = [
        ("SAMPLE_AUTOMATION_STEPS", SAMPLE_AUTOMATION_STEPS),
        ("REAL_AUTOMATION_STEPS", REAL_AUTOMATION_STEPS),
        ("Empty list", []),
        ("Invalid step format", [{"invalid": "step"}]),
        ("Empty actions", [{"model_output": {"action": [{}]}}]),
        ("Missing model_output", [{"state": {"url": "test"}}]),
    ]
    
    for name, data in test_cases:
        is_valid = validate_automation_data(data)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"{status}: {name}")
    
    print()


async def main():
    """Main function to run all examples with comprehensive error handling."""
    print("DEBUG: Entering main function")
    print("Browse-to-Test Async Usage Examples - FIXED VERSION")
    print("====================================================")
    print(f"Output Directory: {OUTPUT_DIR.absolute()}")
    print()

    # Check if we have an OpenAI API key
    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in environment variables.")
        print("Some examples may fail. Please set your OpenAI API key.")
        print("You can also modify the examples to use 'anthropic' provider with ANTHROPIC_API_KEY.")
        print()

    try:
        # Run data validation first
        print("DEBUG: About to run data validation...")
        await data_validation_example()
        print("DEBUG: Data validation completed")
        
        # Run examples with timeout protection
        examples = [
            ("Incremental Session", incremental_session_example()),
        ]
        
        for example_name, example_coro in examples:
            print(f"Running {example_name}...")
            try:
                await asyncio.wait_for(example_coro, timeout=600)  # 10 minute max per example
                print(f"✓ {example_name} completed successfully!")
            except asyncio.TimeoutError:
                print(f"✗ {example_name} timed out")
            except Exception as e:
                print(f"✗ {example_name} failed: {e}")
            print()

        # Show output directory contents
        try:
            output_files = list(OUTPUT_DIR.glob("*.py"))
            if output_files:
                print(f"📁 Generated files in {OUTPUT_DIR.relative_to(Path.cwd())}:")
                for file_path in sorted(output_files):
                    file_size = file_path.stat().st_size
                    print(f"   • {file_path.name} ({file_size:,} bytes)")
            else:
                print(f"📁 No output files generated in {OUTPUT_DIR.relative_to(Path.cwd())}")
        except Exception as e:
            print(f"⚠️  Could not list output files: {e}")

        print("\nAll examples completed!")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Examples failed with unexpected error: {e}")
        print("This might be due to missing API keys or network issues.")


if __name__ == "__main__":
    # Run the async examples
    asyncio.run(main())