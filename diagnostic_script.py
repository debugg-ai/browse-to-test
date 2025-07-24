#!/usr/bin/env python3

"""
Diagnostic Script for browse-to-test TypeScript Support Issues

This script helps diagnose and fix issues with TypeScript language support
in multiprocessing environments.
"""

import sys
import os
import json
from pathlib import Path
import multiprocessing
import importlib.util

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_basic_imports():
    """Check if basic imports work."""
    print_section("BASIC IMPORT CHECK")
    
    try:
        import browse_to_test as btt
        print("✓ browse_to_test import: SUCCESS")
        print(f"  Version: {getattr(btt, '__version__', 'Unknown')}")
    except Exception as e:
        print(f"✗ browse_to_test import: FAILED - {e}")
        return False
    
    try:
        from browse_to_test.output_langs.registry import SupportedLanguage, SupportedFramework
        print("✓ Registry imports: SUCCESS")
        print(f"  Available languages: {[lang.value for lang in SupportedLanguage]}")
        print(f"  Available frameworks: {[fw.value for fw in SupportedFramework]}")
    except Exception as e:
        print(f"✗ Registry imports: FAILED - {e}")
        return False
    
    return True

def check_language_registry():
    """Check language registry functionality."""
    print_section("LANGUAGE REGISTRY CHECK")
    
    try:
        from browse_to_test.output_langs.registry import LanguageRegistry
        registry = LanguageRegistry()
        
        print("✓ LanguageRegistry creation: SUCCESS")
        
        supported_languages = registry.get_supported_languages()
        print(f"✓ Supported languages: {supported_languages}")
        
        if 'typescript' in supported_languages:
            print("✓ TypeScript is listed as supported")
            
            try:
                frameworks = registry.get_frameworks_for_language('typescript')
                print(f"✓ TypeScript frameworks: {frameworks}")
                
                if 'playwright' in frameworks:
                    print("✓ TypeScript + Playwright combination is supported")
                    
                    try:
                        registry.validate_combination('typescript', 'playwright')
                        print("✓ TypeScript + Playwright validation: SUCCESS")
                    except Exception as e:
                        print(f"✗ TypeScript + Playwright validation: FAILED - {e}")
                        return False
                else:
                    print("✗ Playwright not supported for TypeScript")
                    return False
            except Exception as e:
                print(f"✗ Getting TypeScript frameworks: FAILED - {e}")
                return False
        else:
            print("✗ TypeScript not listed as supported")
            return False
            
    except Exception as e:
        print(f"✗ LanguageRegistry check: FAILED - {e}")
        return False
    
    return True

