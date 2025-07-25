#!/usr/bin/env python3
"""
Shared setup manager for generating reusable test utilities and clean test scripts.

This module manages the generation of shared setup files that contain reusable
helper functions, utilities, and configuration, allowing main test scripts to
be clean and focused.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import json
import hashlib
from datetime import datetime

from .language_templates import LanguageTemplateManager, LanguageTemplate


@dataclass
class SetupUtility:
    """Represents a reusable utility function or setup code."""
    
    name: str
    content: str
    dependencies: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    framework: Optional[str] = None
    category: str = "helper"  # helper, exception, config, etc.
    description: str = ""
    
    # Language-specific content 
    language_content: Dict[str, str] = field(default_factory=dict)  # language -> content mapping
    language_imports: Dict[str, List[str]] = field(default_factory=dict)  # language -> imports mapping
    
    def get_hash(self) -> str:
        """Get a hash of the utility content for deduplication."""
        content_str = f"{self.name}_{self.content}_{sorted(self.dependencies)}_{sorted(self.imports)}"
        return hashlib.md5(content_str.encode()).hexdigest()[:8]
    
    def get_content_for_language(self, language: str) -> str:
        """Get content for the specified language, falling back to default content."""
        return self.language_content.get(language, self.content)
    
    def get_imports_for_language(self, language: str) -> List[str]:
        """Get imports for the specified language, falling back to default imports."""
        return self.language_imports.get(language, self.imports)
    
    def set_content_for_language(self, language: str, content: str, imports: Optional[List[str]] = None):
        """Set language-specific content and imports."""
        self.language_content[language] = content
        if imports is not None:
            self.language_imports[language] = imports


@dataclass
class SharedSetupConfig:
    """Configuration for shared setup generation."""
    
    setup_dir: Path = Path("browse_to_test/language_utils/test_setup")
    utilities_file: str = "test_utilities"  # No extension - will be added based on language
    config_file: str = "test_config"
    constants_file: str = "test_constants"
    framework_helpers_file: str = "framework_helpers"
    
    # Generation options
    generate_separate_files: bool = True
    include_docstrings: bool = True
    include_type_hints: bool = True
    organize_by_category: bool = True
    
    # Import management
    auto_generate_imports: bool = True
    include_common_imports: bool = True
    
    # Language-specific options
    language: str = "python"  # Will be set from OutputConfig
    
    def get_utilities_path(self, extension: str = ".py") -> Path:
        return self.setup_dir / f"{self.utilities_file}{extension}"
    
    def get_config_path(self, extension: str = ".py") -> Path:
        return self.setup_dir / f"{self.config_file}{extension}"
    
    def get_constants_path(self, extension: str = ".py") -> Path:
        return self.setup_dir / f"{self.constants_file}{extension}"
    
    def get_framework_helpers_path(self, extension: str = ".py") -> Path:
        return self.setup_dir / f"{self.framework_helpers_file}{extension}"


class SharedSetupManager:
    """
    Manages shared setup utilities and generates clean, modular test scripts.
    
    This class accumulates reusable utilities across multiple test script generations,
    maintains shared setup files, and generates clean test scripts that import
    from these shared modules.
    """
    
    def __init__(self, config: SharedSetupConfig, project_root: Optional[Path] = None, language: str = "python"):
        """
        Initialize the shared setup manager.
        
        Args:
            config: Configuration for shared setup generation
            project_root: Root directory of the project (defaults to current working directory)
            language: Target programming language for code generation
        """
        self.config = config
        self.config.language = language  # Set the language in config
        self.project_root = project_root or Path.cwd()
        self.language = language
        
        # Initialize language template manager
        self.template_manager = LanguageTemplateManager()
        
        # Track accumulated utilities
        self._utilities: Dict[str, SetupUtility] = {}
        self._utility_hashes: Set[str] = set()
        self._framework_utilities: Dict[str, List[str]] = {}
        
        # Track generated files by language
        self._generated_files: Dict[str, Set[Path]] = {}  # language -> set of files
        self._last_generation_time: Optional[datetime] = None
        
        # Setup categories
        self._categories = {
            "helper": "Helper functions for test actions",
            "exception": "Custom exception classes", 
            "config": "Configuration and constants",
            "framework": "Framework-specific utilities",
            "assertion": "Custom assertion helpers",
            "data": "Test data management",
            "reporting": "Test reporting utilities"
        }
        
        # Language-specific settings
        self._current_language = language
        self._supported_languages = self.template_manager.get_supported_languages()
    
    def add_utility(self, utility: SetupUtility) -> bool:
        """
        Add a utility to the shared setup.
        
        Args:
            utility: The utility to add
            
        Returns:
            True if utility was added (new), False if it already exists
        """
        utility_hash = utility.get_hash()
        
        # Check if we already have this utility
        if utility_hash in self._utility_hashes:
            return False
        
        # Add the utility
        self._utilities[utility.name] = utility
        self._utility_hashes.add(utility_hash)
        
        # Track framework-specific utilities
        if utility.framework:
            if utility.framework not in self._framework_utilities:
                self._framework_utilities[utility.framework] = []
            self._framework_utilities[utility.framework].append(utility.name)
        
        return True
    
    def add_standard_utilities(self, framework: str = "playwright") -> None:
        """Add standard utilities for the specified framework and current language."""
        
        # Generate exception utility
        exception_utility = self._create_language_aware_utility(
            name="E2eActionError",
            utility_type="exception",
            category="exception",
            description="Custom exception for test action failures",
            framework=framework
        )
        self.add_utility(exception_utility)
        
        # Generate sensitive data replacement utility
        sensitive_data_utility = self._create_language_aware_utility(
            name="replace_sensitive_data",
            utility_type="helper",
            category="helper",
            description="Replace sensitive data placeholders in strings",
            framework=framework
        )
        self.add_utility(sensitive_data_utility)
        
        if framework == "playwright":
            # Playwright-specific utilities
            safe_action_utility = self._create_language_aware_utility(
                name="safe_action",
                utility_type="framework",
                category="framework",
                description="Safe action execution with error handling for Playwright",
                framework=framework
            )
            self.add_utility(safe_action_utility)
            
            locate_and_act_utility = self._create_language_aware_utility(
                name="try_locate_and_act",
                utility_type="framework",
                category="framework",
                description="Robust element location and interaction for Playwright",
                framework=framework
            )
            self.add_utility(locate_and_act_utility)
        
        elif framework == "selenium":
            # Selenium-specific utilities
            selenium_safe_action_utility = self._create_language_aware_utility(
                name="safe_selenium_action",
                utility_type="framework",
                category="framework",
                description="Safe action execution with error handling for Selenium",
                framework=framework
            )
            self.add_utility(selenium_safe_action_utility)
    
    def _create_language_aware_utility(self, name: str, utility_type: str, category: str, description: str, framework: str) -> SetupUtility:
        """Create a utility with language-specific content."""
        utility = SetupUtility(
            name=name,
            content="",  # Will be set per language
            category=category,
            description=description,
            framework=framework if utility_type == "framework" else None
        )
        
        # Generate content for all supported languages
        for language in self._supported_languages:
            try:
                content = self.template_manager.generate_utility_code(
                    language=language,
                    utility_name=name,
                    utility_type=utility_type,
                    framework=framework
                )
                
                # Get language-specific imports (this is simplified - would need more complex logic)
                imports = self._get_language_imports(language, framework, utility_type)
                
                utility.set_content_for_language(language, content, imports)
                
                # Set default content to current language
                if language == self._current_language:
                    utility.content = content
                    utility.imports = imports
                    
            except Exception as e:
                # If generation fails for a language, log and continue
                print(f"Warning: Failed to generate {name} for {language}: {e}")
        
        return utility
    
    def _get_language_imports(self, language: str, framework: str, utility_type: str) -> List[str]:
        """Get language-specific imports for a utility."""
        imports = []
        
        if language == "python":
            if framework == "playwright" and utility_type == "framework":
                imports = ["from playwright.async_api import Page", "import sys"]
            elif framework == "selenium" and utility_type == "framework":
                imports = ["import sys"]
            elif utility_type == "helper":
                imports = ["typing"]
        
        elif language == "typescript":
            if framework == "playwright":
                imports = ["import { Page } from '@playwright/test'"]
            # Add more TypeScript imports as needed
        
        elif language == "javascript":
            if framework == "playwright":
                imports = ["const { Page } = require('@playwright/test')"]
            # Add more JavaScript imports as needed
        
        # Add more language-specific imports as needed
        
        return imports
    
    def generate_setup_files(self, force_regenerate: bool = False, language: Optional[str] = None) -> Dict[str, Path]:
        """
        Generate all shared setup files for the specified language.
        
        Args:
            force_regenerate: Whether to regenerate files even if they exist
            language: Target language (defaults to current language)
            
        Returns:
            Dictionary mapping file types to their paths
        """
        target_language = language or self._current_language
        extension = self.template_manager.get_file_extension(target_language)
        
        setup_dir = self.project_root / self.config.setup_dir
        setup_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Generate utilities file
        utilities_path = self._generate_utilities_file(setup_dir, force_regenerate, target_language, extension)
        generated_files["utilities"] = utilities_path
        
        # Generate package init file (language-specific)
        init_path = self._generate_init_file(setup_dir, target_language, extension)
        generated_files["init"] = init_path
        
        # Generate framework-specific helpers if needed
        if self._framework_utilities:
            framework_path = self._generate_framework_helpers_file(setup_dir, force_regenerate, target_language, extension)
            generated_files["framework_helpers"] = framework_path
        
        # Generate constants file if needed
        constants_path = self._generate_constants_file(setup_dir, force_regenerate, target_language, extension)
        generated_files["constants"] = constants_path
        
        # Track generated files for this language
        if target_language not in self._generated_files:
            self._generated_files[target_language] = set()
        self._generated_files[target_language].update(generated_files.values())
        
        self._last_generation_time = datetime.now()
        return generated_files
    
    def get_imports_for_test_script(self, framework: str = None, language: str = None) -> List[str]:
        """
        Get the import statements needed for a test script using shared setup.
        
        Args:
            framework: Framework to generate imports for
            language: Target language (defaults to current language)
            
        Returns:
            List of import statements
        """
        target_language = language or self._current_language
        imports = []
        
        # Get language-specific import syntax
        template = self.template_manager.get_template(target_language)
        if not template:
            return imports
        
        # Always import from utilities
        if self._utilities:
            utility_names = list(self._utilities.keys())
            
            if target_language == "python":
                imports.append(f"from {self.config.setup_dir.name}.{self.config.utilities_file} import ({', '.join(utility_names)})")
            elif target_language in ["typescript", "javascript"]:
                imports.append(f"import {{ {', '.join(utility_names)} }} from './{self.config.utilities_file}';")
            elif target_language == "csharp":
                imports.append(f"using {self.config.setup_dir.name}.{self.config.utilities_file};")
            elif target_language == "java":
                imports.append(f"import {self.config.setup_dir.name}.{self.config.utilities_file}.*;")
        
        # Add framework-specific imports if available
        if framework and framework in self._framework_utilities:
            framework_utilities = self._framework_utilities[framework]
            if framework_utilities:
                if target_language == "python":
                    imports.append(f"from {self.config.setup_dir.name}.{self.config.framework_helpers_file} import ({', '.join(framework_utilities)})")
                elif target_language in ["typescript", "javascript"]:
                    imports.append(f"import {{ {', '.join(framework_utilities)} }} from './{self.config.framework_helpers_file}';")
                elif target_language == "csharp":
                    imports.append(f"using {self.config.setup_dir.name}.{self.config.framework_helpers_file};")
                elif target_language == "java":
                    imports.append(f"import {self.config.setup_dir.name}.{self.config.framework_helpers_file}.*;")
        
        return imports
    
    def _generate_utilities_file(self, setup_dir: Path, force_regenerate: bool, language: str, extension: str) -> Path:
        """Generate the main utilities file for the specified language."""
        utilities_path = setup_dir / f"{self.config.utilities_file}{extension}"
        
        if utilities_path.exists() and not force_regenerate:
            return utilities_path
        
        template = self.template_manager.get_template(language)
        if not template:
            raise ValueError(f"Unsupported language: {language}")
        
        lines = []
        
        # File header (language-specific)
        if language == "python":
            lines.extend([
                "#!/usr/bin/env python3",
                '"""',
                "Shared test utilities generated by browse-to-test.",
                "",
                "This file contains reusable helper functions, exception classes,",
                "and utilities that can be imported by test scripts.",
                '"""',
                ""
            ])
        elif language in ["typescript", "javascript"]:
            lines.extend([
                "/**",
                " * Shared test utilities generated by browse-to-test.",
                " *",
                " * This file contains reusable helper functions, exception classes,",
                " * and utilities that can be imported by test scripts.",
                " */",
                ""
            ])
        elif language == "csharp":
            lines.extend([
                "/// <summary>",
                "/// Shared test utilities generated by browse-to-test.",
                "/// </summary>",
                "",
                "using System;",
                "using System.Collections.Generic;",
                "using System.Threading.Tasks;",
                "",
                "namespace TestUtilities",
                "{",
                ""
            ])
        elif language == "java":
            lines.extend([
                "/**",
                " * Shared test utilities generated by browse-to-test.",
                " */",
                "",
                "import java.util.*;",
                "import java.util.concurrent.*;",
                "",
                "public class TestUtilities {",
                ""
            ])
        
        # Collect all imports for this language
        all_imports = set()
        for utility in self._utilities.values():
            imports = utility.get_imports_for_language(language)
            all_imports.update(imports)
        
        # Add imports (language-specific)
        if all_imports and language == "python":
            lines.extend(sorted(all_imports))
            lines.append("")
        elif all_imports and language in ["typescript", "javascript"]:
            lines.extend(sorted(all_imports))
            lines.append("")
        
        # Add utilities by category
        categories_used = set(u.category for u in self._utilities.values())
        
        for category in sorted(categories_used):
            if category in self._categories:
                comment_prefix = template.comment_prefix
                lines.extend([
                    f"{comment_prefix} {self._categories[category]}",
                    "",
                ])
            
            category_utilities = [u for u in self._utilities.values() if u.category == category]
            
            for utility in sorted(category_utilities, key=lambda x: x.name):
                if utility.description and self.config.include_docstrings:
                    lines.append(f"{template.comment_prefix} {utility.description}")
                
                # Get language-specific content
                content = utility.get_content_for_language(language)
                if content:
                    lines.extend(content.split('\n'))
                    lines.extend(["", ""])
        
        # Add language-specific file footer
        if language == "csharp":
            lines.append("}")
        elif language == "java":
            lines.append("}")
        
        # Write file
        utilities_path.write_text('\n'.join(lines))
        
        return utilities_path
    
    def _generate_init_file(self, setup_dir: Path, language: str, extension: str) -> Path:
        """Generate package initialization file for the setup package."""
        
        # Only generate init files for languages that support them
        if language == "python":
            init_path = setup_dir / "__init__.py"
            
            lines = [
                '"""',
                "Shared test setup package generated by browse-to-test.",
                '"""',
                "",
                "# Import all utilities for easy access",
            ]
            
            if self._utilities:
                utility_names = list(self._utilities.keys())
                lines.append(f"from .{self.config.utilities_file} import ({', '.join(utility_names)})")
            
            lines.extend([
                "",
                "__all__ = [",
            ])
            
            for utility_name in sorted(self._utilities.keys()):
                lines.append(f'    "{utility_name}",')
            
            lines.append("]")
            
            init_path.write_text('\n'.join(lines))
            return init_path
            
        elif language in ["typescript", "javascript"]:
            # Generate index file for TypeScript/JavaScript modules
            index_path = setup_dir / f"index{extension}"
            
            lines = [
                "/**",
                " * Shared test setup package generated by browse-to-test.",
                " */",
                ""
            ]
            
            if self._utilities:
                # Export all utilities
                utility_names = list(self._utilities.keys())
                lines.append(f"export {{ {', '.join(utility_names)} }} from './{self.config.utilities_file}';")
                
                # Add framework utilities if they exist
                if self._framework_utilities:
                    for framework, utilities in self._framework_utilities.items():
                        lines.append(f"export {{ {', '.join(utilities)} }} from './{self.config.framework_helpers_file}';")
            
            index_path.write_text('\n'.join(lines))
            return index_path
            
        elif language == "csharp":
            # Generate .csproj file for C# package
            csproj_path = setup_dir / "TestUtilities.csproj"
            
            lines = [
                '<Project Sdk="Microsoft.NET.Sdk">',
                '',
                '  <PropertyGroup>',
                '    <TargetFramework>net6.0</TargetFramework>',
                '    <AssemblyName>TestUtilities</AssemblyName>',
                '    <RootNamespace>TestUtilities</RootNamespace>',
                '  </PropertyGroup>',
                '',
                '  <ItemGroup>',
                '    <PackageReference Include="Microsoft.Playwright" Version="1.40.0" />',
                '  </ItemGroup>',
                '',
                '</Project>'
            ]
            
            csproj_path.write_text('\n'.join(lines))
            return csproj_path
            
        elif language == "java":
            # Generate pom.xml for Java package
            pom_path = setup_dir / "pom.xml"
            
            lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<project xmlns="http://maven.apache.org/POM/4.0.0"',
                '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                '         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">',
                '    <modelVersion>4.0.0</modelVersion>',
                '',
                '    <groupId>com.testutilities</groupId>',
                '    <artifactId>test-utilities</artifactId>',
                '    <version>1.0.0</version>',
                '',
                '    <properties>',
                '        <maven.compiler.source>11</maven.compiler.source>',
                '        <maven.compiler.target>11</maven.compiler.target>',
                '    </properties>',
                '',
                '    <dependencies>',
                '        <dependency>',
                '            <groupId>com.microsoft.playwright</groupId>',
                '            <artifactId>playwright</artifactId>',
                '            <version>1.40.0</version>',
                '        </dependency>',
                '    </dependencies>',
                '',
                '</project>'
            ]
            
            pom_path.write_text('\n'.join(lines))
            return pom_path
        
        # For unsupported languages, return a dummy path
        return setup_dir / f"package_info{extension}"
    
    def _generate_framework_helpers_file(self, setup_dir: Path, force_regenerate: bool, language: str, extension: str) -> Path:
        """Generate framework-specific helpers file."""
        helpers_path = setup_dir / f"{self.config.framework_helpers_file}{extension}"
        
        if helpers_path.exists() and not force_regenerate:
            return helpers_path
        
        template = self.template_manager.get_template(language)
        if not template:
            raise ValueError(f"Unsupported language: {language}")
        
        lines = []
        
        # File header (language-specific)
        if language == "python":
            lines.extend([
                "#!/usr/bin/env python3",
                '"""',
                "Framework-specific test helpers generated by browse-to-test.",
                '"""',
                ""
            ])
        elif language in ["typescript", "javascript"]:
            lines.extend([
                "/**",
                " * Framework-specific test helpers generated by browse-to-test.",
                " */",
                ""
            ])
        elif language == "csharp":
            lines.extend([
                "/// <summary>",
                "/// Framework-specific test helpers generated by browse-to-test.",
                "/// </summary>",
                "",
                "using System;",
                "using System.Threading.Tasks;",
                "",
                "namespace TestUtilities.FrameworkHelpers",
                "{",
                ""
            ])
        elif language == "java":
            lines.extend([
                "/**",
                " * Framework-specific test helpers generated by browse-to-test.",
                " */",
                "",
                "import java.util.concurrent.*;",
                "",
                "public class FrameworkHelpers {",
                ""
            ])
        
        # Group utilities by framework
        for framework, utility_names in self._framework_utilities.items():
            comment_prefix = template.comment_prefix
            lines.extend([
                f"{comment_prefix} {framework.title()} Helpers",
                "",
            ])
            
            framework_utilities = [u for u in self._utilities.values() 
                                 if u.framework == framework and u.name in utility_names]
            
            # Add framework imports for this language
            framework_imports = set()
            for utility in framework_utilities:
                imports = utility.get_imports_for_language(language)
                framework_imports.update(imports)
            
            if framework_imports and language == "python":
                lines.extend(sorted(framework_imports))
                lines.append("")
            elif framework_imports and language in ["typescript", "javascript"]:
                lines.extend(sorted(framework_imports))
                lines.append("")
            
            # Add framework utilities
            for utility in sorted(framework_utilities, key=lambda x: x.name):
                if utility.description:
                    lines.append(f"{comment_prefix} {utility.description}")
                
                # Get language-specific content
                content = utility.get_content_for_language(language)
                if content:
                    lines.extend(content.split('\n'))
                    lines.extend(["", ""])
        
        # Add language-specific file footer
        if language == "csharp":
            lines.append("}")
        elif language == "java":
            lines.append("}")
        
        helpers_path.write_text('\n'.join(lines))
        
        return helpers_path
    
    def _generate_constants_file(self, setup_dir: Path, force_regenerate: bool, language: str, extension: str) -> Path:
        """Generate constants file."""
        constants_path = setup_dir / f"{self.config.constants_file}{extension}"
        
        if constants_path.exists() and not force_regenerate:
            return constants_path
        
        lines = []
        
        # File header and constants (language-specific)
        if language == "python":
            lines.extend([
                "#!/usr/bin/env python3",
                '"""',
                "Test constants and configuration generated by browse-to-test.",
                '"""',
                "",
                "# Default timeouts",
                "DEFAULT_TIMEOUT = 30000",
                "ELEMENT_TIMEOUT = 10000",
                "PAGE_LOAD_TIMEOUT = 30000",
                "",
                "# Default browser options",
                "DEFAULT_BROWSER_OPTIONS = {",
                "    'headless': False,",
                "    'timeout': DEFAULT_TIMEOUT,",
                "}",
                "",
                "# Sensitive data placeholder", 
                "SENSITIVE_DATA = {}",
            ])
        elif language == "typescript":
            lines.extend([
                "/**",
                " * Test constants and configuration generated by browse-to-test.",
                " */",
                "",
                "// Default timeouts",
                "export const DEFAULT_TIMEOUT = 30000;",
                "export const ELEMENT_TIMEOUT = 10000;",
                "export const PAGE_LOAD_TIMEOUT = 30000;",
                "",
                "// Default browser options",
                "export const DEFAULT_BROWSER_OPTIONS = {",
                "    headless: false,",
                "    timeout: DEFAULT_TIMEOUT,",
                "};",
                "",
                "// Sensitive data placeholder",
                "export const SENSITIVE_DATA: Record<string, any> = {};",
            ])
        elif language == "javascript":
            lines.extend([
                "/**",
                " * Test constants and configuration generated by browse-to-test.",
                " */",
                "",
                "// Default timeouts",
                "export const DEFAULT_TIMEOUT = 30000;",
                "export const ELEMENT_TIMEOUT = 10000;",
                "export const PAGE_LOAD_TIMEOUT = 30000;",
                "",
                "// Default browser options",
                "export const DEFAULT_BROWSER_OPTIONS = {",
                "    headless: false,",
                "    timeout: DEFAULT_TIMEOUT,",
                "};",
                "",
                "// Sensitive data placeholder",
                "export const SENSITIVE_DATA = {};",
            ])
        elif language == "csharp":
            lines.extend([
                "/// <summary>",
                "/// Test constants and configuration generated by browse-to-test.",
                "/// </summary>",
                "",
                "using System.Collections.Generic;",
                "",
                "namespace TestUtilities",
                "{",
                "    public static class TestConstants",
                "    {",
                "        // Default timeouts",
                "        public const int DEFAULT_TIMEOUT = 30000;",
                "        public const int ELEMENT_TIMEOUT = 10000;",
                "        public const int PAGE_LOAD_TIMEOUT = 30000;",
                "",
                "        // Default browser options",
                "        public static readonly Dictionary<string, object> DEFAULT_BROWSER_OPTIONS = new()",
                "        {",
                "            { \"headless\", false },",
                "            { \"timeout\", DEFAULT_TIMEOUT }",
                "        };",
                "",
                "        // Sensitive data placeholder",
                "        public static readonly Dictionary<string, object> SENSITIVE_DATA = new();",
                "    }",
                "}",
            ])
        elif language == "java":
            lines.extend([
                "/**",
                " * Test constants and configuration generated by browse-to-test.",
                " */",
                "",
                "import java.util.HashMap;",
                "import java.util.Map;",
                "",
                "public class TestConstants {",
                "    // Default timeouts",
                "    public static final int DEFAULT_TIMEOUT = 30000;",
                "    public static final int ELEMENT_TIMEOUT = 10000;",
                "    public static final int PAGE_LOAD_TIMEOUT = 30000;",
                "",
                "    // Default browser options",
                "    public static final Map<String, Object> DEFAULT_BROWSER_OPTIONS = new HashMap<String, Object>() {{",
                "        put(\"headless\", false);",
                "        put(\"timeout\", DEFAULT_TIMEOUT);",
                "    }};",
                "",
                "    // Sensitive data placeholder",
                "    public static final Map<String, Object> SENSITIVE_DATA = new HashMap<>();",
                "}",
            ])
        
        constants_path.write_text('\n'.join(lines))
        
        return constants_path
    
    def get_setup_status(self) -> Dict[str, Any]:
        """Get status information about the setup manager."""
        return {
            "total_utilities": len(self._utilities),
            "utilities_by_category": {
                category: len([u for u in self._utilities.values() if u.category == category])
                for category in set(u.category for u in self._utilities.values())
            },
            "frameworks_supported": list(self._framework_utilities.keys()),
            "generated_files": len(self._generated_files),
            "last_generation": self._last_generation_time.isoformat() if self._last_generation_time else None,
            "setup_directory": str(self.config.setup_dir),
        } 