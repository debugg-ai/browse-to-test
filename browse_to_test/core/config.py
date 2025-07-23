#!/usr/bin/env python3
"""
Configuration management for the browse-to-test library.
"""

import os
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


@dataclass
class AIConfig:
    """Configuration for AI providers."""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    retry_attempts: int = 3
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    framework: str = "playwright"
    language: str = "python"
    test_type: str = "script"  # script, test, spec
    include_assertions: bool = True
    include_waits: bool = True
    include_error_handling: bool = True
    include_logging: bool = False
    include_screenshots: bool = False
    add_comments: bool = True
    sensitive_data_keys: List[str] = field(default_factory=list)
    mask_sensitive_data: bool = True
    test_timeout: int = 30000
    browser_options: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def framework_config(self) -> Dict[str, Any]:
        """Get framework-specific configuration."""
        return self.browser_options


@dataclass
class ProcessingConfig:
    """Configuration for data processing."""
    analyze_actions_with_ai: bool = True
    optimize_selectors: bool = True
    validate_actions: bool = True
    strict_mode: bool = False
    cache_ai_responses: bool = True
    max_cache_size: int = 1000
    
    # Context collection settings
    collect_system_context: bool = True
    context_cache_ttl: int = 3600  # 1 hour in seconds
    max_context_files: int = 100
    include_existing_tests: bool = True
    include_documentation: bool = True
    include_ui_components: bool = True
    include_api_endpoints: bool = True
    include_database_schema: bool = False  # More expensive, disabled by default
    include_recent_changes: bool = True
    
    # Context analysis settings
    use_intelligent_analysis: bool = True
    context_similarity_threshold: float = 0.3
    max_similar_tests: int = 5
    context_analysis_depth: str = "deep"  # shallow, medium, deep
    
    # File scanning settings
    scan_test_directories: List[str] = field(default_factory=lambda: ["tests/", "test/", "spec/", "e2e/", "__tests__/"])
    scan_documentation_directories: List[str] = field(default_factory=lambda: ["docs/", "documentation/", "README*"])
    scan_component_directories: List[str] = field(default_factory=lambda: ["components/", "src/components/", "lib/"])
    exclude_directories: List[str] = field(default_factory=lambda: ["node_modules/", ".git/", "__pycache__/", "venv/", "env/", ".venv/"])
    
    # Context filtering settings
    filter_context_by_url: bool = True
    include_similar_domain_tests: bool = True
    max_context_prompt_size: int = 8000  # Max characters in context prompt


