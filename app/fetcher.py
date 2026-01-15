import re

from playwright.sync_api import Page
from scrapling.fetchers import StealthySession

from .captcha import recognize_captcha
from .config import GlobalConfig, SiteConfig


class FetchError(Exception):
    pass


class SubscriptionFetcher:
    def __init__(self, site: SiteConfig, global_config: GlobalConfig):
        self.site = site
        self.global_config = global_config
        self.result: dict = {}
        self.error_msg: str | None = None

    def _perform_login(self, page: Page) -> None:
        page.wait_for_selector(
            self.site.username_selector, state="visible", timeout=10000
        )
        page.fill(self.site.username_selector, self.site.username)
        page.fill(self.site.password_selector, self.site.password)

        if self.site.captcha_image_selector and self.site.captcha_input_selector:
            captcha_img = page.locator(self.site.captcha_image_selector)
            if captcha_img.count() > 0:
                print("Captcha detected, recognizing...")

                for attempt in range(self.site.captcha_retry_count):
                    captcha_bytes = captcha_img.screenshot()
                    captcha_text = recognize_captcha(
                        captcha_bytes, self.global_config.openrouter_api_key
                    )

                    if captcha_text:
                        print(
                            f"Captcha recognized (attempt {attempt + 1}): {captcha_text}"
                        )
                        page.fill(self.site.captcha_input_selector, captcha_text)
                        break
                    elif attempt < self.site.captcha_retry_count - 1:
                        print("Captcha recognition failed, retrying...")
                    else:
                        self.error_msg = f"Failed to recognize captcha after {self.site.captcha_retry_count} attempts"
                        return

        page.click(self.site.login_button_selector)
        page.wait_for_selector(
            self.site.post_login_wait_selector, state="attached", timeout=30000
        )

    def _extract_subscription_url(self, page: Page) -> tuple[str, str] | None:
        name_regex = re.compile(self.site.subscription_name_pattern)

        labels = page.query_selector_all(self.site.subscription_label_selector)
        groups = page.query_selector_all(self.site.subscription_group_selector)

        print(f"Found {len(labels)} labels and {len(groups)} groups")

        for i, label in enumerate(labels):
            if i >= len(groups):
                break

            name = (label.text_content() or "").strip()
            if not name_regex.search(name):
                continue

            group = groups[i]
            url_elem = group.query_selector(self.site.subscription_url_selector)

            if not url_elem:
                print("  No URL element found")
                continue

            sub_url = ""
            for retry in range(self.site.subscription_url_retry_count):
                if self.site.subscription_url_type == "input":
                    sub_url = url_elem.input_value() or ""
                else:
                    attr = self.site.subscription_url_attribute or "data-clipboard-text"
                    sub_url = url_elem.get_attribute(attr) or ""

                if sub_url:
                    break

                if retry < self.site.subscription_url_retry_count - 1:
                    page.wait_for_timeout(self.site.subscription_url_retry_delay_ms)

            if not sub_url:
                print("  Empty URL after retries")
                continue

            print(f"  Subscription URL: {sub_url}")
            return (name, sub_url)

        return None

    def _page_action(self, page: Page) -> None:
        page.wait_for_selector(
            f"{self.site.login_wait_selector}, {self.site.post_login_wait_selector}",
            state="attached",
            timeout=30000,
        )

        login_form = page.query_selector(self.site.login_wait_selector)
        if login_form:
            print("Login form detected, performing login...")
            self._perform_login(page)
            if self.error_msg:
                return

        if self.site.post_login_delay_ms > 0:
            page.wait_for_timeout(self.site.post_login_delay_ms)

        sub_info = self._extract_subscription_url(page)
        if sub_info is None:
            self.error_msg = "No matching subscription found"
            return

        name, sub_url = sub_info

        print("Fetching subscription content...")
        response = page.request.get(sub_url)
        content = response.text()

        print(f"Content length: {len(content)} chars")

        if self.site.content_validation and self.site.content_validation not in content:
            self.error_msg = (
                f"Content validation failed: '{self.site.content_validation}' not found"
            )
            return

        self.result = {"name": name, "url": sub_url, "content": content}

    def fetch(self) -> dict:
        print(f"Accessing target page: {self.site.product_url}")

        with StealthySession(
            headless=self.global_config.headless,
            google_search=False,
            user_data_dir=str(self.global_config.browser_data_dir),
            solve_cloudflare=self.global_config.solve_cloudflare,
        ) as session:
            session.fetch(
                self.site.product_url,
                network_idle=True,
                page_action=self._page_action,
                timeout=self.global_config.timeout,
            )

        if self.error_msg:
            raise FetchError(self.error_msg)

        return self.result


def fetch_subscription(site: SiteConfig, global_config: GlobalConfig) -> dict:
    fetcher = SubscriptionFetcher(site, global_config)
    return fetcher.fetch()
