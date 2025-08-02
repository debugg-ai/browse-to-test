#!/usr/bin/env python3
"""
Simplified configuration interface for browse-to-test library.

This module provides a streamlined developer experience with:
- Smart defaults that work out of the box
- Configuration presets for common scenarios
- Progressive disclosure of advanced options
- Reduced cognitive overhead
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from enum import Enum
from browse_to_test.core.configuration.config import Config


class ConfigPreset(Enum):
    """Pre-configured settings for common use cases."""

    FAST = "fast"           # Speed-optimized, minimal analysis
    BALANCED = "balanced"   # Good balance of speed and accuracy  
    ACCURATE = "accurate"   # Accuracy-optimized, comprehensive analysis
    PRODUCTION = "production"  # Production-ready with error handling


@dataclass
class SimpleConfig:
    """
    Simplified configuration with smart defaults.
    
    Only essential options are exposed at the top level.
    Advanced options are available through progressive disclosure.
    """

    # Core settings (80% of users only need these)
    framework: str = "playwright"
    language: str = "python" 
    ai_provider: str = "openai"
    api_key: Optional[str] = None
    
    # Common customizations (15% of users need these)
    include_assertions: bool = True
    include_error_handling: bool = True
    test_timeout_seconds: int = 30
    
    # Advanced settings (5% of users, hidden by default)
    _advanced: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Apply smart defaults and validate configuration."""
        # Auto-detect API key from environment
        if not self.api_key:
            self.api_key = self._detect_api_key()
        
        # Initialize advanced settings if not provided
        if self._advanced is None:
            self._advanced = {}
    
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
    
    def advanced(self, **kwargs) -> 'SimpleConfig':
        """
        Configure advanced options using progressive disclosure.
        
        Only expose advanced options when explicitly requested.
        
        Available advanced options:
        - ai_model: str = Auto-selected based on provider
        - ai_temperature: float = 0.1
        - max_tokens: int = 4000
        - enable_context_collection: bool = True
        - enable_ai_analysis: bool = True
        - include_logging: bool = False
        - include_screenshots: bool = False
        - mask_sensitive_data: bool = True
        - sensitive_data_keys: List[str] = []
        - debug: bool = False
        """
        if self._advanced is None:
            self._advanced = {}
        
        self._advanced.update(kwargs)
        return self
    
    def get_advanced(self, key: str, default: Any = None) -> Any:
        """Get an advanced configuration value."""
        return (self._advanced or {}).get(key, default)


