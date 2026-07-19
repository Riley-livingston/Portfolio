"""Discover Disney+ content IDs via search API pagination."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from scraper.config import BASE_URL, Settings

logger = logging.getLogger(__name__)

SEARCH_QUERIES = list("abcdefghijklmnopqrstuvwxyz0123456789") + [
    "marvel",
    "star wars",
    "pixar",
    "disney",
    "nat geo",
    "hulu",
    "espn",
    "bluey",
    "simpson",
    "mandalorian",
    "frozen",
    "moana",
    "avengers",
    "documentary",
    "original",
]


class DisneyClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = httpx.Client(timeout=30.0, headers=settings.base_headers())

    def close(self) -> None:
        self.client.close()

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries):
            try:
                response = self.client.request(method, url, **kwargs)
                if response.status_code in (429, 500, 502, 503, 504):
                    wait = 2**attempt
                    logger.warning("HTTP %s for %s — retry in %ss", response.status_code, url, wait)
                    time.sleep(wait)
                    continue
                return response
            except httpx.HTTPError as exc:
                last_error = exc
                wait = 2**attempt
                logger.warning("Request error %s — retry in %ss", exc, wait)
                time.sleep(wait)
        if last_error:
            raise last_error
        raise RuntimeError(f"Failed request to {url}")

    def search(self, query: str, page: int = 1, page_size: int = 30) -> dict[str, Any]:
        region = self.settings.region_upper
        url = (
            f"{BASE_URL}/svc/search/v2/{region}/maturity/1850/language/en"
            f"/query/{httpx.QueryParams({'q': query})['q']}/pageSize/{page_size}/page/{page}"
        )
        response = self._request("GET", url)
        if response.status_code == 401:
            raise PermissionError(
                "Disney+ API returned 401. Set DISNEY_SESSION_TOKEN in .env "
                "(Bearer JWT from an authenticated disneyplus.com session)."
            )
        response.raise_for_status()
        return response.json()

    def fetch_video_bundle(self, encoded_family_id: str) -> dict[str, Any]:
        region = self.settings.region_upper
        url = (
            f"{BASE_URL}/svc/content/DmcVideoBundle/version/5.1/region/{region}"
            f"/audience/false/maturity/1850/language/en/encodedFamilyId/{encoded_family_id}"
        )
        response = self._request("GET", url)
        response.raise_for_status()
        payload = response.json()
        return payload.get("data", {}).get("DmcVideoBundle", payload)

    def fetch_series_bundle(self, encoded_series_id: str) -> dict[str, Any]:
        region = self.settings.region_upper
        url = (
            f"{BASE_URL}/svc/content/DmcSeriesBundle/version/5.1/region/{region}"
            f"/audience/false/maturity/1850/language/en/encodedSeriesId/{encoded_series_id}"
        )
        response = self._request("GET", url)
        response.raise_for_status()
        payload = response.json()
        return payload.get("data", {}).get("DmcSeriesBundle", payload)


def extract_hits(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "hits" in payload:
        return [item.get("hit", item) for item in payload.get("hits", []) if item]
    data = payload.get("data") or {}
    for key in ("search", "Search", "results"):
        block = data.get(key) or payload.get(key)
        if isinstance(block, dict) and "hits" in block:
            return [item.get("hit", item) for item in block.get("hits", []) if item]
    return []


def discover_content_ids(client: DisneyClient, settings: Settings) -> dict[str, dict[str, Any]]:
    """Return map of content_id -> discovery metadata."""
    discovered: dict[str, dict[str, Any]] = {}

    for query in SEARCH_QUERIES:
        page = 1
        while True:
            time.sleep(settings.rate_limit_ms / 1000.0)
            try:
                payload = client.search(query, page=page)
            except PermissionError:
                raise
            except httpx.HTTPError as exc:
                logger.error("Search failed for query=%r page=%s: %s", query, page, exc)
                break

            hits = extract_hits(payload)
            if not hits:
                break

            for hit in hits:
                family = hit.get("family") or {}
                content_id = (
                    hit.get("contentId")
                    or hit.get("encodedFamilyId")
                    or family.get("encodedFamilyId")
                    or hit.get("id")
                )
                if not content_id:
                    continue
                content_id = str(content_id)
                program_type = (hit.get("programType") or hit.get("type") or "movie").lower()
                discovered[content_id] = {
                    "content_id": content_id,
                    "program_type": program_type,
                    "hit": hit,
                }

            meta = payload.get("meta") or payload.get("data", {}).get("meta") or {}
            total_pages = meta.get("pageCount") or meta.get("totalPages") or 1
            if page >= total_pages:
                break
            page += 1

        if settings.scrape_limit and len(discovered) >= settings.scrape_limit:
            break

    logger.info("Discovered %s unique content IDs", len(discovered))
    return discovered
