"""Budget tracking for simulated compute spending."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Budget:
    """Track simulated spending against a fixed student budget."""

    total: float
    receipts: list[dict[str, Any]] = field(default_factory=list)

    @property
    def spent(self) -> float:
        return round(sum(float(r.get("cost", 0.0)) for r in self.receipts), 6)

    @property
    def remaining(self) -> float:
        return round(self.total - self.spent, 6)

    def add_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Add a computational receipt and attach budget status metadata."""
        projected_remaining = self.remaining - float(receipt.get("cost", 0.0))
        receipt["budget_total"] = self.total
        receipt["budget_remaining_after"] = round(projected_remaining, 6)
        receipt["over_budget"] = projected_remaining < 0
        self.receipts.append(receipt)
        return receipt

    def summary(self) -> dict[str, Any]:
        """Return a compact budget summary."""
        most_expensive = None
        if self.receipts:
            most_expensive = max(self.receipts, key=lambda r: float(r.get("cost", 0.0)))
        return {
            "budget_total": self.total,
            "spent": self.spent,
            "remaining": self.remaining,
            "num_actions": len(self.receipts),
            "most_expensive_action": most_expensive,
        }
