#!/usr/bin/env python3
"""
Incremental Session Example for Browse-to-Test

This example demonstrates how to use incremental sessions for live test generation
while browser automation is happening. This is perfect for real-time test creation
as users interact with applications.

Key features demonstrated:
- IncrementalSession for live test generation
- Adding steps one by one as they happen
- Async session management
- Real-time script updates
- Session finalization and quality analysis

Requirements:
- Set OPENAI_API_KEY environment variable
- Python 3.7+ for async/await support
"""

import asyncio
import time
import json
import os
from pathlib import Path
from datetime import datetime
import browse_to_test as btt

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_step_sequence():
    """Create a sequence of steps that might happen during live automation."""
    return [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://shop.example.com"}}]
            },
            "state": {
                "url": "https://shop.example.com",
                "title": "Example Shop - Home",
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": time.time(),
                "step_end_time": time.time() + 2,
                "step_number": 1
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://shop.example.com/products",
                "title": "Products - Example Shop",
                "interacted_element": [{
                    "xpath": "//nav//a[contains(text(), 'Products')]",
                    "css_selector": "nav a[href='/products']",
                    "highlight_index": 0,
                    "attributes": {
                        "href": "/products",
                        "class": "nav-link"
                    },
                    "text_content": "Products"
                }]
            },
            "metadata": {
                "step_start_time": time.time() + 2,
                "step_end_time": time.time() + 4,
                "step_number": 2
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://shop.example.com/products/laptop-pro",
                "title": "Laptop Pro - Example Shop",
                "interacted_element": [{
                    "xpath": "//div[@class='product-card'][1]//button",
                    "css_selector": ".product-card:first-child button",
                    "highlight_index": 0,
                    "attributes": {
                        "class": "btn btn-primary product-btn",
                        "data-product-id": "laptop-pro"
                    },
                    "text_content": "View Details"
                }]
            },
            "metadata": {
                "step_start_time": time.time() + 4,
                "step_end_time": time.time() + 6,
                "step_number": 3
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://shop.example.com/cart",
                "title": "Shopping Cart - Example Shop",
                "interacted_element": [{
                    "xpath": "//button[contains(@class, 'add-to-cart')]",
                    "css_selector": ".add-to-cart-btn",
                    "highlight_index": 0,
                    "attributes": {
                        "class": "btn btn-success add-to-cart-btn",
                        "data-product-id": "laptop-pro"
                    },
                    "text_content": "Add to Cart"
                }]
            },
            "metadata": {
                "step_start_time": time.time() + 6,
                "step_end_time": time.time() + 8,
                "step_number": 4
            }
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "2"}}]
            },
            "state": {
                "url": "https://shop.example.com/cart",
                "title": "Shopping Cart - Example Shop",
                "interacted_element": [{
                    "xpath": "//input[@name='quantity']",
                    "css_selector": "input[name='quantity']",
                    "highlight_index": 0,
                    "attributes": {
                        "name": "quantity",
                        "type": "number",
                        "min": "1",
                        "value": "1"
                    }
                }]
            },
            "metadata": {
                "step_start_time": time.time() + 8,
                "step_end_time": time.time() + 10,
                "step_number": 5
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://shop.example.com/checkout",
                "title": "Checkout - Example Shop",
                "interacted_element": [{
                    "xpath": "//button[contains(@class, 'checkout-btn')]",
                    "css_selector": ".checkout-btn",
                    "highlight_index": 0,
                    "attributes": {
                        "class": "btn btn-primary checkout-btn",
                        "type": "submit"
                    },
                    "text_content": "Proceed to Checkout"
                }]
            },
            "metadata": {
                "step_start_time": time.time() + 10,
                "step_end_time": time.time() + 12,
                "step_number": 6
            }
        }
    ]


def example_1_basic_incremental_session():
    """Example 1: Basic incremental session (synchronous)."""
    print("=== Example 1: Basic Incremental Session ===")
    
    steps = create_step_sequence()
    
    try:
        # Create session using the new API
        session = btt.create_session(
            framework="playwright",
            ai_provider="openai",
            language="python"
        )
        
        # Start the session
        result = session.start(target_url="https://shop.example.com")
        print(f"✓ Session started: {result.success}")
        if not result.success:
            print(f"✗ Startup failed: {result.validation_issues}")
            return
        
        print(f"  Initial script: {len(result.current_script.splitlines())} lines")
        
        # Add steps one by one
        for i, step in enumerate(steps, 1):
            print(f"  Adding step {i}...")
            result = session.add_step(step)
            
            if result.success:
                print(f"    ✓ Step {i} added, script now {len(result.current_script.splitlines())} lines")
            else:
                print(f"    ✗ Step {i} failed: {result.validation_issues}")
        
        # Finalize the session
        final_result = session.finalize()
        if final_result.success:
            # Save the final script
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"incremental_session_{timestamp}.py"
            with open(output_file, 'w') as f:
                f.write(final_result.current_script)
            
            print(f"✓ Session finalized: {output_file}")
            print(f"  Final script: {len(final_result.current_script.splitlines())} lines")
            print(f"  Total steps: {final_result.metadata.get('total_steps', 0)}")
        else:
            print(f"✗ Session finalization failed: {final_result.validation_issues}")
        
    except Exception as e:
        print(f"✗ Session failed: {e}")


