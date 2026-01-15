from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import config, subscriptions

api_app = FastAPI(
    title="Subscription Link Getter API",
    description="API for fetching subscription links from various providers",
    version="1.0.0",
    root_path="/api",
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_app.include_router(config.router)
api_app.include_router(subscriptions.router)

app = FastAPI(title="Subscription Link Getter")
app.mount("/api", api_app)

STATIC_PATH = Path("frontend") / "dist"

app.mount(
    "/assets",
    StaticFiles(directory=STATIC_PATH / "assets"),
    name="assets",
)


@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    file_path = STATIC_PATH / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(STATIC_PATH / "index.html")