class SimpleConfigBuilder:
    """
    Simplified builder with preset-based configuration.
    
    Reduces configuration complexity by 90% while maintaining full flexibility.
    """
    
    def __init__(self):
        """Initialize with smart defaults."""
        self._config = SimpleConfig()
    
    # === Preset-based Configuration (Recommended) ===
    
    def preset(self, preset: Union[ConfigPreset, str]) -> 'SimpleConfigBuilder':
        """
        Apply a configuration preset for common scenarios.
        
        Presets automatically configure dozens of options optimally:
        
        - FAST: Minimal analysis, fast generation (~5-10s)
        - BALANCED: Good balance of speed and quality (~15-30s) 
        - ACCURATE: Comprehensive analysis, highest quality (~30-60s)
        - PRODUCTION: Production-ready with full error handling
        
        Args:
            preset: ConfigPreset enum or string name
            
        Returns:
            Self for method chaining
            
        Example:
            >>> config = SimpleConfigBuilder().preset("fast").for_playwright().build()
        """
        if isinstance(preset, str):
            preset = ConfigPreset(preset)
        
        preset_configs = {
            ConfigPreset.FAST: {
                "ai_model": "gpt-3.5-turbo",
                "ai_temperature": 0.0,
                "max_tokens": 2000,
                "enable_context_collection": False,
                "enable_ai_analysis": False,
                "include_logging": False,
                "include_screenshots": False,
            },
            ConfigPreset.BALANCED: {
                "ai_model": "gpt-4",
                "ai_temperature": 0.1,
                "max_tokens": 4000,
                "enable_context_collection": True,
                "enable_ai_analysis": True,
                "include_logging": False,
                "include_screenshots": False,
            },
            ConfigPreset.ACCURATE: {
                "ai_model": "gpt-4",
                "ai_temperature": 0.05,
                "max_tokens": 8000,
                "enable_context_collection": True,
                "enable_ai_analysis": True,
                "context_analysis_depth": "deep",
                "max_context_files": 200,
                "include_logging": True,
                "include_screenshots": True,
            },
            ConfigPreset.PRODUCTION: {
                "ai_model": "gpt-4",
                "ai_temperature": 0.1,
                "max_tokens": 4000,
                "enable_context_collection": True,
                "enable_ai_analysis": True,
                "include_error_handling": True,
                "include_logging": True,
                "mask_sensitive_data": True,
                "debug": False,
            }
        }
        
        advanced_settings = preset_configs.get(preset, {})
        self._config.advanced(**advanced_settings)
        return self
    
    # === Framework-specific Shortcuts ===
    
    def for_playwright(self, language: str = "python") -> 'SimpleConfigBuilder':
        """Configure for Playwright testing."""
        self._config.framework = "playwright"
        self._config.language = language
        return self
    
    def for_selenium(self, language: str = "python") -> 'SimpleConfigBuilder':
        """Configure for Selenium testing."""  
        self._config.framework = "selenium"
        self._config.language = language
        return self
    
    def for_cypress(self) -> 'SimpleConfigBuilder':
        """Configure for Cypress testing."""
        self._config.framework = "cypress"
        self._config.language = "javascript"
        return self
    
    # === AI Provider Shortcuts ===
    
    def with_openai(self, api_key: Optional[str] = None, model: str = "gpt-4") -> 'SimpleConfigBuilder':
        """Configure OpenAI provider."""
        self._config.ai_provider = "openai"
        if api_key:
            self._config.api_key = api_key
        self._config.advanced(ai_model=model)
        return self
    
    def with_anthropic(self, api_key: Optional[str] = None) -> 'SimpleConfigBuilder':
        """Configure Anthropic (Claude) provider."""
        self._config.ai_provider = "anthropic"
        if api_key:
            self._config.api_key = api_key
        self._config.advanced(ai_model="claude-3-sonnet-20240229")
        return self
    
    def with_azure_openai(self, api_key: str, endpoint: str, model: str = "gpt-4") -> 'SimpleConfigBuilder':
        """Configure Azure OpenAI provider."""
        self._config.ai_provider = "azure"
        self._config.api_key = api_key
        self._config.advanced(ai_model=model, base_url=endpoint)
        return self
    
    # === Common Customizations ===
    
    def timeout(self, seconds: int) -> 'SimpleConfigBuilder':
        """Set test timeout in seconds."""
        self._config.test_timeout_seconds = seconds
        return self
    
    def with_assertions(self, enabled: bool = True) -> 'SimpleConfigBuilder':
        """Enable or disable test assertions."""
        self._config.include_assertions = enabled
        return self
    
    def with_error_handling(self, enabled: bool = True) -> 'SimpleConfigBuilder':
        """Enable or disable error handling code."""
        self._config.include_error_handling = enabled
        return self
    
    def sensitive_data(self, keys: List[str]) -> 'SimpleConfigBuilder':
        """Specify keys that contain sensitive data to mask."""
        self._config.advanced(
            mask_sensitive_data=True,
            sensitive_data_keys=keys
        )
        return self
    
    # === Progressive Disclosure for Advanced Users ===
    
    def advanced_ai(self, temperature: float = None, max_tokens: int = None, 
                    model: str = None) -> 'SimpleConfigBuilder':
        """Configure advanced AI settings."""
        advanced_settings = {}
        if temperature is not None:
            advanced_settings["ai_temperature"] = temperature
        if max_tokens is not None:
            advanced_settings["max_tokens"] = max_tokens  
        if model is not None:
            advanced_settings["ai_model"] = model
        
        self._config.advanced(**advanced_settings)
        return self
    
    def advanced_analysis(self, context_collection: bool = None,
                          ai_analysis: bool = None, 
                          analysis_depth: str = None) -> 'SimpleConfigBuilder':
        """Configure advanced analysis settings."""
        advanced_settings = {}
        if context_collection is not None:
            advanced_settings["enable_context_collection"] = context_collection
        if ai_analysis is not None:
            advanced_settings["enable_ai_analysis"] = ai_analysis
        if analysis_depth is not None:
            advanced_settings["context_analysis_depth"] = analysis_depth
        
        self._config.advanced(**advanced_settings)
        return self
    
    def debug(self, enabled: bool = True) -> 'SimpleConfigBuilder':
        """Enable debug mode."""
        self._config.advanced(debug=enabled)
        return self
    
    def build(self) -> SimpleConfig:
        """Build the final configuration."""
        # Validate essential settings
        if not self._config.api_key:
            raise ValueError(
                f"API key required for {self._config.ai_provider}. "
                f"Set environment variable or provide via with_{self._config.ai_provider}() method."
            )
        
        return self._config
    
    # === Migration Helper ===
    
    def from_legacy_config(self, legacy_config: 'Config') -> 'SimpleConfigBuilder':
        """
        Migrate from the old complex configuration system.
        
        Automatically maps complex settings to simplified equivalents.
        """
        # Map core settings
        self._config.framework = legacy_config.output.framework
        self._config.language = legacy_config.output.language
        self._config.ai_provider = legacy_config.ai.provider
        self._config.api_key = legacy_config.ai.api_key
        self._config.include_assertions = legacy_config.output.include_assertions
        self._config.include_error_handling = legacy_config.output.include_error_handling
        self._config.test_timeout_seconds = legacy_config.output.test_timeout // 1000
        
        # Map advanced settings
        advanced_mapping = {
            "ai_model": legacy_config.ai.model,
            "ai_temperature": legacy_config.ai.temperature,
            "max_tokens": legacy_config.ai.max_tokens,
            "enable_context_collection": legacy_config.processing.collect_system_context,
            "enable_ai_analysis": legacy_config.processing.analyze_actions_with_ai,
            "include_logging": legacy_config.output.include_logging,
            "include_screenshots": legacy_config.output.include_screenshots,
            "mask_sensitive_data": legacy_config.output.mask_sensitive_data,
            "sensitive_data_keys": legacy_config.output.sensitive_data_keys,
            "debug": legacy_config.debug,
        }
        
        self._config.advanced(**advanced_mapping)
        return self


