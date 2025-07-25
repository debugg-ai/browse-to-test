#!/usr/bin/env python3

"""
Quick Test Script

A simplified test that verifies core functionality without the complex string escaping.
"""

import sys
import tempfile
import subprocess
import shutil
from pathlib import Path

def test_basic_functionality():
    """Test basic package functionality."""
    print("Testing basic functionality...")
    
    try:
        # Test basic import
        import browse_to_test as btt
        print("✅ Basic import works")
        
        # Test registry
        from browse_to_test.output_langs.registry import SupportedLanguage, LanguageRegistry
        registry = LanguageRegistry()
        languages = registry.get_supported_languages()
        
        if 'typescript' in languages:
            print("✅ TypeScript support detected")
        else:
            print("❌ TypeScript support missing")
            return False
        
        # Test config building
        config = btt.ConfigBuilder().framework("playwright").language("typescript").ai_provider("openai").build()
        print("✅ Config building works")
        
        # Test LanguageManager
        from browse_to_test.output_langs.manager import LanguageManager
        manager = LanguageManager("typescript", "playwright")
        print("✅ LanguageManager creation works")
        
        # Test converter
        converter = btt.E2eTestConverter(config)
        sample_data = [
            {"type": "navigate", "url": "https://example.com"},
            {"type": "click", "selector": "#button"}
        ]
        result = converter.convert(sample_data)
        
        if result and len(result) > 50:
            print("✅ Test conversion works")
        else:
            print("❌ Test conversion failed")
            return False
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_in_clean_environment():
    """Test the package in a clean virtual environment."""
    print("\n" + "="*50)
    print("Testing in clean environment...")
    
    # Find the built package
    dist_dir = Path.cwd() / "dist"
    if not dist_dir.exists():
        print("❌ No dist/ directory found. Run 'python setup.py sdist' first.")
        return False
    
    tar_files = list(dist_dir.glob("*.tar.gz"))
    if not tar_files:
        print("❌ No package files found in dist/")
        return False
    
    package_file = tar_files[-1]
    print(f"Testing package: {package_file.name}")
    
    # Create temporary virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = Path(temp_dir) / "test_venv"
        
        try:
            # Create venv
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, capture_output=True)
            
            # Determine executables
            if sys.platform == 'win32':
                python_exe = venv_dir / "Scripts" / "python.exe"
                pip_exe = venv_dir / "Scripts" / "pip.exe"
            else:
                python_exe = venv_dir / "bin" / "python"
                pip_exe = venv_dir / "bin" / "pip"
            
            # Install package
            subprocess.run([str(pip_exe), "install", str(package_file)], check=True, capture_output=True)
            print("✅ Package installed successfully")
            
            # Create test script file
            test_script = venv_dir / "test_functionality.py"
            test_script.write_text('''
import sys

try:
    import browse_to_test as btt
    print("✅ Basic import successful")
    
    from browse_to_test.output_langs.registry import SupportedLanguage, LanguageRegistry
    registry = LanguageRegistry()
    languages = registry.get_supported_languages()
    
    if "typescript" in languages:
        print("✅ TypeScript support detected")
    else:
        print("❌ TypeScript support missing")
        sys.exit(1)
    
    config = btt.ConfigBuilder().framework("playwright").language("typescript").ai_provider("openai").build()
    print("✅ Config building works")
    
    from browse_to_test.output_langs.manager import LanguageManager
    manager = LanguageManager("typescript", "playwright")
    print("✅ LanguageManager creation works")
    
    print("🎉 All clean environment tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
''')
            
            # Run the test
            result = subprocess.run([str(python_exe), str(test_script)], capture_output=True, text=True)
            print(result.stdout)
            
            if result.stderr:
                print("Stderr:", result.stderr)
            
            if result.returncode == 0:
                print("✅ Clean environment tests passed!")
                return True
            else:
                print("❌ Clean environment tests failed!")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Environment setup failed: {e}")
            return False

def main():
    """Main entry point."""
    print("🧪 Quick Package Test")
    print("="*50)
    
    # Test current environment
    current_success = test_basic_functionality()
    
    # Test clean environment
    clean_success = test_in_clean_environment()
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if current_success and clean_success:
        print("🎉 All tests passed! Package is working correctly.")
        return True
    else:
        print("❌ Some tests failed!")
        if not current_success:
            print("  - Current environment tests failed")
        if not clean_success:
            print("  - Clean environment tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 