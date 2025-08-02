#!/usr/bin/env python3
"""
Configuration adapter to bridge SimpleConfig with legacy Config system.

This module handles the conversion between the new simplified configuration
and the existing complex configuration system, enabling backward compatibility
while providing a better developer experience.
"""

from typing import Dict, Any, List
from .simple_config import SimpleConfig
from .config import Config, AIConfig, OutputConfig, ProcessingConfig, SharedSetupConfig


class ConfigAdapter:
    """
    Adapter to convert SimpleConfig to legacy Config objects.
    
    This enables the new simplified interface to work with existing
    internal systems while maintaining backward compatibility.
    """
    
    @staticmethod
    def to_legacy_config(simple_config: SimpleConfig) -> Config:
        """
        Convert SimpleConfig to legacy Config object.
        
        Args:
            simple_config: New simplified configuration
            
        Returns:
            Legacy Config object with all internal settings properly configured
        """
        # Create AI configuration
        ai_config = AIConfig(
            provider=simple_config.ai_provider,
            model=simple_config.get_advanced("ai_model", ConfigAdapter._get_default_model(simple_config.ai_provider)),
            api_key=simple_config.api_key,
            base_url=simple_config.get_advanced("base_url"),
            temperature=simple_config.get_advanced("ai_temperature", 0.1),
            max_tokens=simple_config.get_advanced("max_tokens", 4000),
            timeout=simple_config.get_advanced("ai_timeout", 30),
            retry_attempts=simple_config.get_advanced("retry_attempts", 3),
            extra_params=simple_config.get_advanced("extra_params", {})
        )
        
        # Create shared setup configuration
        shared_setup = SharedSetupConfig(
            enabled=simple_config.get_advanced("enable_shared_setup", True),
            setup_dir=simple_config.get_advanced("setup_dir", "browse_to_test/output_langs/generated"),
            utilities_file=simple_config.get_advanced("utilities_file", "utilities.py"),
            constants_file=simple_config.get_advanced("constants_file", "constants.py"),
            framework_helpers_file=simple_config.get_advanced("framework_helpers_file", "exceptions.py"),
            generate_separate_files=simple_config.get_advanced("generate_separate_files", True),
            include_docstrings=simple_config.get_advanced("include_docstrings", True),
            organize_by_category=simple_config.get_advanced("organize_by_category", True),
            auto_generate_imports=simple_config.get_advanced("auto_generate_imports", True),
            force_regenerate=simple_config.get_advanced("force_regenerate", False)
        )
        
        # Create output configuration
        output_config = OutputConfig(
            framework=simple_config.framework,
            language=simple_config.language,
            test_type=simple_config.get_advanced("test_type", "script"),
            include_assertions=simple_config.include_assertions,
            include_waits=simple_config.get_advanced("include_waits", True),
            include_error_handling=simple_config.include_error_handling,
            include_logging=simple_config.get_advanced("include_logging", False),
            include_screenshots=simple_config.get_advanced("include_screenshots", False),
            add_comments=simple_config.get_advanced("add_comments", True),
            sensitive_data_keys=simple_config.get_advanced("sensitive_data_keys", []),
            mask_sensitive_data=simple_config.get_advanced("mask_sensitive_data", True),
            test_timeout=simple_config.test_timeout_seconds * 1000,  # Convert to milliseconds
            browser_options=simple_config.get_advanced("browser_options", {}),
            shared_setup=shared_setup,
            typescript_config=simple_config.get_advanced("typescript_config", {}),
            javascript_config=simple_config.get_advanced("javascript_config", {}),
            csharp_config=simple_config.get_advanced("csharp_config", {}),
            java_config=simple_config.get_advanced("java_config", {})
        )
        
        # Create processing configuration with smart defaults
        processing_config = ProcessingConfig(
            analyze_actions_with_ai=simple_config.get_advanced("enable_ai_analysis", True),
            optimize_selectors=simple_config.get_advanced("optimize_selectors", True),
            validate_actions=simple_config.get_advanced("validate_actions", True),
            strict_mode=simple_config.get_advanced("strict_mode", False),
            cache_ai_responses=simple_config.get_advanced("cache_ai_responses", True),
            max_cache_size=simple_config.get_advanced("max_cache_size", 1000),
            
            # Context collection settings
            collect_system_context=simple_config.get_advanced("enable_context_collection", True),
            context_cache_ttl=simple_config.get_advanced("context_cache_ttl", 3600),
            max_context_files=simple_config.get_advanced("max_context_files", 100),
            include_existing_tests=simple_config.get_advanced("include_existing_tests", True),
            include_documentation=simple_config.get_advanced("include_documentation", True),
            include_ui_components=simple_config.get_advanced("include_ui_components", True),
            include_api_endpoints=simple_config.get_advanced("include_api_endpoints", True),
            include_database_schema=simple_config.get_advanced("include_database_schema", False),
            include_recent_changes=simple_config.get_advanced("include_recent_changes", True),
            
            # Context analysis settings
            use_intelligent_analysis=simple_config.get_advanced("use_intelligent_analysis", True),
            context_similarity_threshold=simple_config.get_advanced("context_similarity_threshold", 0.3),
            max_similar_tests=simple_config.get_advanced("max_similar_tests", 5),
            context_analysis_depth=simple_config.get_advanced("context_analysis_depth", "medium"),
            
            # Directory scanning settings
            scan_test_directories=simple_config.get_advanced("scan_test_directories", 
                                                              ["tests/", "test/", "spec/", "e2e/", "__tests__/"]),
            scan_documentation_directories=simple_config.get_advanced("scan_documentation_directories",
                                                                       ["docs/", "documentation/", "README*"]),
            scan_component_directories=simple_config.get_advanced("scan_component_directories",
                                                                   ["components/", "src/components/", "lib/"]),
            exclude_directories=simple_config.get_advanced("exclude_directories",
                                                            ["node_modules/", ".git/", "__pycache__/", "venv/", "env/", ".venv/"]),
            
            # Context filtering settings
            filter_context_by_url=simple_config.get_advanced("filter_context_by_url", True),
            include_similar_domain_tests=simple_config.get_advanced("include_similar_domain_tests", True),
            max_context_prompt_size=simple_config.get_advanced("max_context_prompt_size", 8000)
        )
        
        # Create main configuration
        config = Config(
            ai=ai_config,
            output=output_config,
            processing=processing_config,
            debug=simple_config.get_advanced("debug", False),
            verbose=simple_config.get_advanced("verbose", False),
            log_level=simple_config.get_advanced("log_level", "INFO"),
            project_root=simple_config.get_advanced("project_root")
        )
        
        return config
    
    @staticmethod
    def _get_default_model(provider: str) -> str:
        """Get default model for AI provider."""
        defaults = {
            "openai": "gpt-4",
            "anthropic": "claude-3-sonnet-20240229",
            "azure": "gpt-4",
            "google": "gemini-pro"
        }
        return defaults.get(provider, "gpt-4")
    
    @staticmethod
    def from_legacy_config(legacy_config: Config) -> SimpleConfig:
        """
        Convert legacy Config to SimpleConfig.
        
        Args:
            legacy_config: Legacy Config object
            
        Returns:
            New SimpleConfig with equivalent settings
        """
        simple_config = SimpleConfig(
            framework=legacy_config.output.framework,
            language=legacy_config.output.language,
            ai_provider=legacy_config.ai.provider,
            api_key=legacy_config.ai.api_key,
            include_assertions=legacy_config.output.include_assertions,
            include_error_handling=legacy_config.output.include_error_handling,
            test_timeout_seconds=legacy_config.output.test_timeout // 1000
        )
        
        # Map advanced settings
        advanced_settings = {
            "ai_model": legacy_config.ai.model,
            "ai_temperature": legacy_config.ai.temperature,
            "max_tokens": legacy_config.ai.max_tokens,
            "base_url": legacy_config.ai.base_url,
            "ai_timeout": legacy_config.ai.timeout,
            "retry_attempts": legacy_config.ai.retry_attempts,
            "extra_params": legacy_config.ai.extra_params,
            
            "enable_context_collection": legacy_config.processing.collect_system_context,
            "enable_ai_analysis": legacy_config.processing.analyze_actions_with_ai,
            "include_logging": legacy_config.output.include_logging,
            "include_screenshots": legacy_config.output.include_screenshots,
            "mask_sensitive_data": legacy_config.output.mask_sensitive_data,
            "sensitive_data_keys": legacy_config.output.sensitive_data_keys,
            
            "context_analysis_depth": legacy_config.processing.context_analysis_depth,
            "max_context_files": legacy_config.processing.max_context_files,
            "context_similarity_threshold": legacy_config.processing.context_similarity_threshold,
            "max_similar_tests": legacy_config.processing.max_similar_tests,
            
            "debug": legacy_config.debug,
            "verbose": legacy_config.verbose,
            "log_level": legacy_config.log_level,
            "project_root": legacy_config.project_root,
        }
        
        simple_config.advanced(**advanced_settings)
        return simple_config


