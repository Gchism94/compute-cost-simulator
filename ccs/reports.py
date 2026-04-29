"""Summary reporting helpers."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_receipts(receipts: list[dict[str, Any]] | str | Path) -> list[dict[str, Any]]:
    """Return receipts from an in-memory list or JSONL path."""
    if isinstance(receipts, list):
        return receipts

    loaded: list[dict[str, Any]] = []
    with Path(receipts).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                loaded.append(json.loads(line))
    return loaded


def summarize_logs(receipts: list[dict[str, Any]] | str | Path) -> dict[str, Any]:
    """Summarize simulated cost receipts.

    ``receipts`` may be either a list of receipt dictionaries or a path to a
    JSONL file created with ``log_path``.
    """
    loaded = _load_receipts(receipts)
    total_cost = round(sum(float(r.get("cost", 0.0)) for r in loaded), 6)
    most_expensive = None
    if loaded:
        most_expensive = max(loaded, key=lambda r: float(r.get("cost", 0.0)))

    cost_by_category: dict[str, float] = defaultdict(float)
    cost_by_model: dict[str, float] = defaultdict(float)
    for receipt in loaded:
        category = str(receipt.get("category") or "uncategorized")
        model = str(receipt.get("model") or "unknown")
        cost = float(receipt.get("cost", 0.0))
        cost_by_category[category] += cost
        cost_by_model[model] += cost

    number_of_actions = len(loaded)
    average_cost = total_cost / number_of_actions if number_of_actions else 0.0
    return {
        "total_cost": total_cost,
        "number_of_actions": number_of_actions,
        "most_expensive_action": most_expensive,
        "cost_by_category": {
            key: round(value, 6) for key, value in cost_by_category.items()
        },
        "cost_by_model": {key: round(value, 6) for key, value in cost_by_model.items()},
        "average_cost": round(average_cost, 6),
    }


def cost_by_category(receipts: list[dict[str, Any]]) -> dict[str, float]:
    """Backward-compatible helper for category totals."""
    return summarize_logs(receipts)["cost_by_category"]
