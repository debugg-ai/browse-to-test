"""Tests for the input parser."""

import json
import tempfile
from pathlib import Path

import pytest

# import browse_to_test as btt
from browse_to_test.core.processing.input_parser import InputParser, ParsedAutomationData, ParsedStep, ParsedAction


class TestInputParser:
    """Test the InputParser class."""

    def test_parse_simple_data(self, basic_config, sample_automation_data):
        """Test parsing simple automation data."""
        parser = InputParser(basic_config)
        parsed = parser.parse(sample_automation_data)
        
        assert isinstance(parsed, ParsedAutomationData)
        assert len(parsed.steps) == 3
        assert parsed.total_actions == 3
        
        # Check first step
        step1 = parsed.steps[0]
        assert step1.step_index == 0
        assert len(step1.actions) == 1
        
        action1 = step1.actions[0]
        assert action1.action_type == "go_to_url"
        assert action1.parameters == {"url": "https://example.com"}
        assert action1.step_index == 0
        assert action1.action_index == 0

    def test_parse_complex_data(self, basic_config, complex_automation_data):
        """Test parsing complex automation data with sensitive data."""
        parser = InputParser(basic_config)
        parsed = parser.parse(complex_automation_data)
        
        assert len(parsed.steps) == 6
        assert parsed.total_actions == 6
        
        # Check sensitive data detection
        sensitive_keys = parser.extract_sensitive_data_keys(parsed)
        assert "username" in sensitive_keys
        assert "password" in sensitive_keys
        
        # Check selector information
        step2 = parsed.steps[1]  # Input username step
        action2 = step2.actions[0]
        assert action2.selector_info is not None
        assert "xpath" in action2.selector_info
        assert "css_selector" in action2.selector_info
        assert "data-testid" in action2.selector_info["attributes"]

    def test_parse_invalid_data(self, basic_config, invalid_automation_data):
        """Test parsing invalid automation data."""
        parser = InputParser(basic_config)
        
        # Should not raise exception but handle gracefully
        parsed = parser.parse(invalid_automation_data)
        assert isinstance(parsed, ParsedAutomationData)
        
        # First step has empty actions
        assert len(parsed.steps[0].actions) == 0
        
        # Second step has invalid action but should be parsed anyway
        assert len(parsed.steps[1].actions) == 1
        assert parsed.steps[1].actions[0].action_type == "invalid_action"

    def test_parse_edge_cases(self, basic_config, edge_case_data):
        """Test parsing edge case data."""
        parser = InputParser(basic_config)
        parsed = parser.parse(edge_case_data)
        
        assert isinstance(parsed, ParsedAutomationData)
        assert len(parsed.steps) == len(edge_case_data)
        
        # Check that very long text is handled
        long_text_step = next(
            step for step in parsed.steps 
            if step.actions and "x" * 1000 in str(step.actions[0].parameters)
        )
        assert long_text_step is not None
        
        # Check unicode handling
        unicode_step = next(
            step for step in parsed.steps 
            if step.actions and "🚀" in str(step.actions[0].parameters)
        )
        assert unicode_step is not None

    def test_parse_from_json_string(self, basic_config, sample_automation_data):
        """Test parsing from JSON string."""
        parser = InputParser(basic_config)
        json_string = json.dumps(sample_automation_data)
        parsed = parser.parse(json_string)
        
        assert isinstance(parsed, ParsedAutomationData)
        assert len(parsed.steps) == 3

    def test_parse_from_file(self, basic_config, sample_automation_data):
        """Test parsing from file."""
        parser = InputParser(basic_config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_automation_data, f)
            temp_file = f.name
        
        try:
            parsed = parser.parse(Path(temp_file))
            assert isinstance(parsed, ParsedAutomationData)
            assert len(parsed.steps) == 3
        finally:
            Path(temp_file).unlink()

    def test_parse_from_string_path(self, basic_config, sample_automation_data):
        """Test parsing from string file path."""
        parser = InputParser(basic_config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_automation_data, f)
            temp_file = f.name
        
        try:
            parsed = parser.parse(temp_file)
            assert isinstance(parsed, ParsedAutomationData)
            assert len(parsed.steps) == 3
        finally:
            Path(temp_file).unlink()

    def test_parse_nonexistent_file(self, basic_config):
        """Test parsing nonexistent file."""
        parser = InputParser(basic_config)
        with pytest.raises(FileNotFoundError):
            parser.parse("/nonexistent/file.json")

    def test_parse_invalid_json_file(self, basic_config):
        """Test parsing invalid JSON file."""
        parser = InputParser(basic_config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                parser.parse(temp_file)
        finally:
            Path(temp_file).unlink()

    def test_parse_invalid_json_string(self, basic_config):
        """Test parsing invalid JSON string."""
        parser = InputParser(basic_config)
        with pytest.raises(json.JSONDecodeError):
            parser.parse("invalid json string")

    def test_parse_empty_data(self, basic_config):
        """Test parsing empty data."""
        parser = InputParser(basic_config)
        parsed = parser.parse([])
        
        assert isinstance(parsed, ParsedAutomationData)
        assert len(parsed.steps) == 0
        assert parsed.total_actions == 0

    def test_parse_none_data(self, basic_config):
        """Test parsing None data."""
        parser = InputParser(basic_config)
        with pytest.raises((TypeError, ValueError)):
            parser.parse(None)

    def test_extract_sensitive_data_keys(self, basic_config, complex_automation_data):
        """Test extracting sensitive data keys."""
        parser = InputParser(basic_config)
        parsed = parser.parse(complex_automation_data)
        keys = parser.extract_sensitive_data_keys(parsed)
        
        assert "username" in keys
        assert "password" in keys
        assert len(keys) == 2

    def test_extract_sensitive_data_keys_custom_patterns(self, basic_config):
        """Test extracting sensitive data keys with custom patterns."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "input_text": {
                                "text": "<secret>api_key</secret>",
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {"interacted_element": []}
            },
            {
                "model_output": {
                    "action": [
                        {
                            "input_text": {
                                "text": "<secret>auth_token</secret>",
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {"interacted_element": []}
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        keys = parser.extract_sensitive_data_keys(parsed)
        
        assert "api_key" in keys
        assert "auth_token" in keys

    def test_extract_sensitive_data_keys_no_secrets(self, basic_config, sample_automation_data):
        """Test extracting sensitive data keys when no secrets are present."""
        parser = InputParser(basic_config)
        parsed = parser.parse(sample_automation_data)
        keys = parser.extract_sensitive_data_keys(parsed)
        
        assert len(keys) == 0

    def test_selector_info_extraction(self, basic_config):
        """Test extraction of selector information."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "click_element": {
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": [
                        {
                            "xpath": "//button[@id='submit-btn']",
                            "css_selector": "#submit-btn",
                            "attributes": {
                                "id": "submit-btn",
                                "type": "button",
                                "class": "btn btn-primary",
                                "data-testid": "submit-button"
                            },
                            "text_content": "Submit Form"
                        }
                    ]
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        action = parsed.steps[0].actions[0]
        assert action.selector_info is not None
        assert action.selector_info["xpath"] == "//button[@id='submit-btn']"
        assert action.selector_info["css_selector"] == "#submit-btn"
        assert action.selector_info["attributes"]["id"] == "submit-btn"
        assert action.selector_info["attributes"]["data-testid"] == "submit-button"
        assert action.selector_info["text_content"] == "Submit Form"

    def test_selector_info_missing(self, basic_config):
        """Test handling when selector info is missing."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "click_element": {
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": []  # No element info
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        action = parsed.steps[0].actions[0]
        assert action.selector_info is None

    def test_selector_info_partial(self, basic_config):
        """Test handling when selector info is partial."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "input_text": {
                                "text": "test",
                                "index": 0
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": [
                        {
                            "css_selector": "#email-input",
                            # Missing xpath and attributes
                        }
                    ]
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        action = parsed.steps[0].actions[0]
        assert action.selector_info is not None
        assert action.selector_info["css_selector"] == "#email-input"
        assert "xpath" not in action.selector_info or action.selector_info["xpath"] is None

    def test_metadata_extraction(self, basic_config):
        """Test extraction of metadata."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "go_to_url": {
                                "url": "https://example.com"
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": []
                },
                "metadata": {
                    "step_start_time": 1640995200.0,
                    "elapsed_time": 2.5,
                    "screenshot": "screenshot.png",
                    "custom_field": "custom_value"
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        step = parsed.steps[0]
        assert step.metadata is not None
        assert step.metadata["step_start_time"] == 1640995200.0
        assert step.metadata["elapsed_time"] == 2.5
        assert step.metadata["screenshot"] == "screenshot.png"
        assert step.metadata["custom_field"] == "custom_value"

    def test_metadata_missing(self, basic_config):
        """Test handling when metadata is missing."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "go_to_url": {
                                "url": "https://example.com"
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": []
                }
                # No metadata field
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        step = parsed.steps[0]
        assert step.metadata is None

    @pytest.mark.parametrize("action_type,params", [
        ("go_to_url", {"url": "https://example.com"}),
        ("input_text", {"text": "test input", "index": 0}),
        ("click_element", {"index": 0}),
        ("wait", {"seconds": 2}),
        ("scroll_down", {"amount": 100}),
        ("scroll_up", {}),
        ("done", {"text": "Task completed", "success": True}),
        ("search_google", {"query": "test search"}),
        ("send_keys", {"keys": "Ctrl+A"}),
        ("go_back", {}),
        ("open_tab", {}),
        ("close_tab", {}),
        ("switch_tab", {"index": 1}),
        ("drag_drop", {"from_element": 0, "to_element": 1}),
        ("extract_content", {"selector": ".content"}),
        ("click_download_button", {}),
    ])
    def test_different_action_types(self, basic_config, action_type, params):
        """Test parsing different action types."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            action_type: params
                        }
                    ]
                },
                "state": {
                    "interacted_element": []
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        action = parsed.steps[0].actions[0]
        assert action.action_type == action_type
        assert action.parameters == params

    def test_multiple_actions_per_step(self, basic_config):
        """Test parsing multiple actions in a single step."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            "input_text": {
                                "text": "username",
                                "index": 0
                            }
                        },
                        {
                            "input_text": {
                                "text": "password",
                                "index": 1
                            }
                        },
                        {
                            "click_element": {
                                "index": 2
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": []
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        step = parsed.steps[0]
        assert len(step.actions) == 3
        
        assert step.actions[0].action_type == "input_text"
        assert step.actions[0].parameters["text"] == "username"
        assert step.actions[0].action_index == 0
        
        assert step.actions[1].action_type == "input_text"
        assert step.actions[1].parameters["text"] == "password"
        assert step.actions[1].action_index == 1
        
        assert step.actions[2].action_type == "click_element"
        assert step.actions[2].action_index == 2

    def test_malformed_action_structure(self, basic_config):
        """Test handling malformed action structure."""
        data = [
            {
                "model_output": {
                    "action": [
                        {
                            # Missing action type and parameters
                        },
                        "invalid_action_format",
                        {
                            "valid_action": {
                                "param": "value"
                            }
                        }
                    ]
                },
                "state": {
                    "interacted_element": []
                }
            }
        ]
        
        parser = InputParser(basic_config)
        parsed = parser.parse(data)
        
        step = parsed.steps[0]
        # Should handle malformed actions gracefully
        assert len(step.actions) >= 1  # At least the valid action should be parsed

    def test_very_large_data(self, basic_config, large_automation_data):
        """Test parsing very large automation data."""
        parser = InputParser(basic_config)
        parsed = parser.parse(large_automation_data)
        
        assert isinstance(parsed, ParsedAutomationData)
        assert len(parsed.steps) == 100
        assert parsed.total_actions == 100

    def test_performance_large_data(self, basic_config, large_automation_data):
        """Test performance with large data."""
        import time
        
        parser = InputParser(basic_config)
        
        start_time = time.time()
        parsed = parser.parse(large_automation_data)
        end_time = time.time()
        
        # Should parse 100 actions in reasonable time (< 1 second)
        parse_time = end_time - start_time
        assert parse_time < 1.0
        assert len(parsed.steps) == 100


class TestParsedAction:
    """Test the ParsedAction class."""

    def test_parsed_action_creation(self):
        """Test creating ParsedAction."""
        action = ParsedAction(
            action_type="click_element",
            parameters={"index": 0},
            step_index=1,
            action_index=2,
            selector_info={"css_selector": "#button"},
            metadata={"custom": "value"}
        )
        
        assert action.action_type == "click_element"
        assert action.parameters == {"index": 0}
        assert action.step_index == 1
        assert action.action_index == 2
        assert action.selector_info == {"css_selector": "#button"}
        assert action.metadata == {"custom": "value"}

    def test_parsed_action_minimal(self):
        """Test creating ParsedAction with minimal parameters."""
        action = ParsedAction(
            action_type="wait",
            parameters={"seconds": 1},
            step_index=0,
            action_index=0
        )
        
        assert action.action_type == "wait"
        assert action.parameters == {"seconds": 1}
        assert action.step_index == 0
        assert action.action_index == 0
        assert action.selector_info is None
        assert action.metadata is None


class TestParsedStep:
    """Test the ParsedStep class."""

    def test_parsed_step_creation(self):
        """Test creating ParsedStep."""
        actions = [
            ParsedAction("go_to_url", {"url": "https://example.com"}, 0, 0),
            ParsedAction("click_element", {"index": 0}, 0, 1)
        ]
        
        step = ParsedStep(
            step_index=0,
            actions=actions,
            timing_info={"elapsed_time": 2.5},
            metadata={"custom": "value"}
        )
        
        assert step.step_index == 0
        assert len(step.actions) == 2
        assert step.timing_info == {"elapsed_time": 2.5}
        assert step.metadata == {"custom": "value"}

    def test_parsed_step_empty_actions(self):
        """Test creating ParsedStep with empty actions."""
        step = ParsedStep(
            step_index=0,
            actions=[],
            timing_info=None,
            metadata=None
        )
        
        assert step.step_index == 0
        assert len(step.actions) == 0
        assert step.timing_info is None
        assert step.metadata is None


class TestParsedAutomationData:
    """Test the ParsedAutomationData class."""

    def test_parsed_automation_data_creation(self):
        """Test creating ParsedAutomationData."""
        actions = [ParsedAction("go_to_url", {"url": "https://example.com"}, 0, 0)]
        steps = [ParsedStep(0, actions)]
        
        data = ParsedAutomationData(
            steps=steps,
            sensitive_data_keys=["password"],
            metadata={"source": "test"}
        )
        
        assert len(data.steps) == 1
        assert data.sensitive_data_keys == ["password"]
        assert data.metadata == {"source": "test"}
        assert data.total_actions == 1

    def test_total_actions_calculation(self):
        """Test total actions calculation."""
        # Step 1: 2 actions
        actions1 = [
            ParsedAction("go_to_url", {"url": "https://example.com"}, 0, 0),
            ParsedAction("input_text", {"text": "test", "index": 0}, 0, 1)
        ]
        step1 = ParsedStep(0, actions1)
        
        # Step 2: 1 action
        actions2 = [ParsedAction("click_element", {"index": 0}, 1, 0)]
        step2 = ParsedStep(1, actions2)
        
        # Step 3: 0 actions
        step3 = ParsedStep(2, [])
        
        data = ParsedAutomationData(steps=[step1, step2, step3])
        assert data.total_actions == 3

    def test_empty_steps(self):
        """Test with empty steps."""
        data = ParsedAutomationData(steps=[])
        assert len(data.steps) == 0
        assert data.total_actions == 0

    def test_strict_mode_validation_regression(self, basic_config):
        """Test strict mode validation for missing model_output (Regression test)."""
        # Enable strict mode
        basic_config.processing.strict_mode = True
        parser = InputParser(basic_config)
        
        # Invalid data without model_output should raise error
        invalid_data = [{"invalid": "data"}]
        
        with pytest.raises(ValueError, match="missing required 'model_output' field"):
            parser.parse(invalid_data)

    def test_invalid_model_output_type_strict_mode(self, basic_config):
        """Test that invalid model_output type raises error in strict mode."""
        basic_config.processing.strict_mode = True
        parser = InputParser(basic_config)
        
        # Invalid model_output type
        invalid_data = [
            {
                "model_output": "should_be_dict_not_string",
                "state": {"interacted_element": []},
            }
        ]
        
        with pytest.raises(ValueError, match="invalid model_output type"):
            parser.parse(invalid_data)

    def test_graceful_handling_non_strict_mode(self, basic_config):
        """Test graceful handling of invalid data when strict mode is disabled."""
        # Ensure strict mode is disabled (default)
        basic_config.processing.strict_mode = False
        parser = InputParser(basic_config)
        
        # Invalid data should be handled gracefully
        invalid_data = [{"invalid": "data"}]
        
        parsed = parser.parse(invalid_data)
        assert len(parsed.steps) == 1
        assert len(parsed.steps[0].actions) == 0

    def test_valid_data_with_required_fields(self, basic_config):
        """Test that valid data with required fields works in strict mode."""
        basic_config.processing.strict_mode = True
        parser = InputParser(basic_config)
        
        # Valid data with required model_output
        valid_data = [
            {
                "model_output": {
                    "action": [{"go_to_url": {"url": "https://example.com"}}]
                },
                "state": {"interacted_element": []},
                "metadata": {"description": "Navigate"}
            }
        ]
        
        parsed = parser.parse(valid_data)
        assert len(parsed.steps) == 1
        assert len(parsed.steps[0].actions) == 1
        assert parsed.steps[0].actions[0].action_type == "go_to_url" 