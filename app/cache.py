import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import BaseModel

from .config import load_config

CACHE_TTL_HOURS = 24


class CacheEntry(BaseModel):
    name: str
    url: str
    content: str
    fetched_at: datetime

    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        expiry = self.fetched_at + timedelta(hours=CACHE_TTL_HOURS)
        return now < expiry


class Cache(BaseModel):
    entries: dict[str, CacheEntry] = {}


def _get_cache_file() -> Path:
    config = load_config()
    return Path(config.global_config.cache_file)


def load_cache() -> Cache:
    cache_file = _get_cache_file()
    if not cache_file.exists():
        return Cache()
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        return Cache.model_validate(data)
    except Exception:
        return Cache()


def save_cache(cache: Cache) -> None:
    cache_file = _get_cache_file()
    cache_file.write_text(
        cache.model_dump_json(indent=2),
        encoding="utf-8",
    )


def get_cached_subscription(site_id: str) -> CacheEntry | None:
    cache = load_cache()
    entry = cache.entries.get(site_id)
    if entry and entry.is_valid():
        return entry
    return None


def set_cached_subscription(site_id: str, name: str, url: str, content: str) -> None:
    cache = load_cache()
    cache.entries[site_id] = CacheEntry(
        name=name,
        url=url,
        content=content,
        fetched_at=datetime.now(timezone.utc),
    )
    save_cache(cache)
