"""
CI/CD Integration and Test Maintenance System

This module provides comprehensive CI/CD integration capabilities including
test reporting, maintenance tools, and integration with popular CI platforms.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import subprocess


class CIPlatform(Enum):
    """Supported CI/CD platforms."""
    GITHUB_ACTIONS = "github_actions"
    JENKINS = "jenkins"
    GITLAB_CI = "gitlab_ci"
    AZURE_DEVOPS = "azure_devops"
    CIRCLECI = "circleci"
    TRAVIS_CI = "travis_ci"
    BAMBOO = "bamboo"


class ReportFormat(Enum):
    """Test report formats."""
    JUNIT = "junit"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    CUCUMBER = "cucumber"
    ALLURE = "allure"
    MOCHAWESOME = "mochawesome"


class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"
    RETRIED = "retried"
    FLAKY = "flaky"


class MaintenanceAction(Enum):
    """Test maintenance actions."""
    UPDATE_SELECTORS = "update_selectors"
    FIX_ASSERTIONS = "fix_assertions"
    REMOVE_OBSOLETE = "remove_obsolete"
    OPTIMIZE_WAITS = "optimize_waits"
    UPDATE_DATA = "update_data"
    REFRESH_SCREENSHOTS = "refresh_screenshots"


@dataclass
class TestResult:
    """Individual test result data."""
    test_name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshot_path: Optional[str] = None
    retry_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Test suite results."""
    name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    tests: List[TestResult] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)


@dataclass
class TestReport:
    """Complete test execution report."""
    timestamp: datetime
    total_duration: float
    suites: List[TestSuite] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    flaky_tests: List[str] = field(default_factory=list)
    
    @property
    def total_tests(self) -> int:
        return sum(suite.total_tests for suite in self.suites)
    
    @property
    def total_passed(self) -> int:
        return sum(suite.passed for suite in self.suites)
    
    @property
    def total_failed(self) -> int:
        return sum(suite.failed for suite in self.suites)
    
    @property
    def total_skipped(self) -> int:
        return sum(suite.skipped for suite in self.suites)
    
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.total_passed / self.total_tests) * 100


@dataclass
class CIConfig:
    """CI/CD configuration."""
    platform: CIPlatform
    report_formats: List[ReportFormat] = field(default_factory=lambda: [ReportFormat.JUNIT])
    enable_screenshots: bool = True
    enable_video_recording: bool = False
    parallel_jobs: int = 1
    retry_failed_tests: bool = True
    max_retries: int = 2
    artifact_retention_days: int = 30
    notify_on_failure: bool = True
    enable_test_analytics: bool = True
    enable_maintenance_suggestions: bool = True


@dataclass
class MaintenanceIssue:
    """Test maintenance issue detection."""
    issue_type: MaintenanceAction
    test_file: str
    line_number: int
    description: str
    severity: str
    suggested_fix: str
    auto_fixable: bool = False


