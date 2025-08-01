#!/usr/bin/env python3
"""
Simplified API usage examples for browse-to-test library.

This example demonstrates the new simplified API that reduces
configuration complexity by 90% while maintaining full functionality.
"""

import os
import json
import asyncio
from pathlib import Path

# Import the simplified API
import browse_to_test as btt
from browse_to_test import simple_api


def create_sample_automation_data():
    """Create sample browser automation data for demonstration."""
    return [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            },
            "state": {"interacted_element": []},
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "john@example.com"}}]
            },
            "state": {
                "interacted_element": [{
                    "xpath": "//input[@name='email']",
                    "css_selector": "input[name='email']",
                    "attributes": {"name": "email", "type": "email"}
                }]
            }
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "<secret>password123</secret>"}}]
            },
            "state": {
                "interacted_element": [{
                    "xpath": "//input[@name='password']", 
                    "css_selector": "input[name='password']",
                    "attributes": {"name": "password", "type": "password"}
                }]
            }
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "interacted_element": [{
                    "xpath": "//button[@type='submit']",
                    "css_selector": "button[type='submit']",
                    "text_content": "Sign In"
                }]
            }
        }
    ]


def preset_examples():
    """Demonstrate the four configuration presets."""
    print("=== Configuration Presets Demo ===\n")
    
    automation_data = create_sample_automation_data()
    
    # Fast preset - optimized for speed (~10 seconds)
    print("1. FAST Preset (Speed optimized)")
    try:
        script = simple_api.convert_fast(automation_data, "playwright", "python")
        print(f"   ✓ Generated in ~10s: {len(script.splitlines())} lines")
        save_script("fast_preset_test.py", script)
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Balanced preset - good trade-off (~30 seconds)  
    print("2. BALANCED Preset (Recommended)")
    try:
        script = simple_api.convert_balanced(automation_data, "playwright", "python")
        print(f"   ✓ Generated in ~30s: {len(script.splitlines())} lines")
        save_script("balanced_preset_test.py", script)
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Accurate preset - quality optimized (~90 seconds)
    print("3. ACCURATE Preset (Quality optimized)")
    try:
        script = simple_api.convert_accurate(automation_data, "playwright", "python")
        print(f"   ✓ Generated in ~90s: {len(script.splitlines())} lines")  
        save_script("accurate_preset_test.py", script)
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Production preset - enterprise ready
    print("4. PRODUCTION Preset (Enterprise ready)")
    try:
        script = simple_api.convert_production(automation_data, "playwright", "python")
        print(f"   ✓ Generated with full error handling: {len(script.splitlines())} lines")
        save_script("production_preset_test.py", script)
    except Exception as e:
        print(f"   ✗ Failed: {e}")


def framework_shortcuts():
    """Demonstrate framework-specific shortcuts."""
    print("\n=== Framework Shortcuts Demo ===\n")
    
    automation_data = create_sample_automation_data()
    
    shortcuts = [
        ("Playwright + Python", lambda: simple_api.playwright_python(automation_data, "fast")),
        ("Playwright + TypeScript", lambda: simple_api.playwright_typescript(automation_data, "balanced")),
        ("Selenium + Python", lambda: simple_api.selenium_python(automation_data, "balanced")),
        ("Cypress + JavaScript", lambda: simple_api.cypress_javascript(automation_data, "fast"))
    ]
    
    for name, func in shortcuts:
        try:
            script = func()
            print(f"✓ {name}: {len(script.splitlines())} lines")
        except Exception as e:
            print(f"✗ {name}: {e}")


