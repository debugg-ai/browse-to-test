#!/usr/bin/env python3
"""
Tests for the incremental test script orchestrator.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from browse_to_test.core.orchestration.incremental_orchestrator import (
    IncrementalE2eScriptOrchestrator,
    ScriptState,
    IncrementalUpdateResult
)
from browse_to_test.core.configuration.config import Config, OutputConfig, ProcessingConfig
from browse_to_test.core.processing.input_parser import ParsedStep, ParsedAction
from browse_to_test.plugins.incremental_playwright_plugin import IncrementalPlaywrightPlugin


@pytest.fixture
def basic_config():
    """Create basic configuration for testing."""
    return Config(
        output=OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_error_handling=True,
            include_logging=True,
        ),
        processing=ProcessingConfig(
            analyze_actions_with_ai=False,  # Disable for most tests
            collect_system_context=False,
            strict_mode=False,
        ),
        verbose=False,
        debug=False
    )


@pytest.fixture
def ai_enabled_config():
    """Create configuration with AI analysis enabled."""
    return Config(
        output=OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_error_handling=True,
        ),
        processing=ProcessingConfig(
            analyze_actions_with_ai=True,
            collect_system_context=True,
            use_intelligent_analysis=True,
            strict_mode=False,
        ),
        verbose=True,
        debug=True
    )


@pytest.fixture
def sample_step_data():
    """Sample automation step data for testing."""
    return {
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
            "elapsed_time": 1.2
        }
    }


@pytest.fixture
def complex_step_data():
    """Complex automation step data with multiple actions."""
    return {
        "model_output": {
            "action": [
                {
                    "input_text": {
                        "text": "test@example.com",
                        "index": 0
                    }
                },
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
                    "xpath": "//input[@data-testid='email-input']",
                    "css_selector": "input[data-testid='email-input']",
                    "attributes": {
                        "id": "email",
                        "type": "email",
                        "data-testid": "email-input"
                    }
                },
                {
                    "xpath": "//button[@type='submit']",
                    "css_selector": "button[type='submit']",
                    "attributes": {
                        "type": "submit",
                        "class": "btn btn-primary"
                    }
                }
            ]
        },
        "metadata": {
            "step_start_time": 1640995201.2,
            "elapsed_time": 2.5
        }
    }


class TestScriptState:
    """Tests for ScriptState class."""
    
    def test_script_state_initialization(self):
        """Test script state is initialized correctly."""
        state = ScriptState()
        
        assert state.imports == []
        assert state.helpers == []
        assert state.setup_code == []
        assert state.test_steps == []
        assert state.cleanup_code == []
        assert state.current_step_count == 0
        assert state.total_actions == 0
        assert not state.setup_complete
        assert not state.finalized
        assert state.accumulated_analysis == {}
        assert state.system_context is None
        assert state.validation_issues == []
        assert state.target_url is None
        assert state.start_time is None
        assert state.last_update_time is None
    
    def test_script_state_to_script(self):
        """Test converting script state to complete script."""
        state = ScriptState()
        state.imports = ["import asyncio", "import os"]
        state.helpers = ["def helper():", "    pass"]
        state.setup_code = ["async def test():", "    print('setup')"]
        state.test_steps = ["    print('step 1')", "    print('step 2')"]
        state.cleanup_code = ["    print('cleanup')", "if __name__ == '__main__':", "    asyncio.run(test())"]
        
        script = state.to_script()
        
        assert "import asyncio" in script
        assert "import os" in script
        assert "def helper():" in script
        assert "async def test():" in script
        assert "print('step 1')" in script
        assert "print('step 2')" in script
        assert "print('cleanup')" in script
        assert "asyncio.run(test())" in script
    
    def test_script_state_metadata(self):
        """Test script state metadata generation."""
        state = ScriptState()
        state.current_step_count = 3
        state.total_actions = 7
        state.setup_complete = True
        state.finalized = False
        state.validation_issues = ["issue1", "issue2"]
        state.target_url = "https://example.com"
        state.start_time = datetime(2024, 1, 1, 12, 0, 0)
        state.last_update_time = datetime(2024, 1, 1, 12, 5, 0)
        
        metadata = state.get_metadata()
        
        assert metadata["step_count"] == 3
        assert metadata["total_actions"] == 7
        assert metadata["setup_complete"] is True
        assert metadata["finalized"] is False
        assert metadata["validation_issues_count"] == 2
        assert metadata["has_system_context"] is False
        assert metadata["target_url"] == "https://example.com"
        assert metadata["start_time"] == "2024-01-01T12:00:00"
        assert metadata["last_update"] == "2024-01-01T12:05:00"


class TestIncrementalE2eScriptOrchestrator:
    """Tests for IncrementalE2eScriptOrchestrator class."""
    
    def test_orchestrator_initialization(self, basic_config):
        """Test orchestrator is initialized correctly."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        assert orchestrator.config == basic_config
        assert orchestrator.input_parser is not None
        assert orchestrator.ai_factory is not None
        assert orchestrator.plugin_registry is not None
        assert orchestrator.context_collector is None  # Disabled in basic config
        assert orchestrator.ai_provider is None  # Disabled in basic config
        assert orchestrator.action_analyzer is not None
        assert orchestrator._current_script_state is None
        assert orchestrator._current_plugin is None
        assert orchestrator._session_cache == {}
        assert orchestrator._update_callbacks == []
    
    def test_orchestrator_initialization_with_ai(self, ai_enabled_config):
        """Test orchestrator initialization with AI enabled."""
        with patch('browse_to_test.core.orchestration.incremental_orchestrator.AIProviderFactory') as mock_ai_factory, \
             patch('browse_to_test.core.orchestration.incremental_orchestrator.ContextCollector') as mock_context_collector:
            
            mock_ai_provider = Mock()
            mock_ai_factory.return_value.create_provider.return_value = mock_ai_provider
            
            orchestrator = IncrementalE2eScriptOrchestrator(ai_enabled_config)
            
            assert orchestrator.context_collector is not None
            mock_context_collector.assert_called_once()
    
    def test_start_incremental_session_already_active(self, basic_config):
        """Test starting session when one is already active."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        orchestrator._current_script_state = ScriptState()  # Simulate active session
        
        with pytest.raises(RuntimeError, match="Incremental session already active"):
            orchestrator.start_incremental_session()
    
    def test_add_step_no_active_session(self, basic_config, sample_step_data):
        """Test adding step when no session is active."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        result = orchestrator.add_step(sample_step_data)
        
        assert result.success is False
        assert "No active incremental session" in result.validation_issues[0]
    
    def test_add_step_success(self, basic_config, sample_step_data):
        """Test successfully adding a step."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Set up active session
        orchestrator._current_script_state = ScriptState()
        orchestrator._current_script_state.setup_complete = True
        
        # Mock the plugin
        mock_plugin = Mock()
        mock_plugin.add_incremental_step.return_value = {
            'step_code': ['    # Step 1', '    await page.goto("https://example.com")', ''],
            'validation_issues': [],
            'insights': ['Navigation detected']
        }
        orchestrator._current_plugin = mock_plugin
        
        result = orchestrator.add_step(sample_step_data)
        
        assert result.success is True
        assert result.new_lines_added == 3
        assert len(result.analysis_insights) > 0
        assert orchestrator._current_script_state.current_step_count == 1
        assert orchestrator._current_script_state.total_actions == 1
        assert len(orchestrator._current_script_state.test_steps) == 3
    
    def test_add_step_with_parsed_step(self, basic_config):
        """Test adding a step using ParsedStep object."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Set up active session
        orchestrator._current_script_state = ScriptState()
        orchestrator._current_script_state.setup_complete = True
        
        # Create a ParsedStep
        action = ParsedAction(
            action_type="go_to_url",
            parameters={"url": "https://example.com"},
            step_index=0,
            action_index=0
        )
        step = ParsedStep(step_index=0, actions=[action])
        
        # Mock the plugin
        mock_plugin = Mock()
        mock_plugin.add_incremental_step.return_value = {
            'step_code': ['    # Step 1', '    await page.goto("https://example.com")'],
            'validation_issues': [],
            'insights': []
        }
        orchestrator._current_plugin = mock_plugin
        
        result = orchestrator.add_step(step)
        
        assert result.success is True
        assert result.new_lines_added == 2
        assert orchestrator._current_script_state.current_step_count == 1
        assert orchestrator._current_script_state.total_actions == 1
    
    def test_add_step_with_analysis(self, basic_config, sample_step_data):
        """Test adding step with AI analysis enabled."""
        # Enable AI analysis for this test
        basic_config.processing.analyze_actions_with_ai = True
        
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Mock AI provider
        mock_ai_provider = Mock()
        orchestrator.ai_provider = mock_ai_provider
        
        # Mock action analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_automation_data.return_value = {
            'action_types': {'go_to_url': 1},
            'validation_issues': [],
            'comprehensive_analysis': {
                'critical_actions': [0],
                'context_recommendations': ['Use explicit waits']
            }
        }
        orchestrator.action_analyzer = mock_analyzer
        
        # Set up active session
        orchestrator._current_script_state = ScriptState()
        orchestrator._current_script_state.setup_complete = True
        
        # Mock the plugin
        mock_plugin = Mock()
        mock_plugin.add_incremental_step.return_value = {
            'step_code': ['    await page.goto("https://example.com")'],
            'validation_issues': [],
            'insights': ['Critical action detected']
        }
        orchestrator._current_plugin = mock_plugin
        
        result = orchestrator.add_step(sample_step_data, analyze_step=True)
        
        assert result.success is True
        assert len(result.analysis_insights) > 0
        assert orchestrator._current_script_state.accumulated_analysis != {}
        mock_analyzer.analyze_automation_data.assert_called_once()
    
    def test_finalize_session_no_active_session(self, basic_config):
        """Test finalizing when no session is active."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        result = orchestrator.finalize_session()
        
        assert result.success is False
        assert "No active incremental session" in result.validation_issues[0]
    
    def test_finalize_session_success(self, basic_config):
        """Test successfully finalizing a session."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Set up active session with some content
        orchestrator._current_script_state = ScriptState()
        orchestrator._current_script_state.setup_complete = True
        orchestrator._current_script_state.current_step_count = 2
        orchestrator._current_script_state.total_actions = 3
        orchestrator._current_script_state.test_steps = [
            "    # Step 1",
            "    await page.goto('https://example.com')",
            "    # Step 2", 
            "    await page.click('#submit')"
        ]
        
        # Mock the plugin
        mock_plugin = Mock()
        mock_plugin.finalize_incremental_script.return_value = {
            'final_cleanup_code': ['    await browser.close()', 'if __name__ == "__main__":', '    asyncio.run(run_test())'],
            'validation_issues': [],
            'optimization_insights': ['Script looks good', 'Applied formatting']
        }
        orchestrator._current_plugin = mock_plugin
        
        result = orchestrator.finalize_session()
        
        assert result.success is True
        assert len(result.analysis_insights) > 0
        assert "Script looks good" in result.analysis_insights
        assert orchestrator._current_script_state is None  # Session cleaned up
        assert orchestrator._current_plugin is None
    
    def test_finalize_session_with_validation_issues(self, basic_config):
        """Test finalizing session with validation issues."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Set up active session
        orchestrator._current_script_state = ScriptState()
        orchestrator._current_script_state.setup_complete = True
        
        # Mock the plugin to return validation issues
        mock_plugin = Mock()
        mock_plugin.finalize_incremental_script.return_value = {
            'final_cleanup_code': [],
            'validation_issues': ['Missing imports', 'No test steps found'],
            'optimization_insights': []
        }
        orchestrator._current_plugin = mock_plugin
        
        result = orchestrator.finalize_session()
        
        assert result.success is False  # Validation issues cause failure
        assert len(result.validation_issues) >= 2  # May include additional validation
        assert "Missing imports" in result.validation_issues
        assert "No test steps found" in result.validation_issues
    
    def test_get_current_state_no_session(self, basic_config):
        """Test getting current state when no session is active."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        state = orchestrator.get_current_state()
        
        assert state is None
    
    def test_get_current_state_active_session(self, basic_config):
        """Test getting current state with active session."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Set up active session
        script_state = ScriptState()
        script_state.setup_complete = True
        script_state.current_step_count = 1
        script_state.total_actions = 2
        script_state.test_steps = ["    print('test')"]
        orchestrator._current_script_state = script_state
        
        state = orchestrator.get_current_state()
        
        assert state is not None
        assert state["active"] is True
        assert state["setup_complete"] is True
        assert state["finalized"] is False
        assert state["metadata"]["step_count"] == 1
        assert state["metadata"]["total_actions"] == 2
        assert "print('test')" in state["script_preview"]
    
    def test_update_callbacks(self, basic_config):
        """Test update callback registration and notification."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Create mock callbacks
        callback1 = Mock()
        callback2 = Mock()
        
        # Register callbacks
        orchestrator.register_update_callback(callback1)
        orchestrator.register_update_callback(callback2)
        
        assert len(orchestrator._update_callbacks) == 2
        
        # Test callback notification (via start session)
        mock_plugin = Mock()
        mock_plugin.plugin_name = "test_plugin"
        mock_plugin.setup_incremental_script.return_value = {
            'imports': [], 'helpers': [], 'setup_code': [], 'cleanup_code': []
        }
        
        with patch.object(orchestrator.plugin_registry, 'create_plugin', return_value=mock_plugin):
            orchestrator.start_incremental_session()
        
        assert callback1.call_count == 1
        assert callback2.call_count == 1
        
        # Test callback unregistration
        orchestrator.unregister_update_callback(callback1)
        assert len(orchestrator._update_callbacks) == 1
        
        # Test callback with exception
        callback2.side_effect = Exception("Callback error")
        orchestrator.add_step({"model_output": {"action": []}, "state": {"interacted_element": []}})
        # Should not raise exception even though callback failed
    
    def test_abort_session(self, basic_config):
        """Test aborting an active session."""
        orchestrator = IncrementalE2eScriptOrchestrator(basic_config)
        
        # Set up active session
        orchestrator._current_script_state = ScriptState()
        orchestrator._current_plugin = Mock()
        
        assert orchestrator._current_script_state is not None
        assert orchestrator._current_plugin is not None
        
        orchestrator.abort_session()
        
        assert orchestrator._current_script_state is None
        assert orchestrator._current_plugin is None
