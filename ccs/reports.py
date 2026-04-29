"""Summary reporting helpers."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def cost_by_category(receipts: list[dict[str, Any]]) -> dict[str, float]:
    """Summarize cost by receipt category."""
    totals: dict[str, float] = defaultdict(float)
    for receipt in receipts:
        totals[str(receipt.get("category", "uncategorized"))] += float(receipt.get("cost", 0.0))
    return {key: round(value, 6) for key, value in totals.items()}
