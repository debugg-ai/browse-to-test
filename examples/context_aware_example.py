#!/usr/bin/env python3
"""
Example demonstrating context-aware test generation with browse-to-test.

This example shows how the library can leverage existing tests, documentation,
and system knowledge to generate more intelligent and consistent test scripts.
"""

import browse_to_test as btt
import json


def main():
    """Demonstrate context-aware test generation."""
    
    # Sample automation data for a login flow
    automation_data = [
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
                "step_start_time": 1640995200.0,
                "elapsed_time": 1.2
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "<secret>username</secret>",
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
                            "id": "username",
                            "name": "username",
                            "data-testid": "username-input",
                            "type": "email",
                            "placeholder": "Enter your email"
                        },
                        "text_content": ""
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "<secret>password</secret>",
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
                            "id": "password",
                            "name": "password",
                            "data-testid": "password-input",
                            "type": "password",
                            "placeholder": "Enter your password"
                        }
                    }
                ]
            }
        },
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
                        "xpath": "//button[@data-testid='login-submit']",
                        "css_selector": "button[data-testid='login-submit']",
                        "attributes": {
                            "data-testid": "login-submit",
                            "type": "submit",
                            "class": "btn btn-primary"
                        },
                        "text_content": "Sign In"
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "text": "Successfully logged in",
                            "success": True
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        }
    ]
    
    print("🚀 Context-Aware Test Generation Example")
    print("=" * 50)
    
    # Example 1: Basic generation without context
    print("\n1. Basic Generation (No Context):")
    print("-" * 30)
    
    basic_config = btt.Config(
        ai=btt.AIConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.1
        ),
        output=btt.OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_error_handling=True
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=True,
            collect_system_context=False,  # Disabled for comparison
            use_intelligent_analysis=False
        )
    )
    
    try:
        converter_basic = btt.E2eTestConverter(basic_config)
        basic_script = converter_basic.convert(automation_data)
        print("✅ Basic script generated successfully")
        print(f"📄 Script length: {len(basic_script)} characters")
    except Exception as e:
        print(f"❌ Basic generation failed: {e}")
    
    # Example 2: Context-aware generation with intelligent analysis
    print("\n2. Context-Aware Generation:")
    print("-" * 30)
    
    context_config = btt.Config(
        ai=btt.AIConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.1
        ),
        output=btt.OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_error_handling=True,
            include_logging=True,
            sensitive_data_keys=["username", "password"]
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=True,
            collect_system_context=True,  # Enable context collection
            use_intelligent_analysis=True,  # Enable intelligent analysis
            include_existing_tests=True,
            include_documentation=True,
            include_ui_components=True,
            include_api_endpoints=True,
            context_analysis_depth="deep",
            max_similar_tests=5
        ),
        project_root=".",  # Current project for context collection
        verbose=True,
        debug=True
    )
    
    try:
        orchestrator_context = btt.E2eTestConverter(context_config)
        
        # First, let's see what the configuration validation shows
        validation = orchestrator_context.validate_configuration()
        print(f"🔧 Configuration valid: {validation['is_valid']}")
        print(f"📡 AI Provider: {validation['ai_provider_status']}")
        print(f"🔌 Plugin: {validation['plugin_status']}")
        print(f"🧠 Context Collector: {validation['context_collector_status']}")
        
        if validation['warnings']:
            print("⚠️  Warnings:")
            for warning in validation['warnings'][:3]:
                print(f"   - {warning}")
        
        # Generate preview first
        print("\n📋 Conversion Preview:")
        preview = orchestrator_context.preview_conversion(
            automation_data=automation_data,
            target_url="https://example.com/login",
            max_actions=5
        )
        
        print(f"   📊 Total actions: {preview.get('total_actions', 0)}")
        print(f"   🎯 Target framework: {preview.get('target_framework')}")
        print(f"   📚 Has context: {preview.get('has_context', False)}")
        print(f"   🧠 Has analysis: {preview.get('has_analysis', False)}")
        
        if preview.get('action_types'):
            print(f"   🎬 Action types: {', '.join(preview['action_types'].keys())}")
        
        if preview.get('context_summary'):
            ctx = preview['context_summary']
            print(f"   📁 Existing tests: {ctx.get('existing_tests', 0)}")
            print(f"   📖 Documentation: {ctx.get('documentation_files', 0)}")
            print(f"   🏗️  Project: {ctx.get('project_name', 'Unknown')}")
        
        if preview.get('similar_tests'):
            print(f"   🔗 Similar tests found: {len(preview['similar_tests'])}")
            for test in preview['similar_tests'][:2]:
                print(f"      - {test['file_path']} (similarity: {test['similarity_score']:.2f})")
        
        # Generate the actual context-aware script
        print("\n🎯 Generating context-aware script...")
        context_script = orchestrator_context.convert(automation_data)
        
        print("✅ Context-aware script generated successfully")
        print(f"📄 Script length: {len(context_script)} characters")
        
        # Show a portion of the generated script
        print("\n📜 Generated Script Preview:")
        print("-" * 40)
        script_lines = context_script.split('\n')
        for i, line in enumerate(script_lines[:20]):  # First 20 lines
            print(f"{i+1:2d}: {line}")
        if len(script_lines) > 20:
            print(f"... (and {len(script_lines) - 20} more lines)")
        
    except Exception as e:
        print(f"❌ Context-aware generation failed: {e}")
        if context_config.debug:
            import traceback
            traceback.print_exc()
    
    # Example 3: Multiple framework generation with context
    print("\n3. Multi-Framework Context-Aware Generation:")
    print("-" * 45)
    
    try:
        frameworks = ["playwright", "selenium"]
        available_frameworks = orchestrator_context.get_available_frameworks()
        
        print(f"🔌 Available frameworks: {', '.join(available_frameworks)}")
        
        # Filter to only available frameworks
        frameworks_to_test = [fw for fw in frameworks if fw in available_frameworks]
        
        if frameworks_to_test:
            multi_scripts = orchestrator_context.generate_with_multiple_frameworks(
                automation_data=automation_data,
                frameworks=frameworks_to_test,
                target_url="https://example.com/login"
            )
            
            print(f"✅ Generated scripts for {len(multi_scripts)} frameworks:")
            for framework, script in multi_scripts.items():
                script_lines = len(script.split('\n'))
                print(f"   📝 {framework}: {script_lines} lines")
        else:
            print("⚠️  No compatible frameworks available for demonstration")
        
    except Exception as e:
        print(f"❌ Multi-framework generation failed: {e}")
    
    # Example 4: Configuration optimization
    print("\n4. Configuration Optimization:")
    print("-" * 30)
    
    print("🚀 Speed-optimized configuration:")
    speed_config = btt.Config.from_dict(context_config.to_dict())
    speed_config.optimize_for_speed()
    
    print(f"   📚 Context collection: {speed_config.processing.collect_system_context}")
    print(f"   🧠 Intelligent analysis: {speed_config.processing.use_intelligent_analysis}")
    print(f"   📊 Analysis depth: {speed_config.processing.context_analysis_depth}")
    print(f"   🔢 Max tokens: {speed_config.ai.max_tokens}")
    
    print("\n🎯 Accuracy-optimized configuration:")
    accuracy_config = btt.Config.from_dict(context_config.to_dict())
    accuracy_config.optimize_for_accuracy()
    
    print(f"   📚 Context collection: {accuracy_config.processing.collect_system_context}")
    print(f"   🧠 Intelligent analysis: {accuracy_config.processing.use_intelligent_analysis}")
    print(f"   📊 Analysis depth: {accuracy_config.processing.context_analysis_depth}")
    print(f"   🔢 Max tokens: {accuracy_config.ai.max_tokens}")
    print(f"   📁 Max context files: {accuracy_config.processing.max_context_files}")
    
    # Example 5: Environment-based configuration
    print("\n5. Environment-Based Configuration:")
    print("-" * 35)
    
    # Show how to use environment variables
    print("🌍 Environment variables for configuration:")
    print("   export BROWSE_TO_TEST_AI_PROVIDER=openai")
    print("   export BROWSE_TO_TEST_OUTPUT_FRAMEWORK=playwright")
    print("   export BROWSE_TO_TEST_PROCESSING_COLLECT_CONTEXT=true")
    print("   export BROWSE_TO_TEST_PROCESSING_USE_INTELLIGENT_ANALYSIS=true")
    print("   export BROWSE_TO_TEST_DEBUG=true")
    print("   export OPENAI_API_KEY=your-api-key")
    
    # Demonstrate loading from environment
    try:
        env_config = btt.Config.from_env()
        print(f"\n✅ Environment config loaded:")
        print(f"   🤖 AI Provider: {env_config.ai.provider}")
        print(f"   🎯 Framework: {env_config.output.framework}")
        print(f"   📚 Context enabled: {env_config.processing.collect_system_context}")
        print(f"   🔑 API key configured: {'Yes' if env_config.ai.api_key else 'No'}")
    except Exception as e:
        print(f"⚠️  Environment config: Using defaults ({e})")
    
    print("\n🎉 Context-aware test generation example completed!")
    print("\nKey benefits of context-aware generation:")
    print("✨ Leverages existing test patterns for consistency")
    print("🧠 Uses AI to understand project-specific conventions")
    print("🔍 Identifies similar tests to avoid duplication")
    print("📚 Incorporates documentation and system knowledge")
    print("⚡ Optimizes selectors based on project patterns")
    print("🛡️  Better handling of sensitive data and configuration")


if __name__ == "__main__":
    main() 