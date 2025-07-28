#!/usr/bin/env python3
"""
Base classes for AI provider integration.
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AIProviderError(Exception):
    """Exception raised by AI providers for errors."""
    
    def __init__(self, message: str, provider: Optional[str] = None, model: Optional[str] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model


class AnalysisType(Enum):
    """Types of AI analysis that can be performed."""
    CONVERSION = "conversion"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    CONTEXT_ANALYSIS = "context_analysis"
    INTELLIGENT_ANALYSIS = "intelligent_analysis"
    COMPREHENSIVE = "comprehensive"


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIAnalysisRequest:
    """Request for AI analysis with context support."""
    analysis_type: AnalysisType
    automation_data: List[Dict[str, Any]]
    target_framework: str
    system_context: Optional[Any] = None  # SystemContext object
    current_action: Optional[Dict[str, Any]] = None
    previous_actions: Optional[List[Dict[str, Any]]] = None
    additional_context: Optional[Dict[str, Any]] = None
    target_url: Optional[str] = None
    
    def to_prompt(self) -> str:
        """Generate AI prompt based on analysis type and available context."""
        
        if self.analysis_type == AnalysisType.CONVERSION:
            return self._generate_conversion_prompt()
        elif self.analysis_type == AnalysisType.OPTIMIZATION:
            return self._generate_optimization_prompt()
        elif self.analysis_type == AnalysisType.VALIDATION:
            return self._generate_validation_prompt()
        elif self.analysis_type == AnalysisType.CONTEXT_ANALYSIS:
            return self._generate_context_analysis_prompt()
        elif self.analysis_type == AnalysisType.INTELLIGENT_ANALYSIS:
            return self._generate_intelligent_analysis_prompt()
        else:
            return self._generate_basic_prompt()
    
    def _generate_conversion_prompt(self) -> str:
        """Generate prompt for basic conversion analysis."""
        prompt = f"""
Analyze the following browser automation data and provide recommendations for converting it to {self.target_framework} test code.

Automation Data:
{self._format_automation_data()}

Please provide:
1. Action analysis and recommendations
2. Selector optimization suggestions
3. Potential issues or improvements
4. Framework-specific best practices
"""
        
        if self.system_context:
            prompt += self._add_context_to_prompt()
            
        return prompt
    
    def _generate_optimization_prompt(self) -> str:
        """Generate prompt for optimization analysis."""
        prompt = f"""
Analyze the following automation step for optimization opportunities in {self.target_framework}:

Current Action:
{self._format_current_action()}

Please suggest:
1. More reliable selectors
2. Better wait strategies
3. Error handling improvements
4. Performance optimizations
"""
        
        if self.system_context:
            prompt += self._add_context_optimization()
            
        return prompt
    
    def _generate_validation_prompt(self) -> str:
        """Generate prompt for validation analysis."""
        prompt = f"""
Validate the following automation actions for {self.target_framework} compatibility:

Actions to Validate:
{self._format_automation_data()}

Check for:
1. Invalid or problematic selectors
2. Framework compatibility issues
3. Missing required parameters
4. Potential race conditions
"""
        
        if self.system_context:
            prompt += self._add_context_validation()
            
        return prompt
    
    def _generate_context_analysis_prompt(self) -> str:
        """Generate prompt for analyzing system context relevance."""
        if not self.system_context:
            return "No system context available for analysis."
        
        prompt = f"""
Analyze the provided system context to understand how it relates to the browser automation task:

Target Framework: {self.target_framework}

System Context Summary:
{self._format_system_context_summary()}

Current Automation Task:
{self._format_automation_data()}

Please analyze:
1. Which existing tests are most similar to this automation task
2. What patterns from existing tests can be reused
3. What application-specific knowledge is relevant
4. What potential issues might arise based on the system architecture
5. Recommended test data and configurations based on existing patterns
"""
        return prompt
    
    def _generate_intelligent_analysis_prompt(self) -> str:
        """Generate comprehensive intelligent analysis prompt with full context."""
        prompt = f"""
Perform an intelligent analysis of this browser automation sequence for conversion to {self.target_framework}, leveraging all available system context:

# Automation Sequence
{self._format_automation_data()}

# System Context
{self._format_full_system_context()}

# Analysis Request
Please provide a comprehensive analysis including:

## 1. Context-Aware Recommendations
- How does this automation relate to existing tests in the codebase?
- What patterns from existing tests should be reused?
- What application-specific knowledge should inform the test design?

## 2. Intelligent Action Analysis
- Which actions are critical vs. auxiliary based on the application context?
- What user inputs and data fields are most important based on existing tests?
- Are there similar user flows already tested that we can learn from?

## 3. Framework-Specific Optimization
- Best practices for {self.target_framework} based on existing test patterns
- Selector strategies that align with the project's conventions
- Error handling and wait strategies used in similar tests

## 4. Test Data and Configuration
- What test data patterns are used in existing tests?
- How should sensitive data be handled based on project conventions?
- What configuration should be used based on existing test setup?

## 5. Quality and Reliability
- Potential flakiness issues based on similar tests in the codebase
- Reliability improvements based on lessons from existing tests
- Missing assertions or validations that are common in this codebase

## 6. Integration Considerations
- How should this test integrate with existing test suites?
- What setup/teardown might be needed based on other tests?
- Dependencies on application state or test data

Provide specific, actionable recommendations that leverage the project's existing test patterns and architecture.
"""
        return prompt
    
    def _generate_basic_prompt(self) -> str:
        """Generate a basic analysis prompt for unspecified analysis types."""
        prompt = f"""
Analyze the following browser automation data and provide recommendations for {self.target_framework}:

Automation Data:
{self._format_automation_data()}