class TestReportGenerator:
    """Generates test reports in various formats."""
    
    def __init__(self, config: CIConfig):
        self.config = config
        
    def generate_reports(self, test_report: TestReport, output_dir: Path) -> Dict[ReportFormat, str]:
        """Generate reports in all configured formats."""
        generated_reports = {}
        
        for report_format in self.config.report_formats:
            if report_format == ReportFormat.JUNIT:
                path = self._generate_junit_report(test_report, output_dir)
                generated_reports[report_format] = path
            elif report_format == ReportFormat.JSON:
                path = self._generate_json_report(test_report, output_dir)
                generated_reports[report_format] = path
            elif report_format == ReportFormat.HTML:
                path = self._generate_html_report(test_report, output_dir)
                generated_reports[report_format] = path
            elif report_format == ReportFormat.MARKDOWN:
                path = self._generate_markdown_report(test_report, output_dir)
                generated_reports[report_format] = path
        
        return generated_reports
    
    def _generate_junit_report(self, test_report: TestReport, output_dir: Path) -> str:
        """Generate JUnit XML report."""
        root = ET.Element("testsuites")
        root.set("tests", str(test_report.total_tests))
        root.set("failures", str(test_report.total_failed))
        root.set("time", str(test_report.total_duration))
        root.set("timestamp", test_report.timestamp.isoformat())
        
        for suite in test_report.suites:
            suite_elem = ET.SubElement(root, "testsuite")
            suite_elem.set("name", suite.name)
            suite_elem.set("tests", str(suite.total_tests))
            suite_elem.set("failures", str(suite.failed))
            suite_elem.set("skipped", str(suite.skipped))
            suite_elem.set("time", str(suite.duration))
            
            for test in suite.tests:
                test_elem = ET.SubElement(suite_elem, "testcase")
                test_elem.set("name", test.test_name)
                test_elem.set("time", str(test.duration))
                
                if test.status == TestStatus.FAILED:
                    failure_elem = ET.SubElement(test_elem, "failure")
                    failure_elem.set("message", test.error_message or "Test failed")
                    failure_elem.text = test.stack_trace or ""
                elif test.status == TestStatus.SKIPPED:
                    ET.SubElement(test_elem, "skipped")
        
        output_file = output_dir / "junit-report.xml"
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        return str(output_file)
    
    def _generate_json_report(self, test_report: TestReport, output_dir: Path) -> str:
        """Generate JSON report."""
        report_data = {
            "timestamp": test_report.timestamp.isoformat(),
            "duration": test_report.total_duration,
            "summary": {
                "total": test_report.total_tests,
                "passed": test_report.total_passed,
                "failed": test_report.total_failed,
                "skipped": test_report.total_skipped,
                "success_rate": test_report.success_rate
            },
            "environment": test_report.environment,
            "suites": []
        }
        
        for suite in test_report.suites:
            suite_data = {
                "name": suite.name,
                "duration": suite.duration,
                "summary": {
                    "total": suite.total_tests,
                    "passed": suite.passed,
                    "failed": suite.failed,
                    "skipped": suite.skipped
                },
                "tests": [
                    {
                        "name": test.test_name,
                        "status": test.status.value,
                        "duration": test.duration,
                        "error": test.error_message,
                        "retry_count": test.retry_count,
                        "tags": test.tags
                    }
                    for test in suite.tests
                ]
            }
            report_data["suites"].append(suite_data)
        
        output_file = output_dir / "test-report.json"
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        return str(output_file)
    
    def _generate_html_report(self, test_report: TestReport, output_dir: Path) -> str:
        """Generate HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {test_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .success {{ color: #28a745; }}
        .failure {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; }}
        .suite-header {{ background-color: #e9ecef; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Test Execution Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Timestamp:</strong> {test_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {test_report.total_duration:.2f}s</p>
        <p><strong>Total Tests:</strong> {test_report.total_tests}</p>
        <p><strong class="success">Passed:</strong> {test_report.total_passed}</p>
        <p><strong class="failure">Failed:</strong> {test_report.total_failed}</p>
        <p><strong class="skipped">Skipped:</strong> {test_report.total_skipped}</p>
        <p><strong>Success Rate:</strong> {test_report.success_rate:.1f}%</p>
    </div>
    
    <h2>Test Details</h2>
    <table>
        <thead>
            <tr>
                <th>Suite</th>
                <th>Test</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for suite in test_report.suites:
            for i, test in enumerate(suite.tests):
                suite_name = suite.name if i == 0 else ""
                status_class = test.status.value
                error_msg = test.error_message[:100] + "..." if test.error_message and len(test.error_message) > 100 else (test.error_message or "")
                
                html_content += f"""
            <tr>
                <td>{suite_name}</td>
                <td>{test.test_name}</td>
                <td><span class="{status_class}">{test.status.value.upper()}</span></td>
                <td>{test.duration:.2f}s</td>
                <td>{error_msg}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
</body>
</html>
        """
        
        output_file = output_dir / "test-report.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        return str(output_file)
    
    def _generate_markdown_report(self, test_report: TestReport, output_dir: Path) -> str:
        """Generate Markdown report."""
        markdown_content = f"""# Test Execution Report

