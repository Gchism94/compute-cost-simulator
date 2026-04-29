"""Minimal demo for token-based simulated costs."""

from ccs import Budget, track_llm_call

budget = Budget(total=2.00)

receipt = track_llm_call(
    task="summarize article",
    model_size="medium",
    input_tokens=1200,
    output_tokens=300,
    budget=budget,
)

print(receipt)
print(budget.summary())
