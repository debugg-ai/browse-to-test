#!/usr/bin/env python3
"""AI-powered action analysis and optimization with system context support."""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import json

from ...ai.unified import AIProvider, AIProviderError
from ...ai import AIAnalysisRequest, AnalysisType
from .input_parser import ParsedAutomationData, ParsedAction
from .context_collector import ContextCollector, SystemContext
from ..config import Config


logger = logging.getLogger(__name__)


@dataclass 
class ActionAnalysisResult:
    """Result of analyzing a single action."""

    action_index: int
    action_type: str
    reliability_score: float  # 0.0 to 1.0
    selector_quality: float  # 0.0 to 1.0
    recommended_selector: Optional[str] = None
    recommended_wait_strategy: Optional[str] = None
    potential_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    context_insights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComprehensiveAnalysisResult:
    """Result of comprehensive automation analysis with context."""

    overall_quality_score: float
    total_actions: int
    critical_actions: List[int]  # Indices of critical actions
    auxiliary_actions: List[int]  # Indices of auxiliary actions
    action_results: List[ActionAnalysisResult]
    context_recommendations: List[str] = field(default_factory=list)
    integration_suggestions: List[str] = field(default_factory=list)
    test_data_recommendations: List[str] = field(default_factory=list)
    reliability_concerns: List[str] = field(default_factory=list)
    framework_optimizations: List[str] = field(default_factory=list)
    similar_tests: List[Dict[str, Any]] = field(default_factory=list)
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)


