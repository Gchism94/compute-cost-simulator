"""Hyperparameter explosion demo: repeated runs compound quickly.

This script uses short sleep() calls instead of real model training. The cost
configuration is intentionally scaled up for teaching so a small grid search
can visibly consume a small budget.
"""

import os
import sys
from pathlib import Path
from time import sleep

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ccs import Budget, compute_block


LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "ccs_session.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)


CLASSROOM_COST_CONFIG = {
    "runtime": {
        "cpu_second": 0.08,
        "gpu_second": 0.60,
        "memory_gb_second": 0.0,
        "storage_mb": 0.0,
    },
    "llm": {},
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


budget = Budget(total=0.40)
learning_rates = [0.01, 0.05, 0.10]
tree_depths = [3, 6, 9, 12]
seconds_per_run = 0.05

planned_runs = len(learning_rates) * len(tree_depths)
estimated_cost_per_run = seconds_per_run * (
    CLASSROOM_COST_CONFIG["runtime"]["cpu_second"]
    + CLASSROOM_COST_CONFIG["runtime"]["gpu_second"]
)
estimated_total = planned_runs * estimated_cost_per_run

print("Compute Cost Simulator: Hyperparameter Explosion")
print("=================================================")
print(f"Planned runs: {planned_runs}")
print(f"Estimated cost per run: {dollars(estimated_cost_per_run)}")
print(f"Estimated full grid cost: {dollars(estimated_total)}")
print(f"Budget: {dollars(budget.total)}")

print("\nRun table")
print("---------")
print(f"{'Run':>3} {'Learning rate':>14} {'Depth':>6} {'F1':>5} {'Cost':>8} {'Remaining':>10}")
print("-" * 58)

run_number = 0
for learning_rate in learning_rates:
    for depth in tree_depths:
        run_number += 1
        fake_f1 = 0.61 + (0.015 * depth / 3) - abs(learning_rate - 0.05)
        with compute_block(
            task=f"grid search run {run_number}",
            category="modeling",
            model=f"lr={learning_rate}, depth={depth}",
            budget=budget,
            metric_name="f1",
            metric_value=round(fake_f1, 3),
            gpu_used=True,
            config=CLASSROOM_COST_CONFIG,
            log_path=LOG_PATH,
        ):
            sleep(seconds_per_run)

        receipt = budget.receipts[-1]
        print(
            f"{run_number:>3} "
            f"{learning_rate:>14.2f} "
            f"{depth:>6} "
            f"{receipt['metric_value']:>5.3f} "
            f"{dollars(receipt['cost']):>8} "
            f"{dollars(receipt['budget_remaining_after']):>10}"
        )

summary = budget.summary()
best_run = max(budget.receipts, key=lambda r: r["metric_value"])

print("\nBudget summary")
print("--------------")
print(f"Started with: {dollars(summary['budget_total'])}")
print(f"Estimated full grid cost: {dollars(estimated_total)}")
print(f"Actual spent: {dollars(summary['spent'])}")
print(f"Remaining: {dollars(summary['remaining'])}")
print(f"Actions tracked: {summary['number_of_actions']}")
print(f"Best observed run: {best_run['model']} with F1={best_run['metric_value']:.3f}")

print("\nWhat to notice")
print("--------------")
print("A grid search multiplies options: 3 learning rates x 4 depths = 12 runs.")
print("Each run seems cheap alone, but repeated runs compound into a large total.")
print(
    "Before launching a full grid, estimate the total cost and ask whether a "
    "smaller search would answer the same question."
)
