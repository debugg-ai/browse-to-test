#!/usr/bin/env python3
"""
Main orchestrator for coordinating the test script generation process with context awareness.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import hashlib

from ..configuration.config import Config
from ..processing.input_parser import InputParser, ParsedAutomationData
from ..processing.action_analyzer import ActionAnalyzer, ComprehensiveAnalysisResult
from ..processing.context_collector import ContextCollector, SystemContext
from ...output_langs import LanguageManager
from ...ai.factory import AIProviderFactory
from ...plugins.registry import PluginRegistry


class E2eScriptOrchestrator:
    """
    Main orchestrator that coordinates the entire test script generation process.
    
    Features:
    - Context-aware test generation
    - AI-powered intelligent analysis  
    - Multi-framework support via plugins
    - Configuration management
    - Caching and optimization
    """
    
    def __init__(self, config: Config):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config: Configuration object containing all settings
        """
        self.config = config
        
        # Initialize core components
        self.input_parser = InputParser(config)
        self.ai_factory = AIProviderFactory()
        self.plugin_registry = PluginRegistry()
        
        # Initialize context collector if enabled
        self.context_collector = None
        if config.processing.collect_system_context:
            self.context_collector = ContextCollector(config, config.project_root)
        
        # Initialize AI provider if enabled
        self.ai_provider = None
        if config.processing.analyze_actions_with_ai:
            try:
                self.ai_provider = self.ai_factory.create_provider(config.ai)
            except Exception as e:
                if config.debug:
                    print(f"Warning: Failed to initialize AI provider: {e}")
                    
        # Initialize action analyzer
        self.action_analyzer = ActionAnalyzer(self.ai_provider, config)
        
        # Initialize language manager if enabled
        self.language_manager = None
        if config.output.shared_setup.enabled:
            output_dir = Path(config.output.shared_setup.setup_dir)
            self.language_manager = LanguageManager(
                language=config.output.language,
                framework=config.output.framework,
                output_dir=output_dir
            )
        
        # Internal state
        self._generation_cache: Dict[str, str] = {}
        self._analysis_cache: Dict[str, Any] = {}
        
    def generate_test_script(
        self, 
        automation_data: Union[List[Dict], str, Path], 
        custom_config: Optional[Dict[str, Any]] = None,
        target_url: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate test script from automation data with intelligent analysis.
        
        Args:
            automation_data: Browser automation data (list, JSON string, or file path)
            custom_config: Optional configuration overrides
            target_url: URL being tested (helps with context filtering)
            context_hints: Additional context hints for analysis
            
        Returns:
            Generated test script as string
            
        Raises:
            ValueError: If automation data is invalid
            RuntimeError: If generation fails
        """
        
        # Apply custom configuration if provided
        effective_config = self.config
        if custom_config:
            effective_config = self._apply_config_overrides(custom_config)
        
        try:
            # Parse input data
            parsed_data = self.input_parser.parse(automation_data)
            
            # Extract target URL if not provided
            if not target_url:
                target_url = self._extract_target_url(parsed_data)
            
            # Generate cache key for this request
            cache_key = self._generate_cache_key(parsed_data, effective_config, target_url)
            
            # Check cache if enabled
            if effective_config.processing.cache_ai_responses and cache_key in self._generation_cache:
                if effective_config.verbose:
                    print("Using cached test script")
                return self._generation_cache[cache_key]
            
            # Collect system context if enabled
            system_context = None
            if effective_config.processing.collect_system_context and self.context_collector:
                try:
                    system_context = self.context_collector.collect_context(
                        target_url=target_url,
                        force_refresh=False
                    )
                    if effective_config.verbose:
                        print(f"Collected system context: {len(system_context.existing_tests)} tests, "
                              f"{len(system_context.documentation)} docs")
                except Exception as e:
                    if effective_config.debug:
                        print(f"Warning: Context collection failed: {e}")
            
            # Perform intelligent analysis if enabled
            analysis_results = None
            if effective_config.processing.analyze_actions_with_ai and self.ai_provider:
                try:
                    analysis_results = self.action_analyzer.analyze_automation_data(
                        parsed_data,
                        target_url=target_url,
                        use_intelligent_analysis=effective_config.processing.use_intelligent_analysis
                    )
                    if effective_config.verbose:
                        print(f"Analysis completed: {analysis_results.get('total_actions', 0)} actions analyzed")
                except Exception as e:
                    if effective_config.debug:
                        print(f"Warning: Analysis failed: {e}")
            
            # Create output plugin
            plugin = self.plugin_registry.create_plugin(effective_config.output)
            
            # Generate test script
            generated_script = plugin.generate_test_script(
                parsed_data=parsed_data,
                analysis_results=analysis_results,
                system_context=system_context,
                context_hints=context_hints
            )
            
            # Generate shared setup if enabled
            if self.language_manager and effective_config.output.shared_setup.enabled:
                # Generate setup files
                setup_files = self.language_manager.generate_setup_files(
                    force_regenerate=effective_config.output.shared_setup.force_regenerate
                )
                
                if effective_config.verbose:
                    print(f"Generated shared setup files: {list(setup_files.keys())}")
                
                # Create clean script without inline utilities
                final_script = self._generate_clean_script(
                    generated_script.content,
                    effective_config,
                    analysis_results,
                    system_context
                )
            else:
                # Post-process the generated script normally
                final_script = self._post_process_script(
                    generated_script.content,
                    effective_config,
                    analysis_results,
                    system_context
                )
            
            # Cache the result if enabled
            if effective_config.processing.cache_ai_responses:
                self._generation_cache[cache_key] = final_script
                
                # Limit cache size
                if len(self._generation_cache) > effective_config.processing.max_cache_size:
                    # Remove oldest entries (simple LRU-like behavior)
                    oldest_keys = list(self._generation_cache.keys())[:-effective_config.processing.max_cache_size//2]
                    for key in oldest_keys:
                        del self._generation_cache[key]
            
            return final_script
            
        except Exception as e:
            if effective_config.processing.strict_mode:
                raise RuntimeError(f"Test script generation failed: {e}") from e
            else:
                if effective_config.debug:
                    print(f"Generation failed, attempting fallback: {e}")
                return self._generate_fallback_script(automation_data, effective_config)
    
    def generate_with_multiple_frameworks(
        self, 
        automation_data: Union[List[Dict], str, Path],
        frameworks: List[str],
        custom_config: Optional[Dict[str, Any]] = None,
        target_url: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate test scripts for multiple frameworks simultaneously.
        
        Args:
            automation_data: Browser automation data
            frameworks: List of framework names to generate for
            custom_config: Optional configuration overrides
            target_url: URL being tested
            
        Returns:
            Dictionary mapping framework names to generated scripts
        """
        results = {}
        
        for framework in frameworks:
            try:
                # Create config for this framework
                framework_config = custom_config.copy() if custom_config else {}
                if 'output' not in framework_config:
                    framework_config['output'] = {}
                framework_config['output']['framework'] = framework
                
                # Generate script for this framework
                script = self.generate_test_script(
                    automation_data=automation_data,
                    custom_config=framework_config,
                    target_url=target_url
                )
                
                results[framework] = script
                
            except Exception as e:
                if self.config.debug:
                    print(f"Failed to generate script for {framework}: {e}")
                if self.config.processing.strict_mode:
                    raise
                results[framework] = f"# Error generating script for {framework}: {e}"
        
        return results
    
    def preview_conversion(
        self, 
        automation_data: Union[List[Dict], str, Path],
        max_actions: int = 5,
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview the conversion process without generating full script.
        
        Args:
            automation_data: Browser automation data
            max_actions: Maximum number of actions to analyze for preview
            target_url: URL being tested
            
        Returns:
            Dictionary containing preview information
        """
        try:
            # Parse input data
            parsed_data = self.input_parser.parse(automation_data)
            
            # Extract target URL if not provided
            if not target_url:
                target_url = self._extract_target_url(parsed_data)
            
            # Collect basic context information
            system_context = None
            if self.config.processing.collect_system_context and self.context_collector:
                try:
                    system_context = self.context_collector.collect_context(
                        target_url=target_url,
                        force_refresh=False
                    )
                except Exception:
                    pass  # Ignore context collection errors in preview
            
            # Limit actions for preview
            preview_data = self._limit_actions_for_preview(parsed_data, max_actions)
            
            # Perform basic analysis
            analysis_results = None
            if self.ai_provider:
                try:
                    analysis_results = self.action_analyzer.analyze_automation_data(
                        preview_data,
                        target_url=target_url,
                        use_intelligent_analysis=False  # Use faster analysis for preview
                    )
                except Exception:
                    pass  # Ignore analysis errors in preview
            
            # Create preview summary
            preview = {
                'total_steps': len(parsed_data.steps),
                'total_actions': sum(len(step.actions) for step in parsed_data.steps),
                'preview_actions': sum(len(step.actions) for step in preview_data.steps),
                'target_url': target_url,
                'target_framework': self.config.output.framework,
                'has_context': system_context is not None,
                'has_analysis': analysis_results is not None,
                'action_types': {},
                'validation_issues': [],
                'context_summary': {},
                'similar_tests': [],
                'estimated_quality_score': 0.7,  # Default estimate
            }
            
            # Analyze action types
            for step in parsed_data.steps:
                for action in step.actions:
                    action_type = action.action_type
                    if action_type not in preview['action_types']:
                        preview['action_types'][action_type] = 0
                    preview['action_types'][action_type] += 1
            
            # Add context information
            if system_context:
                preview['context_summary'] = {
                    'existing_tests': len(system_context.existing_tests),
                    'documentation_files': len(system_context.documentation),
                    'ui_components': len(system_context.ui_components),
                    'api_endpoints': len(system_context.api_endpoints),
                    'project_name': getattr(system_context.project, 'name', 'Unknown'),
                    'test_frameworks': getattr(system_context.project, 'test_frameworks', []),
                }
                
                # Find similar tests
                target_actions = set(preview['action_types'].keys())
                for test in system_context.existing_tests[:5]:
                    test_actions = set(test.actions)
                    overlap = len(target_actions.intersection(test_actions))
                    if overlap > 0:
                        similarity = overlap / max(len(target_actions.union(test_actions)), 1)
                        if similarity > 0.2:  # 20% similarity threshold for preview
                            preview['similar_tests'].append({
                                'file_path': test.file_path,
                                'framework': test.framework,
                                'similarity_score': similarity,
                                'common_actions': list(target_actions.intersection(test_actions))
                            })
            
            # Add analysis information
            if analysis_results:
                if 'validation_issues' in analysis_results:
                    preview['validation_issues'] = analysis_results['validation_issues']
                
                if 'comprehensive_analysis' in analysis_results:
                    comp_analysis = analysis_results['comprehensive_analysis']
                    preview['estimated_quality_score'] = comp_analysis.get('overall_quality_score', 0.7)
                    preview['critical_actions'] = len(comp_analysis.get('critical_actions', []))
                    preview['auxiliary_actions'] = len(comp_analysis.get('auxiliary_actions', []))
            
            return preview
            
        except Exception as e:
            return {
                'error': str(e),
                'total_steps': 0,
                'total_actions': 0,
                'target_framework': self.config.output.framework,
            }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return validation results.
        
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'ai_provider_status': 'unknown',
            'plugin_status': 'unknown',
            'context_collector_status': 'unknown',
        }
        
        # Validate core configuration
        config_errors = self.config.validate()
        validation_result['errors'].extend(config_errors)
        
        # Test AI provider
        if self.config.processing.analyze_actions_with_ai:
            try:
                if self.ai_provider:
                    # Test a simple AI call
                    test_response = self.ai_provider.generate(
                        "Say 'test' if you can respond",
                        max_tokens=10
                    )
                    if test_response.content:
                        validation_result['ai_provider_status'] = 'available'
                    else:
                        validation_result['ai_provider_status'] = 'error'
                        validation_result['warnings'].append("AI provider responded but with empty content")
                else:
                    validation_result['ai_provider_status'] = 'unavailable'
                    validation_result['warnings'].append("AI provider not initialized")
            except Exception as e:
                validation_result['ai_provider_status'] = 'error'
                validation_result['errors'].append(f"AI provider error: {e}")
        else:
            validation_result['ai_provider_status'] = 'disabled'
        
        # Test plugin system
        try:
            plugin = self.plugin_registry.create_plugin(self.config.output)
            validation_result['plugin_status'] = 'available'
        except Exception as e:
            validation_result['plugin_status'] = 'error'
            validation_result['errors'].append(f"Plugin error: {e}")
        
        # Test context collector
        if self.config.processing.collect_system_context:
            try:
                if self.context_collector:
                    # Test context collection
                    context = self.context_collector.collect_context(force_refresh=False)
                    validation_result['context_collector_status'] = 'available'
                    validation_result['context_summary'] = {
                        'existing_tests': len(context.existing_tests),
                        'documentation': len(context.documentation),
                        'project_name': getattr(context.project, 'name', 'Unknown'),
                    }
                else:
                    validation_result['context_collector_status'] = 'unavailable'
                    validation_result['warnings'].append("Context collector not initialized")
            except Exception as e:
                validation_result['context_collector_status'] = 'error'
                validation_result['warnings'].append(f"Context collection warning: {e}")
        else:
            validation_result['context_collector_status'] = 'disabled'
        
        # Overall validation status
        validation_result['is_valid'] = len(validation_result['errors']) == 0
        
        return validation_result
    
    def get_available_frameworks(self) -> List[str]:
        """Get list of available output frameworks."""
        return self.plugin_registry.list_available_plugins()
    
    def get_available_ai_providers(self) -> List[str]:
        """Get list of available AI providers."""
        return self.ai_factory.list_available_providers()
    
    def clear_caches(self) -> None:
        """Clear all internal caches."""
        self._generation_cache.clear()
        self._analysis_cache.clear()
        if self.action_analyzer:
            self.action_analyzer.clear_cache()
    
    def _apply_config_overrides(self, custom_config: Dict[str, Any]) -> Config:
        """Apply custom configuration overrides."""
        # Create a copy of the current config
        effective_config = Config.from_dict(self.config.to_dict())
        
        # Apply custom overrides
        effective_config.update_from_dict(custom_config)
        
        return effective_config
    
    def _extract_target_url(self, parsed_data: ParsedAutomationData) -> Optional[str]:
        """Extract target URL from parsed automation data."""
        for step in parsed_data.steps:
            for action in step.actions:
                if action.action_type == 'go_to_url' and 'url' in action.parameters:
                    return action.parameters['url']
        return None
    
    def _generate_cache_key(
        self, 
        parsed_data: ParsedAutomationData, 
        config: Config, 
        target_url: Optional[str]
    ) -> str:
        """Generate cache key for the current request."""
        # Create a hash of the relevant data
        cache_data = {
            'actions': [
                {
                    'type': action.action_type,
                    'params': action.parameters,
                    'selector': action.selector_info
                }
                for step in parsed_data.steps
                for action in step.actions
            ],
            'framework': config.output.framework,
            'language': config.output.language,
            'ai_provider': config.ai.provider,
            'ai_model': config.ai.model,
            'target_url': target_url,
            'context_enabled': config.processing.collect_system_context,
            'intelligent_analysis': config.processing.use_intelligent_analysis,
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _limit_actions_for_preview(self, parsed_data: ParsedAutomationData, max_actions: int) -> ParsedAutomationData:
        """Limit the number of actions for preview purposes."""
        if max_actions <= 0:
            return parsed_data
        
        preview_steps = []
        action_count = 0
        
        for step in parsed_data.steps:
            if action_count >= max_actions:
                break
            
            step_actions = []
            for action in step.actions:
                if action_count >= max_actions:
                    break
                step_actions.append(action)
                action_count += 1
            
            if step_actions:
                # Create a new step with limited actions
                preview_step = type(step)(
                    step_index=step.step_index,
                    actions=step_actions,
                    timing_info=step.timing_info,
                    metadata=step.metadata
                )
                preview_steps.append(preview_step)
        
        # Create new ParsedAutomationData with limited steps
        return ParsedAutomationData(
            steps=preview_steps,
            sensitive_data_keys=parsed_data.sensitive_data_keys,
            metadata=parsed_data.metadata
        )
    
    def _post_process_script(
        self, 
        script: str, 
        config: Config, 
        analysis_results: Optional[Dict[str, Any]],
        system_context: Optional[SystemContext]
    ) -> str:
        """Post-process the generated script with additional enhancements."""
        
        # Add context-aware comments if analysis results are available
        if analysis_results and config.output.include_logging:
            if 'comprehensive_analysis' in analysis_results:
                comp_analysis = analysis_results['comprehensive_analysis']
                
                # Add header comment with analysis insights
                header_comments = []
                header_comments.append("# Generated with intelligent analysis")
                
                if comp_analysis.get('similar_tests'):
                    header_comments.append(f"# Found {len(comp_analysis['similar_tests'])} similar tests in codebase")
                
                if comp_analysis.get('context_recommendations'):
                    header_comments.append("# Context recommendations applied:")
                    for rec in comp_analysis['context_recommendations'][:3]:
                        header_comments.append(f"#   - {rec}")
                
                header_comments.append("")
                script = "\n".join(header_comments) + "\n" + script
        
        # Add system context information if available
        if system_context and config.verbose:
            context_comment = f"# Project: {getattr(system_context.project, 'name', 'Unknown')}"
            if hasattr(system_context.project, 'test_frameworks') and system_context.project.test_frameworks:
                context_comment += f" (Uses: {', '.join(system_context.project.test_frameworks)})"
            script = context_comment + "\n" + script
        
        return script
    
    def _generate_clean_script(
        self,
        script: str,
        config: Config,
        analysis_results: Optional[Dict[str, Any]],
        system_context: Optional[SystemContext]
    ) -> str:
        """Generate a clean test script that imports from shared setup."""
        
        if not self.language_manager:
            return script
        
        lines = []
        
        # Add file header
        lines.extend([
            "#!/usr/bin/env python3",
            '"""',
            "Test script generated by browse-to-test.",
            "",
            "This script uses shared utilities from the output_langs package.",
            '"""',
            ""
        ])
        
        # Add standard framework imports
        if config.output.framework == "playwright":
            lines.extend([
                "import asyncio",
                "from playwright.async_api import async_playwright",
                ""
            ])
        elif config.output.framework == "selenium":
            lines.extend([
                "from selenium import webdriver",
                "from selenium.webdriver.common.by import By",
                "from selenium.webdriver.support.ui import WebDriverWait",
                "from selenium.webdriver.support import expected_conditions as EC",
                ""
            ])
        
        # Add shared setup imports
        setup_imports = self.language_manager.get_import_statements_for_test(use_setup_files=True)
        if setup_imports:
            lines.extend(setup_imports)
            lines.append("")
        
        # Extract and clean the main test content
        clean_content = self._extract_clean_test_content(script, config)
        lines.extend(clean_content.split('\n'))
        
        # Add context-aware comments if available
        if analysis_results and config.output.include_logging:
            header_comments = []
            header_comments.append("# Generated with shared setup utilities")
            
            if analysis_results.get('comprehensive_analysis'):
                comp_analysis = analysis_results['comprehensive_analysis']
                if comp_analysis.get('similar_tests'):
                    header_comments.append(f"# Found {len(comp_analysis['similar_tests'])} similar tests in codebase")
            
            # Insert comments at the beginning after imports
            import_end_idx = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from'):
                    import_end_idx = i
                    break
            
            lines[import_end_idx:import_end_idx] = header_comments + [""]
        
        return '\n'.join(lines)
    
    def _extract_clean_test_content(self, script: str, config: Config) -> str:
        """Extract the main test content, removing inline utilities."""
        
        script_lines = script.split('\n')
        clean_lines = []
        
        # Skip common utility functions and imports that are now in shared setup
        skip_patterns = [
            'def replace_sensitive_data(',
            'class E2eActionError(',
            'async def safe_action(',
            'async def try_locate_and_act(',
            'def safe_selenium_action(',
            'SENSITIVE_DATA = {}',
            'import traceback',
            'from datetime import datetime',
        ]
        
        in_utility_function = False
        
        for line in script_lines:
            stripped_line = line.strip()
            
            # Check if we're starting a utility function
            if any(pattern in stripped_line for pattern in skip_patterns):
                in_utility_function = True
                continue
            
            # Check if we're ending a utility function (blank line after function)
            if in_utility_function and not stripped_line:
                # Look ahead to see if next non-empty line is another function/import
                in_utility_function = False
                continue
            
            # Skip lines inside utility functions
            if in_utility_function:
                continue
            
            # Skip redundant imports that are now handled by shared setup
            if any(pattern in stripped_line for pattern in [
                'import sys',
                'import os', 
                'from pathlib import Path',
                'import urllib.parse',
                'from dotenv import load_dotenv'
            ]) and 'playwright' not in stripped_line and 'selenium' not in stripped_line:
                continue
            
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def _generate_fallback_script(self, automation_data: Any, config: Config) -> str:
        """Generate a basic fallback script when main generation fails."""
        try:
            # Parse data with minimal processing
            parsed_data = self.input_parser.parse(automation_data)
            
            # Create plugin without analysis
            plugin = self.plugin_registry.create_plugin(config.output)
            
            # Generate basic script
            generated_script = plugin.generate_test_script(
                parsed_data=parsed_data,
                analysis_results=None,
                system_context=None
            )
            
            # Add fallback comment
            fallback_comment = "# Generated in fallback mode (limited analysis)\n"
            return fallback_comment + generated_script.content
            
        except Exception as e:
            # Last resort: return error message as comment
            return f"""# Error: Failed to generate test script
# Original error: {e}
# Please check your automation data format and configuration
""" 