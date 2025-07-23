"""
Language utilities for browse-to-test.

This module provides language-specific templates, utilities, and constants
for generating test scripts in different programming languages.

The new unified structure:
- templates/
  - python/
    - utilities.py  (unified utilities for all frameworks)
    - constants.py  (test constants and configuration)
  - typescript/
  - javascript/
  - csharp/
  - java/
"""

from pathlib import Path

# Language template directory
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Supported languages
SUPPORTED_LANGUAGES = [
    "python",
    "typescript", 
    "javascript",
    "csharp",
    "java"
]

def get_template_path(language: str, filename: str = None) -> Path:
    """
    Get the path to a language template file.
    
    Args:
        language: Programming language (python, typescript, etc.)
        filename: Specific template file (optional)
        
    Returns:
        Path to template directory or specific file
        
    Raises:
        ValueError: If language is not supported
    """
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}. Supported: {SUPPORTED_LANGUAGES}")
    
    template_dir = TEMPLATES_DIR / language
    
    if filename:
        return template_dir / filename
    else:
        return template_dir

def get_utilities_content(language: str) -> str:
    """
    Get the utilities file content for a language.
    
    Args:
        language: Programming language
        
    Returns:
        Content of utilities file
    """
    utilities_path = get_template_path(language, "utilities.py" if language == "python" else "utilities")
    
    if utilities_path.exists():
        return utilities_path.read_text()
    else:
        return ""

def get_constants_content(language: str) -> str:
    """
    Get the constants file content for a language.
    
    Args:
        language: Programming language
        
    Returns:
        Content of constants file
    """
    constants_path = get_template_path(language, "constants.py" if language == "python" else "constants")
    
    if constants_path.exists():
        return constants_path.read_text()
    else:
        return "" 