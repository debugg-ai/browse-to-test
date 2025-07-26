#!/usr/bin/env python3
"""
Configuration management for the browse-to-test library.
"""

import os
import json
try:
    import yaml
except ImportError:
    yaml = None
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from .comment_manager import CommentManager


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
class SharedSetupConfig:
    """Configuration for shared setup generation."""
    enabled: bool = True
    setup_dir: str = "browse_to_test/output_langs/generated"
    utilities_file: str = "utilities.py"
    constants_file: str = "constants.py" 
    framework_helpers_file: str = "exceptions.py"
    generate_separate_files: bool = True
    include_docstrings: bool = True
    organize_by_category: bool = True
    auto_generate_imports: bool = True
    force_regenerate: bool = False


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
    
    # Shared setup configuration
    shared_setup: SharedSetupConfig = field(default_factory=SharedSetupConfig)
    
    # Language-specific configuration
    typescript_config: Dict[str, Any] = field(default_factory=dict)
    javascript_config: Dict[str, Any] = field(default_factory=dict)
    csharp_config: Dict[str, Any] = field(default_factory=dict)
    java_config: Dict[str, Any] = field(default_factory=dict)
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        "python": {
            "extension": ".py", 
            "comment_prefix": "#",
            "async_syntax": "async def",
            "import_syntax": "import {module}",
            "from_import_syntax": "from {module} import {items}"
        },
        "typescript": {
            "extension": ".ts",
            "comment_prefix": "//", 
            "async_syntax": "async function",
            "import_syntax": "import {{ {items} }} from '{module}'",
            "from_import_syntax": "import {{ {items} }} from '{module}'"
        },
        "javascript": {
            "extension": ".js",
            "comment_prefix": "//",
            "async_syntax": "async function", 
            "import_syntax": "import {{ {items} }} from '{module}'",
            "from_import_syntax": "import {{ {items} }} from '{module}'"
        },
        "csharp": {
            "extension": ".cs",
            "comment_prefix": "//",
            "async_syntax": "public async Task",
            "import_syntax": "using {module};",
            "from_import_syntax": "using {module};"
        },
        "java": {
            "extension": ".java", 
            "comment_prefix": "//",
            "async_syntax": "public CompletableFuture<Void>",
            "import_syntax": "import {module};",
            "from_import_syntax": "import {module};"
        }
    }
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.language and self.language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.language}. Supported: {list(self.SUPPORTED_LANGUAGES.keys())}")
    
    @property
    def framework_config(self) -> Dict[str, Any]:
        """Get framework-specific configuration."""
        return self.browser_options
    
    @property 
    def language_config(self) -> Dict[str, Any]:
        """Get language-specific configuration and syntax."""
        base_config = self.SUPPORTED_LANGUAGES.get(self.language, {})
        
        # Merge with language-specific overrides
        if self.language == "typescript":
            base_config.update(self.typescript_config)
        elif self.language == "javascript":
            base_config.update(self.javascript_config)
        elif self.language == "csharp":
            base_config.update(self.csharp_config)
        elif self.language == "java":
            base_config.update(self.java_config)
            
        return base_config
    
    @property
    def file_extension(self) -> str:
        """Get the file extension for the target language."""
        return self.language_config.get("extension", ".py")
    
    @property
    def comment_prefix(self) -> str:
        """Get the comment prefix for the target language.""" 
        return self.language_config.get("comment_prefix", "#")
    
    @property
    def comment_manager(self) -> CommentManager:
        """Get a comment manager instance for the target language."""
        return CommentManager(self.language)
    
    def get_framework_language_combination(self) -> str:
        """Get a string representing the framework-language combination."""
        return f"{self.framework}_{self.language}"


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
                if yaml is None:
                    raise ImportError("PyYAML is required to load YAML config files. Install with: pip install PyYAML")
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