def check_language_manager():
    """Check LanguageManager functionality."""
    print_section("LANGUAGE MANAGER CHECK")
    
    try:
        from browse_to_test.output_langs.manager import LanguageManager
        
        manager = LanguageManager(
            language="typescript",
            framework="playwright"
        )
        
        print("✓ LanguageManager creation: SUCCESS")
        print(f"  Language: {manager.language}")
        print(f"  Framework: {manager.framework}")
        print(f"  Metadata: {manager.metadata}")
        
        return True
        
    except Exception as e:
        print(f"✗ LanguageManager check: FAILED - {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def check_config_builder():
    """Check ConfigBuilder functionality."""
    print_section("CONFIG BUILDER CHECK")
    
    try:
        import browse_to_test as btt
        
        config = btt.ConfigBuilder() \
            .framework("playwright") \
            .ai_provider("openai", model="gpt-4") \
            .language("typescript") \
            .build()
        
        print("✓ ConfigBuilder: SUCCESS")
        print(f"  Language: {config.output.language}")
        print(f"  Framework: {config.output.framework}")
        
        return True
        
    except Exception as e:
        print(f"✗ ConfigBuilder check: FAILED - {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def check_multiprocessing():
    """Check multiprocessing functionality."""
    print_section("MULTIPROCESSING CHECK")
    
    def worker_test():
        """Test function to run in worker process."""
        try:
            from browse_to_test.output_langs.manager import LanguageManager
            
            manager = LanguageManager(
                language="typescript",
                framework="playwright"
            )
            
            return {
                "status": "SUCCESS",
                "language": manager.language,
                "framework": manager.framework,
                "metadata_name": manager.metadata.name
            }
            
        except Exception as e:
            import traceback
            return {
                "status": "ERROR", 
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    try:
        with multiprocessing.Pool(1) as pool:
            result = pool.apply(worker_test)
            
        if result["status"] == "SUCCESS":
            print("✓ Multiprocessing test: SUCCESS")
            print(f"  Worker language: {result['language']}")
            print(f"  Worker framework: {result['framework']}")
            return True
        else:
            print("✗ Multiprocessing test: FAILED")
            print(f"  Error: {result['error']}")
            if 'traceback' in result:
                print(f"  Traceback: {result['traceback']}")
            return False
            
    except Exception as e:
        print(f"✗ Multiprocessing test: FAILED - {e}")
        return False

def check_file_paths():
    """Check if all required files exist."""
    print_section("FILE PATH CHECK")
    
    try:
        import browse_to_test
        base_path = Path(browse_to_test.__file__).parent / "output_langs"
        
        print(f"Base path: {base_path}")
        print(f"Base path exists: {base_path.exists()}")
        
        ts_dir = base_path / "typescript"
        print(f"TypeScript dir: {ts_dir}")
        print(f"TypeScript dir exists: {ts_dir.exists()}")
        
        if ts_dir.exists():
            metadata_file = ts_dir / "metadata.json"
            print(f"Metadata file: {metadata_file}")
            print(f"Metadata file exists: {metadata_file.exists()}")
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                print(f"✓ Metadata content: {metadata}")
            else:
                print("✗ Metadata file missing")
                return False
                
            generators_dir = ts_dir / "generators"
            print(f"Generators dir: {generators_dir}")
            print(f"Generators dir exists: {generators_dir.exists()}")
            
            if generators_dir.exists():
                playwright_gen = generators_dir / "playwright_generator.py"
                print(f"Playwright generator: {playwright_gen}")
                print(f"Playwright generator exists: {playwright_gen.exists()}")
                
                if not playwright_gen.exists():
                    print("✗ Playwright generator missing")
                    return False
            else:
                print("✗ Generators directory missing")
                return False
        else:
            print("✗ TypeScript directory missing")
            return False
            
        print("✓ All required files exist")
        return True
        
    except Exception as e:
        print(f"✗ File path check: FAILED - {e}")
        return False

def run_full_integration_test():
    """Run a full integration test."""
    print_section("FULL INTEGRATION TEST")
    
    try:
        import browse_to_test as btt
        from browse_to_test.output_langs.registry import SupportedLanguage, SupportedFramework
        
        # Create config exactly like the user
        class BttConfig:
            def __init__(
                self,
                framework: SupportedFramework = SupportedFramework.PLAYWRIGHT.value,
                language: SupportedLanguage = SupportedLanguage.TYPESCRIPT.value,
                ai_provider: str = "openai",
                ai_model: str = "gpt-4",
            ):
                self.framework = framework
                self.language = language
                self.ai_provider = ai_provider
                self.ai_model = ai_model

            def build_config(self) -> btt.Config:
                builder = (
                    btt.ConfigBuilder()
                    .framework(self.framework)
                    .ai_provider(self.ai_provider, model=self.ai_model)
                    .language(self.language)
                )
                return builder.build()
        
        print("Creating BttConfig...")
        config_builder = BttConfig()
        
        print("Building config...")
        config = config_builder.build_config()
        
        print("Creating E2eTestConverter...")
        converter = btt.E2eTestConverter(config)
        
        print("✓ Full integration test: SUCCESS")
        print(f"  Final language: {config.output.language}")
        print(f"  Final framework: {config.output.framework}")
        
        return True
        
    except Exception as e:
        print(f"✗ Full integration test: FAILED - {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def provide_recommendations(results: dict):
    """Provide recommendations based on test results."""
    print_section("RECOMMENDATIONS")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("🎉 All tests passed! TypeScript support should be working correctly.")
        print("\nIf you're still experiencing issues, try:")
        print("1. Restart your application/process")
        print("2. Clear any Python caches: python -m py_compile")
        print("3. Reinstall browse-to-test: pip install --force-reinstall browse-to-test")
    else:
        print("❌ Some tests failed. Here are the recommendations:")
        
        if not results.get('basic_imports', False):
            print("\n🔧 BASIC IMPORTS FAILED:")
            print("- Check your Python environment")
            print("- Reinstall browse-to-test: pip install --force-reinstall browse-to-test")
            
        if not results.get('file_paths', False):
            print("\n🔧 FILE PATHS FAILED:")
            print("- Your installation may be corrupted")
            print("- Reinstall browse-to-test: pip install --force-reinstall browse-to-test")
            
        if not results.get('language_registry', False):
            print("\n🔧 LANGUAGE REGISTRY FAILED:")
            print("- This should be fixed by the updated registry with fallback support")
            print("- Make sure you're using the latest version")
            
        if not results.get('multiprocessing', False):
            print("\n🔧 MULTIPROCESSING FAILED:")
            print("- This is likely the source of your original issue")
            print("- The updated registry should handle this better")
            print("- Try using multiprocessing.set_start_method('spawn') before creating pools")

def main():
    """Run all diagnostic tests."""
    print("🔍 browse-to-test TypeScript Support Diagnostic Script")
    print("This script will help diagnose TypeScript support issues.")
    
    results = {}
    
    # Run all tests
    results['basic_imports'] = check_basic_imports()
    results['file_paths'] = check_file_paths()
    results['language_registry'] = check_language_registry()
    results['language_manager'] = check_language_manager()
    results['config_builder'] = check_config_builder()
    results['multiprocessing'] = check_multiprocessing()
    results['full_integration'] = run_full_integration_test()
    
    # Provide recommendations
    provide_recommendations(results)
    
    # Summary
    print_section("SUMMARY")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed. See recommendations above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 