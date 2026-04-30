"""Flagship demo: cost-aware computing is planning, not just accounting.

You have a small simulated budget to build a model. The script estimates
cost before expensive actions, chooses what to run, and ends with a defensible
recommendation based on both F1 and cost.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from time import sleep

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ccs import Budget, compute_block, summarize_logs, track_llm_call


LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "ccs_session.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)
if os.path.exists(LOG_PATH):
    os.remove(LOG_PATH)


CLASSROOM_COST_CONFIG = {
    "runtime": {
        "cpu_second": 0.04,
        "gpu_second": 0.42,
        "memory_gb_second": 0.0,
        "storage_mb": 0.0,
    },
    "llm": {
        "medium": {"input_token": 0.000012, "output_token": 0.00003},
    },
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


def runtime_estimate(seconds: float, gpu_used: bool = False) -> float:
    rates = CLASSROOM_COST_CONFIG["runtime"]
    gpu_cost = rates["gpu_second"] if gpu_used else 0.0
    return round(seconds * (rates["cpu_second"] + gpu_cost), 6)


def llm_estimate(input_tokens: int, output_tokens: int) -> float:
    rates = CLASSROOM_COST_CONFIG["llm"]["medium"]
    return round(input_tokens * rates["input_token"] + output_tokens * rates["output_token"], 6)


def print_expensive_step_warning(label: str, estimate: float, budget: Budget) -> None:
    remaining = budget.remaining()
    percent = estimate / remaining if remaining > 0 else float("inf")
    print(f"\nPre-run estimate for {label}")
    print(f"Estimated cost: {dollars(estimate)}")
    print(f"Remaining budget: {dollars(remaining)}")
    print(f"Percent of remaining budget consumed: {percent:.0%}")
    if estimate > remaining:
        print("Decision warning: this would exceed the remaining budget.")
    elif percent >= 0.5:
        print("Decision warning: this would consume a large share of what remains.")
    else:
        print("Decision warning: affordable, but still compare cost with expected gain.")


def run_model(
    budget: Budget,
    task: str,
    model: str,
    seconds: float,
    f1: float,
    gpu_used: bool = False,
) -> dict:
    with compute_block(
        task=task,
        category="modeling",
        model=model,
        budget=budget,
        metric_name="f1",
        metric_value=f1,
        gpu_used=gpu_used,
        config=CLASSROOM_COST_CONFIG,
        log_path=LOG_PATH,
    ):
        sleep(seconds)
    return budget.receipts[-1]


def print_model_result(receipt: dict, previous: dict | None = None) -> None:
    if previous is None:
        marginal_gain = "baseline"
        marginal_cost = "baseline"
    else:
        marginal_gain = f"{receipt['metric_value'] - previous['metric_value']:+.2f}"
        marginal_cost = dollars(max(receipt["cost"] - previous["cost"], 0.0))

    print(
        f"{receipt['model']:24} "
        f"F1={receipt['metric_value']:.2f} "
        f"cost={dollars(receipt['cost'])} "
        f"cost_per_f1={dollars(receipt['cost_per_metric'])} "
        f"marginal_f1={marginal_gain} "
        f"marginal_cost={marginal_cost}"
    )


budget = Budget(total=0.20, warn_at=0.75)
model_receipts: list[dict] = []

print("Compute Cost Simulator: Flagship Budget Failure Demo")
print("=====================================================")

print("\nScenario")
print("--------")
print(
    "You have $0.20 of simulated compute budget to build a classifier. "
    "You need a good model, but you also need a workflow a classmate can reproduce."
)

print("\nStarting Budget")
print("---------------")
print(f"Budget: {dollars(budget.total)}")
print("Rule for this demo: estimate before expensive steps, then decide what to run.")

print("\nStep 1: Cheap Baseline")
print("----------------------")
baseline_estimate = runtime_estimate(seconds=0.15)
print(f"Estimated cost: {dollars(baseline_estimate)}")
baseline = run_model(
    budget,
    task="train cheap logistic regression baseline",
    model="logistic_regression",
    seconds=0.15,
    f1=0.63,
)
model_receipts.append(baseline)
print_model_result(baseline)

print("\nStep 2: Better Model")
print("--------------------")
forest_estimate = runtime_estimate(seconds=0.35)
print(f"Estimated cost: {dollars(forest_estimate)}")
random_forest = run_model(
    budget,
    task="train random forest with basic tuning",
    model="random_forest",
    seconds=0.35,
    f1=0.70,
)
model_receipts.append(random_forest)
print_model_result(random_forest, previous=baseline)

print("\nStep 3: Expensive Model")
print("-----------------------")
neural_estimate = runtime_estimate(seconds=0.16, gpu_used=True)
print_expensive_step_warning("neural network training", neural_estimate, budget)
neural_network = run_model(
    budget,
    task="train small neural network",
    model="neural_network",
    seconds=0.16,
    f1=0.72,
    gpu_used=True,
)
model_receipts.append(neural_network)
print_model_result(neural_network, previous=random_forest)

if budget.percent_spent() >= budget.warn_at:
    print(
        f"Budget warning: {budget.percent_spent():.0%} of the budget is now used. "
        "Future choices need extra scrutiny."
    )

print("\nStep 4: Hyperparameter Search Decision")
print("--------------------------------------")
full_search_runs = 20
seconds_per_search_run = 0.025
full_search_estimate = full_search_runs * runtime_estimate(
    seconds=seconds_per_search_run,
    gpu_used=True,
)
print_expensive_step_warning("full 20-run hyperparameter search", full_search_estimate, budget)
print("Decision: do not run this full search because it would exceed the budget.")

reduced_runs = [
    {"name": "reduced_search_1", "seconds": 0.03, "f1": 0.705},
    {"name": "reduced_search_2", "seconds": 0.03, "f1": 0.715},
    {"name": "reduced_search_3", "seconds": 0.03, "f1": 0.718},
]
reduced_estimate = len(reduced_runs) * runtime_estimate(seconds=0.03, gpu_used=True)
print(f"\nCheaper alternative: run {len(reduced_runs)} targeted trials.")
print(f"Estimated reduced search cost: {dollars(reduced_estimate)}")

previous = random_forest
for run in reduced_runs:
    receipt = run_model(
        budget,
        task=f"targeted hyperparameter trial {run['name']}",
        model=run["name"],
        seconds=run["seconds"],
        f1=run["f1"],
        gpu_used=True,
    )
    model_receipts.append(receipt)
    print_model_result(receipt, previous=previous)
    previous = receipt

print("\nStep 5: AI Assistant / RAG Support Cost")
print("---------------------------------------")
assistant_input_tokens = 2600
assistant_output_tokens = 450
assistant_estimate = llm_estimate(assistant_input_tokens, assistant_output_tokens)
print_expensive_step_warning("AI assistant debugging and RAG context", assistant_estimate, budget)
assistant_receipt = track_llm_call(
    task="ask AI assistant to explain failed trials with retrieved context",
    model_size="medium",
    input_tokens=assistant_input_tokens,
    output_tokens=assistant_output_tokens,
    budget=budget,
    category="ai_support",
    model="rag_debug_helper",
    config=CLASSROOM_COST_CONFIG,
    log_path=LOG_PATH,
)
print(
    f"AI/RAG support used {assistant_receipt['total_tokens']} tokens "
    f"and cost {dollars(assistant_receipt['cost'])}."
)
if budget.percent_spent() >= budget.warn_at:
    print(
        f"Budget warning: {budget.percent_spent():.0%} of the budget is now used. "
        "The workflow is close to failure."
    )

print("\nBudget Status")
print("-------------")
summary = budget.summary()
log_summary = summarize_logs(budget.receipts)
most_expensive = summary["most_expensive_action"]
print(f"Started with: {dollars(summary['budget_total'])}")
print(f"Spent: {dollars(summary['spent'])}")
print(f"Remaining: {dollars(summary['remaining'])}")
print(f"Percent spent: {summary['percent_spent']:.0%}")
print(f"Actions tracked: {summary['number_of_actions']}")
print(f"Total from summarize_logs: {dollars(log_summary['total_cost'])}")
print(f"Most expensive action: {most_expensive['task']} ({dollars(most_expensive['cost'])})")

best_f1 = max(model_receipts, key=lambda r: r["metric_value"])
best_value = min(model_receipts, key=lambda r: r["cost_per_metric"])
final_choice = random_forest
expensive_version_cost = full_search_estimate + neural_network["cost"] + assistant_receipt["cost"]
classroom_projection = expensive_version_cost * 40 * 5
final_reproduction_cost = (
    baseline["cost"] + random_forest["cost"] + reduced_estimate + assistant_receipt["cost"]
)

print("\nFinal Recommendation")
print("--------------------")
print(f"Highest F1 observed: {best_f1['model']} with F1={best_f1['metric_value']:.3f}.")
print(
    f"Best cost-per-F1 option: {best_value['model']} at "
    f"{dollars(best_value['cost_per_metric'])} per F1 point."
)
print(
    f"Recommended final choice: {final_choice['model']} with F1={final_choice['metric_value']:.2f}."
)
print(
    "Reason: the neural network and reduced search only add small F1 gains, while "
    "the budget is already near failure after AI/RAG support."
)
print(
    f"Estimated cost to reproduce the recommended workflow: "
    f"{dollars(final_reproduction_cost)}."
)
print(
    "Feasible under your budget: "
    f"{'yes' if final_reproduction_cost <= budget.total else 'no'}."
)
print(
    f"If 40 students each ran the expensive version 5 times: "
    f"{dollars(classroom_projection)}."
)

ai_receipts = [receipt for receipt in budget.receipts if receipt["category"] == "ai_support"]
model_training_cost = sum(receipt["cost"] for receipt in model_receipts)
ai_usage_cost = sum(receipt["cost"] for receipt in ai_receipts)
total_tokens = sum(receipt.get("total_tokens", 0) for receipt in ai_receipts)

print("\nAI Usage Summary")
print("----------------")
print(f"- AI usage cost: {dollars(ai_usage_cost)}")
print(f"- Model training cost: {dollars(model_training_cost)}")
print(f"- Number of AI calls: {len(ai_receipts)}")
print(f"- Total tokens used: {total_tokens:,}")
print("\nObservation:")
if ai_usage_cost > model_training_cost:
    print("You spent more on AI assistance than on the model itself.")
else:
    print("AI assistance was a smaller portion of your total compute cost.")

print("\nQuestions to consider")
print("---------------------")
print("1. Which action changed your plan before execution?")
print("2. Was the highest-performing model worth its marginal cost?")
print("3. How did repeated runs and AI/RAG support push your budget toward failure?")
print("4. What would you cut first if you had to make this workflow reproducible?")
print("5. How would your decision change if the whole class repeated this workflow?")
