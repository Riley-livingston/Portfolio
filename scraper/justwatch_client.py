"""JustWatch GraphQL client for Disney+ catalog (no subscription required)."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from scraper.config import Settings

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://apis.justwatch.com/graphql"
DISNEY_PLUS_PACKAGE = "dnp"

CATALOG_QUERY = """
query GetDisneyPlusCatalog(
  $country: Country!
  $language: Language!
  $first: Int!
  $after: String
  $filter: OfferFilter!
) {
  popularTitles(
    country: $country
    filter: { packages: ["dnp"] }
    first: $first
    after: $after
    sortBy: POPULAR
  ) {
    totalCount
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        id
        objectType
        ... on Show {
          totalSeasonCount
        }
        content(country: $country, language: $language) {
          title
          originalReleaseYear
          originalReleaseDate
          runtime
          shortDescription
          fullPath
          genres {
            shortName
          }
          credits {
            role
            name
          }
          ... on MovieOrShowContent {
            ageCertification
            scoring {
              imdbScore
              imdbVotes
              tomatoMeter
              certifiedFresh
            }
          }
        }
        offers(country: $country, platform: WEB, filter: $filter) {
          monetizationType
          package {
            clearName
            shortName
          }
        }
      }
    }
  }
}
"""


class JustWatchClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = httpx.Client(
            timeout=60.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ),
                "Origin": "https://www.justwatch.com",
                "Referer": "https://www.justwatch.com/",
            },
        )

    def close(self) -> None:
        self.client.close()

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries):
            try:
                response = self.client.post(GRAPHQL_URL, json=payload)
                if response.status_code in (429, 500, 502, 503, 504):
                    wait = 2**attempt
                    logger.warning("HTTP %s from JustWatch — retry in %ss", response.status_code, wait)
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                data = response.json()
                if data.get("errors"):
                    raise RuntimeError(f"GraphQL errors: {data['errors']}")
                return data
            except (httpx.HTTPError, RuntimeError) as exc:
                last_error = exc
                wait = 2**attempt
                logger.warning("JustWatch request failed: %s — retry in %ss", exc, wait)
                time.sleep(wait)
        if last_error:
            raise last_error
        raise RuntimeError("JustWatch GraphQL request failed")

    def fetch_catalog_page(self, first: int = 100, after: str | None = None) -> dict[str, Any]:
        country = self.settings.justwatch_country
        variables = {
            "country": country,
            "language": self.settings.justwatch_language,
            "first": first,
            "after": after,
            "filter": {
                "packages": [DISNEY_PLUS_PACKAGE],
                "monetizationTypes": ["FLATRATE", "ADS", "FREE"],
            },
        }
        payload = {"query": CATALOG_QUERY, "variables": variables}
        data = self._request(payload)
        return data["data"]["popularTitles"]


def iter_catalog(client: JustWatchClient, settings: Settings, page_size: int = 100):
    """Yield all title nodes from JustWatch Disney+ catalog."""
    after = None
    total_yielded = 0
    total_available = None

    while True:
        time.sleep(settings.rate_limit_ms / 1000.0)
        page = client.fetch_catalog_page(first=page_size, after=after)
        total_available = page.get("totalCount", total_available)
        edges = page.get("edges") or []

        for edge in edges:
            node = edge.get("node")
            if node:
                yield node
                total_yielded += 1
                if settings.scrape_limit and total_yielded >= settings.scrape_limit:
                    logger.info(
                        "Reached SCRAPE_LIMIT=%s (total available on JustWatch: %s)",
                        settings.scrape_limit,
                        total_available,
                    )
                    return

        page_info = page.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        after = page_info.get("endCursor")
        if not after:
            break

    logger.info(
        "Fetched %s titles from JustWatch (total available: %s)",
        total_yielded,
        total_available,
    )
