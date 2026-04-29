"""Scaling inference demo: small per-request costs add up at volume.

The model calls are simulated with sleep(). The point is to show that a workflow
that looks inexpensive for a few records can become expensive for a class,
clinic, or production-size batch.
"""

from time import sleep

from ccs import Budget, compute_block


CLASSROOM_COST_CONFIG = {
    "runtime": {
        "cpu_second": 0.05,
        "gpu_second": 0.35,
        "memory_gb_second": 0.0,
        "storage_mb": 0.0,
    },
    "llm": {},
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


budget = Budget(total=0.30)
seconds_per_prediction = 0.002
volumes = [10, 100, 500]

print("Compute Cost Simulator: Scaling Inference Demo")
print("===============================================")
print("One prediction is tiny. Many predictions can burn through a budget.")

print("\nInference batches")
print("-----------------")
print(f"{'Records':>8} {'Estimated':>10} {'Actual':>10} {'Runtime':>10} {'Remaining':>10}")
print("-" * 56)

for records in volumes:
    estimated_cost = records * seconds_per_prediction * (
        CLASSROOM_COST_CONFIG["runtime"]["cpu_second"]
        + CLASSROOM_COST_CONFIG["runtime"]["gpu_second"]
    )

    with compute_block(
        task=f"run inference for {records} records",
        category="inference",
        model="batch_classifier",
        budget=budget,
        metric_name="records",
        metric_value=records,
        gpu_used=True,
        config=CLASSROOM_COST_CONFIG,
    ):
        sleep(records * seconds_per_prediction)

    receipt = budget.receipts[-1]
    print(
        f"{records:>8} "
        f"{dollars(estimated_cost):>10} "
        f"{dollars(receipt['cost']):>10} "
        f"{receipt['runtime_seconds']:>8.3f}s "
        f"{dollars(receipt['budget_remaining_after']):>10}"
    )

summary = budget.summary()
most_expensive = summary["most_expensive_action"]

print("\nBudget summary")
print("--------------")
print(f"Started with: {dollars(summary['budget_total'])}")
print(f"Spent: {dollars(summary['spent'])}")
print(f"Remaining: {dollars(summary['remaining'])}")
print(f"Actions tracked: {summary['number_of_actions']}")
print(f"Most expensive action: {most_expensive['task']} ({dollars(most_expensive['cost'])})")

print("\nWhat students should notice")
print("---------------------------")
print("Cost scales with volume: 500 records cost much more than 10 records.")
print("The estimated and actual costs are close because both use the same rate model.")
print(
    "Before running inference on a full dataset, estimate the batch cost from a "
    "small sample and check whether the remaining budget can cover the scale-up."
)
