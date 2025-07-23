import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright_script_generator import PlaywrightScriptGenerator

logger = logging.getLogger(__name__)


class PlaywrightTestGenerator(PlaywrightScriptGenerator):
	"""Extends PlaywrightScriptGenerator to generate test scripts with assertions and expectations."""

	def __init__(
		self,
		history_list: list[dict[str, Any]],
		sensitive_data_keys: list[str] | None = None,
		browser_config=None,
		context_config=None,
		test_config: dict[str, Any] | None = None,
	):
		"""
		Initializes the test script generator.

		Args:
		    history_list: A list of dictionaries representing AgentHistory items.
		    sensitive_data_keys: A list of keys used as placeholders for sensitive data.
		    browser_config: Configuration from the original Browser instance.
		    context_config: Configuration from the original BrowserContext instance.
		    test_config: Additional configuration for test-specific behavior.
		"""
		super().__init__(history_list, sensitive_data_keys, browser_config, context_config)
		
		self.test_config = test_config or {}
		self.test_timeout = self.test_config.get('test_timeout', 30000)  # 30 seconds default
		self.screenshot_on_failure = self.test_config.get('screenshot_on_failure', True)
		self.validate_page_loads = self.test_config.get('validate_page_loads', True)
		self.check_console_errors = self.test_config.get('check_console_errors', True)
		self.strict_assertions = self.test_config.get('strict_assertions', False)
		
		# Override action handlers to include test versions
		self._action_handlers.update({
			'go_to_url': self._map_go_to_url_with_tests,
			'input_text': self._map_input_text_with_tests,
			'click_element': self._map_click_element_with_tests,
			'click_element_by_index': self._map_click_element_with_tests,
			'scroll_down': self._map_scroll_with_tests,
			'scroll_up': self._map_scroll_with_tests,
			'search_google': self._map_search_google_with_tests,
			'click_download_button': self._map_click_download_button_with_tests,
			'done': self._map_done_with_tests,
		})

	def _get_imports_and_helpers(self) -> list[str]:
		"""Generates necessary import statements with test-specific additions."""
		base_imports = super()._get_imports_and_helpers()
		
		# Add test-specific imports
		test_imports = [
			'import traceback',
			'from datetime import datetime',
			'import tempfile',
			'',
			'# Test-specific configurations',
			f'TEST_TIMEOUT = {self.test_timeout}',
			f'SCREENSHOT_ON_FAILURE = {self.screenshot_on_failure}',
			f'VALIDATE_PAGE_LOADS = {self.validate_page_loads}',
			f'CHECK_CONSOLE_ERRORS = {self.check_console_errors}',
			f'STRICT_ASSERTIONS = {self.strict_assertions}',
			'',
		]
		
		# Insert test imports after the standard imports
		return base_imports + test_imports

	def _generate_test_helpers(self) -> list[str]:
		"""Generates test-specific helper functions."""
		return [
			'# --- Test Helper Functions ---',
			'',
			'class TestAssertionError(Exception):',
			'    """Custom exception for test assertion failures."""',
			'    pass',
			'',
			'',
			'async def take_screenshot_on_failure(page: Page, test_name: str, error_msg: str):',
			'    """Takes a screenshot when a test fails."""',
			'    if not SCREENSHOT_ON_FAILURE:',
			'        return',
			'    try:',
			'        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")',
			'        screenshot_path = f"test_failure_{test_name}_{timestamp}.png"',
			'        await page.screenshot(path=screenshot_path, full_page=True)',
			'        print(f"  Screenshot saved: {screenshot_path}")',
			'    except Exception as e:',
			'        print(f"  Failed to take screenshot: {e}", file=sys.stderr)',
			'',
			'',
			'async def assert_element_visible(page: Page, selector: str, timeout: int = TEST_TIMEOUT, step_info: str = "") -> bool:',
			'    """Asserts that an element is visible on the page."""',
			'    try:',
			'        locator = page.locator(selector).first',
			'        await locator.wait_for(state="visible", timeout=timeout)',
			'        print(f"  ✓ Element visible: {selector} ({step_info})")',
			'        return True',
			'    except Exception as e:',
			'        error_msg = f"Element not visible: {selector} ({step_info}) - {e}"',
			'        if STRICT_ASSERTIONS:',
			'            await take_screenshot_on_failure(page, "element_visibility", error_msg)',
			'            raise TestAssertionError(error_msg)',
			'        else:',
			'            print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'            return False',
			'',
			'',
			'async def assert_element_text_contains(page: Page, selector: str, expected_text: str, timeout: int = TEST_TIMEOUT, step_info: str = "") -> bool:',
			'    """Asserts that an element contains expected text."""',
			'    try:',
			'        locator = page.locator(selector).first',
			'        await locator.wait_for(timeout=timeout)',
			'        actual_text = await locator.text_content()',
			'        if expected_text.lower() in (actual_text or "").lower():',
			'            print(f"  ✓ Text assertion passed: \'{expected_text}\' found in element ({step_info})")',
			'            return True',
			'        else:',
			'            error_msg = f"Text assertion failed: expected \'{expected_text}\' in \'{actual_text}\' ({step_info})"',
			'            if STRICT_ASSERTIONS:',
			'                await take_screenshot_on_failure(page, "text_assertion", error_msg)',
			'                raise TestAssertionError(error_msg)',
			'            else:',
			'                print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'                return False',
			'    except Exception as e:',
			'        error_msg = f"Text assertion error: {selector} ({step_info}) - {e}"',
			'        if STRICT_ASSERTIONS:',
			'            await take_screenshot_on_failure(page, "text_assertion", error_msg)',
			'            raise TestAssertionError(error_msg)',
			'        else:',
			'            print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'            return False',
			'',
			'',
			'async def assert_url_contains(page: Page, expected_url_part: str, step_info: str = "") -> bool:',
			'    """Asserts that the current URL contains the expected part."""',
			'    try:',
			'        current_url = page.url',
			'        if expected_url_part.lower() in current_url.lower():',
			'            print(f"  ✓ URL assertion passed: \'{expected_url_part}\' found in current URL ({step_info})")',
			'            return True',
			'        else:',
			'            error_msg = f"URL assertion failed: expected \'{expected_url_part}\' in \'{current_url}\' ({step_info})"',
			'            if STRICT_ASSERTIONS:',
			'                await take_screenshot_on_failure(page, "url_assertion", error_msg)',
			'                raise TestAssertionError(error_msg)',
			'            else:',
			'                print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'                return False',
			'    except Exception as e:',
			'        error_msg = f"URL assertion error: ({step_info}) - {e}"',
			'        if STRICT_ASSERTIONS:',
			'            await take_screenshot_on_failure(page, "url_assertion", error_msg)',
			'            raise TestAssertionError(error_msg)',
			'        else:',
			'            print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'            return False',
			'',
			'',
			'async def check_console_errors_and_warn(page: Page, step_info: str = ""):',
			'    """Checks for console errors and warns if any are found."""',
			'    if not CHECK_CONSOLE_ERRORS:',
			'        return',
			'    try:',
			'        # This is a basic implementation - in practice you\'d set up console listeners',
			'        # For now, we\'ll just add a placeholder that could be enhanced',
			'        console_errors = await page.evaluate("() => window.__testConsoleErrors || []")',
			'        if console_errors:',
			'            print(f"  ⚠ Console errors detected ({step_info}): {console_errors}", file=sys.stderr)',
			'    except Exception as e:',
			'        print(f"  Could not check console errors ({step_info}): {e}", file=sys.stderr)',
			'',
			'',
			'async def validate_page_load_success(page: Page, step_info: str = ""):',
			'    """Validates that the page loaded successfully."""',
			'    if not VALIDATE_PAGE_LOADS:',
			'        return True',
			'    try:',
			'        # Check if page title exists and is not empty',
			'        title = await page.title()',
			'        if not title or title.strip() == "":',
			'            print(f"  ⚠ Page has no title ({step_info})", file=sys.stderr)',
			'        ',
			'        # Check if body element exists',
			'        body_count = await page.locator("body").count()',
			'        if body_count == 0:',
			'            error_msg = f"Page has no body element ({step_info})"',
			'            if STRICT_ASSERTIONS:',
			'                await take_screenshot_on_failure(page, "page_load", error_msg)',
			'                raise TestAssertionError(error_msg)',
			'            else:',
			'                print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'                return False',
			'        ',
			'        print(f"  ✓ Page load validation passed ({step_info})")',
			'        return True',
			'    except TestAssertionError:',
			'        raise',
			'    except Exception as e:',
			'        error_msg = f"Page load validation error ({step_info}): {e}"',
			'        if STRICT_ASSERTIONS:',
			'            await take_screenshot_on_failure(page, "page_load", error_msg)',
			'            raise TestAssertionError(error_msg)',
			'        else:',
			'            print(f"  ⚠ {error_msg}", file=sys.stderr)',
			'            return False',
			'',
			'# --- End Test Helper Functions ---',
			'',
		]

	# Override action mapping methods with test versions

	def _map_go_to_url_with_tests(self, params: dict, step_info_str: str, **kwargs) -> list[str]:
		"""Enhanced go_to_url with test validations."""
		url = params.get('url')
		goto_timeout = self._get_goto_timeout()
		script_lines = []
		
		if url and isinstance(url, str):
			escaped_url = json.dumps(url)
			script_lines.extend([
				f'            print(f"Navigating to: {url} ({step_info_str})")',
				f'            await page.goto({escaped_url}, timeout={goto_timeout})',
				f"            await page.wait_for_load_state('load', timeout={goto_timeout})",
				'            await page.wait_for_timeout(1000)',
				'            # Test validations for navigation',
				f'            await validate_page_load_success(page, "{step_info_str}")',
				f'            await assert_url_contains(page, {escaped_url}, "{step_info_str}")',
				f'            await check_console_errors_and_warn(page, "{step_info_str}")',
			])
		else:
			script_lines.append(f'            # Skipping go_to_url ({step_info_str}): missing or invalid url')
		
		return script_lines

	def _map_input_text_with_tests(
		self, params: dict, history_item: dict, action_index_in_step: int, step_info_str: str, **kwargs
	) -> list[str]:
		"""Enhanced input_text with test validations."""
		index = params.get('index')
		text = params.get('text', '')
		selector = self._get_selector_for_action(history_item, action_index_in_step)
		script_lines = []
		
		if selector and index is not None:
			clean_text_expression = f'replace_sensitive_data({json.dumps(str(text))}, SENSITIVE_DATA)'
			escaped_selector = json.dumps(selector)
			escaped_step_info = json.dumps(step_info_str)
			
			script_lines.extend([
				'            # Test: Verify element is visible before input',
				f'            await assert_element_visible(page, {escaped_selector}, step_info={escaped_step_info})',
				'            # Perform input action',
				f'            await _try_locate_and_act(page, {escaped_selector}, "fill", text={clean_text_expression}, step_info={escaped_step_info})',
				'            # Test: Verify input was successful (check value)',
				'            try:',
				f'                input_value = await page.locator({escaped_selector}).first.input_value()',
				f'                expected_text = {clean_text_expression}',
				'                if input_value == expected_text:',
				f'                    print(f"  ✓ Input validation passed: text correctly entered ({step_info_str})")',
				'                else:',
				f'                    print(f"  ⚠ Input validation warning: expected \'{{expected_text}}\' but got \'{{input_value}}\' ({step_info_str})", file=sys.stderr)',
				'            except Exception as input_check_err:',
				f'                print(f"  Could not verify input value ({step_info_str}): {{input_check_err}}", file=sys.stderr)',
			])
		else:
			script_lines.append(
				f'            # Skipping input_text ({step_info_str}): missing index ({index}) or selector ({selector})'
			)
		
		return script_lines

	def _map_click_element_with_tests(
		self, params: dict, history_item: dict, action_index_in_step: int, step_info_str: str, action_type: str, **kwargs
	) -> list[str]:
		"""Enhanced click_element with test validations."""
		if action_type == 'click_element_by_index':
			logger.warning(f"Mapping legacy 'click_element_by_index' to 'click_element' ({step_info_str})")
		
		index = params.get('index')
		selector = self._get_selector_for_action(history_item, action_index_in_step)
		script_lines = []
		
		if selector and index is not None:
			escaped_selector = json.dumps(selector)
			escaped_step_info = json.dumps(step_info_str)
			
			script_lines.extend([
				'            # Test: Verify element is visible and clickable',
				f'            await assert_element_visible(page, {escaped_selector}, step_info={escaped_step_info})',
				'            try:',
				f'                await page.locator({escaped_selector}).first.wait_for(state="attached", timeout=TEST_TIMEOUT)',
				f'                print(f"  ✓ Element is clickable: {selector} ({step_info_str})")',
				'            except Exception as clickable_err:',
				f'                print(f"  ⚠ Element may not be clickable ({step_info_str}): {{clickable_err}}", file=sys.stderr)',
				'            # Perform click action',
				f'            await _try_locate_and_act(page, {escaped_selector}, "click", step_info={escaped_step_info})',
				'            # Wait for potential page changes after click',
				'            await page.wait_for_timeout(1000)',
				'            # Test: Check for console errors after click',
				f'            await check_console_errors_and_warn(page, "{step_info_str} - after click")',
			])
		else:
			script_lines.append(
				f'            # Skipping {action_type} ({step_info_str}): missing index ({index}) or selector ({selector})'
			)
		
		return script_lines

	def _map_scroll_with_tests(self, params: dict, step_info_str: str, action_type: str = None, **kwargs) -> list[str]:
		"""Enhanced scroll actions with test validations."""
		amount = params.get('amount')
		script_lines = []
		
		# Get current scroll position before scroll
		script_lines.append('            # Test: Get scroll position before action')
		script_lines.append('            scroll_before = await page.evaluate("window.pageYOffset")')
		
		if action_type == 'scroll_up':
			if amount and isinstance(amount, int):
				script_lines.append(f'            print(f"Scrolling up by {amount} pixels ({step_info_str})")')
				script_lines.append(f"            await page.evaluate('window.scrollBy(0, -{amount})')")
			else:
				script_lines.append(f'            print(f"Scrolling up by one page height ({step_info_str})")')
				script_lines.append("            await page.evaluate('window.scrollBy(0, -window.innerHeight)')")
		else:  # scroll_down
			if amount and isinstance(amount, int):
				script_lines.append(f'            print(f"Scrolling down by {amount} pixels ({step_info_str})")')
				script_lines.append(f"            await page.evaluate('window.scrollBy(0, {amount})')")
			else:
				script_lines.append(f'            print(f"Scrolling down by one page height ({step_info_str})")')
				script_lines.append("            await page.evaluate('window.scrollBy(0, window.innerHeight)')")
		
		script_lines.extend([
			'            await page.wait_for_timeout(500)',
			'            # Test: Verify scroll position changed',
			'            scroll_after = await page.evaluate("window.pageYOffset")',
			'            if scroll_before != scroll_after:',
			f'                print(f"  ✓ Scroll validation passed: position changed from {{scroll_before}} to {{scroll_after}} ({step_info_str})")',
			'            else:',
			f'                print(f"  ⚠ Scroll validation warning: position did not change ({step_info_str})", file=sys.stderr)',
		])
		
		return script_lines

	def _map_search_google_with_tests(self, params: dict, step_info_str: str, **kwargs) -> list[str]:
		"""Enhanced search_google with test validations."""
		query = params.get('query')
		goto_timeout = self._get_goto_timeout()
		script_lines = []
		
		if query and isinstance(query, str):
			clean_query = f'replace_sensitive_data({json.dumps(query)}, SENSITIVE_DATA)'
			search_url_expression = f'f"https://www.google.com/search?q={{ urllib.parse.quote_plus({clean_query}) }}&udm=14"'
			
			script_lines.extend([
				f'            search_url = {search_url_expression}',
				f'            print(f"Searching Google for query related to: {{ {clean_query} }} ({step_info_str})")',
				f'            await page.goto(search_url, timeout={goto_timeout})',
				f"            await page.wait_for_load_state('load', timeout={goto_timeout})",
				'            await page.wait_for_timeout(1000)',
				'            # Test validations for Google search',
				f'            await validate_page_load_success(page, "{step_info_str}")',
				'            await assert_url_contains(page, "google.com/search", step_info="Google search URL validation")',
				'            # Test: Check if search results are present',
				'            try:',
				'                search_results = await page.locator("[data-ved], .g, .MjjYud").count()',
				'                if search_results > 0:',
				f'                    print(f"  ✓ Search results found: {{search_results}} results ({step_info_str})")',
				'                else:',
				f'                    print(f"  ⚠ No search results found ({step_info_str})", file=sys.stderr)',
				'            except Exception as search_check_err:',
				f'                print(f"  Could not verify search results ({step_info_str}): {{search_check_err}}", file=sys.stderr)',
			])
		else:
			script_lines.append(f'            # Skipping search_google ({step_info_str}): missing or invalid query')
		
		return script_lines

	def _map_click_download_button_with_tests(
		self, params: dict, history_item: dict, action_index_in_step: int, step_info_str: str, **kwargs
	) -> list[str]:
		"""Enhanced click_download_button with test validations."""
		index = params.get('index')
		selector = self._get_selector_for_action(history_item, action_index_in_step)
		download_dir_in_script = "'./files'"
		
		if self.context_config and self.context_config.save_downloads_path:
			download_dir_in_script = repr(self.context_config.save_downloads_path)

		script_lines = []
		
		if selector and index is not None:
			script_lines.extend([
				f'            print(f"Attempting to download file by clicking element ({selector}) ({step_info_str})")',
				'            # Test: Verify download button is visible and clickable',
				f'            await assert_element_visible(page, {json.dumps(selector)}, step_info={json.dumps(step_info_str)})',
				'            try:',
				'                # Setup download expectation with test validation',
				'                async with page.expect_download(timeout=120000) as download_info:',
				f'                    await _try_locate_and_act(page, {json.dumps(selector)}, "click", step_info={json.dumps(f"{step_info_str} (triggering download)")})',
				'                download = await download_info.value',
				f'                configured_download_dir = {download_dir_in_script}',
				'                download_dir_path = Path(configured_download_dir).resolve()',
				'                download_dir_path.mkdir(parents=True, exist_ok=True)',
				"                base, ext = os.path.splitext(download.suggested_filename or f'download_{{len(list(download_dir_path.iterdir())) + 1}}.tmp')",
				'                counter = 1',
				"                download_path_obj = download_dir_path / f'{base}{ext}'",
				'                while download_path_obj.exists():',
				"                    download_path_obj = download_dir_path / f'{base}({{counter}}){ext}'",
				'                    counter += 1',
				'                await download.save_as(str(download_path_obj))',
				"                print(f'  ✓ File downloaded successfully to: {str(download_path_obj)}')",
				'                # Test: Verify download file exists and has content',
				'                if download_path_obj.exists():',
				'                    file_size = download_path_obj.stat().st_size',
				'                    if file_size > 0:',
				f'                        print(f"  ✓ Download validation passed: file size {{file_size}} bytes ({step_info_str})")',
				'                    else:',
				f'                        print(f"  ⚠ Download validation warning: file is empty ({step_info_str})", file=sys.stderr)',
				'                else:',
				f'                    error_msg = f"Download validation failed: file not found at {{download_path_obj}} ({step_info_str})"',
				'                    if STRICT_ASSERTIONS:',
				'                        raise TestAssertionError(error_msg)',
				'                    else:',
				'                        print(f"  ⚠ {error_msg}", file=sys.stderr)',
				'            except PlaywrightActionError as pae:',
				'                raise pae',
				'            except Exception as download_err:',
				f"                raise PlaywrightActionError(f'Download failed for {step_info_str}: {{download_err}}') from download_err",
			])
		else:
			script_lines.append(
				f'            # Skipping click_download_button ({step_info_str}): missing index ({index}) or selector ({selector})'
			)
		
		return script_lines

	def _map_done_with_tests(self, params: dict, step_info_str: str, **kwargs) -> list[str]:
		"""Enhanced done action with final test validations."""
		script_lines = []
		
		if isinstance(params, dict):
			final_text = params.get('text', '')
			success_status = params.get('success', False)
			escaped_final_text_with_placeholders = json.dumps(str(final_text))
			
			script_lines.extend([
				f'            print("\\n--- Task marked as Done by agent ({step_info_str}) ---")',
				f'            print(f"Agent reported success: {success_status}")',
				'            # Final Message from agent (may contain placeholders):',
				f'            final_message = replace_sensitive_data({escaped_final_text_with_placeholders}, SENSITIVE_DATA)',
				'            print(final_message)',
				'            # Final test validations',
				f'            print("\\n--- Running Final Test Validations ({step_info_str}) ---")',
				f'            await check_console_errors_and_warn(page, "{step_info_str} - final check")',
				'            # Test: Verify page is still responsive',
				'            try:',
				'                page_title = await page.title()',
				f'                print(f"  ✓ Final page validation: title = \'{{page_title}}\' ({step_info_str})")',
				'            except Exception as final_err:',
				f'                print(f"  ⚠ Final page validation error ({step_info_str}): {{final_err}}", file=sys.stderr)',
				'            # Test result summary',
				'            if success_status:',
				f'                print(f"  ✓ Test completed successfully according to agent ({step_info_str})")',
				'            else:',
				f'                print(f"  ⚠ Test completed but agent reported failure ({step_info_str})", file=sys.stderr)',
			])
		else:
			script_lines.extend([
				f'            print("\\n--- Task marked as Done by agent ({step_info_str}) ---")',
				'            print("Success: N/A (invalid params)")',
				'            print("Final Message: N/A (invalid params)")',
				f'            print(f"  ⚠ Done action had invalid parameters ({step_info_str})", file=sys.stderr)',
			])
		
		return script_lines

	def generate_script_content(self) -> str:
		"""Generates the full Playwright test script content as a string."""
		script_lines = []
		self._page_counter = 0

		if not self._imports_helpers_added:
			script_lines.extend(self._get_imports_and_helpers())
			self._imports_helpers_added = True

		# Read helper script content
		helper_script_path = Path(__file__).parent / 'playwright_script_helpers.py'
		try:
			with open(helper_script_path, encoding='utf-8') as f_helper:
				helper_script_content = f_helper.read()
		except FileNotFoundError:
			logger.error(f'Helper script not found at {helper_script_path}. Cannot generate script.')
			return '# Error: Helper script file missing.'
		except Exception as e:
			logger.error(f'Error reading helper script {helper_script_path}: {e}')
			return f'# Error: Could not read helper script: {e}'

		script_lines.extend(self._get_sensitive_data_definitions())

		# Add the helper script content
		script_lines.append('\n# --- Helper Functions (from playwright_script_helpers.py) ---')
		script_lines.append(helper_script_content)
		script_lines.append('# --- End Helper Functions ---')

		# Add test-specific helper functions
		script_lines.extend(self._generate_test_helpers())

		# Generate browser launch and context creation code with test enhancements
		browser_launch_args = self._generate_browser_launch_args()
		context_options = self._generate_context_options()
		browser_type = 'chromium'
		if self.browser_config and self.browser_config.browser_class in ['firefox', 'webkit']:
			browser_type = self.browser_config.browser_class

		script_lines.extend([
			'async def run_generated_test_script():',
			'    global SENSITIVE_DATA',
			'    test_results = {"passed": 0, "failed": 0, "warnings": 0}',
			'    async with async_playwright() as p:',
			'        browser = None',
			'        context = None',
			'        page = None',
			'        exit_code = 0',
			'        try:',
			f"            print('=== Starting Playwright Test Script Execution ===')",
			f"            print('Launching {browser_type} browser for testing...')",
			f'            browser = await p.{browser_type}.launch({browser_launch_args})',
			f'            context = await browser.new_context({context_options})',
			"            print('Browser context created for testing.')",
		])

		# Add cookie loading logic (same as parent)
		if self.context_config and self.context_config.cookies_file:
			cookies_file_path = repr(self.context_config.cookies_file)
			script_lines.extend([
				'            # Load cookies if specified',
				f'            cookies_path = {cookies_file_path}',
				'            if cookies_path and os.path.exists(cookies_path):',
				'                try:',
				"                    with open(cookies_path, 'r', encoding='utf-8') as f_cookies:",
				'                        cookies = json.load(f_cookies)',
				"                        valid_same_site = ['Strict', 'Lax', 'None']",
				'                        for cookie in cookies:',
				"                            if 'sameSite' in cookie and cookie['sameSite'] not in valid_same_site:",
				'                                print(f\'  Warning: Fixing invalid sameSite value "{{cookie["sameSite"]}}" to None for cookie {{cookie.get("name")}}\', file=sys.stderr)',
				"                                cookie['sameSite'] = 'None'",
				'                        await context.add_cookies(cookies)',
				"                        print(f'  Successfully loaded {{len(cookies)}} cookies from {{cookies_path}}')",
				'                except Exception as cookie_err:',
				"                    print(f'  Warning: Failed to load or add cookies from {{cookies_path}}: {{cookie_err}}', file=sys.stderr)",
				'            else:',
				'                if cookies_path:',
				"                    print(f'  Cookie file not found at: {cookies_path}')",
				'',
			])

		script_lines.extend([
			'            # Initial page setup for testing',
			'            if context.pages:',
			'                page = context.pages[0]',
			"                print('Using initial page provided by context.')",
			'            else:',
			'                page = await context.new_page()',
			"                print('Created a new page as none existed.')",
			'            ',
			'            # Setup console error tracking for tests',
			'            if CHECK_CONSOLE_ERRORS:',
			'                await page.add_init_script("window.__testConsoleErrors = [];")',
			'                await page.add_init_script("""',
			'                    const originalConsoleError = console.error;',
			'                    console.error = function(...args) {',
			'                        window.__testConsoleErrors.push(args.join(\' \'));',
			'                        originalConsoleError.apply(console, args);',
			'                    };',
			'                """)',
			'            ',
			"            print('\\n=== Starting Test Script Execution ===')",
		])

		# Generate the main script body with test actions
		action_counter = 0
		stop_processing_steps = False
		previous_item_dict = None

		for step_index, item_dict in enumerate(self.history):
			if stop_processing_steps:
				break

			if not isinstance(item_dict, dict):
				logger.warning(f'Skipping step {step_index + 1}: Item is not a dictionary ({type(item_dict)})')
				script_lines.append(f'\n            # --- Test Step {step_index + 1}: Skipped (Invalid Format) ---')
				previous_item_dict = item_dict
				continue

			script_lines.append(f'\n            # --- Test Step {step_index + 1} ---')
			model_output = item_dict.get('model_output')

			if not isinstance(model_output, dict) or 'action' not in model_output:
				script_lines.append('            # No valid model_output or action found for this test step')
				previous_item_dict = item_dict
				continue

			actions = model_output.get('action')
			if not isinstance(actions, list):
				script_lines.append(f'            # Actions format is not a list: {type(actions)}')
				previous_item_dict = item_dict
				continue

			for action_index_in_step, action_detail in enumerate(actions):
				action_counter += 1
				script_lines.append(f'            # Test Action {action_counter}')

				step_info_str = f'Test Step {step_index + 1}, Action {action_index_in_step + 1}'
				action_lines = self._map_action_to_playwright(
					action_dict=action_detail,
					history_item=item_dict,
					previous_history_item=previous_item_dict,
					action_index_in_step=action_index_in_step,
					step_info_str=step_info_str,
				)
				script_lines.extend(action_lines)

				action_type = next(iter(action_detail.keys()), None) if isinstance(action_detail, dict) else None
				if action_type == 'done':
					stop_processing_steps = True
					break

			previous_item_dict = item_dict

		# Enhanced final block with test result reporting
		script_lines.extend([
			'        except TestAssertionError as tae:',
			"            print(f'\\n=== TEST ASSERTION FAILED: {tae} ===', file=sys.stderr)",
			'            exit_code = 2',  # Specific exit code for test failures
			'        except PlaywrightActionError as pae:',
			"            print(f'\\n=== PLAYWRIGHT ACTION ERROR: {pae} ===', file=sys.stderr)",
			'            exit_code = 1',
			'        except Exception as e:',
			"            print(f'\\n=== UNEXPECTED ERROR: {e} ===', file=sys.stderr)",
			'            import traceback',
			'            traceback.print_exc()',
			'            exit_code = 1',
			'        finally:',
			"            print('\\n=== Test Script Execution Finished ===')",
			'            if exit_code == 0:',
			"                print('✓ All tests completed successfully')",
			'            elif exit_code == 1:',
			"                print('✗ Script failed due to execution errors', file=sys.stderr)",
			'            elif exit_code == 2:',
			"                print('✗ Script failed due to test assertion failures', file=sys.stderr)",
			"            print('Closing browser/context...')",
			'            if context:',
			'                 try: await context.close()',
			"                 except Exception as ctx_close_err: print(f'  Warning: could not close context: {ctx_close_err}', file=sys.stderr)",
			'            if browser:',
			'                 try: await browser.close()',
			"                 except Exception as browser_close_err: print(f'  Warning: could not close browser: {browser_close_err}', file=sys.stderr)",
			"            print('Browser/context closed.')",
			'            if exit_code != 0:',
			"                print(f'Test script finished with errors (exit code {exit_code}).', file=sys.stderr)",
			'                sys.exit(exit_code)',
			'',
			'# --- Test Script Entry Point ---',
			"if __name__ == '__main__':",
			"    if os.name == 'nt':",
			'        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())',
			'    asyncio.run(run_generated_test_script())',
		])

		return '\n'.join(script_lines) 