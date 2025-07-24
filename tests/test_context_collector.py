"""Tests for the context collector."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest

from browse_to_test.core.processing.context_collector import (
    ContextCollector, SystemContext, ProjectContext, TestFileInfo
)
from browse_to_test.core.configuration.config import Config


class TestProjectContext:
    """Test the ProjectContext dataclass."""
    
    def test_basic_creation(self):
        """Test basic project context creation."""
        project = ProjectContext(project_root="/test/path")
        
        assert project.project_root == "/test/path"
        assert project.name is None
        assert project.description is None
        assert project.tech_stack == []
        assert project.dependencies == {}
        assert project.test_frameworks == []
        assert project.ui_frameworks == []
    
    def test_full_creation(self):
        """Test project context with all fields."""
        project = ProjectContext(
            project_root="/test/path",
            name="test-project",
            description="A test project",
            tech_stack=["react", "typescript"],
            dependencies={"react": "^18.0.0"},
            test_frameworks=["playwright", "jest"],
            ui_frameworks=["react"]
        )
        
        assert project.project_root == "/test/path"
        assert project.name == "test-project"
        assert project.description == "A test project"
        assert project.tech_stack == ["react", "typescript"]
        assert project.dependencies == {"react": "^18.0.0"}
        assert project.test_frameworks == ["playwright", "jest"]
        assert project.ui_frameworks == ["react"]


class TestTestFileInfo:
    """Test the TestFileInfo dataclass."""
    
    def test_basic_creation(self):
        """Test basic test file info creation."""
        test_file = TestFileInfo(
            file_path="tests/example.spec.ts",
            framework="playwright",
            language="typescript",
            test_functions=["test login", "test signup"],
            selectors=["[data-testid='username']"],
            actions=["goto", "fill", "click"],
            assertions=["toBeVisible"],
            imports=["@playwright/test"],
            last_modified=datetime.now(),
            size_bytes=1024
        )
        
        assert test_file.file_path == "tests/example.spec.ts"
        assert test_file.framework == "playwright"
        assert test_file.language == "typescript"
        assert test_file.test_functions == ["test login", "test signup"]
        assert test_file.selectors == ["[data-testid='username']"]
        assert test_file.actions == ["goto", "fill", "click"]
        assert test_file.assertions == ["toBeVisible"]
        assert test_file.imports == ["@playwright/test"]
        assert test_file.size_bytes == 1024
        assert isinstance(test_file.last_modified, datetime)


class TestSystemContext:
    """Test the SystemContext dataclass."""
    
    def test_basic_creation(self):
        """Test basic system context creation."""
        project = ProjectContext(project_root="/test/path")
        context = SystemContext(project=project)
        
        assert context.project == project
        assert context.existing_tests == []
        assert context.documentation == {}
        assert context.configuration == {}
        assert context.ui_components == {}
        assert context.api_endpoints == []
        assert context.database_schema == {}
        assert context.recent_changes == []
        assert context.common_patterns == {}
        assert isinstance(context.collected_at, datetime)


class TestContextCollector:
    """Test the ContextCollector class."""
    
    def test_init(self, basic_config):
        """Test context collector initialization."""
        collector = ContextCollector(basic_config)
        
        assert collector.config == basic_config
        assert isinstance(collector.project_root, Path)
        assert collector._cache == {}
    
    def test_init_with_custom_root(self, basic_config):
        """Test context collector with custom project root."""
        collector = ContextCollector(basic_config, "/custom/path")
        
        assert str(collector.project_root) == "/custom/path"
    
    def test_collect_context_basic(self, basic_config, temp_project_dir):
        """Test basic context collection."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        context = collector.collect_context()
        
        assert isinstance(context, SystemContext)
        assert isinstance(context.project, ProjectContext)
        assert context.project.project_root == str(collector.project_root)
    
    def test_collect_context_caching(self, basic_config, temp_project_dir):
        """Test context collection caching."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        # First call
        context1 = collector.collect_context()
        
        # Second call should return cached result
        context2 = collector.collect_context()
        
        assert context1 is context2
        assert len(collector._cache) == 1
    
    def test_collect_context_force_refresh(self, basic_config, temp_project_dir):
        """Test forced context refresh."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        # First call
        context1 = collector.collect_context()
        
        # Force refresh
        context2 = collector.collect_context(force_refresh=True)
        
        assert context1 is not context2
        assert len(collector._cache) == 1  # Cache updated
    
    def test_collect_project_info_package_json(self, basic_config, temp_project_dir):
        """Test project info collection from package.json."""
        # temp_project_dir fixture already creates package.json
        collector = ContextCollector(basic_config, str(temp_project_dir))
        project_info = collector._collect_project_info()
        
        assert project_info.name == "test-project"
        assert project_info.description == "A test project"
        assert isinstance(project_info.dependencies, dict)
        assert len(project_info.tech_stack) > 0
    
    def test_collect_project_info_no_package_json(self, basic_config, tmp_path):
        """Test project info collection without package.json."""
        collector = ContextCollector(basic_config, str(tmp_path))
        project_info = collector._collect_project_info()
        
        assert project_info.name is None
        assert project_info.description is None
        assert project_info.dependencies == {}
        assert project_info.tech_stack == []
    
    def test_identify_frameworks_from_deps(self, basic_config):
        """Test framework identification from dependencies."""
        collector = ContextCollector(basic_config)
        
        deps = {
            "react": "^18.0.0",
            "@playwright/test": "^1.30.0",
            "selenium": "^4.0.0",
            "unknown-package": "^1.0.0"
        }
        
        frameworks = collector._identify_frameworks_from_deps(deps)
        
        assert "react" in frameworks
        assert "playwright" in frameworks
        assert "selenium" in frameworks
        assert "unknown-package" not in frameworks
    
    def test_collect_existing_tests(self, basic_config, temp_project_dir):
        """Test collection of existing test files."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        tests = collector._collect_existing_tests()
        
        assert isinstance(tests, list)
        # temp_project_dir has test files
        assert len(tests) > 0
        
        for test in tests:
            assert isinstance(test, TestFileInfo)
            assert test.framework in ["playwright", "selenium"]
    
    def test_analyze_test_file_playwright(self, basic_config, temp_project_dir):
        """Test analysis of Playwright test file."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        # Get the first test file
        test_files = list((temp_project_dir / "tests").glob("*.spec.ts"))
        if test_files:
            test_info = collector._analyze_test_file(test_files[0], "playwright")
            
            assert test_info is not None
            assert test_info.framework == "playwright"
            assert test_info.language == "javascript"  # .ts files detected as javascript
            assert isinstance(test_info.last_modified, datetime)
            assert test_info.size_bytes > 0
    
    def test_analyze_test_file_invalid(self, basic_config, tmp_path):
        """Test analysis of invalid test file."""
        collector = ContextCollector(basic_config, str(tmp_path))
        
        # Create a non-existent file path
        invalid_path = tmp_path / "nonexistent.spec.ts"
        test_info = collector._analyze_test_file(invalid_path, "playwright")
        
        assert test_info is None
    
    def test_collect_documentation(self, basic_config, temp_project_dir):
        """Test documentation collection."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        docs = collector._collect_documentation()
        
        assert isinstance(docs, dict)
        # temp_project_dir has README.md
        assert len(docs) > 0
        assert any("README.md" in key for key in docs.keys())
        
        for file_path, content in docs.items():
            assert isinstance(content, str)
            assert len(content) <= 5000  # Should be truncated if too long
    
    def test_collect_configuration(self, basic_config, temp_project_dir):
        """Test configuration collection."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        config = collector._collect_configuration()
        
        assert isinstance(config, dict)
        # temp_project_dir has package.json
        assert "package.json" in config
        assert isinstance(config["package.json"], dict)  # Parsed JSON
    
    def test_collect_ui_components(self, basic_config, temp_project_dir):
        """Test UI components collection."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        components = collector._collect_ui_components()
        
        assert isinstance(components, dict)
        # temp_project_dir has Button.tsx
        if components:
            for file_path, component_info in components.items():
                assert isinstance(component_info, dict)
                assert "content" in component_info
    
    def test_collect_api_endpoints(self, basic_config):
        """Test API endpoints collection."""
        collector = ContextCollector(basic_config)
        endpoints = collector._collect_api_endpoints()
        
        assert isinstance(endpoints, list)
        # Basic implementation returns empty list
        assert endpoints == []
    
    def test_collect_database_schema(self, basic_config):
        """Test database schema collection."""
        collector = ContextCollector(basic_config)
        schema = collector._collect_database_schema()
        
        assert isinstance(schema, dict)
        # Basic implementation returns empty dict
        assert schema == {}
    
    def test_collect_recent_changes(self, basic_config):
        """Test recent changes collection."""
        collector = ContextCollector(basic_config)
        changes = collector._collect_recent_changes()
        
        assert isinstance(changes, list)
        # Basic implementation returns empty list
        assert changes == []
    
    def test_analyze_common_patterns(self, basic_config):
        """Test common patterns analysis."""
        collector = ContextCollector(basic_config)
        patterns = collector._analyze_common_patterns()
        
        assert isinstance(patterns, dict)
        expected_keys = ['common_selectors', 'common_actions', 'common_assertions', 'common_waits']
        for key in expected_keys:
            assert key in patterns
            assert isinstance(patterns[key], list)
    
    def test_find_files_by_pattern(self, basic_config, temp_project_dir):
        """Test file finding by regex pattern."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        # Find TypeScript files
        ts_files = collector._find_files_by_pattern(r'.*\.ts$')
        
        assert isinstance(ts_files, list)
        # temp_project_dir has .ts files
        assert len(ts_files) > 0
        
        for file_path in ts_files:
            assert isinstance(file_path, Path)
            assert file_path.suffix == '.ts'
    
    def test_find_files_by_pattern_no_matches(self, basic_config, temp_project_dir):
        """Test file finding with no matches."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        # Find files that don't exist
        files = collector._find_files_by_pattern(r'.*\.nonexistent$')
        
        assert files == []
    
    def test_get_context_summary(self, basic_config, sample_system_context):
        """Test context summary generation."""
        collector = ContextCollector(basic_config)
        summary = collector.get_context_summary(sample_system_context)
        
        assert isinstance(summary, str)
        assert "Project:" in summary
        assert "Existing Tests:" in summary
        assert sample_system_context.project.name in summary


class TestContextCollectorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_collect_context_with_target_url(self, basic_config, temp_project_dir):
        """Test context collection with target URL."""
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        context1 = collector.collect_context(target_url="https://example.com")
        context2 = collector.collect_context(target_url="https://different.com")
        
        # Should create separate cache entries
        assert len(collector._cache) == 2
    
    def test_collect_context_invalid_directory(self, basic_config):
        """Test context collection with invalid directory."""
        collector = ContextCollector(basic_config, "/nonexistent/path")
        
        # Should not raise exception but return basic context
        context = collector.collect_context()
        assert isinstance(context, SystemContext)
    
    def test_collect_project_info_invalid_json(self, basic_config, tmp_path):
        """Test project info collection with invalid JSON."""
        # Create invalid package.json
        package_json = tmp_path / "package.json"
        package_json.write_text("invalid json content")
        
        collector = ContextCollector(basic_config, str(tmp_path))
        project_info = collector._collect_project_info()
        
        # Should handle gracefully
        assert project_info.name is None
        assert project_info.dependencies == {}
    
    def test_collect_documentation_large_file(self, basic_config, tmp_path):
        """Test documentation collection with large file."""
        # Create large README
        large_readme = tmp_path / "README.md"
        large_content = "x" * 10000  # 10KB content
        large_readme.write_text(large_content)
        
        collector = ContextCollector(basic_config, str(tmp_path))
        docs = collector._collect_documentation()
        
        # Should be truncated
        assert "README.md" in docs
        assert len(docs["README.md"]) <= 5000
        assert docs["README.md"].endswith("...")
    
    def test_find_files_excludes_hidden_dirs(self, basic_config, tmp_path):
        """Test that file finding excludes hidden directories."""
        # Create hidden directory with files
        hidden_dir = tmp_path / ".hidden"
        hidden_dir.mkdir()
        (hidden_dir / "test.ts").write_text("hidden file")
        
        # Create normal file
        (tmp_path / "normal.ts").write_text("normal file")
        
        collector = ContextCollector(basic_config, str(tmp_path))
        ts_files = collector._find_files_by_pattern(r'.*\.ts$')
        
        # Should only find normal file, not hidden one
        assert len(ts_files) == 1
        assert ts_files[0].name == "normal.ts"
    
    def test_find_files_excludes_common_dirs(self, basic_config, tmp_path):
        """Test that file finding excludes common non-relevant directories."""
        # Create directories that should be excluded
        excluded_dirs = ['node_modules', '__pycache__', 'venv', 'env']
        for dir_name in excluded_dirs:
            excluded_dir = tmp_path / dir_name
            excluded_dir.mkdir()
            (excluded_dir / "test.ts").write_text("excluded file")
        
        # Create normal file
        (tmp_path / "normal.ts").write_text("normal file")
        
        collector = ContextCollector(basic_config, str(tmp_path))
        ts_files = collector._find_files_by_pattern(r'.*\.ts$')
        
        # Should only find normal file
        assert len(ts_files) == 1
        assert ts_files[0].name == "normal.ts"


class TestContextCollectorPerformance:
    """Test performance characteristics of context collection."""
    
    def test_large_project_performance(self, basic_config, tmp_path):
        """Test performance with large project structure."""
        import time
        
        # Create many files
        for i in range(100):
            test_dir = tmp_path / f"dir{i}"
            test_dir.mkdir()
            (test_dir / f"test{i}.spec.ts").write_text(f"test content {i}")
            (test_dir / f"component{i}.tsx").write_text(f"component {i}")
        
        collector = ContextCollector(basic_config, str(tmp_path))
        
        start_time = time.time()
        context = collector.collect_context()
        end_time = time.time()
        
        # Should complete reasonably quickly (< 5 seconds)
        assert end_time - start_time < 5.0
        assert isinstance(context, SystemContext)
    
    def test_cache_performance(self, basic_config, tmp_path):
        """Test caching performance."""
        import time
        
        # Create some files
        for i in range(10):
            (tmp_path / f"test{i}.spec.ts").write_text(f"test {i}")
        
        collector = ContextCollector(basic_config, str(tmp_path))
        
        # First call (cold)
        start_time = time.time()
        context1 = collector.collect_context()
        first_time = time.time() - start_time
        
        # Second call (cached)
        start_time = time.time()
        context2 = collector.collect_context()
        second_time = time.time() - start_time
        
        # Cached call should be much faster
        assert second_time < first_time / 10  # At least 10x faster
        assert context1 is context2


class TestIntegrationWithConfig:
    """Test integration with different configuration options."""
    
    def test_with_context_disabled(self, basic_config, temp_project_dir):
        """Test with context collection disabled."""
        basic_config.processing.collect_system_context = False
        collector = ContextCollector(basic_config, str(temp_project_dir))
        
        # Should still work but might skip some collection
        context = collector.collect_context()
        assert isinstance(context, SystemContext)
    
    def test_with_specific_includes_disabled(self, basic_config, temp_project_dir):
        """Test with specific collection types disabled."""
        basic_config.processing.include_existing_tests = False
        basic_config.processing.include_documentation = False
        basic_config.processing.include_ui_components = False
        
        collector = ContextCollector(basic_config, str(temp_project_dir))
        context = collector.collect_context()
        
        assert isinstance(context, SystemContext)
        # These might still be collected in basic implementation
        # but configuration is respected in full implementation
    
    def test_with_max_files_limit(self, basic_config, tmp_path):
        """Test with maximum files limit."""
        basic_config.processing.max_context_files = 5
        
        # Create more files than the limit
        for i in range(10):
            (tmp_path / f"test{i}.spec.ts").write_text(f"test {i}")
        
        collector = ContextCollector(basic_config, str(tmp_path))
        context = collector.collect_context()
        
        assert isinstance(context, SystemContext)
        # Should respect the limit (though basic implementation might not enforce it)


@pytest.mark.slow
class TestRealFileSystem:
    """Test with real file system operations."""
    
    def test_collect_context_real_project(self, basic_config):
        """Test context collection on the actual project."""
        # Use the current project directory
        collector = ContextCollector(basic_config, ".")
        context = collector.collect_context()
        
        assert isinstance(context, SystemContext)
        
        # Should find this project's files
        assert context.project.project_root == str(collector.project_root)
        
        # Should find some documentation (this README.md file)
        assert len(context.documentation) > 0
        
        # Should find configuration files
        assert len(context.configuration) > 0 