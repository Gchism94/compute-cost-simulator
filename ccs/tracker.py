"""Runtime tracking context manager."""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .budget import Budget
from .cost_model import CostModel


def _write_receipt(receipt: dict[str, Any], log_dir: str | Path = "ccs_logs") -> None:
    """Append receipts to JSONL and CSV files."""
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)

    jsonl_path = path / "receipts.jsonl"
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt) + "\n")

    csv_path = path / "receipts.csv"
    fields = sorted(receipt.keys())
    write_header = not csv_path.exists()
    import csv

    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(receipt)


@contextmanager
def compute_block(
    task: str,
    category: str = "general",
    model: str | None = None,
    budget: Budget | None = None,
    gpu_used: bool = False,
    memory_gb: float | None = None,
    storage_mb: float | None = None,
    metric_name: str | None = None,
    metric_value: float | None = None,
    cost_model: CostModel | None = None,
    log: bool = True,
    log_dir: str | Path = "ccs_logs",
) -> Iterator[dict[str, Any]]:
    """Track a block of code and produce a simulated computational receipt."""
    cm = cost_model or CostModel.from_default_config()
    receipt: dict[str, Any] = {
        "task": task,
        "category": category,
        "model": model,
        "gpu_used": gpu_used,
        "metric_name": metric_name,
        "metric_value": metric_value,
    }
    start = time.perf_counter()
    yield receipt
    runtime = time.perf_counter() - start
    cost = cm.compute_runtime_cost(runtime, gpu_used, memory_gb, storage_mb)
    receipt.update(
        {
            "runtime_seconds": round(runtime, 6),
            "memory_gb": memory_gb,
            "storage_mb": storage_mb,
            "cost": cost,
        }
    )
    if metric_name and metric_value not in (None, 0):
        receipt["cost_per_metric"] = round(cost / float(metric_value), 6)
    if budget is not None:
        budget.add_receipt(receipt)
    if log:
        _write_receipt(receipt, log_dir=log_dir)
