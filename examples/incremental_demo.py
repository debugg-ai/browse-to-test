#!/usr/bin/env python3
"""
Simple demonstration of the new incremental test script generation functionality.

This example shows how to use the live update system to generate test scripts
step by step as browser automation data comes in.
"""

import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import the new incremental functionality
from browse_to_test import (
    start_incremental_session,
    add_incremental_step,
    finalize_incremental_session,
    btt.IncrementalSession,
    Config,
    OutputConfig,
    ProcessingConfig
)

load_dotenv()

def print_separator(title: str):
    """Print a styled separator for demo sections."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_update_info(result, step_num: int = None):
    """Print information about an incremental update."""
    status = "✅ SUCCESS" if result.success else "❌ FAILED"
    step_info = f" (Step {step_num})" if step_num else ""
    
    print(f"{status}{step_info}")
    print(f"  📊 Lines added: {result.new_lines_added}")
    
    if result.validation_issues:
        print(f"  ⚠️  Validation issues: {len(result.validation_issues)}")
        for issue in result.validation_issues[:2]:  # Show first 2 issues
            print(f"     • {issue}")
    
    if result.analysis_insights:
        print(f"  💡 Insights: {len(result.analysis_insights)}")
        for insight in result.analysis_insights[:2]:  # Show first 2 insights
            print(f"     • {insight}")


def create_sample_login_steps() -> List[Dict[str, Any]]:
    """Create sample automation steps for a login flow."""
    return [
        # Step 1: Navigate to login page
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://example.com/login"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "description": "Navigate to login page",
                "elapsed_time": 1.2
            }
        },
        
        # Step 2: Enter username
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "user@example.com",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@data-testid='username-input']",
                        "css_selector": "input[data-testid='username-input']",
                        "attributes": {
                            "data-testid": "username-input",
                            "type": "email",
                            "placeholder": "Enter your email"
                        }
                    }
                ]
            },
            "metadata": {
                "description": "Enter username",
                "elapsed_time": 0.8
            }
        },
        
        # Step 3: Enter password
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "mypassword123",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@data-testid='password-input']",
                        "css_selector": "input[data-testid='password-input']",
                        "attributes": {
                            "data-testid": "password-input",
                            "type": "password",
                            "placeholder": "Enter your password"
                        }
                    }
                ]
            },
            "metadata": {
                "description": "Enter password",
                "elapsed_time": 0.6
            }
        },
        
        # Step 4: Click login button
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
                        "xpath": "//button[@data-testid='login-button']",
                        "css_selector": "button[data-testid='login-button']",
                        "attributes": {
                            "data-testid": "login-button",
                            "type": "submit",
                            "class": "btn btn-primary"
                        }
                    }
                ]
            },
            "metadata": {
                "description": "Click login button",
                "elapsed_time": 0.4
            }
        },
        
        # Step 5: Wait and complete
        {
            "model_output": {
                "action": [
                    {
                        "wait": {
                            "seconds": 2
                        }
                    },
                    {
                        "done": {
                            "success": True,
                            "text": "Login completed successfully"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "description": "Wait for login and complete",
                "elapsed_time": 2.1
            }
        }
    ]


async def demo_basic_incremental_workflow():
    """Demonstrate the basic incremental workflow."""
    print_separator("Basic Incremental Workflow Demo")
    
    print("🚀 Starting incremental test generation session...")
    
    # Start an incremental session for Playwright
    orchestrator, setup_result = start_incremental_session(
        framework="playwright",
        target_url="https://example.com/login",
        config={
            "output": {
                "include_error_handling": True,
                "include_logging": True,
                "include_assertions": True
            },
            "processing": {
                "analyze_actions_with_ai": False,  # Disable AI for demo
                "strict_mode": False
            }
        },
        context_hints={
            "flow_type": "authentication",
            "critical_elements": ["username-input", "password-input", "login-button"]
        }
    )
    
    if not setup_result.success:
        print("❌ Failed to start session!")
        for issue in setup_result.validation_issues:
            print(f"   Error: {issue}")
        return
    
    print_update_info(setup_result)
    print("\n📄 Initial script preview:")
    print(setup_result.updated_script[:200] + "...")
    
    # Get sample steps
    steps = create_sample_login_steps()
    
    # Add steps incrementally
    print(f"\n⚡ Adding {len(steps)} steps incrementally...")
    
    for i, step in enumerate(steps):
        print(f"\n📦 Processing step {i + 1}: {step['metadata'].get('description', 'Unknown')}")
        
        # Add the step
        step_result = add_incremental_step(orchestrator, step, analyze_step=True)
        print_update_info(step_result, i + 1)
        
        # Simulate real-time delay
        await asyncio.sleep(0.2)
    
    # Get current state
    current_state = orchestrator.get_current_state()
    if current_state:
        print("\n📊 Current session state:")
        print(f"   Steps processed: {current_state['metadata']['step_count']}")
        print(f"   Total actions: {current_state['metadata']['total_actions']}")
        print(f"   Setup complete: {current_state['setup_complete']}")
        print(f"   Finalized: {current_state['finalized']}")
    
    # Finalize the session
    print("\n🏁 Finalizing session...")
    final_result = finalize_incremental_session(
        orchestrator, 
        final_validation=True, 
        optimize_script=True
    )
    
    print_update_info(final_result)
    
    if final_result.success:
        # Save the final script
        script_filename = "demo_generated_login_test.py"
        with open(script_filename, 'w') as f:
            f.write(final_result.updated_script)
        
        print(f"\n💾 Final script saved to: {script_filename}")
        print(f"📏 Script length: {len(final_result.updated_script)} characters")
        script_lines = final_result.updated_script.split('\n')
        print(f"📄 Script lines: {len(script_lines)}")
        
        return final_result.updated_script
    else:
        print("\n❌ Session finalization failed!")
        for issue in final_result.validation_issues:
            print(f"   Issue: {issue}")
        return None


async def demo_callback_system():
    """Demonstrate the callback system for live updates."""
    print_separator("Callback System Demo")
    
    print("🔔 Setting up callback system for live updates...")
    
    # Create configuration
    config = Config(
        output=OutputConfig(
            framework="selenium",
            language="python",
            include_error_handling=True,
            include_logging=True
        ),
        processing=ProcessingConfig(
            analyze_actions_with_ai=False,
            strict_mode=False
        )
    )
    
    # Create orchestrator directly for callback demo
    orchestrator = btt.IncrementalSession(config)
    
    # Callback to track updates
    update_count = 0
    total_lines_added = 0
    
    def update_callback(result):
        nonlocal update_count, total_lines_added
        update_count += 1
        total_lines_added += result.new_lines_added
        
        status = "✅" if result.success else "❌"
        print(f"   {status} Callback #{update_count}: +{result.new_lines_added} lines (Total: {total_lines_added})")
        
        if result.analysis_insights:
            print(f"      💡 {result.analysis_insights[0]}")
    
    # Register callback
    orchestrator.register_update_callback(update_callback)
    
    # Start session
    setup_result = orchestrator.start_incremental_session(
        target_url="https://shop.example.com"
    )
    
    if setup_result.success:
        # Add a few steps quickly
        simple_steps = [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://shop.example.com"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate to shop"}
            },
            {
                "model_output": {
                    "action": [{"input_text": {"text": "laptop", "index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "css_selector": "input[data-testid='search']",
                        "attributes": {"data-testid": "search"}
                    }]
                },
                "metadata": {"description": "Search for laptop"}
            },
            {
                "model_output": {
                    "action": [{"click_element": {"index": 0}}]
                },
                "state": {
                    "interacted_element": [{
                        "css_selector": "button[type='submit']",
                        "attributes": {"type": "submit"}
                    }]
                },
                "metadata": {"description": "Click search"}
            }
        ]
        
        for step in simple_steps:
            orchestrator.add_step(step)
            await asyncio.sleep(0.1)  # Brief delay to see callbacks
        
        # Finalize
        orchestrator.finalize_session()
        
        print("\n📊 Callback summary:")
        print(f"   Total callbacks triggered: {update_count}")
        print(f"   Total lines added: {total_lines_added}")
    else:
        print("❌ Failed to start callback demo session")


async def demo_error_handling():
    """Demonstrate error handling in incremental mode."""
    print_separator("Error Handling Demo")
    
    print("🚨 Testing error handling scenarios...")
    
    # Try to add step without starting session
    print("\n1️⃣ Testing: Add step without active session")
    config = Config(
        output=OutputConfig(framework="playwright"),
        processing=ProcessingConfig(analyze_actions_with_ai=False)
    )
    orchestrator = btt.IncrementalSession(config)
    
    invalid_step = {
        "model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]},
        "state": {"interacted_element": []}
    }
    
    result = orchestrator.add_step(invalid_step)
    print(f"   Result: {'❌ Expected failure' if not result.success else '⚠️ Unexpected success'}")
    if result.validation_issues:
        print(f"   Issue: {result.validation_issues[0]}")
    
    # Try to start session twice
    print("\n2️⃣ Testing: Start session twice")
    orchestrator.start_incremental_session()
    try:
        orchestrator.start_incremental_session()
        print("   Result: ⚠️ Unexpected success")
    except RuntimeError as e:
        print(f"   Result: ✅ Expected error caught: {e}")
    
    # Clean up
    orchestrator.finalize_session()
    
    # Test with invalid step data
    print("\n3️⃣ Testing: Invalid step data")
    orchestrator, setup = start_incremental_session("playwright")
    
    if setup.success:
        invalid_step = {"invalid": "data"}  # Missing required fields
        result = orchestrator.add_step(invalid_step)
        print(f"   Result: {'✅ Handled gracefully' if not result.success else '⚠️ Should have failed'}")
        
        orchestrator.finalize_session()


async def main():
    """Main demo function."""
    print("🎭 Browse-to-Test Incremental Demo")
    print("Live test script generation with step-by-step updates")
    
    # Run different demo scenarios
    await demo_basic_incremental_workflow()
    await demo_callback_system()
    await demo_error_handling()
    
    print_separator("Demo Complete")
    print("✨ All incremental demos completed!")
    print("\nKey features demonstrated:")
    print("  • ⚡ Live script generation as steps are added")
    print("  • 🔔 Real-time callback system for updates")
    print("  • 🛡️ Robust error handling and validation")
    print("  • 🎯 Framework support (Playwright & Selenium)")
    print("  • 📊 Step-by-step progress tracking")
    print("  • 🏁 Comprehensive finalization and optimization")
    
    print("\nGenerated files:")
    print("  • demo_generated_login_test.py")
    
    print("\nTry running the generated test with:")
    print("  python demo_generated_login_test.py")


if __name__ == "__main__":
    asyncio.run(main()) 