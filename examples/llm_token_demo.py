"""LLM token demo: compare simulated prompt costs.

The quality scores are fake but realistic enough for a classroom discussion.
You should notice that larger models cost more, and the extra quality may
or may not justify the extra simulated spend.
"""

import os

from ccs import Budget, track_llm_call


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


budget = Budget(total=2.00)

calls = [
    {
        "model_size": "small",
        "input_tokens": 900,
        "output_tokens": 180,
        "quality": 0.72,
    },
    {
        "model_size": "medium",
        "input_tokens": 1200,
        "output_tokens": 300,
        "quality": 0.84,
    },
    {
        "model_size": "large",
        "input_tokens": 1500,
        "output_tokens": 420,
        "quality": 0.89,
    },
]

for call in calls:
    receipt = track_llm_call(
        task=f"summarize clinical note with {call['model_size']} model",
        model_size=call["model_size"],
        input_tokens=call["input_tokens"],
        output_tokens=call["output_tokens"],
        budget=budget,
        log_path=LOG_PATH,
    )
    receipt["quality_score"] = call["quality"]
    receipt["cost_per_quality"] = round(receipt["cost"] / call["quality"], 6)

print("\nLLM comparison")
print("--------------")
for receipt in budget.receipts:
    print(
        f"{receipt['model_size']:6} "
        f"tokens={receipt['total_tokens']:4} "
        f"quality={receipt['quality_score']:.2f} "
        f"cost={dollars(receipt['cost'])} "
        f"cost_per_quality={dollars(receipt['cost_per_quality'])}"
    )

best_quality = max(budget.receipts, key=lambda r: r["quality_score"])
best_value = min(budget.receipts, key=lambda r: r["cost_per_quality"])

print("\nWhat to notice")
print("--------------")
print(
    f"Best quality: {best_quality['model_size']} "
    f"with score={best_quality['quality_score']:.2f}."
)
print(
    f"Best cost-performance value: {best_value['model_size']} "
    f"at {dollars(best_value['cost_per_quality'])} per quality point."
)
print(
    "Token counts matter: longer prompts and longer responses increase simulated "
    "cost even when the task is the same."
)

print("\nBudget summary")
print("--------------")
summary = budget.summary()
print_budget_summary(summary)
