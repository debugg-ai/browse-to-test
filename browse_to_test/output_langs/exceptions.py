"""
Custom exceptions for the output language generation system.
"""
from typing import List, Optional


class OutputLanguageError(Exception):
    """Base exception for all output language generation errors."""
    pass


class LanguageNotSupportedError(OutputLanguageError):
    """Raised when a requested programming language is not supported."""
    
    def __init__(self, language: str, supported_languages: Optional[List[str]] = None):
        self.language = language
        self.supported_languages = supported_languages or []
        
        if self.supported_languages:
            message = f"Language '{language}' is not supported. Supported languages: {', '.join(self.supported_languages)}"
        else:
            message = f"Language '{language}' is not supported."
            
        super().__init__(message)


class FrameworkNotSupportedError(OutputLanguageError):
    """Raised when a requested framework is not supported for a given language."""
    
    def __init__(self, framework: str, language: str, supported_frameworks: Optional[List[str]] = None):
        self.framework = framework
        self.language = language
        self.supported_frameworks = supported_frameworks or []
        
        if self.supported_frameworks:
            message = f"Framework '{framework}' is not supported for language '{language}'. Supported frameworks: {', '.join(self.supported_frameworks)}"
        else:
            message = f"Framework '{framework}' is not supported for language '{language}'."
            
        super().__init__(message)


class TemplateGenerationError(OutputLanguageError):
    """Raised when template generation fails."""
    
    def __init__(self, template_name: str, language: str, reason: Optional[str] = None):
        self.template_name = template_name
        self.language = language
        self.reason = reason
        
        message = f"Failed to generate template '{template_name}' for language '{language}'"
        if reason:
            message += f": {reason}"
            
        super().__init__(message)


class CodeGenerationError(OutputLanguageError):
    """Raised when code generation fails."""
    
    def __init__(self, operation: str, language: str, framework: Optional[str] = None, reason: Optional[str] = None):
        self.operation = operation
        self.language = language
        self.framework = framework
        self.reason = reason
        
        message = f"Failed to generate {operation} for language '{language}'"
        if framework:
            message += f" with framework '{framework}'"
        if reason:
            message += f": {reason}"
            
        super().__init__(message)


class TemplateNotFoundError(OutputLanguageError):
    """Raised when a required template file is not found."""
    
    def __init__(self, template_path: str, language: str):
        self.template_path = template_path
        self.language = language
        
        message = f"Template file not found: '{template_path}' for language '{language}'"
        super().__init__(message)


class GeneratorNotFoundError(OutputLanguageError):
    """Raised when a required generator is not found."""
    
    def __init__(self, generator_type: str, language: str, framework: str):
        self.generator_type = generator_type
        self.language = language
        self.framework = framework
        
        message = f"Generator '{generator_type}' not found for language '{language}' with framework '{framework}'"
        super().__init__(message) 