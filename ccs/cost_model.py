"""Cost model utilities for simulated compute pricing."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from typing import Any

import yaml


@dataclass
class CostModel:
    """Convert resource usage into simulated pedagogical costs."""

    costs: dict[str, float] = field(default_factory=dict)
    llm_models: dict[str, dict[str, float]] = field(default_factory=dict)

    @classmethod
    def from_default_config(cls) -> "CostModel":
        """Load the default cost model from ``config.yaml``."""
        with resources.files("ccs").joinpath("config.yaml").open("r", encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return cls(costs=data.get("costs", {}), llm_models=data.get("llm_models", {}))

    def compute_runtime_cost(
        self,
        runtime_seconds: float,
        gpu_used: bool = False,
        memory_gb: float | None = None,
        storage_mb: float | None = None,
    ) -> float:
        """Estimate simulated cost from runtime and optional resource proxies."""
        cpu_cost = runtime_seconds * self.costs.get("cpu_second", 0.0)
        gpu_cost = runtime_seconds * self.costs.get("gpu_second", 0.0) if gpu_used else 0.0
        memory_cost = (
            runtime_seconds * memory_gb * self.costs.get("memory_gb_second", 0.0)
            if memory_gb is not None
            else 0.0
        )
        storage_cost = (
            storage_mb * self.costs.get("storage_mb", 0.0) if storage_mb is not None else 0.0
        )
        return round(cpu_cost + gpu_cost + memory_cost + storage_cost, 6)

    def compute_llm_cost(self, model_size: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate simulated LLM cost from input and output token counts."""
        if model_size not in self.llm_models:
            raise ValueError(f"Unknown model_size '{model_size}'.")
        rates = self.llm_models[model_size]
        cost = input_tokens * rates["input_token"] + output_tokens * rates["output_token"]
        return round(cost, 6)
