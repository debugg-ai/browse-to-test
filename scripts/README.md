# Package Validation Scripts

This directory contains comprehensive validation scripts to ensure the browse-to-test package is correctly configured and ready for release.

## 🛠️ Available Scripts

### 1. `validate_package.py` - Comprehensive Package Validation

The main validation script that performs complete package validation including:

- ✅ File structure validation
- ✅ JSON syntax validation  
- ✅ setup.py configuration check
- ✅ MANIFEST.in validation
- ✅ Package build test
- ✅ Clean environment installation test

**Usage:**
```bash
# Run full validation
python scripts/validate_package.py

# Skip the clean install test (faster)
python scripts/validate_package.py --skip-install-test
```

### 2. `test_built_package.py` - Built Package Testing

Tests the locally built package in a clean virtual environment to ensure it works correctly after installation.

**Usage:**
```bash
# Build package first
python setup.py sdist bdist_wheel

# Test the built package
python scripts/test_built_package.py

# Keep the test environment for debugging
python scripts/test_built_package.py --keep-env
```

### 3. `pre_commit_check.py` - Quick Pre-commit Validation

Lightweight validation for pre-commit hooks that checks:

- ✅ Critical files exist
- ✅ JSON syntax is valid
- ✅ Package configuration is present
- ✅ Version consistency

**Usage:**
```bash
# Quick pre-commit check
python scripts/pre_commit_check.py
```

## 🚀 Recommended Workflow

### Before Committing Changes

```bash
# Quick validation
python scripts/pre_commit_check.py
```

### Before Pushing to GitHub

```bash
# Full validation
python scripts/validate_package.py
```

### Before Creating a Release

```bash
# Complete validation workflow
python scripts/validate_package.py
python scripts/test_built_package.py
```

## 🔧 Setting Up Pre-commit Hooks

To automatically run validation before commits, add this to your `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python scripts/pre_commit_check.py
exit $?
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## 📋 All-in-One Validation Script

For convenience, you can run all validations with:

```bash
# Create a simple validation runner
cat > validate_all.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Running pre-commit checks..."
python scripts/pre_commit_check.py

echo "🔍 Running full package validation..."
python scripts/validate_package.py

echo "🔍 Testing built package..."
python scripts/test_built_package.py

echo "🎉 All validations passed!"
EOF

chmod +x validate_all.sh
./validate_all.sh
```

## 🤖 CI/CD Integration

The validation scripts are designed to work in CI/CD environments:

### GitHub Actions

The `.github/workflows/package_validation.yml` workflow automatically runs:

1. **Pre-commit checks** on every push/PR
2. **Full package validation** across multiple Python versions
3. **Built package testing** to ensure installation works
4. **Security scanning** with bandit and safety

### Local CI Testing

To test the CI workflow locally:

```bash
# Simulate the CI environment
python -m venv ci_test_env
source ci_test_env/bin/activate  # or ci_test_env\Scripts\activate on Windows

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt

python scripts/pre_commit_check.py
python scripts/validate_package.py
python scripts/test_built_package.py

deactivate
rm -rf ci_test_env
```

## 🛟 Troubleshooting

### Common Issues

1. **"No dist/ directory found"**
   ```bash
   # Build the package first
   python setup.py sdist bdist_wheel
   ```

2. **"Virtual environment creation failed"**
   ```bash
   # Make sure venv module is available
   python -m pip install --upgrade pip setuptools
   ```

3. **"JSON syntax errors"**
   ```bash
   # Check JSON files manually
   python -m json.tool browse_to_test/output_langs/common/constants.json
   ```

4. **"Import tests failed"**
   ```bash
   # Check that all required files are in MANIFEST.in
   python setup.py check
   ```

### Debug Mode

For detailed debugging information:

```bash
# Run with verbose output (if script supports it)
python scripts/validate_package.py --verbose

# Or check specific components
python -c "
from browse_to_test.output_langs.registry import LanguageRegistry
registry = LanguageRegistry()
print('Supported languages:', registry.get_supported_languages())
"
```

## 📊 What Gets Validated

### File Structure
- All critical JSON configuration files
- Language metadata files  
- Template files for each language
- Packaging configuration files

### Package Configuration
- `setup.py` includes all necessary `package_data`
- `MANIFEST.in` includes all non-Python files
- Version consistency across files

### Functionality
- Basic imports work
- TypeScript support is available
- LanguageManager can be created
- Configuration building works
- Test conversion succeeds

### Installation
- Package builds without errors
- Package installs cleanly
- All files are accessible after installation
- Core functionality works in clean environment

## 🎯 Success Criteria

All scripts should exit with code 0 and show:
- ✅ All file checks pass
- ✅ All JSON files are valid
- ✅ Package builds successfully  
- ✅ Package installs and imports work
- ✅ TypeScript support is functional

If any check fails, the script will:
- ❌ Exit with non-zero code
- 🔍 Show detailed error messages
- 💡 Provide troubleshooting hints 