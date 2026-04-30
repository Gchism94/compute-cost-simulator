"""Intro demo: compare simulated model training costs.

This example uses sleep() instead of real ML libraries so students can focus on
the cost-performance tradeoff rather than setup or syntax.
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


def dollars(value: float) -> str:
    return f"${value:.4f}"


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


budget = Budget(total=5.00)

experiments = [
    {
        "task": "train logistic regression",
        "model": "logistic_regression",
        "seconds": 0.25,
        "f1": 0.64,
        "gpu_used": False,
    },
    {
        "task": "train random forest",
        "model": "random_forest",
        "seconds": 0.75,
        "f1": 0.69,
        "gpu_used": False,
    },
    {
        "task": "train neural network",
        "model": "neural_network",
        "seconds": 1.00,
        "f1": 0.72,
        "gpu_used": True,
    },
]

for experiment in experiments:
    with compute_block(
        task=experiment["task"],
        category="modeling",
        model=experiment["model"],
        budget=budget,
        metric_name="f1",
        metric_value=experiment["f1"],
        gpu_used=experiment["gpu_used"],
        log_path=LOG_PATH,
    ):
        sleep(experiment["seconds"])

print("Compute Cost Simulator: Modeling Demo")
print("======================================")
print()
print(f"{'Model':20} {'F1':>5} {'Cost':>10} {'Runtime':>10} {'GPU':>5}")
print("-" * 56)
for receipt in budget.receipts:
    print(
        f"{receipt['model']:20} "
        f"{receipt['metric_value']:>5.2f} "
        f"{dollars(receipt['cost']):>10} "
        f"{receipt['runtime_seconds']:>8.3f}s "
        f"{yes_no(receipt['gpu_used']):>5}"
    )

summary = budget.summary()
cheapest = min(budget.receipts, key=lambda r: r["cost"])
best_f1 = max(budget.receipts, key=lambda r: r["metric_value"])
extra_cost = best_f1["cost"] - cheapest["cost"]
extra_f1 = best_f1["metric_value"] - cheapest["metric_value"]

print("\nBudget Summary")
print("--------------")
print(
    f"You started with {dollars(summary['budget_total'])} and spent "
    f"{dollars(summary['spent'])} across {summary['number_of_actions']} "
    f"simulated model runs."
)
print(
    f"You have {dollars(summary['remaining'])} remaining "
    f"({summary['percent_spent']:.1%} of the budget used)."
)

print("\nYour takeaways")
print("--------------")
print(f"Cheapest model: {cheapest['model']} at {dollars(cheapest['cost'])}.")
print(f"Best F1 score: {best_f1['model']} with F1={best_f1['metric_value']:.2f}.")
print(
    f"Compared with the cheapest model, the best-performing model gained "
    f"{extra_f1:.2f} F1 points and cost {dollars(extra_cost)} more."
)
print(
    "That gain may be worth it if the extra accuracy matters for the task, but "
    "the cheaper model is easier to justify when the goal is a strong result "
    "under a tight simulated budget."
)
