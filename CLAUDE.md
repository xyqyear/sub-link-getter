# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sub-Link-Getter is a FastAPI backend service that automatically extracts subscription links from VPN/proxy provider websites. It handles automated login, captcha recognition (via OpenRouter API), Cloudflare challenge solving, and subscription URL extraction with caching.

## Development Commands

```bash
# Install dependencies
cmd.exe /c uv sync

# Run development server
cmd.exe /c uv run fastapi dev app/main.py

# Run with uvicorn directly
cmd.exe /c uv run uvicorn app.main:app --reload

# Add a package
cmd.exe /c uv add <package_name>
```

Note: Use `cmd.exe /c` prefix because this project runs in a WSL-mounted Windows directory.

## Architecture

### Core Flow
1. **Request** → `app/routers/subscriptions.py` receives fetch request
2. **Cache Check** → `app/cache.py` checks for valid cached data (24h TTL)
3. **Fetch** → `app/fetcher.py` orchestrates browser automation via Scrapling/Playwright
4. **Login** → Detects login form, fills credentials, solves captcha if needed
5. **Extract** → Uses CSS selectors to find subscription URL from page
6. **Validate** → Fetches URL content and validates against expected string
7. **Cache** → Stores result in cache.json

### Key Modules

| Module | Purpose |
|--------|---------|
| `app/main.py` | FastAPI app initialization, CORS, router registration |
| `app/config.py` | Pydantic models (GlobalConfig, SiteConfig, AppConfig), load/save functions |
| `app/fetcher.py` | SubscriptionFetcher class - login, captcha handling, URL extraction |
| `app/cache.py` | CacheEntry model, 24-hour TTL caching logic |
| `app/captcha.py` | OpenRouter API integration for captcha OCR using Gemini model |
| `app/routers/config.py` | CRUD endpoints for site configurations |
| `app/routers/subscriptions.py` | Subscription fetch endpoints with cache support |

### Configuration System

Runtime configuration stored in `config.json`:
- **GlobalConfig**: API keys, browser settings, timeouts
- **SiteConfig**: Per-site login selectors, credentials, extraction rules

See `references/config-writer-instructions.md` for detailed guide on creating site configurations.

### API Endpoints

**Configuration:**
- `GET/PUT /config/global` - Global settings
- `GET/POST /config/sites` - List/create sites
- `GET/PUT/DELETE /config/sites/{site_id}` - Site CRUD
- `GET /config/schema` - SiteConfig JSON schema

**Subscriptions:**
- `GET /subscriptions/{site_id}` - Get subscription content as plain text (uses cache)
- `POST /subscriptions/{site_id}/fetch` - Force fresh fetch, returns summary (name, url, content_length)

## Key Dependencies

- **FastAPI** - Web framework
- **Scrapling** - Stealth web scraping with Playwright
- **Pydantic** - Data validation
- **Browserforge** - Browser fingerprint generation

## Frontend

The `frontend/` directory contains a React-based web UI for managing site configurations.

### Frontend Commands

```bash
cd frontend

# Install dependencies
cmd.exe /c pnpm install

# Run development server (proxies /api to backend at localhost:8000)
cmd.exe /c pnpm dev

# Build for production
cmd.exe /c pnpm build
```

### Frontend Tech Stack

- **Vite** - Build tool
- **React** - UI framework
- **Tailwind CSS** - Styling
- **react-jsonschema-form (RJSF)** - Form generation from JSON schema
- **Monaco Editor** - JSON editing
- **React Router** - Client-side routing

### Frontend Structure

| Path | Purpose |
|------|---------|
| `src/api/` | API client for backend communication |
| `src/components/` | Reusable UI components (SiteList, SiteForm, JsonEditor, Layout) |
| `src/pages/` | Page components (HomePage, SiteEditPage, GlobalConfigPage) |
| `src/types/` | TypeScript type definitions |

### Features

- List all configured sites with subscription URLs
- Add/edit/delete site configurations via form or JSON editor
- Copy subscription URLs to clipboard
- Force refresh subscriptions
- Edit global configuration
