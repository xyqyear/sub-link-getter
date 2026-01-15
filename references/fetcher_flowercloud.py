import re
from pathlib import Path

from playwright.sync_api import Page
from scrapling.fetchers import StealthySession

TARGET_URL = (
    "https://api-flowercloud.com/clientarea.php?action=productdetails&id=232628"
)
USER_DATA_DIR = Path(__file__).parent / ".browser_data"
SUBSCRIPTION_NAME_PATTERN = r".*"


def extract_subscription_url_from_page(
    page: Page, name_pattern: str = SUBSCRIPTION_NAME_PATTERN
) -> tuple[str, str] | None:
    """
    Extract the first matching subscription URL directly from the page.

    Args:
        page: Playwright Page object
        name_pattern: Regex pattern to filter subscription names

    Returns:
        Tuple of (name, url) or None if not found
    """
    name_regex = re.compile(name_pattern)
    subscription_items = page.query_selector_all(".subscription-item")

    print(f"Found {len(subscription_items)} subscription items")

    for item in subscription_items:
        info_elem = item.query_selector(".subscription-info")
        if not info_elem:
            continue

        name = (info_elem.text_content() or "").strip()
        print(f"Processing subscription: {name}")

        if not name_regex.search(name):
            print("  Skipping (doesn't match pattern)")
            continue

        actions_elem = item.query_selector(".subscription-actions")
        if not actions_elem:
            print("  No actions element found")
            continue

        button = actions_elem.query_selector("button[data-copy]")
        if not button:
            print("  No button with data-copy found")
            continue

        sub_url = button.get_attribute("data-copy") or ""
        if not sub_url:
            print("  Empty data-copy attribute")
            continue

        print(f"  Subscription URL: {sub_url}")

        if "api-huacloud.dev" not in sub_url:
            print("  Skipping (not api-huacloud.dev domain)")
            continue

        return (name, sub_url)

    return None


def fetch_subscription_content(
    username: str, password: str, name_pattern: str = SUBSCRIPTION_NAME_PATTERN
) -> dict | None:
    """
    Fetch the first matching subscription content from the target page.

    Args:
        username: Login username/email
        password: Login password
        name_pattern: Regex pattern to filter subscription names

    Returns:
        Dict with 'name', 'url', and 'content' keys, or None if not found
    """
    result: dict | None = None

    def page_action(page: Page):
        nonlocal result

        page.wait_for_selector(
            ".c-login, .subscription-item", state="attached", timeout=30000
        )

        login_dialog = page.query_selector(".c-login")
        if login_dialog:
            print("Login dialog detected, performing login...")
            page.wait_for_selector(
                '.c-login input[name="username"]', state="visible", timeout=10000
            )
            page.fill('.c-login input[name="username"]', username)
            page.fill('.c-login input[name="password"]', password)
            page.click('.c-login button[type="submit"]')
            page.wait_for_selector(
                ".subscription-item", state="attached", timeout=30000
            )

        sub_info = extract_subscription_url_from_page(page, name_pattern)
        if sub_info is None:
            return

        name, sub_url = sub_info

        print("  Fetching subscription content via download...")

        with page.expect_download() as download_info:
            try:
                page.goto(sub_url)
            except Exception:
                pass

        download = download_info.value
        content = download.path().read_text(encoding="utf-8")

        result = {"name": name, "url": sub_url, "content": content}
        print(f"  Content length: {len(content)} chars")
        if "allow-lan" in content:
            print("  Success! Content contains 'allow-lan'")
        else:
            print("  Warning: Content doesn't contain 'allow-lan'")
            result["warning"] = "Content doesn't contain 'allow-lan'"

    print(f"Accessing target page: {TARGET_URL}")

    with StealthySession(
        headless=True, google_search=False, user_data_dir=str(USER_DATA_DIR)
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

    if len(sys.argv) < 3:
        print("Usage: python fetcher.py <username> <password> [name_pattern]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    name_pattern = sys.argv[3] if len(sys.argv) > 3 else SUBSCRIPTION_NAME_PATTERN

    print(f"Fetching subscriptions for user: {username}")
    print(f"Name pattern: {name_pattern}")
    print("-" * 50)

    result = fetch_subscription_content(username, password, name_pattern)

    print("-" * 50)

    if result is None:
        print("No matching subscription found")
        sys.exit(1)

    print(f"Name: {result.get('name', 'Unknown')}")
    print(f"URL: {result.get('url', 'N/A')}")
    if "error" in result:
        print(f"Error: {result['error']}")
    elif "warning" in result:
        print(f"Warning: {result['warning']}")
    else:
        content_preview = result.get("content", "")[:200]
        print(f"Content preview: {content_preview}...")


if __name__ == "__main__":
    main()
