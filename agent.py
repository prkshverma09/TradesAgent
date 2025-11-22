from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, TypedDict
from urllib import error, request

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

load_dotenv()

try:
    from valyu import Valyu as _ValyuClient
except ImportError:
    _ValyuClient = None


class ShopCandidate(TypedDict, total=False):
    name: str
    url: str
    content: str


class ShopContact(TypedDict, total=False):
    name: str
    phone: Optional[str]
    address: Optional[str]
    url: str


class AgentState(TypedDict, total=False):
    item: str
    location: str
    shops: List[ShopCandidate]
    final_results: List[ShopContact]


UK_POSTCODE_PATTERN = re.compile(r"^(GIR ?0AA|[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})$", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")


def is_valid_uk_postcode(value: str) -> bool:
    sanitized = value.strip().upper()
    return bool(UK_POSTCODE_PATTERN.match(sanitized))


def extract_phone_number(texts: List[str]) -> Optional[str]:
    for text in texts:
        if not text:
            continue
        match = PHONE_PATTERN.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_address(text: str) -> Optional[str]:
    if not text:
        return None
    match = UK_POSTCODE_PATTERN.search(text)
    if not match:
        return None
    start = max(0, match.start() - 80)
    end = min(len(text), match.end() + 80)
    snippet = text[start:end].strip()
    return snippet if snippet else None


class ValyuSearchClient:
    def __init__(self) -> None:
        self.client = None
        if _ValyuClient is not None:
            api_key = os.getenv("VALYU_API_KEY")
            if api_key:
                self.client = _ValyuClient(api_key)
            else:
                self.client = _ValyuClient()

    def search(self, item: str, postcode: str) -> List[ShopCandidate]:
        if self.client is None:
            raise RuntimeError("Valyu SDK is not available. Install the valyu package and set VALYU_API_KEY.")
        query = f"plumbing shops near {postcode} selling {item}"
        response = self.client.search(
            query,
            search_type="web",
            max_num_results=10,
            country_code="GB",
            category="plumbing supplies",
            is_tool_call=True,
        )
        if hasattr(response, "success") and not getattr(response, "success"):
            detail = getattr(response, "error", "Valyu search failed")
            raise RuntimeError(str(detail))
        results: List[ShopCandidate] = []
        for entry in getattr(response, "results", []) or []:
            title = getattr(entry, "title", "") or ""
            url = getattr(entry, "url", "") or ""
            content = getattr(entry, "content", "") or getattr(entry, "description", "") or ""
            results.append({"name": title or url, "url": url, "content": content})
        return results


class FirecrawlScraper:
    BASE_URL = "https://api.firecrawl.dev/v1/scrape"

    def __init__(self) -> None:
        self.api_key = os.getenv("FIRECRAWL_API_KEY")

    def scrape_text(self, url: str) -> str:
        if not self.api_key:
            return ""
        payload = json.dumps({"url": url, "formats": ["markdown", "html"]}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"ApiKey key={self.api_key}",
        }
        req = request.Request(self.BASE_URL, data=payload, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode("utf-8")
        except error.URLError:
            return ""
        try:
            response = json.loads(body)
        except json.JSONDecodeError:
            return ""
        if isinstance(response, dict):
            if response.get("success") is False:
                return ""
            direct = response.get("content")
            if isinstance(direct, str):
                return direct
            data = response.get("data")
            if isinstance(data, dict):
                for key in ("markdown", "content", "html", "text"):
                    value = data.get(key)
                    if isinstance(value, str):
                        return value
        return ""


VALYU_CLIENT = ValyuSearchClient()
FIRECRAWL_SCRAPER = FirecrawlScraper()


def search_shops(state: AgentState) -> AgentState:
    item = state.get("item", "").strip()
    postcode = state.get("location", "").strip().upper()
    if not item:
        raise ValueError("Item is required.")
    if not is_valid_uk_postcode(postcode):
        raise ValueError("Location must be a valid UK postcode.")
    shops = VALYU_CLIENT.search(item, postcode)
    next_state = dict(state)
    next_state["location"] = postcode
    next_state["shops"] = shops
    return next_state


def extract_contact_info(state: AgentState) -> AgentState:
    shops = state.get("shops", [])
    results: List[ShopContact] = []
    for candidate in shops:
        texts = [candidate.get("content", "")]
        phone = extract_phone_number(texts)
        address = extract_address(texts[0] if texts else "")
        if (not phone or not address) and candidate.get("url"):
            scraped = FIRECRAWL_SCRAPER.scrape_text(candidate["url"])
            if scraped:
                texts.append(scraped)
                if not phone:
                    phone = extract_phone_number(texts)
                if not address:
                    address = extract_address(scraped)
        results.append(
            {
                "name": candidate.get("name", ""),
                "phone": phone,
                "address": address,
                "url": candidate.get("url", ""),
            }
        )
    next_state = dict(state)
    next_state["final_results"] = results
    return next_state


def save_results(state: AgentState) -> AgentState:
    results = state.get("final_results", [])
    with open("plumbing_shops.json", "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    return state


graph = StateGraph(AgentState)
graph.add_node("search", search_shops)
graph.add_node("extract", extract_contact_info)
graph.add_node("save", save_results)
graph.add_edge(START, "search")
graph.add_edge("search", "extract")
graph.add_edge("extract", "save")
graph.add_edge("save", END)
workflow = graph.compile()


def run_agent(item: str, location: str) -> AgentState:
    return workflow.invoke({"item": item, "location": location})


__all__ = ["run_agent", "workflow", "AgentState"]

