import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

CONFIG_FILE = Path("config.json")


class GlobalConfig(BaseModel):
    openrouter_api_key: str = ""
    headless: bool = False
    solve_cloudflare: bool = True
    timeout: int = 120000
    cache_file: str = "cache.json"
    browser_data_dir: str = ".browser_data"


class SiteConfig(BaseModel):
    id: str = Field(..., description="Unique site identifier")
    name: str = Field(..., description="Display name")
    product_url: str = Field(
        ..., description="URL to access (redirects to login if needed)"
    )

    login_wait_selector: str = Field(..., description="Selector to detect login page")
    post_login_wait_selector: str = Field(
        ..., description="Selector to wait after login"
    )
    username_selector: str = Field(..., description="Username input selector")
    password_selector: str = Field(..., description="Password input selector")
    login_button_selector: str = Field(..., description="Login button selector")
    captcha_image_selector: str | None = Field(
        None, description="Optional captcha image selector"
    )
    captcha_input_selector: str | None = Field(
        None, description="Optional captcha input selector"
    )
    captcha_retry_count: int = Field(
        2, description="Number of captcha recognition attempts"
    )

    username: str = Field(..., description="Login username")
    password: str = Field(..., description="Login password")

    subscription_label_selector: str = Field(
        ..., description="Selector for subscription type labels"
    )
    subscription_group_selector: str = Field(
        ..., description="Selector for subscription groups (paired by index)"
    )
    subscription_url_type: Literal["input", "copy"] = Field(
        ..., description="How to extract URL"
    )
    subscription_url_selector: str = Field(
        ..., description="Selector within group for URL element"
    )
    subscription_url_attribute: str | None = Field(
        None, description="For 'copy' type: data attribute name"
    )
    subscription_name_pattern: str = Field(
        ".*", description="Regex to filter subscription type"
    )
    subscription_url_retry_count: int = Field(
        10, description="Number of retries for getting subscription URL"
    )
    subscription_url_retry_delay_ms: int = Field(
        100, description="Delay in ms between retries"
    )

    post_login_delay_ms: int = Field(
        100, description="Delay in ms after login before extracting subscription"
    )
    content_validation: str = Field(
        "allow-lan", description="String that must be in content"
    )


class AppConfig(BaseModel):
    global_config: GlobalConfig = Field(default_factory=GlobalConfig)
    sites: list[SiteConfig] = Field(default_factory=list)


def load_config() -> AppConfig:
    if not CONFIG_FILE.exists():
        return AppConfig()
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)
    except Exception:
        return AppConfig()


def save_config(config: AppConfig) -> None:
    CONFIG_FILE.write_text(
        config.model_dump_json(indent=2),
        encoding="utf-8",
    )


def get_site_by_id(config: AppConfig, site_id: str) -> SiteConfig | None:
    for site in config.sites:
        if site.id == site_id:
            return site
    return None
