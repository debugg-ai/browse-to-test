#!/usr/bin/env python3
"""
Configuration Builder Example for Browse-to-Test

This example demonstrates the powerful ConfigBuilder pattern for creating
customized configurations for different use cases, environments, and requirements.

Key features demonstrated:
- ConfigBuilder fluent interface
- Configuration presets (fast, balanced, accurate, production)
- Environment-based configuration
- File-based configuration loading/saving
- Custom configuration for different scenarios
- Configuration validation and optimization

Requirements:
- Set OPENAI_API_KEY environment variable
- Optional: Create config files in different formats
"""

import os
import json
from pathlib import Path
import browse_to_test as btt

from dotenv import load_dotenv

load_dotenv()

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_sample_automation_data():
    """Create sample automation data for testing configurations."""
    return [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://banking.example.com"}}]
            },
            "state": {
                "url": "https://banking.example.com",
                "title": "Secure Banking - Login",
                "interacted_element": []
            },
            "metadata": {"step_number": 1}
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "user@bank.com"}}]
            },
            "state": {
                "url": "https://banking.example.com/login",
                "interacted_element": [{
                    "xpath": "//input[@name='username']",
                    "css_selector": "input[name='username']",
                    "attributes": {"name": "username", "type": "email"}
                }]
            },
            "metadata": {"step_number": 2}
        },
        {
            "model_output": {
                "action": [{"input_text": {"index": 0, "text": "<secret>password123</secret>"}}]
            },
            "state": {
                "url": "https://banking.example.com/login",
                "interacted_element": [{
                    "xpath": "//input[@name='password']",
                    "css_selector": "input[name='password']",
                    "attributes": {"name": "password", "type": "password"}
                }]
            },
            "metadata": {"step_number": 3}
        },
        {
            "model_output": {
                "action": [{"click_element": {"index": 0}}]
            },
            "state": {
                "url": "https://banking.example.com/dashboard",
                "interacted_element": [{
                    "xpath": "//button[@type='submit']",
                    "css_selector": "button[type='submit']",
                    "text_content": "Secure Login"
                }]
            },
            "metadata": {"step_number": 4}
        }
    ]


def example_1_basic_config_builder():
    """Example 1: Basic configuration builder usage."""
    print("=== Example 1: Basic Configuration Builder ===")
    
    automation_data = create_sample_automation_data()
    
    try:
        # Build a custom configuration using the fluent interface
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4.1-mini") \
            .language("python") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .include_logging(True) \
            .test_timeout(45000) \
            .sensitive_data_keys(["password", "ssn", "credit_card", "token"]) \
            .build()
        
        print("✓ Configuration built successfully")
        print(f"  Framework: {config.framework}")
        print(f"  Language: {config.language}")
        print(f"  AI Provider: {config.ai_provider}")
        print(f"  AI Model: {config.ai_model}")
        print(f"  Timeout: {config.test_timeout}ms")
        
        # Use the configuration
        script = btt.convert(
            automation_data=automation_data,
            framework=config.framework,
            ai_provider=config.ai_provider,
            language=config.language,
            include_assertions=config.include_assertions,
            include_error_handling=config.include_error_handling,
            include_logging=config.include_logging,
            test_timeout=config.test_timeout,
            sensitive_data_keys=config.sensitive_data_keys
        )
        
        # Save the script
        output_file = OUTPUT_DIR / "basic_config_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Generated test with custom config: {output_file}")
        
    except Exception as e:
        print(f"✗ Basic config example failed: {e}")


