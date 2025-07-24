"""Tests for the new IncrementalSession class introduced in the architectural restructuring."""

import pytest
from unittest.mock import patch, MagicMock

from browse_to_test.core.orchestration.session import IncrementalSession, SessionResult
from browse_to_test.core.configuration.config import ConfigBuilder


class TestSessionResult:
    """Test the SessionResult dataclass."""

    def test_session_result_creation(self):
        """Test SessionResult creation with basic parameters."""
        result = SessionResult(
            success=True,
            current_script="test script",
            lines_added=5,
            step_count=3
        )
        
        assert result.success is True
        assert result.current_script == "test script"
        assert result.lines_added == 5
        assert result.step_count == 3
        assert result.validation_issues == []
        assert result.warnings == []
        assert result.metadata == {}

    def test_session_result_with_optional_fields(self):
        """Test SessionResult with all optional fields."""
        metadata = {"duration": 1.5, "target_url": "https://example.com"}
        result = SessionResult(
            success=False,
            current_script="",
            lines_added=0,
            step_count=0,
            validation_issues=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            metadata=metadata
        )
        
        assert result.success is False
        assert result.current_script == ""
        assert result.lines_added == 0
        assert result.step_count == 0
        assert result.validation_issues == ["Error 1", "Error 2"]
        assert result.warnings == ["Warning 1"]
        assert result.metadata == metadata