@dataclass
class Config:
    """Main configuration class."""
    ai: AIConfig = field(default_factory=AIConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    # Global settings
    debug: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    project_root: Optional[str] = None
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """Create Config from dictionary."""
        config = cls()
        
        if 'ai' in config_dict:
            ai_dict = config_dict['ai']
            for key, value in ai_dict.items():
                if hasattr(config.ai, key):
                    setattr(config.ai, key, value)
        
        if 'output' in config_dict:
            output_dict = config_dict['output']
            for key, value in output_dict.items():
                if hasattr(config.output, key):
                    setattr(config.output, key, value)
        
        if 'processing' in config_dict:
            processing_dict = config_dict['processing']
            for key, value in processing_dict.items():
                if hasattr(config.processing, key):
                    setattr(config.processing, key, value)
        
        # Global settings
        for key in ['debug', 'verbose', 'log_level', 'project_root']:
            if key in config_dict:
                setattr(config, key, config_dict[key])
        
        return config
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Config':
        """Create Config from JSON or YAML file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path) as f:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                config_dict = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {file_path.suffix}")
        
        return cls.from_dict(config_dict)
    
    @classmethod
    def from_env(cls, prefix: str = "BROWSE_TO_TEST") -> 'Config':
        """Create Config from environment variables."""
        config = cls()
        
        # AI settings
        if f"{prefix}_AI_PROVIDER" in os.environ:
            config.ai.provider = os.environ[f"{prefix}_AI_PROVIDER"]
        if f"{prefix}_AI_MODEL" in os.environ:
            config.ai.model = os.environ[f"{prefix}_AI_MODEL"]
        if f"{prefix}_AI_API_KEY" in os.environ:
            config.ai.api_key = os.environ[f"{prefix}_AI_API_KEY"]
        if f"{prefix}_AI_TEMPERATURE" in os.environ:
            config.ai.temperature = float(os.environ[f"{prefix}_AI_TEMPERATURE"])
        if f"{prefix}_AI_MAX_TOKENS" in os.environ:
            config.ai.max_tokens = int(os.environ[f"{prefix}_AI_MAX_TOKENS"])
        
        # Output settings
        if f"{prefix}_OUTPUT_FRAMEWORK" in os.environ:
            config.output.framework = os.environ[f"{prefix}_OUTPUT_FRAMEWORK"]
        if f"{prefix}_OUTPUT_LANGUAGE" in os.environ:
            config.output.language = os.environ[f"{prefix}_OUTPUT_LANGUAGE"]
        if f"{prefix}_OUTPUT_INCLUDE_ASSERTIONS" in os.environ:
            config.output.include_assertions = os.environ[f"{prefix}_OUTPUT_INCLUDE_ASSERTIONS"].lower() == "true"
        if f"{prefix}_OUTPUT_INCLUDE_ERROR_HANDLING" in os.environ:
            config.output.include_error_handling = os.environ[f"{prefix}_OUTPUT_INCLUDE_ERROR_HANDLING"].lower() == "true"
        
        # Processing settings
        if f"{prefix}_PROCESSING_ANALYZE_WITH_AI" in os.environ:
            config.processing.analyze_actions_with_ai = os.environ[f"{prefix}_PROCESSING_ANALYZE_WITH_AI"].lower() == "true"
        if f"{prefix}_PROCESSING_COLLECT_CONTEXT" in os.environ:
            config.processing.collect_system_context = os.environ[f"{prefix}_PROCESSING_COLLECT_CONTEXT"].lower() == "true"
        if f"{prefix}_PROCESSING_USE_INTELLIGENT_ANALYSIS" in os.environ:
            config.processing.use_intelligent_analysis = os.environ[f"{prefix}_PROCESSING_USE_INTELLIGENT_ANALYSIS"].lower() == "true"
        if f"{prefix}_PROCESSING_CONTEXT_ANALYSIS_DEPTH" in os.environ:
            config.processing.context_analysis_depth = os.environ[f"{prefix}_PROCESSING_CONTEXT_ANALYSIS_DEPTH"]
        
        # Global settings
        if f"{prefix}_DEBUG" in os.environ:
            config.debug = os.environ[f"{prefix}_DEBUG"].lower() == "true"
        if f"{prefix}_VERBOSE" in os.environ:
            config.verbose = os.environ[f"{prefix}_VERBOSE"].lower() == "true"
        if f"{prefix}_LOG_LEVEL" in os.environ:
            config.log_level = os.environ[f"{prefix}_LOG_LEVEL"]
        if f"{prefix}_PROJECT_ROOT" in os.environ:
            config.project_root = os.environ[f"{prefix}_PROJECT_ROOT"]
        
        # Also check for standard AI provider environment variables
        if not config.ai.api_key:
            if config.ai.provider == "openai" and "OPENAI_API_KEY" in os.environ:
                config.ai.api_key = os.environ["OPENAI_API_KEY"]
            elif config.ai.provider == "anthropic" and "ANTHROPIC_API_KEY" in os.environ:
                config.ai.api_key = os.environ["ANTHROPIC_API_KEY"]
            elif config.ai.provider == "azure" and "AZURE_OPENAI_API_KEY" in os.environ:
                config.ai.api_key = os.environ["AZURE_OPENAI_API_KEY"]
                if "AZURE_OPENAI_ENDPOINT" in os.environ:
                    config.ai.base_url = os.environ["AZURE_OPENAI_ENDPOINT"]
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Config to dictionary."""
        return {
            'ai': {
                'provider': self.ai.provider,
                'model': self.ai.model,
                'api_key': self.ai.api_key,
                'base_url': self.ai.base_url,
                'temperature': self.ai.temperature,
                'max_tokens': self.ai.max_tokens,
                'timeout': self.ai.timeout,
                'retry_attempts': self.ai.retry_attempts,
                'extra_params': self.ai.extra_params,
            },
            'output': {
                'framework': self.output.framework,
                'language': self.output.language,
                'test_type': self.output.test_type,
                'include_assertions': self.output.include_assertions,
                'include_waits': self.output.include_waits,
                'include_error_handling': self.output.include_error_handling,
                'include_logging': self.output.include_logging,
                'include_screenshots': self.output.include_screenshots,
                'sensitive_data_keys': self.output.sensitive_data_keys,
                'mask_sensitive_data': self.output.mask_sensitive_data,
                'test_timeout': self.output.test_timeout,
                'browser_options': self.output.browser_options,
            },
            'processing': {
                'analyze_actions_with_ai': self.processing.analyze_actions_with_ai,
                'optimize_selectors': self.processing.optimize_selectors,
                'validate_actions': self.processing.validate_actions,
                'strict_mode': self.processing.strict_mode,
                'cache_ai_responses': self.processing.cache_ai_responses,
                'max_cache_size': self.processing.max_cache_size,
                'collect_system_context': self.processing.collect_system_context,
                'context_cache_ttl': self.processing.context_cache_ttl,
                'max_context_files': self.processing.max_context_files,
                'include_existing_tests': self.processing.include_existing_tests,
                'include_documentation': self.processing.include_documentation,
                'include_ui_components': self.processing.include_ui_components,
                'include_api_endpoints': self.processing.include_api_endpoints,
                'include_database_schema': self.processing.include_database_schema,
                'include_recent_changes': self.processing.include_recent_changes,
                'use_intelligent_analysis': self.processing.use_intelligent_analysis,
                'context_similarity_threshold': self.processing.context_similarity_threshold,
                'max_similar_tests': self.processing.max_similar_tests,
                'context_analysis_depth': self.processing.context_analysis_depth,
                'scan_test_directories': self.processing.scan_test_directories,
                'scan_documentation_directories': self.processing.scan_documentation_directories,
                'scan_component_directories': self.processing.scan_component_directories,
                'exclude_directories': self.processing.exclude_directories,
                'filter_context_by_url': self.processing.filter_context_by_url,
                'include_similar_domain_tests': self.processing.include_similar_domain_tests,
                'max_context_prompt_size': self.processing.max_context_prompt_size,
            },
            'debug': self.debug,
            'verbose': self.verbose,
            'log_level': self.log_level,
            'project_root': self.project_root,
        }
    
    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save Config to JSON or YAML file."""
        file_path = Path(file_path)
        
        config_dict = self.to_dict()
        
        with open(file_path, 'w') as f:
            if file_path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif file_path.suffix.lower() == '.json':
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {file_path.suffix}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate AI config
        if not self.ai.provider:
            errors.append("AI provider cannot be empty")
        
        if not self.ai.model:
            errors.append("AI model cannot be empty")
        
        if self.ai.temperature < 0 or self.ai.temperature > 2:
            errors.append("AI temperature must be between 0 and 2")
        
        if self.ai.max_tokens < 1:
            errors.append("AI max_tokens must be positive")
        
        # Validate output config
        if not self.output.framework:
            errors.append("Output framework cannot be empty")
        
        if not self.output.language:
            errors.append("Output language cannot be empty")
        
        if self.output.test_timeout < 1000:
            errors.append("Test timeout must be at least 1000ms")
        
        # Validate processing config
        if self.processing.max_cache_size < 0:
            errors.append("Max cache size cannot be negative")
        
        if self.processing.context_cache_ttl < 0:
            errors.append("Context cache TTL cannot be negative")
        
        if self.processing.context_similarity_threshold < 0 or self.processing.context_similarity_threshold > 1:
            errors.append("Context similarity threshold must be between 0 and 1")
        
        if self.processing.max_similar_tests < 0:
            errors.append("Max similar tests cannot be negative")
        
        if self.processing.context_analysis_depth not in ["shallow", "medium", "deep"]:
            errors.append("Context analysis depth must be 'shallow', 'medium', or 'deep'")
        
        if self.processing.max_context_files < 0:
            errors.append("Max context files cannot be negative")
        
        if self.processing.max_context_prompt_size < 1000:
            errors.append("Max context prompt size should be at least 1000 characters")
        
        # Validate global config
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        
        return errors
    
    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """Update configuration from dictionary of changes."""
        if 'ai' in updates:
            for key, value in updates['ai'].items():
                if hasattr(self.ai, key):
                    setattr(self.ai, key, value)
        
        if 'output' in updates:
            for key, value in updates['output'].items():
                if hasattr(self.output, key):
                    setattr(self.output, key, value)
        
        if 'processing' in updates:
            for key, value in updates['processing'].items():
                if hasattr(self.processing, key):
                    setattr(self.processing, key, value)
        
        # Global settings
        for key in ['debug', 'verbose', 'log_level', 'project_root']:
            if key in updates:
                setattr(self, key, updates[key])
    
    def get_context_collection_config(self) -> Dict[str, Any]:
        """Get configuration specific to context collection."""
        return {
            'collect_system_context': self.processing.collect_system_context,
            'context_cache_ttl': self.processing.context_cache_ttl,
            'max_context_files': self.processing.max_context_files,
            'include_existing_tests': self.processing.include_existing_tests,
            'include_documentation': self.processing.include_documentation,
            'include_ui_components': self.processing.include_ui_components,
            'include_api_endpoints': self.processing.include_api_endpoints,
            'include_database_schema': self.processing.include_database_schema,
            'include_recent_changes': self.processing.include_recent_changes,
            'scan_test_directories': self.processing.scan_test_directories,
            'scan_documentation_directories': self.processing.scan_documentation_directories,
            'scan_component_directories': self.processing.scan_component_directories,
            'exclude_directories': self.processing.exclude_directories,
            'filter_context_by_url': self.processing.filter_context_by_url,
            'include_similar_domain_tests': self.processing.include_similar_domain_tests,
            'project_root': self.project_root,
            'debug': self.debug,
        }
    
    def get_ai_analysis_config(self) -> Dict[str, Any]:
        """Get configuration specific to AI analysis."""
        return {
            'use_intelligent_analysis': self.processing.use_intelligent_analysis,
            'context_similarity_threshold': self.processing.context_similarity_threshold,
            'max_similar_tests': self.processing.max_similar_tests,
            'context_analysis_depth': self.processing.context_analysis_depth,
            'max_context_prompt_size': self.processing.max_context_prompt_size,
            'analyze_actions_with_ai': self.processing.analyze_actions_with_ai,
            'target_framework': self.output.framework,
            'target_language': self.output.language,
            'debug': self.debug,
        }
    
    def optimize_for_speed(self) -> None:
        """Optimize configuration for faster processing (less thorough analysis)."""
        self.processing.collect_system_context = False
        self.processing.use_intelligent_analysis = False
        self.processing.include_ui_components = False
        self.processing.include_api_endpoints = False
        self.processing.include_database_schema = False
        self.processing.include_recent_changes = False
        self.processing.context_analysis_depth = "shallow"
        self.processing.max_context_files = 20
        self.ai.max_tokens = 2000
    
    def optimize_for_accuracy(self) -> None:
        """Optimize configuration for more accurate analysis (slower but more thorough)."""
        self.processing.collect_system_context = True
        self.processing.use_intelligent_analysis = True
        self.processing.include_ui_components = True
        self.processing.include_api_endpoints = True
        self.processing.include_database_schema = True
        self.processing.include_recent_changes = True
        self.processing.context_analysis_depth = "deep"
        self.processing.max_context_files = 200
        self.ai.max_tokens = 8000
        self.processing.max_context_prompt_size = 12000
    
    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config(provider={self.ai.provider}, framework={self.output.framework}, context={self.processing.collect_system_context})" 