#!/usr/bin/env node

/**
 * Visual Regression Testing System
 * 
 * Provides automated UI consistency checking across different environments and deployments.
 * Part of Phase 7: Advanced Automation & Future-Proofing
 */

import { execSync } from 'child_process';
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, statSync } from 'fs';
import { join, dirname, basename } from 'path';

interface VisualTest {
  id: string;
  name: string;
  description: string;
  url: string;
  selector?: string;
  viewport: {
    width: number;
    height: number;
  };
  waitForSelector?: string;
  delay?: number;
  excludeElements?: string[];
  threshold: number;
  category: 'component' | 'page' | 'flow' | 'responsive';
  environments: string[];
  createdAt: Date;
  enabled: boolean;
}

interface VisualTestResult {
  testId: string;
  environment: string;
  timestamp: Date;
  passed: boolean;
  diffPercentage: number;
  screenshotPath: string;
  baselinePath: string;
  diffPath?: string;
  error?: string;
  metadata: {
    viewport: { width: number; height: number };
    userAgent: string;
    duration: number;
  };
}

interface VisualTestSuite {
  name: string;
  description: string;
  tests: VisualTest[];
  environments: {
    [key: string]: {
      baseUrl: string;
      headers?: Record<string, string>;
      cookies?: Array<{ name: string; value: string; domain?: string }>;
    };
  };
  configuration: {
    threshold: number;
    pixelDiffThreshold: number;
    retryAttempts: number;
    concurrency: number;
    captureDelay: number;
  };
}

class VisualRegressionTester {
  private testsDir: string;
  private screenshotsDir: string;
  private baselineDir: string;
  private resultsDir: string;
  private configPath: string;

  constructor() {
    this.testsDir = join(process.cwd(), 'visual-tests');
    this.screenshotsDir = join(this.testsDir, 'screenshots');
    this.baselineDir = join(this.testsDir, 'baseline');
    this.resultsDir = join(this.testsDir, 'results');
    this.configPath = join(this.testsDir, 'visual-config.json');
    
    this.ensureDirectories();
  }

  /**
   * Initialize visual regression testing
   */
  async initialize(): Promise<void> {
    console.log('📸 Initializing Visual Regression Testing...');
    
    // Create default configuration
    await this.createDefaultConfiguration();
    
    // Create example test suite
    await this.createExampleTests();
    
    // Setup Playwright for visual testing
    await this.setupPlaywright();
    
    console.log('✅ Visual Regression Testing initialized');
  }

  /**
   * Create default configuration
   */
  private async createDefaultConfiguration(): Promise<void> {
    if (existsSync(this.configPath)) {
      return;
    }

    const defaultConfig: VisualTestSuite = {
      name: 'Synapse Hub Visual Tests',
      description: 'Automated visual regression testing for UI consistency',
      tests: [],
      environments: {
        development: {
          baseUrl: 'http://localhost:5173',
          headers: {
            'User-Agent': 'Visual-Regression-Test'
          }
        },
        staging: {
          baseUrl: 'https://staging.synapse-hub.com',
          headers: {
            'User-Agent': 'Visual-Regression-Test'
          }
        },
        production: {
          baseUrl: 'https://synapse-hub.com',
          headers: {
            'User-Agent': 'Visual-Regression-Test'
          }
        }
      },
      configuration: {
        threshold: 0.2,
        pixelDiffThreshold: 0.1,
        retryAttempts: 3,
        concurrency: 2,
        captureDelay: 1000
      }
    };

    writeFileSync(this.configPath, JSON.stringify(defaultConfig, null, 2));
    console.log('📋 Created default visual testing configuration');
  }

  /**
   * Create example test cases
   */
  private async createExampleTests(): Promise<void> {
    const config = this.getConfiguration();
    
    if (config.tests.length > 0) {
      return;
    }

    const exampleTests: VisualTest[] = [
      {
        id: 'homepage-desktop',
        name: 'Homepage Desktop',
        description: 'Full homepage screenshot on desktop viewport',
        url: '/',
        viewport: { width: 1920, height: 1080 },
        waitForSelector: 'main',
        delay: 2000,
        threshold: 0.2,
        category: 'page',
        environments: ['development', 'staging'],
        createdAt: new Date(),
        enabled: true
      },
      {
        id: 'homepage-mobile',
        name: 'Homepage Mobile',
        description: 'Full homepage screenshot on mobile viewport',
        url: '/',
        viewport: { width: 375, height: 667 },
        waitForSelector: 'main',
        delay: 2000,
        threshold: 0.2,
        category: 'responsive',
        environments: ['development', 'staging'],
        createdAt: new Date(),
        enabled: true
      },
      {
        id: 'navigation-component',
        name: 'Navigation Component',
        description: 'Main navigation component',
        url: '/',
        selector: 'nav',
        viewport: { width: 1920, height: 1080 },
        waitForSelector: 'nav',
        threshold: 0.1,
        category: 'component',
        environments: ['development', 'staging'],
        createdAt: new Date(),
        enabled: true
      },
      {
        id: 'login-flow',
        name: 'Login Flow',
        description: 'Complete login user flow',
        url: '/login',
        viewport: { width: 1280, height: 720 },
        waitForSelector: 'form',
        threshold: 0.2,
        category: 'flow',
        environments: ['development'],
        createdAt: new Date(),
        enabled: true
      }
    ];

    config.tests = exampleTests;
    writeFileSync(this.configPath, JSON.stringify(config, null, 2));
    console.log('📝 Created example visual test cases');
  }