class ConfigBuilder:
    """
    Builder pattern for creating Config objects with a fluent interface.
    
    This provides a much simpler way to create configurations:
    
    Example:
        >>> config = ConfigBuilder() \\
        ...     .framework("playwright") \\
        ...     .ai_provider("openai") \\
        ...     .language("python") \\
        ...     .enable_context_collection() \\
        ...     .build()
    """
    
    def __init__(self):
        """Initialize builder with default config."""
        self._config = Config()
    
    def framework(self, framework: str) -> 'ConfigBuilder':
        """Set the output framework."""
        self._config.output.framework = framework
        return self
    
    def ai_provider(self, provider: str, model: str = None, api_key: str = None) -> 'ConfigBuilder':
        """Set AI provider configuration."""
        self._config.ai.provider = provider
        if model:
            self._config.ai.model = model
        if api_key:
            self._config.ai.api_key = api_key
        return self
    
    def language(self, language: str) -> 'ConfigBuilder':
        """Set the target language."""
        self._config.output.language = language
        return self
    
    def enable_context_collection(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable or disable context collection."""
        self._config.processing.collect_system_context = enabled
        return self
    
    def enable_ai_analysis(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable or disable AI analysis."""
        self._config.processing.analyze_actions_with_ai = enabled
        return self
    
    def include_assertions(self, include: bool = True) -> 'ConfigBuilder':
        """Include assertions in generated tests."""
        self._config.output.include_assertions = include
        return self
    
    def include_error_handling(self, include: bool = True) -> 'ConfigBuilder':
        """Include error handling in generated tests."""
        self._config.output.include_error_handling = include
        return self
    
    def include_logging(self, include: bool = True) -> 'ConfigBuilder':
        """Include logging statements in generated tests."""
        self._config.output.include_logging = include
        return self
    
    def debug(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable debug mode."""
        self._config.debug = enabled
        return self
    
    def temperature(self, temp: float) -> 'ConfigBuilder':
        """Set AI temperature."""
        self._config.ai.temperature = temp
        return self
    
    def timeout(self, timeout_ms: int) -> 'ConfigBuilder':
        """Set test timeout in milliseconds."""
        self._config.output.test_timeout = timeout_ms
        return self
    
    def sensitive_data_keys(self, keys: List[str]) -> 'ConfigBuilder':
        """Set keys that contain sensitive data."""
        self._config.output.sensitive_data_keys = keys
        return self
    
    def project_root(self, path: str) -> 'ConfigBuilder':
        """Set project root directory."""
        self._config.project_root = path
        return self
    
    def fast_mode(self) -> 'ConfigBuilder':
        """Configure for fast processing (less thorough)."""
        self._config.optimize_for_speed()
        return self
    
    def thorough_mode(self) -> 'ConfigBuilder':
        """Configure for thorough processing (slower but more accurate)."""
        self._config.optimize_for_accuracy()
        return self
    
    def from_dict(self, config_dict: Dict[str, Any]) -> 'ConfigBuilder':
        """Update configuration from dictionary."""
        if config_dict:
            self._config.update_from_dict(config_dict)
        return self
    
    def from_kwargs(self, **kwargs) -> 'ConfigBuilder':
        """Update configuration from keyword arguments."""
        # Map common kwargs to config settings
        if 'api_key' in kwargs:
            self._config.ai.api_key = kwargs['api_key']
        if 'model' in kwargs:
            self._config.ai.model = kwargs['model']
        if 'temperature' in kwargs:
            self._config.ai.temperature = kwargs['temperature']
        if 'timeout' in kwargs:
            self._config.output.test_timeout = kwargs['timeout']
        if 'include_assertions' in kwargs:
            self._config.output.include_assertions = kwargs['include_assertions']
        if 'include_error_handling' in kwargs:
            self._config.output.include_error_handling = kwargs['include_error_handling']
        if 'debug' in kwargs:
            self._config.debug = kwargs['debug']
        if 'project_root' in kwargs:
            self._config.project_root = kwargs['project_root']
        if 'context_collection' in kwargs:
            self._config.processing.collect_system_context = kwargs['context_collection']
        
        return self
    
    def build(self) -> Config:
        """Build and return the final configuration."""
        # Validate configuration before returning
        errors = self._config.validate()
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return self._config