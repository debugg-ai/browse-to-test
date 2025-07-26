#!/usr/bin/env python3
"""
AI-powered action analysis and optimization with system context support.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

from ...ai.base import AIProvider, AIAnalysisRequest, AnalysisType
from .input_parser import ParsedAutomationData, ParsedAction
from .context_collector import ContextCollector, SystemContext
from ..configuration.config import Config


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
    
    def __init__(self, ai_provider: AIProvider, config: Config):
        self.ai_provider = ai_provider
        self.config = config
        self.context_collector = ContextCollector(config)
        
        # Analysis cache to avoid redundant AI calls
        self._analysis_cache: Dict[str, Any] = {}
        
        # Context cache
        self._context_cache: Dict[str, SystemContext] = {}
        
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
            use_intelligent_analysis = self.config.processing.analyze_actions_with_ai
            
        # Collect system context if enabled
        system_context = None
        if self.config.processing.analyze_actions_with_ai:
            try:
                system_context = self.context_collector.collect_context(
                    target_url=target_url,
                    force_refresh=False
                )
            except Exception as e:
                if self.config.debug:
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
                if self.config.debug:
                    print(f"Warning: AI analysis failed: {e}")
                    
                # Fall back to basic analysis
                basic_results['has_ai_analysis'] = False
                basic_results['ai_analysis_error'] = str(e)
                
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
            use_intelligent_analysis = self.config.processing.analyze_actions_with_ai
            
        # Collect system context if enabled (this can remain sync as it's typically fast)
        system_context = None
        if self.config.processing.analyze_actions_with_ai:
            try:
                system_context = self.context_collector.collect_context(
                    target_url=target_url,
                    force_refresh=False
                )
            except Exception as e:
                if self.config.debug:
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
                
                # Merge results
                return self._merge_analysis_results(basic_results, intelligent_results)
                
            except Exception as e:
                if self.config.debug:
                    print(f"Warning: AI analysis failed: {e}")
                # Fall back to basic results
                return basic_results
        else:
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
        if not self.ai_provider:
            raise ValueError("AI provider is required for comprehensive analysis")
        
        # Create analysis request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.COMPREHENSIVE,
            automation_data=parsed_data.to_dict(),
            system_context=system_context,
            target_framework=self.config.output.framework,
            target_url=target_url
        )
        
        # Get AI response
        response = self.ai_provider.analyze_with_context(request)
        
        # Parse response into structured result
        return self._parse_comprehensive_response(response, parsed_data)
    
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
        if not self.ai_provider:
            raise ValueError("AI provider is required for comprehensive analysis")
        
        # Create analysis request
        request = AIAnalysisRequest(
            analysis_type=AnalysisType.COMPREHENSIVE,
            automation_data=parsed_data.to_dict(),
            system_context=system_context,
            target_framework=self.config.output.framework,
            target_url=target_url
        )
        
        # Get AI response directly (will be queued at higher level)
        response = await self.ai_provider.analyze_with_context_async(request)
        
        # Parse response into structured result
        return self._parse_comprehensive_response(response, parsed_data)
    
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
            target_framework=self.config.output.framework,
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
            target_framework=self.config.output.framework,
            system_context=system_context,
            additional_context={
                'target_url': target_url,
                'config': {
                    'include_assertions': self.config.output.include_assertions,
                    'include_error_handling': self.config.output.include_error_handling,
                    'sensitive_data_keys': self.config.output.sensitive_data_keys,
                }
            }
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
            target_framework=self.config.output.framework
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
        
        if not self.config.processing.analyze_actions_with_ai or not self.ai_provider:
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
            target_framework=self.config.output.framework,
            current_action=self._action_to_dict(action),
            additional_context=context
        )
        
        try:
            ai_response = self.ai_provider.analyze_with_context(analysis_request)
            return self._parse_single_action_response(ai_response, action)
        except Exception as e:
            if self.config.debug:
                print(f"Warning: Single action AI analysis failed: {e}")
            
            # Fall back to basic analysis
            return ActionAnalysisResult(
                action_index=action.action_index,
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