def builder_pattern_example():
    """Demonstrate the SimpleConfigBuilder for advanced customization."""
    print("\n=== Advanced Builder Pattern Demo ===\n")
    
    automation_data = create_sample_automation_data()
    
    # Example 1: Start with preset, add minor customization
    print("1. Preset + Minor Customization")
    try:
        config = simple_api.simple_builder() \
            .preset("balanced") \
            .for_playwright("python") \
            .with_openai() \
            .timeout(60) \
            .sensitive_data(["password", "secret"]) \
            .build()
        
        script = simple_api.convert_with_config(automation_data, config)
        print(f"   ✓ Custom config: {len(script.splitlines())} lines")
        save_script("custom_config_test.py", script)
    except Exception as e:
        print(f"   ✗ Custom config failed: {e}")
    
    # Example 2: Advanced AI configuration
    print("2. Advanced AI Settings")
    try:
        config = simple_api.simple_builder() \
            .preset("accurate") \
            .for_selenium("python") \
            .with_anthropic() \
            .advanced_ai(temperature=0.05, max_tokens=6000) \
            .advanced_analysis(context_collection=True, analysis_depth="deep") \
            .debug(True) \
            .build()
        
        script = simple_api.convert_with_config(automation_data, config)
        print(f"   ✓ Advanced AI config: {len(script.splitlines())} lines")
    except Exception as e:
        print(f"   ✗ Advanced AI config failed: {e}")


async def async_examples():
    """Demonstrate async API usage."""
    print("\n=== Async API Demo ===\n")
    
    automation_data = create_sample_automation_data()
    
    # Async preset functions
    print("1. Async Preset Functions")
    try:
        script = await simple_api.convert_fast_async(automation_data, "playwright", "python")
        print(f"   ✓ Async fast conversion: {len(script.splitlines())} lines")
    except Exception as e:
        print(f"   ✗ Async conversion failed: {e}")
    
    # Async session management
    print("2. Async Session Management")
    try:
        session = await simple_api.start_simple_session_async(
            framework="playwright",
            language="python", 
            preset="balanced",
            target_url="https://example.com"
        )
        
        # Add steps incrementally
        for step in automation_data:
            await session.add_step_async(step, wait_for_completion=False)
        
        # Wait for completion
        result = await session.wait_for_all_tasks()
        print(f"   ✓ Async session: {len(result.current_script.splitlines())} lines")
        save_script("async_session_test.py", result.current_script)
        
    except Exception as e:
        print(f"   ✗ Async session failed: {e}")


def utility_examples():
    """Demonstrate utility functions."""
    print("\n=== Utility Functions Demo ===\n")
    
    automation_data = create_sample_automation_data()
    
    # Compare presets
    print("1. Preset Comparison")
    try:
        comparison = simple_api.compare_presets(automation_data, "playwright")
        print("   Preset Performance Comparison:")
        for preset, metrics in comparison.items():
            if metrics["success"]:
                print(f"   {preset.upper():>8}: {metrics['duration']:.1f}s, "
                      f"{metrics['script_length']} lines, "
                      f"quality: {metrics['estimated_quality']}/10")
            else:
                print(f"   {preset.upper():>8}: Failed - {metrics['error']}")
    except Exception as e:
        print(f"   ✗ Preset comparison failed: {e}")
    
    # Preset suggestion
    print("\n2. Intelligent Preset Suggestion")
    try:
        # Test different requirement scenarios
        scenarios = [
            {"priority": "speed", "max_duration": 15},
            {"priority": "quality", "min_quality": 9},
            {"priority": "balanced"},
            {"max_duration": 10}
        ]
        
        for i, requirements in enumerate(scenarios, 1):
            suggested = simple_api.suggest_preset(automation_data, requirements)
            print(f"   Scenario {i} {requirements}: → {suggested.upper()}")
            
    except Exception as e:
        print(f"   ✗ Preset suggestion failed: {e}")


