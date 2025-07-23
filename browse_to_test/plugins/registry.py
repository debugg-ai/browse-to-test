"""
Plugin registry for managing output plugins.
"""

import logging
from typing import Dict, List, Type, Optional
from .base import OutputPlugin, PluginError
from ..core.config import OutputConfig


logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for managing output plugins."""
    
    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, Type[OutputPlugin]] = {}
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Register all available default plugins."""
        try:
            from .playwright_plugin import PlaywrightPlugin
            self.register_plugin("playwright", PlaywrightPlugin)
        except ImportError as e:
            logger.warning(f"Playwright plugin not available: {e}")
        
        try:
            from .selenium_plugin import SeleniumPlugin
            self.register_plugin("selenium", SeleniumPlugin)
        except ImportError as e:
            logger.warning(f"Selenium plugin not available: {e}")
        
        try:
            from .cypress_plugin import CypressPlugin
            self.register_plugin("cypress", CypressPlugin)
        except ImportError as e:
            logger.warning(f"Cypress plugin not available: {e}")
        
        try:
            from .webdriver_io_plugin import WebDriverIOPlugin
            self.register_plugin("webdriverio", WebDriverIOPlugin)
        except ImportError as e:
            logger.warning(f"WebDriverIO plugin not available: {e}")
    
    def register_plugin(self, name: str, plugin_class: Type[OutputPlugin]):
        """
        Register a new output plugin.
        
        Args:
            name: Name to register the plugin under
            plugin_class: Class that implements OutputPlugin
        """
        if not issubclass(plugin_class, OutputPlugin):
            raise ValueError(f"Plugin class must inherit from OutputPlugin")
        
        self._plugins[name.lower()] = plugin_class
        logger.debug(f"Registered output plugin: {name}")
    
    def create_plugin(self, config: OutputConfig) -> OutputPlugin:
        """
        Create a plugin instance from configuration.
        
        Args:
            config: Output configuration containing plugin details
            
        Returns:
            Configured plugin instance
            
        Raises:
            PluginError: If plugin is not available or configuration is invalid
        """
        framework_name = config.framework.lower()
        
        # First, try to find plugin by exact framework name
        if framework_name in self._plugins:
            plugin_class = self._plugins[framework_name]
        else:
            # Try to find plugin that supports the framework
            plugin_class = None
            for plugin_name, plugin_cls in self._plugins.items():
                try:
                    # Create temporary instance to check support
                    temp_instance = plugin_cls(config)
                    if temp_instance.supports_framework(config.framework):
                        plugin_class = plugin_cls
                        break
                except Exception:
                    continue
            
            if plugin_class is None:
                available = ', '.join(self._get_supported_frameworks())
                raise PluginError(
                    f"No plugin found for framework: {config.framework}. "
                    f"Supported frameworks: {available}"
                )
        
        try:
            # Create plugin instance
            plugin = plugin_class(config)
            
            # Validate the configuration
            validation_errors = plugin.validate_config()
            if validation_errors:
                raise PluginError(
                    f"Plugin configuration validation failed: {'; '.join(validation_errors)}",
                    plugin_name=plugin.plugin_name
                )
            
            # Check if plugin supports the requested configuration
            if not plugin.supports_config(config):
                raise PluginError(
                    f"Plugin {plugin.plugin_name} does not support framework '{config.framework}' "
                    f"with language '{config.language}'",
                    plugin_name=plugin.plugin_name
                )
            
            logger.info(f"Created plugin: {plugin.plugin_name} for {config.framework}/{config.language}")
            return plugin
            
        except Exception as e:
            if isinstance(e, PluginError):
                raise
            raise PluginError(
                f"Failed to create plugin for {config.framework}: {e}",
                plugin_name=framework_name
            ) from e
    
    def list_available_plugins(self) -> List[str]:
        """
        List all registered plugin names.
        
        Returns:
            List of available plugin names
        """
        return sorted(self._plugins.keys())
    
    def get_plugin_info(self, plugin_name: str) -> Dict[str, any]:
        """
        Get information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dictionary containing plugin information
            
        Raises:
            PluginError: If plugin is not found
        """
        plugin_name = plugin_name.lower()
        
        if plugin_name not in self._plugins:
            raise PluginError(f"Unknown plugin: {plugin_name}")
        
        plugin_class = self._plugins[plugin_name]
        
        # Create a temporary instance to get information
        try:
            from ..core.config import OutputConfig
            temp_config = OutputConfig()
            temp_instance = plugin_class(temp_config)
            return {
                "name": temp_instance.plugin_name,
                "supported_frameworks": temp_instance.supported_frameworks,
                "supported_languages": temp_instance.supported_languages,
                "class": plugin_class.__name__,
                "module": plugin_class.__module__,
            }
        except Exception as e:
            logger.warning(f"Could not get info for plugin {plugin_name}: {e}")
            return {
                "name": plugin_name,
                "supported_frameworks": [],
                "supported_languages": [],
                "class": plugin_class.__name__,
                "module": plugin_class.__module__,
                "error": str(e)
            }
    
    def _get_supported_frameworks(self) -> List[str]:
        """Get list of all supported frameworks across all plugins."""
        frameworks = set()
        
        for plugin_name, plugin_class in self._plugins.items():
            try:
                from ..core.config import OutputConfig
                temp_config = OutputConfig()
                temp_instance = plugin_class(temp_config)
                frameworks.update(temp_instance.supported_frameworks)
            except Exception:
                continue
        
        return sorted(list(frameworks))
    
    def get_supported_languages_for_framework(self, framework: str) -> List[str]:
        """
        Get supported languages for a specific framework.
        
        Args:
            framework: Framework name
            
        Returns:
            List of supported language names
        """
        languages = set()
        
        for plugin_name, plugin_class in self._plugins.items():
            try:
                from ..core.config import OutputConfig
                temp_config = OutputConfig()
                temp_instance = plugin_class(temp_config)
                if temp_instance.supports_framework(framework):
                    languages.update(temp_instance.supported_languages)
            except Exception:
                continue
        
        return sorted(list(languages))
    
    def validate_framework_language_combination(self, framework: str, language: str) -> bool:
        """
        Check if a framework/language combination is supported.
        
        Args:
            framework: Framework name
            language: Language name
            
        Returns:
            True if combination is supported, False otherwise
        """
        for plugin_name, plugin_class in self._plugins.items():
            try:
                from ..core.config import OutputConfig
                temp_config = OutputConfig(framework=framework, language=language)
                temp_instance = plugin_class(temp_config)
                if temp_instance.supports_config(temp_config):
                    return True
            except Exception:
                continue
        
        return False
    
    def find_best_plugin_for_config(self, config: OutputConfig) -> Optional[str]:
        """
        Find the best plugin for a given configuration.
        
        Args:
            config: Output configuration
            
        Returns:
            Name of the best plugin, or None if no suitable plugin found
        """
        # First, try exact framework match
        framework_name = config.framework.lower()
        if framework_name in self._plugins:
            try:
                plugin_class = self._plugins[framework_name]
                temp_instance = plugin_class(config)
                if temp_instance.supports_config(config):
                    return framework_name
            except Exception:
                pass
        
        # Then, try to find any plugin that supports the configuration
        for plugin_name, plugin_class in self._plugins.items():
            try:
                temp_instance = plugin_class(config)
                if temp_instance.supports_config(config):
                    return plugin_name
            except Exception:
                continue
        
        return None 