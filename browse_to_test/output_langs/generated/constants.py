# Test configuration constants

# Timeout settings (in milliseconds)
DEFAULT_TIMEOUT_MS = 10000
PAGE_LOAD_TIMEOUT_MS = 30000
ELEMENT_TIMEOUT_MS = 10000
ACTION_TIMEOUT_MS = 5000
LONG_TIMEOUT_MS = 60000
SHORT_TIMEOUT_MS = 2000

# Browser configuration
DEFAULT_BROWSER = "chromium"
HEADLESS_MODE = False
SLOW_MO_MS = 0
VIEWPORT = {'width': 1280, 'height': 720}
USER_AGENT = "browse-to-test/1.0.0"

# Common element selectors
COMMON_SELECTORS = {
    "submit_button": ["button[type='submit']", "input[type='submit']", "[role='button'][aria-label*='submit']", ".submit-btn", ".btn-submit"],
    "text_input": ["input[type='text']", "input[type='email']", "input[type='password']", "input[type='search']", "textarea"],
    "link": ["a[href]", "[role='link']"],
    "form": ["form", "[role='form']"],
    "modal": [".modal", "[role='dialog']", "[role='alertdialog']", ".popup", ".overlay"],
    "close_button": [".close", "[aria-label*='close']", "[aria-label*='Close']", "[title*='close']", "[title*='Close']", ".btn-close", ".close-btn"],
    "dropdown": ["select", "[role='combobox']", "[role='listbox']", ".dropdown"],
    "checkbox": ["input[type='checkbox']", "[role='checkbox']"],
    "radio": ["input[type='radio']", "[role='radio']"],
}

# Sensitive data patterns
SENSITIVE_DATA_PATTERNS = ['password', 'secret', 'token', 'key', 'credential', 'auth', 'api_key', 'access_token', 'private_key', 'session_id', 'cookie', 'jwt', 'bearer']