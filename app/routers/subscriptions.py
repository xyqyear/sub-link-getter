from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..cache import get_cached_subscription, set_cached_subscription
from ..config import get_site_by_id, load_config
from ..fetcher import FetchError, fetch_subscription

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class SubscriptionResponse(BaseModel):
    name: str
    url: str
    content: str
    cached: bool = False


@router.get("/{site_id}")
def get_subscription(site_id: str, use_cache: bool = True) -> SubscriptionResponse:
    config = load_config()
    site = get_site_by_id(config, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")

    if use_cache:
        cached = get_cached_subscription(site_id)
        if cached:
            return SubscriptionResponse(
                name=cached.name,
                url=cached.url,
                content=cached.content,
                cached=True,
            )

    try:
        result = fetch_subscription(site, config.global_config)
    except FetchError as e:
        raise HTTPException(status_code=500, detail=str(e))

    set_cached_subscription(site_id, result["name"], result["url"], result["content"])

    return SubscriptionResponse(
        name=result["name"],
        url=result["url"],
        content=result["content"],
        cached=False,
    )


@router.post("/{site_id}/fetch")
def fetch_subscription_fresh(site_id: str) -> SubscriptionResponse:
    return get_subscription(site_id, use_cache=False)