def migrate_legacy_config(legacy_config: 'Config') -> SimpleConfig:
    """
    Migrate from legacy configuration to SimpleConfig.
    
    Args:
        legacy_config: Old Config object
        
    Returns:
        New SimpleConfig with equivalent settings
    """
    return SimpleConfigBuilder().from_legacy_config(legacy_config).build()


# === Preset Factory Functions ===

def fast_config(framework: str = "playwright", language: str = "python", 
                ai_provider: str = "openai") -> SimpleConfig:
    """Create a fast configuration preset."""
    return (SimpleConfigBuilder()
            .preset(ConfigPreset.FAST)
            .for_playwright(language) if framework == "playwright" 
            else SimpleConfigBuilder().preset(ConfigPreset.FAST)
            .with_openai() if ai_provider == "openai"
            else SimpleConfigBuilder().preset(ConfigPreset.FAST)
            .build())

def balanced_config(framework: str = "playwright", language: str = "python",
                    ai_provider: str = "openai") -> SimpleConfig:
    """Create a balanced configuration preset.""" 
    builder = SimpleConfigBuilder().preset(ConfigPreset.BALANCED)
    
    if framework == "playwright":
        builder = builder.for_playwright(language)
    elif framework == "selenium":
        builder = builder.for_selenium(language)
    elif framework == "cypress":
        builder = builder.for_cypress()
    
    if ai_provider == "openai":
        builder = builder.with_openai()
    elif ai_provider == "anthropic":
        builder = builder.with_anthropic()
    
    return builder.build()

def accurate_config(framework: str = "playwright", language: str = "python",
                    ai_provider: str = "openai") -> SimpleConfig:
    """Create an accuracy-optimized configuration preset."""
    builder = SimpleConfigBuilder().preset(ConfigPreset.ACCURATE)
    
    # Apply framework
    if framework == "playwright":
        builder = builder.for_playwright(language)
    elif framework == "selenium": 
        builder = builder.for_selenium(language)
    elif framework == "cypress":
        builder = builder.for_cypress()
    
    # Apply AI provider
    if ai_provider == "openai":
        builder = builder.with_openai()
    elif ai_provider == "anthropic":
        builder = builder.with_anthropic()
    
    return builder.build()

def production_config(framework: str = "playwright", language: str = "python",
                      ai_provider: str = "openai") -> SimpleConfig:
    """Create a production-ready configuration preset."""
    builder = SimpleConfigBuilder().preset(ConfigPreset.PRODUCTION)
    
    # Apply framework
    if framework == "playwright":
        builder = builder.for_playwright(language)
    elif framework == "selenium":
        builder = builder.for_selenium(language) 
    elif framework == "cypress":
        builder = builder.for_cypress()
    
    # Apply AI provider
    if ai_provider == "openai":
        builder = builder.with_openai()
    elif ai_provider == "anthropic":
        builder = builder.with_anthropic()
    
    return builder.build()