#!/usr/bin/env python3

"""
Comprehensive Package Validation Script

This script validates that the browse-to-test package is correctly configured
and contains all necessary files before release.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
import glob
from pathlib import Path
from typing import List, Dict, Set, Tuple
import importlib.util

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str, color: str = Colors.CYAN):
    """Print a formatted header."""
    print(f"\n{color}{Colors.BOLD}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.END}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

class PackageValidator:
    """Validates the package configuration and contents."""
    
    def __init__(self, project_root: Path = None):
        """Initialize the validator."""
        self.project_root = project_root or Path.cwd()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Critical files that must be present
        self.critical_files = [
            "browse_to_test/output_langs/common/constants.json",
            "browse_to_test/output_langs/common/messages.json", 
            "browse_to_test/output_langs/common/patterns.json",
            "browse_to_test/output_langs/python/metadata.json",
            "browse_to_test/output_langs/typescript/metadata.json",
            "browse_to_test/output_langs/javascript/metadata.json",
            "browse_to_test/output_langs/python/templates/base_imports.txt",
            "browse_to_test/output_langs/python/templates/exception_classes.txt",
            "browse_to_test/output_langs/python/templates/utility_functions.txt",
            "browse_to_test/output_langs/typescript/templates/base_imports.txt",
            "browse_to_test/output_langs/typescript/templates/exception_classes.txt",
            "browse_to_test/output_langs/typescript/templates/utility_functions.txt",
        ]
        
        # Packaging files
        self.packaging_files = [
            "setup.py",
            "MANIFEST.in", 
            "README.md",
            "requirements.txt",
        ]

    def validate_file_structure(self) -> bool:
        """Validate that all critical files exist."""
        print_header("File Structure Validation")
        
        missing_files = []
        
        print_info("Checking critical package files...")
        for file_path in self.critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print_success(f"{file_path}")
            else:
                print_error(f"{file_path} - MISSING!")
                missing_files.append(file_path)
        
        print_info("Checking packaging files...")
        for file_path in self.packaging_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print_success(f"{file_path}")
            else:
                print_error(f"{file_path} - MISSING!")
                missing_files.append(file_path)
        
        if missing_files:
            self.errors.extend([f"Missing file: {f}" for f in missing_files])
            return False
        
        print_success(f"All {len(self.critical_files + self.packaging_files)} required files present")
        return True

    def validate_json_files(self) -> bool:
        """Validate that JSON files are properly formatted."""
        print_header("JSON File Validation")
        
        json_files = list(self.project_root.glob("browse_to_test/output_langs/**/*.json"))
        invalid_files = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
                print_success(f"{json_file.relative_to(self.project_root)}")
            except json.JSONDecodeError as e:
                print_error(f"{json_file.relative_to(self.project_root)} - Invalid JSON: {e}")
                invalid_files.append(str(json_file.relative_to(self.project_root)))
        
        if invalid_files:
            self.errors.extend([f"Invalid JSON: {f}" for f in invalid_files])
            return False
        
        print_success(f"All {len(json_files)} JSON files are valid")
        return True

    def validate_setup_py(self) -> bool:
        """Validate setup.py configuration."""
        print_header("setup.py Validation")
        
        setup_py = self.project_root / "setup.py"
        if not setup_py.exists():
            self.errors.append("setup.py not found")
            return False
        
        try:
            # Check that setup.py can be imported/executed
            spec = importlib.util.spec_from_file_location("setup", setup_py)
            setup_module = importlib.util.module_from_spec(spec)
            
            # Read the file content to check package_data
            setup_content = setup_py.read_text()
            
            # Check for important configurations
            checks = [
                ("include_package_data=True", "include_package_data is enabled"),
                ("package_data=", "package_data is configured"),
                ("*.json", "JSON files are included in package_data"),
                ("*.txt", "Template files are included in package_data"),
                ("output_langs", "output_langs directory is included"),
            ]
            
            for check_str, description in checks:
                if check_str in setup_content:
                    print_success(description)
                else:
                    print_error(f"Missing: {description}")
                    self.errors.append(f"setup.py missing: {description}")
            
            print_success("setup.py configuration validated")
            return True
            
        except Exception as e:
            print_error(f"setup.py validation failed: {e}")
            self.errors.append(f"setup.py error: {e}")
            return False

    def validate_manifest_in(self) -> bool:
        """Validate MANIFEST.in configuration."""
        print_header("MANIFEST.in Validation")
        
        manifest_file = self.project_root / "MANIFEST.in"
        if not manifest_file.exists():
            self.errors.append("MANIFEST.in not found")
            return False
        
        manifest_content = manifest_file.read_text()
        
        # Check for important inclusions
        required_patterns = [
            "browse_to_test/output_langs/common *.json",
            "browse_to_test/output_langs *.json", 
            "browse_to_test/output_langs/*/templates *.txt",
        ]
        
        for pattern in required_patterns:
            if pattern in manifest_content:
                print_success(f"Pattern included: {pattern}")
            else:
                print_warning(f"Pattern missing: {pattern}")
                self.warnings.append(f"MANIFEST.in missing pattern: {pattern}")
        
        print_success("MANIFEST.in validated")
        return True

    def build_and_test_package(self) -> bool:
        """Build the package and verify contents."""
        print_header("Package Build Test")
        
        # Clean previous builds
        for build_dir in ["build", "dist", "*.egg-info"]:
            for path in self.project_root.glob(build_dir):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        
        print_info("Building source distribution...")
        try:
            result = subprocess.run([
                sys.executable, "setup.py", "sdist"
            ], cwd=self.project_root, capture_output=True, text=True, check=True)
            
            print_success("Package built successfully")
            
        except subprocess.CalledProcessError as e:
            print_error(f"Package build failed: {e}")
            print_error(f"stdout: {e.stdout}")
            print_error(f"stderr: {e.stderr}")
            self.errors.append(f"Package build failed: {e}")
            return False
        
        # Find the built package
        dist_dir = self.project_root / "dist"
        tar_files = list(dist_dir.glob("*.tar.gz"))
        
        if not tar_files:
            print_error("No distribution file found")
            self.errors.append("No distribution file created")
            return False
        
        tar_file = tar_files[0]
        print_info(f"Checking contents of {tar_file.name}...")
        
        # Check package contents
        try:
            result = subprocess.run([
                "tar", "-tzf", str(tar_file)
            ], capture_output=True, text=True, check=True)
            
            package_contents = result.stdout.strip().split('\n')
            
            # Verify critical files are in the package
            missing_in_package = []
            for critical_file in self.critical_files:
                expected_path = f"browse_to_test-*/browse_to_test/{critical_file.split('/', 1)[1]}"
                found = any(path.endswith(critical_file.split('/', 1)[1]) for path in package_contents)
                
                if found:
                    print_success(f"Package contains: {critical_file}")
                else:
                    print_error(f"Package missing: {critical_file}")
                    missing_in_package.append(critical_file)
            
            if missing_in_package:
                self.errors.extend([f"Package missing: {f}" for f in missing_in_package])
                return False
            
            print_success(f"Package contains all {len(self.critical_files)} critical files")
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to inspect package: {e}")
            self.errors.append(f"Package inspection failed: {e}")
            return False

    def test_import_after_install(self) -> bool:
        """Test that the package can be imported after installation."""
        print_header("Import Test (Clean Environment)")
        
        # Create a temporary virtual environment
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_dir = Path(temp_dir) / "test_venv"
            
            print_info("Creating temporary virtual environment...")
            try:
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_dir)
                ], check=True, capture_output=True)
                
                # Determine the python executable in the venv
                if os.name == 'nt':  # Windows
                    python_exe = venv_dir / "Scripts" / "python.exe"
                    pip_exe = venv_dir / "Scripts" / "pip.exe"
                else:  # Unix/Linux/macOS
                    python_exe = venv_dir / "bin" / "python"
                    pip_exe = venv_dir / "bin" / "pip"
                
                print_success("Virtual environment created")
                
                # Install the package from the built distribution
                dist_dir = self.project_root / "dist"
                tar_files = list(dist_dir.glob("*.tar.gz"))
                if not tar_files:
                    print_error("No distribution file to install")
                    return False
                
                tar_file = tar_files[0]
                print_info(f"Installing {tar_file.name} in clean environment...")
                
                subprocess.run([
                    str(pip_exe), "install", str(tar_file)
                ], check=True, capture_output=True)
                
                print_success("Package installed successfully")
                
                # Test import and basic functionality
                test_script = '''
import sys
import json
from pathlib import Path

# Test basic import
try:
    import browse_to_test as btt
    print("✅ Basic import successful")
except Exception as e:
    print(f"❌ Basic import failed: {e}")
    sys.exit(1)

# Test registry import and TypeScript support
try:
    from browse_to_test.output_langs.registry import SupportedLanguage, SupportedFramework, LanguageRegistry
    
    registry = LanguageRegistry()
    languages = registry.get_supported_languages()
    
    if 'typescript' in languages:
        print("✅ TypeScript support detected")
    else:
        print("❌ TypeScript support missing")
        sys.exit(1)
        
    # Test config building
    config = btt.ConfigBuilder().framework("playwright").language("typescript").ai_provider("openai").build()
    print("✅ Config building works")
    
    # Test that critical files are accessible
    import browse_to_test.output_langs.manager
    manager = browse_to_test.output_langs.manager.LanguageManager("typescript", "playwright")
    print("✅ LanguageManager creation works")
    
    print("✅ All import tests passed")
    
except Exception as e:
    print(f"❌ Import test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
                
                result = subprocess.run([
                    str(python_exe), "-c", test_script
                ], capture_output=True, text=True)
                
                print(result.stdout)
                if result.stderr:
                    print_warning(f"Stderr: {result.stderr}")
                
                if result.returncode == 0:
                    print_success("All import tests passed")
                    return True
                else:
                    print_error("Import tests failed")
                    self.errors.append("Import tests failed in clean environment")
                    return False
                    
            except subprocess.CalledProcessError as e:
                print_error(f"Virtual environment test failed: {e}")
                self.errors.append(f"Virtual environment test failed: {e}")
                return False

    def run_validation(self) -> bool:
        """Run all validation checks."""
        print_header("Package Validation Starting", Colors.MAGENTA)
        print_info(f"Project root: {self.project_root}")
        
        validations = [
            ("File Structure", self.validate_file_structure),
            ("JSON Files", self.validate_json_files),
            ("setup.py", self.validate_setup_py),
            ("MANIFEST.in", self.validate_manifest_in),
            ("Package Build", self.build_and_test_package),
            ("Clean Import Test", self.test_import_after_install),
        ]
        
        results = {}
        for name, validation_func in validations:
            try:
                results[name] = validation_func()
            except Exception as e:
                print_error(f"Validation '{name}' crashed: {e}")
                results[name] = False
                self.errors.append(f"Validation '{name}' crashed: {e}")
        
        # Summary
        print_header("Validation Summary", Colors.MAGENTA)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for name, result in results.items():
            if result:
                print_success(f"{name}")
            else:
                print_error(f"{name}")
        
        print(f"\n{Colors.BOLD}Results: {passed}/{total} validations passed{Colors.END}")
        
        if self.warnings:
            print_warning(f"{len(self.warnings)} warnings:")
            for warning in self.warnings:
                print_warning(f"  - {warning}")
        
        if self.errors:
            print_error(f"{len(self.errors)} errors:")
            for error in self.errors:
                print_error(f"  - {error}")
            return False
        
        print_success("🎉 All validations passed! Package is ready for release.")
        return True

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate browse-to-test package")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--skip-install-test", action="store_true", help="Skip clean install test")
    
    args = parser.parse_args()
    
    validator = PackageValidator(args.project_root)
    
    if args.skip_install_test:
        # Monkey patch to skip the install test
        validator.test_import_after_install = lambda: True
    
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 