class PresetOptimizer:
    """
    Optimizes configuration presets based on usage patterns and performance data.
    
    This class dynamically adjusts preset configurations based on:
    - Historical performance data
    - User feedback
    - Framework-specific optimizations
    """
    
    @staticmethod
    def optimize_for_framework(simple_config: SimpleConfig) -> SimpleConfig:
        """
        Apply framework-specific optimizations to configuration.
        
        Args:
            simple_config: Base configuration to optimize
            
        Returns:
            Optimized configuration
        """
        framework = simple_config.framework
        
        # Framework-specific optimizations
        optimizations = {
            "playwright": {
                "include_waits": True,  # Playwright has good wait handling
                "browser_options": {"headless": True},
                "test_type": "script"
            },
            "selenium": {
                "include_waits": True,  # Selenium needs explicit waits
                "browser_options": {"headless": True},
                "test_type": "test"
            },
            "cypress": {
                "include_waits": False,  # Cypress handles waits automatically
                "test_type": "spec"
            }
        }
        
        if framework in optimizations:
            simple_config.advanced(**optimizations[framework])
        
        return simple_config
    
    @staticmethod
    def optimize_for_language(simple_config: SimpleConfig) -> SimpleConfig:
        """
        Apply language-specific optimizations to configuration.
        
        Args:
            simple_config: Base configuration to optimize
            
        Returns:
            Optimized configuration
        """
        language = simple_config.language
        
        # Language-specific optimizations
        optimizations = {
            "python": {
                "add_comments": True,
                "include_docstrings": True
            },
            "typescript": {
                "add_comments": True,
                "typescript_config": {"strict": True}
            },
            "javascript": {
                "add_comments": True,
                "javascript_config": {"async_await": True}
            }
        }
        
        if language in optimizations:
            simple_config.advanced(**optimizations[language])
        
        return simple_config