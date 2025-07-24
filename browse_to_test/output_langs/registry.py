"""
Language and Framework Registry for the output language generation system.

This module manages the registration and discovery of supported programming
languages and testing frameworks.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional
import json
from dataclasses import dataclass

from .exceptions import LanguageNotSupportedError, FrameworkNotSupportedError


class SupportedLanguage(Enum):
    """Enumeration of supported programming languages."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    # Future languages (implementation pending):
    # CSHARP = "csharp"
    # JAVA = "java"


class SupportedFramework(Enum):
    """Enumeration of supported testing frameworks."""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    # Future frameworks (implementation pending):
    # CYPRESS = "cypress"
    # WEBDRIVER_IO = "webdriver-io"


@dataclass
class LanguageMetadata:
    """Metadata about a supported language."""
    name: str
    display_name: str
    file_extension: str
    comment_prefix: str
    supports_async: bool
    frameworks: List[str]
    package_manager: Optional[str] = None
    template_engine: str = "jinja2"
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LanguageMetadata':
        """Create LanguageMetadata from dictionary."""
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert LanguageMetadata to dictionary."""
        return {
            'name': self.name,
            'display_name': self.display_name, 
            'file_extension': self.file_extension,
            'comment_prefix': self.comment_prefix,
            'supports_async': self.supports_async,
            'frameworks': self.frameworks,
            'package_manager': self.package_manager,
            'template_engine': self.template_engine
        }


class LanguageRegistry:
    """
    Registry for managing supported languages and frameworks.
    
    This class provides methods to discover, validate, and manage
    the available language generators and their capabilities.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the language registry.
        
        Args:
            base_path: Base path to the output_langs directory
        """
        self.base_path = base_path or Path(__file__).parent
        self._language_metadata: Dict[str, LanguageMetadata] = {}
        self._framework_language_matrix: Dict[str, Set[str]] = {}
        self._load_language_metadata()
    
    def _load_language_metadata(self):
        """Load metadata for all supported languages."""
        for language in SupportedLanguage:
            lang_dir = self.base_path / language.value
            metadata_file = lang_dir / "metadata.json"
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata_dict = json.load(f)
                    
                    self._language_metadata[language.value] = LanguageMetadata.from_dict(metadata_dict)
                    
                    # Build framework-language matrix
                    for framework in metadata_dict.get('frameworks', []):
                        if framework not in self._framework_language_matrix:
                            self._framework_language_matrix[framework] = set()
                        self._framework_language_matrix[framework].add(language.value)
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Warning: Failed to load metadata for {language.value}: {e}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported programming languages."""
        return [lang.value for lang in SupportedLanguage]
    
    def get_supported_frameworks(self) -> List[str]:
        """Get list of all supported testing frameworks."""
        return [framework.value for framework in SupportedFramework]
    
    def get_frameworks_for_language(self, language: str) -> List[str]:
        """
        Get list of supported frameworks for a specific language.
        
        Args:
            language: Programming language name
            
        Returns:
            List of supported framework names
            
        Raises:
            LanguageNotSupportedError: If language is not supported
        """
        if language not in self._language_metadata:
            raise LanguageNotSupportedError(language, self.get_supported_languages())
        
        return self._language_metadata[language].frameworks
    
    def get_languages_for_framework(self, framework: str) -> List[str]:
        """
        Get list of languages that support a specific framework.
        
        Args:
            framework: Testing framework name
            
        Returns:
            List of language names that support the framework
        """
        return list(self._framework_language_matrix.get(framework, set()))
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a programming language is supported."""
        return language in [lang.value for lang in SupportedLanguage]
    
    def is_framework_supported(self, framework: str) -> bool:
        """Check if a testing framework is supported."""
        return framework in [fw.value for fw in SupportedFramework]
    
    def is_combination_supported(self, language: str, framework: str) -> bool:
        """
        Check if a language+framework combination is supported.
        
        Args:
            language: Programming language name
            framework: Testing framework name
            
        Returns:
            True if the combination is supported
        """
        if not self.is_language_supported(language):
            return False
        
        if not self.is_framework_supported(framework):
            return False
        
        return framework in self.get_frameworks_for_language(language)
    
    def validate_combination(self, language: str, framework: str) -> None:
        """
        Validate that a language+framework combination is supported.
        
        Args:
            language: Programming language name
            framework: Testing framework name
            
        Raises:
            LanguageNotSupportedError: If language is not supported
            FrameworkNotSupportedError: If framework is not supported for the language
        """
        if not self.is_language_supported(language):
            raise LanguageNotSupportedError(language, self.get_supported_languages())
        
        if not framework in self.get_frameworks_for_language(language):
            raise FrameworkNotSupportedError(
                framework, 
                language, 
                self.get_frameworks_for_language(language)
            )
    
    def get_language_metadata(self, language: str) -> LanguageMetadata:
        """
        Get metadata for a specific language.
        
        Args:
            language: Programming language name
            
        Returns:
            LanguageMetadata object
            
        Raises:
            LanguageNotSupportedError: If language is not supported
        """
        if language not in self._language_metadata:
            raise LanguageNotSupportedError(language, self.get_supported_languages())
        
        return self._language_metadata[language]
    
    def get_language_directory(self, language: str) -> Path:
        """
        Get the directory path for a specific language.
        
        Args:
            language: Programming language name
            
        Returns:
            Path to the language directory
            
        Raises:
            LanguageNotSupportedError: If language is not supported
        """
        if not self.is_language_supported(language):
            raise LanguageNotSupportedError(language, self.get_supported_languages())
        
        return self.base_path / language
    
    def get_generator_path(self, language: str, framework: str) -> Path:
        """
        Get the path to a specific language+framework generator.
        
        Args:
            language: Programming language name
            framework: Testing framework name
            
        Returns:
            Path to the generator file
            
        Raises:
            LanguageNotSupportedError: If language is not supported
            FrameworkNotSupportedError: If framework is not supported for the language
        """
        self.validate_combination(language, framework)
        
        lang_dir = self.get_language_directory(language)
        generator_file = lang_dir / "generators" / f"{framework}_generator.py"
        
        return generator_file
    
    def reload_metadata(self):
        """Reload all language metadata from disk."""
        self._language_metadata.clear()
        self._framework_language_matrix.clear()
        self._load_language_metadata() 