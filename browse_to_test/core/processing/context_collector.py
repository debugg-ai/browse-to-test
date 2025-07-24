#!/usr/bin/env python3
"""
Context collector for gathering system and test information to enhance AI analysis.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime

from ..configuration.config import Config


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
        
    def collect_context(self, target_url: Optional[str] = None, force_refresh: bool = False) -> SystemContext:
        """Collect comprehensive system context."""
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
        
        return project
    
    def _identify_frameworks_from_deps(self, dependencies: Dict[str, str]) -> List[str]:
        """Identify frameworks from dependency list."""
        frameworks = []
        framework_indicators = {
            'react': ['react', '@types/react'],
            'playwright': ['playwright', '@playwright/test'],
            'selenium': ['selenium'],
        }
        
        for framework, indicators in framework_indicators.items():
            for dep in dependencies:
                if any(indicator in dep.lower() for indicator in indicators):
                    if framework not in frameworks:
                        frameworks.append(framework)
                    break
                    
        return frameworks
    
    def _collect_existing_tests(self) -> List[TestFileInfo]:
        """Collect information about existing test files."""
        tests = []
        
        test_file_patterns = {
            'playwright': [r'.*\.spec\.(js|ts|py)$'],
            'selenium': [r'.*test.*selenium.*\.py$'],
        }
        
        for framework, patterns in test_file_patterns.items():
            for pattern in patterns:
                for file_path in self._find_files_by_pattern(pattern):
                    try:
                        test_info = self._analyze_test_file(file_path, framework)
                        if test_info:
                            tests.append(test_info)
                    except Exception:
                        continue
                        
        return tests
    
    def _analyze_test_file(self, file_path: Path, framework: str) -> Optional[TestFileInfo]:
        """Analyze a single test file to extract useful information."""
        try:
            content = file_path.read_text(encoding='utf-8')
            stat = file_path.stat()
            
            # Determine language
            language = 'python' if file_path.suffix == '.py' else 'javascript'
            
            return TestFileInfo(
                file_path=str(file_path.relative_to(self.project_root)),
                framework=framework,
                language=language,
                test_functions=[],
                selectors=[],
                actions=[],
                assertions=[],
                imports=[],
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                size_bytes=stat.st_size
            )
            
        except Exception:
            return None
    
    def _collect_documentation(self) -> Dict[str, str]:
        """Collect documentation files and their content."""
        docs = {}
        
        doc_patterns = [r'README\.md$', r'.*\.md$']
        
        for pattern in doc_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if len(content) > 5000:
                        content = content[:4997] + '...'
                    docs[str(file_path.relative_to(self.project_root))] = content
                except Exception:
                    continue
                    
        return docs
    
    def _collect_configuration(self) -> Dict[str, Any]:
        """Collect configuration files and settings."""
        config = {}
        
        config_patterns = [r'package\.json$', r'requirements\.txt$']
        
        for pattern in config_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    if file_path.suffix == '.json':
                        try:
                            config[str(file_path.name)] = json.loads(content)
                            continue
                        except json.JSONDecodeError:
                            pass
                    
                    config[str(file_path.name)] = content[:2000] + ('...' if len(content) > 2000 else '')
                    
                except Exception:
                    continue
                    
        return config
    
    def _collect_ui_components(self) -> Dict[str, Any]:
        """Collect information about UI components and design systems."""
        components = {}
        
        component_patterns = [r'components/.*\.(js|ts|jsx|tsx)$']
        
        for pattern in component_patterns:
            for file_path in self._find_files_by_pattern(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    components[str(file_path.relative_to(self.project_root))] = {"content": content[:1000]}
                except Exception:
                    continue
                    
        return components
    
    def _collect_api_endpoints(self) -> List[Dict[str, Any]]:
        """Collect API endpoint information from code and documentation."""
        endpoints = []
        return endpoints
    
    def _collect_database_schema(self) -> Dict[str, Any]:
        """Collect database schema information."""
        schema = {}
        return schema
    
    def _collect_recent_changes(self) -> List[Dict[str, Any]]:
        """Collect information about recent changes."""
        changes = []
        return changes
    
    def _analyze_common_patterns(self) -> Dict[str, List[str]]:
        """Analyze common patterns across existing tests."""
        patterns = {
            'common_selectors': [],
            'common_actions': [],
            'common_assertions': [],
            'common_waits': [],
        }
        return patterns
    
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
                        
        except Exception:
            pass
                
        return files
    
    def get_context_summary(self, context: SystemContext) -> str:
        """Generate a human-readable summary of the collected context."""
        summary = []
        
        summary.append(f"## Project: {context.project.name or 'Unknown'}")
        if context.project.description:
            summary.append(f"Description: {context.project.description}")
        
        summary.append(f"\n## Existing Tests: {len(context.existing_tests)} files")
        
        return '\n'.join(summary) 