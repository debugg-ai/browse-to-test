"""Tests for the configuration system."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

import browse_to_test as btt
from browse_to_test.core.configuration.config import Config, AIConfig, OutputConfig, ProcessingConfig


class TestAIConfig:
    """Test the AIConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = AIConfig()
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.api_key is None
        assert config.temperature == 0.1
        assert config.max_tokens == 4000
        assert config.timeout == 30
        assert config.retry_attempts == 3

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AIConfig(
            provider="anthropic",
            model="claude-3-sonnet",
            api_key="test-key",
            temperature=0.5,
            max_tokens=8000,
            timeout=60,
            retry_attempts=5,
            extra_params={"custom": "value"}
        )
        assert config.provider == "anthropic"
        assert config.model == "claude-3-sonnet"
        assert config.api_key == "test-key"
        assert config.temperature == 0.5
        assert config.max_tokens == 8000
        assert config.timeout == 60
        assert config.retry_attempts == 5
        assert config.extra_params == {"custom": "value"}

    @pytest.mark.parametrize("provider,model", [
        ("openai", "gpt-3.5-turbo"),
        ("openai", "gpt-4"),
        ("anthropic", "claude-3-sonnet"),
        ("anthropic", "claude-3-haiku"),
        ("azure", "gpt-4"),
        ("local", "llama2"),
    ])
    def test_provider_model_combinations(self, provider, model):
        """Test various provider and model combinations."""
        config = AIConfig(provider=provider, model=model)
        assert config.provider == provider
        assert config.model == model

    def test_edge_case_values(self):
        """Test edge case values."""
        # Minimum values
        config = AIConfig(temperature=0.0, max_tokens=1, timeout=1, retry_attempts=0)
        assert config.temperature == 0.0
        assert config.max_tokens == 1
        assert config.timeout == 1
        assert config.retry_attempts == 0

        # Maximum reasonable values
        config = AIConfig(temperature=2.0, max_tokens=32000, timeout=3600)
        assert config.temperature == 2.0
        assert config.max_tokens == 32000
        assert config.timeout == 3600