class ActionAnalyzer:
    """Analyzes automation actions with AI and system context support."""
    
    def __init__(self, config_or_ai_provider, config_or_ai_provider_2=None):
        """
        Initialize ActionAnalyzer with backward compatibility.
        
        Supports both:
        - ActionAnalyzer(config, ai_provider) - new style
        - ActionAnalyzer(ai_provider, config) - old style for backward compatibility
        """
        # Determine which parameters are which based on type
        if hasattr(config_or_ai_provider, 'framework'):
            # First parameter is Config (new style)
            self.config = config_or_ai_provider
            self.ai_provider = config_or_ai_provider_2
        else:
            # First parameter is ai_provider (old style)
            self.ai_provider = config_or_ai_provider
            self.config = config_or_ai_provider_2
            
        self.context_collector = ContextCollector(self.config)
        
        # Analysis cache to avoid redundant AI calls
        self._analysis_cache: Dict[str, Any] = {}
        
        # Context cache
        self._context_cache: Dict[str, SystemContext] = {}
        
        # Initialize advanced caching
        self._init_cache()
        
    def analyze_automation_data(
        self, 
        parsed_data: ParsedAutomationData,
        target_url: Optional[str] = None,
        use_intelligent_analysis: bool = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of automation data with system context.
        
        Args:
            parsed_data: Parsed automation data to analyze
            target_url: URL being tested (helps with context filtering)
            use_intelligent_analysis: Whether to use AI for intelligent analysis
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        
        # Determine if we should use intelligent analysis
        if use_intelligent_analysis is None:
            use_intelligent_analysis = getattr(self.config, 'enable_ai_analysis', True)
            
        # Collect system context if enabled
        system_context = None
        if getattr(self.config, 'enable_ai_analysis', True):
            try:
                system_context = self.context_collector.collect_context(
                    target_url=target_url,
                    force_refresh=False
                )
            except Exception as e:
                if self.config and getattr(self.config, 'debug', False):
                    print(f"Warning: Could not collect system context: {e}")
        
        # Perform basic analysis first
        basic_results = self._analyze_basic_patterns(parsed_data)
        
        # Enhance with AI analysis if enabled
        if use_intelligent_analysis and self.ai_provider:
            try:
                if system_context:
                    # Use intelligent analysis with full context
                    ai_results = self._perform_intelligent_analysis(
                        parsed_data, system_context, target_url
                    )
                else:
                    # Use basic AI analysis without context
                    ai_results = self._perform_basic_ai_analysis(parsed_data)
                    
                # Merge basic and AI results
                enhanced_results = self._merge_analysis_results(basic_results, ai_results)
                enhanced_results['has_ai_analysis'] = True
                enhanced_results['has_context'] = system_context is not None
                
                return enhanced_results
                
            except Exception as e:
                if self.config and getattr(self.config, 'debug', False):
                    print(f"Warning: AI analysis failed: {e}")
                    
                # Fall back to basic analysis
                basic_results['has_ai_analysis'] = False
                basic_results['ai_analysis_error'] = str(e)
                basic_results['has_context'] = system_context is not None
                
                return basic_results
                
        # No AI analysis was attempted
        basic_results['has_ai_analysis'] = False
        basic_results['has_context'] = system_context is not None
        
        return basic_results
    
    async def analyze_automation_data_async(
        self, 
        parsed_data: ParsedAutomationData,
        target_url: Optional[str] = None,
        use_intelligent_analysis: bool = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of automation data with system context asynchronously.
        
        Args:
            parsed_data: Parsed automation data to analyze
            target_url: URL being tested (helps with context filtering)
            use_intelligent_analysis: Whether to use AI for intelligent analysis
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        
        # Determine if we should use intelligent analysis
        if use_intelligent_analysis is None:
            use_intelligent_analysis = getattr(self.config, 'enable_ai_analysis', True)
            
        # Collect system context if enabled (this can remain sync as it's typically fast)
        system_context = None
        if getattr(self.config, 'enable_ai_analysis', True):
            try:
                system_context = self.context_collector.collect_context(
                    target_url=target_url,
                    force_refresh=False
                )
            except Exception as e:
                if self.config and getattr(self.config, 'debug', False):
                    print(f"Warning: Could not collect system context: {e}")
        
        # Perform basic analysis first (sync, fast)
        basic_results = self._analyze_basic_patterns(parsed_data)
        
        # Enhanced analysis with AI (async)
        if use_intelligent_analysis and self.ai_provider:
            try:
                # Perform intelligent analysis directly (will be queued at higher level)
                intelligent_results = await self._perform_intelligent_analysis_async(
                    parsed_data, system_context, target_url
                )
                
                # Merge results and add analysis flags
                enhanced_results = self._merge_analysis_results(basic_results, intelligent_results)
                enhanced_results['has_ai_analysis'] = True
                enhanced_results['has_context'] = system_context is not None
                
                return enhanced_results
                
            except Exception as e:
                if self.config and getattr(self.config, 'debug', False):
                    print(f"Warning: AI analysis failed: {e}")
                # Fall back to basic results
                basic_results['has_ai_analysis'] = False
                basic_results['ai_analysis_error'] = str(e)
                basic_results['has_context'] = system_context is not None
                
                return basic_results
        else:
            # No AI analysis was attempted
            basic_results['has_ai_analysis'] = False
            basic_results['has_context'] = system_context is not None
            
            return basic_results
    
    def analyze_comprehensive(
        self,
        parsed_data: ParsedAutomationData,
        system_context: Optional[SystemContext] = None,
        target_url: Optional[str] = None
    ) -> ComprehensiveAnalysisResult:
        """
        Perform comprehensive analysis using AI.
        
        This is the main entry point for AI-powered analysis.
        """
        analysis_start_time = time.time()
        logger.info(f"🔍 Starting comprehensive analysis - "
                   f"Steps: {len(parsed_data.steps)}, "
                   f"Actions: {parsed_data.total_actions}, "
                   f"Has context: {'Yes' if system_context else 'No'}")
        
        if not self.ai_provider:
            raise ValueError("AI provider is required for comprehensive analysis")
        
        # Check if there are any valid actions to analyze
        if parsed_data.total_actions == 0:
            # Return empty analysis result for data with no valid actions
            return ComprehensiveAnalysisResult(
                overall_quality_score=0.0,
                total_actions=0,
                critical_actions=[],
                auxiliary_actions=[],
                action_results=[],
                context_recommendations=["No valid actions found in automation data"],
                integration_suggestions=[],
                test_data_recommendations=[],
                reliability_concerns=["Automation data contains no actionable steps"],
                framework_optimizations=[],
                similar_tests=[],
                analysis_metadata={"skip_reason": "no_valid_actions"}
            )
        
        # Create analysis request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.COMPREHENSIVE,
            automation_data=parsed_data.to_dict(),
            system_context=system_context,
            target_framework=getattr(self.config, 'framework', 'playwright'),
            target_url=target_url
        )
        
        # Get AI response
        response = self.ai_provider.analyze_with_context(request)
        
        # Parse response into structured result
        result = self._parse_comprehensive_response(response, parsed_data)
        
        analysis_end_time = time.time()
        analysis_duration = analysis_end_time - analysis_start_time
        logger.info(f"✅ Comprehensive analysis completed in {analysis_duration:.2f}s - "
                   f"Quality score: {result.overall_quality_score:.2f}")
        
        return result
    
    async def analyze_comprehensive_async(
        self,
        parsed_data: ParsedAutomationData,
        system_context: Optional[SystemContext] = None,
        target_url: Optional[str] = None
    ) -> ComprehensiveAnalysisResult:
        """
        Perform comprehensive analysis using AI asynchronously.
        
        This is the main entry point for AI-powered analysis.
        """
        analysis_start_time = time.time()
        logger.info(f"🔍 Starting async comprehensive analysis - "
                   f"Steps: {len(parsed_data.steps)}, "
                   f"Actions: {parsed_data.total_actions}, "
                   f"Has context: {'Yes' if system_context else 'No'}")
        
        if not self.ai_provider:
            raise ValueError("AI provider is required for comprehensive analysis")
        
        # Check if there are any valid actions to analyze
        if parsed_data.total_actions == 0:
            # Return empty analysis result for data with no valid actions
            return ComprehensiveAnalysisResult(
                overall_quality_score=0.0,
                total_actions=0,
                critical_actions=[],
                auxiliary_actions=[],
                action_results=[],
                context_recommendations=["No valid actions found in automation data"],
                integration_suggestions=[],
                test_data_recommendations=[],
                reliability_concerns=["Automation data contains no actionable steps"],
                framework_optimizations=[],
                similar_tests=[],
                analysis_metadata={"skip_reason": "no_valid_actions"}
            )
        
        # Create analysis request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.COMPREHENSIVE,
            automation_data=parsed_data.to_dict(),
            system_context=system_context,
            target_framework=getattr(self.config, 'framework', 'playwright'),
            target_url=target_url
        )
        
        # Get AI response directly (will be queued at higher level)
        response = await self.ai_provider.analyze_with_context_async(request)
        
        # Parse response into structured result
        result = self._parse_comprehensive_response(response, parsed_data)
        
        analysis_end_time = time.time()
        analysis_duration = analysis_end_time - analysis_start_time
        logger.info(f"✅ Async comprehensive analysis completed in {analysis_duration:.2f}s - "
                   f"Quality score: {result.overall_quality_score:.2f}")
        
        return result
    
    async def _perform_intelligent_analysis_async(
        self,
        parsed_data: ParsedAutomationData,
        system_context: Optional[SystemContext],
        target_url: Optional[str]
    ) -> Dict[str, Any]:
        """
        Perform intelligent analysis with AI asynchronously.
        
        This is a helper method that's called as an async task.
        """
        # Create analysis request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.OPTIMIZATION,
            automation_data=parsed_data.to_dict(),
            system_context=system_context,
            target_framework=getattr(self.config, 'framework', 'playwright'),
            target_url=target_url
        )
        
        # Use async AI provider
        response = await self.ai_provider.analyze_with_context_async(request)
        
        # Extract insights from response
        return {
            'ai_insights': response.content,
            'ai_metadata': response.metadata,
            'response_time': response.response_time,
            'quality_score': self._calculate_ai_quality_score(response),
            'recommendations': self._extract_recommendations(response.content)
        }
    
    def _perform_intelligent_analysis(
        self, 
        parsed_data: ParsedAutomationData, 
        system_context: SystemContext,
        target_url: Optional[str] = None
    ) -> ComprehensiveAnalysisResult:
        """Perform intelligent analysis leveraging system context."""
        
        # Create analysis request
        analysis_request = AIAnalysisRequest(
            analysis_type=AnalysisType.INTELLIGENT_ANALYSIS,
            automation_data=self._convert_parsed_data_to_dict(parsed_data),
            target_framework=getattr(self.config, 'framework', 'playwright'),
            system_context=system_context
        )
        
        # Perform AI analysis
        ai_response = self.ai_provider.analyze_with_context(analysis_request)
        
        # Parse AI response into structured results
        return self._parse_intelligent_analysis_response(ai_response, parsed_data, system_context)
    
    def _perform_basic_ai_analysis(self, parsed_data: ParsedAutomationData) -> Dict[str, Any]:
        """Perform basic AI analysis without system context."""
        
        analysis_request = AIAnalysisRequest(
            analysis_type=AnalysisType.CONVERSION,
            automation_data=self._convert_parsed_data_to_dict(parsed_data),
            target_framework=getattr(self.config, 'framework', 'playwright')
        )
        
        ai_response = self.ai_provider.analyze_with_context(analysis_request)
        
        return {
            'ai_recommendations': ai_response.content,
            'analysis_type': 'basic_ai',
            'tokens_used': ai_response.tokens_used,
            'model_used': ai_response.model
        }
    
    def _analyze_basic_patterns(self, parsed_data: ParsedAutomationData) -> Dict[str, Any]:
        """Perform basic pattern analysis without AI."""
        
        results = {
            'total_steps': len(parsed_data.steps),
            'total_actions': sum(len(step.actions) for step in parsed_data.steps),
            'action_types': {},
            'selector_analysis': {},
            'validation_issues': [],
            'basic_recommendations': [],
        }
        
        # Analyze action type distribution
        for step in parsed_data.steps:
            for action in step.actions:
                action_type = action.action_type
                if action_type not in results['action_types']:
                    results['action_types'][action_type] = 0
                results['action_types'][action_type] += 1
        
        # Analyze selectors
        selectors = []
        for step in parsed_data.steps:
            for action in step.actions:
                if action.selector_info:
                    selectors.append(action.selector_info)
        
        results['selector_analysis'] = self._analyze_selectors(selectors)
        
        # Basic validation
        results['validation_issues'] = self._validate_basic_patterns(parsed_data)
        
        # Basic recommendations
        results['basic_recommendations'] = self._generate_basic_recommendations(parsed_data)
        
        return results
    
    def _analyze_selectors(self, selectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze selector quality and patterns."""
        
        if not selectors:
            return {'total_selectors': 0}
        
        analysis = {
            'total_selectors': len(selectors),
            'selector_types': {},
            'quality_issues': [],
            'recommendations': []
        }
        
        for selector_info in selectors:
            # Categorize selector types
            if 'css_selector' in selector_info:
                css = selector_info['css_selector']
                if css.startswith('#'):
                    selector_type = 'id'
                elif css.startswith('.'):
                    selector_type = 'class'
                elif '[data-testid' in css:
                    selector_type = 'test_id'
                else:
                    selector_type = 'other_css'
            elif 'xpath' in selector_info:
                selector_type = 'xpath'
            else:
                selector_type = 'unknown'
            
            if selector_type not in analysis['selector_types']:
                analysis['selector_types'][selector_type] = 0
            analysis['selector_types'][selector_type] += 1
        
        # Generate selector recommendations
        if analysis['selector_types'].get('xpath', 0) > analysis['selector_types'].get('test_id', 0):
            analysis['recommendations'].append("Consider using data-testid attributes instead of XPath for better reliability")
        
        if analysis['selector_types'].get('class', 0) > analysis['selector_types'].get('id', 0):
            analysis['recommendations'].append("Prefer ID selectors over class selectors when possible")
        
        return analysis
    
    def _validate_basic_patterns(self, parsed_data: ParsedAutomationData) -> List[str]:
        """Validate automation patterns for common issues."""
        
        issues = []
        
        # Check for missing waits after navigation
        for i, step in enumerate(parsed_data.steps):
            for j, action in enumerate(step.actions):
                if action.action_type == 'go_to_url':
                    # Check if next action has appropriate wait
                    if j + 1 < len(step.actions):
                        next_action = step.actions[j + 1]
                        if next_action.action_type not in ['wait', 'wait_for_element']:
                            issues.append(f"Step {i+1}: Consider adding wait after navigation")
                    elif i + 1 < len(parsed_data.steps):
                        next_step = parsed_data.steps[i + 1]
                        if next_step.actions and next_step.actions[0].action_type not in ['wait', 'wait_for_element']:
                            issues.append(f"Step {i+1}: Consider adding wait after navigation")
        
        # Check for actions without selectors that might need them
        for i, step in enumerate(parsed_data.steps):
            for j, action in enumerate(step.actions):
                if action.action_type in ['click_element', 'input_text'] and not action.selector_info:
                    issues.append(f"Step {i+1}, Action {j+1}: Missing selector information for {action.action_type}")
        
        # Check for sensitive data patterns
        sensitive_patterns = ['password', 'email', 'username', 'secret', 'key', 'token']
        for i, step in enumerate(parsed_data.steps):
            for j, action in enumerate(step.actions):
                if action.action_type == 'input_text':
                    text_value = action.parameters.get('text', '').lower()
                    if any(pattern in text_value for pattern in sensitive_patterns):
                        issues.append(f"Step {i+1}, Action {j+1}: Potential sensitive data in input")
        
        return issues
    
    def _generate_basic_recommendations(self, parsed_data: ParsedAutomationData) -> List[str]:
        """Generate basic recommendations for improvement."""
        
        recommendations = []
        
        # Analyze action patterns
        action_counts = {}
        for step in parsed_data.steps:
            for action in step.actions:
                action_type = action.action_type
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        # Recommend waits if many interactions
        if action_counts.get('click_element', 0) > 3:
            recommendations.append("Consider adding explicit waits between interactions for better reliability")
        
        # Recommend error handling
        if action_counts.get('input_text', 0) > 2:
            recommendations.append("Add validation checks after form inputs")
        
        # Recommend screenshots for debugging
        if len(parsed_data.steps) > 5:
            recommendations.append("Consider adding screenshots at key points for debugging")
        
        return recommendations
    
    def _parse_comprehensive_response(
        self, 
        ai_response: Any, 
        parsed_data: ParsedAutomationData,
        system_context: Optional[SystemContext] = None
    ) -> ComprehensiveAnalysisResult:
        """Parse AI response into comprehensive analysis results."""
        return self._parse_intelligent_analysis_response(ai_response, parsed_data, system_context)
    
    def _parse_intelligent_analysis_response(
        self, 
        ai_response: Any, 
        parsed_data: ParsedAutomationData,
        system_context: SystemContext
    ) -> ComprehensiveAnalysisResult:
        """Parse AI response into structured analysis results."""
        
        # Create basic result structure
        result = ComprehensiveAnalysisResult(
            overall_quality_score=0.8,  # Default score
            total_actions=sum(len(step.actions) for step in parsed_data.steps),
            critical_actions=[],
            auxiliary_actions=[],
            action_results=[],
            analysis_metadata={
                'ai_model': ai_response.model,
                'tokens_used': ai_response.tokens_used,
                'analysis_timestamp': datetime.now().isoformat(),
                'has_system_context': True
            }
        )
        
        # Parse AI response content (this is simplified - in practice, you'd want more sophisticated parsing)
        ai_content = ai_response.content.lower()
        
        # Extract context recommendations
        if 'existing test' in ai_content or 'similar test' in ai_content:
            result.context_recommendations.append("Leverage patterns from existing tests")
        
        if 'data-testid' in ai_content or 'test id' in ai_content:
            result.framework_optimizations.append("Use data-testid selectors for consistency")
        
        if 'error handling' in ai_content:
            result.framework_optimizations.append("Implement comprehensive error handling")
        
        if 'sensitive data' in ai_content or 'environment variable' in ai_content:
            result.test_data_recommendations.append("Use environment variables for sensitive data")
        
        # Identify similar tests from context
        if system_context and system_context.existing_tests:
            # Simple similarity matching (could be enhanced with more sophisticated analysis)
            target_actions = set()
            for step in parsed_data.steps:
                for action in step.actions:
                    target_actions.add(action.action_type)
            
            for test in system_context.existing_tests[:5]:
                test_actions = set(test.actions)
                overlap = len(target_actions.intersection(test_actions)) / max(len(target_actions.union(test_actions)), 1)
                if overlap > 0.3:  # 30% similarity threshold
                    result.similar_tests.append({
                        'file_path': test.file_path,
                        'framework': test.framework,
                        'similarity_score': overlap,
                        'common_actions': list(target_actions.intersection(test_actions))
                    })
        
        # Analyze individual actions
        action_index = 0
        for step_index, step in enumerate(parsed_data.steps):
            for action in step.actions:
                action_result = ActionAnalysisResult(
                    action_index=action_index,
                    action_type=action.action_type,
                    reliability_score=self._calculate_action_reliability(action, ai_content),
                    selector_quality=self._calculate_selector_quality(action),
                    metadata={'step_index': step_index}
                )
                
                # Categorize as critical or auxiliary
                if action.action_type in ['click_element', 'input_text', 'go_to_url']:
                    result.critical_actions.append(action_index)
                else:
                    result.auxiliary_actions.append(action_index)
                
                # Extract context insights from AI response
                if action.action_type in ai_content:
                    action_result.context_insights.append(f"AI identified {action.action_type} as important")
                
                result.action_results.append(action_result)
                action_index += 1
        
        # Calculate overall quality score
        if result.action_results:
            avg_reliability = sum(ar.reliability_score for ar in result.action_results) / len(result.action_results)
            avg_selector_quality = sum(ar.selector_quality for ar in result.action_results) / len(result.action_results)
            result.overall_quality_score = (avg_reliability + avg_selector_quality) / 2
        
        return result
    
    def _calculate_action_reliability(self, action: ParsedAction, ai_content: str) -> float:
        """Calculate reliability score for an action."""
        
        base_score = 0.7
        
        # Higher score for actions with good selectors
        if action.selector_info:
            if 'data-testid' in str(action.selector_info):
                base_score += 0.2
            elif 'id' in str(action.selector_info):
                base_score += 0.1
            elif 'xpath' in str(action.selector_info):
                base_score -= 0.1
        
        # Adjust based on action type
        if action.action_type in ['go_to_url', 'wait']:
            base_score += 0.1
        elif action.action_type in ['scroll_down', 'scroll_up']:
            base_score -= 0.1
        
        # AI feedback adjustment
        if action.action_type in ai_content and 'reliable' in ai_content:
            base_score += 0.1
        
        return min(1.0, max(0.0, base_score))
    
    def _calculate_selector_quality(self, action: ParsedAction) -> float:
        """Calculate selector quality score."""
        
        if not action.selector_info:
            return 0.5
        
        selector_info = action.selector_info
        score = 0.6
        
        # Prefer data attributes
        if 'data-testid' in str(selector_info):
            score = 0.9
        elif 'data-' in str(selector_info):
            score = 0.8
        elif 'id' in str(selector_info):
            score = 0.7
        elif 'class' in str(selector_info):
            score = 0.6
        elif 'xpath' in str(selector_info):
            score = 0.4
        
        return score
    
    def _merge_analysis_results(self, basic_results: Dict[str, Any], ai_results: Any) -> Dict[str, Any]:
        """Merge basic analysis with AI analysis results."""
        
        merged = basic_results.copy()
        
        if isinstance(ai_results, ComprehensiveAnalysisResult):
            merged.update({
                'comprehensive_analysis': {
                    'overall_quality_score': ai_results.overall_quality_score,
                    'critical_actions': ai_results.critical_actions,
                    'auxiliary_actions': ai_results.auxiliary_actions,
                    'context_recommendations': ai_results.context_recommendations,
                    'integration_suggestions': ai_results.integration_suggestions,
                    'test_data_recommendations': ai_results.test_data_recommendations,
                    'framework_optimizations': ai_results.framework_optimizations,
                    'similar_tests': ai_results.similar_tests,
                    'action_analysis': [
                        {
                            'action_index': ar.action_index,
                            'action_type': ar.action_type,
                            'reliability_score': ar.reliability_score,
                            'selector_quality': ar.selector_quality,
                            'context_insights': ar.context_insights,
                            'suggestions': ar.suggestions
                        }
                        for ar in ai_results.action_results
                    ]
                },
                'analysis_metadata': ai_results.analysis_metadata
            })
        else:
            # Handle simple AI results
            merged['ai_analysis'] = ai_results
        
        return merged
    
    def _convert_parsed_data_to_dict(self, parsed_data: ParsedAutomationData) -> List[Dict[str, Any]]:
        """Convert parsed data back to dictionary format for AI analysis."""
        
        result = []
        for step in parsed_data.steps:
            step_dict = {
                'model_output': {
                    'action': []
                },
                'state': {
                    'interacted_element': []
                },
                'metadata': step.metadata or {}
            }
            
            for action in step.actions:
                action_dict = {action.action_type: action.parameters}
                step_dict['model_output']['action'].append(action_dict)
                
                if action.selector_info:
                    step_dict['state']['interacted_element'].append(action.selector_info)
            
            result.append(step_dict)
        
        return result
    
    def analyze_single_action(
        self, 
        action: ParsedAction, 
        context: Optional[Dict[str, Any]] = None
    ) -> ActionAnalysisResult:
        """Analyze a single action for optimization opportunities."""
        
        if not getattr(self.config, 'enable_ai_analysis', True) or not self.ai_provider:
            # Return basic analysis
            return ActionAnalysisResult(
                action_index=action.action_index,
                action_type=action.action_type,
                reliability_score=self._calculate_action_reliability(action, ""),
                selector_quality=self._calculate_selector_quality(action)
            )
        
        # Create optimization request
        analysis_request = AIAnalysisRequest(
            analysis_type=AnalysisType.OPTIMIZATION,
            automation_data=[],  # Not needed for single action analysis
            target_framework=getattr(self.config, 'framework', 'playwright'),
            current_action=self._action_to_dict(action),
            system_context=context
        )
        
        try:
            ai_response = self.ai_provider.analyze_with_context(analysis_request)
            return self._parse_single_action_response(ai_response, action)
        except Exception as e:
            if getattr(self.config, 'debug', False):
                logger.warning(f"Single action AI analysis failed: {e}")
            
            # Fall back to basic analysis
            return ActionAnalysisResult(
                action_index=getattr(action, 'action_index', 0),
                action_type=action.action_type,
                reliability_score=self._calculate_action_reliability(action, ""),
                selector_quality=self._calculate_selector_quality(action),
                potential_issues=[f"AI analysis failed: {str(e)}"]
            )
    
    def _action_to_dict(self, action: ParsedAction) -> Dict[str, Any]:
        """Convert action to dictionary format."""
        return {
            'action_type': action.action_type,
            'parameters': action.parameters,
            'selector_info': action.selector_info,
            'metadata': action.metadata
        }
    
    def _parse_single_action_response(self, ai_response: Any, action: ParsedAction) -> ActionAnalysisResult:
        """Parse AI response for single action analysis."""
        
        result = ActionAnalysisResult(
            action_index=action.action_index,
            action_type=action.action_type,
            reliability_score=self._calculate_action_reliability(action, ai_response.content),
            selector_quality=self._calculate_selector_quality(action)
        )
        
        # Extract suggestions from AI response
        content = ai_response.content.lower()
        
        if 'data-testid' in content:
            result.suggestions.append("Consider using data-testid selectors")
        
        if 'wait' in content:
            result.suggestions.append("Add explicit wait strategy")
        
        if 'error' in content:
            result.suggestions.append("Implement error handling")
        
        return result
    
    def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result."""
        return self._analysis_cache.get(cache_key)
    
    def cache_analysis(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache analysis result."""
        self._analysis_cache[cache_key] = result
    
    def clear_cache(self) -> None:
        """Clear analysis cache."""
        self._analysis_cache.clear()
        self._context_cache.clear()
    
    def _init_cache(self):
        """Initialize advanced caching system."""
        self._cache_ttl = timedelta(hours=1)  # 1 hour TTL
        self._cache_timestamps = {}
        self._cache_hit_count = {}
        self._max_cache_size = 100
        
    def _generate_cache_key(
        self,
        parsed_data: ParsedAutomationData,
        system_context: Optional[SystemContext],
        target_url: Optional[str],
        analysis_type: AnalysisType
    ) -> str:
        """Generate a unique cache key for the analysis request."""
        # Create a hashable representation
        cache_data = {
            'analysis_type': analysis_type.value,
            'framework': getattr(self.config, 'framework', 'playwright'),
            'target_url': target_url or '',
            'steps': []
        }
        
        # Add step data
        for step in parsed_data.steps:
            step_data = {
                'actions': [
                    {
                        'type': action.action_type,
                        'params': json.dumps(action.parameters, sort_keys=True),
                        'selector': str(action.selector_info)
                    }
                    for action in step.actions
                ]
            }
            cache_data['steps'].append(step_data)
        
        # Add context fingerprint if available
        if system_context:
            cache_data['context_fingerprint'] = self._create_context_fingerprint(system_context)
        
        # Generate hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def _create_context_fingerprint(self, context: SystemContext) -> str:
        """Create a lightweight fingerprint of the system context."""
        fingerprint_parts = []
        
        if hasattr(context, 'project') and context.project:
            if hasattr(context.project, 'name'):
                fingerprint_parts.append(f"proj:{context.project.name}")
            if hasattr(context.project, 'test_frameworks'):
                fingerprint_parts.append(f"fw:{','.join(context.project.test_frameworks)}")
        
        if hasattr(context, 'existing_tests'):
            fingerprint_parts.append(f"tests:{len(context.existing_tests)}")
        
        if hasattr(context, 'ui_components'):
            fingerprint_parts.append(f"ui:{len(context.ui_components)}")
        
        return '|'.join(fingerprint_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Retrieve item from cache if valid."""
        if cache_key not in self._analysis_cache:
            return None
        
        # Check TTL
        if cache_key in self._cache_timestamps:
            timestamp = self._cache_timestamps[cache_key]
            if datetime.now() - timestamp > self._cache_ttl:
                # Expired
                self._remove_from_cache(cache_key)
                return None
        
        # Update hit count
        self._cache_hit_count[cache_key] = self._cache_hit_count.get(cache_key, 0) + 1
        
        return self._analysis_cache[cache_key]
    
    def _add_to_cache(self, cache_key: str, value: Any):
        """Add item to cache with TTL and size management."""
        # Check cache size
        if len(self._analysis_cache) >= self._max_cache_size:
            self._evict_lru_item()
        
        # Add to cache
        self._analysis_cache[cache_key] = value
        self._cache_timestamps[cache_key] = datetime.now()
        self._cache_hit_count[cache_key] = 0
    
    def _remove_from_cache(self, cache_key: str):
        """Remove item from cache."""
        if cache_key in self._analysis_cache:
            del self._analysis_cache[cache_key]
        if cache_key in self._cache_timestamps:
            del self._cache_timestamps[cache_key]
        if cache_key in self._cache_hit_count:
            del self._cache_hit_count[cache_key]
    
    def _evict_lru_item(self):
        """Evict least recently used item from cache."""
        if not self._analysis_cache:
            return
        
        # Find LRU item (oldest timestamp with lowest hit count)
        lru_key = None
        oldest_time = datetime.now()
        lowest_hits = float('inf')
        
        for key, timestamp in self._cache_timestamps.items():
            hits = self._cache_hit_count.get(key, 0)
            
            # Prioritize by hit count, then by age
            if hits < lowest_hits or (hits == lowest_hits and timestamp < oldest_time):
                lru_key = key
                oldest_time = timestamp
                lowest_hits = hits
        
        if lru_key:
            self._remove_from_cache(lru_key)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_hits = sum(self._cache_hit_count.values())
        cache_size = len(self._analysis_cache)
        
        return {
            'cache_size': cache_size,
            'max_cache_size': self._max_cache_size,
            'total_hits': total_hits,
            'hit_distribution': dict(self._cache_hit_count),
            'oldest_entry_age': min(
                (datetime.now() - ts).total_seconds()
                for ts in self._cache_timestamps.values()
            ) if self._cache_timestamps else 0,
            'ttl_seconds': self._cache_ttl.total_seconds()
        }
    
    def _convert_step_to_analysis_format(self, step) -> Dict[str, Any]:
        """
        Convert a step object to a format suitable for AI analysis.
        
        Args:
            step: Step object (could be ParsedStep, dict, or other format)
            
        Returns:
            Dictionary representation for AI analysis
        """
        try:
            # Handle ParsedStep objects
            if hasattr(step, 'actions') and hasattr(step, 'metadata'):
                step_dict = {
                    'model_output': {
                        'action': []
                    },
                    'state': {
                        'interacted_element': []
                    },
                    'metadata': step.metadata or {}
                }
                
                for action in step.actions:
                    action_dict = {action.action_type: action.parameters}
                    step_dict['model_output']['action'].append(action_dict)
                    
                    if action.selector_info:
                        step_dict['state']['interacted_element'].append(action.selector_info)
                        
                return step_dict
            
            # Handle dictionary format
            elif isinstance(step, dict):
                # If it's already in the right format, return as-is
                if 'model_output' in step or 'action' in step:
                    return step
                
                # Try to extract action information
                actions = step.get('actions', [])
                if not actions and 'action' in step:
                    actions = step['action'] if isinstance(step['action'], list) else [step['action']]
                
                step_dict = {
                    'model_output': {
                        'action': actions
                    },
                    'state': {
                        'interacted_element': step.get('interacted_element', [])
                    },
                    'metadata': step.get('metadata', {})
                }
                
                return step_dict
            
            # Fallback for unknown formats
            else:
                logger.warning(f"Unknown step format: {type(step)}, using minimal representation")
                return {
                    'model_output': {
                        'action': [{'unknown_action': str(step)}]
                    },
                    'state': {
                        'interacted_element': []
                    },
                    'metadata': {}
                }
                
        except Exception as e:
            logger.error(f"Failed to convert step to analysis format: {e}")
            # Return minimal safe format
            return {
                'model_output': {
                    'action': [{'error': 'conversion_failed'}]
                },
                'state': {
                    'interacted_element': []
                },
                'metadata': {'conversion_error': str(e)}
            }
    
    def _parse_step_analysis_response(self, ai_response: Any, original_step) -> Dict[str, Any]:
        """
        Parse AI response for single step analysis and extract actionable insights.
        
        Args:
            ai_response: Response from AI provider
            original_step: Original step that was analyzed
            
        Returns:
            Dictionary with extracted insights
        """
        try:
            content = ai_response.content.lower()
            insights = {
                'reliability_score': 0.8,  # Default baseline
                'selector_quality': 0.8,   # Default baseline
                'suggestions': [],
                'potential_issues': [],
                'improvements': []
            }
            
            # Extract reliability indicators from AI response
            if 'reliable' in content and 'very' in content:
                insights['reliability_score'] = 0.95
            elif 'reliable' in content:
                insights['reliability_score'] = 0.85
            elif 'unreliable' in content or 'brittle' in content:
                insights['reliability_score'] = 0.6
            elif 'flaky' in content or 'unstable' in content:
                insights['reliability_score'] = 0.5
            
            # Extract selector quality indicators
            if 'data-testid' in content or 'test id' in content:
                insights['selector_quality'] = 0.95
                insights['suggestions'].append("Continue using data-testid selectors for reliability")
            elif 'id selector' in content or 'unique id' in content:
                insights['selector_quality'] = 0.85
                insights['suggestions'].append("ID selectors are good, consider data-testid for tests")
            elif 'xpath' in content and ('avoid' in content or 'brittle' in content):
                insights['selector_quality'] = 0.4
                insights['potential_issues'].append("XPath selectors can be brittle and hard to maintain")
                insights['improvements'].append("Consider using data-testid or CSS selectors instead")
            elif 'class selector' in content and 'unstable' in content:
                insights['selector_quality'] = 0.6
                insights['potential_issues'].append("Class-based selectors may break with CSS changes")
            
            # Extract specific suggestions
            if 'wait' in content and ('add' in content or 'include' in content):
                insights['suggestions'].append("Add explicit wait conditions for better stability")
            
            if 'timeout' in content:
                insights['suggestions'].append("Consider adjusting timeout values for this action")
            
            if 'error handling' in content or 'exception' in content:
                insights['improvements'].append("Add error handling for this step")
            
            if 'screenshot' in content or 'debug' in content:
                insights['improvements'].append("Add screenshot capture for debugging purposes")
            
            # Extract performance suggestions
            if 'slow' in content or 'performance' in content:
                insights['potential_issues'].append("This action may impact test performance")
                insights['improvements'].append("Consider optimizing for faster execution")
            
            # Extract maintainability suggestions
            if 'maintainability' in content or 'readable' in content:
                insights['improvements'].append("Consider adding descriptive comments for this step")
            
            # Framework-specific suggestions
            framework = getattr(self.config, 'framework', 'playwright')
            if framework == 'playwright':
                if 'page.locator' in content:
                    insights['suggestions'].append("Using Playwright locators is recommended")
                if 'auto-wait' in content:
                    insights['suggestions'].append("Leverage Playwright's built-in auto-waiting")
            elif framework == 'selenium':
                if 'webdriverwait' in content:
                    insights['suggestions'].append("Use WebDriverWait for explicit waits")
                if 'expected_conditions' in content:
                    insights['suggestions'].append("Leverage Selenium's expected conditions")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to parse AI step analysis response: {e}")
            # Return safe defaults
            return {
                'reliability_score': 0.7,
                'selector_quality': 0.7,
                'suggestions': ["AI analysis parsing failed - using defaults"],
                'potential_issues': [f"Analysis parsing error: {str(e)}"],
                'improvements': []
            }
    
    def analyze_steps(self, steps):
        """Analyze steps for the executor (sync version)."""
        # Simple pass-through for now - can be enhanced later
        return steps
    
    async def analyze_steps_async(self, steps):
        """Analyze steps for the executor (async version).""" 
        # Simple pass-through for now - can be enhanced later
        return steps
    
    def analyze_single_step(self, step):
        """Analyze a single step with AI analysis if enabled."""
        if not getattr(self.config, 'enable_ai_analysis', True) or not self.ai_provider:
            # Return step unchanged if AI analysis is disabled or no AI provider
            return step
        
        try:
            start_time = time.time()
            
            # Convert step to analyzable format
            step_data = self._convert_step_to_analysis_format(step)
            
            # Create AI analysis request for single step optimization
            analysis_request = AIAnalysisRequest(
                analysis_type=AnalysisType.OPTIMIZATION,
                automation_data=[step_data],  # Single step in list format
                target_framework=getattr(self.config, 'framework', 'playwright'),
                current_action=step_data
            )
            
            # Make real AI call
            ai_response = self.ai_provider.analyze_with_context(analysis_request)
            processing_time = time.time() - start_time
            
            # Parse AI response and extract insights
            analysis_insights = self._parse_step_analysis_response(ai_response, step)
            
            # Add analysis metadata to step
            if not hasattr(step, 'analysis_metadata'):
                step.analysis_metadata = {}
                
            step.analysis_metadata.update({
                'ai_analysis_completed': True,
                'ai_processing_time': processing_time,
                'reliability_score': analysis_insights.get('reliability_score', 0.8),
                'selector_quality': analysis_insights.get('selector_quality', 0.8),
                'suggestions': analysis_insights.get('suggestions', []),
                'potential_issues': analysis_insights.get('potential_issues', []),
                'recommended_improvements': analysis_insights.get('improvements', []),
                'ai_model': ai_response.model,
                'ai_provider': ai_response.provider,
                'tokens_used': ai_response.tokens_used
            })
            
            logger.debug(f"AI step analysis completed in {processing_time:.2f}s - "
                        f"reliability: {analysis_insights.get('reliability_score', 'unknown')}")
            return step
                
        except Exception as e:
            logger.warning(f"Single step AI analysis failed: {e}")
            # Add error metadata but return step to allow continuation
            if not hasattr(step, 'analysis_metadata'):
                step.analysis_metadata = {}
            step.analysis_metadata.update({
                'ai_analysis_failed': True,
                'ai_analysis_error': str(e),
                'ai_processing_time': time.time() - start_time if 'start_time' in locals() else 0
            })
            return step
    
    async def analyze_single_step_async(self, step):
        """Analyze a single step with AI analysis if enabled (async version)."""
        if not getattr(self.config, 'enable_ai_analysis', True) or not self.ai_provider:
            # Return step unchanged if AI analysis is disabled or no AI provider
            return step
        
        try:
            start_time = time.time()
            
            # Convert step to analyzable format
            step_data = self._convert_step_to_analysis_format(step)
            
            # Create AI analysis request for single step optimization
            analysis_request = AIAnalysisRequest(
                analysis_type=AnalysisType.OPTIMIZATION,
                automation_data=[step_data],  # Single step in list format
                target_framework=getattr(self.config, 'framework', 'playwright'),
                current_action=step_data
            )
            
            # Make real async AI call
            ai_response = await self.ai_provider.analyze_with_context_async(analysis_request)
            processing_time = time.time() - start_time
            
            # Parse AI response and extract insights
            analysis_insights = self._parse_step_analysis_response(ai_response, step)
            
            # Add analysis metadata to step
            if not hasattr(step, 'analysis_metadata'):
                step.analysis_metadata = {}
                
            step.analysis_metadata.update({
                'ai_analysis_completed': True,
                'ai_processing_time': processing_time,
                'reliability_score': analysis_insights.get('reliability_score', 0.8),
                'selector_quality': analysis_insights.get('selector_quality', 0.8),
                'suggestions': analysis_insights.get('suggestions', []),
                'potential_issues': analysis_insights.get('potential_issues', []),
                'recommended_improvements': analysis_insights.get('improvements', []),
                'ai_model': ai_response.model,
                'ai_provider': ai_response.provider,
                'tokens_used': ai_response.tokens_used,
                'async_processing': True
            })
            
            logger.debug(f"Async AI step analysis completed in {processing_time:.2f}s - "
                        f"reliability: {analysis_insights.get('reliability_score', 'unknown')}")
            return step
                
        except Exception as e:
            logger.warning(f"Async single step AI analysis failed: {e}")
            # Add error metadata but return step to allow continuation
            if not hasattr(step, 'analysis_metadata'):
                step.analysis_metadata = {}
            step.analysis_metadata.update({
                'ai_analysis_failed': True,
                'ai_analysis_error': str(e),
                'ai_processing_time': time.time() - start_time if 'start_time' in locals() else 0,
                'async_processing': True
            })
            return step 