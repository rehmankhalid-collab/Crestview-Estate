import json
from functools import lru_cache
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parent.parent / "data" / "content.json"


@lru_cache
def get_content() -> dict:
    """Static marketing copy for the landing page.

    Lives in data/content.json rather than the templates so property stats,
    floor plans, amenities, and gallery photo slots can be edited (or later
    swapped for a real CMS / admin-managed DB table) without touching HTML.
    """
    with CONTENT_PATH.open(encoding="utf-8") as f:
        return json.load(f)
