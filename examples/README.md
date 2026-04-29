# Example Scripts

The examples are command-line teaching scripts. They use simulated costs and
fake but realistic metrics so students can focus on cost-aware reasoning rather
than setup.

By default, examples append receipts to `logs/ccs_session.jsonl`. The flagship
demo resets that shared log so you can start a clean dashboard session.

## Testing The Dashboard

1. Generate a shared receipt log:

```bash
python examples/flagship_budget_failure_demo.py
python examples/intro_modeling_demo.py
python examples/llm_token_demo.py
python examples/rag_cost_burn_demo.py
python examples/vibe_coding_cost_demo.py
```

2. Start the optional dashboard:

```bash
streamlit run dashboard/app.py
```

3. Load:

```text
logs/ccs_session.jsonl
```

## Primary Overview

### `flagship_budget_failure_demo.py`

- Teaching purpose: introduce the full learning arc from estimation to final recommendation.
- Core concept: cost-aware computing is planning, not just post-hoc tracking.
- Suggested module: overview lesson or capstone preview.
- Command:

```bash
python examples/flagship_budget_failure_demo.py
```

## Modular Curriculum Pieces

### `intro_modeling_demo.py`

- Teaching purpose: compare simple simulated model training choices.
- Core concept: the highest F1 score is not automatically the best choice.
- Suggested module: cost-performance tradeoffs.
- Command:

```bash
python examples/intro_modeling_demo.py
```

### `llm_token_demo.py`

- Teaching purpose: compare small, medium, and large simulated LLM calls.
- Core concept: model size and token counts affect cost.
- Suggested module: token economics.
- Command:

```bash
python examples/llm_token_demo.py
```

### `token_burn_demo.py`

- Teaching purpose: show how verbose prompts and repeated context consume budget.
- Core concept: inefficient token use can exhaust funds without much quality gain.
- Suggested module: token economics and prompt discipline.
- Command:

```bash
python examples/token_burn_demo.py
```

### `hyperparameter_explosion_demo.py`

- Teaching purpose: show how grid searches multiply costs.
- Core concept: repeated experimentation compounds small per-run costs.
- Suggested module: hyperparameter costs and experiment planning.
- Command:

```bash
python examples/hyperparameter_explosion_demo.py
```

### `rag_cost_burn_demo.py`

- Teaching purpose: show that RAG has layered costs.
- Core concept: embedding, indexing, retrieval, retrieved context, chat history,
  and generation all contribute to cost.
- Suggested module: RAG and AI workflow costs.
- Command:

```bash
python examples/rag_cost_burn_demo.py
```

### `vibe_coding_cost_demo.py`

- Teaching purpose: compare unstructured AI-assisted coding with a planned workflow.
- Core concept: each chat turn has a cost, and vague repeated prompts compound.
- Suggested module: AI coding assistants and workflow planning.
- Command:

```bash
python examples/vibe_coding_cost_demo.py
```

### `scaling_inference_demo.py`

- Teaching purpose: show how low per-record inference cost grows with volume.
- Core concept: scaling changes the meaning of “cheap.”
- Suggested module: scaling and deployment.
- Command:

```bash
python examples/scaling_inference_demo.py
```

### `budget_challenge_demo.py`

- Teaching purpose: ask students to choose a workflow under a fixed budget.
- Core concept: final recommendations should justify both performance and cost.
- Suggested module: budget-constrained final challenge.
- Command:

```bash
python examples/budget_challenge_demo.py
```