def example_2_configuration_presets():
    """Example 2: Using configuration presets for different scenarios."""
    print("\n=== Example 2: Configuration Presets ===")
    
    automation_data = create_sample_automation_data()
    
    # Define presets to test
    presets = [
        (btt.Config.ConfigPreset.FAST, "fast"),
        (btt.Config.ConfigPreset.BALANCED, "balanced"), 
        (btt.Config.ConfigPreset.ACCURATE, "accurate"),
        (btt.Config.ConfigPreset.PRODUCTION, "production")
    ]
    
    for preset_enum, preset_name in presets:
        print(f"\n  Testing {preset_name.upper()} preset:")
        
        try:
            # Create configuration from preset
            config = btt.Config.from_preset(preset_enum)
            
            print(f"    Framework: {config.framework}")
            print(f"    AI Analysis: {config.enable_ai_analysis}")
            print(f"    Context Collection: {config.enable_context_collection}")
            print(f"    Error Handling: {config.include_error_handling}")
            print(f"    Temperature: {config.ai_temperature}")
            
            # Generate script with preset
            script = btt.convert(
                automation_data=automation_data,
                framework=config.framework,
                ai_provider=config.ai_provider,
                language=config.language,
                enable_ai_analysis=config.enable_ai_analysis,
                enable_context_collection=config.enable_context_collection,
                include_error_handling=config.include_error_handling,
                temperature=config.ai_temperature
            )
            
            # Save preset-based script
            output_file = OUTPUT_DIR / f"{preset_name}_preset_test.py"
            with open(output_file, 'w') as f:
                f.write(script)
            
            print(f"    ✓ Generated: {output_file}")
            
        except Exception as e:
            print(f"    ✗ {preset_name} preset failed: {e}")


def example_3_builder_chaining_patterns():
    """Example 3: Advanced builder chaining patterns."""
    print("\n=== Example 3: Advanced Builder Patterns ===")
    
    automation_data = create_sample_automation_data()
    
    scenarios = [
        {
            "name": "speed_optimized",
            "description": "Speed-optimized for CI/CD",
            "builder": btt.ConfigBuilder()
                .framework("playwright")
                .ai_provider("openai")
                .language("typescript")
                .fast_mode()  # Enables speed optimizations
                .test_timeout(15000)
                .debug(False)
        },
        {
            "name": "accuracy_focused", 
            "description": "Accuracy-focused for critical tests",
            "builder": btt.ConfigBuilder()
                .framework("selenium")
                .ai_provider("openai", model="gpt-4")
                .language("python")
                .thorough_mode()  # Enables thorough analysis
                .include_assertions(True)
                .include_error_handling(True)
                .include_logging(True)
                .temperature(0.05)  # Low temperature for consistency
        },
        {
            "name": "security_hardened",
            "description": "Security-hardened for sensitive applications",
            "builder": btt.ConfigBuilder()
                .framework("playwright")
                .ai_provider("openai")
                .language("python")
                .sensitive_data_keys([
                    "password", "pwd", "pass", "secret", "token", "key",
                    "ssn", "social", "credit_card", "cc", "card_number",
                    "cvv", "pin", "auth", "api_key", "bearer", "session"
                ])
                .include_error_handling(True)
                .include_logging(True)
                .strict_mode(True)
                .test_timeout(60000)
        }
    ]
    
    for scenario in scenarios:
        print(f"\n  {scenario['description']}:")
        
        try:
            config = scenario["builder"].build()
            
            # Show key configuration details
            print(f"    Framework: {config.framework}")
            print(f"    Language: {config.language}")
            print(f"    Sensitive keys: {len(config.sensitive_data_keys)} defined")
            print(f"    Strict mode: {config.strict_mode}")
            
            # Generate script
            script = btt.convert(
                automation_data=automation_data,
                framework=config.framework,
                ai_provider=config.ai_provider,
                language=config.language,
                include_assertions=config.include_assertions,
                include_error_handling=config.include_error_handling,
                include_logging=config.include_logging,
                sensitive_data_keys=config.sensitive_data_keys,
                test_timeout=config.test_timeout,
                temperature=config.ai_temperature
            )
            
            # Determine file extension
            extension = ".ts" if config.language == "typescript" else ".py"
            output_file = OUTPUT_DIR / f"{scenario['name']}_test{extension}"
            
            with open(output_file, 'w') as f:
                f.write(script)
            
            print(f"    ✓ Generated: {output_file}")
            
        except Exception as e:
            print(f"    ✗ {scenario['name']} failed: {e}")


