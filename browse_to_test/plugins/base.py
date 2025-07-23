"""
Abstract base classes for output plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from ..core.input_parser import ParsedAutomationData
from ..core.config import OutputConfig


@dataclass
class GeneratedTestScript:
    """Container for generated test script and metadata."""
    
    content: str  # The generated script content
    language: str  # Programming language
    framework: str  # Test framework
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    
    def __post_init__(self):
        """Ensure metadata is not None."""
        if self.metadata is None:
            self.metadata = {}


class PluginError(Exception):
    """Exception raised by output plugins."""
    
    def __init__(self, message: str, plugin_name: Optional[str] = None):
        super().__init__(message)
        self.plugin_name = plugin_name


class OutputPlugin(ABC):
    """Abstract base class for output plugins."""
    
    def __init__(self, config: OutputConfig):
        """
        Initialize the output plugin.
        
        Args:
            config: Output configuration settings
        """
        self.config = config
    
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Return the name of this plugin."""
        pass
    
    @property
    @abstractmethod
    def supported_frameworks(self) -> List[str]:
        """Return list of supported framework names."""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Return list of supported programming languages."""
        pass
    
    @abstractmethod
    def validate_config(self) -> List[str]:
        """
        Validate the plugin configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        pass
    
    @abstractmethod
    def generate_test_script(
        self, 
        parsed_data: ParsedAutomationData,
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> GeneratedTestScript:
        """
        Generate test script from parsed automation data.
        
        Args:
            parsed_data: Parsed automation data to convert
            analysis_results: Optional analysis results from ActionAnalyzer
            
        Returns:
            Generated test script with metadata
            
        Raises:
            PluginError: If generation fails
        """
        pass
    
    @abstractmethod
    def get_template_variables(self) -> Dict[str, Any]:
        """
        Get template variables for script generation.
        
        Returns:
            Dictionary of variables available to templates
        """
        pass
    
    def supports_framework(self, framework: str) -> bool:
        """Check if plugin supports a specific framework."""
        return framework.lower() in [f.lower() for f in self.supported_frameworks]
    
    def supports_language(self, language: str) -> bool:
        """Check if plugin supports a specific language."""
        return language.lower() in [l.lower() for l in self.supported_languages]
    
    def supports_config(self, config: OutputConfig) -> bool:
        """Check if plugin supports the given configuration."""
        return (
            self.supports_framework(config.framework) and 
            self.supports_language(config.language)
        )
    
    def _format_code(self, code: str) -> str:
        """
        Format generated code according to configuration.
        
        Args:
            code: Raw generated code
            
        Returns:
            Formatted code
        """
        if not code:
            return code
        
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Apply indentation
            if line.strip():
                # Count existing indentation
                existing_indent = len(line) - len(line.lstrip())
                if existing_indent > 0:
                    # Replace with configured indentation
                    indent_level = existing_indent // 4  # Assume 4-space default
                    new_indent = ' ' * (indent_level * self.config.indent_size)
                    formatted_line = new_indent + line.lstrip()
                else:
                    formatted_line = line
                
                # Apply line length limit
                if len(formatted_line) > self.config.max_line_length:
                    # Simple line breaking (plugins can override for language-specific rules)
                    formatted_line = self._break_long_line(formatted_line)
                
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _break_long_line(self, line: str) -> str:
        """
        Break a long line into multiple lines (basic implementation).
        
        Plugins should override this for language-specific line breaking.
        """
        if len(line) <= self.config.max_line_length:
            return line
        
        # Very basic line breaking - just add a comment indicating it's too long
        return f"{line}  # TODO: Break this long line"
    
    def _add_header_comment(self, content: str) -> str:
        """Add header comment to generated script."""
        if not self.config.add_comments:
            return content
        
        header_lines = [
            "# Generated test script using browse-to-test",
            f"# Framework: {self.config.framework}",
            f"# Language: {self.config.language}",
            "# This script was automatically generated from browser automation data",
            "",
        ]
        
        return '\n'.join(header_lines) + content
    
    def _handle_sensitive_data(self, text: str) -> str:
        """
        Handle sensitive data placeholders in text.
        
        Args:
            text: Text that may contain sensitive data placeholders
            
        Returns:
            Text with appropriate handling applied
        """
        if not self.config.mask_sensitive_data:
            return text
        
        # Replace sensitive data placeholders with environment variable references
        import re
        
        # Pattern to match <secret>key</secret>
        pattern = r'<secret>([^<]+)</secret>'
        
        def replace_secret(match):
            key = match.group(1)
            if key in self.config.sensitive_data_keys:
                return f"{{get_env_var('{key.upper()}')}}"
            return match.group(0)  # Keep original if not in sensitive keys
        
        return re.sub(pattern, replace_secret, text) 