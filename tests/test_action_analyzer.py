"""Tests for action analysis and optimization functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from browse_to_test.core.processing.action_analyzer import (
    ActionAnalyzer,
    ActionAnalysisResult,
    ComprehensiveAnalysisResult
)
from browse_to_test.core.processing.input_parser import ParsedAutomationData, ParsedStep, ParsedAction
from browse_to_test.core.processing.context_collector import SystemContext, ProjectContext, TestFileInfo
from browse_to_test.core.configuration.config import Config, ProcessingConfig
from browse_to_test.ai.base import AIProvider, AIResponse, AnalysisType


class TestActionAnalysisResult:
    """Test the ActionAnalysisResult dataclass."""
    
    def test_basic_creation(self):
        """Test creating basic ActionAnalysisResult."""
        result = ActionAnalysisResult(
            action_index=0,
            action_type="click_element",
            reliability_score=0.8,
            selector_quality=0.9
        )
        
        assert result.action_index == 0
        assert result.action_type == "click_element"
        assert result.reliability_score == 0.8
        assert result.selector_quality == 0.9
        assert result.recommended_selector is None
        assert result.potential_issues == []
        assert result.suggestions == []
        assert result.context_insights == []
        assert result.metadata == {}
    
    def test_full_creation(self):
        """Test creating ActionAnalysisResult with all fields."""
        result = ActionAnalysisResult(
            action_index=1,
            action_type="input_text",
            reliability_score=0.7,
            selector_quality=0.85,
            recommended_selector="[data-testid='email-input']",
            recommended_wait_strategy="wait_for_element",
            potential_issues=["Selector might be fragile"],
            suggestions=["Use data-testid"],
            context_insights=["Similar pattern found in login.spec.ts"],
            metadata={"framework": "playwright"}
        )
        
        assert result.action_index == 1
        assert result.recommended_selector == "[data-testid='email-input']"
        assert result.recommended_wait_strategy == "wait_for_element"
        assert len(result.potential_issues) == 1
        assert len(result.suggestions) == 1
        assert len(result.context_insights) == 1
        assert result.metadata["framework"] == "playwright"


class TestComprehensiveAnalysisResult:
    """Test the ComprehensiveAnalysisResult dataclass."""
    
    def test_basic_creation(self):
        """Test creating basic ComprehensiveAnalysisResult."""
        result = ComprehensiveAnalysisResult(
            overall_quality_score=0.85,
            total_actions=5,
            critical_actions=[0, 1, 2],
            auxiliary_actions=[3, 4],
            action_results=[]
        )
        
        assert result.overall_quality_score == 0.85
        assert result.total_actions == 5
        assert result.critical_actions == [0, 1, 2]
        assert result.auxiliary_actions == [3, 4]
        assert result.context_recommendations == []
        assert result.similar_tests == []
    
    def test_full_creation(self):
        """Test creating comprehensive result with all fields."""
        action_result = ActionAnalysisResult(0, "click", 0.8, 0.9)
        
        result = ComprehensiveAnalysisResult(
            overall_quality_score=0.9,
            total_actions=3,
            critical_actions=[0, 1],
            auxiliary_actions=[2],
            action_results=[action_result],
            context_recommendations=["Use existing login pattern"],
            integration_suggestions=["Add to auth test suite"],
            test_data_recommendations=["Use test user credentials"],
            reliability_concerns=["Navigation timing"],
            framework_optimizations=["Add explicit waits"],
            similar_tests=[{"file": "login.spec.ts", "similarity": 0.8}],
            analysis_metadata={"timestamp": "2024-01-01"}
        )
        
        assert len(result.action_results) == 1
        assert len(result.context_recommendations) == 1
        assert len(result.similar_tests) == 1
        assert result.analysis_metadata["timestamp"] == "2024-01-01"


class TestActionAnalyzer:
    """Test the ActionAnalyzer class."""
    
    @pytest.fixture
    def mock_ai_provider(self):
        """Create a mock AI provider."""
        provider = Mock(spec=AIProvider)
        provider.analyze_with_context.return_value = AIResponse(
            content="Mock analysis response with data-testid recommendations",
            model="mock-model",
            provider="mock",
            tokens_used=150
        )
        return provider
    
    @pytest.fixture
    def basic_config(self):
        """Create basic configuration."""
        return Config(
            processing=ProcessingConfig(
                analyze_actions_with_ai=True,
                collect_system_context=True,
                use_intelligent_analysis=True
            )
        )
    
    @pytest.fixture
    def analyzer_with_ai(self, mock_ai_provider, basic_config):
        """Create ActionAnalyzer with AI provider."""
        return ActionAnalyzer(mock_ai_provider, basic_config)
    
    @pytest.fixture
    def analyzer_without_ai(self, basic_config):
        """Create ActionAnalyzer without AI provider."""
        config = Config(
            processing=ProcessingConfig(
                analyze_actions_with_ai=False,
                collect_system_context=False
            )
        )
        return ActionAnalyzer(None, config)
    
    @pytest.fixture
    def sample_parsed_data(self):
        """Create sample parsed automation data."""
        actions = [
            ParsedAction(
                action_type="go_to_url",
                parameters={"url": "https://example.com"},
                step_index=0,
                action_index=0
            ),
            ParsedAction(
                action_type="input_text",
                parameters={"text": "test@example.com", "index": 0},
                step_index=0,
                action_index=1,
                selector_info={
                    "css_selector": "[data-testid='email-input']",
                    "xpath": "//input[@data-testid='email-input']",
                    "attributes": {"data-testid": "email-input"}
                }
            ),
            ParsedAction(
                action_type="click_element",
                parameters={"index": 0},
                step_index=0,
                action_index=2,
                selector_info={
                    "css_selector": "#submit-btn",
                    "attributes": {"id": "submit-btn"}
                }
            )
        ]
        
        step = ParsedStep(
            step_index=0,
            actions=actions,
            metadata={"elapsed_time": 2.5}
        )
        
        return ParsedAutomationData(
            steps=[step],
            total_actions=3
        )
    
    @pytest.fixture
    def sample_system_context(self):
        """Create sample system context."""
        project = ProjectContext(
            project_root="/test/project",
            name="test-app",
            description="Test application",
            tech_stack=["react", "typescript"],
            test_frameworks=["playwright"]
        )
        
        test_files = [
            TestFileInfo(
                file_path="tests/login.spec.ts",
                framework="playwright",
                language="typescript",
                test_functions=["test login flow"],
                selectors=["[data-testid='email']", "[data-testid='password']"],
                actions=["goto", "fill", "click"],
                assertions=["toBeVisible"],
                imports=["@playwright/test"],
                last_modified=datetime.now(),
                size_bytes=1024
            )
        ]
        
        return SystemContext(
            project=project,
            existing_tests=test_files,
            documentation={"README.md": "Test app documentation"},
            ui_components={"Button.tsx": {"component_names": ["Button"]}}
        )
    
    def test_init_with_ai_provider(self, mock_ai_provider, basic_config):
        """Test initializing ActionAnalyzer with AI provider."""
        analyzer = ActionAnalyzer(mock_ai_provider, basic_config)
        
        assert analyzer.ai_provider == mock_ai_provider
        assert analyzer.config == basic_config
        assert analyzer._analysis_cache == {}
        assert analyzer._context_cache == {}
    
    def test_init_without_ai_provider(self, basic_config):
        """Test initializing ActionAnalyzer without AI provider."""
        analyzer = ActionAnalyzer(None, basic_config)
        
        assert analyzer.ai_provider is None
        assert analyzer.config == basic_config
    
    def test_analyze_basic_patterns(self, analyzer_without_ai, sample_parsed_data):
        """Test basic pattern analysis without AI."""
        with patch.object(analyzer_without_ai, 'context_collector'):
            results = analyzer_without_ai.analyze_automation_data(sample_parsed_data)
        
        assert results['total_steps'] == 1
        assert results['total_actions'] == 3
        assert 'go_to_url' in results['action_types']
        assert 'input_text' in results['action_types']
        assert 'click_element' in results['action_types']
        assert results['action_types']['go_to_url'] == 1
        assert results['action_types']['input_text'] == 1
        assert results['action_types']['click_element'] == 1
        assert results['has_ai_analysis'] == False
    
    def test_analyze_selectors_quality(self, analyzer_without_ai):
        """Test selector quality analysis."""
        # Test with more xpath selectors to trigger recommendations
        selectors = [
            {"css_selector": "[data-testid='submit']", "attributes": {"data-testid": "submit"}},
            {"css_selector": "#user-id", "attributes": {"id": "user-id"}},
            {"css_selector": ".btn-primary", "attributes": {"class": "btn-primary"}},
            {"xpath": "//button[1]"},
            {"xpath": "//div[2]/span[1]"},  # More xpath to trigger recommendation
            {"css_selector": ".another-class"}  # More class selectors
        ]
        
        analysis = analyzer_without_ai._analyze_selectors(selectors)
        
        assert analysis['total_selectors'] == 6
        assert analysis['selector_types']['test_id'] == 1
        assert analysis['selector_types']['id'] == 1
        assert analysis['selector_types']['class'] == 2
        assert analysis['selector_types']['xpath'] == 2
        # Should recommend using data-testid instead of xpath (2 xpath > 1 testid)
        assert len(analysis['recommendations']) >= 1
        assert "data-testid" in analysis['recommendations'][0]
    
    def test_analyze_selectors_empty(self, analyzer_without_ai):
        """Test selector analysis with empty list."""
        analysis = analyzer_without_ai._analyze_selectors([])
        
        assert analysis['total_selectors'] == 0
        assert analysis == {'total_selectors': 0}
    
    def test_validate_basic_patterns(self, analyzer_without_ai, sample_parsed_data):
        """Test basic pattern validation."""
        # Add a navigation without wait to trigger validation issue
        nav_action = ParsedAction(
            action_type="go_to_url",
            parameters={"url": "https://example.com"},
            step_index=0,
            action_index=0
        )
        click_action = ParsedAction(
            action_type="click_element",
            parameters={"index": 0},
            step_index=0,
            action_index=1
        )
        
        step = ParsedStep(
            step_index=0,
            actions=[nav_action, click_action]
        )
        
        test_data = ParsedAutomationData(steps=[step], total_actions=2)
        
        issues = analyzer_without_ai._validate_basic_patterns(test_data)
        
        assert len(issues) >= 1
        assert any("wait after navigation" in issue for issue in issues)
    
    def test_validate_missing_selectors(self, analyzer_without_ai):
        """Test validation of missing selectors."""
        action_without_selector = ParsedAction(
            action_type="click_element",
            parameters={"index": 0},
            step_index=0,
            action_index=0
        )
        
        step = ParsedStep(step_index=0, actions=[action_without_selector])
        test_data = ParsedAutomationData(steps=[step], total_actions=1)
        
        issues = analyzer_without_ai._validate_basic_patterns(test_data)
        
        assert any("Missing selector information" in issue for issue in issues)
    
    def test_validate_sensitive_data(self, analyzer_without_ai):
        """Test validation of sensitive data patterns."""
        sensitive_action = ParsedAction(
            action_type="input_text",
            parameters={"text": "mypassword123"},
            step_index=0,
            action_index=0
        )
        
        step = ParsedStep(step_index=0, actions=[sensitive_action])
        test_data = ParsedAutomationData(steps=[step], total_actions=1)
        
        issues = analyzer_without_ai._validate_basic_patterns(test_data)
        
        assert any("sensitive data" in issue for issue in issues)
    
    def test_generate_basic_recommendations(self, analyzer_without_ai):
        """Test generation of basic recommendations."""
        # Create data with many interactions to trigger recommendations
        actions = []
        for i in range(5):
            actions.append(ParsedAction(
                action_type="click_element",
                parameters={"index": i},
                step_index=0,
                action_index=i
            ))
        
        step = ParsedStep(step_index=0, actions=actions)
        test_data = ParsedAutomationData(steps=[step], total_actions=5)
        
        recommendations = analyzer_without_ai._generate_basic_recommendations(test_data)
        
        assert len(recommendations) >= 1
        assert any("wait" in rec.lower() for rec in recommendations)
    
    @patch('browse_to_test.core.processing.action_analyzer.ContextCollector')
    def test_analyze_with_ai_and_context(self, mock_context_collector, analyzer_with_ai, sample_parsed_data, sample_system_context):
        """Test analysis with AI and system context."""
        # Mock context collector
        mock_context_collector.return_value.collect_context.return_value = sample_system_context
        analyzer_with_ai.context_collector = mock_context_collector.return_value
        
        results = analyzer_with_ai.analyze_automation_data(
            sample_parsed_data,
            target_url="https://example.com",
            use_intelligent_analysis=True
        )
        
        assert results['has_ai_analysis'] == True
        assert results['has_context'] == True
        assert 'comprehensive_analysis' in results
        analyzer_with_ai.ai_provider.analyze_with_context.assert_called_once()
    
    @patch('browse_to_test.core.processing.action_analyzer.ContextCollector')
    def test_analyze_with_ai_failure(self, mock_context_collector, analyzer_with_ai, sample_parsed_data):
        """Test analysis when AI fails."""
        # Mock AI provider to raise exception
        analyzer_with_ai.ai_provider.analyze_with_context.side_effect = Exception("AI API error")
        mock_context_collector.return_value.collect_context.return_value = None
        analyzer_with_ai.context_collector = mock_context_collector.return_value
        
        results = analyzer_with_ai.analyze_automation_data(sample_parsed_data)
        
        assert results['has_ai_analysis'] == False
        assert 'ai_analysis_error' in results
        assert "AI API error" in results['ai_analysis_error']
    
    def test_calculate_action_reliability(self, analyzer_without_ai):
        """Test action reliability calculation."""
        # Test action with good selector
        good_action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0,
            selector_info={"css_selector": "[data-testid='submit']"}
        )
        
        reliability = analyzer_without_ai._calculate_action_reliability(good_action, "reliable")
        assert reliability >= 0.8  # Should be high for good selector
        
        # Test action with poor selector
        poor_action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0,
            selector_info={"xpath": "//div[1]/span[2]/button"}
        )
        
        reliability = analyzer_without_ai._calculate_action_reliability(poor_action, "")
        assert reliability <= 0.7  # Should be lower for xpath
    
    def test_calculate_selector_quality(self, analyzer_without_ai):
        """Test selector quality calculation."""
        # Test data-testid selector (best)
        testid_action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0,
            selector_info={"css_selector": "[data-testid='submit']"}
        )
        
        quality = analyzer_without_ai._calculate_selector_quality(testid_action)
        assert quality == 0.9  # Highest score for data-testid
        
        # Test ID selector (good)
        id_action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0,
            selector_info={"css_selector": "#submit-btn", "attributes": {"id": "submit-btn"}}
        )
        
        quality = analyzer_without_ai._calculate_selector_quality(id_action)
        assert quality == 0.7  # Good score for ID
        
        # Test XPath (poor)
        xpath_action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0,
            selector_info={"xpath": "//button[1]"}
        )
        
        quality = analyzer_without_ai._calculate_selector_quality(xpath_action)
        assert quality == 0.4  # Low score for XPath
        
        # Test no selector
        no_selector_action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0
        )
        
        quality = analyzer_without_ai._calculate_selector_quality(no_selector_action)
        assert quality == 0.5  # Default score
    
    def test_analyze_single_action_without_ai(self, analyzer_without_ai):
        """Test single action analysis without AI."""
        action = ParsedAction(
            action_type="input_text",
            parameters={"text": "test"},
            step_index=0,
            action_index=0,
            selector_info={"css_selector": "[data-testid='input']"}
        )
        
        result = analyzer_without_ai.analyze_single_action(action)
        
        assert result.action_index == 0
        assert result.action_type == "input_text"
        assert result.reliability_score > 0
        assert result.selector_quality > 0
    
    def test_analyze_single_action_with_ai(self, analyzer_with_ai):
        """Test single action analysis with AI."""
        action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0,
            selector_info={"css_selector": ".btn"}
        )
        
        result = analyzer_with_ai.analyze_single_action(action, {"context": "login"})
        
        assert result.action_index == 0
        assert result.action_type == "click_element"
        analyzer_with_ai.ai_provider.analyze_with_context.assert_called_once()
    
    def test_analyze_single_action_ai_failure(self, analyzer_with_ai):
        """Test single action analysis when AI fails."""
        analyzer_with_ai.ai_provider.analyze_with_context.side_effect = Exception("AI error")
        
        action = ParsedAction(
            action_type="click_element",
            parameters={},
            step_index=0,
            action_index=0
        )
        
        result = analyzer_with_ai.analyze_single_action(action)
        
        assert result.action_type == "click_element"
        assert len(result.potential_issues) >= 1
        assert "AI analysis failed" in result.potential_issues[0]
    
    def test_caching_functionality(self, analyzer_without_ai):
        """Test analysis result caching."""
        cache_key = "test_analysis"
        test_result = {"analysis": "test"}
        
        # Test caching
        analyzer_without_ai.cache_analysis(cache_key, test_result)
        cached_result = analyzer_without_ai.get_cached_analysis(cache_key)
        
        assert cached_result == test_result
        
        # Test cache miss
        missing_result = analyzer_without_ai.get_cached_analysis("nonexistent")
        assert missing_result is None
        
        # Test cache clearing
        analyzer_without_ai.clear_cache()
        cleared_result = analyzer_without_ai.get_cached_analysis(cache_key)
        assert cleared_result is None
    
    def test_convert_parsed_data_to_dict(self, analyzer_without_ai, sample_parsed_data):
        """Test conversion of parsed data to dictionary format."""
        result = analyzer_without_ai._convert_parsed_data_to_dict(sample_parsed_data)
        
        assert len(result) == 1  # One step
        assert 'model_output' in result[0]
        assert 'state' in result[0]
        assert 'metadata' in result[0]
        assert len(result[0]['model_output']['action']) == 3  # Three actions
    
    def test_action_to_dict(self, analyzer_without_ai):
        """Test conversion of action to dictionary format."""
        action = ParsedAction(
            action_type="click_element",
            parameters={"index": 0},
            step_index=0,
            action_index=0,
            selector_info={"css_selector": "#btn"},
            metadata={"test": "data"}
        )
        
        result = analyzer_without_ai._action_to_dict(action)
        
        assert result['action_type'] == "click_element"
        assert result['parameters'] == {"index": 0}
        assert result['selector_info'] == {"css_selector": "#btn"}
        assert result['metadata'] == {"test": "data"}
    
    def test_parse_intelligent_analysis_response(self, analyzer_with_ai, sample_parsed_data, sample_system_context):
        """Test parsing of AI response into structured results."""
        ai_response = AIResponse(
            content="This analysis includes data-testid selectors and error handling recommendations. Similar tests exist.",
            model="test-model",
            provider="test",
            tokens_used=200
        )
        
        result = analyzer_with_ai._parse_intelligent_analysis_response(
            ai_response, sample_parsed_data, sample_system_context
        )
        
        assert isinstance(result, ComprehensiveAnalysisResult)
        assert result.total_actions == 3
        assert len(result.action_results) == 3
        assert len(result.framework_optimizations) >= 1
        assert result.analysis_metadata['ai_model'] == "test-model"
        assert result.analysis_metadata['tokens_used'] == 200
    
    def test_merge_analysis_results(self, analyzer_with_ai):
        """Test merging of basic and AI analysis results."""
        basic_results = {
            'total_steps': 1,
            'total_actions': 2,
            'action_types': {'click': 1, 'input': 1}
        }
        
        comprehensive_result = ComprehensiveAnalysisResult(
            overall_quality_score=0.8,
            total_actions=2,
            critical_actions=[0],
            auxiliary_actions=[1],
            action_results=[],
            context_recommendations=["Use existing patterns"],
            analysis_metadata={"ai_model": "test"}
        )
        
        merged = analyzer_with_ai._merge_analysis_results(basic_results, comprehensive_result)
        
        assert merged['total_steps'] == 1  # From basic
        assert merged['comprehensive_analysis']['overall_quality_score'] == 0.8  # From AI
        assert merged['analysis_metadata']['ai_model'] == "test"


class TestActionAnalyzerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_automation_data(self):
        """Test analysis with empty automation data."""
        config = Config()
        analyzer = ActionAnalyzer(None, config)
        
        empty_data = ParsedAutomationData(steps=[], total_actions=0)
        
        with patch.object(analyzer, 'context_collector'):
            results = analyzer.analyze_automation_data(empty_data)
        
        assert results['total_steps'] == 0
        assert results['total_actions'] == 0
    
    def test_malformed_actions(self):
        """Test analysis with malformed action data."""
        config = Config()
        analyzer = ActionAnalyzer(None, config)
        
        # Create action with minimal data
        action = ParsedAction(
            action_type="unknown_action",
            parameters={},
            step_index=0,
            action_index=0
        )
        
        step = ParsedStep(step_index=0, actions=[action])
        data = ParsedAutomationData(steps=[step], total_actions=1)
        
        with patch.object(analyzer, 'context_collector'):
            results = analyzer.analyze_automation_data(data)
        
        assert results['total_actions'] == 1
        assert 'unknown_action' in results['action_types']
    
    @patch('browse_to_test.core.processing.action_analyzer.ContextCollector')
    def test_context_collection_failure(self, mock_context_collector):
        """Test when context collection fails."""
        # Create analyzer with AI
        mock_ai = Mock(spec=AIProvider)
        mock_ai.analyze_with_context.return_value = AIResponse(
            content="Test analysis", model="test", provider="test", tokens_used=50
        )
        
        config = Config(
            processing=ProcessingConfig(
                analyze_actions_with_ai=True,
                collect_system_context=True
            )
        )
        
        # Mock context collector to raise exception
        mock_context_collector.return_value.collect_context.side_effect = Exception("Context error")
        
        analyzer = ActionAnalyzer(mock_ai, config)
        analyzer.context_collector = mock_context_collector.return_value
        
        # Create sample data
        action = ParsedAction("click", {}, 0, 0)
        step = ParsedStep(0, [action])
        sample_data = ParsedAutomationData([step], 1)
        
        # Should not crash, should continue with basic analysis
        results = analyzer.analyze_automation_data(sample_data)
        
        assert 'total_actions' in results
        # Should still attempt AI analysis without context
        analyzer.ai_provider.analyze_with_context.assert_called_once()
    
    def test_large_dataset_performance(self):
        """Test analysis with large dataset."""
        config = Config()
        analyzer = ActionAnalyzer(None, config)
        
        # Create large dataset
        actions = []
        for i in range(100):
            actions.append(ParsedAction(
                action_type="click_element",
                parameters={"index": i},
                step_index=0,
                action_index=i
            ))
        
        step = ParsedStep(step_index=0, actions=actions)
        large_data = ParsedAutomationData(steps=[step], total_actions=100)
        
        with patch.object(analyzer, 'context_collector'):
            results = analyzer.analyze_automation_data(large_data)
        
        assert results['total_actions'] == 100
        assert results['action_types']['click_element'] == 100
    
    def test_unicode_and_special_characters(self):
        """Test analysis with unicode and special characters in data."""
        config = Config()
        analyzer = ActionAnalyzer(None, config)
        
        action = ParsedAction(
            action_type="input_text",
            parameters={"text": "🚀 Test with émojis and spëcial chars 中文"},
            step_index=0,
            action_index=0
        )
        
        step = ParsedStep(step_index=0, actions=[action])
        data = ParsedAutomationData(steps=[step], total_actions=1)
        
        with patch.object(analyzer, 'context_collector'):
            results = analyzer.analyze_automation_data(data)
        
        assert results['total_actions'] == 1
        # Should handle unicode without crashing
        assert 'input_text' in results['action_types']


class TestActionAnalyzerIntegration:
    """Integration tests for ActionAnalyzer with other components."""
    
    @patch('browse_to_test.core.processing.action_analyzer.ContextCollector')
    def test_integration_with_context_collector(self, mock_context_collector):
        """Test integration with ContextCollector."""
        config = Config(
            processing=ProcessingConfig(
                collect_system_context=True,
                analyze_actions_with_ai=True  # Context collection requires AI to be enabled
            )
        )
        
        # Mock context collector
        mock_context = SystemContext(
            project=ProjectContext(
                project_root="/test",
                name="test-app",
                tech_stack=["react"],
                test_frameworks=["playwright"]
            )
        )
        mock_context_collector.return_value.collect_context.return_value = mock_context
        
        # Create a mock AI provider too since we're enabling AI
        mock_ai = Mock(spec=AIProvider)
        mock_ai.analyze_with_context.return_value = AIResponse(
            content="Test analysis", model="test", provider="test", tokens_used=50
        )
        
        analyzer = ActionAnalyzer(mock_ai, config)
        analyzer.context_collector = mock_context_collector.return_value
        
        action = ParsedAction("click", {}, 0, 0)
        step = ParsedStep(0, [action])
        data = ParsedAutomationData([step], 1)
        
        results = analyzer.analyze_automation_data(data, target_url="https://test.com")
        
        # Verify context collector was called
        mock_context_collector.return_value.collect_context.assert_called_once_with(
            target_url="https://test.com", 
            force_refresh=False
        )
        
        assert results['has_context'] == True
    
    def test_integration_with_ai_provider(self):
        """Test integration with AI provider."""
        mock_ai = Mock(spec=AIProvider)
        mock_ai.analyze_with_context.return_value = AIResponse(
            content="Test analysis response",
            model="test-model",
            provider="test",
            tokens_used=100
        )
        
        config = Config(
            processing=ProcessingConfig(
                analyze_actions_with_ai=True,
                collect_system_context=False
            )
        )
        
        analyzer = ActionAnalyzer(mock_ai, config)
        
        action = ParsedAction("click", {}, 0, 0)
        step = ParsedStep(0, [action])
        data = ParsedAutomationData([step], 1)
        
        with patch.object(analyzer, 'context_collector'):
            results = analyzer.analyze_automation_data(data)
        
        mock_ai.analyze_with_context.assert_called_once()
        assert results['has_ai_analysis'] == True
    
    def test_caching_with_complex_data(self):
        """Test caching behavior with complex analysis data."""
        config = Config()
        analyzer = ActionAnalyzer(None, config)
        
        # Complex analysis result
        complex_result = {
            'total_actions': 10,
            'action_types': {'click': 5, 'input': 3, 'navigate': 2},
            'selector_analysis': {'total_selectors': 8, 'quality_score': 0.75},
            'recommendations': ['Use data-testid', 'Add waits', 'Error handling'],
            'metadata': {'analysis_time': datetime.now().isoformat()}
        }
        
        cache_key = "complex_analysis_123"
        
        # Cache the result
        analyzer.cache_analysis(cache_key, complex_result)
        
        # Retrieve and verify
        cached = analyzer.get_cached_analysis(cache_key)
        assert cached == complex_result
        assert cached['total_actions'] == 10
        assert len(cached['recommendations']) == 3
        
        # Test cache persistence across multiple operations
        for i in range(5):
            additional_key = f"test_{i}"
            analyzer.cache_analysis(additional_key, {"test": i})
        
        # Original should still be there
        assert analyzer.get_cached_analysis(cache_key) == complex_result
        
        # Clear and verify all gone
        analyzer.clear_cache()
        assert analyzer.get_cached_analysis(cache_key) is None
        assert analyzer.get_cached_analysis("test_0") is None 