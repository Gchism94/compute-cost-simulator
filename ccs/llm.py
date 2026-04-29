"""Helpers for simulated LLM token costs."""

from __future__ import annotations

from typing import Any

from .budget import Budget
from .cost_model import CostModel


def track_llm_call(
    task: str,
    model_size: str,
    input_tokens: int,
    output_tokens: int,
    budget: Budget | None = None,
    category: str = "llm",
    cost_model: CostModel | None = None,
) -> dict[str, Any]:
    """Create a simulated receipt for an LLM call."""
    cm = cost_model or CostModel.from_default_config()
    cost = cm.compute_llm_cost(model_size, input_tokens, output_tokens)
    receipt = {
        "task": task,
        "category": category,
        "model": model_size,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost,
    }
    if budget is not None:
        budget.add_receipt(receipt)
    return receipt
