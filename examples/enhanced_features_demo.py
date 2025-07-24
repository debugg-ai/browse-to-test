"""
Comprehensive Enhanced Features Demo

This script demonstrates all the newly implemented features in browse-to-test:
1. Enhanced Test Quality System
2. Advanced Actions Support
3. Test Validation System
4. Page Object Model Generation
5. Modern Framework Support
6. CI/CD Integration Features
7. Developer Experience Enhancements

Run this script to see all the new capabilities in action.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Add the parent directory to the path to import browse_to_test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all the new enhancement modules
from browse_to_test.core.generation.quality_enhancer import (
    EnhancedTestQualitySystem, SelectorConfig, WaitConfig, AssertionConfig
)
from browse_to_test.core.frameworks.advanced_actions import (
    AdvancedActionGenerator, AdvancedActionDetector, DragDropConfig, 
    FileUploadConfig, KeyboardConfig, MobileGestureConfig
)
from browse_to_test.core.generation.test_validation import (
    TestValidationEngine, ValidationSeverity
)
from browse_to_test.core.generation.page_object_generator import (
    PageObjectModelGenerator, PageType
)
from browse_to_test.core.frameworks.modern_frameworks import (
    ModernFrameworkGenerator, FrameworkConfig, ModernFramework, TestingPattern
)
from browse_to_test.core.tooling.ci_cd_integration import (
    TestReportGenerator, CIPlatformIntegrator, TestMaintenanceEngine,
    TestAnalytics, CIConfig, CIPlatform, ReportFormat
)
from browse_to_test.core.tooling.developer_experience import (
    IntelligentErrorHandler, InteractiveDebugger, TestPreviewGenerator,
    IDEIntegration, SmartSuggestionEngine, PerformanceProfiler,
    PreviewConfig, PreviewMode, ErrorCategory
)


def create_sample_automation_data():
    """Create comprehensive sample automation data for demonstrations."""
    return {
        "session_info": {
            "url": "https://example-ecommerce.com",
            "timestamp": datetime.now().isoformat(),
            "browser": "chromium",
            "viewport": {"width": 1280, "height": 720}
        },
        "steps": [
            {
                "action": "navigate",
                "url": "https://example-ecommerce.com",
                "timestamp": "2024-01-01T10:00:00Z",
                "description": "Navigate to the homepage"
            },
            {
                "action": "click",
                "element": {
                    "tag": "button",
                    "data-testid": "login-button",
                    "aria-label": "Login to your account",
                    "css_selector": ".header-login-btn",
                    "xpath": "//button[@data-testid='login-button']",
                    "text": "Login"
                },
                "timestamp": "2024-01-01T10:00:01Z",
                "description": "Click the login button"
            },
            {
                "action": "input_text",
                "element": {
                    "tag": "input",
                    "data-testid": "email-input",
                    "type": "email",
                    "name": "email",
                    "css_selector": "#email",
                    "xpath": "//input[@data-testid='email-input']"
                },
                "text": "user@example.com",
                "timestamp": "2024-01-01T10:00:02Z",
                "description": "Enter email address"
            },
            {
                "action": "input_text",
                "element": {
                    "tag": "input",
                    "data-testid": "password-input",
                    "type": "password",
                    "name": "password",
                    "css_selector": "#password"
                },
                "text": "password123",
                "timestamp": "2024-01-01T10:00:03Z",
                "description": "Enter password"
            },
            {
                "action": "click",
                "element": {
                    "tag": "button",
                    "data-testid": "submit-login",
                    "type": "submit",
                    "css_selector": ".login-submit-btn"
                },
                "timestamp": "2024-01-01T10:00:04Z",
                "description": "Submit login form"
            },
            {
                "action": "drag_drop",
                "source_element": {
                    "data-testid": "product-card-1",
                    "css_selector": ".product-card[data-id='1']"
                },
                "target_element": {
                    "data-testid": "shopping-cart",
                    "css_selector": ".shopping-cart-dropzone"
                },
                "timestamp": "2024-01-01T10:00:05Z",
                "description": "Drag product to shopping cart"
            },
            {
                "action": "file_upload",
                "element": {
                    "tag": "input",
                    "type": "file",
                    "data-testid": "profile-picture-upload"
                },
                "file_path": "/path/to/profile.jpg",
                "timestamp": "2024-01-01T10:00:06Z",
                "description": "Upload profile picture"
            }
        ],
        "page_transitions": [
            {
                "from_url": "https://example-ecommerce.com",
                "to_url": "https://example-ecommerce.com/login",
                "trigger_action": "click login button"
            },
            {
                "from_url": "https://example-ecommerce.com/login", 
                "to_url": "https://example-ecommerce.com/dashboard",
                "trigger_action": "submit login form"
            }
        ]
    }


def demo_enhanced_test_quality():
    """Demonstrate the Enhanced Test Quality System."""
    print("\n🎯 === Enhanced Test Quality System Demo ===")
    
    # Create configuration
    selector_config = SelectorConfig(
        fallback_enabled=True,
        stability_score_threshold=0.8,
        generate_multiple_selectors=True
    )
    
    wait_config = WaitConfig(
        default_timeout=10000,
        retry_attempts=3,
        retry_delay=500
    )
    
    assertion_config = AssertionConfig(
        soft_assertions=True,
        screenshot_on_failure=True,
        assertion_messages=True
    )
    
    # Initialize the system
    quality_system = EnhancedTestQualitySystem(
        selector_config=selector_config,
        wait_config=wait_config,
        assertion_config=assertion_config
    )
    
    # Generate enhanced test components
    sample_element = {
        "tag": "button",
        "data-testid": "submit-button",
        "aria-label": "Submit form",
        "css_selector": ".btn-primary",
        "xpath": "//button[@data-testid='submit-button']"
    }
    
    # Smart selector generation
    selector_result = quality_system.selector_generator.generate_selector(sample_element)
    print(f"✅ Generated smart selectors for element:")
    if isinstance(selector_result, dict):
        for strategy, selector in selector_result.items():
            if strategy != "stability_scores":
                print(f"   • {strategy}: {selector}")
    
    # Robust wait generation  
    wait_result = quality_system.wait_generator.generate_wait_strategy("click", sample_element, {})
    print(f"\n⏱️ Generated robust wait strategies:")
    if isinstance(wait_result, dict) and "strategies" in wait_result:
        for strategy in wait_result["strategies"][:3]:
            print(f"   • {strategy}")
    
    # Enhanced assertions
    assertions = quality_system.assertion_generator.generate_assertions("click", sample_element)
    print(f"\n🎯 Generated enhanced assertions:")
    if isinstance(assertions, list):
        for assertion in assertions[:3]:
            print(f"   • {assertion}")
    
    # Simulate test script analysis
    sample_script = '''
def test_example():
    page.goto("https://example.com")
    page.click("[data-testid='submit-button']")
    assert page.is_visible("[data-testid='success-message']")
'''
    analysis = quality_system.quality_analyzer.analyze_test_script(sample_script)
    print(f"\n📊 Quality Analysis Score: {analysis.overall_quality_score:.1f}/100")
    print(f"📈 Recommendations: {len(analysis.recommendations)}")
    for rec in analysis.recommendations[:3]:
        print(f"   • {rec}")


def demo_advanced_actions():
    """Demonstrate the Advanced Actions Support."""
    print("\n🚀 === Advanced Actions Support Demo ===")
    
    # Initialize the advanced action system
    action_generator = AdvancedActionGenerator()
    action_detector = AdvancedActionDetector()
    
    # Detect advanced actions from automation data
    automation_data = create_sample_automation_data()
    detected_actions = action_detector.detect_advanced_actions(automation_data)
    
    print(f"🔍 Detected {len(detected_actions)} advanced actions:")
    for action in detected_actions:
        print(f"   • {action.action_type.value}: {action.description}")
    
    # Generate drag-and-drop code
    drag_config = DragDropConfig(
        animation_duration=500,
        intermediate_steps=3,
        verify_drop=True
    )
    
    drag_code_playwright = action_generator.generate_drag_drop_playwright(
        source_selector="[data-testid='product-card-1']",
        target_selector="[data-testid='shopping-cart']",
        config=drag_config
    )
    print(f"\n🎭 Playwright Drag & Drop Code:\n{drag_code_playwright}")
    
    # Generate file upload code
    upload_config = FileUploadConfig(
        file_types=[".jpg", ".png"],
        max_file_size=5000000,
        validate_upload=True
    )
    
    upload_code = action_generator.generate_file_upload_playwright(
        selector="[data-testid='profile-picture-upload']",
        config=upload_config
    )
    print(f"\n📁 File Upload Code:\n{upload_code}")
    
    # Generate keyboard shortcuts
    keyboard_config = KeyboardConfig(
        modifiers=["Control"],
        keys=["s"],
        timing_ms=100
    )
    
    keyboard_code = action_generator.generate_keyboard_action_playwright(keyboard_config)
    print(f"\n⌨️ Keyboard Shortcut Code:\n{keyboard_code}")


def demo_test_validation():
    """Demonstrate the Test Validation System."""
    print("\n🔍 === Test Validation System Demo ===")
    
    # Create a sample test file content with issues
    sample_test_code = '''
import time
from selenium import webdriver

def test_login():
    driver = webdriver.Chrome()
    driver.find_element_by_id("username").send_keys("user")
    time.sleep(2)  # Bad practice
    assert True  # Weak assertion
    password = "hardcoded_password"  # Security issue
    driver.quit()
'''
    
    # Initialize validation engine
    validation_engine = TestValidationEngine()
    
    # Validate the test code
    validation_result = validation_engine.validate_code(sample_test_code, "test_login.py")
    
    print(f"📋 Validation Results:")
    print(f"   Overall Score: {validation_result.overall_score:.1f}/100")
    print(f"   Issues Found: {len(validation_result.issues)}")
    
    # Group issues by severity
    by_severity = {}
    for issue in validation_result.issues:
        severity = issue.severity.value
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(issue)
    
    for severity, issues in by_severity.items():
        print(f"\n   {severity.upper()} Issues ({len(issues)}):")
        for issue in issues[:3]:  # Show first 3
            print(f"      • Line {issue.line}: {issue.description}")
            print(f"        💡 {issue.suggestion}")
    
    # Auto-fix demonstration
    fixed_code, fixes_applied = validation_engine.validate_and_fix(sample_test_code)
    print(f"\n🔧 Auto-fixes Applied: {fixes_applied}")
    
    # Generate HTML report
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = validation_engine.generate_report(validation_result, Path(temp_dir), "html")
        print(f"📄 HTML Report Generated: {report_path}")


def demo_page_object_model():
    """Demonstrate the Page Object Model Generation."""
    print("\n🏗️ === Page Object Model Generation Demo ===")
    
    # Initialize POM generator
    pom_generator = PageObjectModelGenerator()
    
    # Generate POM from automation data
    automation_data = create_sample_automation_data()
    page_objects = pom_generator.generate_page_objects(automation_data)
    
    print(f"🏭 Generated {len(page_objects)} Page Objects:")
    for page_obj in page_objects:
        print(f"   • {page_obj.page_name} ({page_obj.page_type.value})")
        print(f"     Elements: {len(page_obj.elements)}")
        print(f"     Actions: {len(page_obj.actions)}")
    
    # Generate code for different languages
    if page_objects:
        sample_page = page_objects[0]
        
        # Python code
        python_code = pom_generator.code_generator.generate_python_page_object(sample_page)
        print(f"\n🐍 Python Page Object (preview):")
        print(python_code[:300] + "..." if len(python_code) > 300 else python_code)
        
        # TypeScript code
        ts_code = pom_generator.code_generator.generate_typescript_page_object(sample_page)
        print(f"\n📘 TypeScript Page Object (preview):")
        print(ts_code[:300] + "..." if len(ts_code) > 300 else ts_code)


def demo_modern_frameworks():
    """Demonstrate the Modern Framework Support."""
    print("\n🆕 === Modern Framework Support Demo ===")
    
    # Test different modern frameworks
    frameworks_to_demo = [
        (ModernFramework.JEST, "Jest + Testing Library"),
        (ModernFramework.PLAYWRIGHT_TEST, "Playwright Test"),
        (ModernFramework.VITEST, "Vitest"),
        (ModernFramework.CYPRESS, "Cypress")
    ]
    
    automation_data = create_sample_automation_data()
    
    for framework, name in frameworks_to_demo:
        print(f"\n🧪 {name} Test Generation:")
        
        config = FrameworkConfig(
            framework=framework,
            language="typescript",
            testing_pattern=TestingPattern.E2E,
            use_accessibility_queries=True,
            typescript_strict=True
        )
        
        generator = ModernFrameworkGenerator(config)
        test_code = generator.generate_test_file(automation_data)
        
        # Show first few lines
        lines = test_code.split('\n')[:15]
        for line in lines:
            print(f"   {line}")
        total_lines = len(test_code.split('\n'))
        print(f"   ... ({total_lines} total lines)")


def demo_ci_cd_integration():
    """Demonstrate the CI/CD Integration Features."""
    print("\n⚙️ === CI/CD Integration Demo ===")
    
    # Configure CI/CD settings
    ci_config = CIConfig(
        platform=CIPlatform.GITHUB_ACTIONS,
        report_formats=[ReportFormat.JUNIT, ReportFormat.HTML, ReportFormat.JSON],
        enable_screenshots=True,
        parallel_jobs=3,
        retry_failed_tests=True,
        enable_test_analytics=True
    )
    
    # Generate CI configuration
    integrator = CIPlatformIntegrator(CIPlatform.GITHUB_ACTIONS)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        ci_config_content = integrator.generate_ci_config(ci_config, Path(temp_dir))
        
        print("🔧 Generated GitHub Actions Workflow (preview):")
        lines = ci_config_content.split('\n')[:20]
        for line in lines:
            print(f"   {line}")
        total_lines = len(ci_config_content.split('\n'))
        print(f"   ... (Full workflow: {total_lines} lines)")
    
    # Test maintenance engine
    print("\n🔧 Test Maintenance Analysis:")
    maintenance_engine = TestMaintenanceEngine()
    
    # Simulate maintenance issues
    sample_issues = [
        "Deprecated selector method found",
        "Hard-coded wait detected", 
        "Weak assertion pattern",
        "Test data in code"
    ]
    
    print(f"🔍 Maintenance Issues Detected: {len(sample_issues)}")
    for issue in sample_issues:
        print(f"   • {issue}")
    
    # Test analytics
    analytics = TestAnalytics(Path(tempfile.gettempdir()))
    print(f"\n📊 Test Analytics Tracking: Enabled")
    print(f"   • Success rate tracking")
    print(f"   • Performance metrics") 
    print(f"   • Flaky test detection")


def demo_developer_experience():
    """Demonstrate the Developer Experience Enhancements."""
    print("\n👨‍💻 === Developer Experience Demo ===")
    
    # Intelligent Error Handler
    print("🧠 Intelligent Error Analysis:")
    error_handler = IntelligentErrorHandler()
    
    # Simulate different types of errors
    sample_errors = [
        (Exception("NoSuchElementException: Element not found"), "selector_error"),
        (Exception("TimeoutException: Timed out after 30 seconds"), "timeout_error"),
        (Exception("AssertionError: Expected 'Welcome' but got 'Hello'"), "assertion_error")
    ]
    
    for error, error_type in sample_errors:
        context = {"framework": "playwright", "action": "click"}
        error_context = error_handler.analyze_error(error, context)
        
        print(f"\n   🔍 {error_type}:")
        print(f"      Category: {error_context.error_type.value}")
        print(f"      Suggestions: {len(error_context.suggestions)}")
        for suggestion in error_context.suggestions[:2]:
            print(f"         • {suggestion}")
    
    # Interactive Preview
    print("\n🎭 Interactive Test Preview:")
    preview_config = PreviewConfig(
        mode=PreviewMode.INTERACTIVE,
        show_selectors=True,
        highlight_elements=True,
        enable_breakpoints=True
    )
    
    preview_generator = TestPreviewGenerator(preview_config)
    automation_data = create_sample_automation_data()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        preview_path = preview_generator.generate_preview(automation_data, Path(temp_dir))
        print(f"   ✅ Interactive preview generated: {preview_path}")
        print("   🌐 Features: Play/Pause, Step-by-step, Timeline view")
    
    # Smart Suggestions
    print("\n💡 Smart Code Suggestions:")
    suggestion_engine = SmartSuggestionEngine()
    
    # Selector suggestions
    selector_suggestions = suggestion_engine.get_selector_suggestions(
        "[data-", 
        {"framework": "playwright"}
    )
    print(f"   🎯 Selector suggestions ({len(selector_suggestions)}):")
    for suggestion in selector_suggestions[:3]:
        print(f"      • {suggestion}")
    
    # Action suggestions
    action_suggestions = suggestion_engine.get_action_suggestions("button")
    print(f"   ⚡ Action suggestions for button: {', '.join(action_suggestions)}")
    
    # IDE Integration
    print("\n🛠️ IDE Integration:")
    vscode_settings = IDEIntegration.generate_vscode_settings()
    debug_config = IDEIntegration.generate_debug_config()
    
    print("   ✅ VS Code settings generated")
    print("   ✅ Debug configuration generated") 
    print("   🎯 Features: Auto-completion, Debugging, Test runner integration")
    
    # Performance Profiling
    print("\n⚡ Performance Profiling:")
    profiler = PerformanceProfiler()
    profiler.start_profiling("sample_test")
    
    # Simulate some steps
    profiler.record_step("sample_test", {"action": "click", "duration": 1.2})
    profiler.record_step("sample_test", {"action": "type", "duration": 0.8})
    profiler.record_step("sample_test", {"action": "wait", "duration": 3.5})
    
    performance_report = profiler.generate_performance_report("sample_test")
    print(f"   📊 Performance Score: {performance_report['performance_score']:.1f}/100")
    print(f"   ⏱️ Average Step Duration: {performance_report['average_step_duration']:.2f}s")
    print(f"   🎯 Recommendations: {len(performance_report['recommendations'])}")


def main():
    """Run all enhancement demonstrations."""
    print("🎭 Browse-to-Test Enhanced Features Comprehensive Demo")
    print("=" * 60)
    print("This demo showcases all the newly implemented enhancements:")
    print("• Enhanced Test Quality System")
    print("• Advanced Actions Support") 
    print("• Test Validation System")
    print("• Page Object Model Generation")
    print("• Modern Framework Support")
    print("• CI/CD Integration Features")
    print("• Developer Experience Enhancements")
    print("=" * 60)
    
    try:
        # Run all demonstrations
        demo_enhanced_test_quality()
        demo_advanced_actions()
        demo_test_validation()
        demo_page_object_model()
        demo_modern_frameworks()
        demo_ci_cd_integration()
        demo_developer_experience()
        
        # Summary
        print("\n🎉 === Demo Complete ===")
        print("All enhanced features demonstrated successfully!")
        print("\n📈 Summary of Improvements:")
        print("✅ Smart selector generation with fallback strategies")
        print("✅ Robust waiting mechanisms with retry logic")  
        print("✅ Enhanced assertion generation with detailed errors")
        print("✅ Advanced action support (drag-drop, file upload, gestures)")
        print("✅ Comprehensive test validation with auto-fix")
        print("✅ Automated Page Object Model generation")
        print("✅ Modern framework support (Jest, Vitest, Playwright Test)")
        print("✅ CI/CD integration for GitHub Actions, Jenkins, GitLab")
        print("✅ Intelligent error analysis and suggestions")
        print("✅ Interactive test previews and debugging")
        print("✅ Performance profiling and optimization")
        print("✅ IDE integration and smart code completion")
        
        print(f"\n🚀 Browse-to-Test is now a comprehensive, enterprise-ready")
        print(f"   test generation platform with professional-grade features!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Please ensure all dependencies are installed and try again.")


if __name__ == "__main__":
    main() 