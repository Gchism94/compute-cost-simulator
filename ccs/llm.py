"""Helpers for simulated LLM token costs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .budget import Budget
from .cost_model import estimate_llm_cost


def _append_jsonl(receipt: dict[str, Any], log_path: str | Path) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt) + "\n")


def track_llm_call(
    task: str,
    model_size: str,
    input_tokens: int,
    output_tokens: int,
    budget: Budget | None = None,
    category: str = "llm",
    model: str | None = None,
    log_path: str | Path | None = None,
    config: dict[str, Any] | None = None,
    estimated_cost: float | None = None,
) -> dict[str, Any]:
    """Create a simulated receipt for an LLM call.

    ``model_size`` selects one of the configured teaching-rate tiers. ``model``
    can be used as a display name when a course wants labels such as
    ``draft_model`` or ``review_model`` instead of ``small``/``medium``/``large``.
    """
    if budget is not None and estimated_cost is not None:
        budget.check_affordable(estimated_cost)

    cost = estimate_llm_cost(model_size, input_tokens, output_tokens, config=config)
    receipt = {
        "task": task,
        "category": category,
        "model": model or model_size,
        "model_size": model_size,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if budget is not None:
        budget.add_receipt(receipt)
    if log_path is not None:
        _append_jsonl(receipt, log_path)
    return receipt
