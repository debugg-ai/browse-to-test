#!/usr/bin/env python3

"""
Test Built Package Script

This script installs the locally built package in a clean environment
and runs comprehensive tests against it.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*50}")
    print(f" {text}")
    print(f"{'='*50}{Colors.END}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

class PackageTester:
    """Tests the built package in a clean environment."""
    
    def __init__(self, project_root: Path = None):
        """Initialize the tester."""
        self.project_root = project_root or Path.cwd()
        self.errors: List[str] = []
    
    def find_built_package(self) -> Path:
        """Find the built package file."""
        dist_dir = self.project_root / "dist"
        
        if not dist_dir.exists():
            print_error("No dist/ directory found. Run 'python setup.py sdist' first.")
            sys.exit(1)
        
        tar_files = list(dist_dir.glob("*.tar.gz"))
        wheel_files = list(dist_dir.glob("*.whl"))
        
        # Prefer wheel files if available, otherwise use tar.gz
        if wheel_files:
            return wheel_files[-1]  # Get the latest
        elif tar_files:
            return tar_files[-1]   # Get the latest
        else:
            print_error("No package files found in dist/")
            sys.exit(1)
    
    def create_test_environment(self) -> Path:
        """Create a temporary virtual environment for testing."""
        temp_dir = Path(tempfile.mkdtemp(prefix="btt_test_"))
        venv_dir = temp_dir / "test_venv"
        
        print_info(f"Creating test environment: {venv_dir}")
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_dir)
            ], check=True, capture_output=True)
            
            print_success("Test environment created")
            return venv_dir
            
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to create virtual environment: {e}")
            sys.exit(1)
    
    def install_package(self, venv_dir: Path, package_file: Path) -> tuple:
        """Install the package in the test environment."""
        print_info(f"Installing {package_file.name}...")
        
        # Determine the python and pip executables
        if os.name == 'nt':  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"
        
        try:
            # Upgrade pip first
            subprocess.run([
                str(pip_exe), "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install the package
            subprocess.run([
                str(pip_exe), "install", str(package_file)
            ], check=True, capture_output=True)
            
            print_success(f"Package {package_file.name} installed successfully")
            return python_exe, pip_exe
            
        except subprocess.CalledProcessError as e:
            print_error(f"Package installation failed: {e}")
            sys.exit(1)
    
    def run_import_tests(self, python_exe: Path) -> bool:
        """Run import and basic functionality tests."""
        print_header("Import Tests")
        
        test_script = '''
import sys
import traceback

def test_basic_import():
    """Test basic package import."""
    try:
        import browse_to_test as btt
        print("✅ Basic import successful")
        print(f"   Version: {getattr(btt, '__version__', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Basic import failed: {e}")
        traceback.print_exc()
        return False

def test_registry_import():
    """Test registry and language support."""
    try:
        from browse_to_test.output_langs.registry import SupportedLanguage, SupportedFramework, LanguageRegistry
        
        registry = LanguageRegistry()
        languages = registry.get_supported_languages()
        frameworks = registry.get_supported_frameworks()
        
        print(f"✅ Registry import successful")
        print(f"   Languages: {languages}")
        print(f"   Frameworks: {frameworks}")
        
        # Test TypeScript specifically
        if 'typescript' in languages:
            print("✅ TypeScript support detected")
        else:
            print("❌ TypeScript support missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Registry import failed: {e}")
        traceback.print_exc()
        return False

def test_config_building():
    """Test configuration building."""
    try:
        import browse_to_test as btt
        
        config = btt.ConfigBuilder()\\
            .framework("playwright")\\
            .language("typescript")\\
            .ai_provider("openai", model="gpt-4")\\
            .build()
        
        print("✅ Config building successful")
        print(f"   Language: {config.output.language}")
        print(f"   Framework: {config.output.framework}")
        return True
        
    except Exception as e:
        print(f"❌ Config building failed: {e}")
        traceback.print_exc()
        return False

def test_language_manager():
    """Test LanguageManager creation."""
    try:
        from browse_to_test.output_langs.manager import LanguageManager
        
        # Test with TypeScript
        manager = LanguageManager("typescript", "playwright")
        print("✅ LanguageManager (TypeScript) creation successful")
        print(f"   Language: {manager.language}")
        print(f"   Framework: {manager.framework}")
        print(f"   Metadata: {manager.metadata.name}")
        
        # Test with Python
        manager_py = LanguageManager("python", "playwright")
        print("✅ LanguageManager (Python) creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ LanguageManager creation failed: {e}")
        traceback.print_exc()
        return False

def test_converter():
    """Test E2eTestConverter."""
    try:
        import browse_to_test as btt
        
        config = btt.ConfigBuilder()\\
            .framework("playwright")\\
            .language("typescript")\\
            .ai_provider("openai", model="gpt-4")\\
            .build()
        
        converter = btt.E2eTestConverter(config)
        print("✅ E2eTestConverter creation successful")
        
        # Test basic conversion
        sample_data = [
            {"type": "navigate", "url": "https://example.com"},
            {"type": "click", "selector": "#button"}
        ]
        
        result = converter.convert(sample_data)
        if result and len(result) > 50:  # Basic sanity check
            print("✅ Test conversion successful")
            print(f"   Generated {len(result)} characters")
            return True
        else:
            print("❌ Test conversion failed - empty or too short result")
            return False
        
    except Exception as e:
        print(f"❌ E2eTestConverter test failed: {e}")
        traceback.print_exc()
        return False

def test_file_access():
    """Test that package files are accessible."""
    try:
        import browse_to_test.output_langs.manager
        
        # Try to create a manager (this will test file access)
        manager = browse_to_test.output_langs.manager.LanguageManager("typescript", "playwright")
        
        # Check that we can access metadata
        metadata = manager.metadata
        if metadata and metadata.name == "typescript":
            print("✅ File access test successful")
            print(f"   TypeScript metadata loaded: {metadata.display_name}")
            return True
        else:
            print("❌ File access test failed - could not load metadata")
            return False
            
    except Exception as e:
        print(f"❌ File access test failed: {e}")
        traceback.print_exc()
        return False

# Run all tests
tests = [
    ("Basic Import", test_basic_import),
    ("Registry Import", test_registry_import),
    ("Config Building", test_config_building),
    ("LanguageManager", test_language_manager),
    ("Converter", test_converter),
    ("File Access", test_file_access),
]

print("Running package tests...")
print("=" * 50)

results = {}
for test_name, test_func in tests:
    print(f"\n--- {test_name} ---")
    try:
        results[test_name] = test_func()
    except Exception as e:
        print(f"❌ Test '{test_name}' crashed: {e}")
        traceback.print_exc()
        results[test_name] = False

# Summary
print("\n" + "=" * 50)
print("TEST SUMMARY")
print("=" * 50)

passed = sum(1 for result in results.values() if result)
total = len(results)

for test_name, result in results.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} {test_name}")

print(f"\nResults: {passed}/{total} tests passed")

if passed == total:
    print("\n🎉 All tests passed!")
    sys.exit(0)
else:
    print(f"\n❌ {total - passed} tests failed!")
    sys.exit(1)
'''
        
        try:
            result = subprocess.run([
                str(python_exe), "-c", test_script
            ], capture_output=True, text=True, cwd=self.project_root)
            
            print(result.stdout)
            if result.stderr:
                print(f"{Colors.YELLOW}Stderr:{Colors.END}")
                print(result.stderr)
            
            if result.returncode == 0:
                print_success("All import tests passed!")
                return True
            else:
                print_error("Some import tests failed!")
                self.errors.append("Import tests failed")
                return False
                
        except Exception as e:
            print_error(f"Failed to run import tests: {e}")
            self.errors.append(f"Import test execution failed: {e}")
            return False
    
    def run_integration_tests(self, python_exe: Path) -> bool:
        """Run integration tests using pytest if available."""
        print_header("Integration Tests")
        
        # Check if we have tests directory
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            print_info("No tests directory found, skipping integration tests")
            return True
        
        try:
            # Try to install pytest in the test environment
            pip_exe = python_exe.parent / ("pip.exe" if os.name == 'nt' else "pip")
            
            print_info("Installing pytest...")
            subprocess.run([
                str(pip_exe), "install", "pytest", "pytest-asyncio"
            ], check=True, capture_output=True)
            
            print_info("Running integration tests...")
            result = subprocess.run([
                str(python_exe), "-m", "pytest", str(tests_dir), "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            print(result.stdout)
            if result.stderr:
                print(f"{Colors.YELLOW}Stderr:{Colors.END}")
                print(result.stderr)
            
            if result.returncode == 0:
                print_success("Integration tests passed!")
                return True
            else:
                print_error("Some integration tests failed!")
                return False
                
        except subprocess.CalledProcessError as e:
            print_error(f"Integration tests failed: {e}")
            return False
        except Exception as e:
            print_info(f"Could not run integration tests: {e}")
            return True  # Don't fail the whole process if pytest is not available
    
    def cleanup_environment(self, venv_dir: Path):
        """Clean up the test environment."""
        try:
            print_info(f"Cleaning up test environment: {venv_dir.parent}")
            shutil.rmtree(venv_dir.parent)
            print_success("Test environment cleaned up")
        except Exception as e:
            print_error(f"Failed to clean up test environment: {e}")
    
    def run_tests(self, keep_env: bool = False) -> bool:
        """Run all tests against the built package."""
        print_header("Testing Built Package")
        
        # Find the package
        package_file = self.find_built_package()
        print_info(f"Testing package: {package_file}")
        
        # Create test environment
        venv_dir = self.create_test_environment()
        
        try:
            # Install package
            python_exe, pip_exe = self.install_package(venv_dir, package_file)
            
            # Run tests
            import_success = self.run_import_tests(python_exe)
            integration_success = self.run_integration_tests(python_exe)
            
            # Summary
            print_header("Test Summary")
            
            if import_success and integration_success:
                print_success("🎉 All tests passed! Package is working correctly.")
                return True
            else:
                print_error("❌ Some tests failed!")
                for error in self.errors:
                    print_error(f"  - {error}")
                return False
                
        finally:
            if not keep_env:
                self.cleanup_environment(venv_dir)
            else:
                print_info(f"Test environment preserved at: {venv_dir}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test browse-to-test built package")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--keep-env", action="store_true", help="Keep test environment after testing")
    
    args = parser.parse_args()
    
    tester = PackageTester(args.project_root)
    success = tester.run_tests(keep_env=args.keep_env)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 