Please provide:
1. General analysis and observations
2. Recommended approach for {self.target_framework}
3. Potential issues or improvements
4. Best practices and suggestions
"""
        
        if self.system_context:
            prompt += self._add_context_to_prompt()
            
        return prompt
    
    def _format_automation_data(self) -> str:
        """Format automation data for inclusion in prompts."""
        if not self.automation_data:
            return "No automation data provided."
        
        formatted = []
        for i, step in enumerate(self.automation_data, 1):
            formatted.append(f"Step {i}:")
            if 'model_output' in step:
                formatted.append(f"  Actions: {step['model_output']}")
            if 'state' in step:
                formatted.append(f"  Element State: {step['state']}")
            formatted.append("")
            
        return "\n".join(formatted)
    
    def _format_current_action(self) -> str:
        """Format current action for optimization prompts."""
        if not self.current_action:
            return "No current action provided."
        
        return f"Action: {self.current_action}"
    
    def _format_system_context_summary(self) -> str:
        """Format a summary of system context for prompts."""
        if not self.system_context:
            return "No system context available."
        
        try:
            # Use the context collector's summary method if available
            if hasattr(self.system_context, '__class__') and hasattr(self.system_context.__class__, 'get_context_summary'):
                from ..core.context_collector import ContextCollector
                collector = ContextCollector(None)  # Temporary instance for method access
                return collector.get_context_summary(self.system_context)
            else:
                # Fallback manual summary
                summary = []
                if hasattr(self.system_context, 'project'):
                    summary.append(f"Project: {getattr(self.system_context.project, 'name', 'Unknown')}")
                if hasattr(self.system_context, 'existing_tests'):
                    summary.append(f"Existing Tests: {len(self.system_context.existing_tests)} files")
                if hasattr(self.system_context, 'project') and hasattr(self.system_context.project, 'test_frameworks'):
                    summary.append(f"Test Frameworks: {', '.join(self.system_context.project.test_frameworks)}")
                return "\n".join(summary)
        except Exception:
            return "System context available but could not be formatted."
    
    def _format_full_system_context(self) -> str:
        """Format complete system context for detailed analysis."""
        if not self.system_context:
            return "No system context available."
        
        try:
            context_parts = []
            
            # Project information
            if hasattr(self.system_context, 'project'):
                project = self.system_context.project
                context_parts.append("## Project Information")
                context_parts.append(f"Name: {getattr(project, 'name', 'Unknown')}")
                if hasattr(project, 'description') and project.description:
                    context_parts.append(f"Description: {project.description}")
                if hasattr(project, 'tech_stack') and project.tech_stack:
                    context_parts.append(f"Tech Stack: {', '.join(project.tech_stack)}")
                if hasattr(project, 'test_frameworks') and project.test_frameworks:
                    context_parts.append(f"Test Frameworks: {', '.join(project.test_frameworks)}")
                context_parts.append("")
            
            # Existing tests
            if hasattr(self.system_context, 'existing_tests') and self.system_context.existing_tests:
                context_parts.append("## Existing Tests")
                context_parts.append(f"Total test files: {len(self.system_context.existing_tests)}")
                
                # Group by framework
                frameworks = {}
                for test in self.system_context.existing_tests[:10]:  # Limit for prompt size
                    if test.framework not in frameworks:
                        frameworks[test.framework] = []
                    frameworks[test.framework].append(test)
                
                for framework, tests in frameworks.items():
                    context_parts.append(f"\n### {framework.title()} Tests ({len(tests)} files)")
                    for test in tests[:3]:  # Show only first 3 for each framework
                        context_parts.append(f"- {test.file_path}")
                        if test.test_functions:
                            context_parts.append(f"  Functions: {', '.join(test.test_functions[:3])}")
                        if test.selectors:
                            context_parts.append(f"  Common selectors: {', '.join(test.selectors[:3])}")
                context_parts.append("")
            
            # UI Components
            if hasattr(self.system_context, 'ui_components') and self.system_context.ui_components:
                context_parts.append("## UI Components")
                context_parts.append(f"Component files analyzed: {len(self.system_context.ui_components)}")
                
                # Extract common component patterns
                all_components = []
                all_props = []
                for comp_file, comp_info in list(self.system_context.ui_components.items())[:5]:
                    if isinstance(comp_info, dict):
                        all_components.extend(comp_info.get('component_names', []))
                        all_props.extend(comp_info.get('props', []))
                
                if all_components:
                    context_parts.append(f"Common components: {', '.join(set(all_components[:10]))}")
                if all_props:
                    context_parts.append(f"Common props: {', '.join(set(all_props[:10]))}")
                context_parts.append("")
            
            # API Endpoints
            if hasattr(self.system_context, 'api_endpoints') and self.system_context.api_endpoints:
                context_parts.append("## API Endpoints")
                context_parts.append(f"Total endpoints: {len(self.system_context.api_endpoints)}")
                
                # Group by method
                methods = {}
                for endpoint in self.system_context.api_endpoints[:10]:
                    method = endpoint.get('method', 'UNKNOWN')
                    if method not in methods:
                        methods[method] = []
                    methods[method].append(endpoint.get('path', ''))
                
                for method, paths in methods.items():
                    context_parts.append(f"{method}: {', '.join(paths[:3])}")
                context_parts.append("")
            
            # Recent changes
            if hasattr(self.system_context, 'recent_changes') and self.system_context.recent_changes:
                context_parts.append("## Recent Changes")
                for change in self.system_context.recent_changes[:3]:
                    if isinstance(change, dict):
                        context_parts.append(f"- {change.get('message', 'Unknown change')}")
                context_parts.append("")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            return f"System context available but could not be fully formatted: {str(e)}"
    
    def _add_context_to_prompt(self) -> str:
        """Add basic context information to conversion prompts."""
        context_info = "\n\n## System Context\n"
        context_info += self._format_system_context_summary()
        
        if hasattr(self.system_context, 'existing_tests') and self.system_context.existing_tests:
            # Find similar tests
            similar_tests = []
            for test in self.system_context.existing_tests[:5]:
                if test.framework == self.target_framework:
                    similar_tests.append(test)
            
            if similar_tests:
                context_info += "\n\n### Similar Existing Tests\n"
                for test in similar_tests[:3]:
                    context_info += f"- {test.file_path}\n"
                    if test.selectors:
                        context_info += f"  Common selectors: {', '.join(test.selectors[:3])}\n"
        
        context_info += "\nPlease consider this context when making recommendations."
        return context_info
    
    def _add_context_optimization(self) -> str:
        """Add context for optimization analysis."""
        if not self.system_context:
            return ""
        
        context_info = "\n\n## Optimization Context\n"
        
        # Add information about existing selector patterns
        if hasattr(self.system_context, 'existing_tests'):
            all_selectors = []
            for test in self.system_context.existing_tests:
                if test.framework == self.target_framework:
                    all_selectors.extend(test.selectors)
            
            if all_selectors:
                unique_selectors = list(set(all_selectors))[:10]
                context_info += f"Common selector patterns in this project: {', '.join(unique_selectors)}\n"
        
        context_info += "Consider these patterns when suggesting optimizations."
        return context_info
    
    def _add_context_validation(self) -> str:
        """Add context for validation analysis."""
        if not self.system_context:
            return ""
        
        context_info = "\n\n## Validation Context\n"
        
        # Add framework-specific patterns from existing tests
        if hasattr(self.system_context, 'existing_tests'):
            framework_tests = [test for test in self.system_context.existing_tests 
                             if test.framework == self.target_framework]
            
            if framework_tests:
                context_info += f"This project has {len(framework_tests)} existing {self.target_framework} tests.\n"
                
                # Common actions used
                all_actions = []
                for test in framework_tests:
                    all_actions.extend(test.actions)
                
                if all_actions:
                    unique_actions = list(set(all_actions))[:10]
                    context_info += f"Common actions used: {', '.join(unique_actions)}\n"
        
        context_info += "Validate against these established patterns."
        return context_info


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AIResponse:
        """Generate a response from the AI provider."""
        pass
    
    @abstractmethod
    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AIResponse:
        """Generate a response from the AI provider asynchronously."""
        pass
    
    def analyze_with_context(self, request: AIAnalysisRequest, **kwargs) -> AIResponse:
        """Perform context-aware analysis using the AI provider."""
        
        # Generate appropriate system prompt based on analysis type
        system_prompt = self._generate_system_prompt(request)
        
        # Generate the main prompt
        prompt = request.to_prompt()
        
        # Make the AI call
        response = self.generate(prompt, system_prompt, **kwargs)
        
        # Add metadata about the analysis
        response.metadata.update({
            'analysis_type': request.analysis_type.value,
            'target_framework': request.target_framework,
            'has_context': request.system_context is not None,
            'context_summary': request._format_system_context_summary() if request.system_context else None
        })
        
        return response
    
    async def analyze_with_context_async(self, request: AIAnalysisRequest, **kwargs) -> AIResponse:
        """Perform context-aware analysis using the AI provider asynchronously."""
        
        # Generate appropriate system prompt based on analysis type
        system_prompt = self._generate_system_prompt(request)
        
        # Generate the main prompt
        prompt = request.to_prompt()
        
        # Make the AI call
        response = await self.generate_async(prompt, system_prompt, **kwargs)
        
        # Add metadata about the analysis
        response.metadata.update({
            'analysis_type': request.analysis_type.value,
            'target_framework': request.target_framework,
            'has_context': request.system_context is not None,
            'context_summary': request._format_system_context_summary() if request.system_context else None
        })
        
        return response
    
    def _generate_system_prompt(self, request: AIAnalysisRequest) -> str:
        """Generate system prompt based on analysis type."""
        
        base_prompt = f"""You are an expert test automation engineer specializing in {request.target_framework} and browser test automation. You help convert browser automation data into high-quality, maintainable test scripts."""
        
        if request.analysis_type == AnalysisType.INTELLIGENT_ANALYSIS:
            return base_prompt + """
            
