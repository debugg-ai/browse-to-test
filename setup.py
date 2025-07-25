#!/usr/bin/env python3
"""
Setup script for browse-to-test library.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
def get_version():
    """Extract version from __init__.py"""
    init_file = this_directory / "browse_to_test" / "__init__.py"
    for line in init_file.read_text().splitlines():
        if line.startswith("__version__"):
            return line.split('"')[1]
    raise RuntimeError("Unable to find version string in __init__.py")

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req for req in requirements if req and not req.startswith('#')]

setup(
    name="browse-to-test",
    version=get_version(),
    author="Browse-to-Test Contributors", 
    author_email="",
    description="AI-powered browser automation to test script converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/browse-to-test",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.7.0"],
        "azure": ["openai>=1.0.0"],  # Azure uses OpenAI SDK
        "playwright": ["playwright>=1.30.0"],
        "selenium": ["selenium>=4.0.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.7.0", 
            "playwright>=1.30.0",
            "selenium>=4.0.0",
            "PyYAML>=5.4.0",  # For YAML config support
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "browse-to-test=browse_to_test.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "browse_to_test.output_langs.common": ["*.json"],
        "browse_to_test.output_langs.python": ["metadata.json"],
        "browse_to_test.output_langs.python.templates": ["*.txt"],
        "browse_to_test.output_langs.typescript": ["metadata.json"],
        "browse_to_test.output_langs.typescript.templates": ["*.txt"],
        "browse_to_test.output_langs.javascript": ["metadata.json"],
        "browse_to_test.output_langs.javascript.templates": ["*.txt"],
        "browse_to_test.core.configuration.templates": ["*.txt", "*.py", "*.js", "*.ts"],
        "browse_to_test": [
            "output_langs/common/*.json",
            "output_langs/*/metadata.json",
            "output_langs/*/templates/*.txt",
            "output_langs/*/templates/*.py",
            "output_langs/*/templates/*.js", 
            "output_langs/*/templates/*.ts",
            "core/*/templates/*.txt",
            "core/*/templates/*.py",
            "core/*/templates/*.js",
            "core/*/templates/*.ts",
        ],
    },
    keywords=[
        "test automation",
        "browser testing", 
        "playwright",
        "selenium",
        "ai",
        "code generation",
        "testing",
        "qa",
        "end-to-end testing",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/browse-to-test/issues",
        "Source": "https://github.com/yourusername/browse-to-test",
        "Documentation": "https://browse-to-test.readthedocs.io/",
    },
) 