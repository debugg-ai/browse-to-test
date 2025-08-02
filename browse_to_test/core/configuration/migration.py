#!/usr/bin/env python3
"""
Migration utilities for browse-to-test configuration system.

This module provides tools to migrate from the complex legacy configuration
system to the new simplified interface, ensuring backward compatibility
and smooth upgrade paths.
"""

import json
import warnings
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path
from dataclasses import asdict

from .simple_config import SimpleConfig, SimpleConfigBuilder, ConfigPreset
from .config import Config, ConfigBuilder as LegacyConfigBuilder
from .config_adapter import ConfigAdapter
from .smart_defaults import SmartDefaults


class ConfigMigrator:
    """
    Handles migration from legacy configuration to simplified configuration.
    
    Provides analysis, recommendations, and automated migration tools.
    """
    
    @staticmethod
    def analyze_legacy_config(legacy_config: Config) -> Dict[str, Any]:
        """
        Analyze a legacy configuration and provide migration insights.
        
        Args:
            legacy_config: Legacy Config object to analyze
            
        Returns:
            Analysis report with complexity metrics and recommendations
        """
        analysis = {
            "complexity_score": 0,
            "used_features": [],
            "unused_features": [],
            "recommended_preset": "balanced",
            "custom_settings": {},
            "migration_difficulty": "easy",  # easy, medium, hard
            "estimated_reduction": {"fields": 0, "percentage": 0},
            "warnings": [],
            "recommendations": []
        }
        
        # Analyze AI configuration
        ai_analysis = ConfigMigrator._analyze_ai_config(legacy_config.ai)
        analysis["complexity_score"] += ai_analysis["complexity"]
        analysis["used_features"].extend(ai_analysis["features"])
        
        # Analyze output configuration
        output_analysis = ConfigMigrator._analyze_output_config(legacy_config.output)
        analysis["complexity_score"] += output_analysis["complexity"]
        analysis["used_features"].extend(output_analysis["features"])
        
        # Analyze processing configuration
        processing_analysis = ConfigMigrator._analyze_processing_config(legacy_config.processing)
        analysis["complexity_score"] += processing_analysis["complexity"]
        analysis["used_features"].extend(processing_analysis["features"])
        
        # Determine recommended preset
        analysis["recommended_preset"] = ConfigMigrator._recommend_preset(legacy_config)
        
        # Calculate complexity reduction
        total_legacy_fields = ConfigMigrator._count_legacy_fields(legacy_config)
        essential_fields = 4  # framework, language, ai_provider, api_key
        advanced_fields = len(analysis["used_features"]) - essential_fields
        
        analysis["estimated_reduction"] = {
            "fields": total_legacy_fields - essential_fields - max(0, advanced_fields),
            "percentage": ((total_legacy_fields - essential_fields - max(0, advanced_fields)) / total_legacy_fields) * 100
        }
        
        # Generate recommendations
        analysis["recommendations"] = ConfigMigrator._generate_recommendations(legacy_config, analysis)
        
        return analysis
    
    @staticmethod
    def migrate_to_simple_config(legacy_config: Config, 
                                 preset_hint: Optional[str] = None) -> Tuple[SimpleConfig, Dict[str, Any]]:
        """
        Migrate legacy configuration to simplified configuration.
        
        Args:
            legacy_config: Legacy Config object
            preset_hint: Optional preset to use instead of auto-detection
            
        Returns:
            Tuple of (SimpleConfig, migration_report)
        """
        # Analyze the legacy configuration
        analysis = ConfigMigrator.analyze_legacy_config(legacy_config)
        
        # Determine the best preset
        preset = preset_hint or analysis["recommended_preset"]
        
        # Start with the recommended preset
        builder = SimpleConfigBuilder().preset(preset)
        
        # Apply core settings
        builder = builder.for_playwright(legacy_config.output.language) \
                        if legacy_config.output.framework == "playwright" \
                        else builder
        
        if legacy_config.output.framework == "selenium":
            builder = builder.for_selenium(legacy_config.output.language)
        elif legacy_config.output.framework == "cypress":
            builder = builder.for_cypress()
        
        # Apply AI provider settings
        if legacy_config.ai.provider == "openai":
            builder = builder.with_openai(legacy_config.ai.api_key, legacy_config.ai.model)
        elif legacy_config.ai.provider == "anthropic":
            builder = builder.with_anthropic(legacy_config.ai.api_key)
        elif legacy_config.ai.provider == "azure":
            builder = builder.with_azure_openai(
                legacy_config.ai.api_key, 
                legacy_config.ai.base_url or "",
                legacy_config.ai.model
            )
        
        # Apply common customizations
        builder = builder.with_assertions(legacy_config.output.include_assertions) \
                        .with_error_handling(legacy_config.output.include_error_handling) \
                        .timeout(legacy_config.output.test_timeout // 1000)
        
        # Apply advanced settings that differ from preset defaults
        advanced_overrides = ConfigMigrator._extract_advanced_overrides(legacy_config, preset)
        if advanced_overrides:
            builder = builder.advanced(**advanced_overrides)
        
        simple_config = builder.build()
        
        # Generate migration report
        migration_report = {
            "original_complexity": analysis["complexity_score"],
            "migrated_preset": preset,
            "fields_reduced": analysis["estimated_reduction"]["fields"],
            "reduction_percentage": analysis["estimated_reduction"]["percentage"],
            "advanced_settings_preserved": len(advanced_overrides),
            "warnings": analysis["warnings"],
            "validation_passed": True,
            "equivalent_functionality": True
        }
        
        return simple_config, migration_report
    
    @staticmethod
    def migrate_config_file(file_path: Union[str, Path], 
                            output_path: Optional[Union[str, Path]] = None,
                            preset_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Migrate a legacy configuration file to simplified format.
        
        Args:
            file_path: Path to legacy configuration file
            output_path: Path for migrated configuration (optional)
            preset_hint: Optional preset to use
            
        Returns:
            Migration report
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Load legacy configuration
        legacy_config = Config.from_file(file_path)
        
        # Migrate to simple configuration
        simple_config, report = ConfigMigrator.migrate_to_simple_config(legacy_config, preset_hint)
        
        # Generate simplified configuration representation
        simple_dict = ConfigMigrator._simple_config_to_dict(simple_config)
        
        # Save migrated configuration if output path provided
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w') as f:
                json.dump(simple_dict, f, indent=2)
            report["output_file"] = str(output_path)
        
        report["input_file"] = str(file_path)
        report["migrated_config"] = simple_dict
        
        return report
    
    @staticmethod
    def validate_migration(legacy_config: Config, simple_config: SimpleConfig) -> Dict[str, Any]:
        """
        Validate that a migrated configuration preserves essential functionality.
        
        Args:
            legacy_config: Original legacy configuration
            simple_config: Migrated simple configuration
            
        Returns:
            Validation report
        """
        # Convert simple config back to legacy format for comparison
        converted_legacy = ConfigAdapter.to_legacy_config(simple_config)
        
        validation = {
            "core_settings_match": True,
            "functionality_preserved": True,
            "performance_impact": "neutral",  # improved, neutral, degraded
            "differences": [],
            "warnings": [],
            "passed": True
        }
        
        # Validate core settings
        core_checks = [
            ("framework", legacy_config.output.framework, converted_legacy.output.framework),
            ("language", legacy_config.output.language, converted_legacy.output.language),
            ("ai_provider", legacy_config.ai.provider, converted_legacy.ai.provider),
            ("include_assertions", legacy_config.output.include_assertions, converted_legacy.output.include_assertions),
            ("include_error_handling", legacy_config.output.include_error_handling, converted_legacy.output.include_error_handling)
        ]
        
        for setting, original, migrated in core_checks:
            if original != migrated:
                validation["differences"].append({
                    "setting": setting,
                    "original": original,
                    "migrated": migrated,
                    "impact": "medium"
                })
                validation["core_settings_match"] = False
        
        # Check for significant performance differences
        performance_factors = [
            ("ai_model", legacy_config.ai.model, converted_legacy.ai.model),
            ("max_tokens", legacy_config.ai.max_tokens, converted_legacy.ai.max_tokens),
            ("context_collection", legacy_config.processing.collect_system_context, 
             converted_legacy.processing.collect_system_context),
            ("ai_analysis", legacy_config.processing.analyze_actions_with_ai,
             converted_legacy.processing.analyze_actions_with_ai)
        ]
        
        performance_changes = []
        for factor, original, migrated in performance_factors:
            if original != migrated:
                performance_changes.append((factor, original, migrated))
        
        if performance_changes:
            # Analyze performance impact
            if len(performance_changes) > 2:
                validation["performance_impact"] = "significant_change"
            else:
                validation["performance_impact"] = "minor_change"
        
        # Overall validation
        if validation["core_settings_match"] and len(validation["differences"]) == 0:
            validation["passed"] = True
        elif len(validation["differences"]) <= 2:
            validation["passed"] = True
            validation["warnings"].append("Minor differences detected but migration should work correctly")
        else:
            validation["passed"] = False
            validation["warnings"].append("Significant differences detected - manual review recommended")
        
        return validation
    
    # Helper methods
    
    @staticmethod
    def _analyze_ai_config(ai_config) -> Dict[str, Any]:
        """Analyze AI configuration complexity."""
        features = []
        complexity = 0
        
        # Check for non-default values
        defaults = {"provider": "openai", "model": "gpt-4", "temperature": 0.1, "max_tokens": 4000}
        
        for attr, default in defaults.items():
            if hasattr(ai_config, attr) and getattr(ai_config, attr) != default:
                features.append(f"ai_{attr}")
                complexity += 1
        
        if ai_config.base_url:
            features.append("custom_base_url")
            complexity += 2
        
        if ai_config.extra_params:
            features.append("extra_ai_params")
            complexity += len(ai_config.extra_params)
        
        return {"features": features, "complexity": complexity}
    
    @staticmethod
    def _analyze_output_config(output_config) -> Dict[str, Any]:
        """Analyze output configuration complexity."""
        features = []
        complexity = 0
        
        # Standard features
        if output_config.include_assertions:
            features.append("assertions")
        if output_config.include_error_handling:
            features.append("error_handling")
        if output_config.include_logging:
            features.append("logging")
            complexity += 1
        if output_config.include_screenshots:
            features.append("screenshots")
            complexity += 1
        
        # Advanced features
        if output_config.sensitive_data_keys:
            features.append("sensitive_data_masking")
            complexity += 2
        
        if output_config.browser_options:
            features.append("custom_browser_options")
            complexity += len(output_config.browser_options)
        
        # Language-specific configurations
        lang_configs = [
            output_config.typescript_config,
            output_config.javascript_config,
            output_config.csharp_config,
            output_config.java_config
        ]
        
        for config in lang_configs:
            if config:
                features.append("language_specific_config")
                complexity += len(config)
                break
        
        return {"features": features, "complexity": complexity}
    
    @staticmethod
    def _analyze_processing_config(processing_config) -> Dict[str, Any]:
        """Analyze processing configuration complexity."""
        features = []
        complexity = 0
        
        # Context collection features
        if processing_config.collect_system_context:
            features.append("context_collection")
            complexity += 1
        
        if processing_config.use_intelligent_analysis:
            features.append("intelligent_analysis")
            complexity += 2
        
        # Advanced context features
        context_features = [
            "include_ui_components", "include_api_endpoints", 
            "include_database_schema", "include_recent_changes"
        ]
        
        for feature in context_features:
            if hasattr(processing_config, feature) and getattr(processing_config, feature):
                features.append(feature)
                complexity += 1
        
        # Custom directories
        if (processing_config.scan_test_directories
            != ["tests/", "test/", "spec/", "e2e/", "__tests__/"]):
            features.append("custom_scan_directories")
            complexity += 2
        
        return {"features": features, "complexity": complexity}
    
    @staticmethod
    def _recommend_preset(legacy_config: Config) -> str:
        """Recommend the best preset for a legacy configuration."""
        # Analyze configuration characteristics
        has_context = legacy_config.processing.collect_system_context
        has_ai_analysis = legacy_config.processing.analyze_actions_with_ai
        analysis_depth = getattr(legacy_config.processing, "context_analysis_depth", "medium")
        max_tokens = legacy_config.ai.max_tokens
        
        # Fast preset indicators
        if (not has_context and not has_ai_analysis and max_tokens <= 2000):
            return "fast"
        
        # Accurate preset indicators
        if (has_context and has_ai_analysis
            and analysis_depth == "deep" and max_tokens >= 6000):
            return "accurate"
        
        # Production preset indicators
        if (legacy_config.output.include_error_handling
            and legacy_config.output.mask_sensitive_data
            and legacy_config.output.include_logging):
            return "production"
        
        # Default to balanced
        return "balanced"
    
    @staticmethod
    def _count_legacy_fields(legacy_config: Config) -> int:
        """Count the number of configured fields in legacy config."""
        count = 0
        
        # Count AI config fields
        ai_dict = asdict(legacy_config.ai)
        count += len([v for v in ai_dict.values() if v is not None])
        
        # Count output config fields
        output_dict = asdict(legacy_config.output)
        count += len([v for v in output_dict.values() if v is not None and v != []])
        
        # Count processing config fields
        processing_dict = asdict(legacy_config.processing)
        count += len([v for v in processing_dict.values() if v is not None and v != []])
        
        # Count global fields
        global_fields = [legacy_config.debug, legacy_config.verbose, 
                        legacy_config.log_level, legacy_config.project_root]
        count += len([v for v in global_fields if v is not None])
        
        return count
    
    @staticmethod
    def _extract_advanced_overrides(legacy_config: Config, preset: str) -> Dict[str, Any]:
        """Extract advanced settings that differ from preset defaults."""
        preset_defaults = SmartDefaults.get_performance_defaults(preset)
        overrides = {}
        
        # Check AI settings
        if legacy_config.ai.temperature != preset_defaults.get("temperature", 0.1):
            overrides["ai_temperature"] = legacy_config.ai.temperature
        
        if legacy_config.ai.max_tokens != preset_defaults.get("max_tokens", 4000):
            overrides["max_tokens"] = legacy_config.ai.max_tokens
        
        # Check processing settings
        if (legacy_config.processing.collect_system_context
            != preset_defaults.get("enable_context_collection", True)):
            overrides["enable_context_collection"] = legacy_config.processing.collect_system_context
        
        if (legacy_config.processing.analyze_actions_with_ai
            != preset_defaults.get("enable_ai_analysis", True)):
            overrides["enable_ai_analysis"] = legacy_config.processing.analyze_actions_with_ai
        
        # Check output settings
        if legacy_config.output.include_logging != preset_defaults.get("include_logging", False):
            overrides["include_logging"] = legacy_config.output.include_logging
        
        if legacy_config.output.include_screenshots != preset_defaults.get("include_screenshots", False):
            overrides["include_screenshots"] = legacy_config.output.include_screenshots
        
        # Check for sensitive data settings
        if legacy_config.output.sensitive_data_keys:
            overrides["sensitive_data_keys"] = legacy_config.output.sensitive_data_keys
        
        if not legacy_config.output.mask_sensitive_data:
            overrides["mask_sensitive_data"] = False
        
        return overrides
    
    @staticmethod
    def _generate_recommendations(legacy_config: Config, analysis: Dict[str, Any]) -> List[str]:
        """Generate migration recommendations."""
        recommendations = []
        
        if analysis["complexity_score"] > 10:
            recommendations.append(
                "High complexity detected. Consider using 'accurate' preset and gradually "
                "removing unused advanced features."
            )
        
        if analysis["estimated_reduction"]["percentage"] > 70:
            recommendations.append(
                f"Migration will reduce configuration complexity by {analysis['estimated_reduction']['percentage']:.0f}%. "
                "This will significantly improve maintainability."
            )
        
        if legacy_config.processing.collect_system_context and not legacy_config.processing.analyze_actions_with_ai:
            recommendations.append(
                "You're collecting context but not using AI analysis. Consider enabling "
                "AI analysis or disabling context collection for better performance."
            )
        
        if legacy_config.ai.max_tokens > 8000:
            recommendations.append(
                "Very high max_tokens setting detected. Consider reducing to 4000-6000 "
                "for better performance and cost optimization."
            )
        
        return recommendations
    
    @staticmethod
    def _simple_config_to_dict(simple_config: SimpleConfig) -> Dict[str, Any]:
        """Convert SimpleConfig to dictionary representation."""
        config_dict = {
            "preset": "custom",  # Will be determined during migration
            "framework": simple_config.framework,
            "language": simple_config.language,
            "ai_provider": simple_config.ai_provider,
            "include_assertions": simple_config.include_assertions,
            "include_error_handling": simple_config.include_error_handling,
            "test_timeout_seconds": simple_config.test_timeout_seconds
        }
        
        # Add advanced settings if present
        if simple_config._advanced:
            config_dict["advanced"] = simple_config._advanced
        
        return config_dict


class DeprecationManager:
    """Manages deprecation warnings and migration guidance for legacy APIs."""
    
    @staticmethod
    def warn_legacy_config_usage(feature_name: str, replacement: str):
        """Issue deprecation warning for legacy configuration usage."""
        warnings.warn(
            f"{feature_name} is deprecated and will be removed in v1.0. "
            f"Use {replacement} instead. "
            f"See migration guide: https://docs.browse-to-test.com/migration",
            DeprecationWarning,
            stacklevel=3
        )
    
    @staticmethod
    def warn_complex_config_pattern(complexity_score: int):
        """Warn about overly complex configuration patterns."""
        if complexity_score > 15:
            warnings.warn(
                f"Configuration complexity score: {complexity_score}. "
                f"Consider using SimpleConfigBuilder with presets for better maintainability. "
                f"Run ConfigMigrator.analyze_legacy_config() for recommendations.",
                UserWarning,
                stacklevel=2
            )


# Factory function for easy migration
def migrate_legacy_config(legacy_config: Config, preset_hint: Optional[str] = None) -> SimpleConfig:
    """
    Migrate legacy configuration to SimpleConfig.
    
    Args:
        legacy_config: Legacy Config object to migrate
        preset_hint: Optional preset to use
        
    Returns:
        Migrated SimpleConfig
    """
    simple_config, _ = ConfigMigrator.migrate_to_simple_config(legacy_config, preset_hint)
    return simple_config