class TestOutputConfig:
    """Test the OutputConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = OutputConfig()
        assert config.framework == "playwright"
        assert config.language == "python"
        assert config.test_type == "script"
        assert config.include_assertions is True
        assert config.include_waits is True
        assert config.include_error_handling is True
        assert config.include_logging is False
        assert config.include_screenshots is False
        assert config.sensitive_data_keys == []
        assert config.mask_sensitive_data is True
        assert config.test_timeout == 30000
        assert config.browser_options == {}

    def test_custom_values(self):
        """Test custom configuration values."""
        config = OutputConfig(
            framework="selenium",
            language="javascript",
            test_type="test",
            include_assertions=False,
            include_waits=False,
            include_error_handling=False,
            include_logging=True,
            include_screenshots=True,
            sensitive_data_keys=["password", "token"],
            mask_sensitive_data=False,
            test_timeout=60000,
            browser_options={"headless": True}
        )
        assert config.framework == "selenium"
        assert config.language == "javascript"
        assert config.test_type == "test"
        assert config.include_assertions is False
        assert config.include_waits is False
        assert config.include_error_handling is False
        assert config.include_logging is True
        assert config.include_screenshots is True
        assert config.sensitive_data_keys == ["password", "token"]
        assert config.mask_sensitive_data is False
        assert config.test_timeout == 60000
        assert config.browser_options == {"headless": True}

    @pytest.mark.parametrize("framework,language", [
        ("playwright", "python"),
        ("playwright", "javascript"),
        ("playwright", "typescript"),
        ("selenium", "python"),
        ("selenium", "java"),
        ("cypress", "javascript"),
        ("cypress", "typescript"),
    ])
    def test_framework_language_combinations(self, framework, language):
        """Test various framework and language combinations."""
        config = OutputConfig(framework=framework, language=language)
        assert config.framework == framework
        assert config.language == language

    def test_sensitive_data_keys_edge_cases(self):
        """Test edge cases for sensitive data keys."""
        # Empty list
        config = OutputConfig(sensitive_data_keys=[])
        assert config.sensitive_data_keys == []

        # Single item
        config = OutputConfig(sensitive_data_keys=["password"])
        assert config.sensitive_data_keys == ["password"]

        # Many items
        keys = [f"key{i}" for i in range(100)]
        config = OutputConfig(sensitive_data_keys=keys)
        assert config.sensitive_data_keys == keys

        # Duplicate items
        config = OutputConfig(sensitive_data_keys=["password", "password", "token"])
        assert config.sensitive_data_keys == ["password", "password", "token"]


class TestProcessingConfig:
    """Test the ProcessingConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ProcessingConfig()
        assert config.analyze_actions_with_ai is True
        assert config.optimize_selectors is True
        assert config.validate_actions is True
        assert config.strict_mode is False
        assert config.cache_ai_responses is True
        assert config.max_cache_size == 1000
        assert config.collect_system_context is True
        assert config.context_cache_ttl == 3600
        assert config.max_context_files == 100
        assert config.include_existing_tests is True
        assert config.include_documentation is True
        assert config.include_ui_components is True
        assert config.include_api_endpoints is True
        assert config.include_database_schema is False
        assert config.include_recent_changes is True
        assert config.use_intelligent_analysis is True
        assert config.context_similarity_threshold == 0.3
        assert config.max_similar_tests == 5
        assert config.context_analysis_depth == "deep"

    def test_context_collection_disabled(self):
        """Test configuration with context collection disabled."""
        config = ProcessingConfig(
            collect_system_context=False,
            use_intelligent_analysis=False,
            include_existing_tests=False,
            include_documentation=False,
            include_ui_components=False,
            include_api_endpoints=False,
            include_recent_changes=False
        )
        assert config.collect_system_context is False
        assert config.use_intelligent_analysis is False
        assert config.include_existing_tests is False
        assert config.include_documentation is False
        assert config.include_ui_components is False
        assert config.include_api_endpoints is False
        assert config.include_recent_changes is False

    def test_performance_tuning(self):
        """Test performance-related configuration."""
        config = ProcessingConfig(
            max_cache_size=5000,
            context_cache_ttl=7200,
            max_context_files=500,
            max_context_prompt_size=16000
        )
        assert config.max_cache_size == 5000
        assert config.context_cache_ttl == 7200
        assert config.max_context_files == 500
        assert config.max_context_prompt_size == 16000

    @pytest.mark.parametrize("depth", ["shallow", "medium", "deep"])
    def test_context_analysis_depths(self, depth):
        """Test different context analysis depths."""
        config = ProcessingConfig(context_analysis_depth=depth)
        assert config.context_analysis_depth == depth

    def test_edge_case_values(self):
        """Test edge case values."""
        # Minimum values
        config = ProcessingConfig(
            max_cache_size=0,
            context_cache_ttl=0,
            max_context_files=0,
            context_similarity_threshold=0.0,
            max_similar_tests=0,
            max_context_prompt_size=1000
        )
        assert config.max_cache_size == 0
        assert config.context_cache_ttl == 0
        assert config.max_context_files == 0
        assert config.context_similarity_threshold == 0.0
        assert config.max_similar_tests == 0

        # Maximum values
        config = ProcessingConfig(
            max_cache_size=10000,
            context_similarity_threshold=1.0,
            max_similar_tests=100
        )
        assert config.max_cache_size == 10000
        assert config.context_similarity_threshold == 1.0
        assert config.max_similar_tests == 100


