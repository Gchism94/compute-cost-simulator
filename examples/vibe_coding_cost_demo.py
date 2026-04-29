"""Vibe-coding cost demo: iterative prompting can burn tokens quickly.

This example simulates a student using an AI coding assistant. No real coding
assistant is called; CCS receipts show how chat turns, pasted context, and
repeated vague prompts can compound simulated token costs.
"""

from __future__ import annotations

from time import sleep

from ccs import Budget, track_llm_call


CLASSROOM_COST_CONFIG = {
    "runtime": {},
    "llm": {
        "medium": {"input_token": 0.000015, "output_token": 0.00004},
    },
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


def run_chat_turns(label: str, budget: Budget, turns: list[dict[str, int | str]]) -> None:
    print(f"\n{label}")
    print("-" * len(label))
    print(
        f"{'Turn':>4} {'Request':34} {'Input':>7} {'Output':>7} "
        f"{'Cost':>8} {'Cumulative':>11}"
    )
    print("-" * 82)

    for turn_number, turn in enumerate(turns, start=1):
        sleep(0.02)
        receipt = track_llm_call(
            task=str(turn["request"]),
            model_size="medium",
            input_tokens=int(turn["input_tokens"]),
            output_tokens=int(turn["output_tokens"]),
            budget=budget,
            category="ai_coding",
            model="coding_assistant",
            config=CLASSROOM_COST_CONFIG,
        )
        print(
            f"{turn_number:>4} "
            f"{str(turn['request'])[:34]:34} "
            f"{receipt['input_tokens']:>7} "
            f"{receipt['output_tokens']:>7} "
            f"{dollars(receipt['cost']):>8} "
            f"{dollars(budget.spent):>11}"
        )


unstructured_budget = Budget(total=1.00)
planned_budget = Budget(total=1.00)

unstructured_turns = [
    {
        "request": "generate starter code",
        "input_tokens": 900,
        "output_tokens": 1400,
    },
    {
        "request": "debug vague error",
        "input_tokens": 1700,
        "output_tokens": 900,
    },
    {
        "request": "paste full traceback",
        "input_tokens": 4200,
        "output_tokens": 1100,
    },
    {
        "request": "refactor entire file",
        "input_tokens": 5200,
        "output_tokens": 1800,
    },
    {
        "request": "write tests after refactor",
        "input_tokens": 4300,
        "output_tokens": 1500,
    },
    {
        "request": "write documentation",
        "input_tokens": 3600,
        "output_tokens": 1300,
    },
    {
        "request": "follow up after tests fail",
        "input_tokens": 6100,
        "output_tokens": 1600,
    },
]

planned_turns = [
    {
        "request": "outline implementation plan",
        "input_tokens": 450,
        "output_tokens": 450,
    },
    {
        "request": "generate one small function",
        "input_tokens": 700,
        "output_tokens": 650,
    },
    {
        "request": "ask about one error line",
        "input_tokens": 850,
        "output_tokens": 500,
    },
    {
        "request": "request focused tests",
        "input_tokens": 900,
        "output_tokens": 700,
    },
    {
        "request": "summarize docs for final code",
        "input_tokens": 650,
        "output_tokens": 450,
    },
]

print("Compute Cost Simulator: Vibe-Coding Cost Demo")
print("==============================================")
print("AI coding tools are useful, but each chat turn has a simulated token cost.")

run_chat_turns("A. Unstructured vibe-coding loop", unstructured_budget, unstructured_turns)
run_chat_turns("B. Planned workflow with smaller prompts", planned_budget, planned_turns)

unstructured_summary = unstructured_budget.summary()
planned_summary = planned_budget.summary()
savings = unstructured_summary["spent"] - planned_summary["spent"]
monthly_unstructured = unstructured_summary["spent"] * 20
monthly_planned = planned_summary["spent"] * 20

print("\nWorkflow comparison")
print("-------------------")
print(f"Unstructured turns: {unstructured_summary['number_of_actions']}")
print(f"Planned turns: {planned_summary['number_of_actions']}")
print(f"Unstructured total: {dollars(unstructured_summary['spent'])}")
print(f"Planned total: {dollars(planned_summary['spent'])}")
print(f"Simulated savings from planning: {dollars(savings)}")
print(f"20 similar sessions unstructured: {dollars(monthly_unstructured)}")
print(f"20 similar sessions planned: {dollars(monthly_planned)}")

print("\nWhat students should notice")
print("---------------------------")
print("Each chat turn has a cost, even when the assistant gives a bad answer.")
print("Pasting large files or tracebacks increases input tokens quickly.")
print("Repeated vague prompts compound because every retry sends more context.")
print("Planning, smaller context, and local testing reduce token use.")
print("AI coding tools can be valuable, but they are not free.")
