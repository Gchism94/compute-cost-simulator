"""Token burn demo: inefficient prompts can exhaust LLM budgets.

This example compares concise and wasteful prompting patterns. It does not call
an actual LLM; it uses CCS token receipts to show simulated token costs.
"""

from ccs import Budget, track_llm_call


CLASSROOM_COST_CONFIG = {
    "runtime": {},
    "llm": {
        "medium": {"input_token": 0.00004, "output_token": 0.00008},
    },
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


budget = Budget(total=0.35)

prompt_patterns = [
    {
        "label": "concise prompt",
        "task": "summarize note with concise prompt",
        "input_tokens": 500,
        "output_tokens": 120,
        "expected_quality": 0.80,
    },
    {
        "label": "verbose prompt",
        "task": "summarize note with verbose prompt",
        "input_tokens": 2500,
        "output_tokens": 350,
        "expected_quality": 0.84,
    },
    {
        "label": "repeat context 3 times",
        "task": "summarize note after repeated context",
        "input_tokens": 7500,
        "output_tokens": 500,
        "expected_quality": 0.85,
    },
]

print("Compute Cost Simulator: Token Burn Demo")
print("========================================")
print("More tokens do not always mean a much better answer.")

print("\nPrompt comparison")
print("-----------------")
print(
    f"{'Prompt pattern':24} {'Tokens':>8} {'Quality':>8} "
    f"{'Estimated':>10} {'Actual':>8} {'Remaining':>10}"
)
print("-" * 78)

for pattern in prompt_patterns:
    estimated_cost = (
        pattern["input_tokens"] * CLASSROOM_COST_CONFIG["llm"]["medium"]["input_token"]
        + pattern["output_tokens"] * CLASSROOM_COST_CONFIG["llm"]["medium"]["output_token"]
    )
    receipt = track_llm_call(
        task=pattern["task"],
        model_size="medium",
        input_tokens=pattern["input_tokens"],
        output_tokens=pattern["output_tokens"],
        budget=budget,
        config=CLASSROOM_COST_CONFIG,
    )
    receipt["quality_score"] = pattern["expected_quality"]
    receipt["estimated_cost"] = round(estimated_cost, 6)

    print(
        f"{pattern['label']:24} "
        f"{receipt['total_tokens']:>8} "
        f"{receipt['quality_score']:>8.2f} "
        f"{dollars(receipt['estimated_cost']):>10} "
        f"{dollars(receipt['cost']):>8} "
        f"{dollars(receipt['budget_remaining_after']):>10}"
    )

summary = budget.summary()
most_expensive = summary["most_expensive_action"]
concise = budget.receipts[0]
verbose = budget.receipts[-1]
extra_cost = verbose["cost"] - concise["cost"]
extra_quality = verbose["quality_score"] - concise["quality_score"]

print("\nBudget summary")
print("--------------")
print(f"Started with: {dollars(summary['budget_total'])}")
print(f"Spent: {dollars(summary['spent'])}")
print(f"Remaining: {dollars(summary['remaining'])}")
print(f"Actions tracked: {summary['number_of_actions']}")
print(f"Most expensive action: {most_expensive['task']} ({dollars(most_expensive['cost'])})")

print("\nWhat students should notice")
print("---------------------------")
print("The repeated-context prompt uses many more tokens than the concise prompt.")
print(
    f"In this simulation it costs {dollars(extra_cost)} more for only "
    f"{extra_quality:.2f} extra quality points."
)
print(
    "Token inefficiency is a budget problem: repeated context, long instructions, "
    "and oversized outputs can exhaust funds before the work improves much."
)
