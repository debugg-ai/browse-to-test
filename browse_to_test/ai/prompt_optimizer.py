"""
Optimized prompt templates for reduced token usage and better efficiency.

This module provides optimized prompts that maintain effectiveness while
significantly reducing token consumption.
"""

from typing import Dict, List, Optional, Any
from enum import Enum


class PromptTemplate(Enum):
    """Optimized prompt templates."""
    
    # Conversion prompts - more concise
    CONVERSION_COMPACT = """Convert browser actions to {framework} test:

Actions:
{actions}

Output clean {framework} code with:
- Proper selectors
- Error handling
- Assertions"""

    CONVERSION_WITH_CONTEXT = """Convert to {framework} test using project patterns:

Project: {project_name} ({framework})
Similar tests: {similar_tests}

Actions:
{actions}

Follow existing conventions."""

    # Optimization prompts
    OPTIMIZATION_COMPACT = """Optimize {framework} test step:

Current: {action}
Issues: {issues}

Suggest improved selector and wait strategy."""

    # Validation prompts
    VALIDATION_COMPACT = """Validate {framework} compatibility:

Actions: {actions}

Check: selectors, waits, framework support.
List issues only."""

    # Batch processing prompts
    BATCH_CONVERSION = """Convert multiple sequences to {framework}:

{sequences}

For each sequence, provide:
### Request: [id]
- Code snippet
- Key assertions
- Notes if needed"""

    # Intelligent analysis with minimal tokens
    INTELLIGENT_COMPACT = """Analyze for {framework} with context:

Context:
- Project: {project_summary}
- Tests: {test_count} existing
- Patterns: {common_patterns}

Task: {actions}

Provide:
1. Reusable patterns
2. Test approach
3. Key validations"""