async def example_2_async_incremental_session():
    """Example 2: Async incremental session with live updates."""
    print("\n=== Example 2: Async Incremental Session ===")
    
    steps = create_step_sequence()
    
    try:
        # Create session with async support
        session = btt.create_session(
            framework="playwright",
            ai_provider="openai",
            language="python",
            include_assertions=True,
            include_error_handling=True
        )
        
        # Start session asynchronously
        result = await session.start_async(target_url="https://shop.example.com")
        print(f"✓ Async session started: {result.success}")
        
        if not result.success:
            print(f"✗ Startup failed: {result.validation_issues}")
            return
        
        # Add steps asynchronously with different strategies
        print("  Adding steps with mixed sync/async patterns...")
        
        # Add first few steps synchronously
        for i, step in enumerate(steps[:3], 1):
            print(f"  Adding step {i} (sync)...")
            result = session.add_step(step, wait_for_completion=True)
            
            if result.success:
                print(f"    ✓ Step {i} completed")
            else:
                print(f"    ✗ Step {i} failed: {result.validation_issues}")
        
        # Add remaining steps asynchronously
        async_tasks = []
        for i, step in enumerate(steps[3:], 4):
            print(f"  Queueing step {i} (async)...")
            task = session.add_step_async(step, wait_for_completion=False)
            async_tasks.append((i, task))
        
        # Wait for async steps to complete
        print("  Waiting for async steps to complete...")
        for i, task in async_tasks:
            try:
                result = await task
                if result.success:
                    print(f"    ✓ Async step {i} completed")
                else:
                    print(f"    ✗ Async step {i} failed: {result.validation_issues}")
            except Exception as e:
                print(f"    ✗ Async step {i} error: {e}")
        
        # Finalize session
        final_result = await session.finalize_async()
        if final_result.success:
            # Save the final script
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"async_incremental_session_{timestamp}.py"
            with open(output_file, 'w') as f:
                f.write(final_result.current_script)
            
            print(f"✓ Async session finalized: {output_file}")
            print(f"  Duration: {final_result.metadata.get('duration_seconds', 0):.2f}s")
            print(f"  Final script: {len(final_result.current_script.splitlines())} lines")
        else:
            print(f"✗ Session finalization failed: {final_result.validation_issues}")
        
    except Exception as e:
        print(f"✗ Async session failed: {e}")


async def example_3_live_monitoring_session():
    """Example 3: Session with live monitoring and statistics."""
    print("\n=== Example 3: Live Monitoring Session ===")
    
    steps = create_step_sequence()
    
    try:
        # Create session with monitoring
        session = btt.create_session(
            framework="selenium",
            ai_provider="openai",
            language="python",
            include_assertions=True,
            include_logging=True
        )
        
        # Start session
        await session.start_async(target_url="https://shop.example.com")
        print("✓ Monitoring session started")
        
        # Add steps with monitoring
        for i, step in enumerate(steps, 1):
            print(f"\n  Processing step {i}...")
            
            # Show session stats before adding step
            stats = session.get_session_stats()
            print(f"    Session stats: {stats.get('steps_added', 0)} steps, {stats.get('errors', 0)} errors")
            
            # Add step asynchronously
            result = await session.add_step_async(step, wait_for_completion=True)
            
            if result.success:
                print(f"    ✓ Step {i} added successfully")
                print(f"    Script lines: {len(result.current_script.splitlines())}")
            else:
                print(f"    ✗ Step {i} failed: {result.validation_issues}")
            
            # Monitor queue if available
            if hasattr(session, 'get_queue_stats'):
                queue_stats = session.get_queue_stats()
                print(f"    Queue: {queue_stats.get('pending_tasks', 0)} pending, "
                      f"{queue_stats.get('completed_tasks', 0)} completed")
            
            # Simulate real-time delay
            await asyncio.sleep(0.5)
        
        # Final statistics
        print(f"\n  Final session statistics:")
        final_stats = session.get_session_stats()
        for key, value in final_stats.items():
            if key != 'start_time':  # Skip datetime object
                print(f"    {key}: {value}")
        
        # Finalize with quality analysis
        print("  Performing final script analysis...")
        final_result = await session.finalize_async()
        
        if final_result.success:
            # Save the script
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = OUTPUT_DIR / f"monitored_session_{timestamp}.py"
            with open(output_file, 'w') as f:
                f.write(final_result.current_script)
            
            print(f"✓ Monitoring session completed: {output_file}")
            
            # Save session metadata
            metadata_file = OUTPUT_DIR / f"session_metadata_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                # Convert datetime to string for JSON serialization
                serializable_metadata = {}
                for key, value in final_result.metadata.items():
                    if isinstance(value, datetime):
                        serializable_metadata[key] = value.isoformat()
                    else:
                        serializable_metadata[key] = value
                json.dump(serializable_metadata, f, indent=2)
            
            print(f"  Session metadata: {metadata_file}")
        
    except Exception as e:
        print(f"✗ Monitoring session failed: {e}")