def example_4_environment_based_config():
    """Example 4: Environment-based configuration."""
    print("\n=== Example 4: Environment-Based Configuration ===")
    
    # Create different environment configurations
    environments = {
        "development": {
            "ai_provider": "openai",
            "framework": "playwright", 
            "language": "python",
            "include_logging": True,
            "debug": True,
            "test_timeout": 30000,
            "temperature": 0.2
        },
        "staging": {
            "ai_provider": "openai",
            "framework": "playwright",
            "language": "typescript", 
            "include_assertions": True,
            "include_error_handling": True,
            "test_timeout": 45000,
            "temperature": 0.1
        },
        "production": {
            "ai_provider": "openai",
            "framework": "selenium",
            "language": "python",
            "include_assertions": True,
            "include_error_handling": True,
            "include_logging": True,
            "strict_mode": True,
            "test_timeout": 60000,
            "temperature": 0.05,
            "sensitive_data_keys": ["password", "token", "key", "secret"]
        }
    }
    
    automation_data = create_sample_automation_data()
    
    for env_name, env_config in environments.items():
        print(f"\n  {env_name.upper()} environment:")
        
        try:
            # Build configuration from environment settings
            config = btt.ConfigBuilder() \
                .from_kwargs(**env_config) \
                .build()
            
            print(f"    Framework: {config.framework}")
            print(f"    Language: {config.language}")
            print(f"    Debug mode: {getattr(config, 'debug', False)}")
            print(f"    Strict mode: {config.strict_mode}")
            
            # Generate environment-specific script
            script = btt.convert(
                automation_data=automation_data,
                **env_config
            )
            
            # Save with environment prefix
            extension = ".ts" if env_config["language"] == "typescript" else ".py"
            output_file = OUTPUT_DIR / f"{env_name}_env_test{extension}"
            
            with open(output_file, 'w') as f:
                f.write(script)
            
            print(f"    ✓ Generated: {output_file}")
            
        except Exception as e:
            print(f"    ✗ {env_name} environment failed: {e}")


def example_5_config_persistence():
    """Example 5: Configuration file loading and saving."""
    print("\n=== Example 5: Configuration Persistence ===")
    
    try:
        # Create a comprehensive configuration
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4") \
            .language("python") \
            .include_assertions(True) \
            .include_error_handling(True) \
            .include_logging(True) \
            .sensitive_data_keys(["password", "token", "secret"]) \
            .test_timeout(45000) \
            .temperature(0.1) \
            .strict_mode(True) \
            .debug(False) \
            .build()
        
        # Save configuration to JSON file
        json_config_file = OUTPUT_DIR / "browse_to_test_config.json"
        config.save_to_file(str(json_config_file), format="json")
        print(f"✓ Saved JSON config: {json_config_file}")
        
        # Load configuration from JSON file
        loaded_config = btt.Config.from_file(json_config_file)
        print("✓ Loaded config from JSON file")
        print(f"  Framework: {loaded_config.framework}")
        print(f"  AI Provider: {loaded_config.ai_provider}")
        print(f"  Language: {loaded_config.language}")
        
        # Test the loaded configuration
        automation_data = create_sample_automation_data()
        script = btt.convert(
            automation_data=automation_data,
            framework=loaded_config.framework,
            ai_provider=loaded_config.ai_provider,
            language=loaded_config.language,
            include_assertions=loaded_config.include_assertions,
            include_error_handling=loaded_config.include_error_handling,
            test_timeout=loaded_config.test_timeout
        )
        
        output_file = OUTPUT_DIR / "config_from_file_test.py"
        with open(output_file, 'w') as f:
            f.write(script)
        
        print(f"✓ Generated test from loaded config: {output_file}")
        
        # Show the saved configuration content
        print(f"\n  Configuration file content:")
        with open(json_config_file) as f:
            config_content = json.load(f)
            print(f"    AI provider: {config_content['ai']['provider']}")
            print(f"    Framework: {config_content['output']['framework']}")
            print(f"    Language: {config_content['output']['language']}")
            print(f"    Timeout: {config_content['output']['test_timeout']}ms")
            
    except Exception as e:
        print(f"✗ Config persistence failed: {e}")


