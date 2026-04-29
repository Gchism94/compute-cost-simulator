# Compute Cost Simulator

A lightweight, standalone Python prototype for teaching **cost-aware computing**.

The Compute Cost Simulator (CCS) helps students see that computational actions have costs. It translates runtime, simulated CPU/GPU use, storage, and LLM token usage into simple pedagogical "receipts" that can be used in notebooks, labs, and assignments.

## Why this exists

Students often learn to optimize for accuracy, speed, or completion without considering the resource cost of their choices. CCS makes compute visible by asking students to reason about:

- how much an action costs,
- whether the performance gain justifies the cost,
- what happens when a workflow scales,
- and whether another student could reproduce the result within the same budget.

All costs are **simulated** and intended for teaching. CCS does not require cloud credentials or billing APIs.

## Quickstart

```bash
pip install -e .
```

```python
from ccs import Budget, compute_block

budget = Budget(total=5.00)

with compute_block(
    task="train logistic regression",
    category="modeling",
    model="logistic_regression",
    budget=budget,
    metric_name="f1",
    metric_value=0.64,
):
    # model.fit(X_train, y_train)
    pass

print(budget.summary())
```

## LLM token cost example

```python
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
```

## Example assignment idea

> You have a simulated compute budget of $5. Train at least three models for the same prediction task. Your final recommendation should justify the model using both predictive performance and simulated compute cost.

Reflection prompts:

1. Which model performed best?
2. Which model was most cost-effective?
3. Did the most expensive model justify its cost?
4. How would your choice change if the model had to run weekly?
5. How much would it cost another student to reproduce your result?

## Project status

This is a prototype scaffold designed for Codex/local development. The first implementation target is a simple Python package with:

- `compute_block()` context manager
- `Budget` class
- configurable cost model
- JSON/CSV logging
- LLM token cost helper
- summary reports
- tests

## Repository structure

```text
compute-cost-simulator/
├── ccs/
│   ├── __init__.py
│   ├── tracker.py
│   ├── budget.py
│   ├── cost_model.py
│   ├── llm.py
│   ├── reports.py
│   └── config.yaml
├── examples/
│   ├── intro_modeling_demo.py
│   └── llm_token_demo.py
├── tests/
│   ├── test_budget.py
│   ├── test_cost_model.py
│   └── test_tracker.py
├── .github/workflows/tests.yml
├── pyproject.toml
└── README.md
```