class TestIncrementalSession:
    """Test the IncrementalSession class."""

    @pytest.fixture
    def basic_config(self):
        """Create a basic config for testing."""
        return ConfigBuilder().framework("playwright").build()

    @pytest.fixture
    def mock_converter(self):
        """Mock E2eTestConverter."""
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock:
            yield mock

    def test_init(self, basic_config, mock_converter):
        """Test IncrementalSession initialization."""
        session = IncrementalSession(basic_config)
        
        assert session.config == basic_config
        mock_converter.assert_called_once_with(basic_config)
        assert not session.is_active()
        assert session.get_step_count() == 0
        assert session.get_current_script() == ""

    def test_start_basic(self, basic_config, mock_converter):
        """Test starting a basic session."""
        session = IncrementalSession(basic_config)
        
        result = session.start()
        
        assert result.success is True
        assert session.is_active()
        assert result.current_script != ""  # Should have initial setup
        assert "session_started" in result.metadata
        assert result.metadata["session_started"] is True

    def test_start_with_target_url(self, basic_config, mock_converter):
        """Test starting session with target URL."""
        session = IncrementalSession(basic_config)
        
        result = session.start(target_url="https://example.com")
        
        assert result.success is True
        assert session.is_active()
        assert result.metadata["target_url"] == "https://example.com"

    def test_start_with_context_hints(self, basic_config, mock_converter):
        """Test starting session with context hints."""
        context_hints = {"type": "login", "form_id": "login-form"}
        session = IncrementalSession(basic_config)
        
        result = session.start(context_hints=context_hints)
        
        assert result.success is True
        assert session.is_active()
        assert session._context_hints == context_hints

    def test_start_already_active(self, basic_config, mock_converter):
        """Test starting session when already active."""
        session = IncrementalSession(basic_config)
        
        # Start first session
        session.start()
        assert session.is_active()
        
        # Try to start again
        result = session.start()
        
        assert result.success is False
        assert "Session is already active" in result.validation_issues

    def test_start_with_exception(self, basic_config, mock_converter):
        """Test start method when exception occurs."""
        session = IncrementalSession(basic_config)
        
        # Mock an exception during start
        with patch.object(session, '_generate_initial_setup', side_effect=Exception("Setup error")):
            result = session.start()
            
            assert result.success is False
            assert not session.is_active()
            assert any("Startup failed" in issue for issue in result.validation_issues)

    def test_add_step_basic(self, basic_config, mock_converter, sample_automation_data):
        """Test adding a basic step."""
        session = IncrementalSession(basic_config)
        session.start()
        
        step_data = sample_automation_data[0]
        
        # Mock the converter to return a script
        mock_converter.return_value.convert.return_value = "Updated script with step"
        
        result = session.add_step(step_data)
        
        assert result.success is True
        assert result.step_count == 1
        assert result.current_script == "Updated script with step"
        assert result.lines_added >= 0

    def test_add_step_not_active(self, basic_config, mock_converter):
        """Test adding step when session is not active."""
        session = IncrementalSession(basic_config)
        
        result = session.add_step({"test": "data"})
        
        assert result.success is False
        assert "Session is not active" in result.validation_issues

    def test_add_step_with_validation(self, basic_config, mock_converter):
        """Test adding step with validation enabled."""
        session = IncrementalSession(basic_config)
        session.start()
        
        # Mock validation to return errors
        mock_converter.return_value.validate_data.return_value = ["Validation error"]
        mock_converter.return_value.convert.return_value = "Script with issues"
        
        result = session.add_step({"test": "data"}, validate=True)
        
        assert result.success is True  # Add still succeeds
        assert result.validation_issues == ["Validation error"]
        mock_converter.return_value.validate_data.assert_called_once()

    def test_add_step_without_validation(self, basic_config, mock_converter):
        """Test adding step without validation."""
        session = IncrementalSession(basic_config)
        session.start()
        
        mock_converter.return_value.convert.return_value = "Updated script"
        
        result = session.add_step({"test": "data"}, validate=False)
        
        assert result.success is True
        assert result.validation_issues == []
        mock_converter.return_value.validate_data.assert_not_called()

    def test_add_step_with_exception(self, basic_config, mock_converter):
        """Test add_step when an exception occurs (should gracefully handle and still succeed)."""
        session = IncrementalSession(basic_config)
        session.start()
        
        # Mock converter to raise exception
        mock_converter.return_value.convert.side_effect = Exception("Conversion error")
        
        result = session.add_step({"test": "data"})
        
        # Session should still succeed (graceful error handling) but script won't be updated
        assert result.success is True
        assert result.step_count == 1  # Step was added to internal list
        # The script should remain the initial setup script since conversion failed

    def test_add_multiple_steps(self, basic_config, mock_converter, sample_automation_data):
        """Test adding multiple steps sequentially."""
        session = IncrementalSession(basic_config)
        session.start()
        
        # Mock converter to return different scripts for each step
        mock_converter.return_value.convert.side_effect = [
            "Script with step 1",
            "Script with step 1 and 2", 
            "Script with step 1, 2, and 3"
        ]
        
        results = []
        for i, step in enumerate(sample_automation_data):
            result = session.add_step(step)
            results.append(result)
            
            assert result.success is True
            assert result.step_count == i + 1

        # Check final state
        assert session.get_step_count() == 3
        assert session.get_current_script() == "Script with step 1, 2, and 3"

    def test_remove_last_step(self, basic_config, mock_converter):
        """Test removing the last step."""
        session = IncrementalSession(basic_config)
        session.start()
        
        # Add a step first
        mock_converter.return_value.convert.side_effect = [
            "Script with step",
            "Script without step"
        ]
        session.add_step({"test": "data"})
        
        # Remove the step
        result = session.remove_last_step()
        
        assert result.success is True
        assert result.step_count == 0
        assert "step_removed" in result.metadata

    def test_remove_last_step_not_active(self, basic_config, mock_converter):
        """Test removing step when session is not active."""
        session = IncrementalSession(basic_config)
        
        result = session.remove_last_step()
        
        assert result.success is False
        assert "Session is not active" in result.validation_issues

    def test_remove_last_step_no_steps(self, basic_config, mock_converter):
        """Test removing step when no steps exist."""
        session = IncrementalSession(basic_config)
        session.start()
        
        result = session.remove_last_step()
        
        assert result.success is False
        assert "No steps to remove" in result.validation_issues

    def test_remove_last_step_with_exception(self, basic_config, mock_converter):
        """Test remove_last_step when an exception occurs (should gracefully handle)."""
        session = IncrementalSession(basic_config)
        session.start()
        session.add_step({"test": "data"})
        
        # Mock converter to raise exception during regeneration
        mock_converter.return_value.convert.side_effect = Exception("Regeneration error")
        
        result = session.remove_last_step()
        
        # Should still succeed (graceful error handling) - step is removed from internal list
        assert result.success is True
        assert result.step_count == 0  # Step was removed from internal list
        assert "step_removed" in result.metadata

    def test_finalize_basic(self, basic_config, mock_converter):
        """Test basic session finalization."""
        session = IncrementalSession(basic_config)
        session.start()
        
        result = session.finalize()
        
        assert result.success is True
        assert not session.is_active()
        assert len(result.current_script) > 0  # Should have some script content
        assert "session_finalized" in result.metadata
        assert "duration_seconds" in result.metadata

    def test_finalize_with_validation(self, basic_config, mock_converter):
        """Test finalization with validation enabled."""
        session = IncrementalSession(basic_config)
        session.start()
        session.add_step({"test": "data"})
        
        mock_converter.return_value.validate_data.return_value = ["Final validation error"]
        
        result = session.finalize(validate=True)
        
        assert result.success is True
        assert result.validation_issues == ["Final validation error"]
        # Note: validate_data may be called multiple times (during add_step and finalize)

    def test_finalize_without_validation(self, basic_config, mock_converter):
        """Test finalization without validation."""
        session = IncrementalSession(basic_config)
        session.start()
        
        mock_converter.return_value.convert.return_value = "Final script"
        
        result = session.finalize(validate=False)
        
        assert result.success is True
        assert result.validation_issues == []
        mock_converter.return_value.validate_data.assert_not_called()

    def test_finalize_not_active(self, basic_config, mock_converter):
        """Test finalizing when session is not active."""
        session = IncrementalSession(basic_config)
        
        result = session.finalize()
        
        assert result.success is False
        assert "Session is not active" in result.validation_issues

    def test_finalize_with_exception(self, basic_config, mock_converter):
        """Test finalize when an exception occurs (should gracefully handle)."""
        session = IncrementalSession(basic_config)
        session.start()
        
        # Mock converter to raise exception
        mock_converter.return_value.convert.side_effect = Exception("Finalization error")
        
        result = session.finalize()
        
        # Should still succeed (graceful error handling) with initial setup script
        assert result.success is True
        assert not session.is_active()  # Session is still finalized
        assert "session_finalized" in result.metadata

    def test_generate_initial_setup_playwright(self, mock_converter):
        """Test initial setup generation for Playwright."""
        config = ConfigBuilder().framework("playwright").build()
        session = IncrementalSession(config)
        
        session._generate_initial_setup()
        
        # Check that playwright imports were added
        imports = session._script_sections['imports']
        assert any("playwright" in line for line in imports)
        assert any("pytest" in line for line in imports)

    def test_generate_initial_setup_selenium(self, mock_converter):
        """Test initial setup generation for Selenium."""
        config = ConfigBuilder().framework("selenium").build()
        session = IncrementalSession(config)
        
        session._generate_initial_setup()
        
        # Check that selenium imports were added
        imports = session._script_sections['imports']
        assert any("selenium" in line for line in imports)
        assert any("pytest" in line for line in imports)

    def test_regenerate_script_failure(self, basic_config, mock_converter):
        """Test script regeneration when converter fails."""
        session = IncrementalSession(basic_config)
        session.start()
        original_script = session.get_current_script()
        
        # Add step data
        session._steps = [{"test": "data"}]
        
        # Mock converter to fail
        mock_converter.return_value.convert.side_effect = Exception("Conversion failed")
        
        # Should not raise exception, just log warning
        session._regenerate_script()
        
        # Script should remain unchanged
        assert session.get_current_script() == original_script

    def test_session_state_tracking(self, basic_config, mock_converter):
        """Test that session properly tracks its state."""
        session = IncrementalSession(basic_config)
        
        # Initial state
        assert not session.is_active()
        assert session.get_step_count() == 0
        assert session._start_time is None
        
        # After start
        session.start()
        assert session.is_active()
        assert session._start_time is not None
        assert session._target_url is None
        
        # After adding steps
        mock_converter.return_value.convert.return_value = "Updated script"
        session.add_step({"step": 1})
        session.add_step({"step": 2})
        
        assert session.get_step_count() == 2
        assert len(session._steps) == 2
        
        # After finalization
        session.finalize()
        assert not session.is_active()


