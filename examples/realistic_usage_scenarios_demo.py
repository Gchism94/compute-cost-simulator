"""Compare structured labs with more open-ended student project workflows.

This example writes scenario-tagged receipts to:
- logs/ccs_session.jsonl
- logs/realistic_usage_scenarios.jsonl

All costs are simulated teaching estimates.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from time import sleep
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ccs import Budget, compute_block, summarize_logs, track_llm_call


LOG_DIR = "logs"
SHARED_LOG_PATH = os.path.join(LOG_DIR, "ccs_session.jsonl")
SCENARIO_LOG_PATH = os.path.join(LOG_DIR, "realistic_usage_scenarios.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)
if os.path.exists(SCENARIO_LOG_PATH):
    os.remove(SCENARIO_LOG_PATH)


CLASSROOM_COST_CONFIG = {
    "runtime": {
        "cpu_second": 0.04,
        "gpu_second": 0.38,
        "memory_gb_second": 0.0,
        "storage_mb": 0.0004,
    },
    "llm": {
        "small": {"input_token": 0.000004, "output_token": 0.00001},
        "medium": {"input_token": 0.000014, "output_token": 0.000035},
        "large": {"input_token": 0.00005, "output_token": 0.00012},
    },
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


def write_receipt(receipt: dict[str, Any]) -> None:
    for path in (SHARED_LOG_PATH, SCENARIO_LOG_PATH):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(receipt) + "\n")


def run_model(
    budget: Budget,
    scenario: str,
    task: str,
    model: str,
    seconds: float,
    f1: float,
    gpu_used: bool = False,
) -> dict[str, Any]:
    with compute_block(
        task=task,
        category="modeling",
        model=model,
        budget=budget,
        metric_name="f1",
        metric_value=f1,
        gpu_used=gpu_used,
        config=CLASSROOM_COST_CONFIG,
    ) as receipt:
        receipt["scenario"] = scenario
        sleep(seconds)
    write_receipt(receipt)
    return receipt


def run_compute(
    budget: Budget,
    scenario: str,
    task: str,
    category: str,
    model: str,
    seconds: float,
    storage_mb: float = 0,
) -> dict[str, Any]:
    with compute_block(
        task=task,
        category=category,
        model=model,
        budget=budget,
        storage_mb=storage_mb,
        config=CLASSROOM_COST_CONFIG,
    ) as receipt:
        receipt["scenario"] = scenario
        sleep(seconds)
    write_receipt(receipt)
    return receipt


def run_ai_call(
    budget: Budget,
    scenario: str,
    task: str,
    model_size: str,
    input_tokens: int,
    output_tokens: int,
    category: str = "llm",
    model: str | None = None,
) -> dict[str, Any]:
    receipt = track_llm_call(
        task=task,
        model_size=model_size,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        budget=budget,
        category=category,
        model=model,
        config=CLASSROOM_COST_CONFIG,
    )
    receipt["scenario"] = scenario
    write_receipt(receipt)
    return receipt


def scenario_costs(receipts: list[dict[str, Any]]) -> dict[str, float]:
    total = sum(float(receipt.get("cost", 0.0)) for receipt in receipts)
    ai = sum(
        float(receipt.get("cost", 0.0))
        for receipt in receipts
        if receipt.get("category") in {"llm", "ai_support"}
    )
    modeling = sum(
        float(receipt.get("cost", 0.0))
        for receipt in receipts
        if receipt.get("category") == "modeling"
    )
    return {
        "total": total,
        "ai": ai,
        "modeling": modeling,
        "ai_share": ai / total if total else 0.0,
    }


def print_scenario_summary(scenario: str, budget: Budget) -> None:
    summary = summarize_logs(budget.receipts)
    costs = scenario_costs(budget.receipts)
    classroom_projection = costs["total"] * 40
    repeated_project_projection = costs["total"] * 40 * 5

    print(f"\n{scenario}")
    print("-" * len(scenario))
    print(f"Total Cost: {dollars(costs['total'])}")
    print(f"Actions Tracked: {summary['number_of_actions']}")
    print(f"AI / LLM Cost: {dollars(costs['ai'])}")
    print(f"Modeling Cost: {dollars(costs['modeling'])}")
    print(f"AI Share of Cost: {costs['ai_share']:.0%}")
    print(f"Projected Cost for 40 Students: {dollars(classroom_projection)}")
    print(f"Projected Cost if Each Student Repeats It 5 Times: {dollars(repeated_project_projection)}")


def run_structured_lab() -> Budget:
    scenario = "Structured In-Class Lab"
    budget = Budget(total=0.25)
    run_model(budget, scenario, "train logistic regression", "logistic_regression", 0.08, 0.63)
    run_model(budget, scenario, "train random forest", "random_forest", 0.16, 0.69)
    run_ai_call(
        budget,
        scenario,
        "ask for a short debugging explanation",
        "small",
        input_tokens=350,
        output_tokens=120,
    )
    return budget


def run_student_project() -> Budget:
    scenario = "Student Project Workflow"
    budget = Budget(total=1.25)
    run_model(budget, scenario, "train tuned random forest", "random_forest", 0.24, 0.72)
    run_model(budget, scenario, "train XGBoost-like model", "xgboost_like_model", 0.30, 0.75)
    run_model(budget, scenario, "train neural network", "neural_network", 0.24, 0.77, gpu_used=True)
    run_model(budget, scenario, "try transformer-style classifier", "transformer_classifier", 0.36, 0.79, gpu_used=True)

    ai_turns = [
        ("debug model warning", 1100, 350),
        ("refactor feature pipeline", 1700, 600),
        ("write focused tests", 1400, 450),
        ("summarize model errors", 1300, 400),
    ]
    for task, input_tokens, output_tokens in ai_turns:
        run_ai_call(budget, scenario, task, "medium", input_tokens, output_tokens, category="ai_support")

    run_compute(budget, scenario, "retrieve project documents", "rag_retrieval", "top_k=4", 0.04)
    run_ai_call(
        budget,
        scenario,
        "answer project question with retrieved context",
        "medium",
        input_tokens=2800,
        output_tokens=500,
        category="ai_support",
        model="rag_project_helper",
    )
    return budget


def run_uninhibited_workflow() -> Budget:
    scenario = "Uninhibited AI-Assisted Workflow"
    budget = Budget(total=2.00)
    run_model(budget, scenario, "train large baseline model", "large_baseline_model", 0.36, 0.74, gpu_used=True)
    run_model(budget, scenario, "retry large model with more features", "large_feature_model", 0.42, 0.76, gpu_used=True)

    heavy_ai_turns = [
        ("generate starter project code", 2600, 1400),
        ("paste full traceback for debugging", 6200, 1800),
        ("paste full source file for refactor", 7800, 2400),
        ("retry after vague prompt", 5200, 1700),
        ("add tests after failures", 4800, 1600),
        ("ask for documentation draft", 4200, 1300),
        ("repeat with RAG context", 9000, 2200),
    ]
    for task, input_tokens, output_tokens in heavy_ai_turns:
        run_ai_call(budget, scenario, task, "large", input_tokens, output_tokens, category="ai_support")

    for retry in range(1, 4):
        run_ai_call(
            budget,
            scenario,
            f"retry chatbot answer {retry}",
            "large",
            input_tokens=3600 + retry * 700,
            output_tokens=1100,
            category="ai_support",
        )
    return budget


print("Compute Cost Simulator: Realistic Usage Scenarios")
print("==================================================")
print("This demo compares constrained classwork with more open-ended project habits.")

structured_lab = run_structured_lab()
student_project = run_student_project()
uninhibited_workflow = run_uninhibited_workflow()

print_scenario_summary("Scenario A: Structured In-Class Lab", structured_lab)
print_scenario_summary("Scenario B: Student Project Workflow", student_project)
print_scenario_summary("Scenario C: Uninhibited AI-Assisted Workflow", uninhibited_workflow)

print("\nWhat to Notice")
print("--------------")
print("Structured labs stay cheap by limiting models, tokens, and repetitions.")
print("Project work costs more because you try more models and ask for more AI help.")
print("Uninhibited AI use can become the biggest cost driver through repeated long prompts.")
print("Small per-action costs can become large when repeated across a whole class.")

print("\nQuestions to Consider")
print("---------------------")
print("1. Which scenario looks most like your own workflow?")
print("2. Which repeated action would you reduce first?")
print("3. How would you keep project work useful without letting costs drift?")
print(f"\nScenario Log Written To: {SCENARIO_LOG_PATH}")
