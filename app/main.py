from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import config, subscriptions

app = FastAPI(
    title="Subscription Link Getter",
    description="API for fetching subscription links from various providers",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(subscriptions.router)


@app.get("/")
def root():
    return {"message": "Subscription Link Getter API", "docs": "/docs"}
