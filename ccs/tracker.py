"""Runtime tracking context manager."""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .budget import Budget
from .cost_model import CostModel, estimate_runtime_cost


def _append_jsonl(receipt: dict[str, Any], log_path: str | Path) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt) + "\n")


@contextmanager
def compute_block(
    task: str,
    category: str = "general",
    model: str | None = None,
    budget: Budget | None = None,
    metric_name: str | None = None,
    metric_value: float | None = None,
    gpu_used: bool = False,
    memory_gb_seconds: float = 0,
    storage_mb: float = 0,
    log_path: str | Path | None = None,
    config: dict[str, Any] | None = None,
    cost_model: CostModel | None = None,
    memory_gb: float | None = None,
    log: bool | None = None,
    log_dir: str | Path | None = None,
) -> Iterator[dict[str, Any]]:
    """Track a block of code and create a simulated compute receipt.

    Pass ``budget`` to store the receipt on a ``Budget``. Pass ``log_path`` to
    append the receipt to a JSONL file that can later be summarized or loaded
    in the optional dashboard.
    """
    receipt: dict[str, Any] = {
        "task": task,
        "category": category,
        "model": model,
        "gpu_used": gpu_used,
        "metric_name": metric_name,
        "metric_value": metric_value,
    }
    start = time.perf_counter()
    try:
        yield receipt
    finally:
        runtime_seconds = time.perf_counter() - start
        effective_memory_gb_seconds = memory_gb_seconds
        if memory_gb is not None and memory_gb_seconds == 0:
            effective_memory_gb_seconds = runtime_seconds * memory_gb

        if cost_model is not None:
            cost = cost_model.compute_runtime_cost(
                runtime_seconds=runtime_seconds,
                gpu_used=gpu_used,
                memory_gb=memory_gb,
                storage_mb=storage_mb,
            )
        else:
            cost = estimate_runtime_cost(
                runtime_seconds=runtime_seconds,
                gpu_used=gpu_used,
                memory_gb_seconds=effective_memory_gb_seconds,
                storage_mb=storage_mb,
                config=config,
            )

        receipt.update(
            {
                "runtime_seconds": round(runtime_seconds, 6),
                "memory_gb_seconds": round(effective_memory_gb_seconds, 6),
                "storage_mb": storage_mb,
                "cost": cost,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        if metric_name and metric_value not in (None, 0):
            receipt["cost_per_metric"] = round(cost / float(metric_value), 6)
        else:
            receipt["cost_per_metric"] = None

        if budget is not None:
            budget.add_receipt(receipt)

        if log_path is not None:
            _append_jsonl(receipt, log_path)
        elif log and log_dir is not None:
            _append_jsonl(receipt, Path(log_dir) / "receipts.jsonl")
