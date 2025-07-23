# 🚀 Deployment Guide

This document explains how to set up automatic deployment for the browse-to-test library using GitHub Actions.

## 📋 Prerequisites

### 1. PyPI Account and API Token
1. Create an account on [PyPI](https://pypi.org) if you don't have one
2. Go to Account Settings → API tokens
3. Create a new API token with the scope "Entire account"
4. Copy the token (starts with `pypi-`)

### 2. GitHub Repository Secrets
Add the following secret to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Your PyPI API token from step 1

## 🔄 How the Workflow Works

The deployment workflow (`.github/workflows/deploy.yml`) automatically:

### **On Pull Requests:**
- ✅ Runs tests on Python 3.8-3.12
- ✅ Performs code quality checks (flake8, mypy, bandit)
- ✅ Builds package (dry run) 
- ✅ Validates package structure

### **On Push to Main:**
- ✅ Runs full test suite
- ✅ Auto-increments patch version (e.g., 0.2.0 → 0.2.1)
- ✅ Builds the package
- ✅ Publishes to PyPI
- ✅ Creates GitHub release
- ✅ Commits version bump back to repository

## 📦 Version Management

The workflow automatically manages versioning:

- **Patch version** is auto-incremented for each deployment
- Current version is read from `browse_to_test/__init__.py`
- Version is updated in both `__init__.py` and `setup.py`
- Version bump is committed back to the repository

### Manual Version Updates

For major or minor version bumps, manually update the version in:
```python
# browse_to_test/__init__.py
__version__ = "1.0.0"  # Update this line
```

## 🔧 Workflow Jobs

### 1. **Test Job**
- Runs on matrix of Python versions
- Installs dependencies and runs comprehensive tests
- Uploads coverage reports to Codecov
- Must pass for deployment to proceed

### 2. **Build Job** 
- Only runs on pushes to main
- Increments version automatically
- Builds wheel and source distributions
- Stores artifacts for deployment
- Commits version bump

### 3. **Deploy Job**
- Downloads build artifacts
- Publishes to PyPI using API token
- Creates GitHub release with auto-generated notes
- Only runs after successful test and build

### 4. **Deploy-Test Job**
- Runs on pull requests
- Tests package building without publishing
- Provides early feedback on package structure

## 🚨 Troubleshooting

### Common Issues

#### **"No such secret: PYPI_API_TOKEN"**
- Ensure you've added the PyPI API token to GitHub repository secrets
- Check the secret name matches exactly: `PYPI_API_TOKEN`

#### **"403 Forbidden" during PyPI upload**
- Verify your PyPI API token has correct permissions
- Ensure the package name is available on PyPI
- Check if you're the owner/maintainer of the package

#### **Version conflicts**
- If version already exists on PyPI, the upload will fail
- Manually increment version number to resolve
- Or wait for the auto-increment to handle it

#### **Tests failing**
- All tests must pass before deployment
- Check the Actions tab for detailed error logs
- Fix failing tests and push again

### Manual Deployment

If automatic deployment fails, you can deploy manually:

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check package
twine check dist/*

# Upload to PyPI
twine upload dist/* --verbose
```

## 🔒 Security Features

The workflow includes several security measures:

- **API Token**: Uses PyPI API tokens instead of username/password
- **Secret Management**: Sensitive data stored in GitHub secrets
- **Code Quality**: Automatic linting and security scanning
- **Test Coverage**: Comprehensive testing before deployment
- **Artifact Verification**: Package integrity checks before upload

## 📈 Monitoring

### Viewing Deployments
- Check the **Actions** tab in your GitHub repository
- Each workflow run shows detailed logs
- Failed deployments will show error messages

### PyPI Releases
- View published packages at: `https://pypi.org/project/browse-to-test/`
- Each release includes automatic release notes
- Download statistics available on PyPI

### GitHub Releases
- Automatic releases created with each deployment
- Release notes include commit information
- Tagged versions for easy reference

## ⚙️ Customization

### Modify Version Increment Strategy
Edit the version increment logic in the workflow:
```yaml
# Currently increments patch version (0.2.0 → 0.2.1)
# Modify this section to change strategy
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
```

### Add Additional Quality Checks
Add more steps to the test job:
```yaml
- name: Additional checks
  run: |
    # Add your custom checks here
    pylint browse_to_test
    black --check browse_to_test
```

### Deployment Notifications
Add notification steps to the deploy job:
```yaml
- name: Notify deployment
  run: |
    # Send notifications (Slack, Discord, etc.)
    echo "Deployed version ${{ steps.version.outputs.version }}"
```

## 🎯 Best Practices

1. **Always test locally** before pushing to main
2. **Use pull requests** for code review
3. **Write comprehensive tests** for new features
4. **Update documentation** with breaking changes
5. **Monitor deployment logs** for issues
6. **Keep dependencies updated** in requirements files

## 📞 Support

If you encounter issues with the deployment workflow:

1. Check the GitHub Actions logs for detailed error messages
2. Verify all secrets are properly configured
3. Ensure your PyPI account has the necessary permissions
4. Review this documentation for common solutions

For package-specific issues, refer to the main README.md file. 