**Timestamp:** {test_report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {test_report.total_duration:.2f}s  
**Success Rate:** {test_report.success_rate:.1f}%

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {test_report.total_tests} |
| ✅ Passed | {test_report.total_passed} |
| ❌ Failed | {test_report.total_failed} |
| ⏭️ Skipped | {test_report.total_skipped} |

## Test Results by Suite

"""
        
        for suite in test_report.suites:
            markdown_content += f"""### {suite.name}

**Duration:** {suite.duration:.2f}s  
**Tests:** {suite.total_tests} | **Passed:** {suite.passed} | **Failed:** {suite.failed} | **Skipped:** {suite.skipped}

| Test | Status | Duration | Error |
|------|--------|----------|-------|
"""
            
            for test in suite.tests:
                status_emoji = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(test.status.value, "❓")
                error_msg = test.error_message[:50] + "..." if test.error_message and len(test.error_message) > 50 else (test.error_message or "")
                markdown_content += f"| {test.test_name} | {status_emoji} {test.status.value} | {test.duration:.2f}s | {error_msg} |\n"
        
        output_file = output_dir / "test-report.md"
        with open(output_file, 'w') as f:
            f.write(markdown_content)
        return str(output_file)


class CIPlatformIntegrator:
    """Integrates with various CI/CD platforms."""
    
    def __init__(self, platform: CIPlatform):
        self.platform = platform
    
    def generate_ci_config(self, config: CIConfig, project_path: Path) -> str:
        """Generate CI configuration file."""
        if self.platform == CIPlatform.GITHUB_ACTIONS:
            return self._generate_github_actions_config(config, project_path)
        elif self.platform == CIPlatform.JENKINS:
            return self._generate_jenkins_config(config, project_path)
        elif self.platform == CIPlatform.GITLAB_CI:
            return self._generate_gitlab_ci_config(config, project_path)
        else:
            raise ValueError(f"Unsupported CI platform: {self.platform}")
    
    def _generate_github_actions_config(self, config: CIConfig, project_path: Path) -> str:
        """Generate GitHub Actions workflow."""
        return f"""name: Browse-to-Test Automated Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        npm install
        pip install -r requirements.txt
        npx playwright install
    
    - name: Run tests
      run: |
        pytest tests/ --browser=${{{{ matrix.browser }}}} \\
          --junit-xml=test-results/junit-${{{{ matrix.browser }}}}.xml \\
          --html=test-results/report-${{{{ matrix.browser }}}}.html \\
          --self-contained-html
      env:
        CI: true
        BROWSER: ${{{{ matrix.browser }}}}
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{{{ matrix.browser }}}}
        path: test-results/
        retention-days: {config.artifact_retention_days}
    
    - name: Upload screenshots
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: screenshots-${{{{ matrix.browser }}}}
        path: test-results/screenshots/
        retention-days: 7
    
    - name: Publish Test Results
      uses: dorny/test-reporter@v1
      if: success() || failure()
      with:
        name: Test Results (${{{{ matrix.browser }}}})
        path: test-results/junit-${{{{ matrix.browser }}}}.xml
        reporter: java-junit
    
    - name: Comment PR
      uses: actions/github-script@v6
      if: github.event_name == 'pull_request' && failure()
      with:
        script: |
          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '❌ Tests failed on ${{{{ matrix.browser }}}}. Check the [workflow run]({{{{ github.server_url }}}}/{{{{ github.repository }}}}/actions/runs/{{{{ github.run_id }}}}) for details.'
          }})

  maintenance-check:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run maintenance analysis
      run: python -m browse_to_test.maintenance --analyze --fix-auto
    
    - name: Create maintenance PR
      if: success()
      uses: peter-evans/create-pull-request@v5
      with:
        token: ${{{{ secrets.GITHUB_TOKEN }}}}
        commit-message: 'chore: automated test maintenance'
        title: 'Automated Test Maintenance'
        body: |
          This PR contains automated test maintenance updates:
          - Updated selectors for better stability
          - Optimized wait conditions
          - Fixed deprecated assertions
          
          Generated by browse-to-test maintenance system.
        branch: maintenance/automated-updates