class TestConfig:
    """Test the main Config class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        assert isinstance(config.ai, AIConfig)
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.processing, ProcessingConfig)
        assert config.debug is False
        assert config.verbose is False
        assert config.log_level == "INFO"
        assert config.project_root is None

    def test_custom_nested_configs(self):
        """Test custom nested configurations."""
        ai_config = AIConfig(provider="anthropic", model="claude-3-sonnet")
        output_config = OutputConfig(framework="selenium", language="java")
        processing_config = ProcessingConfig(collect_system_context=False)

        config = Config(
            ai=ai_config,
            output=output_config,
            processing=processing_config,
            debug=True,
            verbose=True,
            log_level="DEBUG",
            project_root="/custom/path"
        )

        assert config.ai.provider == "anthropic"
        assert config.ai.model == "claude-3-sonnet"
        assert config.output.framework == "selenium"
        assert config.output.language == "java"
        assert config.processing.collect_system_context is False
        assert config.debug is True
        assert config.verbose is True
        assert config.log_level == "DEBUG"
        assert config.project_root == "/custom/path"

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "ai": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.5
            },
            "output": {
                "framework": "cypress",
                "language": "typescript",
                "include_assertions": False
            },
            "processing": {
                "analyze_actions_with_ai": False,
                "context_analysis_depth": "shallow"
            },
            "debug": True,
            "log_level": "DEBUG"
        }

        config = Config.from_dict(config_dict)
        assert config.ai.provider == "openai"
        assert config.ai.model == "gpt-3.5-turbo"
        assert config.ai.temperature == 0.5
        assert config.output.framework == "cypress"
        assert config.output.language == "typescript"
        assert config.output.include_assertions is False
        assert config.processing.analyze_actions_with_ai is False
        assert config.processing.context_analysis_depth == "shallow"
        assert config.debug is True
        assert config.log_level == "DEBUG"

    def test_from_dict_partial(self):
        """Test creating config from partial dictionary."""
        config_dict = {
            "ai": {
                "provider": "anthropic"
                # Only provider specified, other values should be defaults
            },
            "debug": True
        }

        config = Config.from_dict(config_dict)
        assert config.ai.provider == "anthropic"
        assert config.ai.model == "gpt-4"  # Default value
        assert config.ai.temperature == 0.1  # Default value
        assert config.debug is True
        assert config.log_level == "INFO"  # Default value

    def test_from_dict_empty(self):
        """Test creating config from empty dictionary."""
        config = Config.from_dict({})
        # Should have all default values
        assert config.ai.provider == "openai"
        assert config.output.framework == "playwright"
        assert config.processing.collect_system_context is True
        assert config.debug is False

    def test_from_file_json(self):
        """Test loading config from JSON file."""
        config_data = {
            "ai": {"provider": "openai", "model": "gpt-4"},
            "output": {"framework": "playwright", "language": "python"},
            "debug": True
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config.from_file(temp_file)
            assert config.ai.provider == "openai"
            assert config.ai.model == "gpt-4"
            assert config.output.framework == "playwright"
            assert config.debug is True
        finally:
            os.unlink(temp_file)

    def test_from_file_yaml(self):
        """Test loading config from YAML file."""
        config_data = {
            "ai": {"provider": "anthropic", "model": "claude-3-sonnet"},
            "output": {"framework": "selenium", "language": "java"},
            "verbose": True
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_file = f.name

        try:
            config = Config.from_file(temp_file)
            assert config.ai.provider == "anthropic"
            assert config.ai.model == "claude-3-sonnet"
            assert config.output.framework == "selenium"
            assert config.verbose is True
        finally:
            os.unlink(temp_file)

    def test_from_file_nonexistent(self):
        """Test loading config from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_file("/nonexistent/file.json")

    def test_from_file_invalid_format(self):
        """Test loading config from file with invalid format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid config content")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported config file format"):
                Config.from_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_from_file_invalid_json(self):
        """Test loading config from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                Config.from_file(temp_file)
        finally:
            os.unlink(temp_file)

    def test_from_env(self):
        """Test loading config from environment variables."""
        env_vars = {
            "BROWSE_TO_TEST_AI_PROVIDER": "anthropic",
            "BROWSE_TO_TEST_AI_MODEL": "claude-3-haiku",
            "BROWSE_TO_TEST_AI_TEMPERATURE": "0.7",
            "BROWSE_TO_TEST_OUTPUT_FRAMEWORK": "cypress",
            "BROWSE_TO_TEST_OUTPUT_LANGUAGE": "typescript",
            "BROWSE_TO_TEST_OUTPUT_INCLUDE_ASSERTIONS": "false",
            "BROWSE_TO_TEST_PROCESSING_ANALYZE_WITH_AI": "false",
            "BROWSE_TO_TEST_PROCESSING_COLLECT_CONTEXT": "false",
            "BROWSE_TO_TEST_DEBUG": "true",
            "BROWSE_TO_TEST_VERBOSE": "true",
            "BROWSE_TO_TEST_LOG_LEVEL": "DEBUG"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()
            assert config.ai.provider == "anthropic"
            assert config.ai.model == "claude-3-haiku"
            assert config.ai.temperature == 0.7
            assert config.output.framework == "cypress"
            assert config.output.language == "typescript"
            assert config.output.include_assertions is False
            assert config.processing.analyze_actions_with_ai is False
            assert config.processing.collect_system_context is False
            assert config.debug is True
            assert config.verbose is True
            assert config.log_level == "DEBUG"

    def test_from_env_standard_keys(self):
        """Test loading config from standard environment variables."""
        env_vars = {
            "OPENAI_API_KEY": "openai-key-123",
            "ANTHROPIC_API_KEY": "anthropic-key-456",
            "AZURE_OPENAI_API_KEY": "azure-key-789",
            "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com"
        }

        with patch.dict(os.environ, env_vars, clear=False):
            # Test OpenAI
            config = Config.from_env()
            config.ai.provider = "openai"
            if not config.ai.api_key:  # Only if not already set by browse_to_test vars
                config = Config.from_env()
                # The from_env method should pick up standard keys

            # Test Anthropic
            config = Config.from_env()
            config.ai.provider = "anthropic"
            
            # Test Azure
            config = Config.from_env()
            config.ai.provider = "azure"

    def test_from_env_no_vars(self):
        """Test loading config when no environment variables are set."""
        # This should return default config
        config = Config.from_env()
        assert config.ai.provider == "openai"
        assert config.output.framework == "playwright"
        assert config.debug is False

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            ai=AIConfig(provider="anthropic", model="claude-3-sonnet"),
            output=OutputConfig(framework="selenium", language="java"),
            debug=True
        )

        config_dict = config.to_dict()
        assert config_dict["ai"]["provider"] == "anthropic"
        assert config_dict["ai"]["model"] == "claude-3-sonnet"
        assert config_dict["output"]["framework"] == "selenium"
        assert config_dict["output"]["language"] == "java"
        assert config_dict["debug"] is True

    def test_save_to_file_json(self):
        """Test saving config to JSON file."""
        config = Config(
            ai=AIConfig(provider="openai", model="gpt-4"),
            debug=True
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            config.save_to_file(temp_file)
            
            # Verify file was saved correctly
            with open(temp_file) as f:
                saved_data = json.load(f)
            
            assert saved_data["ai"]["provider"] == "openai"
            assert saved_data["ai"]["model"] == "gpt-4"
            assert saved_data["debug"] is True
        finally:
            os.unlink(temp_file)

    def test_save_to_file_yaml(self):
        """Test saving config to YAML file."""
        config = Config(
            ai=AIConfig(provider="anthropic", model="claude-3-sonnet"),
            verbose=True
        )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name

        try:
            config.save_to_file(temp_file)
            
            # Verify file was saved correctly
            with open(temp_file) as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data["ai"]["provider"] == "anthropic"
            assert saved_data["ai"]["model"] == "claude-3-sonnet"
            assert saved_data["verbose"] is True
        finally:
            os.unlink(temp_file)

    def test_save_to_file_invalid_format(self):
        """Test saving config to file with invalid format."""
        config = Config()
        with pytest.raises(ValueError, match="Unsupported config file format"):
            config.save_to_file("config.txt")

    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        config = Config()
        errors = config.validate()
        assert errors == []

    def test_validate_invalid_config(self):
        """Test validation of invalid configuration."""
        config = Config(
            ai=AIConfig(
                provider="",  # Empty provider
                model="",     # Empty model
                temperature=-1.0,  # Invalid temperature
                max_tokens=-1      # Invalid max_tokens
            ),
            output=OutputConfig(
                framework="",  # Empty framework
                language="",   # Empty language
                test_timeout=500  # Too low timeout
            ),
            processing=ProcessingConfig(
                max_cache_size=-1,  # Invalid cache size
                context_similarity_threshold=2.0,  # Invalid threshold
                context_analysis_depth="invalid"   # Invalid depth
            ),
            log_level="INVALID"  # Invalid log level
        )

        errors = config.validate()
        assert len(errors) > 0
        assert any("provider cannot be empty" in error for error in errors)
        assert any("model cannot be empty" in error for error in errors)
        assert any("temperature must be between 0 and 2" in error for error in errors)
        assert any("max_tokens must be positive" in error for error in errors)
        assert any("framework cannot be empty" in error for error in errors)
        assert any("language cannot be empty" in error for error in errors)
        assert any("Test timeout must be at least 1000ms" in error for error in errors)
        assert any("Max cache size cannot be negative" in error for error in errors)
        assert any("similarity threshold must be between 0 and 1" in error for error in errors)
        assert any("analysis depth must be" in error for error in errors)
        assert any("Log level must be one of" in error for error in errors)

    def test_update_from_dict(self):
        """Test updating configuration from dictionary."""
        config = Config()
        
        updates = {
            "ai": {"provider": "anthropic", "temperature": 0.5},
            "output": {"framework": "selenium"},
            "debug": True
        }
        
        config.update_from_dict(updates)
        
        assert config.ai.provider == "anthropic"
        assert config.ai.temperature == 0.5
        assert config.ai.model == "gpt-4"  # Unchanged
        assert config.output.framework == "selenium"
        assert config.output.language == "python"  # Unchanged
        assert config.debug is True

    def test_get_context_collection_config(self):
        """Test getting context collection specific configuration."""
        config = Config(
            processing=ProcessingConfig(
                collect_system_context=True,
                include_existing_tests=False,
                max_context_files=200
            ),
            project_root="/test/path"
        )
        
        context_config = config.get_context_collection_config()
        
        assert context_config["collect_system_context"] is True
        assert context_config["include_existing_tests"] is False
        assert context_config["max_context_files"] == 200
        assert context_config["project_root"] == "/test/path"

    def test_get_ai_analysis_config(self):
        """Test getting AI analysis specific configuration."""
        config = Config(
            processing=ProcessingConfig(
                use_intelligent_analysis=True,
                context_analysis_depth="deep",
                max_similar_tests=10
            ),
            output=OutputConfig(framework="playwright", language="typescript")
        )
        
        ai_config = config.get_ai_analysis_config()
        
        assert ai_config["use_intelligent_analysis"] is True
        assert ai_config["context_analysis_depth"] == "deep"
        assert ai_config["max_similar_tests"] == 10
        assert ai_config["target_framework"] == "playwright"
        assert ai_config["target_language"] == "typescript"

    def test_optimize_for_speed(self):
        """Test speed optimization."""
        config = Config()
        config.optimize_for_speed()
        
        assert config.processing.collect_system_context is False
        assert config.processing.use_intelligent_analysis is False
        assert config.processing.include_ui_components is False
        assert config.processing.context_analysis_depth == "shallow"
        assert config.processing.max_context_files == 20
        assert config.ai.max_tokens == 2000

    def test_optimize_for_accuracy(self):
        """Test accuracy optimization."""
        config = Config()
        config.optimize_for_accuracy()
        
        assert config.processing.collect_system_context is True
        assert config.processing.use_intelligent_analysis is True
        assert config.processing.include_ui_components is True
        assert config.processing.context_analysis_depth == "deep"
        assert config.processing.max_context_files == 200
        assert config.ai.max_tokens == 8000
        assert config.processing.max_context_prompt_size == 12000

    def test_repr(self):
        """Test string representation of config."""
        config = Config(
            ai=AIConfig(provider="anthropic"),
            output=OutputConfig(framework="selenium"),
            processing=ProcessingConfig(collect_system_context=False)
        )
        
        repr_str = repr(config)
        assert "anthropic" in repr_str
        assert "selenium" in repr_str
        assert "context=False" in repr_str

    def test_config_roundtrip(self):
        """Test config can be saved and loaded without data loss."""
        original_config = Config(
            ai=AIConfig(
                provider="anthropic",
                model="claude-3-sonnet",
                temperature=0.7,
                extra_params={"custom": "value"}
            ),
            output=OutputConfig(
                framework="selenium",
                language="java",
                sensitive_data_keys=["password", "token"],
                browser_options={"headless": True}
            ),
            processing=ProcessingConfig(
                context_analysis_depth="medium",
                max_similar_tests=3,
                scan_test_directories=["custom_tests/"]
            ),
            debug=True,
            project_root="/custom/path"
        )

        # Convert to dict and back
        config_dict = original_config.to_dict()
        loaded_config = Config.from_dict(config_dict)

        # Verify all values are preserved
        assert loaded_config.ai.provider == original_config.ai.provider
        assert loaded_config.ai.model == original_config.ai.model
        assert loaded_config.ai.temperature == original_config.ai.temperature
        assert loaded_config.ai.extra_params == original_config.ai.extra_params
        assert loaded_config.output.framework == original_config.output.framework
        assert loaded_config.output.language == original_config.output.language
        assert loaded_config.output.sensitive_data_keys == original_config.output.sensitive_data_keys
        assert loaded_config.output.browser_options == original_config.output.browser_options
        assert loaded_config.processing.context_analysis_depth == original_config.processing.context_analysis_depth
        assert loaded_config.processing.max_similar_tests == original_config.processing.max_similar_tests
        assert loaded_config.processing.scan_test_directories == original_config.processing.scan_test_directories
        assert loaded_config.debug == original_config.debug
        assert loaded_config.project_root == original_config.project_root 