class PromptOptimizer:
    """
    Optimize prompts for token efficiency while maintaining quality.
    
    Strategies:
    - Remove redundant instructions
    - Use concise language
    - Leverage implicit understanding
    - Smart context inclusion
    """
    
    def __init__(self):
        self.abbreviations = {
            # Common terms
            'browser automation': 'automation',
            'test script': 'test',
            'user interface': 'UI',
            'application': 'app',
            'element': 'elem',
            'selector': 'sel',
            'function': 'func',
            'validation': 'check',
            'navigation': 'nav',
            
            # Framework names (keep as-is for clarity)
            # 'playwright': 'pw',
            # 'selenium': 'sel',
            # 'puppeteer': 'pup',
            
            # Actions
            'click on': 'click',
            'fill in': 'fill',
            'navigate to': 'goto',
            'wait for': 'wait',
            'should be': 'is',
            'should have': 'has',
            'should contain': 'contains',
            
            # Technical terms
            'asynchronous': 'async',
            'synchronous': 'sync',
            'configuration': 'config',
            'implementation': 'impl',
            'recommendation': 'suggest',
            'optimization': 'optimize',
            
            # Phrases
            'best practices': 'practices',
            'error handling': 'errors',
            'Please provide': 'Provide',
            'should be used': 'use',
            'in order to': 'to',
            'make sure to': 'ensure',
            'it is important': 'important',
        }
        
        self.removal_phrases = [
            'Please note that',
            'It is recommended that',
            'You should consider',
            'In this case',
            'For this purpose',
            'As mentioned',
            'It should be noted',
            'Keep in mind that',
            'Remember to',
            'Be sure to',
        ]
    
    def optimize_prompt(
        self,
        template: PromptTemplate,
        variables: Dict[str, Any],
        max_length: Optional[int] = None
    ) -> str:
        """
        Generate an optimized prompt from a template.
        
        Args:
            template: The prompt template to use
            variables: Variables to fill in the template
            max_length: Maximum character length (optional)
            
        Returns:
            Optimized prompt string
        """
        # Get base prompt
        prompt = template.value.format(**variables)
        
        # Apply optimizations
        prompt = self._apply_abbreviations(prompt)
        prompt = self._remove_redundant_phrases(prompt)
        prompt = self._compress_whitespace(prompt)
        
        # Truncate if needed
        if max_length and len(prompt) > max_length:
            prompt = self._smart_truncate(prompt, max_length)
        
        return prompt
    
    def optimize_context(
        self,
        context: Dict[str, Any],
        relevance_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Optimize context data to include only relevant information.
        
        Args:
            context: Full context dictionary
            relevance_threshold: Minimum relevance score
            
        Returns:
            Optimized context with only relevant data
        """
        optimized = {}
        
        # Always include core information
        core_fields = ['project_name', 'framework', 'target_url']
        for field in core_fields:
            if field in context:
                optimized[field] = context[field]
        
        # Selectively include other fields based on relevance
        if 'existing_tests' in context and context['existing_tests']:
            # Only include most relevant tests
            relevant_tests = self._get_relevant_tests(
                context['existing_tests'],
                context.get('current_action'),
                limit=3
            )
            if relevant_tests:
                optimized['similar_tests'] = relevant_tests
        
        # Compress patterns
        if 'common_patterns' in context:
            optimized['patterns'] = self._compress_patterns(
                context['common_patterns']
            )
        
        return optimized
    
    def create_batch_prompt(
        self,
        requests: List[Dict[str, Any]],
        framework: str,
        max_tokens: int = 4000
    ) -> str:
        """
        Create an optimized batch processing prompt.
        
        Args:
            requests: List of request data
            framework: Target framework
            max_tokens: Maximum tokens (rough estimate)
            
        Returns:
            Optimized batch prompt
        """
        # Group similar requests
        grouped = self._group_similar_requests(requests)
        
        # Build compact prompt
        sections = []
        for group_key, group_requests in grouped.items():
            if len(group_requests) > 1:
                # Combine similar requests
                sections.append(self._format_request_group(
                    group_key, group_requests, framework
                ))
            else:
                # Single request
                sections.append(self._format_single_request(
                    group_requests[0], framework
                ))
        
        # Combine with batch template
        prompt = PromptTemplate.BATCH_CONVERSION.value.format(
            framework=framework,
            sequences='\n\n'.join(sections)
        )
        
        # Ensure within token limit
        return self._fit_to_token_limit(prompt, max_tokens)
    
    def _apply_abbreviations(self, text: str) -> str:
        """Apply abbreviations to reduce length."""
        for full, abbrev in self.abbreviations.items():
            text = text.replace(full, abbrev)
        return text
    
    def _remove_redundant_phrases(self, text: str) -> str:
        """Remove redundant phrases."""
        for phrase in self.removal_phrases:
            text = text.replace(phrase + ' ', '')
            text = text.replace(phrase + ', ', '')
        return text
    
    def _compress_whitespace(self, text: str) -> str:
        """Compress excessive whitespace."""
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        # Replace multiple newlines with double newline
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        return text
    
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """Intelligently truncate text to fit length limit."""
        if len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        cut_point = max(last_period, last_newline)
        if cut_point > max_length * 0.8:  # If we're not losing too much
            return truncated[:cut_point + 1]
        
        return truncated + '...'
    
    def _get_relevant_tests(
        self,
        tests: List[Any],
        current_action: Optional[str],
        limit: int = 3
    ) -> List[str]:
        """Get most relevant existing tests."""
        # Simple relevance scoring based on action similarity
        if not current_action:
            return [str(t) for t in tests[:limit]]
        
        # This would implement more sophisticated relevance scoring
        return [str(t) for t in tests[:limit]]
    
    def _compress_patterns(self, patterns: List[str]) -> str:
        """Compress pattern list into concise format."""
        if not patterns:
            return ""
        
        # Group similar patterns
        unique_patterns = list(set(patterns))[:5]  # Limit to 5
        return ', '.join(unique_patterns)
    
    def _group_similar_requests(
        self,
        requests: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group similar requests for efficient batching."""
        groups = {}
        
        for request in requests:
            # Simple grouping by action type
            action_type = self._get_action_type(request)
            if action_type not in groups:
                groups[action_type] = []
            groups[action_type].append(request)
        
        return groups
    
    def _get_action_type(self, request: Dict[str, Any]) -> str:
        """Extract primary action type from request."""
        if 'actions' in request and request['actions']:
            first_action = request['actions'][0]
            if isinstance(first_action, dict):
                return first_action.get('type', 'unknown')
        return 'unknown'
    
    def _format_request_group(
        self,
        group_key: str,
        requests: List[Dict[str, Any]],
        framework: str
    ) -> str:
        """Format a group of similar requests."""
        return f"""### Group: {group_key} ({len(requests)} similar)
Actions: {self._summarize_actions(requests)}
Pattern: Reuse same approach for all."""
    
    def _format_single_request(
        self,
        request: Dict[str, Any],
        framework: str
    ) -> str:
        """Format a single request concisely."""
        request_id = request.get('id', 'unknown')
        actions = self._summarize_actions([request])
        return f"""### Request: {request_id}
{actions}"""
    
    def _summarize_actions(self, requests: List[Dict[str, Any]]) -> str:
        """Create concise summary of actions."""
        all_actions = []
        for req in requests:
            if 'actions' in req:
                all_actions.extend(req['actions'])
        
        # Summarize
        summary_parts = []
        for action in all_actions[:3]:  # First 3 actions
            if isinstance(action, dict):
                action_str = f"{action.get('type', '?')}({action.get('selector', '?')})"
            else:
                action_str = str(action)[:20]
            summary_parts.append(action_str)
        
        if len(all_actions) > 3:
            summary_parts.append(f"... +{len(all_actions) - 3} more")
        
        return ', '.join(summary_parts)
    
    def _fit_to_token_limit(self, text: str, max_tokens: int) -> str:
        """Ensure text fits within token limit."""
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        return self._smart_truncate(text, max_chars)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Rough estimate for planning
        # More accurate would use tiktoken or similar
        words = len(text.split())
        chars = len(text)
        
        # Average of word-based and character-based estimates
        return (words + chars // 4) // 2