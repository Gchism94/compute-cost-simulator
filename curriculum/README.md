# Curriculum Overview

Compute Cost Simulator supports a seven-module sequence for teaching
cost-aware computing. The sequence can be used as a short unit, a recurring lab
theme, or a final project scaffold.

The flagship demo, `examples/flagship_budget_failure_demo.py`, can be used as
the overview lesson before students work through the individual modules. It
shows the full arc: estimate before running, choose what to execute, track
receipts, hit budget pressure, and justify a final recommendation.

## Module 1: Compute Is Not Free

Students learn that every computational action has a resource footprint, even
when no real money is charged in a classroom setting.

Suggested examples:
- `examples/flagship_budget_failure_demo.py`
- `examples/intro_modeling_demo.py`

## Module 2: Cost-Performance Tradeoffs

Students compare model performance with simulated cost and discuss whether a
small metric gain is worth the extra budget.

Suggested examples:
- `examples/intro_modeling_demo.py`
- `examples/budget_challenge_demo.py`

## Module 3: Token Economics

Students learn that LLM cost depends on model size, input tokens, output tokens,
and repeated prompts.

Suggested examples:
- `examples/llm_token_demo.py`
- `examples/token_burn_demo.py`

## Module 4: Repeated Experimentation And Hyperparameter Costs

Students estimate the cost of repeated runs before launching them and see how
grid searches multiply spending.

Suggested examples:
- `examples/hyperparameter_explosion_demo.py`
- `examples/flagship_budget_failure_demo.py`

## Module 5: RAG And Vibe-Coding Cost Loops

Students examine AI workflows where costs are spread across embedding,
retrieval, context, generation, and iterative chat turns.

Suggested examples:
- `examples/rag_cost_burn_demo.py`
- `examples/vibe_coding_cost_demo.py`

## Module 6: Scaling And Deployment

Students project costs from a small sample to classroom, organizational, or
deployment scale.

Suggested examples:
- `examples/scaling_inference_demo.py`
- `examples/rag_cost_burn_demo.py`

## Module 7: Budget-Constrained Final Challenge

Students design or simulate a workflow under a fixed budget and defend the
final choice using both performance and cost.

Suggested examples:
- `examples/budget_challenge_demo.py`
- `examples/flagship_budget_failure_demo.py`

## Teaching Pattern

For each module:

1. Estimate the cost before running.
2. Execute or simulate the action.
3. Inspect the receipt.
4. Compare cost with performance or usefulness.
5. Decide what should be run next.
6. Reflect on reproducibility and scale.
