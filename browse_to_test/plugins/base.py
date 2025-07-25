"""
Abstract base classes for output plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from ..core.processing.input_parser import ParsedAutomationData, ParsedStep
from ..core.configuration.config import OutputConfig


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
    """Exception raised by plugins during operation."""
    
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
        analysis_results: Optional[Dict[str, Any]] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> GeneratedTestScript:
        """
        Generate test script from parsed automation data.
        
        Args:
            parsed_data: Parsed automation data to convert
            analysis_results: Optional analysis results from ActionAnalyzer
            system_context: Optional system context information
            context_hints: Optional context hints for generation
            
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
    
    # Incremental support methods (optional)
    
    def supports_incremental(self) -> bool:
        """
        Check if this plugin supports incremental script generation.
        
        Returns:
            True if incremental methods are implemented, False otherwise
        """
        return (
            hasattr(self, 'setup_incremental_script') and
            hasattr(self, 'add_incremental_step') and
            hasattr(self, 'finalize_incremental_script')
        )
    
    def setup_incremental_script(
        self,
        target_url: Optional[str] = None,
        system_context: Optional[Any] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Set up incremental script generation (setup phase).
        
        This should initialize the script structure with imports, helpers,
        and framework setup code.
        
        Args:
            target_url: URL being tested
            system_context: System context information
            context_hints: Additional context hints
            
        Returns:
            Dictionary containing:
            - 'imports': List of import lines
            - 'helpers': List of helper function lines
            - 'setup_code': List of setup/initialization lines
            - 'cleanup_code': List of cleanup lines
            
        Raises:
            NotImplementedError: If plugin doesn't support incremental mode
        """
        raise NotImplementedError(f"Plugin {self.plugin_name} does not support incremental script generation")
    
    def add_incremental_step(
        self,
        step: ParsedStep,
        current_state: Any,  # ScriptState from incremental_orchestrator
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new step to the incremental script generation.
        
        Args:
            step: Parsed step to add
            current_state: Current script state
            analysis_results: Analysis results for this step
            
        Returns:
            Dictionary containing:
            - 'step_code': List of code lines for this step
            - 'validation_issues': List of validation issues found
            - 'insights': List of analysis insights
            
        Raises:
            NotImplementedError: If plugin doesn't support incremental mode
        """
        raise NotImplementedError(f"Plugin {self.plugin_name} does not support incremental script generation")
    
    def finalize_incremental_script(
        self,
        current_state: Any,  # ScriptState from incremental_orchestrator
        final_validation: bool = True,
        optimize_script: bool = True
    ) -> Dict[str, Any]:
        """
        Finalize the incremental script generation (finalization phase).
        
        Args:
            current_state: Current script state
            final_validation: Whether to perform final validation
            optimize_script: Whether to apply optimizations
            
        Returns:
            Dictionary containing:
            - 'final_cleanup_code': Updated cleanup code
            - 'validation_issues': List of validation issues
            - 'optimization_insights': List of optimization insights
            
        Raises:
            NotImplementedError: If plugin doesn't support incremental mode
        """
        raise NotImplementedError(f"Plugin {self.plugin_name} does not support incremental script generation")
    
    # Helper methods
    
    def supports_framework(self, framework: str) -> bool:
        """Check if this plugin supports a specific framework."""
        return framework.lower() in [f.lower() for f in self.supported_frameworks]
    
    def supports_language(self, language: str) -> bool:
        """Check if this plugin supports a specific language."""
        return language.lower() in [l.lower() for l in self.supported_languages]
    
    def supports_config(self, config: OutputConfig) -> bool:
        """Check if this plugin supports a given configuration."""
        return (
            self.supports_framework(config.framework) and
            self.supports_language(config.language)
        )
    
    def _format_code(self, content: str) -> str:
        """
        Format generated code (basic implementation).
        
        Subclasses can override this for framework-specific formatting.
        """
        # Basic formatting: ensure consistent indentation and line endings
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            formatted_lines.append(line)
        
        # Remove excessive blank lines
        result_lines = []
        prev_blank = False
        
        for line in formatted_lines:
            is_blank = not line.strip()
            
            if is_blank and prev_blank:
                continue  # Skip consecutive blank lines
            
            result_lines.append(line)
            prev_blank = is_blank
        
        return '\n'.join(result_lines)
    
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
        # Handle None input gracefully
        if text is None:
            return text
            
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
        
        processed_text = re.sub(pattern, replace_secret, text)
        
        # Only check for sensitive keywords if no placeholders were replaced
        # This prevents masking placeholder syntax like <secret>password</secret>
        if processed_text == text and self.config.sensitive_data_keys:
            for sensitive_key in self.config.sensitive_data_keys:
                # Check if the sensitive key is contained in the text (case-insensitive)
                if sensitive_key.lower() in processed_text.lower():
                    # Mask the sensitive data
                    processed_text = "***REDACTED***"
                    break
        
        return processed_text 