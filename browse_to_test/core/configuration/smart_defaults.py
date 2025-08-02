#!/usr/bin/env python3
"""
Smart defaults system for browse-to-test configuration.

This module implements intelligent default values that adapt based on:
- Environment detection
- Framework capabilities  
- Language conventions
- Performance optimization
- User context
"""

import os
import platform
from typing import Dict, Any, Optional, List
from pathlib import Path


class SmartDefaults:
    """
    Intelligent default configuration generator.
    
    Provides context-aware defaults that reduce configuration burden
    while maintaining optimal performance and compatibility.
    """
    
    @staticmethod
    def get_framework_defaults(framework: str) -> Dict[str, Any]:
        """
        Get framework-specific intelligent defaults.
        
        Args:
            framework: Target testing framework
            
        Returns:
            Dictionary of optimized defaults for the framework
        """
        defaults = {
            "playwright": {
                # Playwright-specific optimizations
                "include_waits": True,
                "include_error_handling": True,
                "test_timeout_seconds": 30,
                "browser_options": {
                    "headless": True,
                    "viewport": {"width": 1280, "height": 720}
                },
                "supports_screenshots": True,
                "supports_video": True,
                "supports_tracing": True,
                "recommended_selectors": ["data-testid", "css", "xpath"],
                "async_by_default": True
            },
            "selenium": {
                # Selenium-specific optimizations
                "include_waits": True,
                "include_error_handling": True,
                "test_timeout_seconds": 45,  # Selenium typically slower
                "browser_options": {
                    "headless": True,
                    "window_size": "1280,720"
                },
                "supports_screenshots": True,
                "supports_video": False,
                "supports_tracing": False,
                "recommended_selectors": ["id", "css", "xpath"],
                "async_by_default": False
            },
            "cypress": {
                # Cypress-specific optimizations
                "include_waits": False,  # Cypress handles waits automatically
                "include_error_handling": True,
                "test_timeout_seconds": 60,  # Cypress has built-in retries
                "browser_options": {
                    "headless": True,
                    "viewport": [1280, 720]
                },
                "supports_screenshots": True,
                "supports_video": True,
                "supports_tracing": False,
                "recommended_selectors": ["data-cy", "css"],
                "async_by_default": False
            },
            "puppeteer": {
                # Puppeteer-specific optimizations
                "include_waits": True,
                "include_error_handling": True,
                "test_timeout_seconds": 30,
                "browser_options": {
                    "headless": True,
                    "defaultViewport": {"width": 1280, "height": 720}
                },
                "supports_screenshots": True,
                "supports_video": False,
                "supports_tracing": True,
                "recommended_selectors": ["css", "xpath"],
                "async_by_default": True
            }
        }
        
        return defaults.get(framework, {})
    
    @staticmethod
    def get_language_defaults(language: str) -> Dict[str, Any]:
        """
        Get language-specific intelligent defaults.
        
        Args:
            language: Target programming language
            
        Returns:
            Dictionary of language-optimized defaults
        """
        defaults = {
            "python": {
                "file_extension": ".py",
                "comment_style": "#",
                "import_style": "from_import",
                "async_syntax": "async def",
                "supports_type_hints": True,
                "supports_docstrings": True,
                "test_framework_conventions": {
                    "pytest": {"file_prefix": "test_", "class_prefix": "Test"},
                    "unittest": {"file_prefix": "test_", "class_prefix": "Test"},
                    "nose": {"file_prefix": "test_", "class_prefix": "Test"}
                },
                "recommended_formatter": "black",
                "recommended_linter": "flake8"
            },
            "typescript": {
                "file_extension": ".ts",
                "comment_style": "//",
                "import_style": "es6",
                "async_syntax": "async function",
                "supports_type_hints": True,
                "supports_docstrings": False,
                "test_framework_conventions": {
                    "jest": {"file_suffix": ".test.ts", "describe_it": True},
                    "mocha": {"file_suffix": ".spec.ts", "describe_it": True}
                },
                "recommended_formatter": "prettier",
                "recommended_linter": "eslint"
            },
            "javascript": {
                "file_extension": ".js",
                "comment_style": "//", 
                "import_style": "es6",
                "async_syntax": "async function",
                "supports_type_hints": False,
                "supports_docstrings": False,
                "test_framework_conventions": {
                    "jest": {"file_suffix": ".test.js", "describe_it": True},
                    "mocha": {"file_suffix": ".spec.js", "describe_it": True}
                },
                "recommended_formatter": "prettier",
                "recommended_linter": "eslint"
            },
            "csharp": {
                "file_extension": ".cs",
                "comment_style": "//",
                "import_style": "using",
                "async_syntax": "public async Task",
                "supports_type_hints": True,
                "supports_docstrings": True,
                "test_framework_conventions": {
                    "xunit": {"class_suffix": "Tests", "fact_theory": True},
                    "nunit": {"class_suffix": "Tests", "test_attribute": True},
                    "mstest": {"class_suffix": "Tests", "test_method": True}
                },
                "recommended_formatter": "dotnet format",
                "recommended_linter": "roslyn"
            },
            "java": {
                "file_extension": ".java",
                "comment_style": "//",
                "import_style": "import",
                "async_syntax": "public CompletableFuture<Void>",
                "supports_type_hints": True,
                "supports_docstrings": True,
                "test_framework_conventions": {
                    "junit5": {"class_suffix": "Test", "annotations": True},
                    "junit4": {"class_suffix": "Test", "annotations": True},
                    "testng": {"class_suffix": "Test", "annotations": True}
                },
                "recommended_formatter": "google-java-format",
                "recommended_linter": "checkstyle"
            }
        }
        
        return defaults.get(language, {})
    
    @staticmethod
    def get_ai_provider_defaults(provider: str) -> Dict[str, Any]:
        """
        Get AI provider-specific intelligent defaults.
        
        Args:
            provider: AI provider name
            
        Returns:
            Dictionary of provider-optimized defaults
        """
        defaults = {
            "openai": {
                "default_model": "gpt-4",
                "fast_model": "gpt-3.5-turbo",
                "accurate_model": "gpt-4",
                "max_tokens": 4000,
                "temperature": 0.1,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "rate_limit_rpm": 3500,  # Requests per minute
                "cost_per_1k_tokens": 0.03,
                "recommended_for": ["general", "code_generation", "analysis"]
            },
            "anthropic": {
                "default_model": "claude-3-sonnet-20240229",
                "fast_model": "claude-3-haiku-20240307",
                "accurate_model": "claude-3-opus-20240229",
                "max_tokens": 4000,
                "temperature": 0.1,
                "supports_function_calling": True,
                "supports_json_mode": False,
                "rate_limit_rpm": 1000,
                "cost_per_1k_tokens": 0.015,
                "recommended_for": ["analysis", "complex_reasoning", "code_review"]
            },
            "azure": {
                "default_model": "gpt-4",
                "fast_model": "gpt-35-turbo",
                "accurate_model": "gpt-4-32k",
                "max_tokens": 4000,
                "temperature": 0.1,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "rate_limit_rpm": 1000,  # Varies by subscription
                "cost_per_1k_tokens": 0.03,
                "recommended_for": ["enterprise", "compliance", "data_residency"]
            },
            "google": {
                "default_model": "gemini-pro",
                "fast_model": "gemini-pro",
                "accurate_model": "gemini-pro",
                "max_tokens": 2048,
                "temperature": 0.1,
                "supports_function_calling": True,
                "supports_json_mode": False,
                "rate_limit_rpm": 300,
                "cost_per_1k_tokens": 0.0005,
                "recommended_for": ["cost_sensitive", "multimodal", "experimental"]
            }
        }
        
        return defaults.get(provider, {})
    
    @staticmethod
    def get_environment_defaults() -> Dict[str, Any]:
        """
        Get environment-specific intelligent defaults.
        
        Returns:
            Dictionary of environment-optimized defaults
        """
        system = platform.system().lower()
        is_ci = SmartDefaults._is_ci_environment()
        is_docker = SmartDefaults._is_docker_environment()
        has_display = SmartDefaults._has_display()
        
        defaults = {
            "platform": system,
            "is_ci": is_ci,
            "is_docker": is_docker,
            "has_display": has_display,
            "headless": is_ci or is_docker or not has_display,
            "parallel_execution": not is_ci,  # CI environments often control parallelism
            "max_workers": SmartDefaults._get_optimal_worker_count(),
            "browser_options": SmartDefaults._get_browser_options_for_environment(),
            "timeout_multiplier": 2.0 if is_ci else 1.0,  # CI environments need longer timeouts
            "retry_attempts": 3 if is_ci else 1,
            "enable_logging": is_ci or os.getenv("DEBUG", "").lower() == "true",
            "enable_screenshots_on_failure": True,
            "enable_video_recording": False,  # Disabled by default for performance
        }
        
        return defaults
    
    @staticmethod
    def get_performance_defaults(preset: str = "balanced") -> Dict[str, Any]:
        """
        Get performance-optimized defaults based on preset.
        
        Args:
            preset: Performance preset ("fast", "balanced", "accurate")
            
        Returns:
            Dictionary of performance-tuned defaults
        """
        presets = {
            "fast": {
                "ai_model_tier": "fast",
                "max_tokens": 2000,
                "temperature": 0.0,
                "enable_context_collection": False,
                "enable_ai_analysis": False,
                "context_analysis_depth": "shallow",
                "max_context_files": 20,
                "cache_ai_responses": True,
                "max_cache_size": 500,
                "parallel_ai_requests": True,
                "include_logging": False,
                "include_screenshots": False,
                "estimated_time_seconds": 10
            },
            "balanced": {
                "ai_model_tier": "default",
                "max_tokens": 4000,
                "temperature": 0.1,
                "enable_context_collection": True,
                "enable_ai_analysis": True,
                "context_analysis_depth": "medium",
                "max_context_files": 100,
                "cache_ai_responses": True,
                "max_cache_size": 1000,
                "parallel_ai_requests": True,
                "include_logging": False,
                "include_screenshots": False,
                "estimated_time_seconds": 30
            },
            "accurate": {
                "ai_model_tier": "accurate",
                "max_tokens": 8000,
                "temperature": 0.05,
                "enable_context_collection": True,
                "enable_ai_analysis": True,
                "context_analysis_depth": "deep",
                "max_context_files": 200,
                "cache_ai_responses": True,
                "max_cache_size": 2000,
                "parallel_ai_requests": False,  # Sequential for consistency
                "include_logging": True,
                "include_screenshots": True,
                "estimated_time_seconds": 90
            }
        }
        
        return presets.get(preset, presets["balanced"])
    
    @staticmethod
    def get_project_context_defaults(project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get project-specific intelligent defaults by analyzing project structure.
        
        Args:
            project_root: Root directory of the project
            
        Returns:
            Dictionary of project-optimized defaults
        """
        if not project_root:
            project_root = Path.cwd()
        
        project_root = Path(project_root)
        
        # Detect project characteristics
        package_json = project_root / "package.json"
        requirements_txt = project_root / "requirements.txt"
        pyproject_toml = project_root / "pyproject.toml"
        composer_json = project_root / "composer.json"
        pom_xml = project_root / "pom.xml"
        
        project_type = "unknown"
        if package_json.exists():
            project_type = "nodejs"
        elif requirements_txt.exists() or pyproject_toml.exists():
            project_type = "python"
        elif composer_json.exists():
            project_type = "php"
        elif pom_xml.exists():
            project_type = "java"
        
        # Detect testing frameworks
        testing_frameworks = SmartDefaults._detect_testing_frameworks(project_root)
        
        # Detect CI/CD systems
        ci_systems = SmartDefaults._detect_ci_systems(project_root)
        
        defaults = {
            "project_type": project_type,
            "project_root": str(project_root),
            "testing_frameworks": testing_frameworks,
            "ci_systems": ci_systems,
            "has_existing_tests": len(list(project_root.glob("**/test*.py")))
                                 + len(list(project_root.glob("**/*.test.js")))
                                 + len(list(project_root.glob("**/*.spec.ts"))) > 0,
            "recommended_output_dir": SmartDefaults._get_recommended_output_dir(project_root, project_type),
            "sensitive_patterns": SmartDefaults._get_sensitive_patterns(project_type),
        }
        
        return defaults
    
    # Helper methods
    
    @staticmethod
    def _is_ci_environment() -> bool:
        """Check if running in CI environment."""
        ci_vars = [
            "CI", "CONTINUOUS_INTEGRATION", "BUILD_NUMBER", 
            "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL",
            "TRAVIS", "CIRCLECI", "AZURE_PIPELINES"
        ]
        return any(var in os.environ for var in ci_vars)
    
    @staticmethod
    def _is_docker_environment() -> bool:
        """Check if running in Docker container."""
        if os.path.exists("/.dockerenv"):
            return True
        if os.path.exists("/proc/1/cgroup"):
            with open("/proc/1/cgroup") as f:
                return "docker" in f.read()
        return False
    
    @staticmethod
    def _has_display() -> bool:
        """Check if display is available."""
        return "DISPLAY" in os.environ or platform.system() == "Windows"
    
    @staticmethod
    def _get_optimal_worker_count() -> int:
        """Get optimal number of parallel workers."""
        cpu_count = os.cpu_count() or 1
        # Conservative approach: use half of available CPUs, min 1, max 4 for test generation
        return max(1, min(4, cpu_count // 2))
    
    @staticmethod
    def _get_browser_options_for_environment() -> Dict[str, Any]:
        """Get browser options optimized for current environment."""
        is_ci = SmartDefaults._is_ci_environment()
        is_docker = SmartDefaults._is_docker_environment()
        system = platform.system().lower()
        
        options = {
            "headless": is_ci or is_docker,
            "no_sandbox": is_docker,  # Required for Docker
            "disable_dev_shm_usage": is_docker,  # Prevents /dev/shm issues
        }
        
        if system == "linux":
            options.update({
                "disable_gpu": True,
                "disable_software_rasterizer": True
            })
        
        return options
    
    @staticmethod
    def _detect_testing_frameworks(project_root: Path) -> List[str]:
        """Detect testing frameworks in project."""
        frameworks = []
        
        # Check package.json for JS/TS frameworks
        package_json = project_root / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    
                    if "jest" in deps:
                        frameworks.append("jest")
                    if "cypress" in deps:
                        frameworks.append("cypress")
                    if "playwright" in deps:
                        frameworks.append("playwright")
                    if "mocha" in deps:
                        frameworks.append("mocha")
            except (json.JSONDecodeError, OSError, IOError):
                pass
        
        # Check Python files for testing frameworks
        if any(project_root.glob("**/test_*.py")) or any(project_root.glob("**/*_test.py")):
            frameworks.append("pytest")
        
        return frameworks
    
    @staticmethod
    def _detect_ci_systems(project_root: Path) -> List[str]:
        """Detect CI/CD systems in project."""
        ci_systems = []
        
        if (project_root / ".github" / "workflows").exists():
            ci_systems.append("github_actions")
        if (project_root / ".gitlab-ci.yml").exists():
            ci_systems.append("gitlab_ci")
        if (project_root / "Jenkinsfile").exists():
            ci_systems.append("jenkins")
        if (project_root / ".travis.yml").exists():
            ci_systems.append("travis")
        if (project_root / ".circleci").exists():
            ci_systems.append("circleci")
        
        return ci_systems
    
    @staticmethod
    def _get_recommended_output_dir(project_root: Path, project_type: str) -> str:
        """Get recommended output directory for generated tests."""
        conventions = {
            "nodejs": "tests/generated",
            "python": "tests/generated", 
            "java": "src/test/generated",
            "php": "tests/generated"
        }
        return conventions.get(project_type, "tests/generated")
    
    @staticmethod
    def _get_sensitive_patterns(project_type: str) -> List[str]:
        """Get patterns for sensitive data detection."""
        common_patterns = ["password", "secret", "token", "key", "api_key"]
        
        type_specific = {
            "nodejs": ["env", "process.env"],
            "python": ["os.environ", "getenv"],
            "java": ["System.getProperty", "System.getenv"],
            "php": ["$_ENV", "getenv"]
        }
        
        return common_patterns + type_specific.get(project_type, [])