You have access to detailed information about the project's existing tests, architecture, and patterns. Use this context to provide intelligent, project-specific recommendations that align with existing conventions and best practices.

Focus on:
- Leveraging existing test patterns and utilities
- Suggesting improvements based on project-specific knowledge
- Identifying potential issues based on similar tests in the codebase
- Recommending test data and configuration strategies
- Ensuring consistency with the project's testing approach

Provide specific, actionable advice that takes into account the project's unique characteristics and existing test suite."""
        
        elif request.analysis_type == AnalysisType.CONTEXT_ANALYSIS:
            return base_prompt + """
            
You are analyzing system context to understand how browser automation tasks relate to an existing codebase. Focus on identifying patterns, similarities, and relevant information that can inform intelligent test generation."""
        
        elif request.analysis_type == AnalysisType.OPTIMIZATION:
            return base_prompt + """
            
You specialize in optimizing test automation for reliability, maintainability, and performance. Consider existing project patterns when making suggestions."""
        
        elif request.analysis_type == AnalysisType.VALIDATION:
            return base_prompt + """
            
You validate automation sequences for potential issues, compatibility problems, and adherence to best practices. Consider the project's existing test patterns and conventions."""
        
        else:
            return base_prompt + """
            
Analyze the provided browser automation data and provide clear, actionable recommendations for creating high-quality test scripts."""
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available and properly configured."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the AI model being used."""
        pass 