"""
    
    def _generate_jenkins_config(self, config: CIConfig, project_path: Path) -> str:
        """Generate Jenkins pipeline."""
        return f"""pipeline {{
    agent any
    
    parameters {{
        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit'],
            description: 'Browser to run tests on'
        )
        booleanParam(
            name: 'RUN_MAINTENANCE',
            defaultValue: false,
            description: 'Run test maintenance after execution'
        )
    }}
    
    environment {{
        CI = 'true'
        PYTHONPATH = "${{env.WORKSPACE}}"
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                echo 'Setting up test environment...'
                sh 'python -m pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
                sh 'npx playwright install'
            }}
        }}
        
        stage('Run Tests') {{
            parallel {{
                stage('E2E Tests') {{
                    steps {{
                        sh '''
                            pytest tests/e2e/ \\
                                --browser=${{params.BROWSER}} \\
                                --junit-xml=test-results/junit-e2e.xml \\
                                --html=test-results/report-e2e.html \\
                                --self-contained-html
                        '''
                    }}
                    post {{
                        always {{
                            archiveArtifacts artifacts: 'test-results/**/*', allowEmptyArchive: true
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'test-results',
                                reportFiles: 'report-e2e.html',
                                reportName: 'Test Report'
                            ])
                        }}
                    }}
                }}
                
                stage('Unit Tests') {{
                    steps {{
                        sh '''
                            pytest tests/unit/ \\
                                --junit-xml=test-results/junit-unit.xml \\
                                --cov=browse_to_test \\
                                --cov-report=html:test-results/coverage
                        '''
                    }}
                }}
            }}
        }}
        
        stage('Test Maintenance') {{
            when {{
                expression {{ params.RUN_MAINTENANCE }}
            }}
            steps {{
                sh 'python -m browse_to_test.maintenance --analyze --report'
                archiveArtifacts artifacts: 'maintenance-report.json', allowEmptyArchive: true
            }}
        }}
    }}
    
    post {{
        always {{
            junit 'test-results/junit-*.xml'
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-results/coverage',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }}
        
        failure {{
            emailext (
                subject: "Test Failed: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Test execution failed. Check the build at ${{env.BUILD_URL}}",
                to: "${{env.CHANGE_AUTHOR_EMAIL}}"
            )
        }}
    }}
}}"""
    
    def _generate_gitlab_ci_config(self, config: CIConfig, project_path: Path) -> str:
        """Generate GitLab CI configuration."""
        return f"""stages:
  - test
  - maintenance
  - deploy

variables:
  CI: "true"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - node_modules/

.test_template: &test_definition
  stage: test
  image: python:3.11
  before_script:
    - apt-get update -qq && apt-get install -y -qq nodejs npm
    - pip install -r requirements.txt
    - npx playwright install-deps
    - npx playwright install
  script:
    - pytest tests/ 
        --browser=$BROWSER 
        --junit-xml=test-results/junit-$BROWSER.xml 
        --html=test-results/report-$BROWSER.html 
        --self-contained-html
  artifacts:
    when: always
    paths:
      - test-results/
    reports:
      junit: test-results/junit-$BROWSER.xml
    expire_in: {config.artifact_retention_days} days

test:chromium:
  <<: *test_definition
  variables:
    BROWSER: "chromium"

test:firefox:
  <<: *test_definition
  variables:
    BROWSER: "firefox"

test:webkit:
  <<: *test_definition
  variables:
    BROWSER: "webkit"

maintenance:
  stage: maintenance
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python -m browse_to_test.maintenance --analyze --report
  artifacts:
    paths:
      - maintenance-report.json
    expire_in: 1 week
  only:
    - schedules
    - main

