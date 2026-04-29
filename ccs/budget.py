"""Budget tracking for simulated compute spending."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Budget:
    """Track simulated spending against a fixed teaching budget.

    Receipts are stored as plain dictionaries so students can inspect and edit
    them easily in a notebook.
    """

    total: float
    spent: float = 0.0
    receipts: list[dict[str, Any]] = field(default_factory=list)
    warn_at: float = 0.8

    def add_receipt(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Add a receipt and annotate it with budget status fields."""
        cost = float(receipt.get("cost", 0.0))
        self.spent = round(self.spent + cost, 6)
        receipt["budget_total"] = self.total
        receipt["budget_spent_after"] = self.spent
        receipt["budget_remaining_after"] = self.remaining()
        receipt["budget_warning"] = self.percent_spent() >= self.warn_at
        receipt["over_budget"] = self.is_over_budget()
        self.receipts.append(receipt)
        return receipt

    def remaining(self) -> float:
        """Return the simulated budget remaining."""
        return round(self.total - self.spent, 6)

    def percent_spent(self) -> float:
        """Return the fraction of the budget that has been spent."""
        if self.total == 0:
            return 1.0 if self.spent > 0 else 0.0
        return round(self.spent / self.total, 6)

    def is_over_budget(self) -> bool:
        """Return whether spending has exceeded the budget."""
        return self.spent > self.total

    def summary(self) -> dict[str, Any]:
        """Return a compact budget summary dictionary."""
        most_expensive = None
        if self.receipts:
            most_expensive = max(self.receipts, key=lambda r: float(r.get("cost", 0.0)))

        return {
            "budget_total": self.total,
            "spent": self.spent,
            "remaining": self.remaining(),
            "percent_spent": self.percent_spent(),
            "is_over_budget": self.is_over_budget(),
            "warning_threshold": self.warn_at,
            "warning": self.percent_spent() >= self.warn_at,
            "number_of_actions": len(self.receipts),
            "most_expensive_action": most_expensive,
        }

    def to_json(self, path: str | Path) -> None:
        """Write the budget summary and receipts to a JSON file."""
        data = {"summary": self.summary(), "receipts": self.receipts}
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def to_csv(self, path: str | Path) -> None:
        """Write receipts to a CSV file for spreadsheet inspection."""
        fieldnames = sorted({key for receipt in self.receipts for key in receipt})
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.receipts)
