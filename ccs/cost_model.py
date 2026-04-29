"""Simulated cost model utilities.

The rates in this module are pedagogical estimates for teaching. They are not
connected to real cloud, hardware, or API billing.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_COST_CONFIG: dict[str, Any] = {
    "runtime": {
        "cpu_second": 0.002,
        "gpu_second": 0.025,
        "memory_gb_second": 0.0004,
        "storage_mb": 0.00001,
    },
    "llm": {
        "small": {"input_token": 0.000001, "output_token": 0.000002},
        "medium": {"input_token": 0.00001, "output_token": 0.00002},
        "large": {"input_token": 0.00005, "output_token": 0.0001},
    },
}


def load_cost_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load a simulated cost configuration.

    With no path, this returns a copy of :data:`DEFAULT_COST_CONFIG`. When a
    path is supplied, it should point to a JSON file with optional ``runtime``
    and ``llm`` sections. Supplied values override the defaults.
    """
    config = deepcopy(DEFAULT_COST_CONFIG)
    if path is None:
        return config

    with Path(path).open("r", encoding="utf-8") as f:
        user_config = json.load(f)

    for section in ("runtime", "llm"):
        if section in user_config:
            config[section].update(user_config[section])
    return config


def estimate_runtime_cost(
    runtime_seconds: float,
    gpu_used: bool = False,
    memory_gb_seconds: float = 0,
    storage_mb: float = 0,
    config: dict[str, Any] | None = None,
) -> float:
    """Estimate a simulated cost for a timed compute action."""
    rates = (config or load_cost_config())["runtime"]
    cpu_cost = runtime_seconds * rates.get("cpu_second", 0.0)
    gpu_cost = runtime_seconds * rates.get("gpu_second", 0.0) if gpu_used else 0.0
    memory_cost = memory_gb_seconds * rates.get("memory_gb_second", 0.0)
    storage_cost = storage_mb * rates.get("storage_mb", 0.0)
    return round(cpu_cost + gpu_cost + memory_cost + storage_cost, 6)


def estimate_llm_cost(
    model_size: str,
    input_tokens: int,
    output_tokens: int,
    config: dict[str, Any] | None = None,
) -> float:
    """Estimate a simulated LLM cost from token counts."""
    llm_rates = (config or load_cost_config())["llm"]
    if model_size not in llm_rates:
        available = ", ".join(sorted(llm_rates))
        raise ValueError(
            f"Unknown model_size '{model_size}'. Expected one of: {available}."
        )

    rates = llm_rates[model_size]
    cost = (
        input_tokens * rates.get("input_token", 0.0)
        + output_tokens * rates.get("output_token", 0.0)
    )
    return round(cost, 6)


class CostModel:
    """Compatibility wrapper around the module-level cost functions."""

    def __init__(
        self,
        costs: dict[str, float] | None = None,
        llm_models: dict[str, dict[str, float]] | None = None,
    ) -> None:
        self.config = load_cost_config()
        if costs is not None:
            self.config["runtime"] = costs
        if llm_models is not None:
            self.config["llm"] = llm_models

    @classmethod
    def from_default_config(cls) -> "CostModel":
        return cls()

    def compute_runtime_cost(
        self,
        runtime_seconds: float,
        gpu_used: bool = False,
        memory_gb: float | None = None,
        storage_mb: float | None = None,
    ) -> float:
        memory_gb_seconds = runtime_seconds * memory_gb if memory_gb is not None else 0
        return estimate_runtime_cost(
            runtime_seconds=runtime_seconds,
            gpu_used=gpu_used,
            memory_gb_seconds=memory_gb_seconds,
            storage_mb=storage_mb or 0,
            config=self.config,
        )

    def compute_llm_cost(self, model_size: str, input_tokens: int, output_tokens: int) -> float:
        return estimate_llm_cost(model_size, input_tokens, output_tokens, config=self.config)
