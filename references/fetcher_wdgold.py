import os
import re
from pathlib import Path

from playwright.sync_api import Page
from scrapling.fetchers import StealthySession

from app.captcha import recognize_captcha

TARGET_URL = "https://wd-gold.com/clientarea.php?action=productdetails&id=152195"
USER_DATA_DIR = Path(__file__).parent / ".browser_data_wdgold"
SUBSCRIPTION_NAME_PATTERN = r"Clash"


def extract_subscription_url_from_page(
    page: Page, name_pattern: str = SUBSCRIPTION_NAME_PATTERN
) -> tuple[str, str] | None:
    """
    Extract the first matching subscription URL from the page.

    Args:
        page: Playwright Page object
        name_pattern: Regex pattern to filter subscription names

    Returns:
        Tuple of (name, url) or None if not found
    """
    name_regex = re.compile(name_pattern)

    labels = page.query_selector_all(".subscribe-area .subscribe-label")
    input_groups = page.query_selector_all(".subscribe-area .ray-input-group")

    print(
        f"Found {len(labels)} subscription labels and {len(input_groups)} input groups"
    )

    for i, label in enumerate(labels):
        if i >= len(input_groups):
            break

        name = (label.text_content() or "").strip()
        print(f"Processing subscription: {name}")

        if not name_regex.search(name):
            print("  Skipping (doesn't match pattern)")
            continue

        input_group = input_groups[i]
        copy_btn = input_group.query_selector("a.ray-btn.copy[data-clipboard-text]")

        if not copy_btn:
            print("  No copy button found")
            continue

        sub_url = copy_btn.get_attribute("data-clipboard-text") or ""
        if not sub_url:
            print("  Empty data-clipboard-text attribute")
            continue

        print(f"  Subscription URL: {sub_url}")
        return (name, sub_url)

    return None


def fetch_subscription_content(
    username: str,
    password: str,
    api_key: str,
    name_pattern: str = SUBSCRIPTION_NAME_PATTERN,
) -> dict | None:
    """
    Fetch the first matching subscription content from the target page.

    Args:
        username: Login username/email
        password: Login password
        api_key: OpenRouter API key for captcha recognition
        name_pattern: Regex pattern to filter subscription names

    Returns:
        Dict with 'name', 'url', and 'content' keys, or None if not found
    """
    result: dict | None = None

    def page_action(page: Page):
        nonlocal result

        page.wait_for_selector(
            ".signin-signup-form, .ray-btn", state="attached", timeout=30000
        )

        login_form = page.query_selector(".signin-signup-form")
        if login_form:
            print("Login form detected, performing login...")

            page.wait_for_selector("#inputEmail", state="visible", timeout=10000)
            page.fill("#inputEmail", username)
            page.fill("#inputPassword", password)

            captcha_img = page.locator("#inputCaptchaImage")
            if captcha_img.count() > 0:
                print("Captcha detected, recognizing...")
                captcha_bytes = captcha_img.screenshot()

                captcha_text = recognize_captcha(captcha_bytes, api_key)
                if captcha_text:
                    print(f"Captcha recognized: {captcha_text}")
                    page.fill("#inputCaptcha", captcha_text)
                else:
                    print("Failed to recognize captcha")
                    return

            page.click("#login")
            page.wait_for_selector(".ray-btn", state="attached", timeout=30000)

        sub_info = extract_subscription_url_from_page(page, name_pattern)
        if sub_info is None:
            return

        name, sub_url = sub_info

        print("  Fetching subscription content...")
        response = page.request.get(sub_url)
        content = response.text()

        result = {"name": name, "url": sub_url, "content": content}
        print(f"  Content length: {len(content)} chars")

    print(f"Accessing target page: {TARGET_URL}")

    with StealthySession(
        headless=False,
        google_search=False,
        user_data_dir=str(USER_DATA_DIR),
        solve_cloudflare=True,
    ) as session:
        session.fetch(
            TARGET_URL,
            network_idle=True,
            page_action=page_action,
            timeout=120000,
        )

    return result


def main():
    import sys

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        sys.exit(1)

    if len(sys.argv) < 3:
        print(
            "Usage: OPENROUTER_API_KEY=xxx python fetcher_wdgold.py <username> <password> [name_pattern]"
        )
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    name_pattern = sys.argv[3] if len(sys.argv) > 3 else SUBSCRIPTION_NAME_PATTERN

    print(f"Fetching subscriptions for user: {username}")
    print(f"Name pattern: {name_pattern}")
    print("-" * 50)

    result = fetch_subscription_content(username, password, api_key, name_pattern)

    print("-" * 50)

    if result is None:
        print("No matching subscription found")
        sys.exit(1)

    print(f"Name: {result.get('name', 'Unknown')}")
    print(f"URL: {result.get('url', 'N/A')}")
    content_preview = result.get("content", "")[:200]
    print(f"Content preview: {content_preview}...")


if __name__ == "__main__":
    main()
