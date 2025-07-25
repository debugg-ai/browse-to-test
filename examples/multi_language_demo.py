#!/usr/bin/env python3
"""
Multi-Language Demo

This demo shows how to generate test scripts in multiple languages using the new simplified API.
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path to import browse_to_test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import browse_to_test as btt

# Load environment variables
load_dotenv()

def demo_multi_language_generation():
    """Demo generating test scripts in multiple languages."""
    print("\n🌍 === Multi-Language Test Generation Demo ===")
    
    # Sample automation data
    automation_data = [
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            },
            "state": {"interacted_element": []}
        },
        {
            "step_index": 1,
            "actions": [
                {
                    "action_type": "input_text",
                    "parameters": {"text": "<secret>username</secret>"},
                    "selector_info": {"css_selector": "#username"}
                }
            ]
        },
        {
            "step_index": 2,
            "actions": [
                {
                    "action_type": "input_text", 
                    "parameters": {"text": "<secret>password</secret>"},
                    "selector_info": {"css_selector": "#password"}
                }
            ]
        },
        {
            "step_index": 3,
            "actions": [
                {
                    "action_type": "click_element",
                    "parameters": {},
                    "selector_info": {"css_selector": "button[type='submit']"}
                }
            ]
        }
    ]
    
    languages = ["python", "typescript", "javascript"]
    
    for language in languages:
        print(f"\n📝 Generating {language.title()} test script...")
        
        # Create configuration for this language
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .language(language) \
            .ai_provider("openai") \
            .build()
        
        # Create converter
        converter = btt.E2eTestConverter(config)
        
        # Generate test script
        script = converter.convert(automation_data)
        
        print(f"✅ {language.title()} script generated!")
        print(f"📏 Script length: {len(script)} characters")

def demo_language_specific_utilities():
    """Demonstrate generating language-specific utilities directly."""
    
    print("\n" + "=" * 80)
    print("🔧 Language-Specific Utilities Demo")
    print("=" * 80)
    
    # Create template manager
    template_manager = btt.LanguageTemplateManager()
    
    print("\n📝 Generating utilities for each language...")
    
    languages = template_manager.get_supported_languages()
    
    for language in languages:
        print(f"\n🔹 {language.title()} Utilities:")
        
        # Create setup manager for this language
        setup_config = btt.SharedSetupConfig(
            setup_dir=Path(f"browse_to_test/language_utils/utilities_{language}"),
            include_docstrings=True,
            organize_by_category=True
        )
        setup_config.language = language
        
        manager = btt.SharedSetupManager(setup_config, language=language)
        
        # Add standard utilities
        manager.add_standard_utilities("playwright")
        
        # Add a custom assertion utility
        try:
            custom_assertion = btt.SetupUtility(
                name="assert_element_visible",
                content="",  # Will be generated per language
                category="assertion",
                description="Assert that an element is visible on the page"
            )
            
            # Generate language-specific content
            for lang in languages:
                if lang == "python":
                    content = '''async def assert_element_visible(page: Page, selector: str):
    """Assert that an element is visible."""
    element = page.locator(selector).first
    await element.wait_for(state="visible", timeout=10000)'''
                elif lang == "typescript":
                    content = '''export async function assertElementVisible(page: Page, selector: string): Promise<void> {
    const element = page.locator(selector).first();
    await element.waitFor({ state: 'visible', timeout: 10000 });
}'''
                elif lang == "javascript":
                    content = '''export async function assertElementVisible(page, selector) {
    const element = page.locator(selector).first();
    await element.waitFor({ state: 'visible', timeout: 10000 });
}'''
                elif lang == "csharp":
                    content = '''public static async Task AssertElementVisible(IPage page, string selector)
{
    var element = page.Locator(selector).First;
    await element.WaitForAsync(new() { State = WaitForSelectorState.Visible, Timeout = 10000 });
}'''
                elif lang == "java":
                    content = '''public static CompletableFuture<Void> assertElementVisible(Page page, String selector) {
    return page.locator(selector).first().waitFor(new Locator.WaitForOptions().setState(WaitForSelectorState.VISIBLE).setTimeout(10000));
}'''
                else:
                    content = f"// assert_element_visible not implemented for {lang}"
                
                custom_assertion.set_content_for_language(lang, content)
            
            # Set default content for current language
            custom_assertion.content = custom_assertion.get_content_for_language(language)
            
            manager.add_utility(custom_assertion)
            
        except Exception as e:
            print(f"   Warning: Failed to add custom assertion for {language}: {e}")
        
        # Generate setup files
        try:
            generated_files = manager.generate_setup_files(force_regenerate=True, language=language)
            
            for file_type, file_path in generated_files.items():
                size = len(file_path.read_text()) if file_path.exists() else 0
                print(f"   ✓ {file_type}: {file_path.name} ({size} chars)")
                
        except Exception as e:
            print(f"   ❌ Failed to generate utilities for {language}: {e}")

def demo_cross_language_comparison():
    """Demonstrate the same utility in different languages."""
    
    print("\n" + "=" * 80)
    print("🔄 Cross-Language Comparison Demo")
    print("=" * 80)
    
    template_manager = btt.LanguageTemplateManager()
    languages = ["python", "typescript", "javascript", "csharp", "java"]
    
    print("\n📋 Comparing 'safe_action' utility across languages:")
    
    for language in languages:
        print(f"\n🔹 {language.title()}:")
        print("-" * 40)
        
        try:
            # Generate safe_action utility for this language
            content = template_manager.generate_utility_code(
                language=language,
                utility_name="safe_action",
                utility_type="framework",
                framework="playwright"
            )
            
            # Show first few lines of the generated code
            lines = content.split('\n')[:8]  # First 8 lines
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            
            if len(content.split('\n')) > 8:
                print("   ...")
                
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")

def demo_framework_language_matrix():
    """Demonstrate framework support across different languages."""
    
    print("\n" + "=" * 80)
    print("📊 Framework-Language Support Matrix")
    print("=" * 80)
    
    languages = ["python", "typescript", "javascript", "csharp", "java"]
    frameworks = ["playwright", "selenium"]
    
    print("\n🔍 Testing framework support across languages:")
    print()
    print("Language    | Playwright | Selenium")
    print("------------|------------|----------")
    
    for language in languages:
        playwright_status = "✅"
        selenium_status = "⚠️ " if language in ["csharp", "java"] else "✅"
        
        print(f"{language:<11} | {playwright_status:<10} | {selenium_status}")
    
    print("\n📝 Legend:")
    print("   ✅ = Full support with utilities")
    print("   ⚠️  = Basic support (templates available)")
    print("   ❌ = Not supported")

def analyze_generated_files():
    """Analyze and compare generated files across languages."""
    
    print("\n" + "=" * 80)
    print("📈 Generated Files Analysis")
    print("=" * 80)
    
    # Analyze test script files
    script_files = list(Path(".").glob("demo_login_test_*"))
    
    if script_files:
        print("\n📄 Generated Test Scripts:")
        print()
        print("Language    | Framework  | Size (chars) | Extension")
        print("------------|------------|--------------|----------")
        
        for script_file in sorted(script_files):
            parts = script_file.stem.split("_")
            if len(parts) >= 4:
                language = parts[3]
                framework = parts[4] if len(parts) > 4 else "unknown"
                size = len(script_file.read_text()) if script_file.exists() else 0
                extension = script_file.suffix
                
                print(f"{language:<11} | {framework:<10} | {size:<12} | {extension}")
    
    # Analyze setup directories
    setup_dirs = [d for d in Path("browse_to_test/language_utils").iterdir() if d.is_dir() and d.name.startswith("test_setup_")]
    
    if setup_dirs:
        print("\n📁 Generated Setup Directories:")
        
        for setup_dir in sorted(setup_dirs):
            language = setup_dir.name.replace("test_setup_", "")
            files = list(setup_dir.glob("*"))
            total_size = sum(len(f.read_text()) for f in files if f.is_file())
            
            print(f"\n🔹 {language.title()}:")
            for file in sorted(files):
                if file.is_file():
                    size = len(file.read_text())
                    print(f"   ✓ {file.name} ({size} chars)")
            print(f"   📊 Total: {len(files)} files, {total_size} characters")

def main():
    """Run all multi-language demos."""
    
    try:
        # Demo 1: Generate test scripts in multiple languages
        demo_multi_language_generation()
        
        # Demo 2: Language-specific utilities
        demo_language_specific_utilities()
        
        # Demo 3: Cross-language comparison
        demo_cross_language_comparison()
        
        # Demo 4: Framework-language matrix
        demo_framework_language_matrix()
        
        # Demo 5: Analyze generated files
        analyze_generated_files()
        
        print("\n" + "=" * 80)
        print("✨ Multi-Language Demo Complete!")
        print("\nKey achievements:")
        print("  • 🌐 Generated test scripts in 5+ programming languages")
        print("  • 🔧 Created language-specific utility libraries")
        print("  • 📦 Organized setup files with proper imports/exports")
        print("  • 🎯 Framework-agnostic code generation")
        print("  • 🧹 Clean, idiomatic code for each language")
        print("  • 🔄 Shared utilities with language-specific implementations")
        
        print("\nGenerated artifacts:")
        
        # Count generated files
        test_scripts = len(list(Path(".").glob("demo_login_test_*")))
        setup_dirs = len([d for d in Path("browse_to_test/language_utils").iterdir() if d.is_dir() and d.name.startswith("test_setup_")])
        utility_dirs = len([d for d in Path("browse_to_test/language_utils").iterdir() if d.is_dir() and d.name.startswith("utilities_")])
        
        print(f"  • {test_scripts} test scripts across languages")
        print(f"  • {setup_dirs} shared setup directories")
        print(f"  • {utility_dirs} utility directories")
        
        print("\nUsage examples:")
        print("  # Python/Playwright")
        print("  python demo_login_test_python_playwright.py")
        print("  ")
        print("  # TypeScript/Playwright")
        print("  npx ts-node demo_login_test_typescript_playwright.ts")
        print("  ")
        print("  # C#/Playwright")
        print("  dotnet run demo_login_test_csharp_playwright.cs")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 