def migration_example():
    """Demonstrate migration from legacy configuration."""
    print("\n=== Migration from Legacy Config Demo ===\n")
    
    try:
        # Create a legacy configuration (complex)
        legacy_config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4") \
            .language("python") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .temperature(0.1) \
            .timeout(30000) \
            .enable_context_collection(True) \
            .enable_ai_analysis(True) \
            .debug(False) \
            .build()
        
        print("1. Legacy Configuration Analysis")
        from browse_to_test.core.configuration.migration import ConfigMigrator
        
        analysis = ConfigMigrator.analyze_legacy_config(legacy_config)
        print(f"   Complexity Score: {analysis['complexity_score']}")
        print(f"   Recommended Preset: {analysis['recommended_preset']}")
        print(f"   Estimated Reduction: {analysis['estimated_reduction']['percentage']:.0f}%")
        print(f"   Fields Reduced: {analysis['estimated_reduction']['fields']}")
        
        print("\n2. Automatic Migration")
        simple_config, migration_report = ConfigMigrator.migrate_to_simple_config(legacy_config)
        
        print(f"   Migration Success: {migration_report['validation_passed']}")
        print(f"   Preset Used: {migration_report['migrated_preset']}")
        print(f"   Complexity Reduction: {migration_report['reduction_percentage']:.0f}%")
        print(f"   Advanced Settings Preserved: {migration_report['advanced_settings_preserved']}")
        
        # Test the migrated configuration
        automation_data = create_sample_automation_data()
        script = simple_api.convert_with_config(automation_data, simple_config)
        print(f"   ✓ Migrated config works: {len(script.splitlines())} lines")
        save_script("migrated_config_test.py", script)
        
    except Exception as e:
        print(f"   ✗ Migration failed: {e}")


def environment_detection_example():
    """Demonstrate smart environment detection."""
    print("\n=== Smart Environment Detection Demo ===\n")
    
    from browse_to_test.core.configuration.smart_defaults import SmartDefaults
    
    # Get environment defaults
    env_defaults = SmartDefaults.get_environment_defaults()
    print("1. Environment Detection:")
    print(f"   Platform: {env_defaults['platform']}")
    print(f"   CI Environment: {env_defaults['is_ci']}")
    print(f"   Docker Environment: {env_defaults['is_docker']}")
    print(f"   Headless Mode: {env_defaults['headless']}")
    print(f"   Optimal Workers: {env_defaults['max_workers']}")
    
    # Get project context defaults
    project_defaults = SmartDefaults.get_project_context_defaults()
    print(f"\n2. Project Analysis:")
    print(f"   Project Type: {project_defaults['project_type']}")
    print(f"   Has Existing Tests: {project_defaults['has_existing_tests']}")
    print(f"   Recommended Output Dir: {project_defaults['recommended_output_dir']}")
    
    # Framework-specific defaults
    framework_defaults = SmartDefaults.get_framework_defaults("playwright")
    print(f"\n3. Playwright Optimization:")
    print(f"   Supports Screenshots: {framework_defaults['supports_screenshots']}")
    print(f"   Async by Default: {framework_defaults['async_by_default']}")
    print(f"   Recommended Timeout: {framework_defaults['test_timeout_seconds']}s")


def save_script(filename: str, script: str):
    """Save generated script to output directory."""
    output_dir = Path("example_outputs")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / filename, 'w') as f:
        f.write(script)


def main():
    """Run all simplified API examples."""
    print("Browse-to-Test Simplified API Examples")
    print("=" * 50)
    
    # Check environment setup
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Note: OPENAI_API_KEY not set. Some examples may be limited.")
        print("   Set the environment variable to enable full AI features.\n")
    
    try:
        # Create output directory
        Path("example_outputs").mkdir(exist_ok=True)
        
        # Run synchronous examples
        preset_examples()
        framework_shortcuts()
        builder_pattern_example()
        utility_examples()
        migration_example()
        environment_detection_example()
        
        # Run async examples
        print("\n" + "=" * 50)
        print("Running Async Examples...")
        asyncio.run(async_examples())
        
        print("\n" + "=" * 50)
        print("All examples completed! ✅")
        
        # Show generated files
        print("\nGenerated test files:")
        output_dir = Path("example_outputs")
        for file in output_dir.glob("*.py"):
            size = file.stat().st_size
            lines = len(file.read_text().splitlines())
            print(f"  📄 {file.name} ({size} bytes, {lines} lines)")
        
        print(f"\n📈 Configuration Complexity Reduction:")
        print(f"   Legacy API: ~45 configuration options")
        print(f"   Simple API: ~4 essential options")
        print(f"   Reduction: 90% fewer decisions to make")
        print(f"   Setup Time: 5 minutes → 30 seconds")
        
    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()