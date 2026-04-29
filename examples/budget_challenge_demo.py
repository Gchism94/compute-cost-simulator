"""Budget challenge demo: choose a workflow under a simulated $5 budget.

Students can edit the approaches below and defend a final choice using both
performance and cost. No real model training happens here; sleep() stands in
for compute time.
"""

import os
from time import sleep

from ccs import Budget, compute_block, track_llm_call


LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "ccs_session.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)


def dollars(value: float) -> str:
    return f"${value:.4f}"


def summary_dollars(value: float) -> str:
    return f"${value:.2f}"


def print_budget_summary(summary: dict) -> None:
    most_expensive = summary["most_expensive_action"]
    print(f"Started with: {summary_dollars(summary['budget_total'])}")
    print(f"Spent: {summary_dollars(summary['spent'])}")
    print(f"Remaining: {summary_dollars(summary['remaining'])}")
    print(f"Actions tracked: {summary['number_of_actions']}")
    print(
        "Most expensive action: "
        f"{most_expensive['task']} ({summary_dollars(most_expensive['cost'])})"
    )


budget = Budget(total=5.00)

modeling_approaches = [
    {
        "task": "baseline rules plus logistic regression",
        "model": "logistic_regression",
        "seconds": 0.20,
        "f1": 0.62,
        "gpu_used": False,
    },
    {
        "task": "feature engineering plus random forest",
        "model": "random_forest",
        "seconds": 0.80,
        "f1": 0.70,
        "gpu_used": False,
    },
    {
        "task": "deep model with embeddings",
        "model": "neural_network",
        "seconds": 1.20,
        "f1": 0.74,
        "gpu_used": True,
    },
]

for approach in modeling_approaches:
    with compute_block(
        task=approach["task"],
        category="modeling",
        model=approach["model"],
        budget=budget,
        metric_name="f1",
        metric_value=approach["f1"],
        gpu_used=approach["gpu_used"],
        log_path=LOG_PATH,
    ):
        sleep(approach["seconds"])

# A realistic workflow may include both modeling and LLM assistance. Here the
# LLM call represents using a model to summarize errors before choosing what to
# improve next.
llm_receipt = track_llm_call(
    task="summarize model errors for revision plan",
    model_size="medium",
    input_tokens=1000,
    output_tokens=250,
    budget=budget,
    log_path=LOG_PATH,
)
llm_receipt["quality_score"] = 0.82

print("\nBudget challenge results")
print("------------------------")
for receipt in budget.receipts:
    if receipt["category"] == "modeling":
        print(
            f"{receipt['model']:20} "
            f"f1={receipt['metric_value']:.2f} "
            f"cost={dollars(receipt['cost'])} "
            f"cost_per_f1={dollars(receipt['cost_per_metric'])}"
        )
    else:
        print(
            f"{receipt['model']:20} "
            f"quality={receipt['quality_score']:.2f} "
            f"tokens={receipt['total_tokens']} "
            f"cost={dollars(receipt['cost'])}"
        )

model_receipts = [r for r in budget.receipts if r["category"] == "modeling"]
best_f1 = max(model_receipts, key=lambda r: r["metric_value"])
best_value = min(model_receipts, key=lambda r: r["cost_per_metric"])

print("\nWhat to notice")
print("--------------")
print(
    f"The top model is {best_f1['model']} with f1={best_f1['metric_value']:.2f}, "
    f"but it costs {dollars(best_f1['cost'])}."
)
print(
    f"The strongest value choice is {best_value['model']} at "
    f"{dollars(best_value['cost_per_metric'])} per F1 point."
)
print(
    "A defensible final choice should explain whether a small performance gain is "
    "worth the extra simulated compute spend."
)

print("\nBudget summary")
print("--------------")
summary = budget.summary()
print_budget_summary(summary)
