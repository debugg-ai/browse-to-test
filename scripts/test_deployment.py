#!/usr/bin/env python3
"""
Test script to verify deployment setup.

This script checks that all deployment dependencies are available
and that the package can be built successfully.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def check_dependencies():
    """Check that all required dependencies are installed."""
    print("\n🧪 Checking Dependencies")
    print("=" * 50)
    
    dependencies = [
        ("python --version", "Python installation"),
        ("pip --version", "Pip installation"),
        ("pytest --version", "Pytest installation"),
        ("flake8 --version", "Flake8 linter"),
        ("mypy --version", "MyPy type checker"),
        ("bandit --version", "Bandit security scanner"),
        ("twine --version", "Twine upload tool"),
        ("python -c 'import build; print(build.__version__)'", "Build tool"),
    ]
    
    all_good = True
    for cmd, desc in dependencies:
        if not run_command(cmd, desc):
            all_good = False
    
    return all_good

def check_package_structure():
    """Check that the package structure is correct."""
    print("\n📦 Checking Package Structure")
    print("=" * 50)
    
    required_files = [
        "browse_to_test/__init__.py",
        "setup.py",
        "requirements.txt",
        "requirements-dev.txt",
        "README.md",
        ".github/workflows/deploy.yml"
    ]
    
    all_good = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - EXISTS")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    return all_good

def check_version_extraction():
    """Check that version can be extracted from __init__.py."""
    print("\n🔢 Checking Version Extraction")
    print("=" * 50)
    
    try:
        with open("browse_to_test/__init__.py", "r") as f:
            content = f.read()
            
        # Extract version like the workflow does
        import re
        version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
        if version_match:
            version = version_match.group(1)
            print(f"✅ Current version: {version}")
            
            # Test version increment logic
            parts = version.split('.')
            if len(parts) == 3:
                major, minor, patch = parts
                new_patch = int(patch) + 1
                new_version = f"{major}.{minor}.{new_patch}"
                print(f"✅ Next version would be: {new_version}")
                return True
            else:
                print(f"❌ Invalid version format: {version}")
                return False
        else:
            print("❌ Could not find version in __init__.py")
            return False
    except Exception as e:
        print(f"❌ Error reading version: {e}")
        return False

def test_package_build():
    """Test building the package."""
    print("\n🏗️ Testing Package Build")
    print("=" * 50)
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning previous builds")
    
    # Build package
    if not run_command("python -m build", "Building package"):
        return False
    
    # Check artifacts
    if not run_command("ls -la dist/", "Listing build artifacts"):
        return False
    
    # Validate package
    if not run_command("twine check dist/*", "Validating package"):
        return False
    
    print("✅ Package build successful!")
    return True

def test_basic_functionality():
    """Test basic package functionality."""
    print("\n⚡ Testing Basic Functionality")
    print("=" * 50)
    
    test_script = '''
import browse_to_test as btt

# Test basic imports
print("✅ Package imports successfully")

# Test configuration
config = btt.ConfigBuilder().framework("playwright").build()
print("✅ ConfigBuilder works")

# Test converter creation
converter = btt.TestConverter(config)
print("✅ TestConverter creation works")

print("✅ All basic functionality tests passed!")
'''
    
    try:
        exec(test_script)
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def run_quick_tests():
    """Run a subset of tests to verify functionality."""
    print("\n🧪 Running Quick Tests")
    print("=" * 50)
    
    # Run just a few key tests
    test_commands = [
        ("python -m pytest tests/test_new_api.py::TestSimplifiedAPI::test_convert_simple_usage -v", 
         "Testing new API"),
        ("python -m pytest tests/test_config_builder.py::TestConfigBuilder::test_basic_builder_creation -v", 
         "Testing config builder"),
        ("flake8 browse_to_test --count --select=E9,F63,F7,F82 --show-source --statistics", 
         "Basic syntax check"),
    ]
    
    all_good = True
    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            all_good = False
    
    return all_good

def main():
    """Main test function."""
    print("🚀 Browse-to-Test Deployment Verification")
    print("=" * 60)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Package Structure", check_package_structure),
        ("Version Extraction", check_version_extraction),
        ("Package Build", test_package_build),
        ("Basic Functionality", test_basic_functionality),
        ("Quick Tests", run_quick_tests),
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Ready for deployment to PyPI")
        print("\n📋 Next Steps:")
        print("1. Commit your changes")
        print("2. Push to main branch") 
        print("3. GitHub Actions will automatically deploy")
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print("🔧 Please fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 