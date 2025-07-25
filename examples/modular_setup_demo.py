#!/usr/bin/env python3
"""
Modular Setup Demo

This demo shows how to use browse-to-test with modular shared setup files 
that can be reused across multiple test scripts.
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Add the parent directory to the path to import browse_to_test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import browse_to_test as btt
from browse_to_test.core.configuration.config import (
    Config, ConfigBuilder, SharedSetupConfig
)

# Load environment variables
load_dotenv()

def demo_basic_shared_setup():
    """Demo basic shared setup generation and usage."""
    print("\n🔧 === Basic Shared Setup Demo ===")
    
    # Create configuration with shared setup enabled
    config = ConfigBuilder() \
        .framework("playwright") \
        .language("python") \
        .ai_provider("openai") \
        .enable_shared_setup(
            setup_dir="shared_test_utils",
            generate_utilities=True,
            generate_constants=True,
            generate_exceptions=True
        ) \
        .build()
    
    # Create converter with shared setup
    converter = btt.E2eTestConverter(config)
    
    print("🎭 Browse-to-Test Modular Setup Demo")
    print("Generating clean test scripts with shared utilities")
    print("=" * 60)
    
    # Sample browser automation data
    sample_automation_data = [
        {
            "step_index": 0,
            "actions": [
                {
                    "action_type": "go_to_url",
                    "parameters": {"url": "https://example.com/login"},
                    "selector_info": {}
                }
            ]
        },
        {
            "step_index": 1,
            "actions": [
                {
                    "action_type": "input_text",
                    "parameters": {"text": "<secret>username</secret>"},
                    "selector_info": {"css_selector": "#username"}
                }
            ]
        },
        {
            "step_index": 2,
            "actions": [
                {
                    "action_type": "input_text",
                    "parameters": {"text": "<secret>password</secret>"},
                    "selector_info": {"css_selector": "#password"}
                }
            ]
        },
        {
            "step_index": 3,
            "actions": [
                {
                    "action_type": "click_element",
                    "parameters": {},
                    "selector_info": {"css_selector": "button[type='submit']"}
                }
            ]
        }
    ]
    
    print("\n🚀 Generating first test script with shared setup...")
    
    # Generate the first test script
    first_script = converter.convert(
        automation_data=sample_automation_data,
        target_url="https://example.com/login"
    )
    
    # Save the first script
    first_script_path = Path("example_outputs/demo_clean_login_test.py")
    first_script_path.write_text(first_script)
    
    print(f"✅ First script generated: {first_script_path}")
    print(f"📏 Script length: {len(first_script)} characters")
    
    # Show shared setup status
    if converter.language_manager:
        # Status information can be retrieved from language manager
        status = "Ready"  # Updated to work with new language manager
        print(f"📊 Shared setup status:")
        print(f"   - Total utilities: {status['total_utilities']}")
        print(f"   - Generated files: {status['generated_files']}")
        print(f"   - Setup directory: {status['setup_directory']}")
    
    print("\n" + "=" * 60)
    print("🔄 Generating second test script (should reuse setup)...")
    
    # Sample data for a different test flow
    second_automation_data = [
        {
            "step_index": 0,
            "actions": [
                {
                    "action_type": "go_to_url",
                    "parameters": {"url": "https://example.com/dashboard"},
                    "selector_info": {}
                }
            ]
        },
        {
            "step_index": 1,
            "actions": [
                {
                    "action_type": "click_element",
                    "parameters": {},
                    "selector_info": {"css_selector": ".user-profile"}
                }
            ]
        },
        {
            "step_index": 2,
            "actions": [
                {
                    "action_type": "input_text",
                    "parameters": {"text": "Updated Name"},
                    "selector_info": {"css_selector": "#display-name"}
                }
            ]
        }
    ]
    
    # Generate second test script (using same converter instance)
    second_script = converter.convert(
        automation_data=second_automation_data,
        target_url="https://example.com/dashboard"
    )
    
    # Save the second script
    second_script_path = Path("example_outputs/demo_clean_profile_test.py")
    second_script_path.write_text(second_script)
    
    print(f"✅ Second script generated: {second_script_path}")
    print(f"📏 Script length: {len(second_script)} characters")
    
    # Show the difference in file sizes compared to original bloated script
    original_script_path = Path("example_outputs/demo_generated_login_test.py")
    if original_script_path.exists():
        original_size = len(original_script_path.read_text())
        print(f"\n📈 Size comparison:")
        print(f"   - Original bloated script: {original_size} characters")
        print(f"   - New clean script: {len(first_script)} characters")
        print(f"   - Reduction: {((original_size - len(first_script)) / original_size * 100):.1f}%")
    
    print("\n" + "=" * 60)
    print("📁 Generated files structure:")
    
    # List all generated files
    generated_files = [
        first_script_path,
        second_script_path,
        Path("example_outputs/test_setup/__init__.py"),
        Path("example_outputs/test_setup/test_utilities.py"),
        Path("example_outputs/test_setup/test_constants.py")
    ]
    
    for file_path in generated_files:
        if file_path.exists():
            size = len(file_path.read_text())
            print(f"   ✓ {file_path} ({size} characters)")
        else:
            print(f"   ✗ {file_path} (not found)")
    
    return first_script_path, second_script_path


def demo_incremental_modular_setup():
    """Demonstrate incremental generation with modular setup."""
    
    print("\n" + "=" * 60)
    print("⚡ Incremental Modular Setup Demo")
    print("=" * 60)
    
    # Create configuration with shared setup enabled
    config = Config(
        output=btt.OutputConfig(
            framework="playwright",
            shared_setup=SharedSetupConfig(
                enabled=True,
                setup_dir="browse_to_test/language_utils/test_setup_incremental",
                include_docstrings=True,
                organize_by_category=True
            )
        ),
        verbose=True
    )
    
    # Create incremental orchestrator
    orchestrator = btt.IncrementalSession(config)
    
    print("\n🚀 Starting incremental session with shared setup...")
    
    # Start incremental session
    result = orchestrator.start_incremental_session(
        target_url="https://example.com/checkout"
    )
    
    print(f"✅ Session started successfully")
    print(f"📊 Initial setup: {result.new_lines_added} lines")
    
    # Add steps incrementally
    steps = [
        {
            "step_index": 0,
            "actions": [{
                "action_type": "go_to_url",
                "parameters": {"url": "https://example.com/checkout"},
                "selector_info": {}
            }]
        },
        {
            "step_index": 1,
            "actions": [{
                "action_type": "input_text",
                "parameters": {"text": "John Doe"},
                "selector_info": {"css_selector": "#customer-name"}
            }]
        },
        {
            "step_index": 2,
            "actions": [{
                "action_type": "input_text",
                "parameters": {"text": "4111111111111111"},
                "selector_info": {"css_selector": "#card-number"}
            }]
        },
        {
            "step_index": 3,
            "actions": [{
                "action_type": "click_element",
                "parameters": {},
                "selector_info": {"css_selector": "#submit-payment"}
            }]
        }
    ]
    
    print("\n⚡ Adding steps incrementally...")
    for i, step in enumerate(steps, 1):
        result = orchestrator.add_step(step)
        print(f"   Step {i}: +{result.new_lines_added} lines")
    
    print("\n🏁 Finalizing incremental session...")
    final_result = orchestrator.finalize_session()
    
    if final_result.success:
        # Save the incremental script
        incremental_script_path = Path("example_outputs/demo_incremental_clean_checkout.py")
        incremental_script_path.write_text(final_result.updated_script)
        
        print(f"✅ Incremental script generated: {incremental_script_path}")
        print(f"📏 Final script length: {len(final_result.updated_script)} characters")
        print(f"📊 Total steps processed: {final_result.metadata['step_count']}")
        
        return incremental_script_path
    else:
        print("❌ Incremental generation failed")
        return None


def demo_manual_utility_addition():
    """Demonstrate manually adding custom utilities to the shared setup."""
    
    print("\n" + "=" * 60)
    print("🔧 Manual Utility Addition Demo")
    print("=" * 60)
    
    # Create a shared setup manager directly
    setup_config = SharedSetupConfig(
        setup_dir=Path("browse_to_test/language_utils/test_setup_custom"),
        include_docstrings=True,
        organize_by_category=True
    )
    
    manager = btt.SharedSetupManager(setup_config)
    
    # Add standard utilities
    manager.add_standard_utilities("playwright")
    
    print("📝 Adding custom utilities...")
    
    # Add a custom assertion helper
    custom_assertion = btt.SetupUtility(
        name="assert_element_text",
        content='''async def assert_element_text(page: Page, selector: str, expected_text: str):
    """Assert that an element contains the expected text."""
    element = page.locator(selector).first
    actual_text = await element.text_content()
    if expected_text not in actual_text:
        raise AssertionError(f"Expected '{expected_text}' in element text, got '{actual_text}'")''',
        imports=["from playwright.async_api import Page"],
        category="assertion",
        description="Assert element text content matches expected value"
    )
    
    added = manager.add_utility(custom_assertion)
    print(f"   ✓ Custom assertion utility added: {added}")
    
    # Add a data management utility
    data_utility = btt.SetupUtility(
        name="load_test_data",
        content='''def load_test_data(file_path: str) -> dict:
    """Load test data from JSON file."""
    import json
    from pathlib import Path
    
    data_file = Path(file_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Test data file not found: {file_path}")
    
    with open(data_file, 'r') as f:
        return json.load(f)''',
        imports=["import json", "from pathlib import Path"],
        category="data",
        description="Load test data from JSON files"
    )
    
    added = manager.add_utility(data_utility)
    print(f"   ✓ Data utility added: {added}")
    
    # Generate setup files with custom utilities
    print("\n📁 Generating setup files with custom utilities...")
    generated_files = manager.generate_setup_files(force_regenerate=True)
    
    for file_type, file_path in generated_files.items():
        print(f"   ✓ {file_type}: {file_path}")
    
    # Show status
    status = manager.get_setup_status()
    print(f"\n📊 Final setup status:")
    print(f"   - Total utilities: {status['total_utilities']}")
    print(f"   - Categories: {list(status['utilities_by_category'].keys())}")
    print(f"   - Frameworks: {status['frameworks_supported']}")
    
    return generated_files


def main():
    """Run all modular setup demos."""
    
    try:
        # Demo 1: Basic shared setup generation
        first_script, second_script = demo_basic_shared_setup()
        
        # Demo 2: Incremental generation with modular setup
        incremental_script = demo_incremental_modular_setup()
        
        # Demo 3: Manual utility addition
        custom_files = demo_manual_utility_addition()
        
        print("\n" + "=" * 60)
        print("✨ All modular setup demos completed!")
        print("\nKey benefits demonstrated:")
        print("  • 🧹 Clean, focused test scripts")
        print("  • 🔄 Reusable utility functions")
        print("  • 📦 Organized setup packages")
        print("  • ⚡ Incremental utility accumulation")
        print("  • 🎯 Framework-specific helpers")
        print("  • 🛠️ Custom utility extensibility")
        
        print("\nGenerated files:")
        print(f"  • Clean test scripts: {first_script}, {second_script}")
        if incremental_script:
            print(f"  • Incremental script: {incremental_script}")
        print(f"  • Shared setup directories: browse_to_test/output_langs/generated/, browse_to_test/output_langs/python/, browse_to_test/output_langs/typescript/")
        
        print("\nTry importing utilities in your test scripts:")
        print("  from browse_to_test.output_langs.generated import (E2eActionError, replace_sensitive_data, safe_action)")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 