async def example_4_error_recovery_session():
    """Example 4: Session with error recovery and retry logic."""
    print("\n=== Example 4: Error Recovery Session ===")
    
    steps = create_step_sequence()
    
    # Add a potentially problematic step
    problematic_step = {
        "model_output": {
            "action": [{"invalid_action": {"invalid": "data"}}]  # This might cause issues
        },
        "state": {"url": "https://shop.example.com"},
        "metadata": {"step_number": 99}
    }
    steps.insert(3, problematic_step)  # Insert in the middle
    
    try:
        session = btt.create_session(
            framework="playwright",
            ai_provider="openai",
            language="python"
        )
        
        await session.start_async(target_url="https://shop.example.com")
        print("✓ Error recovery session started")
        
        successful_steps = 0
        error_count = 0
        
        for i, step in enumerate(steps, 1):
            print(f"  Processing step {i}...")
            
            try:
                # Try to add step with timeout
                result = await asyncio.wait_for(
                    session.add_step_async(step, wait_for_completion=True),
                    timeout=30.0
                )
                
                if result.success:
                    print(f"    ✓ Step {i} succeeded")
                    successful_steps += 1
                else:
                    print(f"    ⚠ Step {i} had issues: {result.validation_issues}")
                    # Continue anyway - graceful degradation
                    successful_steps += 1
                
            except asyncio.TimeoutError:
                print(f"    ✗ Step {i} timed out")
                error_count += 1
                
            except Exception as e:
                print(f"    ✗ Step {i} error: {e}")
                error_count += 1
                
                # Try to recover by removing the last step if it was problematic
                if hasattr(session, 'remove_last_step'):
                    try:
                        recovery_result = session.remove_last_step()
                        if recovery_result.success:
                            print(f"    ↺ Recovered by removing problematic step")
                    except Exception:
                        pass  # Recovery failed, continue
        
        print(f"\n  Session summary: {successful_steps} successful, {error_count} errors")
        
        # Try to finalize even with errors
        try:
            final_result = await session.finalize_async()
            
            if final_result.success and final_result.current_script.strip():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = OUTPUT_DIR / f"error_recovery_session_{timestamp}.py"
                with open(output_file, 'w') as f:
                    f.write(final_result.current_script)
                
                print(f"✓ Recovered session saved: {output_file}")
                print(f"  Final script quality: {'Good' if len(final_result.current_script) > 500 else 'Partial'}")
            else:
                print("✗ Session produced no usable script")
                
        except Exception as e:
            print(f"✗ Session finalization failed: {e}")
    
    except Exception as e:
        print(f"✗ Error recovery session failed: {e}")


async def main():
    """Run all incremental session examples."""
    print("Browse-to-Test Incremental Session Examples")
    print("=" * 55)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ Warning: OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("Examples will fail without it.\n")
        return
    
    try:
        # Run examples
        example_1_basic_incremental_session()
        await example_2_async_incremental_session()
        await example_3_live_monitoring_session()
        await example_4_error_recovery_session()
        
        # Show generated files
        print(f"\n📁 Generated files in {OUTPUT_DIR.relative_to(Path.cwd())}:")
        output_files = list(OUTPUT_DIR.glob("incremental_*.py")) + \
                      list(OUTPUT_DIR.glob("async_incremental_*.py")) + \
                      list(OUTPUT_DIR.glob("monitored_*.py")) + \
                      list(OUTPUT_DIR.glob("error_recovery_*.py")) + \
                      list(OUTPUT_DIR.glob("session_metadata_*.json"))
        
        for file_path in sorted(output_files):
            size = file_path.stat().st_size
            print(f"   • {file_path.name} ({size:,} bytes)")
        
        print("\n✓ All incremental session examples completed!")
        print("\nKey benefits of incremental sessions:")
        print("- Real-time test generation as automation happens")
        print("- Live script updates and monitoring")
        print("- Error recovery and graceful degradation")
        print("- Session state management and finalization")
        print("- Perfect for browser automation tools and live testing")
        
    except Exception as e:
        print(f"\n✗ Incremental session examples failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())