pages:
  stage: deploy
  dependencies:
    - test:chromium
  script:
    - mkdir public
    - cp test-results/report-chromium.html public/index.html
    - cp -r test-results/* public/
  artifacts:
    paths:
      - public
  only:
    - main
"""


class TestMaintenanceEngine:
    """Automated test maintenance system."""
    
    def __init__(self):
        self.issues: List[MaintenanceIssue] = []
    
    def analyze_test_files(self, test_dir: Path) -> List[MaintenanceIssue]:
        """Analyze test files for maintenance issues."""
        self.issues = []
        
        for test_file in test_dir.rglob("*.py"):
            if test_file.name.startswith("test_"):
                self._analyze_file(test_file)
        
        return self.issues
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single test file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for outdated selectors
                if re.search(r'find_element\(By\.ID,|find_element_by_id', line):
                    self.issues.append(MaintenanceIssue(
                        issue_type=MaintenanceAction.UPDATE_SELECTORS,
                        test_file=str(file_path),
                        line_number=i,
                        description="Deprecated selenium selector method",
                        severity="medium",
                        suggested_fix="Use find_element(By.ID, 'id') instead",
                        auto_fixable=True
                    ))
                
                # Check for hard-coded waits
                if re.search(r'time\.sleep\(|sleep\(', line):
                    self.issues.append(MaintenanceIssue(
                        issue_type=MaintenanceAction.OPTIMIZE_WAITS,
                        test_file=str(file_path),
                        line_number=i,
                        description="Hard-coded sleep detected",
                        severity="high",
                        suggested_fix="Use WebDriverWait or Playwright auto-waiting",
                        auto_fixable=False
                    ))
                
                # Check for weak assertions
                if re.search(r'assert.*True$|assert.*False$', line):
                    self.issues.append(MaintenanceIssue(
                        issue_type=MaintenanceAction.FIX_ASSERTIONS,
                        test_file=str(file_path),
                        line_number=i,
                        description="Weak assertion detected",
                        severity="medium",
                        suggested_fix="Use specific assertion methods",
                        auto_fixable=False
                    ))
                
                # Check for test data in code
                if re.search(r'(username|password|email).*=.*["\'].*["\']', line, re.IGNORECASE):
                    self.issues.append(MaintenanceIssue(
                        issue_type=MaintenanceAction.UPDATE_DATA,
                        test_file=str(file_path),
                        line_number=i,
                        description="Hard-coded test data detected",
                        severity="low",
                        suggested_fix="Move test data to external configuration",
                        auto_fixable=False
                    ))
        
        except Exception as e:
            pass  # Skip files that can't be read
    
    def auto_fix_issues(self, test_dir: Path) -> Dict[str, int]:
        """Automatically fix issues that are auto-fixable."""
        fixes_applied = {
            "selector_updates": 0,
            "wait_optimizations": 0,
            "assertion_improvements": 0,
            "data_externalization": 0
        }
        
        auto_fixable_issues = [issue for issue in self.issues if issue.auto_fixable]
        
        # Group issues by file
        issues_by_file = {}
        for issue in auto_fixable_issues:
            if issue.test_file not in issues_by_file:
                issues_by_file[issue.test_file] = []
            issues_by_file[issue.test_file].append(issue)
        
        # Apply fixes file by file
        for file_path, file_issues in issues_by_file.items():
            if self._apply_fixes_to_file(file_path, file_issues):
                fixes_applied["selector_updates"] += len([i for i in file_issues if i.issue_type == MaintenanceAction.UPDATE_SELECTORS])
        
        return fixes_applied
    
    def _apply_fixes_to_file(self, file_path: str, issues: List[MaintenanceIssue]) -> bool:
        """Apply fixes to a single file."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Sort issues by line number in reverse order to avoid line number shifts
            sorted_issues = sorted(issues, key=lambda x: x.line_number, reverse=True)
            
            for issue in sorted_issues:
                if issue.issue_type == MaintenanceAction.UPDATE_SELECTORS:
                    line_idx = issue.line_number - 1
                    if line_idx < len(lines):
                        # Fix deprecated selector methods
                        original_line = lines[line_idx]
                        fixed_line = re.sub(
                            r'find_element_by_id\(["\']([^"\']+)["\']\)',
                            r'find_element(By.ID, "\1")',
                            original_line
                        )
                        fixed_line = re.sub(
                            r'find_element_by_class_name\(["\']([^"\']+)["\']\)',
                            r'find_element(By.CLASS_NAME, "\1")',
                            fixed_line
                        )
                        lines[line_idx] = fixed_line
            
            # Write back to file
            with open(file_path, 'w') as f:
                f.writelines(lines)
            
            return True
        
        except Exception as e:
            return False
    
    def generate_maintenance_report(self, output_path: Path) -> str:
        """Generate a comprehensive maintenance report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(self.issues),
            "issues_by_severity": {
                "high": len([i for i in self.issues if i.severity == "high"]),
                "medium": len([i for i in self.issues if i.severity == "medium"]),
                "low": len([i for i in self.issues if i.severity == "low"])
            },
            "issues_by_type": {},
            "auto_fixable_count": len([i for i in self.issues if i.auto_fixable]),
            "detailed_issues": []
        }
        
        # Count issues by type
        for action in MaintenanceAction:
            count = len([i for i in self.issues if i.issue_type == action])
            report["issues_by_type"][action.value] = count
        
        # Add detailed issues
        for issue in self.issues:
            report["detailed_issues"].append({
                "type": issue.issue_type.value,
                "file": issue.test_file,
                "line": issue.line_number,
                "description": issue.description,
                "severity": issue.severity,
                "suggested_fix": issue.suggested_fix,
                "auto_fixable": issue.auto_fixable
            })
        
        report_file = output_path / "maintenance-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)


class TestAnalytics:
    """Test execution analytics and trends."""
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)
    
    def track_execution(self, test_report: TestReport) -> None:
        """Track test execution for analytics."""
        analytics_file = self.reports_dir / "analytics.jsonl"
        
        analytics_entry = {
            "timestamp": test_report.timestamp.isoformat(),
            "total_tests": test_report.total_tests,
            "passed": test_report.total_passed,
            "failed": test_report.total_failed,
            "skipped": test_report.total_skipped,
            "duration": test_report.total_duration,
            "success_rate": test_report.success_rate,
            "environment": test_report.environment,
            "flaky_tests": test_report.flaky_tests
        }
        
        with open(analytics_file, 'a') as f:
            f.write(json.dumps(analytics_entry) + '\n')
    
    def generate_trends_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate trends report for the last N days."""
        analytics_file = self.reports_dir / "analytics.jsonl"
        
        if not analytics_file.exists():
            return {"error": "No analytics data available"}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = []
        
        with open(analytics_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_date = datetime.fromisoformat(entry["timestamp"])
                    if entry_date >= cutoff_date:
                        recent_data.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
        
        if not recent_data:
            return {"error": "No recent data available"}
        
        # Calculate trends
        success_rates = [entry["success_rate"] for entry in recent_data]
        durations = [entry["duration"] for entry in recent_data]
        
        trends = {
            "period_days": days,
            "total_executions": len(recent_data),
            "average_success_rate": sum(success_rates) / len(success_rates),
            "average_duration": sum(durations) / len(durations),
            "success_rate_trend": self._calculate_trend(success_rates),
            "duration_trend": self._calculate_trend(durations),
            "most_flaky_tests": self._get_most_flaky_tests(recent_data),
            "stability_score": self._calculate_stability_score(recent_data)
        }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg) * 100
        
        if change_percent > 5:
            return "improving"
        elif change_percent < -5:
            return "declining"
        else:
            return "stable"
    
    def _get_most_flaky_tests(self, data: List[Dict]) -> List[str]:
        """Get most frequently flaky tests."""
        flaky_counts = {}
        
        for entry in data:
            for test in entry.get("flaky_tests", []):
                flaky_counts[test] = flaky_counts.get(test, 0) + 1
        
        return sorted(flaky_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_stability_score(self, data: List[Dict]) -> float:
        """Calculate overall test stability score."""
        if not data:
            return 0.0
        
        success_rates = [entry["success_rate"] for entry in data]
        avg_success_rate = sum(success_rates) / len(success_rates)
        
        # Calculate variance in success rates (lower variance = more stable)
        variance = sum((rate - avg_success_rate) ** 2 for rate in success_rates) / len(success_rates)
        stability_score = max(0, 100 - variance)
        
        return round(stability_score, 2) 