class TestIncrementalSessionIntegration:
    """Integration tests for IncrementalSession."""

    def test_full_session_workflow(self, sample_automation_data):
        """Test a complete session workflow."""
        config = ConfigBuilder().framework("playwright").build()
        
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_converter_class:
            mock_converter = MagicMock()
            mock_converter.convert.side_effect = [
                "Script with step 1",
                "Script with step 1 and 2",
                "Script with step 1, 2, and 3",
                "Final optimized script"
            ]
            mock_converter.validate_data.return_value = []
            mock_converter_class.return_value = mock_converter
            
            session = IncrementalSession(config)
            
            # Start session
            start_result = session.start("https://example.com")
            assert start_result.success
            
            # Add steps
            step_results = []
            for step in sample_automation_data:
                result = session.add_step(step)
                step_results.append(result)
                assert result.success
            
            # Finalize
            final_result = session.finalize()
            assert final_result.success
            assert final_result.current_script == "Final optimized script"
            assert final_result.step_count == 3
            
            # Verify converter was called appropriately
            assert mock_converter.convert.call_count == 4  # 3 steps + finalization

    def test_session_with_errors_continues(self, sample_automation_data):
        """Test that session continues even when individual operations have errors."""
        config = ConfigBuilder().framework("playwright").build()
        
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter') as mock_converter_class:
            mock_converter = MagicMock()
            # First step succeeds, second fails, third succeeds
            mock_converter.convert.side_effect = [
                "Script with step 1",
                Exception("Step 2 failed"),
                "Script with step 1 and 3"
            ]
            mock_converter_class.return_value = mock_converter
            
            session = IncrementalSession(config)
            session.start()
            
            # Add first step (should succeed)
            result1 = session.add_step(sample_automation_data[0])
            assert result1.success
            
            # Add second step (should succeed but with warning logged)
            result2 = session.add_step(sample_automation_data[1])
            assert result2.success  # Graceful error handling
            
            # Add third step (should succeed) 
            result3 = session.add_step(sample_automation_data[2])
            assert result3.success
            
            # Session should still be functional
            assert session.is_active()
            assert session.get_step_count() == 3  # All steps tracked even if conversion failed

    def test_session_metadata_tracking(self):
        """Test that session properly tracks metadata."""
        config = ConfigBuilder().framework("playwright").build()
        
        with patch('browse_to_test.core.orchestration.session.E2eTestConverter'):
            session = IncrementalSession(config)
            
            # Start with metadata
            # start_time = datetime.now()
            result = session.start("https://example.com", {"test": "hint"})
            
            assert result.metadata["session_started"] is True
            assert result.metadata["target_url"] == "https://example.com"
            assert "start_time" in result.metadata
            
            # Check internal state
            assert session._target_url == "https://example.com"
            assert session._context_hints == {"test": "hint"}
            assert session._start_time is not None
            
            # Finalize and check duration
            final_result = session.finalize()
            assert "duration_seconds" in final_result.metadata
            assert final_result.metadata["duration_seconds"] >= 0 