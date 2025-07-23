#!/usr/bin/env python3
"""
Context collector for gathering system and test information to enhance AI analysis.
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

from .config import Config


@dataclass
class TestFileInfo:
    """Information about an existing test file."""
    file_path: str
    framework: str
    language: str
    test_functions: List[str]
    selectors: List[str]
    actions: List[str]
    assertions: List[str]
    imports: List[str]
    last_modified: datetime
    size_bytes: int
    
    
@dataclass
class ProjectContext:
    """Overall project context information."""
    project_root: str
    name: Optional[str] = None
    description: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    test_frameworks: List[str] = field(default_factory=list)
    ui_frameworks: List[str] = field(default_factory=list)
    

@dataclass
class SystemContext:
    """Complete system context for AI analysis."""
    project: ProjectContext
    existing_tests: List[TestFileInfo] = field(default_factory=list)
    documentation: Dict[str, str] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    ui_components: Dict[str, Any] = field(default_factory=dict)
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    database_schema: Dict[str, Any] = field(default_factory=dict)
    recent_changes: List[Dict[str, Any]] = field(default_factory=list)
    common_patterns: Dict[str, List[str]] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)
    

class ContextCollector:
    """Collects and analyzes system context for enhanced test generation."""
    
    def __init__(self, config: Config, project_root: Optional[str] = None):
        self.config = config
        self.project_root = Path(project_root or os.getcwd())
        self._cache: Dict[str, SystemContext] = {}
        
        # File patterns for different types of content
        self.test_file_patterns = {
            'playwright': [r'.*\.spec\.(js|ts|py)$', r'.*test.*playwright.*\.py$'],
            'selenium': [r'.*test.*selenium.*\.py$', r'.*webdriver.*test.*\.py$'],
            'cypress': [r'.*\.cy\.(js|ts)$', r'cypress/.*\.spec\.(js|ts)$'],
            'jest': [r'.*\.(test|spec)\.(js|ts)$'],
            'pytest': [r'test_.*\.py$', r'.*_test\.py$'],
        }
        
        self.doc_file_patterns = [
            r'README\.md$', r'.*\.md$', r'docs/.*', r'documentation/.*',
            r'API\.md$', r'CONTRIBUTING\.md$', r'CHANGELOG\.md$'
        ]
        
        self.config_file_patterns = [
            r'package\.json$', r'requirements\.txt$', r'Pipfile$', r'pyproject\.toml$',
            r'playwright\.config\.(js|ts)$', r'jest\.config\.(js|ts)$',
            r'cypress\.config\.(js|ts)$', r'pytest\.ini$', r'setup\.cfg$',
            r'\.env.*$', r'config\.json$', r'settings\.py$'
        ]
        
    def collect_context(self, target_url: Optional[str] = None, force_refresh: bool = False) -> SystemContext:
        """
        Collect comprehensive system context.
        
        Args:
            target_url: URL being tested (helps filter relevant context)
            force_refresh: Whether to bypass cache and collect fresh context
            
        Returns:
            SystemContext containing all relevant information
        """
        cache_key = f"{self.project_root}_{target_url or 'default'}"
        
        if not force_refresh and cache_key in self._cache:
            cached_context = self._cache[cache_key]
            # Check if cache is still valid (within last hour)
            if (datetime.now() - cached_context.collected_at).seconds < 3600:
                return cached_context
        
        context = SystemContext(
            project=self._collect_project_info(),
            existing_tests=self._collect_existing_tests(),
            documentation=self._collect_documentation(),
            configuration=self._collect_configuration(),
            ui_components=self._collect_ui_components(),
            api_endpoints=self._collect_api_endpoints(),
            database_schema=self._collect_database_schema(),
            recent_changes=self._collect_recent_changes(),
            common_patterns=self._analyze_common_patterns(),
        )
        
        # Filter context based on target URL if provided
        if target_url:
            context = self._filter_context_by_url(context, target_url)
        
        self._cache[cache_key] = context
        return context
    
    def _collect_project_info(self) -> ProjectContext:
        """Collect basic project information."""
        project = ProjectContext(project_root=str(self.project_root))
        
        # Try to get project info from package.json
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    project.name = data.get('name')
                    project.description = data.get('description')
                    
                    # Extract dependencies
                    deps = {}
                    deps.update(data.get('dependencies', {}))
                    deps.update(data.get('devDependencies', {}))
                    project.dependencies = deps
                    
                    # Identify frameworks
                    project.tech_stack.extend(self._identify_frameworks_from_deps(deps))
                    
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Try to get info from setup.py or pyproject.toml for Python projects
        setup_py = self.project_root / 'setup.py'
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                # Simple regex extraction (could be improved)
                name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if name_match:
                    project.name = name_match.group(1)
                    
                desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
                if desc_match:
                    project.description = desc_match.group(1)
                    
            except FileNotFoundError:
                pass
        
        # Check requirements.txt for Python dependencies
        requirements = self.project_root / 'requirements.txt'
        if requirements.exists():
            try:
                content = requirements.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            name, version = line.split('==', 1)
                            project.dependencies[name] = version
                        else:
                            project.dependencies[line] = 'latest'
                            
                project.tech_stack.extend(self._identify_frameworks_from_deps(project.dependencies))
                            
            except FileNotFoundError:
                pass
        
        # Identify test frameworks
        project.test_frameworks = self._identify_test_frameworks()
        
        return project
    
    def _identify_frameworks_from_deps(self, dependencies: Dict[str, str]) -> List[str]:
        """Identify frameworks from dependency list."""
        frameworks = []
        framework_indicators = {
            'react': ['react', '@types/react'],
            'vue': ['vue', '@vue/'],
            'angular': ['@angular/', 'angular'],
            'express': ['express'],
            'fastapi': ['fastapi'],
            'django': ['django'],
            'flask': ['flask'],
            'playwright': ['playwright', '@playwright/test'],
            'selenium': ['selenium'],
            'cypress': ['cypress'],
            'jest': ['jest'],
            'pytest': ['pytest'],
        }
        
        for framework, indicators in framework_indicators.items():
            for dep in dependencies:
                if any(indicator in dep.lower() for indicator in indicators):
                    if framework not in frameworks:
                        frameworks.append(framework)
                    break
                    
        return frameworks
    
    def _identify_test_frameworks(self) -> List[str]:
        """Identify test frameworks used in the project."""
        frameworks = []
        
        # Check for specific test framework files/folders
        test_indicators = {
            'playwright': ['playwright.config.js', 'playwright.config.ts', 'tests/', 'e2e/'],
            'cypress': ['cypress.config.js', 'cypress.config.ts', 'cypress/'],
            'jest': ['jest.config.js', 'jest.config.ts', '__tests__/'],
            'pytest': ['pytest.ini', 'conftest.py', 'tests/'],
            'selenium': ['webdriver/', 'selenium/'],
        }
        
        for framework, indicators in test_indicators.items():
            for indicator in indicators:
                if (self.project_root / indicator).exists():
                    frameworks.append(framework)
                    break
                    
        return frameworks
    
    def _collect_existing_tests(self) -> List[TestFileInfo]:
        """Collect information about existing test files."""
        tests = []
        
        for framework, patterns in self.test_file_patterns.items():
            for pattern in patterns:
                for file_path in self._find_files_by_pattern(pattern):
                    try:
                        test_info = self._analyze_test_file(file_path, framework)
                        if test_info:
                            tests.append(test_info)
                    except Exception as e:
                        # Log but don't fail on individual file analysis errors
                        if self.config.debug:
                            print(f"Error analyzing test file {file_path}: {e}")
                        continue
                        
        return tests
    
    def _analyze_test_file(self, file_path: Path, framework: str) -> Optional[TestFileInfo]:
        """Analyze a single test file to extract useful information."""
        try:
            content = file_path.read_text(encoding='utf-8')
            stat = file_path.stat()
            
            # Determine language
            language = 'python' if file_path.suffix == '.py' else 'javascript'
            
            # Extract test functions
            test_functions = self._extract_test_functions(content, language)
            
            # Extract selectors
            selectors = self._extract_selectors(content)
            
            # Extract actions
            actions = self._extract_actions(content, framework)
            
            # Extract assertions
            assertions = self._extract_assertions(content, language)
            
            # Extract imports
            imports = self._extract_imports(content, language)
            
            return TestFileInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                framework=framework,
                language=language,
                test_functions=test_functions,
                selectors=selectors,
                actions=actions,
                assertions=assertions,
                imports=imports,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                size_bytes=stat.st_size
            )
            
        except Exception as e:
            if self.config.debug:
                print(f"Error reading test file {file_path}: {e}")
            return None
    
    def _extract_test_functions(self, content: str, language: str) -> List[str]:
        """Extract test function names from file content."""
        functions = []
        
        if language == 'python':
            # Python test functions
            patterns = [
                r'def (test_\w+)\(',
                r'def (test\w+)\(',
                r'async def (test_\w+)\(',
                r'async def (test\w+)\(',
            ]
        else:
            # JavaScript/TypeScript test functions
            patterns = [
                r'test\(["\']([^"\']+)["\']',
                r'it\(["\']([^"\']+)["\']',
                r'describe\(["\']([^"\']+)["\']',
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            functions.extend(matches)
            
        return functions
    
    def _extract_selectors(self, content: str) -> List[str]:
        """Extract CSS selectors and XPath expressions from test content."""
        selectors = []
        
        # CSS selectors
        css_patterns = [
            r'["\']([#.]\w+[^"\']*)["\']',  # CSS selectors starting with # or .
            r'getByRole\(["\']([^"\']+)["\']',  # Playwright role selectors
            r'getByTestId\(["\']([^"\']+)["\']',  # Test ID selectors
            r'getByText\(["\']([^"\']+)["\']',  # Text selectors
            r'querySelector\(["\']([^"\']+)["\']',  # querySelector calls
        ]
        
        # XPath patterns
        xpath_patterns = [
            r'["\']([^"\']*//[^"\']*)["\']',  # XPath expressions
        ]
        
        for pattern in css_patterns + xpath_patterns:
            matches = re.findall(pattern, content)
            selectors.extend(matches)
            
        return list(set(selectors))  # Remove duplicates
    
    def _extract_actions(self, content: str, framework: str) -> List[str]:
        """Extract test actions from content based on framework."""
        actions = []
        
        action_patterns = {
            'playwright': [
                r'\.click\(',
                r'\.fill\(',
                r'\.type\(',
                r'\.goto\(',
                r'\.waitFor\(',
                r'\.screenshot\(',
                r'\.select\(',
            ],
            'selenium': [
                r'\.click\(',
                r'\.send_keys\(',
                r'\.get\(',
                r'\.find_element\(',
                r'\.switch_to\.',
                r'\.execute_script\(',
            ],
            'cypress': [
                r'cy\.visit\(',
                r'cy\.click\(',
                r'cy\.type\(',
                r'cy\.get\(',
                r'cy\.wait\(',
                r'cy\.screenshot\(',
            ],
        }
        
        patterns = action_patterns.get(framework, [])
        for pattern in patterns:
            matches = re.findall(pattern, content)
            actions.extend([match.replace('.', '').replace('(', '') for match in matches])
            
        return list(set(actions))
    
    def _extract_assertions(self, content: str, language: str) -> List[str]:
        """Extract assertion patterns from test content."""
        assertions = []
        
        if language == 'python':
            patterns = [
                r'assert\s+([^;\n]+)',
                r'expect\([^)]+\)\.([^(;\n]+)',
                r'self\.assert\w+\(',
            ]
        else:
            patterns = [
                r'expect\([^)]+\)\.([^(;\n]+)',
                r'assert\.[^(]+\(',
                r'should\([^)]+\)',
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            assertions.extend(matches)
            
        return assertions
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements from file content."""
        imports = []
        
        if language == 'python':
            patterns = [
                r'from\s+([^\s]+)\s+import',
                r'import\s+([^\s\n]+)',
            ]
        else:
            patterns = [
                r'import\s+[^\'\"]*[\'\"']([^\'\"]+)[\'\"']',
                r'from\s+[\'\"']([^\'\"]+)[\'\"']',
                r'require\([\'\"']([^\'\"]+)[\'\"']\)',
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
            
        return imports
    
    def _collect_documentation(self) -> Dict[str, str]:
        """Collect documentation files and their content."""
        docs = {}
        
        for pattern in self.doc_file_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Limit doc content to avoid overwhelming AI
                    if len(content) > 5000:
                        content = content[:5000] + '...'
                    docs[str(file_path.relative_to(self.project_root))] = content
                except Exception:
                    continue
                    
        return docs
    
    def _collect_configuration(self) -> Dict[str, Any]:
        """Collect configuration files and settings."""
        config = {}
        
        for pattern in self.config_file_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Try to parse as JSON/YAML if applicable
                    if file_path.suffix in ['.json']:
                        try:
                            config[str(file_path.name)] = json.loads(content)
                            continue
                        except json.JSONDecodeError:
                            pass
                    
                    elif file_path.suffix in ['.yml', '.yaml']:
                        try:
                            config[str(file_path.name)] = yaml.safe_load(content)
                            continue
                        except yaml.YAMLError:
                            pass
                    
                    # Store as text if parsing fails
                    config[str(file_path.name)] = content[:2000] + ('...' if len(content) > 2000 else '')
                    
                except Exception:
                    continue
                    
        return config
    
    def _collect_ui_components(self) -> Dict[str, Any]:
        """Collect information about UI components and design systems."""
        components = {}
        
        # Look for component libraries and design system files
        component_patterns = [
            r'components/.*\.(js|ts|jsx|tsx|vue)$',
            r'src/components/.*\.(js|ts|jsx|tsx|vue)$',
            r'lib/.*\.(js|ts|jsx|tsx|vue)$',
            r'design-system/.*',
            r'storybook/.*',
        ]
        
        for pattern in component_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Extract component names and props
                    component_info = self._analyze_component_file(content, file_path.suffix)
                    if component_info:
                        components[str(file_path.relative_to(self.project_root))] = component_info
                        
                except Exception:
                    continue
                    
        return components
    
    def _analyze_component_file(self, content: str, file_extension: str) -> Optional[Dict[str, Any]]:
        """Analyze a component file to extract useful information."""
        info = {
            'component_names': [],
            'props': [],
            'events': [],
            'css_classes': [],
        }
        
        # Extract component names (React/Vue patterns)
        component_patterns = [
            r'export\s+(?:default\s+)?(?:class|function|const)\s+(\w+)',
            r'component\s*:\s*[\'\"'](\w+)[\'\"']',
        ]
        
        for pattern in component_patterns:
            matches = re.findall(pattern, content)
            info['component_names'].extend(matches)
        
        # Extract props (simplified)
        prop_patterns = [
            r'props\s*:\s*\{([^}]+)\}',
            r'interface\s+\w+Props\s*\{([^}]+)\}',
        ]
        
        for pattern in prop_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                # Extract individual prop names
                prop_names = re.findall(r'(\w+)\s*:', match)
                info['props'].extend(prop_names)
        
        # Extract CSS classes
        css_patterns = [
            r'className\s*=\s*[\'\"']([^\'\"']+)[\'\"']',
            r'class\s*=\s*[\'\"']([^\'\"']+)[\'\"']',
        ]
        
        for pattern in css_patterns:
            matches = re.findall(pattern, content)
            info['css_classes'].extend(matches)
        
        return info if any(info.values()) else None
    
    def _collect_api_endpoints(self) -> List[Dict[str, Any]]:
        """Collect API endpoint information from code and documentation."""
        endpoints = []
        
        # Look for API route definitions
        api_patterns = [
            r'routes/.*\.(js|ts|py)$',
            r'api/.*\.(js|ts|py)$',
            r'controllers/.*\.(js|ts|py)$',
            r'views\.py$',
            r'urls\.py$',
        ]
        
        for pattern in api_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_endpoints = self._extract_api_endpoints(content, file_path.suffix)
                    endpoints.extend(file_endpoints)
                except Exception:
                    continue
                    
        return endpoints
    
    def _extract_api_endpoints(self, content: str, file_extension: str) -> List[Dict[str, Any]]:
        """Extract API endpoint definitions from file content."""
        endpoints = []
        
        # Express.js style routes
        if file_extension in ['.js', '.ts']:
            patterns = [
                r'app\.(get|post|put|delete|patch)\([\'\"']([^\'\"']+)[\'\"']',
                r'router\.(get|post|put|delete|patch)\([\'\"']([^\'\"']+)[\'\"']',
            ]
        
        # Python Flask/FastAPI style routes
        elif file_extension == '.py':
            patterns = [
                r'@app\.route\([\'\"']([^\'\"']+)[\'\"'],\s*methods\s*=\s*\[[\'\"']([^\'\"']+)[\'\"']\]',
                r'@app\.(get|post|put|delete|patch)\([\'\"']([^\'\"']+)[\'\"']',
            ]
        else:
            return endpoints
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    method, path = match
                    endpoints.append({
                        'method': method.upper(),
                        'path': path,
                    })
                    
        return endpoints
    
    def _collect_database_schema(self) -> Dict[str, Any]:
        """Collect database schema information."""
        schema = {}
        
        # Look for database model files
        model_patterns = [
            r'models/.*\.py$',
            r'models\.py$',
            r'schema/.*\.(sql|py|js|ts)$',
            r'migrations/.*\.(sql|py|js|ts)$',
        ]
        
        for pattern in model_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_schema = self._extract_schema_info(content, file_path.suffix)
                    if file_schema:
                        schema[str(file_path.relative_to(self.project_root))] = file_schema
                except Exception:
                    continue
                    
        return schema
    
    def _extract_schema_info(self, content: str, file_extension: str) -> Optional[Dict[str, Any]]:
        """Extract database schema information from file content."""
        info = {
            'models': [],
            'fields': [],
            'relationships': [],
        }
        
        if file_extension == '.py':
            # Django/SQLAlchemy model patterns
            model_patterns = [
                r'class\s+(\w+)\s*\([^)]*Model[^)]*\)',
                r'class\s+(\w+)\s*\([^)]*Base[^)]*\)',
            ]
            
            for pattern in model_patterns:
                matches = re.findall(pattern, content)
                info['models'].extend(matches)
            
            # Field patterns
            field_patterns = [
                r'(\w+)\s*=\s*models\.\w+Field',
                r'(\w+)\s*=\s*Column\(',
            ]
            
            for pattern in field_patterns:
                matches = re.findall(pattern, content)
                info['fields'].extend(matches)
        
        return info if any(info.values()) else None
    
    def _collect_recent_changes(self) -> List[Dict[str, Any]]:
        """Collect information about recent changes (if git is available)."""
        changes = []
        
        try:
            import subprocess
            
            # Get recent commits
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            changes.append({
                                'commit': parts[0],
                                'message': parts[1],
                                'type': 'commit'
                            })
                            
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Git not available or error occurred
            pass
            
        return changes
    
    def _analyze_common_patterns(self) -> Dict[str, List[str]]:
        """Analyze common patterns across existing tests."""
        patterns = {
            'common_selectors': [],
            'common_actions': [],
            'common_assertions': [],
            'common_waits': [],
        }
        
        # This would be populated by analyzing the collected test files
        # For now, return empty patterns
        return patterns
    
    def _filter_context_by_url(self, context: SystemContext, target_url: str) -> SystemContext:
        """Filter context to be more relevant to the target URL."""
        # Extract domain and path information
        from urllib.parse import urlparse
        parsed_url = urlparse(target_url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Filter tests that might be related to this URL
        relevant_tests = []
        for test in context.existing_tests:
            test_content = self._get_test_file_content(test.file_path)
            if test_content and (domain in test_content or any(part in test_content for part in path.split('/') if part)):
                relevant_tests.append(test)
        
        # Create filtered context
        filtered_context = SystemContext(
            project=context.project,
            existing_tests=relevant_tests,
            documentation=context.documentation,  # Keep all docs for now
            configuration=context.configuration,
            ui_components=context.ui_components,
            api_endpoints=context.api_endpoints,
            database_schema=context.database_schema,
            recent_changes=context.recent_changes,
            common_patterns=context.common_patterns,
            collected_at=context.collected_at
        )
        
        return filtered_context
    
    def _get_test_file_content(self, file_path: str) -> Optional[str]:
        """Get content of a test file for analysis."""
        try:
            full_path = self.project_root / file_path
            return full_path.read_text(encoding='utf-8')
        except Exception:
            return None
    
    def _find_files_by_pattern(self, pattern: str) -> List[Path]:
        """Find files matching a regex pattern."""
        files = []
        compiled_pattern = re.compile(pattern)
        
        try:
            for root, dirs, filenames in os.walk(self.project_root):
                # Skip common non-relevant directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    relative_path = str(file_path.relative_to(self.project_root))
                    
                    if compiled_pattern.search(relative_path):
                        files.append(file_path)
                        
        except Exception as e:
            if self.config.debug:
                print(f"Error walking directory: {e}")
                
        return files
    
    def get_context_summary(self, context: SystemContext) -> str:
        """Generate a human-readable summary of the collected context."""
        summary = []
        
        summary.append(f"## Project: {context.project.name or 'Unknown'}")
        if context.project.description:
            summary.append(f"Description: {context.project.description}")
        
        if context.project.tech_stack:
            summary.append(f"Tech Stack: {', '.join(context.project.tech_stack)}")
        
        if context.project.test_frameworks:
            summary.append(f"Test Frameworks: {', '.join(context.project.test_frameworks)}")
        
        summary.append(f"\n## Existing Tests: {len(context.existing_tests)} files")
        if context.existing_tests:
            frameworks = set(test.framework for test in context.existing_tests)
            summary.append(f"Frameworks used: {', '.join(frameworks)}")
        
        if context.documentation:
            summary.append(f"\n## Documentation: {len(context.documentation)} files")
            
        if context.ui_components:
            summary.append(f"\n## UI Components: {len(context.ui_components)} files analyzed")
            
        if context.api_endpoints:
            summary.append(f"\n## API Endpoints: {len(context.api_endpoints)} found")
            
        return '\n'.join(summary) 