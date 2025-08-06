#!/usr/bin/env python3
"""
Unified configuration system for browse-to-test library.

This module consolidates all configuration functionality into a single, 
clean interface that eliminates confusion and redundancy.
"""

import os
import json
from dataclasses import dataclass, field, MISSING
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum

try:
    import yaml
except ImportError:
    yaml = None


class ConfigPreset(Enum):
    """Pre-configured settings for common use cases."""
    FAST = "fast"           # Speed-optimized, minimal analysis
    BALANCED = "balanced"   # Good balance of speed and accuracy  
    ACCURATE = "accurate"   # Accuracy-optimized, comprehensive analysis
    PRODUCTION = "production"  # Production-ready with error handling


@dataclass
class Config:
    """
    Unified configuration for browse-to-test library.
    
    This single configuration class handles all aspects of the library:
    - AI provider settings
    - Output generation options
    - Processing preferences
    - Framework-specific settings
    
    Example:
        >>> config = Config(framework="playwright", ai_provider="openai")
        >>> config = Config.from_preset(ConfigPreset.PRODUCTION)
    """
    
    # Core settings (most users only need these)
    framework: str = "playwright"
    language: str = "python"
    ai_provider: str = "openai"
    ai_model: Optional[str] = None  # Auto-selected if None
    api_key: Optional[str] = None   # Auto-detected if None
    
    # Common customizations
    include_assertions: bool = True
    include_error_handling: bool = True
    include_waits: bool = True
    include_logging: bool = False
    include_screenshots: bool = False
    add_comments: bool = True
    test_timeout: int = 30000  # milliseconds
    
    # AI settings
    ai_temperature: float = 0.1
    ai_max_tokens: int = 4000
    ai_timeout: int = 30
    ai_retry_attempts: int = 3
    ai_base_url: Optional[str] = None
    ai_extra_params: Dict[str, Any] = field(default_factory=dict)
    
    # Processing settings
    enable_context_collection: bool = True
    enable_ai_analysis: bool = True
    mask_sensitive_data: bool = True
    sensitive_data_keys: List[str] = field(default_factory=lambda: [
        "password", "pass", "pwd", "secret", "token", "key", "auth", 
        "api_key", "email", "username", "credit_card", "cc", "card_number", 
        "ssn", "social"
    ])
    strict_mode: bool = False
    context_analysis_depth: str = "medium"
    max_similar_tests: int = 5
    
    # Output settings
    test_type: str = "script"  # script, test, spec
    browser_options: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced settings (rarely changed)
    enable_final_script_analysis: bool = False
    # Note: debug, verbose, and log_level are implemented as properties
    
    # Language metadata (internal use)
    _language_metadata: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
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
        }
    })
    
    def __init__(self, ai=None, output=None, processing=None, **kwargs):
        """
        Initialize Config with backward compatibility for old constructor style.
        
        Supports both new style:
            Config(framework="playwright", ai_provider="openai")
        
        And old style:
            Config(ai=AIConfig(...), output=OutputConfig(...), processing=ProcessingConfig(...))
        """
        # Handle old-style constructor with separate config objects
        if ai is not None or output is not None or processing is not None:
            # Extract values from old-style config objects
            merged_kwargs = kwargs.copy()
            
            if ai is not None:
                if hasattr(ai, 'provider'):
                    merged_kwargs['ai_provider'] = ai.provider
                if hasattr(ai, 'model'):
                    merged_kwargs['ai_model'] = ai.model
                if hasattr(ai, 'api_key'):
                    merged_kwargs['api_key'] = ai.api_key
                if hasattr(ai, 'temperature'):
                    merged_kwargs['ai_temperature'] = ai.temperature
                if hasattr(ai, 'max_tokens'):
                    merged_kwargs['ai_max_tokens'] = ai.max_tokens
            
            if output is not None:
                if hasattr(output, 'framework'):
                    merged_kwargs['framework'] = output.framework
                if hasattr(output, 'language'):
                    merged_kwargs['language'] = output.language
                if hasattr(output, 'include_assertions'):
                    merged_kwargs['include_assertions'] = output.include_assertions
                if hasattr(output, 'include_error_handling'):
                    merged_kwargs['include_error_handling'] = output.include_error_handling
                if hasattr(output, 'include_logging'):
                    merged_kwargs['include_logging'] = output.include_logging
                if hasattr(output, 'test_timeout'):
                    merged_kwargs['test_timeout'] = output.test_timeout
                if hasattr(output, 'sensitive_data_keys'):
                    merged_kwargs['sensitive_data_keys'] = output.sensitive_data_keys
            
            if processing is not None:
                if hasattr(processing, 'collect_system_context'):
                    merged_kwargs['enable_context_collection'] = processing.collect_system_context
                if hasattr(processing, 'analyze_actions_with_ai'):
                    merged_kwargs['enable_ai_analysis'] = processing.analyze_actions_with_ai
                if hasattr(processing, 'use_intelligent_analysis'):
                    merged_kwargs['enable_ai_analysis'] = processing.use_intelligent_analysis
                if hasattr(processing, 'context_analysis_depth'):
                    merged_kwargs['context_analysis_depth'] = processing.context_analysis_depth
                if hasattr(processing, 'max_similar_tests'):
                    merged_kwargs['max_similar_tests'] = processing.max_similar_tests
                if hasattr(processing, 'include_existing_tests'):
                    merged_kwargs['_include_existing_tests'] = processing.include_existing_tests
                if hasattr(processing, 'max_context_files'):
                    merged_kwargs['_max_context_files'] = processing.max_context_files
                if hasattr(processing, 'scan_test_directories'):
                    merged_kwargs['_scan_test_directories'] = processing.scan_test_directories
            
            # Initialize using the from_dict method which handles backward compatibility
            temp_config = Config.from_dict(merged_kwargs)
            
            # Copy all field values from temp_config to self
            for field_name in self.__dataclass_fields__:
                setattr(self, field_name, getattr(temp_config, field_name))
            
            # Set private attributes and property-backed values
            if hasattr(temp_config, '_project_root'):
                self._project_root = temp_config._project_root
                
            # Set ProcessingProxy-specific attributes
            if '_include_existing_tests' in merged_kwargs:
                self._include_existing_tests = merged_kwargs['_include_existing_tests']
            if '_max_context_files' in merged_kwargs:
                self._max_context_files = merged_kwargs['_max_context_files']
            if '_scan_test_directories' in merged_kwargs:
                self._scan_test_directories = merged_kwargs['_scan_test_directories']
            
            # Handle fields passed in constructor directly from ProcessingConfig
            if hasattr(processing, 'scan_test_directories') and processing.scan_test_directories:
                self._scan_test_directories = processing.scan_test_directories
            
            # Handle property-backed fields (debug, verbose, log_level)
            if 'debug' in merged_kwargs:
                self.debug = merged_kwargs['debug']
            if 'verbose' in merged_kwargs:
                self.verbose = merged_kwargs['verbose']
            if 'log_level' in merged_kwargs:
                self.log_level = merged_kwargs['log_level']
            if 'project_root' in merged_kwargs:
                self.project_root = merged_kwargs['project_root']
                
        else:
            # New-style constructor - use dataclass initialization
            # Set defaults first
            for field_name, field_def in self.__dataclass_fields__.items():
                if field_def.default is not MISSING:
                    setattr(self, field_name, field_def.default)
                elif field_def.default_factory is not MISSING:
                    setattr(self, field_name, field_def.default_factory())
                else:
                    # Required field without default
                    setattr(self, field_name, None)
            
            # Override with provided kwargs
            for key, value in kwargs.items():
                if key in self.__dataclass_fields__:
                    setattr(self, key, value)
        
        # Always call post_init for validation and setup
        self.__post_init__()
    
    
    def __post_init__(self):
        """Apply smart defaults and validate configuration."""
        # Auto-detect API key if not provided
        if not self.api_key:
            self.api_key = self._detect_api_key()
        
        # Auto-select AI model if not provided
        if not self.ai_model:
            self.ai_model = self._get_default_model()
        
        # Initialize project_root if not set
        if not hasattr(self, '_project_root'):
            self._project_root = None
        
        # Validate configuration
        self._validate()
    
    def _detect_api_key(self) -> Optional[str]:
        """Smart API key detection from environment variables."""
        provider_key_map = {
            "openai": ["OPENAI_API_KEY", "BROWSE_TO_TEST_AI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
            "azure": ["AZURE_OPENAI_API_KEY"],
            "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
        }
        
        for key_name in provider_key_map.get(self.ai_provider, []):
            if key_name in os.environ:
                return os.environ[key_name]
        
        return None
    
    def _get_default_model(self) -> str:
        """Get default model for AI provider."""
        default_models = {
            "openai": "gpt-4.1-mini",
            "anthropic": "claude-3-sonnet-20240229",
            "azure": "gpt-4",
            "google": "gemini-pro"
        }
        return default_models.get(self.ai_provider, "gpt-4.1-mini")
    
    def _validate(self):
        """Validate configuration settings."""
        # Enhanced language validation with better error messages
        if self.language and self.language not in self._language_metadata:
            available = list(self._language_metadata.keys())
            # For backward compatibility, allow common languages not yet implemented
            common_languages = ['java', 'csharp', 'ruby', 'go']
            if self.language not in common_languages:
                # Create helpful error message with suggestions
                error_msg = f"Unsupported language '{self.language}'. Available: {available}"
                
                # Add framework-specific suggestions if available
                try:
                    from ..output_langs.registry import LanguageRegistry
                    registry = LanguageRegistry()
                    
                    # Check if the language is supported but framework combination is invalid
                    if registry.is_language_supported(self.language):
                        frameworks_for_lang = registry.get_frameworks_for_language(self.language)
                        if self.framework not in frameworks_for_lang:
                            error_msg += f". Note: '{self.language}' is supported but not with framework '{self.framework}'. Supported frameworks for {self.language}: {frameworks_for_lang}"
                    else:
                        # Suggest alternatives based on framework
                        langs_for_framework = registry.get_languages_for_framework(self.framework)
                        if langs_for_framework:
                            error_msg += f". For framework '{self.framework}', try: {langs_for_framework}"
                            
                except ImportError:
                    pass  # Registry not available, use basic error
                    
                raise ValueError(error_msg)
        
        # Validate framework-language combination more thoroughly
        if self.language in self._language_metadata and self.framework:
            try:
                from ..output_langs.registry import LanguageRegistry
                registry = LanguageRegistry()
                
                # Check if combination is valid
                if not registry.is_combination_supported(self.language, self.framework):
                    frameworks_for_lang = registry.get_frameworks_for_language(self.language)
                    raise ValueError(
                        f"Framework '{self.framework}' is not supported for language '{self.language}'. "
                        f"Supported frameworks for {self.language}: {frameworks_for_lang}"
                    )
            except ImportError:
                pass  # Registry not available, skip detailed validation
        
        # Validate timeout
        if self.test_timeout <= 0:
            raise ValueError("test_timeout must be positive")
        
        # Validate AI settings
        if self.ai_temperature < 0 or self.ai_temperature > 2:
            raise ValueError("AI temperature must be between 0 and 2")
        
        if self.ai_max_tokens <= 0:
            raise ValueError("ai_max_tokens must be positive")
    
    @classmethod
    def from_preset(cls, preset: ConfigPreset) -> 'Config':
        """Create configuration from preset."""
        if preset == ConfigPreset.FAST:
            return cls(
                enable_context_collection=False,
                enable_ai_analysis=False,
                ai_temperature=0.3,
                ai_max_tokens=2000,
                include_error_handling=False,
                add_comments=False
            )
        elif preset == ConfigPreset.BALANCED:
            return cls()  # Default settings are balanced
        elif preset == ConfigPreset.ACCURATE:
            return cls(
                enable_context_collection=True,
                enable_ai_analysis=True,
                enable_final_script_analysis=True,
                ai_temperature=0.05,
                ai_max_tokens=6000,
                ai_retry_attempts=5
            )
        elif preset == ConfigPreset.PRODUCTION:
            return cls(
                include_error_handling=True,
                include_logging=True,
                strict_mode=True,
                mask_sensitive_data=True,
                ai_retry_attempts=5,
                test_timeout=60000
            )
        else:
            raise ValueError(f"Unknown preset: {preset}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        if not data:
            return cls()
            
        # Handle backward compatibility for 'provider' parameter
        data = data.copy()  # Don't modify the original
        flattened = {}
        
        # Handle nested structure from old tests
        if 'ai' in data:
            ai_data = data['ai']
            if 'provider' in ai_data:
                flattened['ai_provider'] = ai_data['provider']
            if 'model' in ai_data:
                flattened['ai_model'] = ai_data['model']
            if 'api_key' in ai_data:
                flattened['api_key'] = ai_data['api_key']
            if 'temperature' in ai_data:
                flattened['ai_temperature'] = ai_data['temperature']
            if 'max_tokens' in ai_data:
                flattened['ai_max_tokens'] = ai_data['max_tokens']
        
        if 'output' in data:
            output_data = data['output']
            if 'framework' in output_data:
                flattened['framework'] = output_data['framework']
            if 'language' in output_data:
                flattened['language'] = output_data['language']
            if 'include_assertions' in output_data:
                flattened['include_assertions'] = output_data['include_assertions']
            if 'include_error_handling' in output_data:
                flattened['include_error_handling'] = output_data['include_error_handling']
            if 'include_logging' in output_data:
                flattened['include_logging'] = output_data['include_logging']
            if 'test_timeout' in output_data:
                flattened['test_timeout'] = output_data['test_timeout']
            if 'sensitive_data_keys' in output_data:
                flattened['sensitive_data_keys'] = output_data['sensitive_data_keys']
        
        if 'processing' in data:
            processing_data = data['processing']
            if 'collect_system_context' in processing_data:
                flattened['enable_context_collection'] = processing_data['collect_system_context']
            if 'analyze_actions_with_ai' in processing_data:
                flattened['enable_ai_analysis'] = processing_data['analyze_actions_with_ai']
            if 'enable_context_collection' in processing_data:
                flattened['enable_context_collection'] = processing_data['enable_context_collection']
            if 'enable_ai_analysis' in processing_data:
                flattened['enable_ai_analysis'] = processing_data['enable_ai_analysis']
            if 'context_analysis_depth' in processing_data:
                flattened['context_analysis_depth'] = processing_data['context_analysis_depth']
            if 'max_similar_tests' in processing_data:
                flattened['max_similar_tests'] = processing_data['max_similar_tests']
            if 'scan_test_directories' in processing_data:
                flattened['_scan_test_directories'] = processing_data['scan_test_directories']
        
        # Handle top-level keys
        for key, value in data.items():
            if key not in ['ai', 'output', 'processing']:
                # Handle common aliases
                if key == 'provider':
                    flattened['ai_provider'] = value
                elif key == 'model':
                    flattened['ai_model'] = value
                elif key == 'timeout':
                    flattened['test_timeout'] = value
                elif key == 'context_collection':
                    flattened['enable_context_collection'] = value
                else:
                    flattened[key] = value
        
        # Handle property-backed fields specially
        property_fields = {}
        property_field_names = {'debug', 'verbose', 'log_level', 'project_root'}
        for prop_name in property_field_names:
            if prop_name in flattened:
                property_fields[prop_name] = flattened.pop(prop_name)
        
        # Handle special private fields that aren't dataclass fields
        private_fields = {}
        private_field_names = {'_scan_test_directories', '_include_existing_tests', '_max_context_files', '_include_documentation', '_max_context_prompt_size'}
        for private_name in private_field_names:
            if private_name in flattened:
                private_fields[private_name] = flattened.pop(private_name)
        
        # Handle project_root specially since it's a property, not a dataclass field
        project_root_value = flattened.pop('_project_root_value', None)
        if project_root_value is not None:
            property_fields['project_root'] = project_root_value
        
        # Filter out unknown keys to avoid errors
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in flattened.items() if k in valid_fields}
        
        config = cls(**filtered_data)
        
        # Set property-backed fields after initialization
        for prop_name, prop_value in property_fields.items():
            setattr(config, prop_name, prop_value)
        
        # Set private fields after initialization
        for private_name, private_value in private_fields.items():
            setattr(config, private_name, private_value)
        
        return config
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Config':
        """Load configuration from file (JSON or YAML)."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Validate file extension
        supported_extensions = ['.json', '.yml', '.yaml']
        if file_path.suffix.lower() not in supported_extensions:
            raise ValueError(f"Unsupported config file format. Supported extensions: {', '.join(supported_extensions)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yml', '.yaml']:
                    if yaml is None:
                        raise ImportError("PyYAML required for YAML configuration files")
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        except json.JSONDecodeError:
            # Let JSON decode errors pass through for test compatibility
            raise
        
        return cls.from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format with backward compatibility."""
        # Create nested structure for backward compatibility
        result = {
            'ai': {
                'provider': self.ai_provider,
                'model': self.ai_model,
                'api_key': self.api_key,
                'temperature': self.ai_temperature,
                'max_tokens': self.ai_max_tokens,
                'timeout': self.ai_timeout,
                'retry_attempts': self.ai_retry_attempts,
                'base_url': self.ai_base_url,
                'extra_params': self.ai_extra_params
            },
            'output': {
                'framework': self.framework,
                'language': self.language,
                'include_assertions': self.include_assertions,
                'include_error_handling': self.include_error_handling,
                'include_waits': self.include_waits,
                'include_logging': self.include_logging,
                'include_screenshots': self.include_screenshots,
                'add_comments': self.add_comments,
                'test_timeout': self.test_timeout,
                'test_type': self.test_type,
                'browser_options': self.browser_options,
                'sensitive_data_keys': self.sensitive_data_keys
            },
            'processing': {
                'enable_context_collection': self.enable_context_collection,
                'enable_ai_analysis': self.enable_ai_analysis,
                'mask_sensitive_data': self.mask_sensitive_data,
                'strict_mode': self.strict_mode,
                'enable_final_script_analysis': self.enable_final_script_analysis,
                'context_analysis_depth': self.context_analysis_depth,
                'max_similar_tests': self.max_similar_tests,
                'scan_test_directories': getattr(self, '_scan_test_directories', [])
            }
        }
        
        # Add top-level properties
        if hasattr(self, '_debug'):
            result['debug'] = self._debug
        if hasattr(self, '_verbose'):
            result['verbose'] = self._verbose
        if hasattr(self, '_log_level'):
            result['log_level'] = self._log_level
        if hasattr(self, '_project_root') and self._project_root:
            result['project_root'] = self._project_root
            
        return result
    
    def to_file(self, file_path: Union[str, Path], format: str = "json"):
        """Save configuration to file."""
        file_path = Path(file_path)
        data = self.to_dict()
        
        # Auto-detect format from file extension if not specified explicitly
        if format == "json":  # Default format, check if we should auto-detect
            extension = file_path.suffix.lower()
            if extension in ['.yml', '.yaml']:
                format = 'yaml'
            elif extension == '.json':
                format = 'json'
            elif extension and extension not in ['.json', '.yml', '.yaml']:
                # Unsupported file extension
                raise ValueError(f"Unsupported config file format: {extension}")
        
        # Validate format
        valid_formats = ["json", "yaml", "yml"]
        if format.lower() not in valid_formats:
            raise ValueError(f"Unsupported format '{format}'. Use one of: {valid_formats}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() in ["yaml", "yml"]:
                if yaml is None:
                    raise ImportError("PyYAML required for YAML output")
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)
    
    def get_language_metadata(self) -> Dict[str, str]:
        """Get metadata for current language."""
        return self._language_metadata.get(self.language, {})
    
    @staticmethod
    def detect_language_from_filename(filename: str) -> str:
        """
        Auto-detect language from file extension.
        
        Args:
            filename: Output filename with extension
            
        Returns:
            Detected language string
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.py'):
            return 'python'
        elif filename_lower.endswith('.ts'):
            return 'typescript' 
        elif filename_lower.endswith('.js'):
            return 'javascript'
        elif filename_lower.endswith('.java'):
            return 'java'
        elif filename_lower.endswith('.cs'):
            return 'csharp'
        else:
            return 'python'  # Default fallback
    
    @staticmethod
    def get_optimal_framework_for_language(language: str) -> str:
        """
        Get the recommended framework for a language.
        
        Args:
            language: Programming language
            
        Returns:
            Recommended framework
        """
        try:
            from ..output_langs.registry import LanguageRegistry
            registry = LanguageRegistry()
            
            frameworks = registry.get_frameworks_for_language(language)
            
            # Prefer playwright if available
            if 'playwright' in frameworks:
                return 'playwright'
            elif 'selenium' in frameworks:
                return 'selenium'
            elif frameworks:
                return frameworks[0]  # Return first available
            else:
                return 'playwright'  # Safe default
                
        except Exception:
            return 'playwright'  # Safe default
    
    def validate_and_suggest_alternatives(self) -> tuple:
        """
        Validate current configuration and suggest alternatives if invalid.
        
        Returns:
            (is_valid: bool, message: str, suggestions: dict)
        """
        try:
            self._validate()
            return (True, f"✓ Configuration is valid: {self.language} + {self.framework}", {})
        except ValueError as e:
            suggestions = {}
            
            try:
                from ..output_langs.registry import LanguageRegistry
                registry = LanguageRegistry()
                
                # Suggest optimal framework for current language
                if registry.is_language_supported(self.language):
                    optimal_framework = self.get_optimal_framework_for_language(self.language)
                    suggestions['recommended_framework'] = optimal_framework
                
                # Suggest alternative languages for current framework
                langs_for_framework = registry.get_languages_for_framework(self.framework)
                if langs_for_framework:
                    suggestions['alternative_languages'] = langs_for_framework
                    
            except ImportError:
                pass
                
            return (False, str(e), suggestions)
    
    # Backward compatibility properties for old tests
    @property
    def processing(self):
        """Backward compatibility for config.processing access."""
        return self
    
    @processing.setter
    def processing(self, value):
        """Backward compatibility setter for config.processing."""
        # Just ignore the setter - the unified config handles everything
        pass
    
    @property
    def analyze_actions_with_ai(self) -> bool:
        """Backward compatibility for AI analysis setting."""
        return self.enable_ai_analysis
    
    @analyze_actions_with_ai.setter
    def analyze_actions_with_ai(self, value: bool):
        """Backward compatibility setter."""
        self.enable_ai_analysis = value
    
    @property
    def ai_api_key(self) -> Optional[str]:
        """Backward compatibility for API key."""
        return self.api_key
    
    @property
    def ai_max_retries(self) -> int:
        """Backward compatibility for max retries."""
        return self.ai_retry_attempts
    
    @property
    def ai(self):
        """Backward compatibility for config.ai access."""
        return self
    
    @property
    def framework_config(self):
        """Backward compatibility for framework config."""
        return {}
    
    @property
    def shared_setup(self):
        """Backward compatibility for shared setup config."""
        return None
    
    # Additional backward compatibility properties for tests
    @property
    def output(self):
        """Backward compatibility for config.output access."""
        class OutputProxy(OutputConfig):
            def __init__(self, config):
                self._config = config
                # Initialize attributes directly to avoid conflicts with properties
                self._framework = config.framework
                self._language = config.language
                self._include_assertions = config.include_assertions
                self._include_error_handling = config.include_error_handling
                self._include_logging = config.include_logging
                self._include_waits = config.include_waits
                self._include_screenshots = config.include_screenshots
                self._test_timeout = config.test_timeout
                self._add_comments = config.add_comments
                self._mask_sensitive_data = config.mask_sensitive_data
                self._sensitive_data_keys = config.sensitive_data_keys
                self._test_type = config.test_type
                self._browser_options = config.browser_options
            
            @property
            def framework(self):
                return self._config.framework
            
            @framework.setter
            def framework(self, value):
                self._config.framework = value
            
            @property
            def language(self):
                return self._config.language
            
            @language.setter
            def language(self, value):
                self._config.language = value
            
            @property
            def include_assertions(self):
                return self._config.include_assertions
            
            @include_assertions.setter
            def include_assertions(self, value):
                self._config.include_assertions = value
            
            @property
            def include_error_handling(self):
                return self._config.include_error_handling
            
            @include_error_handling.setter
            def include_error_handling(self, value):
                self._config.include_error_handling = value
            
            @property
            def include_logging(self):
                return self._config.include_logging
            
            @include_logging.setter
            def include_logging(self, value):
                self._config.include_logging = value
            
            @property
            def include_waits(self):
                return self._config.include_waits
            
            @include_waits.setter
            def include_waits(self, value):
                self._config.include_waits = value
            
            @property
            def test_timeout(self):
                return self._config.test_timeout
            
            @test_timeout.setter
            def test_timeout(self, value):
                self._config.test_timeout = value
            
            @property
            def sensitive_data_keys(self):
                return self._config.sensitive_data_keys
            
            @sensitive_data_keys.setter
            def sensitive_data_keys(self, value):
                self._config.sensitive_data_keys = value
            
            @property
            def mask_sensitive_data(self):
                return self._config.mask_sensitive_data
            
            @mask_sensitive_data.setter
            def mask_sensitive_data(self, value):
                self._config.mask_sensitive_data = value
            
            @property
            def browser_options(self):
                return getattr(self._config, 'browser_options', {})
            
            @browser_options.setter
            def browser_options(self, value):
                self._config.browser_options = value
        
        return OutputProxy(self)
    
    @property
    def ai(self):
        """Backward compatibility for config.ai access."""
        class AIProxy(AIConfig):
            def __init__(self, config):
                self._config = config
                # Initialize attributes directly to avoid conflicts with properties
                self._provider = config.ai_provider
                self._api_key = config.api_key
                self._model = config.ai_model or "gpt-4.1-mini"
                self._temperature = config.ai_temperature
                self._max_tokens = config.ai_max_tokens
                self._timeout = config.ai_timeout
                self._retry_attempts = config.ai_retry_attempts
                
                # Set attributes needed by AIConfig
                self.ai_provider = config.ai_provider  # Alias for compatibility
            
            @property
            def provider(self):
                return self._config.ai_provider
            
            @provider.setter
            def provider(self, value):
                self._config.ai_provider = value
            
            @property
            def model(self):
                return self._config.ai_model
            
            @model.setter
            def model(self, value):
                self._config.ai_model = value
            
            @property
            def api_key(self):
                return self._config.api_key
            
            @api_key.setter
            def api_key(self, value):
                self._config.api_key = value
            
            @property
            def temperature(self):
                return self._config.ai_temperature
            
            @temperature.setter
            def temperature(self, value):
                self._config.ai_temperature = value
            
            @property
            def max_tokens(self):
                return self._config.ai_max_tokens
            
            @max_tokens.setter
            def max_tokens(self, value):
                self._config.ai_max_tokens = value
            
            @property
            def extra_params(self):
                return self._config.ai_extra_params
            
            @extra_params.setter
            def extra_params(self, value):
                self._config.ai_extra_params = value
        
        return AIProxy(self)
    
    @property
    def processing(self):
        """Backward compatibility for config.processing access."""
        class ProcessingProxy(ProcessingConfig):
            def __init__(self, config):
                self._config = config
                # Initialize attributes directly to avoid conflicts with properties
                self._analyze_actions_with_ai = config.enable_ai_analysis
                self._collect_system_context = config.enable_context_collection
                self._use_intelligent_analysis = config.enable_ai_analysis
                self._strict_mode = config.strict_mode
            
            @property
            def collect_system_context(self):
                return self._config.enable_context_collection
            
            @collect_system_context.setter
            def collect_system_context(self, value):
                self._config.enable_context_collection = value
            
            @property
            def analyze_actions_with_ai(self):
                return self._config.enable_ai_analysis
            
            @analyze_actions_with_ai.setter
            def analyze_actions_with_ai(self, value):
                self._config.enable_ai_analysis = value
            
            @property
            def use_intelligent_analysis(self):
                # Map to enable_ai_analysis for compatibility
                return self._config.enable_ai_analysis
            
            @use_intelligent_analysis.setter
            def use_intelligent_analysis(self, value):
                self._config.enable_ai_analysis = value
            
            @property
            def context_analysis_depth(self):
                return self._config.context_analysis_depth
            
            @context_analysis_depth.setter
            def context_analysis_depth(self, value: str):
                self._config.context_analysis_depth = value
            
            @property
            def strict_mode(self):
                return self._config.strict_mode
            
            @strict_mode.setter
            def strict_mode(self, value):
                self._config.strict_mode = value
            
            @property
            def include_ui_components(self):
                # Default behavior: enabled if context collection is enabled
                return self._config.enable_context_collection
            
            @include_ui_components.setter
            def include_ui_components(self, value):
                # For now, map to context collection (could be separate in future)
                self._config.enable_context_collection = value
            
            @property
            def include_existing_tests(self):
                return getattr(self._config, '_include_existing_tests', True)
            
            @include_existing_tests.setter
            def include_existing_tests(self, value):
                self._config._include_existing_tests = value
            
            @property
            def include_documentation(self):
                return getattr(self._config, '_include_documentation', True)
            
            @include_documentation.setter
            def include_documentation(self, value):
                self._config._include_documentation = value
            
            @property
            def max_context_files(self):
                return getattr(self._config, '_max_context_files', 100)
            
            @max_context_files.setter
            def max_context_files(self, value):
                self._config._max_context_files = value
            
            @property
            def max_context_prompt_size(self):
                return getattr(self._config, '_max_context_prompt_size', 8000)
            
            @max_context_prompt_size.setter
            def max_context_prompt_size(self, value):
                self._config._max_context_prompt_size = value
            
            @property
            def enable_final_script_analysis(self):
                return self._config.enable_final_script_analysis
            
            @enable_final_script_analysis.setter
            def enable_final_script_analysis(self, value):
                self._config.enable_final_script_analysis = value
            
            @property
            def max_similar_tests(self):
                return self._config.max_similar_tests
            
            @max_similar_tests.setter
            def max_similar_tests(self, value):
                self._config.max_similar_tests = value
            
            @property
            def scan_test_directories(self):
                return getattr(self._config, '_scan_test_directories', [])
            
            @scan_test_directories.setter
            def scan_test_directories(self, value):
                self._config._scan_test_directories = value
        
        return ProcessingProxy(self)
    
    @property
    def project_root(self):
        """Project root path for compatibility."""
        return getattr(self, '_project_root', None)
    
    @project_root.setter
    def project_root(self, value):
        """Set project root path."""
        self._project_root = value
    
    @property
    def verbose(self):
        """Get verbose mode setting."""
        return getattr(self, '_verbose', False)
    
    @verbose.setter
    def verbose(self, value):
        """Set verbose mode setting."""
        self._verbose = bool(value)
    
    @property
    def log_level(self):
        """Get log level setting."""
        return getattr(self, '_log_level', 'INFO')
    
    @log_level.setter
    def log_level(self, value):
        """Set log level setting."""
        self._log_level = str(value)
    
    @property
    def debug(self):
        """Get debug mode setting."""
        return getattr(self, '_debug', False)
    
    @debug.setter
    def debug(self, value):
        """Set debug mode setting."""
        self._debug = bool(value)
    
    def validate(self):
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate temperature
        if not (0 <= self.ai_temperature <= 2):
            errors.append("AI temperature must be between 0 and 2")
        
        # Validate timeout
        if self.test_timeout < 1000:
            errors.append("Test timeout must be at least 1000ms")
        
        # Validate framework
        if not self.framework or self.framework.strip() == "":
            errors.append("Output framework cannot be empty")
        
        # Validate language
        if not self.language or self.language.strip() == "":
            errors.append("Output language cannot be empty")
        
        # Validate provider
        if not self.ai_provider or self.ai_provider.strip() == "":
            errors.append("AI provider cannot be empty")
        
        # Validate AI model
        if hasattr(self, 'ai_model') and self.ai_model is not None and self.ai_model.strip() == "":
            errors.append("AI model cannot be empty")
        
        # Validate AI max tokens
        if self.ai_max_tokens <= 0:
            errors.append("AI max_tokens must be positive")
        
        # Check if we have sub-configs and validate them
        if hasattr(self, 'ai') and hasattr(self.ai, 'provider'):
            if not self.ai.provider or self.ai.provider.strip() == "":
                errors.append("AI provider cannot be empty")
            if not self.ai.model or self.ai.model.strip() == "":
                errors.append("AI model cannot be empty")
            if not (0 <= self.ai.temperature <= 2):
                errors.append("AI temperature must be between 0 and 2")
            if self.ai.max_tokens <= 0:
                errors.append("AI max_tokens must be positive")
        
        if hasattr(self, 'output') and hasattr(self.output, 'framework'):
            if not self.output.framework or self.output.framework.strip() == "":
                errors.append("Output framework cannot be empty")
            if not self.output.language or self.output.language.strip() == "":
                errors.append("Output language cannot be empty")
        
        if hasattr(self, 'processing') and hasattr(self.processing, 'max_cache_size'):
            if self.processing.max_cache_size < 0:
                errors.append("Processing max_cache_size must be non-negative")
            if hasattr(self.processing, 'context_similarity_threshold'):
                if not (0 <= self.processing.context_similarity_threshold <= 1):
                    errors.append("Processing context_similarity_threshold must be between 0 and 1")
        
        return errors
    
    def optimize_for_speed(self):
        """Optimize configuration for speed."""
        self.enable_context_collection = False
        self.enable_ai_analysis = False
        self.ai_temperature = 0.3
        self.ai_max_tokens = 2000
        self.include_error_handling = False
        self.add_comments = False
        # Set ProcessingProxy-specific attributes
        self._include_existing_tests = False
        self._include_documentation = False
        self._max_context_files = 20
        return self
    
    def optimize_for_accuracy(self):
        """Optimize configuration for accuracy."""
        self.enable_context_collection = True
        self.enable_ai_analysis = True
        self.enable_final_script_analysis = True
        self.ai_temperature = 0.05
        self.ai_max_tokens = 8000
        self.ai_retry_attempts = 5
        self.context_analysis_depth = "deep"
        # Set ProcessingProxy-specific attributes
        self._include_existing_tests = True
        self._include_documentation = True
        self._max_context_files = 200
        self._max_context_prompt_size = 12000
        return self
    
    def save_to_file(self, file_path: str, format: str = "json"):
        """Save configuration to file."""
        return self.to_file(file_path, format)
    
    def get_ai_analysis_config(self):
        """Get AI analysis configuration."""
        return {
            'enabled': self.enable_ai_analysis,
            'provider': self.ai_provider,
            'model': self.ai_model,
            'temperature': self.ai_temperature,
            'max_tokens': self.ai_max_tokens,
            'use_intelligent_analysis': self.enable_ai_analysis,
            'context_analysis_depth': self.context_analysis_depth,
            'max_similar_tests': self.max_similar_tests,
            'target_framework': self.framework,
            'target_language': self.language
        }
    
    def get_context_collection_config(self):
        """Get context collection configuration."""
        return {
            'enabled': self.enable_context_collection,
            'collect_system_context': self.enable_context_collection,
            'include_existing_tests': self.processing.include_existing_tests,
            'max_context_files': self.processing.max_context_files,
            'project_root': self.project_root
        }
    
    def update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        if not data:
            return
        
        for key, value in data.items():
            if key == 'ai' and isinstance(value, dict):
                # Update AI proxy properties
                for ai_key, ai_value in value.items():
                    if hasattr(self.ai, ai_key):
                        setattr(self.ai, ai_key, ai_value)
            elif key == 'output' and isinstance(value, dict):
                # Update output proxy properties
                for output_key, output_value in value.items():
                    if hasattr(self.output, output_key):
                        setattr(self.output, output_key, output_value)
            elif key == 'processing' and isinstance(value, dict):
                # Update processing proxy properties
                for proc_key, proc_value in value.items():
                    if hasattr(self.processing, proc_key):
                        setattr(self.processing, proc_key, proc_value)
            elif key in self.__dataclass_fields__:
                setattr(self, key, value)
            elif key == 'debug':
                self.debug = value
            elif key == 'verbose':
                self.verbose = value
            elif key == 'log_level':
                self.log_level = value
            elif key == 'project_root':
                self.project_root = value
    
    def __repr__(self):
        """Return string representation of the config."""
        return f"Config(framework='{self.framework}', language='{self.language}', ai_provider='{self.ai_provider}', context={self.enable_context_collection})"
    
    @classmethod
    def from_env(cls, prefix: str = "BROWSE_TO_TEST_"):
        """Create configuration from environment variables."""
        import os
        
        # Initialize nested config structure
        config_data = {
            'ai': {},
            'output': {},
            'processing': {}
        }
        
        # Map environment variables to nested config structure
        env_mappings = {
            # AI configuration
            f'{prefix}AI_PROVIDER': ('ai', 'provider'),
            f'{prefix}AI_MODEL': ('ai', 'model'),
            f'{prefix}AI_API_KEY': ('ai', 'api_key'),
            f'{prefix}AI_TEMPERATURE': ('ai', 'temperature'),
            f'{prefix}AI_MAX_TOKENS': ('ai', 'max_tokens'),
            f'{prefix}AI_TIMEOUT': ('ai', 'timeout'),
            f'{prefix}AI_RETRY_ATTEMPTS': ('ai', 'retry_attempts'),
            
            # Output configuration
            f'{prefix}OUTPUT_FRAMEWORK': ('output', 'framework'),
            f'{prefix}OUTPUT_LANGUAGE': ('output', 'language'),
            f'{prefix}OUTPUT_INCLUDE_ASSERTIONS': ('output', 'include_assertions'),
            f'{prefix}OUTPUT_INCLUDE_ERROR_HANDLING': ('output', 'include_error_handling'),
            f'{prefix}OUTPUT_USE_PAGE_OBJECT_MODEL': ('output', 'use_page_object_model'),
            f'{prefix}OUTPUT_ADD_COMMENTS': ('output', 'add_comments'),
            f'{prefix}OUTPUT_MASK_SENSITIVE_DATA': ('output', 'mask_sensitive_data'),
            
            # Processing configuration
            f'{prefix}PROCESSING_ANALYZE_WITH_AI': ('processing', 'analyze_actions_with_ai'),
            f'{prefix}PROCESSING_COLLECT_CONTEXT': ('processing', 'collect_system_context'),
            f'{prefix}PROCESSING_USE_INTELLIGENT_ANALYSIS': ('processing', 'use_intelligent_analysis'),
            f'{prefix}PROCESSING_INCLUDE_EXISTING_TESTS': ('processing', 'include_existing_tests'),
            f'{prefix}PROCESSING_INCLUDE_DOCUMENTATION': ('processing', 'include_documentation'),
            f'{prefix}PROCESSING_CONTEXT_ANALYSIS_DEPTH': ('processing', 'context_analysis_depth'),
            f'{prefix}PROCESSING_STRICT_MODE': ('processing', 'strict_mode'),
            
            # Top-level configuration
            f'{prefix}DEBUG': ('debug',),
            f'{prefix}VERBOSE': ('verbose',),
            f'{prefix}LOG_LEVEL': ('log_level',),
            f'{prefix}PROJECT_ROOT': ('project_root',),
        }
        
        for env_key, path in env_mappings.items():
            if env_key in os.environ:
                value = os.environ[env_key]
                
                # Convert string values to appropriate types
                if any(key in env_key.lower() for key in ['temperature']):
                    value = float(value)
                elif any(key in env_key.lower() for key in ['max_tokens', 'timeout', 'retry_attempts']):
                    value = int(value)
                elif any(key in env_key.lower() for key in ['debug', 'verbose', 'assertions', 'error_handling', 'page_object', 'comments', 'mask_sensitive', 'analyze_with_ai', 'analyze', 'collect', 'intelligent', 'existing', 'documentation', 'strict']):
                    value = value.lower() in ('true', '1', 'yes')
                
                # Set value in nested structure
                if len(path) == 1:
                    config_data[path[0]] = value
                elif len(path) == 2:
                    config_data[path[0]][path[1]] = value
        
        # Use from_dict to handle the nested structure properly
        return cls.from_dict(config_data)


class ConfigBuilder:
    """
    Fluent builder for Config objects.
    
    Provides a clean, chainable interface for building configurations.
    
    Example:
        >>> config = ConfigBuilder() \\
        ...     .framework("playwright") \\
        ...     .ai_provider("openai", model="gpt-4") \\
        ...     .language("python") \\
        ...     .include_assertions(True) \\
        ...     .build()
    """
    
    def __init__(self):
        self._data = {}
        # Create a default config for compatibility
        self._config = Config()
    
    def framework(self, framework: str) -> 'ConfigBuilder':
        """Set target framework."""
        self._data['framework'] = framework
        return self
    
    def language(self, language: str) -> 'ConfigBuilder':
        """Set target language."""
        self._data['language'] = language
        return self
    
    def auto_detect_language(self, output_filename: str) -> 'ConfigBuilder':
        """Auto-detect language from output filename extension."""
        detected_language = Config.detect_language_from_filename(output_filename)
        self._data['language'] = detected_language
        return self
    
    def optimize_for_language(self, language: str) -> 'ConfigBuilder':
        """Set language and auto-select optimal framework for it."""
        optimal_framework = Config.get_optimal_framework_for_language(language)
        self._data['language'] = language
        self._data['framework'] = optimal_framework
        return self
    
    def ai_provider(self, provider: str, model: Optional[str] = None, 
                   api_key: Optional[str] = None, **kwargs) -> 'ConfigBuilder':
        """Set AI provider and related settings."""
        self._data['ai_provider'] = provider
        if model:
            self._data['ai_model'] = model
        if api_key:
            self._data['api_key'] = api_key
        if kwargs:
            self._data['ai_extra_params'] = kwargs
        return self
    
    def include_assertions(self, include: bool = True) -> 'ConfigBuilder':
        """Enable/disable assertions in output."""
        self._data['include_assertions'] = include
        return self
    
    def include_error_handling(self, include: bool = True) -> 'ConfigBuilder':
        """Enable/disable error handling in output."""
        self._data['include_error_handling'] = include
        return self
    
    def include_logging(self, include: bool = True) -> 'ConfigBuilder':
        """Enable/disable logging in output."""
        self._data['include_logging'] = include
        return self
    
    def test_timeout(self, timeout: int) -> 'ConfigBuilder':
        """Set test timeout in milliseconds."""
        self._data['test_timeout'] = timeout
        return self
    
    def sensitive_data_keys(self, keys: List[str]) -> 'ConfigBuilder':
        """Set sensitive data keys for masking."""
        self._data['sensitive_data_keys'] = keys
        return self
    
    def strict_mode(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable/disable strict validation mode."""
        self._data['strict_mode'] = enabled
        return self
    
    def enable_final_script_analysis(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable/disable final script analysis."""
        self._data['enable_final_script_analysis'] = enabled
        return self
    
    def debug(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable/disable debug mode."""
        self._data['debug'] = enabled
        return self
    
    def enable_ai_analysis(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable/disable AI analysis (backward compatibility)."""
        self._data['enable_ai_analysis'] = enabled
        return self
    
    def include_waits(self, include: bool = True) -> 'ConfigBuilder':
        """Enable/disable waits in output."""
        self._data['include_waits'] = include
        return self
    
    def enable_context_collection(self, enabled: bool = True) -> 'ConfigBuilder':
        """Enable/disable context collection (backward compatibility)."""
        self._data['enable_context_collection'] = enabled
        return self
    
    def from_preset(self, preset: ConfigPreset) -> 'ConfigBuilder':
        """Start from a preset configuration."""
        config = Config.from_preset(preset)
        self._data = config.to_dict()
        return self
    
    def from_kwargs(self, **kwargs) -> 'ConfigBuilder':
        """Load settings from keyword arguments."""
        # Handle backward compatibility mappings
        kwargs_copy = kwargs.copy()
        if 'context_collection' in kwargs_copy:
            kwargs_copy['enable_context_collection'] = kwargs_copy.pop('context_collection')
        if 'timeout' in kwargs_copy:
            kwargs_copy['test_timeout'] = kwargs_copy.pop('timeout')
        if 'temperature' in kwargs_copy:
            kwargs_copy['ai_temperature'] = kwargs_copy.pop('temperature')
        if 'model' in kwargs_copy:
            kwargs_copy['ai_model'] = kwargs_copy.pop('model')
        if 'project_root' in kwargs_copy:
            kwargs_copy['_project_root_value'] = kwargs_copy.pop('project_root')
        self._data.update(kwargs_copy)
        return self
    
    def from_file(self, file_path: Union[str, Path]) -> 'ConfigBuilder':
        """Load settings from file."""
        config = Config.from_file(file_path)
        self._data = config.to_dict()
        return self
    
    def temperature(self, temp: float) -> 'ConfigBuilder':
        """Set AI temperature."""
        self._data['ai_temperature'] = temp
        return self
    
    def fast_mode(self) -> 'ConfigBuilder':
        """Configure for fast mode (speed optimized)."""
        self._data.update({
            'enable_context_collection': False,
            'enable_ai_analysis': False,
            'ai_temperature': 0.3,
            'ai_max_tokens': 2000,
            'include_error_handling': False,
            'add_comments': False
        })
        return self
    
    def thorough_mode(self) -> 'ConfigBuilder':
        """Configure for thorough mode (accuracy optimized)."""
        self._data.update({
            'enable_context_collection': True,
            'enable_ai_analysis': True,
            'enable_final_script_analysis': True,
            'ai_temperature': 0.05,
            'ai_max_tokens': 8000,
            'ai_retry_attempts': 5
        })
        return self
    
    def project_root(self, root_path: str) -> 'ConfigBuilder':
        """Set project root path."""
        self._data['_project_root_value'] = root_path
        return self
    
    def timeout(self, timeout_ms: int) -> 'ConfigBuilder':
        """Set test timeout in milliseconds."""
        self._data['test_timeout'] = timeout_ms
        return self
    
    def from_dict(self, data: Dict[str, Any]) -> 'ConfigBuilder':
        """Load settings from dictionary with nested structure support."""
        if data is None:
            return self
            
        flattened = {}
        
        # Handle nested structure from old tests
        if 'ai' in data:
            ai_data = data['ai']
            if 'provider' in ai_data:
                flattened['ai_provider'] = ai_data['provider']
            if 'model' in ai_data:
                flattened['ai_model'] = ai_data['model']
            if 'api_key' in ai_data:
                flattened['api_key'] = ai_data['api_key']
            if 'temperature' in ai_data:
                flattened['ai_temperature'] = ai_data['temperature']
            if 'max_tokens' in ai_data:
                flattened['ai_max_tokens'] = ai_data['max_tokens']
        
        if 'output' in data:
            output_data = data['output']
            if 'framework' in output_data:
                flattened['framework'] = output_data['framework']
            if 'language' in output_data:
                flattened['language'] = output_data['language']
            if 'include_assertions' in output_data:
                flattened['include_assertions'] = output_data['include_assertions']
            if 'include_error_handling' in output_data:
                flattened['include_error_handling'] = output_data['include_error_handling']
            if 'include_logging' in output_data:
                flattened['include_logging'] = output_data['include_logging']
            if 'test_timeout' in output_data:
                flattened['test_timeout'] = output_data['test_timeout']
            if 'sensitive_data_keys' in output_data:
                flattened['sensitive_data_keys'] = output_data['sensitive_data_keys']
        
        if 'processing' in data:
            processing_data = data['processing']
            if 'collect_system_context' in processing_data:
                flattened['enable_context_collection'] = processing_data['collect_system_context']
            if 'analyze_actions_with_ai' in processing_data:
                flattened['enable_ai_analysis'] = processing_data['analyze_actions_with_ai']
            if 'enable_context_collection' in processing_data:
                flattened['enable_context_collection'] = processing_data['enable_context_collection']
            if 'enable_ai_analysis' in processing_data:
                flattened['enable_ai_analysis'] = processing_data['enable_ai_analysis']
            if 'context_analysis_depth' in processing_data:
                flattened['context_analysis_depth'] = processing_data['context_analysis_depth']
            if 'max_similar_tests' in processing_data:
                flattened['max_similar_tests'] = processing_data['max_similar_tests']
            if 'scan_test_directories' in processing_data:
                flattened['_scan_test_directories'] = processing_data['scan_test_directories']
        
        # Handle top-level keys
        for key, value in data.items():
            if key not in ['ai', 'output', 'processing']:
                flattened[key] = value
        
        self._data.update(flattened)
        return self
    
    def build(self) -> Config:
        """Build the final Config object."""
        config = Config.from_dict(self._data)
        
        # Add compatibility validation if expected by tests
        if hasattr(config, 'validate'):
            errors = config.validate()
            if errors:
                raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return config


# The backward compatibility classes are defined at the end of the file

# Import utilities for backward compatibility
try:
    from .utils.comment_manager import CommentManager, CommentStyle
    from .utils.language_templates import LanguageTemplateManager, LanguageTemplate
except ImportError:
    # Fallback to old location during transition
    try:
        from ..core.configuration.comment_manager import CommentManager, CommentStyle
        from ..core.configuration.language_templates import LanguageTemplateManager, LanguageTemplate
    except ImportError:
        # Final fallback - create dummy classes
        class CommentManager:
            def __init__(self, language="python"):
                self.language = language
        
        class CommentStyle:
            pass
            
        class LanguageTemplateManager:
            def __init__(self):
                pass
        
        class LanguageTemplate:
            pass


class AIConfig:
    """Configuration for AI providers used in tests."""
    
    def __init__(self, provider: str = "openai", api_key: str = None, model: str = "gpt-4.1-mini", 
                 temperature: float = 0.1, max_tokens: int = 4000, timeout: int = 30, 
                 retry_attempts: int = 3, **kwargs):
        """Initialize AI configuration."""
        self.provider = provider
        self.ai_provider = provider  # Alias for compatibility
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        # Store any additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)


class OutputConfig:
    """Configuration for output generation."""
    
    def __init__(self, framework: str = "playwright", language: str = "python",
                 include_assertions: bool = True, include_error_handling: bool = True,
                 include_logging: bool = False, include_waits: bool = True,
                 include_screenshots: bool = False, test_timeout: int = 30000, 
                 add_comments: bool = True, mask_sensitive_data: bool = True, 
                 sensitive_data_keys: List[str] = None, test_type: str = "script", 
                 framework_config: Dict[str, Any] = None, browser_options: Dict[str, Any] = None, **kwargs):
        """Initialize output configuration."""
        self.framework = framework
        self.language = language
        self.include_assertions = include_assertions
        self.include_error_handling = include_error_handling
        self.include_logging = include_logging
        self.include_waits = include_waits
        self.include_screenshots = include_screenshots
        self.test_timeout = test_timeout
        self.test_type = test_type
        self.add_comments = add_comments
        self.mask_sensitive_data = mask_sensitive_data
        self.framework_config = framework_config or {}
        self.browser_options = browser_options or {}
        # Handle sensitive_data_keys - default to empty list for OutputConfig
        # This matches the test expectations
        self.sensitive_data_keys = sensitive_data_keys if sensitive_data_keys is not None else []
        # Store any additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)


class ProcessingConfig:
    """Configuration for processing options."""
    
    def __init__(self, analyze_actions_with_ai: bool = True, collect_system_context: bool = True,
                 use_intelligent_analysis: bool = True, include_existing_tests: bool = True,
                 context_analysis_depth: str = "deep", optimize_selectors: bool = True,
                 validate_actions: bool = True, strict_mode: bool = False,
                 cache_ai_responses: bool = True, max_cache_size: int = 1000,
                 context_cache_ttl: int = 3600, max_context_files: int = 100,
                 include_documentation: bool = True, include_ui_components: bool = True,
                 include_api_endpoints: bool = True, include_database_schema: bool = False,
                 include_recent_changes: bool = True, context_similarity_threshold: float = 0.3,
                 max_similar_tests: int = 5, scan_test_directories: List[str] = None, **kwargs):
        """Initialize processing configuration."""
        self.analyze_actions_with_ai = analyze_actions_with_ai
        self.collect_system_context = collect_system_context
        self.use_intelligent_analysis = use_intelligent_analysis
        self.include_existing_tests = include_existing_tests
        self.context_analysis_depth = context_analysis_depth
        self.optimize_selectors = optimize_selectors
        self.validate_actions = validate_actions
        self.strict_mode = strict_mode
        self.cache_ai_responses = cache_ai_responses
        self.max_cache_size = max_cache_size
        self.context_cache_ttl = context_cache_ttl
        self.max_context_files = max_context_files
        self.include_documentation = include_documentation
        self.include_ui_components = include_ui_components
        self.include_api_endpoints = include_api_endpoints
        self.include_database_schema = include_database_schema
        self.include_recent_changes = include_recent_changes
        self.context_similarity_threshold = context_similarity_threshold
        self.max_similar_tests = max_similar_tests
        self.scan_test_directories = scan_test_directories if scan_test_directories is not None else []
        # Store any additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)