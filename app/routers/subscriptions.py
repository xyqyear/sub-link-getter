from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from ..cache import get_cached_subscription, set_cached_subscription
from ..config import get_site_by_id, load_config
from ..fetcher import FetchError, fetch_subscription

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class FetchSummaryResponse(BaseModel):
    name: str
    url: str
    content_length: int
    cached: bool = False


@router.get("/{site_id}", response_class=PlainTextResponse)
def get_subscription(site_id: str, use_cache: bool = True) -> str:
    config = load_config()
    site = get_site_by_id(config, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")

    if use_cache:
        cached = get_cached_subscription(site_id)
        if cached:
            return cached.content

    try:
        result = fetch_subscription(site, config.global_config)
    except FetchError as e:
        raise HTTPException(status_code=500, detail=str(e))

    set_cached_subscription(site_id, result["name"], result["url"], result["content"])

    return result["content"]


@router.post("/{site_id}/fetch")
def fetch_subscription_fresh(site_id: str) -> FetchSummaryResponse:
    config = load_config()
    site = get_site_by_id(config, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")

    try:
        result = fetch_subscription(site, config.global_config)
    except FetchError as e:
        raise HTTPException(status_code=500, detail=str(e))

    set_cached_subscription(site_id, result["name"], result["url"], result["content"])

    return FetchSummaryResponse(
        name=result["name"],
        url=result["url"],
        content_length=len(result["content"]),
        cached=False,
    )
