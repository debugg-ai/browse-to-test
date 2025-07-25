"""
Language Manager for the output language generation system.

This module provides the main interface for generating test scripts and utilities
in different programming languages and testing frameworks.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import importlib

from .registry import LanguageRegistry
from .exceptions import (
    LanguageNotSupportedError,
    FrameworkNotSupportedError,
    CodeGenerationError,
    GeneratorNotFoundError
)


class LanguageManager:
    """
    Main manager for language-specific code generation.
    
    This class provides a unified interface for generating test scripts,
    utility functions, and constants across different programming languages
    and testing frameworks.
    """
    
    def __init__(self, language: str, framework: str, output_dir: Optional[Path] = None):
        """
        Initialize the language manager.
        
        Args:
            language: Target programming language (python, typescript, etc.)
            framework: Target testing framework (playwright, selenium, etc.)
            output_dir: Directory where output files will be generated
            
        Raises:
            LanguageNotSupportedError: If language is not supported
            FrameworkNotSupportedError: If framework is not supported for the language
        """
        self.language = language
        self.framework = framework
        self.output_dir = output_dir or Path.cwd()
        
        # Initialize registry and validate combination
        self.registry = LanguageRegistry()
        self.registry.validate_combination(language, framework)
        
        # Get language metadata
        self.metadata = self.registry.get_language_metadata(language)
        
        # Load generator
        self.generator = self._load_generator()
        
        # Load shared resources
        self._load_shared_resources()
    
    def _load_generator(self):
        """Load the appropriate generator for the language+framework combination."""
        try:
            # Construct module path for generator
            module_path = f"browse_to_test.output_langs.{self.language}.generators.{self.framework}_generator"
            generator_module = importlib.import_module(module_path)
            
            # Construct generator class name (e.g., PlaywrightPythonGenerator)
            class_name = f"{self.framework.title()}{self.language.title()}Generator"
            generator_class = getattr(generator_module, class_name)
            
            return generator_class()
            
        except (ImportError, AttributeError) as e:
            raise GeneratorNotFoundError(
                f"{self.framework}_generator", 
                self.language, 
                self.framework
            ) from e
    
    def _load_shared_resources(self):
        """Load shared constants and messages."""
        base_path = Path(__file__).parent
        
        # Load constants
        constants_path = base_path / "common" / "constants.json"
        with open(constants_path, 'r') as f:
            self.constants = json.load(f)
        
        # Load messages  
        messages_path = base_path / "common" / "messages.json"
        with open(messages_path, 'r') as f:
            self.messages = json.load(f)
        
        # Load patterns
        patterns_path = base_path / "common" / "patterns.json"
        with open(patterns_path, 'r') as f:
            self.patterns = json.load(f)
    
    def generate_utilities(self, **kwargs) -> str:
        """
        Generate utility functions for the current language and framework.
        
        Args:
            **kwargs: Additional generation options
            
        Returns:
            Generated utility functions as string
            
        Raises:
            CodeGenerationError: If generation fails
        """
        try:
            return self.generator.generate_utilities(**kwargs)
        except Exception as e:
            raise CodeGenerationError(
                "utilities", 
                self.language, 
                self.framework, 
                str(e)
            ) from e
    
    def generate_constants(self, **kwargs) -> str:
        """
        Generate constants for the current language.
        
        Args:
            **kwargs: Additional generation options
            
        Returns:
            Generated constants as string
            
        Raises:
            CodeGenerationError: If generation fails
        """
        try:
            return self.generator.generate_constants(**kwargs)
        except Exception as e:
            raise CodeGenerationError(
                "constants", 
                self.language, 
                self.framework, 
                str(e)
            ) from e
    
    def generate_exceptions(self, **kwargs) -> str:
        """
        Generate exception classes for the current language.
        
        Args:
            **kwargs: Additional generation options
            
        Returns:
            Generated exception classes as string
            
        Raises:
            CodeGenerationError: If generation fails
        """
        try:
            return self.generator.generate_exceptions(**kwargs)
        except Exception as e:
            raise CodeGenerationError(
                "exceptions", 
                self.language, 
                self.framework, 
                str(e)
            ) from e
    
    def generate_imports(self, **kwargs) -> str:
        """
        Generate import statements for the current language and framework.
        
        Args:
            **kwargs: Additional generation options
            
        Returns:
            Generated import statements as string
            
        Raises:
            CodeGenerationError: If generation fails
        """
        try:
            return self.generator.generate_imports(**kwargs)
        except Exception as e:
            raise CodeGenerationError(
                "imports", 
                self.language, 
                self.framework, 
                str(e)
            ) from e
    
    def generate_test_script(self, automation_data: List[Dict[str, Any]], **kwargs) -> str:
        """
        Generate a complete test script from automation data.
        
        Args:
            automation_data: List of automation steps/actions
            **kwargs: Additional generation options (test_name, include_utilities, etc.)
            
        Returns:
            Generated test script as string
            
        Raises:
            CodeGenerationError: If generation fails
        """
        try:
            return self.generator.generate_test_script(automation_data, **kwargs)
        except Exception as e:
            raise CodeGenerationError(
                "test_script", 
                self.language, 
                self.framework, 
                str(e)
            ) from e
    
    def generate_setup_files(self, output_directory: Optional[Path] = None, force_regenerate: bool = False) -> Dict[str, Path]:
        """
        Generate all setup files (utilities, constants, exceptions) for the current language.
        
        Args:
            output_directory: Directory to write files to (defaults to self.output_dir)
            force_regenerate: Whether to regenerate files even if they exist
            
        Returns:
            Dictionary mapping file types to their paths
            
        Raises:
            CodeGenerationError: If generation fails
        """
        output_dir = output_directory or self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        file_extension = self.metadata.file_extension
        
        try:
            # Generate utilities file
            utilities_path = output_dir / f"utilities{file_extension}"
            if force_regenerate or not utilities_path.exists():
                utilities_content = self.generate_utilities()
                utilities_path.write_text(utilities_content)
                generated_files["utilities"] = utilities_path
            
            # Generate constants file
            constants_path = output_dir / f"constants{file_extension}"
            if force_regenerate or not constants_path.exists():
                constants_content = self.generate_constants()
                constants_path.write_text(constants_content)
                generated_files["constants"] = constants_path
            
            # Generate exceptions file
            exceptions_path = output_dir / f"exceptions{file_extension}"
            if force_regenerate or not exceptions_path.exists():
                exceptions_content = self.generate_exceptions()
                exceptions_path.write_text(exceptions_content)
                generated_files["exceptions"] = exceptions_path
            
            # Generate imports file (if needed)
            if hasattr(self.generator, 'generate_imports'):
                imports_path = output_dir / f"imports{file_extension}"
                if force_regenerate or not imports_path.exists():
                    imports_content = self.generate_imports(include_utilities=False)
                    imports_path.write_text(imports_content)
                    generated_files["imports"] = imports_path
            
            return generated_files
            
        except Exception as e:
            raise CodeGenerationError(
                "setup_files", 
                self.language, 
                self.framework, 
                str(e)
            ) from e
    
    def get_import_statements_for_test(self, use_setup_files: bool = True) -> List[str]:
        """
        Get the import statements needed for a test script.
        
        Args:
            use_setup_files: Whether to import from generated setup files
            
        Returns:
            List of import statements
        """
        imports = []
        
        if use_setup_files:
            # Import from generated setup files
            if self.language == "python":
                imports.append(f"from .utilities import *")
                imports.append(f"from .constants import *")
                imports.append(f"from .exceptions import *")
            elif self.language in ["typescript", "javascript"]:
                imports.append(f"import * from './utilities{self.metadata.file_extension}';")
                imports.append(f"import * from './constants{self.metadata.file_extension}';")
                imports.append(f"import * from './exceptions{self.metadata.file_extension}';")
            # Add more languages as needed
        else:
            # Generate inline imports
            try:
                imports_content = self.generate_imports(include_utilities=True)
                imports.extend(imports_content.split('\n'))
            except Exception:
                # Fallback to basic framework imports
                framework_imports = self.metadata.frameworks.get(self.framework, [])
                imports.extend(framework_imports)
        
        return imports
    
    def validate_automation_data(self, automation_data: List[Dict[str, Any]]) -> List[str]:
        """
        Validate automation data for common issues.
        
        Args:
            automation_data: List of automation steps to validate
            
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        for i, step in enumerate(automation_data):
            step_num = i + 1
            
            # Check required fields
            if 'type' not in step:
                issues.append(f"Step {step_num}: Missing 'type' field")
                continue
            
            action_type = step['type'].lower()
            
            # Validate action-specific requirements
            if action_type in ['click', 'fill', 'select', 'assert_visible']:
                if 'selector' not in step or not step['selector'].strip():
                    issues.append(f"Step {step_num}: Missing or empty 'selector' for {action_type} action")
            
            if action_type in ['fill', 'select']:
                if 'text' not in step or step['text'] is None:
                    issues.append(f"Step {step_num}: Missing 'text' field for {action_type} action")
            
            if action_type == 'navigate':
                if 'url' not in step or not step['url'].strip():
                    issues.append(f"Step {step_num}: Missing or empty 'url' for navigate action")
            
            # Check for potentially problematic selectors
            if 'selector' in step:
                selector = step['selector']
                if '//' in selector:  # Likely XPath
                    if self.framework == 'playwright' and not selector.startswith('xpath='):
                        issues.append(f"Step {step_num}: XPath selector should be prefixed with 'xpath=' for Playwright")
        
        return issues
    
    def get_supported_actions(self) -> List[str]:
        """
        Get list of supported action types for the current framework.
        
        Returns:
            List of supported action type names
        """
        # This could be extended to be framework-specific
        return list(self.constants.get("action_types", {}).keys())
    
    def get_framework_info(self) -> Dict[str, Any]:
        """
        Get information about the current framework and language combination.
        
        Returns:
            Dictionary with framework information
        """
        return {
            "language": self.language,
            "framework": self.framework,
            "display_name": self.metadata.display_name,
            "file_extension": self.metadata.file_extension,
            "supports_async": self.metadata.supports_async,
            "package_manager": self.metadata.package_manager,
            "supported_actions": self.get_supported_actions()
        } 