def example_6_config_validation():
    """Example 6: Configuration validation and optimization."""
    print("\n=== Example 6: Configuration Validation ===")
    
    # Test various configuration scenarios
    test_configs = [
        {
            "name": "valid_config",
            "config": {
                "framework": "playwright",
                "ai_provider": "openai",
                "language": "python",
                "ai_temperature": 0.1,
                "test_timeout": 30000
            },
            "should_pass": True
        },
        {
            "name": "invalid_temperature",
            "config": {
                "framework": "playwright", 
                "ai_provider": "openai",
                "language": "python",
                "ai_temperature": 5.0,  # Invalid - too high
                "test_timeout": 30000
            },
            "should_pass": False
        },
        {
            "name": "invalid_timeout",
            "config": {
                "framework": "playwright",
                "ai_provider": "openai", 
                "language": "python",
                "ai_temperature": 0.1,
                "test_timeout": -1000  # Invalid - negative
            },
            "should_pass": False
        }
    ]
    
    for test_case in test_configs:
        print(f"\n  Testing {test_case['name']}:")
        
        try:
            config = btt.ConfigBuilder() \
                .from_kwargs(**test_case["config"]) \
                .build()
            
            # Validate the configuration
            errors = config.validate()
            
            if errors:
                print(f"    ✗ Validation failed: {errors}")
                if test_case["should_pass"]:
                    print(f"    ⚠ Expected to pass but found errors")
            else:
                print(f"    ✓ Validation passed")
                if not test_case["should_pass"]:
                    print(f"    ⚠ Expected to fail but validation passed")
            
            # Show optimization suggestions
            if hasattr(config, 'optimize_for_speed'):
                speed_config = btt.Config.from_dict(test_case["config"])
                speed_config.optimize_for_speed()
                print(f"    Speed optimization: AI analysis = {speed_config.enable_ai_analysis}")
                
                accuracy_config = btt.Config.from_dict(test_case["config"]) 
                accuracy_config.optimize_for_accuracy()
                print(f"    Accuracy optimization: Temperature = {accuracy_config.ai_temperature}")
            
        except Exception as e:
            print(f"    ✗ Config creation failed: {e}")
            if test_case["should_pass"]:
                print(f"    ⚠ Expected to pass but failed with error")


def main():
    """Run all configuration builder examples."""
    print("Browse-to-Test Configuration Builder Examples")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ Warning: OPENAI_API_KEY not found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("Some examples may fail without it.\n")
    
    try:
        # Run examples
        example_1_basic_config_builder()
        example_2_configuration_presets() 
        example_3_builder_chaining_patterns()
        example_4_environment_based_config()
        example_5_config_persistence()
        example_6_config_validation()
        
        # Show generated files
        print(f"\n📁 Generated files in {OUTPUT_DIR.relative_to(Path.cwd())}:")
        output_files = list(OUTPUT_DIR.glob("*_test.py")) + \
                      list(OUTPUT_DIR.glob("*_test.ts")) + \
                      list(OUTPUT_DIR.glob("*.json"))
        
        for file_path in sorted(output_files):
            if any(prefix in file_path.name for prefix in [
                'basic_config', 'fast_preset', 'balanced_preset', 
                'accurate_preset', 'production_preset', 'speed_optimized',
                'accuracy_focused', 'security_hardened', 'development_env',
                'staging_env', 'production_env', 'config_from_file',
                'browse_to_test_config'
            ]):
                size = file_path.stat().st_size
                print(f"   • {file_path.name} ({size:,} bytes)")
        
        print("\n✓ All configuration builder examples completed!")
        print("\nKey benefits of ConfigBuilder:")
        print("- Fluent, chainable interface for clean configuration")
        print("- Built-in presets for common scenarios") 
        print("- Environment-based configuration support")
        print("- Configuration validation and optimization")
        print("- File-based persistence (JSON/YAML)")
        print("- Type-safe configuration with sensible defaults")
        
    except Exception as e:
        print(f"\n✗ Configuration builder examples failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()