  /**
   * Setup Playwright for visual testing
   */
  private async setupPlaywright(): Promise<void> {
    try {
      // Check if Playwright is installed
      execSync('npx playwright --version', { stdio: 'pipe' });
      console.log('🎭 Playwright already available');
    } catch {
      console.log('🎭 Installing Playwright...');
      try {
        execSync('npx playwright install', { stdio: 'pipe' });
        console.log('✅ Playwright installed successfully');
      } catch (error) {
        console.warn('⚠️  Failed to install Playwright:', error.message);
        console.log('Please run: npx playwright install');
      }
    }

    // Create Playwright test script
    const playwrightScript = `
import { test, expect } from '@playwright/test';
import { VisualRegressionTester } from './visual-regression-testing';

const tester = new VisualRegressionTester();

// This will be dynamically generated based on visual test configuration
test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Setup common page configuration
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Visual-Regression-Test'
    });
  });

  // Tests will be generated dynamically
});`;

    const playwrightTestPath = join(this.testsDir, 'playwright.visual.spec.ts');
    if (!existsSync(playwrightTestPath)) {
      writeFileSync(playwrightTestPath, playwrightScript.trim());
      console.log('🎭 Created Playwright test template');
    }
  }

  /**
   * Run visual regression tests
   */
  async runVisualTests(
    environment: string = 'development',
    testIds?: string[],
    updateBaseline: boolean = false
  ): Promise<VisualTestResult[]> {
    console.log(`📸 Running visual regression tests for ${environment}...`);
    
    const config = this.getConfiguration();
    const envConfig = config.environments[environment];
    
    if (!envConfig) {
      throw new Error(`Environment configuration not found: ${environment}`);
    }

    // Filter tests
    let testsToRun = config.tests.filter(test => 
      test.enabled && test.environments.includes(environment)
    );

    if (testIds && testIds.length > 0) {
      testsToRun = testsToRun.filter(test => testIds.includes(test.id));
    }

    if (testsToRun.length === 0) {
      console.log('✅ No tests to run');
      return [];
    }

    console.log(`🎯 Running ${testsToRun.length} visual tests`);
    
    const results: VisualTestResult[] = [];
    
    // Process tests with concurrency control
    const batches = this.createTestBatches(testsToRun, config.configuration.concurrency);
    
    for (const batch of batches) {
      const batchPromises = batch.map(test => 
        this.runSingleTest(test, environment, envConfig, updateBaseline)
      );
      
      const batchResults = await Promise.allSettled(batchPromises);
      
      batchResults.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          results.push(result.value);
        } else {
          results.push({
            testId: batch[index].id,
            environment,
            timestamp: new Date(),
            passed: false,
            diffPercentage: 100,
            screenshotPath: '',
            baselinePath: '',
            error: result.reason.message,
            metadata: {
              viewport: batch[index].viewport,
              userAgent: 'Visual-Regression-Test',
              duration: 0
            }
          });
        }
      });
    }

    // Generate test report
    await this.generateTestReport(results, environment);
    
    const passedTests = results.filter(r => r.passed).length;
    const failedTests = results.length - passedTests;
    
    console.log(`\n📊 Visual Test Results:`);
    console.log(`  ✅ Passed: ${passedTests}`);
    console.log(`  ❌ Failed: ${failedTests}`);
    console.log(`  📈 Success Rate: ${Math.round((passedTests / results.length) * 100)}%`);

    return results;
  }

  /**
   * Run a single visual test
   */
  private async runSingleTest(
    test: VisualTest,
    environment: string,
    envConfig: any,
    updateBaseline: boolean
  ): Promise<VisualTestResult> {
    const startTime = Date.now();
    
    try {
      console.log(`  📸 Testing: ${test.name}`);
      
      const url = `${envConfig.baseUrl}${test.url}`;
      const screenshotPath = join(
        this.screenshotsDir,
        environment,
        `${test.id}-${Date.now()}.png`
      );
      const baselinePath = join(this.baselineDir, `${test.id}.png`);
      
      // Ensure directories exist
      mkdirSync(dirname(screenshotPath), { recursive: true });
      mkdirSync(dirname(baselinePath), { recursive: true });
      
      // Take screenshot using Playwright
      const screenshot = await this.takeScreenshot(test, url, envConfig);
      writeFileSync(screenshotPath, screenshot);
      
      let passed = true;
      let diffPercentage = 0;
      let diffPath: string | undefined;
      
      if (updateBaseline) {
        // Update baseline image
        writeFileSync(baselinePath, screenshot);
        console.log(`    📁 Updated baseline for ${test.id}`);
      } else if (existsSync(baselinePath)) {
        // Compare with baseline
        const comparison = await this.compareImages(baselinePath, screenshotPath, test.threshold);
        passed = comparison.passed;
        diffPercentage = comparison.diffPercentage;
        diffPath = comparison.diffPath;
        
        if (passed) {
          console.log(`    ✅ ${test.name}: PASSED (${diffPercentage.toFixed(2)}% diff)`);
        } else {
          console.log(`    ❌ ${test.name}: FAILED (${diffPercentage.toFixed(2)}% diff, threshold: ${test.threshold}%)`);
        }
      } else {
        // No baseline exists, create it
        writeFileSync(baselinePath, screenshot);
        console.log(`    📁 Created baseline for ${test.id}`);
      }
      
      const duration = Date.now() - startTime;
      
      return {
        testId: test.id,
        environment,
        timestamp: new Date(),
        passed,
        diffPercentage,
        screenshotPath,
        baselinePath,
        diffPath,
        metadata: {
          viewport: test.viewport,
          userAgent: 'Visual-Regression-Test',
          duration
        }
      };
      
    } catch (error) {
      const duration = Date.now() - startTime;
      
      return {
        testId: test.id,
        environment,
        timestamp: new Date(),
        passed: false,
        diffPercentage: 100,
        screenshotPath: '',
        baselinePath: '',
        error: error.message,
        metadata: {
          viewport: test.viewport,
          userAgent: 'Visual-Regression-Test',
          duration
        }
      };
    }
  }

  /**
   * Take screenshot using Playwright
   */
  private async takeScreenshot(test: VisualTest, url: string, envConfig: any): Promise<Buffer> {
    const playwrightCode = `
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: ${JSON.stringify(test.viewport)},
    extraHTTPHeaders: ${JSON.stringify(envConfig.headers || {})},
    userAgent: 'Visual-Regression-Test'
  });
  
  const page = await context.newPage();
  
  ${envConfig.cookies ? `
  await context.addCookies(${JSON.stringify(envConfig.cookies)});
  ` : ''}
  
  await page.goto('${url}');
  
  ${test.waitForSelector ? `
  await page.waitForSelector('${test.waitForSelector}');
  ` : ''}
  
  ${test.delay ? `
  await page.waitForTimeout(${test.delay});
  ` : ''}
  
  ${test.excludeElements ? `
  // Hide excluded elements
  await page.evaluate(() => {
    const selectors = ${JSON.stringify(test.excludeElements)};
    selectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => el.style.visibility = 'hidden');
    });
  });
  ` : ''}
  
  const screenshot = await page.screenshot({
    ${test.selector ? `clip: await page.locator('${test.selector}').boundingBox(),` : 'fullPage: true,'}
    animations: 'disabled'
  });
  
  await browser.close();
  
  process.stdout.write(screenshot);
})();`;

    const tempScriptPath = join(this.testsDir, `temp-${test.id}-${Date.now()}.js`);
    writeFileSync(tempScriptPath, playwrightCode);
    
    try {
      const screenshot = execSync(`node ${tempScriptPath}`, { 
        encoding: null,
        maxBuffer: 10 * 1024 * 1024 // 10MB buffer
      });
      return screenshot;
    } finally {
      // Clean up temp script
      try {
        require('fs').unlinkSync(tempScriptPath);
      } catch {}
    }
  }

  /**
   * Compare two images and return difference
   */
  private async compareImages(
    baselinePath: string,
    screenshotPath: string,
    threshold: number
  ): Promise<{ passed: boolean; diffPercentage: number; diffPath?: string }> {
    try {
      // Use pixelmatch for image comparison
      const pixelmatchCode = `
const fs = require('fs');
const PNG = require('pngjs').PNG;
const pixelmatch = require('pixelmatch');

const img1 = PNG.sync.read(fs.readFileSync('${baselinePath}'));
const img2 = PNG.sync.read(fs.readFileSync('${screenshotPath}'));
const { width, height } = img1;
const diff = new PNG({ width, height });

const numDiffPixels = pixelmatch(img1.data, img2.data, diff.data, width, height, {
  threshold: 0.1,
  includeAA: false
});

const diffPercentage = (numDiffPixels / (width * height)) * 100;
const passed = diffPercentage <= ${threshold};

const result = {
  passed,
  diffPercentage,
  numDiffPixels,
  totalPixels: width * height
};

if (!passed) {
  const diffPath = '${screenshotPath.replace('.png', '-diff.png')}';
  fs.writeFileSync(diffPath, PNG.sync.write(diff));
  result.diffPath = diffPath;
}

console.log(JSON.stringify(result));
`;

      const tempScriptPath = join(this.testsDir, `compare-${Date.now()}.js`);
      writeFileSync(tempScriptPath, pixelmatchCode);
      
      try {
        const output = execSync(`node ${tempScriptPath}`, { encoding: 'utf8' });
        const result = JSON.parse(output.trim());
        
        return {
          passed: result.passed,
          diffPercentage: result.diffPercentage,
          diffPath: result.diffPath
        };
      } finally {
        // Clean up temp script
        try {
          require('fs').unlinkSync(tempScriptPath);
        } catch {}
      }
      
    } catch (error) {
      console.warn(`⚠️  Image comparison failed: ${error.message}`);
      // Fallback to basic file comparison
      const baseline = readFileSync(baselinePath);
      const screenshot = readFileSync(screenshotPath);
      
      if (baseline.equals(screenshot)) {
        return { passed: true, diffPercentage: 0 };
      } else {
        return { passed: false, diffPercentage: 100 };
      }
    }
  }

  /**
   * Generate visual test report
   */
  private async generateTestReport(results: VisualTestResult[], environment: string): Promise<void> {
    const reportPath = join(this.resultsDir, `visual-report-${environment}-${Date.now()}.html`);
    
    const passedTests = results.filter(r => r.passed);
    const failedTests = results.filter(r => !r.passed);
    
    const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Regression Test Report - ${environment}</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 20px; background: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .stat.passed { border-left: 4px solid #28a745; }
        .stat.failed { border-left: 4px solid #dc3545; }
        .test-result { margin-bottom: 20px; border: 1px solid #ddd; border-radius: 6px; overflow: hidden; }
        .test-header { padding: 15px; background: #f8f9fa; border-bottom: 1px solid #ddd; }
        .test-header.passed { background: #d4edda; }
        .test-header.failed { background: #f8d7da; }
        .test-content { padding: 15px; }
        .screenshot-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .screenshot { text-align: center; }
        .screenshot img { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }
        .metadata { background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; }
        .error { background: #f8d7da; padding: 10px; border-radius: 4px; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Visual Regression Test Report</h1>
            <p>Environment: <strong>${environment}</strong></p>
            <p>Generated: ${new Date().toLocaleString()}</p>
        </div>
        
        <div class="stats">
            <div class="stat passed">
                <h3>${passedTests.length}</h3>
                <p>Passed Tests</p>
            </div>
            <div class="stat failed">
                <h3>${failedTests.length}</h3>
                <p>Failed Tests</p>
            </div>
            <div class="stat">
                <h3>${Math.round((passedTests.length / results.length) * 100)}%</h3>
                <p>Success Rate</p>
            </div>
            <div class="stat">
                <h3>${results.reduce((sum, r) => sum + r.metadata.duration, 0)}ms</h3>
                <p>Total Duration</p>
            </div>
        </div>
        
        ${results.map(result => `
            <div class="test-result">
                <div class="test-header ${result.passed ? 'passed' : 'failed'}">
                    <h3>${result.testId} ${result.passed ? '✅' : '❌'}</h3>
                    <p>Diff: ${result.diffPercentage.toFixed(2)}% | Duration: ${result.metadata.duration}ms | Viewport: ${result.metadata.viewport.width}x${result.metadata.viewport.height}</p>
                </div>
                <div class="test-content">
                    ${result.error ? `
                        <div class="error">
                            <strong>Error:</strong> ${result.error}
                        </div>
                    ` : `
                        <div class="screenshot-grid">
                            <div class="screenshot">
                                <h4>Current Screenshot</h4>
                                <img src="${result.screenshotPath}" alt="Current screenshot" />
                            </div>
                            <div class="screenshot">
                                <h4>Baseline</h4>
                                <img src="${result.baselinePath}" alt="Baseline screenshot" />
                            </div>
                            ${result.diffPath ? `
                                <div class="screenshot">
                                    <h4>Difference</h4>
                                    <img src="${result.diffPath}" alt="Difference" />
                                </div>
                            ` : ''}
                        </div>
                    `}
                </div>
            </div>
        `).join('')}
    </div>
</body>
</html>`;

    writeFileSync(reportPath, html);
    console.log(`📄 Visual test report generated: ${reportPath}`);
  }

  /**
   * Create test batches for concurrency control
   */
  private createTestBatches<T>(items: T[], batchSize: number): T[][] {
    const batches: T[][] = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  /**
   * Add a new visual test
   */
  async addVisualTest(test: Omit<VisualTest, 'id' | 'createdAt'>): Promise<string> {
    const config = this.getConfiguration();
    
    const newTest: VisualTest = {
      ...test,
      id: `${test.name.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`,
      createdAt: new Date()
    };
    
    config.tests.push(newTest);
    writeFileSync(this.configPath, JSON.stringify(config, null, 2));
    
    console.log(`✅ Added visual test: ${newTest.id}`);
    return newTest.id;
  }

  /**
   * Get configuration
   */
  private getConfiguration(): VisualTestSuite {
    if (!existsSync(this.configPath)) {
      throw new Error('Visual testing configuration not found. Run init first.');
    }
    
    return JSON.parse(readFileSync(this.configPath, 'utf8'));
  }

  /**
   * List all visual tests
   */
  listVisualTests(): VisualTest[] {
    const config = this.getConfiguration();
    return config.tests.sort((a, b) => a.name.localeCompare(b.name));
  }

  /**
   * Ensure required directories exist
   */
  private ensureDirectories(): void {
    [
      this.testsDir,
      this.screenshotsDir,
      this.baselineDir,
      this.resultsDir
    ].forEach(dir => {
      if (!existsSync(dir)) {
        mkdirSync(dir, { recursive: true });
      }
    });
  }
}

// CLI Interface
if (require.main === module) {
  const tester = new VisualRegressionTester();
  
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'init':
      tester.initialize().catch(error => {
        console.error('Initialization failed:', error);
        process.exit(1);
      });
      break;
    
    case 'run':
      const environment = args[1] || 'development';
      const updateBaseline = args.includes('--update-baseline');
      const testIds = args.filter(arg => !arg.startsWith('--') && arg !== environment).slice(1);
      
      tester.runVisualTests(environment, testIds.length > 0 ? testIds : undefined, updateBaseline)
        .catch(error => {
          console.error('Visual tests failed:', error);
          process.exit(1);
        });
      break;
    
    case 'list':
      try {
        const tests = tester.listVisualTests();
        console.log(`📋 Visual Tests (${tests.length}):`);
        tests.forEach(test => {
          const status = test.enabled ? '✅' : '❌';
          console.log(`  ${status} ${test.id} (${test.category})`);
          console.log(`    ${test.description}`);
          console.log(`    Environments: ${test.environments.join(', ')}`);
          console.log(`    Viewport: ${test.viewport.width}x${test.viewport.height}`);
        });
      } catch (error) {
        console.error('Failed to list tests:', error);
        process.exit(1);
      }
      break;
    
    case 'baseline':
      const baselineEnv = args[1] || 'development';
      tester.runVisualTests(baselineEnv, undefined, true)
        .catch(error => {
          console.error('Baseline update failed:', error);
          process.exit(1);
        });
      break;
    
    default:
      console.log(`
📸 Visual Regression Testing System

Usage:
  tsx scripts/visual-regression-testing.ts <command> [options]

Commands:
  init                                - Initialize visual testing
  run [env] [test-ids...] [options]   - Run visual tests
  list                                - List all visual tests  
  baseline [env]                      - Update baseline images

Options:
  --update-baseline                   - Update baseline during run

Environments:
  development                         - Local development (default)
  staging                             - Staging environment
  production                          - Production environment

Examples:
  tsx scripts/visual-regression-testing.ts init
  tsx scripts/visual-regression-testing.ts run development
  tsx scripts/visual-regression-testing.ts run staging homepage-desktop navigation-component
  tsx scripts/visual-regression-testing.ts baseline development
  tsx scripts/visual-regression-testing.ts run development --update-baseline
      `);
  }
}

export { VisualRegressionTester, VisualTest, VisualTestResult, VisualTestSuite }; 