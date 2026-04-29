# Compute Cost Simulator

Compute Cost Simulator (CCS) is a lightweight Python package for teaching
**cost-aware computing** in notebooks and scripts. It helps students connect
computational choices to simulated costs for CPU time, GPU time, memory,
storage, and LLM token usage.

All costs in CCS are **simulated pedagogical estimates**. They are not real
billing data, provider prices, or cloud account charges.

## Why Cost-Aware Computing Matters

Students often learn to optimize for accuracy, speed, or completion without
asking what a computation costs. CCS makes that tradeoff visible by giving each
action a simple receipt. Instructors can use those receipts to support
discussion about:

- whether a small performance gain is worth extra compute,
- how budgets shape modeling and analysis choices,
- how LLM prompt length affects cost,
- how reproducibility changes when many students repeat the same workflow.

## Installation

From the repository root:

```bash
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
pytest
```

## Quickstart

```python
from ccs import Budget, compute_block, track_llm_call

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

track_llm_call(
    task="summarize clinical note",
    model_size="medium",
    input_tokens=1200,
    output_tokens=300,
    budget=budget,
)

print(budget.summary())
```

## Core Concepts

### Computational Receipts

A receipt is a plain Python dictionary that records an action, its category,
model name, runtime or token usage, simulated cost, timestamp, and optional
performance metric.

```python
{
    "task": "train logistic regression",
    "category": "modeling",
    "model": "logistic_regression",
    "runtime_seconds": 0.25,
    "cost": 0.0005,
    "metric_name": "f1",
    "metric_value": 0.64,
}
```

Receipts can be stored in a `Budget`, appended to JSONL logs, or summarized
with `summarize_logs()`.

### Simulated Budgets

`Budget` tracks total simulated spending, remaining balance, warning status,
and all receipts.

```python
from ccs import Budget

budget = Budget(total=5.00)
print(budget.remaining())
print(budget.summary())
```

### Cost-Performance Tradeoffs

`compute_block()` lets students compare approaches using both cost and a metric
such as accuracy, F1, latency, or quality score.

```python
with compute_block(
    task="train random forest",
    category="modeling",
    model="random_forest",
    budget=budget,
    metric_name="f1",
    metric_value=0.69,
):
    pass
```

The resulting receipt includes `cost_per_metric`, which is useful for asking:
“Did the better score justify the extra simulated cost?”

### LLM Token Costs

`track_llm_call()` estimates simulated cost from model size and token counts.

```python
track_llm_call(
    task="summarize article",
    model_size="small",
    input_tokens=900,
    output_tokens=180,
    budget=budget,
)
```

This is useful for teaching why shorter prompts, shorter outputs, and smaller
models may matter in high-volume workflows.

## Examples

The examples use `time.sleep()` and fake but realistic metrics so they run
without external ML dependencies.

```bash
python examples/intro_modeling_demo.py
python examples/llm_token_demo.py
python examples/budget_challenge_demo.py
```

## Optional Dashboard

CCS includes a lightweight Streamlit dashboard prototype for inspecting JSONL
receipt logs. Streamlit is optional and is not required for core package use.

Install the optional dashboard dependency:

```bash
pip install -e ".[dashboard]"
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard can load a JSONL receipt log and display total simulated cost,
remaining budget when available, cost by category, cost by model, the most
expensive action, and a receipt table.

To create a JSONL log, pass `log_path` to `compute_block()` or
`track_llm_call()`:

```python
with compute_block("train baseline", budget=budget, log_path="receipts.jsonl"):
    pass

track_llm_call(
    task="summarize notes",
    model_size="small",
    input_tokens=900,
    output_tokens=180,
    budget=budget,
    log_path="receipts.jsonl",
)
```

## Example Assignment

Train or simulate at least three approaches under a $5 compute budget and
justify the final choice using both performance and cost.

Reflection questions:

1. Which approach performed best?
2. Which approach was most cost-effective?
3. Did the most expensive approach justify its simulated cost?
4. How would your choice change if the workflow ran every week?
5. What would it cost for every student in the class to reproduce your result?

## Current Limitations

- Costs are simulated and intentionally simplified.
- No real cloud billing APIs are used.
- The dashboard is an optional prototype, not a full course analytics system.
- No notebooks are included yet.
- The default rates are teaching defaults, not provider-specific prices.
- The examples simulate ML work instead of training real models.

## Roadmap

- Add more classroom-ready examples and assignment templates.
- Add optional notebook examples.
- Add richer reporting for cost by category, model, and workflow.
- Improve the optional dashboard with filters and export options.
- Add configurable course-specific cost profiles.
- Add documentation for instructors on adapting budgets and rubrics.

## Public API

- `Budget`
- `compute_block`
- `track_llm_call`
- `load_cost_config`
- `summarize_logs`
