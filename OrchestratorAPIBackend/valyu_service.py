"""
Valyu search service for finding stores near a location.
Extracted from TradesAgent project.
"""
import os
import re
from typing import List, Optional, TypedDict
from dotenv import load_dotenv

load_dotenv()

try:
    from valyu import Valyu as ValyuClient
except ImportError:
    ValyuClient = None


class StoreResult(TypedDict, total=False):
    """Single store search result from Valyu"""
    name: str
    url: str
    content: str


class ValyuSearchService:
    """Service for searching stores using Valyu API"""

    # UK postcode validation pattern
    UK_POSTCODE_PATTERN = re.compile(
        r"^(GIR ?0AA|[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})$",
        re.IGNORECASE
    )

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Valyu search client.

        Args:
            api_key: Valyu API key. If not provided, will use VALYU_API_KEY from environment.
        """
        self.client = None

        if ValyuClient is None:
            raise RuntimeError(
                "Valyu SDK is not available. "
                "Install it with: pip install valyu"
            )

        # Get API key from parameter or environment
        key = api_key or os.getenv("VALYU_API_KEY")
        if not key:
            raise RuntimeError(
                "VALYU_API_KEY is required. "
                "Set it in your .env file or pass it to the constructor."
            )

        self.client = ValyuClient(key)

    @classmethod
    def is_valid_uk_postcode(cls, postcode: str) -> bool:
        """
        Validate UK postcode format.

        Args:
            postcode: Postcode string to validate

        Returns:
            True if valid UK postcode, False otherwise
        """
        sanitized = postcode.strip().upper()
        return bool(cls.UK_POSTCODE_PATTERN.match(sanitized))

    def search_stores(
        self,
        part_to_acquire: str,
        location_postcode: str,
        max_results: int = 10
    ) -> List[StoreResult]:
        """
        Search for stores selling a specific part near a UK postcode.

        Args:
            part_to_acquire: Item/part to search for
            location_postcode: UK postcode for location
            max_results: Maximum number of results to return (default: 10)

        Returns:
            List of store results with name, url, and content

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If Valyu API call fails
        """
        if not part_to_acquire or not part_to_acquire.strip():
            raise ValueError("part_to_acquire is required and cannot be empty")

        postcode = location_postcode.strip().upper()
        if not self.is_valid_uk_postcode(postcode):
            raise ValueError(
                f"Invalid UK postcode: {location_postcode}. "
                "Must be a valid UK postcode format (e.g., 'SW1A 1AA', 'E1 6AN')"
            )

        # Build search query
        query = f"plumbing shops near {postcode} selling {part_to_acquire}"

        # Call Valyu API
        try:
            response = self.client.search(
                query,
                search_type="web",
                max_num_results=max_results,
                country_code="GB",
                category="plumbing supplies",
                is_tool_call=True,
            )
        except Exception as e:
            raise RuntimeError(f"Valyu API error: {str(e)}")

        # Check for API errors
        if hasattr(response, "success") and not getattr(response, "success"):
            error_detail = getattr(response, "error", "Valyu search failed")
            raise RuntimeError(f"Valyu search failed: {error_detail}")

        # Parse results
        results: List[StoreResult] = []
        for entry in getattr(response, "results", []) or []:
            title = getattr(entry, "title", "") or ""
            url = getattr(entry, "url", "") or ""
            content = (
                getattr(entry, "content", "") or
                getattr(entry, "description", "") or
                ""
            )

            results.append({
                "name": title or url,
                "url": url,
                "content": content
            })

        return results
