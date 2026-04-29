# Compute Cost Simulator

![Zero dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)

Compute Cost Simulator (CCS) is a lightweight Python package for teaching
**cost-aware computing** in notebooks and scripts. It helps students see how
CPU time, GPU time, memory, storage, and LLM token usage can shape technical
decisions.

All costs in CCS are **simulated pedagogical estimates**. They are not real
billing data, provider prices, or cloud account charges.

## Why This Matters

CCS has no required external dependencies and does not need cloud setup,
credentials, dashboards, or billing APIs. Students can run the examples with a
standard Python installation and focus on the lesson: estimating costs, making
tradeoffs, and explaining decisions rather than fighting environment setup.

## Primary Demo

Start with the flagship learning arc:

```bash
python examples/flagship_budget_failure_demo.py
```

This demo shows a student working under a small simulated budget. It walks
through a cheap baseline, better model, expensive model, hyperparameter search
decision, AI/RAG support cost, budget warning, near-failure, and final
recommendation. It is the best first lesson because it frames cost-aware
computing as planning before execution, not just accounting afterward.

## Learning Pathway

1. Run the flagship demo to introduce the full decision arc.
2. Use `examples/intro_modeling_demo.py` to focus on model cost-performance tradeoffs.
3. Use `examples/llm_token_demo.py` and `examples/token_burn_demo.py` to teach token economics.
4. Use `examples/hyperparameter_explosion_demo.py` to show repeated experimentation costs.
5. Use `examples/rag_cost_burn_demo.py` and `examples/vibe_coding_cost_demo.py` to discuss AI workflow loops.
6. Use `examples/scaling_inference_demo.py` to connect small per-action costs to deployment scale.
7. Use `examples/budget_challenge_demo.py` as a final practice activity.

See [examples/README.md](examples/README.md) and
[curriculum/README.md](curriculum/README.md) for the full curriculum map.

## Installation

Core install:

```bash
pip install -e .
```

No additional packages are required to run the examples.

Development install:

```bash
pip install -r requirements-dev.txt
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

- **Computational receipts:** plain dictionaries that record task, category,
  model, runtime or token usage, simulated cost, timestamp, and optional metrics.
- **Simulated budgets:** `Budget` tracks spent amount, remaining balance,
  warnings, and receipts.
- **Cost-performance tradeoffs:** `compute_block()` can pair simulated cost
  with metrics such as F1 or quality score.
- **LLM token costs:** `track_llm_call()` shows how input and output tokens
  affect simulated cost.
- **Summaries:** `summarize_logs()` groups receipts by category and model.

## Design Philosophy

CCS is intentionally small. The package favors readable code, plain Python data
structures, and command-line examples over infrastructure. The goal is
pedagogical clarity: students should spend their attention on deciding what is
worth running, not on installing a heavy stack.

## Optional: Dashboard

CCS includes a lightweight Streamlit dashboard prototype for JSONL receipt logs.
Streamlit is optional and is not required for core package use.

Install Streamlit only if you want to use the dashboard:

```bash
pip install "streamlit>=1.30"
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

To test the dashboard end to end:

```bash
python examples/flagship_budget_failure_demo.py
python examples/intro_modeling_demo.py
python examples/llm_token_demo.py
streamlit run dashboard/app.py
```

Then load `logs/ccs_session.jsonl`.

## Teaching Materials

- [Assignment template](teaching/assignment_template.md)
- [Reflection questions](teaching/reflection_questions.md)
- [Rubric](teaching/rubric.md)
- [Discussion prompts](teaching/discussion_prompts.md)
- [Roadmap](ROADMAP.md)

## Current Limitations

- Costs are simulated and intentionally simplified.
- No real cloud billing APIs are used.
- The examples simulate compute rather than training real models.
- The dashboard is optional and prototype-level.
- No notebooks are included yet.

## Public API

- `Budget`
- `compute_block`
- `track_llm_call`
- `load_cost_config`
- `summarize_logs`
