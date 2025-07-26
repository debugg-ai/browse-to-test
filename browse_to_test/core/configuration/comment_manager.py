"""
Comment Management System for Multi-Language Code Generation.

This module provides a centralized system for generating language-specific
comments across different programming languages and testing frameworks.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class CommentStyle:
    """Configuration for language-specific comment styles."""
    single_line_prefix: str
    multi_line_start: str
    multi_line_end: str
    multi_line_continue: str
    doc_string_start: str
    doc_string_end: str
    inline_comment_prefix: str


class CommentManager:
    """
    Centralized manager for language-specific comment generation.
    
    This class provides methods to generate properly formatted comments
    for different programming languages, ensuring consistency across
    the entire codebase.
    """
    
    COMMENT_STYLES = {
        "python": CommentStyle(
            single_line_prefix="# ",
            multi_line_start='"""',
            multi_line_end='"""',
            multi_line_continue="# ",
            doc_string_start='"""',
            doc_string_end='"""',
            inline_comment_prefix="  # "
        ),
        "typescript": CommentStyle(
            single_line_prefix="// ",
            multi_line_start="/*",
            multi_line_end="*/",
            multi_line_continue=" * ",
            doc_string_start="/**",
            doc_string_end=" */",
            inline_comment_prefix="  // "
        ),
        "javascript": CommentStyle(
            single_line_prefix="// ",
            multi_line_start="/*",
            multi_line_end="*/",
            multi_line_continue=" * ",
            doc_string_start="/**",
            doc_string_end=" */",
            inline_comment_prefix="  // "
        ),
        "csharp": CommentStyle(
            single_line_prefix="// ",
            multi_line_start="/*",
            multi_line_end="*/",
            multi_line_continue=" * ",
            doc_string_start="/// <summary>",
            doc_string_end="/// </summary>",
            inline_comment_prefix="  // "
        ),
        "java": CommentStyle(
            single_line_prefix="// ",
            multi_line_start="/*",
            multi_line_end="*/",
            multi_line_continue=" * ",
            doc_string_start="/**",
            doc_string_end=" */",
            inline_comment_prefix="  // "
        )
    }
    
    def __init__(self, language: str = "python"):
        """
        Initialize comment manager for a specific language.
        
        Args:
            language: Target programming language
        """
        self.language = language.lower()
        if self.language not in self.COMMENT_STYLES:
            raise ValueError(f"Unsupported language: {language}. Supported: {list(self.COMMENT_STYLES.keys())}")
        
        self.style = self.COMMENT_STYLES[self.language]
    
    def single_line(self, text: str, indent: str = "") -> str:
        """
        Generate a single-line comment.
        
        Args:
            text: Comment text
            indent: Indentation string
            
        Returns:
            Formatted single-line comment
        """
        return f"{indent}{self.style.single_line_prefix}{text}"
    
    def multi_line(self, lines: List[str], indent: str = "") -> List[str]:
        """
        Generate a multi-line comment.
        
        Args:
            lines: List of comment lines
            indent: Indentation string
            
        Returns:
            List of formatted comment lines
        """
        if not lines:
            return []
        
        result = []
        result.append(f"{indent}{self.style.multi_line_start}")
        
        for line in lines:
            if line.strip():
                result.append(f"{indent}{self.style.multi_line_continue}{line}")
            else:
                result.append(f"{indent}{self.style.multi_line_continue}")
        
        result.append(f"{indent}{self.style.multi_line_end}")
        return result
    
    def doc_string(self, description: str, params: Optional[Dict[str, str]] = None, 
                   returns: Optional[str] = None, indent: str = "") -> List[str]:
        """
        Generate a documentation string/comment.
        
        Args:
            description: Function/class description
            params: Dictionary of parameter names and descriptions
            returns: Return value description
            indent: Indentation string
            
        Returns:
            List of formatted documentation lines
        """
        result = []
        
        if self.language == "python":
            result.append(f"{indent}{self.style.doc_string_start}")
            result.append(f"{indent}{description}")
            
            if params:
                result.append(f"{indent}")
                result.append(f"{indent}Args:")
                for param, desc in params.items():
                    result.append(f"{indent}    {param}: {desc}")
            
            if returns:
                result.append(f"{indent}")
                result.append(f"{indent}Returns:")
                result.append(f"{indent}    {returns}")
                
            result.append(f"{indent}{self.style.doc_string_end}")
            
        elif self.language in ["javascript", "typescript"]:
            result.append(f"{indent}{self.style.doc_string_start}")
            result.append(f"{indent} * {description}")
            
            if params:
                result.append(f"{indent} *")
                for param, desc in params.items():
                    result.append(f"{indent} * @param {{{param}}} {desc}")
            
            if returns:
                result.append(f"{indent} * @returns {returns}")
                
            result.append(f"{indent}{self.style.doc_string_end}")
            
        elif self.language == "csharp":
            result.append(f"{indent}{self.style.doc_string_start}")
            result.append(f"{indent}{description}")
            result.append(f"{indent}{self.style.doc_string_end}")
            
            if params:
                for param, desc in params.items():
                    result.append(f"{indent}/// <param name=\"{param}\">{desc}</param>")
            
            if returns:
                result.append(f"{indent}/// <returns>{returns}</returns>")
                
        else:  # java
            result.append(f"{indent}{self.style.doc_string_start}")
            result.append(f"{indent} * {description}")
            
            if params:
                result.append(f"{indent} *")
                for param, desc in params.items():
                    result.append(f"{indent} * @param {param} {desc}")
            
            if returns:
                result.append(f"{indent} * @return {returns}")
                
            result.append(f"{indent}{self.style.doc_string_end}")
        
        return result
    
    def inline(self, text: str) -> str:
        """
        Generate an inline comment.
        
        Args:
            text: Comment text
            
        Returns:
            Formatted inline comment
        """
        return f"{self.style.inline_comment_prefix}{text}"
    
    def step_header(self, step_number: int, description: str = "", 
                   metadata: Optional[Dict[str, Any]] = None, indent: str = "") -> List[str]:
        """
        Generate a detailed step header comment.
        
        Args:
            step_number: Step number (1-based)
            description: Step description
            metadata: Additional step metadata
            indent: Indentation string
            
        Returns:
            List of formatted step header lines
        """
        lines = []
        
        # Main step header
        if description:
            lines.append(self.single_line(f"Step {step_number}: {description}", indent))
        else:
            lines.append(self.single_line(f"Step {step_number}", indent))
        
        # Add metadata as comments if provided
        if metadata:
            for key, value in metadata.items():
                if key != 'description':  # Don't duplicate description
                    lines.append(self.single_line(f"{key}: {value}", indent))
        
        return lines
    
    def action_comment(self, action_type: str, target: str = "", 
                      additional_info: Optional[Dict[str, Any]] = None, 
                      indent: str = "") -> str:
        """
        Generate a detailed action comment.
        
        Args:
            action_type: Type of action (click, fill, navigate, etc.)
            target: Target element or URL
            additional_info: Additional action information
            indent: Indentation string
            
        Returns:
            Formatted action comment
        """
        comment_parts = [action_type.title()]
        
        if target:
            comment_parts.append(f"on '{target}'")
        
        if additional_info:
            for key, value in additional_info.items():
                if value:
                    comment_parts.append(f"({key}: {value})")
        
        return self.single_line(" ".join(comment_parts), indent)
    
    def error_comment(self, error_type: str, details: str = "", indent: str = "") -> str:
        """
        Generate an error comment.
        
        Args:
            error_type: Type of error
            details: Error details
            indent: Indentation string
            
        Returns:
            Formatted error comment
        """
        text = f"ERROR: {error_type}"
        if details:
            text += f" - {details}"
        return self.single_line(text, indent)
    
    def section_separator(self, title: str, indent: str = "", width: int = 60) -> List[str]:
        """
        Generate a section separator comment.
        
        Args:
            title: Section title
            indent: Indentation string
            width: Total width of separator
            
        Returns:
            List of separator lines
        """
        lines = []
        
        if self.language == "python":
            separator = "#" * width
            lines.append(f"{indent}{separator}")
            lines.append(self.single_line(f"{title:^{width-2}}", indent))
            lines.append(f"{indent}{separator}")
        else:
            separator = "/" * width
            lines.append(f"{indent}{self.style.single_line_prefix}{separator}")
            lines.append(self.single_line(f"{title:^{width-3}}", indent))
            lines.append(f"{indent}{self.style.single_line_prefix}{separator}")
        
        return lines
    
    def timestamp_comment(self, indent: str = "") -> str:
        """
        Generate a timestamp comment.
        
        Args:
            indent: Indentation string
            
        Returns:
            Formatted timestamp comment
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.single_line(f"Generated at: {timestamp}", indent)
    
    def contextual_info_comment(self, context: Dict[str, Any], indent: str = "") -> List[str]:
        """
        Generate contextual information comments based on input data.
        
        Args:
            context: Dictionary containing contextual information
            indent: Indentation string
            
        Returns:
            List of formatted context comment lines
        """
        lines = []
        
        if context.get('url'):
            lines.append(self.single_line(f"Target URL: {context['url']}", indent))
        
        if context.get('page_title'):
            lines.append(self.single_line(f"Page Title: {context['page_title']}", indent))
        
        if context.get('element_count'):
            lines.append(self.single_line(f"Elements Found: {context['element_count']}", indent))
        
        if context.get('viewport'):
            lines.append(self.single_line(f"Viewport: {context['viewport']}", indent))
        
        if context.get('browser'):
            lines.append(self.single_line(f"Browser: {context['browser']}", indent))
        
        if context.get('user_inputs'):
            lines.append(self.single_line(f"User Inputs: {len(context['user_inputs'])} fields", indent))
        
        return lines 