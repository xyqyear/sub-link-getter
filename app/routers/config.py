from fastapi import APIRouter, HTTPException

from ..config import (
    GlobalConfig,
    SiteConfig,
    get_site_by_id,
    load_config,
    save_config,
)

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/schema/site")
def get_site_schema() -> dict:
    return SiteConfig.model_json_schema()


@router.get("/schema/global")
def get_global_schema() -> dict:
    return GlobalConfig.model_json_schema()


@router.get("/global")
def get_global_config() -> GlobalConfig:
    config = load_config()
    return config.global_config


@router.put("/global")
def update_global_config(global_config: GlobalConfig) -> GlobalConfig:
    config = load_config()
    config.global_config = global_config
    save_config(config)
    return global_config


@router.get("/sites")
def list_sites() -> list[SiteConfig]:
    config = load_config()
    return config.sites


@router.get("/sites/{site_id}")
def get_site(site_id: str) -> SiteConfig:
    config = load_config()
    site = get_site_by_id(config, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")
    return site


@router.post("/sites")
def create_site(site: SiteConfig) -> SiteConfig:
    config = load_config()
    if get_site_by_id(config, site.id) is not None:
        raise HTTPException(status_code=409, detail=f"Site '{site.id}' already exists")
    config.sites.append(site)
    save_config(config)
    return site


@router.put("/sites/{site_id}")
def update_site(site_id: str, site: SiteConfig) -> SiteConfig:
    config = load_config()
    for i, s in enumerate(config.sites):
        if s.id == site_id:
            site.id = site_id
            config.sites[i] = site
            save_config(config)
            return site
    raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")


@router.delete("/sites/{site_id}")
def delete_site(site_id: str) -> dict:
    config = load_config()
    for i, s in enumerate(config.sites):
        if s.id == site_id:
            config.sites.pop(i)
            save_config(config)
            return {"message": f"Site '{site_id}' deleted"}
    raise HTTPException(status_code=404, detail=f"Site '{site_id}' not found")
